import unittest

import numpy as np

from collision_detection.calibration.modeling.zeroerr_peak_threshold_calibrate import (
    calibrate_joint,
    longest_true_run,
)


class PeakThresholdCalibrateTest(unittest.TestCase):
    def test_longest_true_run(self):
        self.assertEqual(3, longest_true_run([False, True, True, True, False, True]))

    def test_persistence_guard_breaks_three_window_episode(self):
        values = []
        for index in range(1000):
            residual = 0.5
            if 400 <= index < 405:
                residual = 2.0
            values.append([index * 0.01, residual, 1.0, 0.0, 0.0])
        floor, delta, summary = calibrate_joint(
            values, percentile=99.9, margin_scale=1.1, margin_nm=0.1,
            stationary_velocity=0.02, stationary_acceleration=0.5,
            minimum_floor=0.5, persistence_windows=3,
        )
        self.assertGreaterEqual(floor, 0.5)
        self.assertGreater(delta, 1.0)
        self.assertLess(summary["proxy_max_consecutive_exceedance_windows"], 3)


if __name__ == "__main__":
    unittest.main()
