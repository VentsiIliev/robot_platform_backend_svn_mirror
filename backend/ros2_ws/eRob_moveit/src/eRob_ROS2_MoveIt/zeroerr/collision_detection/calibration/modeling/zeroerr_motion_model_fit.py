#!/usr/bin/env python3
"""Fit smooth asymmetric friction, pose, and motion residual models by session."""

from __future__ import annotations

import argparse
import csv
import json
import shutil
import time
from pathlib import Path

import numpy as np


JOINTS = [f"Joint_{index}" for index in range(1, 7)]
FRICTION_FEATURES = [
    "coulomb_positive", "coulomb_negative", "static_positive",
    "static_negative", "viscous_velocity",
]
POSITION_FEATURES = [
    "bias", "sin_q2", "cos_q2", "sin_q2_q3", "cos_q2_q3",
    "sin_q2_q3_q4", "cos_q2_q3_q4", "sin_q3", "cos_q3",
]
MOTION_FEATURES = [
    "positive_velocity_squared", "negative_velocity_squared",
    "positive_acceleration", "negative_acceleration",
]
FEATURES = [*FRICTION_FEATURES, *POSITION_FEATURES, *MOTION_FEATURES]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", action="append", required=True,
                        help="One collision-free peak/training CSV per session")
    parser.add_argument("--config", required=True)
    parser.add_argument("--transition-velocity", type=float, default=0.01)
    parser.add_argument("--stribeck-velocity", type=float, default=0.05)
    parser.add_argument("--ridge", type=float, default=0.2)
    parser.add_argument("--huber-scale", type=float, default=1.5)
    parser.add_argument("--apply", action="store_true")
    return parser.parse_args()


def position_features(q: list[float]) -> list[float]:
    q2, q3, q4 = q[1:4]
    q23, q234 = q2 + q3, q2 + q3 + q4
    return [
        1.0, np.sin(q2), np.cos(q2), np.sin(q23), np.cos(q23),
        np.sin(q234), np.cos(q234), np.sin(q3), np.cos(q3),
    ]


def model_features(
    q: list[float], velocity: float, acceleration: float,
    transition_velocity: float, stribeck_velocity: float,
) -> list[float]:
    direction = np.tanh(velocity / transition_velocity)
    positive, negative = max(direction, 0.0), max(-direction, 0.0)
    stribeck = np.exp(-((abs(velocity) / stribeck_velocity) ** 2))
    velocity_positive, velocity_negative = max(velocity, 0.0), max(-velocity, 0.0)
    return [
        positive * (1.0 - stribeck),
        -negative * (1.0 - stribeck),
        positive * stribeck,
        -negative * stribeck,
        velocity,
        *position_features(q),
        velocity_positive ** 2, velocity_negative ** 2,
        max(acceleration, 0.0), max(-acceleration, 0.0),
    ]


def load_peak_session(path: Path, session_index: int, transition: float, stribeck: float):
    samples = {joint: [] for joint in JOINTS}
    with path.open(newline="", encoding="utf-8") as handle:
        rows = csv.DictReader(handle)
        fields = set(rows.fieldnames or [])
        peak_format = "position_1" in fields
        if not peak_format:
            grouped: dict[float, dict[str, dict]] = {}
            for row in rows:
                joint = row.get("joint", "")
                if joint in JOINTS:
                    grouped.setdefault(float(row["timestamp"]), {})[joint] = row
            iterable = []
            for timestamp, batch in sorted(grouped.items()):
                if all(joint in batch for joint in JOINTS):
                    q = [float(batch[joint]["position_rad"]) for joint in JOINTS]
                    iterable.extend((joint, q, batch[joint]) for joint in JOINTS)
        else:
            iterable = []
            for row in rows:
                joint = row.get("joint", "")
                if joint in JOINTS:
                    q = [float(row[f"position_{index}"]) for index in range(1, 7)]
                    iterable.append((joint, q, row))
        for joint, q, row in iterable:
            try:
                velocity = float(row.get("velocity_rad_s", row.get("velocity", "nan")))
                acceleration = float(row.get("acceleration_rad_s2", row.get("acceleration", "nan")))
                measured = float(row.get("measured_torque_nm", row.get("measured_torque", "nan")))
                expected = float(row.get("expected_torque_nm", row.get("expected_torque", "nan")))
            except (TypeError, ValueError):
                continue
            feature = model_features(q, velocity, acceleration, transition, stribeck)
            values = [*feature, measured - expected, float(session_index)]
            if all(np.isfinite(value) for value in values):
                samples[joint].append(values)
    return samples


def robust_fit(design, target, ridge, huber_scale):
    penalty = np.eye(design.shape[1]) * ridge
    penalty[FEATURES.index("bias"), FEATURES.index("bias")] = 0.0
    weights = np.ones(len(target))
    coefficients = np.zeros(design.shape[1])
    for _ in range(30):
        weighted = weights[:, None] * design
        coefficients = np.linalg.solve(
            design.T @ weighted + penalty, design.T @ (weights * target))
        residual = target - design @ coefficients
        centre = np.median(residual)
        sigma = 1.4826 * np.median(np.abs(residual - centre)) + 1.0e-9
        updated = np.minimum(
            1.0, huber_scale * sigma / np.maximum(np.abs(residual), 1.0e-12))
        if np.max(np.abs(updated - weights)) < 1.0e-4:
            break
        weights = updated
    return coefficients


def metrics(residual):
    absolute = np.abs(residual)
    return {
        "rmse_nm": float(np.sqrt(np.mean(residual ** 2))),
        "mae_nm": float(np.mean(absolute)),
        "p95_abs_nm": float(np.percentile(absolute, 95)),
        "p99_abs_nm": float(np.percentile(absolute, 99)),
        "max_abs_nm": float(np.max(absolute)),
    }


