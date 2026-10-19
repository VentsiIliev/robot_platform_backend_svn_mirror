import unittest

import numpy as np

from collision_detection.calibration.modeling.zeroerr_motion_model_fit import (
    FEATURES,
    excitation_metrics,
    model_features,
    robust_fit,
)


class MotionModelFitTest(unittest.TestCase):
    def test_feature_vector_matches_runtime_model(self):
        values = model_features([0.0] * 6, 0.2, -0.4, 0.01, 0.05)
        self.assertEqual(len(FEATURES), len(values))
        self.assertGreater(values[0], 0.0)
        self.assertEqual(0.0, values[1])
        self.assertGreater(values[-1], 0.0)

    def test_linear_velocity_is_not_duplicated_in_motion_features(self):
        self.assertIn("viscous_velocity", FEATURES)
        self.assertNotIn("positive_velocity", FEATURES)
        self.assertNotIn("negative_velocity", FEATURES)

    def test_asymmetric_fit_requires_velocity_in_both_directions(self):
        design = np.zeros((200, len(FEATURES)))
        velocity_index = FEATURES.index("viscous_velocity")
        design[:100, velocity_index] = 0.2
        self.assertFalse(excitation_metrics(design)["identifiable"])
        design[100:, velocity_index] = -0.2
        self.assertTrue(excitation_metrics(design)["identifiable"])

    def test_friction_transition_is_continuous_at_zero(self):
        negative = model_features([0.0] * 6, -1.0e-8, 0.0, 0.01, 0.05)
        zero = model_features([0.0] * 6, 0.0, 0.0, 0.01, 0.05)
        positive = model_features([0.0] * 6, 1.0e-8, 0.0, 0.01, 0.05)
        self.assertLess(np.linalg.norm(np.asarray(negative[:5]) - zero[:5]), 2.0e-6)
        self.assertLess(np.linalg.norm(np.asarray(positive[:5]) - zero[:5]), 2.0e-6)

    def test_robust_fit_recovers_linear_coefficients_with_outlier(self):
        rng = np.random.default_rng(7)
        design = rng.normal(size=(2000, len(FEATURES)))
        expected = rng.normal(scale=0.2, size=len(FEATURES))
        target = design @ expected + rng.normal(scale=0.01, size=len(design))
        target[10] += 100.0
        actual = robust_fit(design, target, ridge=1.0e-4, huber_scale=1.5)
        np.testing.assert_allclose(actual, expected, atol=0.01)


if __name__ == "__main__":
    unittest.main()
