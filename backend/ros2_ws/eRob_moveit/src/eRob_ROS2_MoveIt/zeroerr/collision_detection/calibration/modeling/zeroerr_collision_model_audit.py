#!/usr/bin/env python3
"""Audit collision-session timing, torque scaling/signs, payload, and URDF limits."""

from __future__ import annotations

import argparse
import csv
import json
import math
import xml.etree.ElementTree as ET
from collections import defaultdict
from pathlib import Path

import numpy as np


JOINTS = [f"Joint_{index}" for index in range(1, 7)]


def number(value) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return math.nan


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", action="append", required=True)
    parser.add_argument("--urdf", required=True, help="Expanded robot URDF")
    parser.add_argument("--output", required=True)
    return parser.parse_args()


def load_csv(path: Path):
    result = defaultdict(list)
    timestamps = []
    with path.open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            joint = row.get("joint", "")
            if joint not in JOINTS:
                continue
            timestamp = float(row["timestamp"])
            timestamps.append(timestamp)
            position = number(row.get("position_rad", row.get(f"position_{JOINTS.index(joint)+1}")))
            result[joint].append({
                "timestamp": timestamp,
                "position": position,
                "velocity": number(row.get("velocity_rad_s", row.get("velocity"))),
                "measured": number(row.get("measured_torque_nm", row.get("measured_torque"))),
                "sensor": number(row.get("torque_sensor_nm", row.get("measured_torque_nm"))),
                "expected": number(row.get("expected_torque_nm", row.get("expected_torque"))),
                "external": number(row.get("external_torque_nm", row.get("external_torque"))),
            })
    return result, np.unique(np.asarray(timestamps, dtype=float))


def urdf_summary(path: Path):
    root = ET.parse(path).getroot()
    masses = {}
    for link in root.findall("link"):
        mass = link.find("inertial/mass")
        if mass is not None and "value" in mass.attrib:
            masses[link.attrib["name"]] = float(mass.attrib["value"])
    limits = {}
    for joint in root.findall("joint"):
        limit = joint.find("limit")
        if limit is not None:
            limits[joint.attrib["name"]] = {
                key: float(limit.attrib[key]) for key in ("lower", "upper", "velocity", "effort")
                if key in limit.attrib
            }
    return {"link_masses_kg": masses, "total_declared_mass_kg": sum(masses.values()),
            "joint_limits": limits}


def finite(values):
    values = np.asarray(values, dtype=float)
    return values[np.isfinite(values)]


def main() -> int:
    args = parse_args()
    report = {
        "urdf": urdf_summary(Path(args.urdf).expanduser().resolve()),
        "sessions": [], "joints": {}, "warnings": [],
        "limitations": [
            "Sensor-to-measured comparison checks software consistency only; absolute Nm scaling requires a traceable applied-load test.",
            "Declared URDF mass is not proof of the installed payload; weigh or identify the mounted tool independently.",
        ],
    }
    all_joint = defaultdict(list)
    for raw_path in args.input:
        path = Path(raw_path).expanduser().resolve()
        samples, timestamps = load_csv(path)
        gaps = np.diff(timestamps)
        report["sessions"].append({
            "path": str(path), "unique_timestamps": int(len(timestamps)),
            "duration_sec": float(timestamps[-1] - timestamps[0]) if len(timestamps) > 1 else 0.0,
            "median_interval_ms": float(1000 * np.median(gaps)) if len(gaps) else None,
            "p99_interval_ms": float(1000 * np.percentile(gaps, 99)) if len(gaps) else None,
            "max_interval_ms": float(1000 * np.max(gaps)) if len(gaps) else None,
        })
        for joint, rows in samples.items():
            all_joint[joint].extend(rows)
    for joint in JOINTS:
        rows = all_joint[joint]
        if not rows:
            continue
        measured, sensor = finite([row["measured"] for row in rows]), finite([row["sensor"] for row in rows])
        paired = np.asarray([[row["sensor"], row["measured"]] for row in rows
                             if np.isfinite(row["sensor"]) and np.isfinite(row["measured"])])
        slope = float(np.linalg.lstsq(paired[:, :1], paired[:, 1], rcond=None)[0][0]) if len(paired) else None
        report["joints"][joint] = {
            "samples": len(rows),
            "position_min_rad": float(np.nanmin([row["position"] for row in rows])),
            "position_max_rad": float(np.nanmax([row["position"] for row in rows])),
            "velocity_max_abs_rad_s": float(np.nanmax(np.abs([row["velocity"] for row in rows]))),
            "measured_torque_min_nm": float(np.min(measured)),
            "measured_torque_max_nm": float(np.max(measured)),
            "torque_sensor_to_measured_slope": slope,
            "torque_sensor_measured_correlation": float(np.corrcoef(paired.T)[0, 1]) if len(paired) > 2 else None,
            "sign_mismatch_fraction": float(np.mean(np.sign(paired[:, 0]) != np.sign(paired[:, 1]))) if len(paired) else None,
        }
        limits = report["urdf"]["joint_limits"].get(joint, {})
        observed_min = report["joints"][joint]["position_min_rad"]
        observed_max = report["joints"][joint]["position_max_rad"]
        if "lower" in limits and observed_min < limits["lower"] - 1.0e-3:
            report["warnings"].append(
                f"{joint} observed {observed_min:.6f} rad below URDF lower {limits['lower']:.6f}")
        if "upper" in limits and observed_max > limits["upper"] + 1.0e-3:
            report["warnings"].append(
                f"{joint} observed {observed_max:.6f} rad above URDF upper {limits['upper']:.6f}")
        if limits.get("velocity", 0.0) > 20.0:
            report["warnings"].append(
                f"{joint} URDF velocity limit {limits['velocity']:.3f} rad/s is implausibly high")
    output = Path(args.output).expanduser().resolve()
    output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(f"Audit written to {output}")
    for joint, values in report["joints"].items():
        print(f"{joint}: scale={values['torque_sensor_to_measured_slope']:.6f} "
              f"sign_mismatch={100*values['sign_mismatch_fraction']:.3f}%")
    for warning in report["warnings"]:
        print(f"WARNING: {warning}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
