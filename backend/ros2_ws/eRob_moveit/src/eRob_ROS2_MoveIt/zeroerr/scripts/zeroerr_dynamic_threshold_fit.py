#!/usr/bin/env python3

"""Fit directional motion-conditioned thresholds from collision-free runs."""

from __future__ import annotations

import argparse
import csv
import json
import shutil
import time
from collections import defaultdict
from pathlib import Path

import numpy as np


JOINT_NAMES = [f"Joint_{index}" for index in range(1, 7)]
FEATURE_NAMES = [
    "bias",
    "positive_velocity",
    "negative_velocity",
    "positive_acceleration",
    "negative_acceleration",
    "positive_velocity_squared",
    "negative_velocity_squared",
    "positive_acceleration_squared",
    "negative_acceleration_squared",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, help="Collision training CSV")
    parser.add_argument(
        "--run", required=True, action="append",
        help="Collision-free calibration/test run directory; may be repeated")
    parser.add_argument("--config", required=True, help="Monitor configuration JSON")
    parser.add_argument("--percentile", type=float, default=99.9)
    parser.add_argument("--margin-scale", type=float, default=1.10)
    parser.add_argument("--ridge", type=float, default=0.1)
    parser.add_argument("--decay-sec", type=float, default=0.35)
    parser.add_argument("--apply", action="store_true")
    return parser.parse_args()


def run_time_bounds(run_directory: Path) -> tuple[float, float]:
    path = run_directory / "coverage_points.csv"
    timestamps = []
    with path.open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            timestamps.append(float(row["unix_time"]))
    if not timestamps:
        raise SystemExit(f"No calibration timestamps in {path}")
    return min(timestamps), max(timestamps) + 2.0


def load_samples(path: Path, time_ranges: list[tuple[float, float]]):
    samples = defaultdict(list)
    with path.open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            timestamp = float(row["timestamp"])
            if not any(start <= timestamp <= stop for start, stop in time_ranges):
                continue
            joint = row.get("joint", "")
            if joint not in JOINT_NAMES:
                continue
            velocity = float(row["velocity_rad_s"])
            acceleration = float(row["acceleration_rad_s2"])
            residual = abs(float(row["external_torque_nm"]))
            values = (timestamp, velocity, acceleration, residual)
            if all(np.isfinite(value) for value in values):
                samples[joint].append(values)
    return samples


def design_matrix(values: np.ndarray, decay_sec: float) -> np.ndarray:
    timestamp = values[:, 0]
    velocity = values[:, 1]
    acceleration = values[:, 2]
    velocity_positive = np.maximum(velocity, 0.0)
    velocity_negative = np.maximum(-velocity, 0.0)
    acceleration_positive = np.maximum(acceleration, 0.0)
    acceleration_negative = np.maximum(-acceleration, 0.0)
    instantaneous = np.column_stack([
        velocity_positive, velocity_negative,
        acceleration_positive, acceleration_negative,
    ])
    envelope = np.zeros_like(instantaneous)
    previous = np.zeros(4, dtype=float)
    previous_time = None
    for index, (sample_time, sample) in enumerate(zip(timestamp, instantaneous)):
        dt = 0.0 if previous_time is None else max(0.0, sample_time - previous_time)
        previous = np.maximum(sample, previous * np.exp(-dt / decay_sec))
        envelope[index] = previous
        previous_time = sample_time
    velocity_positive = envelope[:, 0]
    velocity_negative = envelope[:, 1]
    acceleration_positive = envelope[:, 2]
    acceleration_negative = envelope[:, 3]
    return np.column_stack([
        np.ones(len(values)),
        velocity_positive,
        velocity_negative,
        acceleration_positive,
        acceleration_negative,
        velocity_positive * velocity_positive,
        velocity_negative * velocity_negative,
        acceleration_positive * acceleration_positive,
        acceleration_negative * acceleration_negative,
    ])


def fit_joint(
    values: np.ndarray, percentile: float, margin: float,
    ridge: float, decay_sec: float,
):
    design = design_matrix(values, decay_sec)
    residual = values[:, 3]
    penalty = np.eye(design.shape[1]) * ridge
    penalty[0, 0] = 0.0
    coefficients = np.linalg.solve(
        design.T @ design + penalty,
        design.T @ residual,
    )
    # Move the fitted centre to the requested one-sided residual percentile,
    # then retain an explicit safety margin. The fixed threshold remains the
    # lower floor at runtime.
    coefficients[0] += max(
        0.0,
        float(np.percentile(residual - design @ coefficients, percentile)),
    )
    coefficients *= margin
    predicted = design @ coefficients
    return coefficients, {
        "samples": int(len(values)),
        "max_abs_velocity_rad_s": float(np.max(np.abs(values[:, 1]))),
        "max_abs_acceleration_rad_s2": float(np.max(np.abs(values[:, 2]))),
        "calibration_exceedance_fraction": float(np.mean(residual > predicted)),
        "predicted_threshold_min_nm": float(np.min(predicted)),
        "predicted_threshold_max_nm": float(np.max(predicted)),
    }


def main() -> int:
    args = parse_args()
    input_path = Path(args.input).expanduser().resolve()
    run_directories = [Path(value).expanduser().resolve() for value in args.run]
    config_path = Path(args.config).expanduser().resolve()
    time_ranges = [run_time_bounds(path) for path in run_directories]
    samples = load_samples(input_path, time_ranges)
    payload = json.loads(config_path.read_text(encoding="utf-8"))

    coefficients = {}
    limits = {}
    fit_summary = {}
    for joint_name in JOINT_NAMES:
        values = np.asarray(samples.get(joint_name, []), dtype=float)
        if len(values) < 100:
            raise SystemExit(f"Insufficient samples for {joint_name}: {len(values)}")
        fitted, summary = fit_joint(
            values,
            float(args.percentile),
            float(args.margin_scale),
            float(args.ridge),
            float(args.decay_sec),
        )
        coefficients[joint_name] = fitted.tolist()
        limits[joint_name] = [
            summary["max_abs_velocity_rad_s"],
            summary["max_abs_acceleration_rad_s2"],
        ]
        fit_summary[joint_name] = summary
        print(
            f"{joint_name}: samples={summary['samples']} "
            f"calibration_exceedance={100.0 * summary['calibration_exceedance_fraction']:.3f}% "
            f"threshold_range={summary['predicted_threshold_min_nm']:.2f}.."
            f"{summary['predicted_threshold_max_nm']:.2f} Nm"
        )

    payload["dynamic_threshold_enabled"] = True
    payload["dynamic_threshold_feature_names"] = FEATURE_NAMES
    payload["dynamic_threshold_coefficients"] = coefficients
    payload["dynamic_threshold_training_limits"] = limits
    payload["dynamic_threshold_decay_sec"] = float(args.decay_sec)
    payload["dynamic_threshold_fit"] = {
        "input_csv": str(input_path),
        "run_directories": [str(path) for path in run_directories],
        "time_ranges": [list(bounds) for bounds in time_ranges],
        "percentile": float(args.percentile),
        "margin_scale": float(args.margin_scale),
        "joints": fit_summary,
    }
    if args.apply:
        backup = run_directories[-1] / (
            f"collision_monitor_config.backup-{time.strftime('%Y%m%d-%H%M%S')}.json")
        shutil.copy2(config_path, backup)
        config_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        print(f"Applied dynamic thresholds to {config_path}")
        print(f"Previous configuration backed up to {backup}")
    else:
        print("Dry fit only; pass --apply to update the monitor configuration")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
