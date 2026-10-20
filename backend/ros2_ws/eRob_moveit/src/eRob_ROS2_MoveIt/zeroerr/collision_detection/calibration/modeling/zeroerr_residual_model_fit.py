#!/usr/bin/env python3

"""Fit deployable friction and position residual corrections from clean motion."""

from __future__ import annotations

import argparse
import csv
import json
import shutil
import time
from collections import defaultdict
from pathlib import Path

import numpy as np

# Shared configuration access also works when this tool is run from source.
try:
    from zeroerr_configuration.sensorless_collision import read_monitor_config, write_monitor_config
except ModuleNotFoundError as error:
    if error.name != 'zeroerr_configuration':
        raise
    import sys
    sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
    from zeroerr_configuration.sensorless_collision import read_monitor_config, write_monitor_config



JOINT_NAMES = [f"Joint_{index}" for index in range(1, 7)]
POSITION_FEATURE_NAMES = [
    "bias",
    "sin_q2", "cos_q2",
    "sin_q2_q3", "cos_q2_q3",
    "sin_q2_q3_q4", "cos_q2_q3_q4",
    "sin_q3", "cos_q3",
]
MODEL_FEATURE_NAMES = ["friction_sign", "velocity", *POSITION_FEATURE_NAMES]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, help="Combined collision training CSV")
    parser.add_argument("--config", required=True, help="Profile sensorless_collision.yaml (or historical JSON input)")
    parser.add_argument("--ridge", type=float, default=1.0)
    parser.add_argument("--huber-scale", type=float, default=1.5)
    parser.add_argument("--apply", action="store_true")
    return parser.parse_args()


def _position_features(positions: list[float]) -> list[float]:
    q2, q3, q4 = positions[1:4]
    q23 = q2 + q3
    q234 = q23 + q4
    return [
        1.0,
        np.sin(q2), np.cos(q2),
        np.sin(q23), np.cos(q23),
        np.sin(q234), np.cos(q234),
        np.sin(q3), np.cos(q3),
    ]


def load_batches(path: Path, velocity_deadband: float):
    by_timestamp = defaultdict(dict)
    with path.open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            timestamp = float(row["timestamp"])
            joint_name = row.get("joint", "")
            if joint_name in JOINT_NAMES:
                by_timestamp[timestamp][joint_name] = row

    samples = {joint_name: [] for joint_name in JOINT_NAMES}
    complete_timestamps = []
    for timestamp in sorted(by_timestamp):
        rows = by_timestamp[timestamp]
        if any(joint_name not in rows for joint_name in JOINT_NAMES):
            continue
        positions = [float(rows[name]["position_rad"]) for name in JOINT_NAMES]
        position_features = _position_features(positions)
        for joint_name in JOINT_NAMES:
            row = rows[joint_name]
            velocity = float(row["velocity_rad_s"])
            sign = 0.0 if abs(velocity) < velocity_deadband else np.sign(velocity)
            target = (
                float(row["measured_torque_nm"])
                - float(row["expected_torque_nm"])
            )
            values = [sign, velocity, *position_features, target]
            if not all(np.isfinite(value) for value in values):
                break
            samples[joint_name].append(values)
        else:
            complete_timestamps.append(timestamp)
            continue
        for joint_name in JOINT_NAMES:
            if len(samples[joint_name]) > len(complete_timestamps):
                samples[joint_name].pop()

    if len(complete_timestamps) < 200:
        raise SystemExit(f"Insufficient complete synchronized samples: {len(complete_timestamps)}")
    return np.asarray(complete_timestamps), {
        name: np.asarray(values, dtype=float) for name, values in samples.items()
    }


def session_slices(timestamps: np.ndarray) -> list[slice]:
    if len(timestamps) < 2:
        return [slice(None)]
    gaps = np.diff(timestamps)
    typical_gap = max(float(np.median(gaps)), 1.0e-3)
    boundaries = list(np.flatnonzero(gaps > max(5.0, 20.0 * typical_gap)) + 1)
    starts = [0, *boundaries]
    stops = [*boundaries, len(timestamps)]
    return [slice(start, stop) for start, stop in zip(starts, stops)]


def robust_ridge_fit(
    design: np.ndarray,
    target: np.ndarray,
    ridge: float,
    huber_scale: float,
) -> np.ndarray:
    # Regularize the deployable coefficients in their physical representation.
    # Standardizing the trigonometric columns over a limited work envelope can
    # turn a low-variance feature into a huge coefficient that only cancels
    # another term inside the training envelope and extrapolates dangerously.
    intercept_index = MODEL_FEATURE_NAMES.index("bias")
    penalty = np.eye(design.shape[1], dtype=float) * ridge
    penalty[intercept_index, intercept_index] = 0.0
    weights = np.ones(len(target), dtype=float)
    coefficients = np.zeros(design.shape[1], dtype=float)
    for _ in range(20):
        weighted = weights[:, None] * design
        coefficients = np.linalg.solve(
            design.T @ weighted + penalty,
            design.T @ (weights * target),
        )
        residual = target - design @ coefficients
        median = float(np.median(residual))
        robust_sigma = 1.4826 * float(np.median(np.abs(residual - median))) + 1.0e-9
        limit = huber_scale * robust_sigma
        new_weights = np.minimum(1.0, limit / np.maximum(np.abs(residual), 1.0e-12))
        if np.max(np.abs(new_weights - weights)) < 1.0e-4:
            break
        weights = new_weights

    return coefficients


