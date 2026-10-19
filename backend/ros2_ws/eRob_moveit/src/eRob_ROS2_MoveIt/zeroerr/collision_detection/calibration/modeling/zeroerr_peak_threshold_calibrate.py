#!/usr/bin/env python3
"""Calibrate collision floors and dynamic bias from peak-preserving sessions."""

from __future__ import annotations

import argparse
import csv
import json
import math
import shutil
import time
from collections import defaultdict
from pathlib import Path

import numpy as np


JOINTS = [f"Joint_{index}" for index in range(1, 7)]


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", action="append", required=True)
    parser.add_argument("--config", required=True)
    parser.add_argument("--percentile", type=float, default=99.9)
    parser.add_argument("--margin-scale", type=float, default=1.10)
    parser.add_argument("--margin-nm", type=float, default=0.10)
    parser.add_argument("--stationary-velocity", type=float, default=0.02)
    parser.add_argument("--stationary-acceleration", type=float, default=0.5)
    parser.add_argument("--minimum-floor", type=float, default=0.5)
    parser.add_argument("--apply", action="store_true")
    return parser.parse_args()


def load_sessions(paths):
    samples = defaultdict(list)
    intervals = []
    for path in paths:
        timestamps = []
        with path.open(newline="", encoding="utf-8") as handle:
            for row in csv.DictReader(handle):
                joint = row.get("joint", "")
                if joint not in JOINTS:
                    continue
                values = (
                    float(row["timestamp"]),
                    abs(float(row["external_torque_nm"])),
                    float(row["threshold_nm"]),
                    abs(float(row["velocity_rad_s"])),
                    abs(float(row["acceleration_rad_s2"])),
                )
                if all(math.isfinite(value) for value in values):
                    samples[joint].append(values)
                    if joint == "Joint_1":
                        timestamps.append(values[0])
        intervals.extend(
            stop - start for start, stop in zip(timestamps, timestamps[1:])
            if 0.0 < stop - start < 0.1
        )
    return samples, float(np.median(intervals))


def longest_true_run(mask):
    longest = current = 0
    for value in mask:
        current = current + 1 if value else 0
        longest = max(longest, current)
    return longest


def calibrate_joint(
    values, *, percentile, margin_scale, margin_nm, stationary_velocity,
    stationary_acceleration, minimum_floor, persistence_windows,
):
    values = np.asarray(values, dtype=float)
    residual, old_threshold = values[:, 1], values[:, 2]
    stationary = residual[
        (values[:, 3] <= stationary_velocity)
        & (values[:, 4] <= stationary_acceleration)
    ]
    if len(stationary) < 100:
        raise ValueError(f"only {len(stationary)} stationary samples")
    floor = max(
        minimum_floor,
        float(np.percentile(stationary, percentile)) * margin_scale + margin_nm,
    )
    score = residual - old_threshold
    quantile_delta = float(np.percentile(score, percentile)) + margin_nm
    episode_delta = max(
        min(score[index:index + persistence_windows])
        for index in range(len(score) - persistence_windows + 1)
    ) + margin_nm
    bias_delta = max(quantile_delta, episode_delta)
    # This proxy is exact where the old dynamic fit was above its floor and
    # conservative for persistence selection. A fresh session remains the
    # required final validation after applying the calibration.
    proxy_threshold = np.maximum(floor, old_threshold + bias_delta)
    exceedance = residual >= proxy_threshold
    return floor, bias_delta, {
        "samples": int(len(values)),
        "stationary_samples": int(len(stationary)),
        "stationary_p99_9_abs_nm": float(np.percentile(stationary, percentile)),
        "static_floor_nm": float(floor),
        "dynamic_bias_delta_nm": float(bias_delta),
        "proxy_exceedance_windows": int(np.count_nonzero(exceedance)),
        "proxy_max_consecutive_exceedance_windows": int(longest_true_run(exceedance)),
    }


def main():
    args = parse_args()
    paths = [Path(value).expanduser().resolve() for value in args.input]
    config_path = Path(args.config).expanduser().resolve()
    payload = json.loads(config_path.read_text(encoding="utf-8"))
    samples, median_interval = load_sessions(paths)
    persistence_windows = max(
        1, math.ceil(float(payload["confirm_duration_ms"]) / (median_interval * 1000.0)))
    floors = []
    report = {
        "inputs": [str(path) for path in paths],
        "percentile": float(args.percentile),
        "margin_scale": float(args.margin_scale),
        "margin_nm": float(args.margin_nm),
        "median_peak_interval_ms": median_interval * 1000.0,
        "persistence_windows": persistence_windows,
        "joints": {},
    }
    coefficients = payload["dynamic_threshold_coefficients"]
    for joint in JOINTS:
        floor, delta, summary = calibrate_joint(
            samples[joint], percentile=float(args.percentile),
            margin_scale=float(args.margin_scale), margin_nm=float(args.margin_nm),
            stationary_velocity=float(args.stationary_velocity),
            stationary_acceleration=float(args.stationary_acceleration),
            minimum_floor=float(args.minimum_floor),
            persistence_windows=persistence_windows,
        )
        floors.append(floor)
        coefficients[joint][0] = float(coefficients[joint][0]) + delta
        report["joints"][joint] = summary
        print(
            f"{joint}: floor={floor:.3f} Nm bias_delta={delta:+.3f} Nm "
            f"proxy_exceed={summary['proxy_exceedance_windows']} "
            f"max_run={summary['proxy_max_consecutive_exceedance_windows']}"
        )
    payload["external_torque_thresholds"] = floors
    payload["dynamic_threshold_coefficients"] = coefficients
    payload["peak_threshold_calibration"] = report
    report_path = paths[-1].parent / "peak_threshold_calibration_report.json"
    report_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    if args.apply:
        backup = config_path.with_name(
            f"{config_path.stem}.pre-threshold-calibration-"
            f"{time.strftime('%Y%m%d-%H%M%S')}.json"
        )
        shutil.copy2(config_path, backup)
        config_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        print(f"Applied thresholds to {config_path}; backup={backup}")
    else:
        print(f"Preview only; report={report_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