def excitation_metrics(design, minimum_velocity=0.05, minimum_samples=50):
    """Report whether both directions needed by the asymmetric model are observed."""
    velocity = design[:, FEATURES.index("viscous_velocity")]
    positive_samples = int(np.count_nonzero(velocity >= minimum_velocity))
    negative_samples = int(np.count_nonzero(velocity <= -minimum_velocity))
    return {
        "minimum_velocity_rad_s": float(minimum_velocity),
        "minimum_samples_per_direction": int(minimum_samples),
        "positive_velocity_samples": positive_samples,
        "negative_velocity_samples": negative_samples,
        "identifiable": (
            positive_samples >= minimum_samples
            and negative_samples >= minimum_samples
        ),
    }


def main() -> int:
    args = parse_args()
    paths = [Path(value).expanduser().resolve() for value in args.input]
    if len(paths) < 2:
        raise SystemExit("At least two independent session CSVs are required")
    transition = max(1.0e-5, float(args.transition_velocity))
    stribeck = max(transition, float(args.stribeck_velocity))
    combined = {joint: [] for joint in JOINTS}
    for session, path in enumerate(paths):
        loaded = load_peak_session(path, session, transition, stribeck)
        for joint in JOINTS:
            combined[joint].extend(loaded[joint])
    report = {
        "inputs": [str(path) for path in paths], "feature_names": FEATURES,
        "transition_velocity_rad_s": transition,
        "stribeck_velocity_rad_s": stribeck, "joints": {},
    }
    fitted = {}
    for joint in JOINTS:
        values = np.asarray(combined[joint], dtype=float)
        if len(values) < 500:
            raise SystemExit(f"Insufficient samples for {joint}: {len(values)}")
        design, target, session_ids = values[:, :-2], values[:, -2], values[:, -1].astype(int)
        folds = []
        for held_out in range(len(paths)):
            train, validate = session_ids != held_out, session_ids == held_out
            if np.count_nonzero(validate) < 50:
                raise SystemExit(f"Session {held_out + 1} has too few {joint} samples")
            coefficients = robust_fit(
                design[train], target[train], float(args.ridge), float(args.huber_scale))
            folds.append({
                "held_out_session": held_out + 1,
                "training_samples": int(np.count_nonzero(train)),
                "validation_samples": int(np.count_nonzero(validate)),
                "before": metrics(target[validate]),
                "after": metrics(target[validate] - design[validate] @ coefficients),
            })
        excitation = excitation_metrics(design)
        accepted = excitation["identifiable"] and all(
            fold["after"]["rmse_nm"] < fold["before"]["rmse_nm"]
            and fold["after"]["p99_abs_nm"] < fold["before"]["p99_abs_nm"]
            for fold in folds)
        coefficients = robust_fit(
            design, target, float(args.ridge), float(args.huber_scale))
        fitted[joint] = coefficients
        report["joints"][joint] = {
            "accepted": accepted, "samples": len(values),
            "excitation": excitation,
            "coefficients": coefficients.tolist(), "held_out": folds,
            "combined_before": metrics(target),
            "combined_after": metrics(target - design @ coefficients),
        }
        before, after = report["joints"][joint]["combined_before"], report["joints"][joint]["combined_after"]
        print(f"{joint}: {'ACCEPT' if accepted else 'REJECT'} p99 "
              f"{before['p99_abs_nm']:.3f} -> {after['p99_abs_nm']:.3f} Nm")
    report_path = paths[-1].parent / "motion_model_fit_report.json"
    report_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    if args.apply:
        rejected = [joint for joint in JOINTS if not report["joints"][joint]["accepted"]]
        if rejected:
            raise SystemExit(f"Refusing partial deployment; held-out validation failed: {rejected}")
        config_path = Path(args.config).expanduser().resolve()
        payload = json.loads(config_path.read_text(encoding="utf-8"))
        matrix = np.vstack([fitted[joint] for joint in JOINTS])
        payload["friction_coulomb_positive_nm"] = matrix[:, 0].tolist()
        payload["friction_coulomb_negative_nm"] = matrix[:, 1].tolist()
        payload["friction_static_positive_nm"] = matrix[:, 2].tolist()
        payload["friction_static_negative_nm"] = matrix[:, 3].tolist()
        payload["friction_viscous_nm_per_rad_s"] = matrix[:, 4].tolist()
        payload["friction_transition_velocity_rad_s"] = transition
        payload["friction_stribeck_velocity_rad_s"] = stribeck
        payload["position_correction_coefficients"] = {
            joint: matrix[index, 5:14].tolist() for index, joint in enumerate(JOINTS)}
        payload["motion_residual_correction_coefficients"] = {
            joint: [0.0, 0.0, *matrix[index, 14:18].tolist()]
            for index, joint in enumerate(JOINTS)}
        payload["motion_residual_correction_limits"] = {
            joint: [
                float(max(np.abs(np.asarray(combined[joint])[:, 4]).max(), 0.01)),
                float(max(np.asarray(combined[joint])[:, 16:18].max(), 0.1)),
            ] for joint in JOINTS}
        payload["motion_model_fit"] = report
        backup = config_path.with_name(
            f"{config_path.stem}.pre-motion-fit-{time.strftime('%Y%m%d-%H%M%S')}.json")
        shutil.copy2(config_path, backup)
        config_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        print(f"Applied model to {config_path}; backup={backup}")
    else:
        print(f"Report written to {report_path}; preview only")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
