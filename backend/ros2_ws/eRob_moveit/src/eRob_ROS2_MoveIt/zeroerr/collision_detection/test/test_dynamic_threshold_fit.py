#!/usr/bin/env python3

"""Tests for monotonic motion-conditioned collision thresholds."""

from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path

import numpy as np


SCRIPT_PATH = (
    Path(__file__).parents[1]
    / "calibration"
    / "modeling"
    / "zeroerr_dynamic_threshold_fit.py"
)
SPEC = importlib.util.spec_from_file_location("zeroerr_dynamic_threshold_fit", SCRIPT_PATH)
FIT_MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(FIT_MODULE)


class DynamicThresholdFitTests(unittest.TestCase):
    def test_fit_coefficients_are_nonnegative_and_predictions_are_monotonic(self) -> None:
        timestamps = np.arange(0.0, 4.0, 0.01)
        velocities = np.linspace(-1.5, 1.5, len(timestamps))
        accelerations = np.sin(timestamps * 2.0) * 4.0
        residuals = (
            1.0
            + 0.8 * np.maximum(velocities, 0.0)
            + 0.5 * np.maximum(-velocities, 0.0)
            + 0.1 * np.abs(accelerations)
        )
        values = np.column_stack((timestamps, velocities, accelerations, residuals))

        coefficients, summary = FIT_MODULE.fit_joint(
            values,
            percentile=99.0,
            margin=1.1,
            ridge=0.1,
            decay_sec=0.35,
        )

        self.assertTrue(np.all(coefficients >= 0.0))
        self.assertGreaterEqual(summary["minimum_coefficient"], 0.0)
        baseline = float(coefficients[0])
        for feature_index in range(1, len(coefficients)):
            feature = np.zeros(len(coefficients), dtype=float)
            feature[0] = 1.0
            feature[feature_index] = 1.0
            self.assertGreaterEqual(float(coefficients @ feature), baseline)


if __name__ == "__main__":
    unittest.main()