def metrics(values: np.ndarray) -> dict[str, float]:
    absolute = np.abs(values)
    return {
        "mae_nm": float(np.mean(absolute)),
        "rmse_nm": float(np.sqrt(np.mean(values * values))),
        "p95_abs_nm": float(np.percentile(absolute, 95.0)),
        "p99_abs_nm": float(np.percentile(absolute, 99.0)),
        "max_abs_nm": float(np.max(absolute)),
    }


def cross_validate(
    design: np.ndarray,
    target: np.ndarray,
    sessions: list[slice],
    ridge: float,
    huber_scale: float,
) -> list[dict]:
    if len(sessions) < 2:
        return []
    results = []
    all_indices = np.arange(len(target))
    for validation_number, validation_slice in enumerate(sessions, start=1):
        validation = all_indices[validation_slice]
        training = np.setdiff1d(all_indices, validation, assume_unique=True)
        coefficients = robust_ridge_fit(
            design[training], target[training], ridge, huber_scale)
        corrected = target[validation] - design[validation] @ coefficients
        results.append({
            "validation_session": validation_number,
            "training_samples": int(len(training)),
            "validation_samples": int(len(validation)),
            "before": metrics(target[validation]),
            "after": metrics(corrected),
        })
    return results


def fit_is_safe(cross_validation: list[dict]) -> bool:
    if not cross_validation:
        return False
    return all(
        result["after"]["rmse_nm"] < result["before"]["rmse_nm"]
        and result["after"]["p99_abs_nm"] < result["before"]["p99_abs_nm"]
        # Tail and energy reduction are the collision-observer priorities. A
        # small mean-error tradeoff is allowed when both improve substantially.
        and result["after"]["mae_nm"] <= 1.15 * result["before"]["mae_nm"]
        for result in cross_validation
    )


def main() -> int:
    args = parse_args()
    input_path = Path(args.input).expanduser().resolve()
    config_path = Path(args.config).expanduser().resolve()
    payload = read_monitor_config(config_path)
    deadband = float(payload.get("friction_velocity_deadband_rad_s", 0.01))
    timestamps, samples = load_batches(input_path, deadband)
    sessions = session_slices(timestamps)
    if len(sessions) < 2:
        raise SystemExit(
            "At least two timestamp-separated sessions are required for held-out validation")

    coulomb = np.asarray(payload.get("friction_coulomb_nm", [0.0] * 6), dtype=float)
    viscous = np.asarray(
        payload.get("friction_viscous_nm_per_rad_s", [0.0] * 6), dtype=float)
    position_by_joint = payload.get("position_correction_coefficients", {})
    report = {
        "input_csv": str(input_path),
        "sample_count": int(len(timestamps)),
        "session_sample_counts": [int(item.stop - item.start) for item in sessions],
        "feature_names": MODEL_FEATURE_NAMES,
        "joints": {},
    }

    for index, joint_name in enumerate(JOINT_NAMES):
        values = samples[joint_name]
        design = values[:, :-1]
        target = values[:, -1]
        validation = cross_validate(
            design, target, sessions, float(args.ridge), float(args.huber_scale))
        accepted = fit_is_safe(validation)
        delta = robust_ridge_fit(
            design, target, float(args.ridge), float(args.huber_scale))
        corrected = target - design @ delta
        report["joints"][joint_name] = {
            "accepted": accepted,
            "delta_coefficients": delta.tolist(),
            "combined_before": metrics(target),
            "combined_after": metrics(corrected),
            "cross_validation": validation,
        }
        before = metrics(target)
        after = metrics(corrected)
        print(
            f"{joint_name}: {'ACCEPT' if accepted else 'REJECT'} "
            f"cross-session fit; combined p99 {before['p99_abs_nm']:.3f} -> "
            f"{after['p99_abs_nm']:.3f} Nm, RMSE {before['rmse_nm']:.3f} -> "
            f"{after['rmse_nm']:.3f} Nm")
        if not accepted:
            continue
        coulomb[index] += delta[0]
        viscous[index] += delta[1]
        old_position = np.asarray(
            position_by_joint.get(joint_name, [0.0] * len(POSITION_FEATURE_NAMES)),
            dtype=float,
        )
        position_by_joint[joint_name] = (old_position + delta[2:]).tolist()

    payload["friction_coulomb_nm"] = coulomb.tolist()
    payload["friction_viscous_nm_per_rad_s"] = viscous.tolist()
    payload["position_correction_coefficients"] = position_by_joint
    payload["residual_model_fit"] = report

    report_path = input_path.with_name("residual_model_fit_report.json")
    report_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(f"Fit report written to {report_path}")
    if args.apply:
        backup = input_path.parent / (
            f"{config_path.stem}.pre-model-fit-{time.strftime('%Y%m%d-%H%M%S')}{config_path.suffix}")
        shutil.copy2(config_path, backup)
        write_monitor_config(config_path, payload)
        print(f"Applied accepted model corrections to {config_path}")
        print(f"Previous configuration backed up to {backup}")
    else:
        print("Preview only; pass --apply to update the monitor configuration")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
