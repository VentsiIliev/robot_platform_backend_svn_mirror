import unittest
from unittest.mock import patch

import numpy as np

from scripts.safety.collision_detection.external_torque_estimator import (
    MomentumObserverEstimator,
)


class _UnitModel:
    num_joints = 1

    def compute_mass_matrix(self, positions):
        return np.ones((1, 1), dtype=float)

    def compute_observer_auxiliary(self, positions, velocities):
        return np.zeros(1, dtype=float)

    def compute_expected_torque(self, positions, velocities, accelerations):
        return np.asarray(accelerations, dtype=float)


class MomentumObserverEstimatorTests(unittest.TestCase):
    def test_warmup_requires_stationary_samples_as_well_as_elapsed_time(self):
        estimator = MomentumObserverEstimator(
            _UnitModel(), warmup_sec=1.0, warmup_min_samples=3,
            warmup_vel_threshold_rad_s=0.02,
        )
        measured = np.zeros(1)
        position = np.zeros(1)
        acceleration = np.zeros(1)

        with patch(
            "scripts.safety.collision_detection.external_torque_estimator.time.monotonic",
            side_effect=[0.0, 2.0, 3.0, 4.0, 5.0],
        ):
            estimator.update(measured, position, np.ones(1), acceleration)
            estimator.update(measured, position, np.ones(1), acceleration)
            self.assertFalse(estimator.ready)
            estimator.update(measured, position, np.zeros(1), acceleration)
            estimator.update(measured, position, np.zeros(1), acceleration)
            self.assertFalse(estimator.ready)
            estimator.update(measured, position, np.zeros(1), acceleration)

        self.assertTrue(estimator.ready)

    def test_nonfinite_input_is_rejected_without_poisoning_filter(self):
        estimator = MomentumObserverEstimator(_UnitModel(), warmup_sec=0.0)
        vector = np.zeros(1)
        estimator.update(vector, vector, vector, vector)

        with self.assertRaisesRegex(ValueError, "finite joint vectors"):
            estimator.update(vector, vector, np.array([np.nan]), vector)

        estimator.update(vector, vector, vector, vector)
        self.assertTrue(np.all(np.isfinite(estimator.filtered)))

    def test_expected_torque_history_uses_full_inverse_dynamics(self):
        estimator = MomentumObserverEstimator(_UnitModel(), warmup_sec=0.0)
        estimator.update(
            np.array([1.0]), np.zeros(1), np.zeros(1), np.array([1.0])
        )

        self.assertEqual(1.0, estimator.expected_torque_history[-1][0])
        self.assertEqual(0.0, estimator.observer_auxiliary_history[-1][0])


if __name__ == "__main__":
    unittest.main()
