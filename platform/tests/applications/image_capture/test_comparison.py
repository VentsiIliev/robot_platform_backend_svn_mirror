import unittest
import numpy as np
from src.applications.image_capture.processing.comparison import compare_conversion, compare_fit


class ComparisonTests(unittest.TestCase):
    def test_reflection_rotation_and_scale_do_not_count_as_distortion(self):
        points = np.array([[0, 0], [100, 0], [100, 50], [0, 50]], float)
        converted = points @ np.array([[0, .5], [.5, 0]]) + [100, 200]
        result = compare_conversion(points, converted)
        self.assertLess(result['similarity_max_residual_mm'], 1e-10)
        self.assertAlmostEqual(result['similarity_scale_mm_per_pixel'], .5)
        converted[0] += [2, 0]
        self.assertGreater(compare_conversion(points, converted)['similarity_max_residual_mm'], .1)

    def test_finite_line_distance_and_join_gap(self):
        primitives = [{'type':'line', 'p0':[0,0], 'p1':[10,0]},
                      {'type':'line', 'p0':[12,0], 'p1':[0,0]}]
        result = compare_fit([[5,1], [15,0]], primitives)
        self.assertAlmostEqual(result['original_to_fit_max_mm'], 3)
        self.assertAlmostEqual(result['max_join_gap_mm'], 2)
