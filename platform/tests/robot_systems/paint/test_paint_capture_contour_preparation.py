import copy
from types import SimpleNamespace
import unittest
from unittest.mock import MagicMock

import numpy as np

from src.robot_systems.paint.application_wiring import _build_paint_path_preparation_service
from src.robot_systems.paint.domain.paint_capture_contour_preparation import PaintCaptureContourPreparation


class _Transformer:
    def is_available(self):
        return True

    def transform(self, x, y):
        return 100.0 - 0.5 * y, 200.0 + 0.5 * x


class TestPaintCaptureContourPreparation(unittest.TestCase):
    def test_editable_contour_matches_production_points_without_processing_twice(self):
        system = SimpleNamespace(
            _robot_config=None, _navigation=None,
            get_target_point_definition=lambda name: None,
            get_target_frame_for_work_area=lambda area: None,
            get_shared_vision_resolver=lambda: (_Transformer(), None),
            system_config=SimpleNamespace(BYPASS_CONTOUR_PREPARATION=False),
        )
        service = _build_paint_path_preparation_service(system)
        raw = {"contour": [[0.0, 0.0], [20.0, 0.0], [20.2, 10.0], [20.0, 20.0], [0.0, 20.0]],
               "matchingContour": [[1.25, 2.5], [21.5, 2.5], [21.5, 22.5]]}
        original = copy.deepcopy(raw)

        prepared = PaintCaptureContourPreparation(service)(raw)
        pixels = prepared["contour"]
        production = service.build_execution_plan(raw, skip_debug_plot=True)
        converted = [_Transformer().transform(*point) for point in pixels]

        np.testing.assert_allclose(converted, np.asarray(production.prepared_paths[0])[:, :2], atol=1e-8)
        self.assertGreater(len(pixels), len(raw["contour"]))
        self.assertEqual(original, raw)
        self.assertEqual(raw["matchingContour"], prepared["matchingContour"])
        self.assertTrue(prepared["paint_contour_prepared"])

        # Reloading/repreparing already edited points must not smooth them.
        prepared["contour"][4][0] += 1.25
        untouched = copy.deepcopy(prepared)
        again = PaintCaptureContourPreparation(service)(prepared)
        self.assertEqual(untouched, again)
        plan = service.build_execution_plan(again, skip_debug_plot=True)
        np.testing.assert_allclose(plan.raw_paths[0], plan.prepared_paths[0], atol=1e-8)

    def test_original_capture_is_kept_for_matching_and_full_paint_copy_is_updated(self):
        service = MagicMock()
        source = [[0., 0.], [10., 0.], [10., 10.], [0., 10.]]
        processed = [[0.1, 0.1], [9.9, 0.1], [9.9, 9.9], [0.1, 9.9]]
        service.build_execution_plan.return_value = SimpleNamespace(
            raw_pixel_paths=[source], raw_paths=[source], prepared_paths=[processed])
        raw = {"contour": source, "sprayPattern": {"Contour": [
            {"contour": source, "settings": {"paint_selection_source": True}},
            {"contour": source[:2], "settings": {"closed_path": False}},
        ]}}
        prepared = PaintCaptureContourPreparation(service)(raw)
        self.assertEqual(source, prepared["matchingContour"])
        np.testing.assert_allclose(processed, prepared["contour"])
        np.testing.assert_allclose(processed, prepared["sprayPattern"]["Contour"][0]["contour"])
        self.assertEqual(source[:2], prepared["sprayPattern"]["Contour"][1]["contour"])

    def test_inverse_uses_actual_calibration_instead_of_an_affine_approximation(self):
        def forward(points, settings):
            return {"poses": [[x + 0.03 * y * y, y] for x, y in points]}

        source = np.asarray([[0, 0], [10, 0], [10, 10], [0, 10], [0, 5]], dtype=float)
        robot = np.asarray(forward(source, {})["poses"])
        expected = np.asarray([[1, 2], [8, 9], [2, 7]], dtype=float)
        processed = np.asarray(forward(expected, {})["poses"])
        service = MagicMock()
        service.convert_contour_to_robot.side_effect = forward

        actual = PaintCaptureContourPreparation(service)._to_pixels(source, robot, processed, {})

        np.testing.assert_allclose(actual, expected, atol=1e-5)
        self.assertTrue(service.convert_contour_to_robot.called)

    def test_degenerate_contour_fails_instead_of_drawing_invalid_points(self):
        points = np.asarray([[0, 0], [1, 0], [2, 0]], dtype=float)
        with self.assertRaisesRegex(ValueError, "two-dimensional"):
            PaintCaptureContourPreparation(MagicMock())._to_pixels(points, points, points, {})
