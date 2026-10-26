import json
from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace
import unittest
from unittest.mock import Mock

import numpy as np

from tests.engine.robot.path_preparation.test_default_workpiece_path_preparation_service import _make_service
from src.applications.image_capture.service.image_capture_application_service import ImageCaptureApplicationService


class RobotConversionTests(unittest.TestCase):
    def converter(self):
        resolver = Mock()
        resolver.resolve.side_effect = lambda request, target, frame: SimpleNamespace(
            final_xy=(request.x_pixels * 0.5 + 100, request.y_pixels * -0.5 + 200), z=request.z_mm,
        )
        return _make_service(resolver=resolver, target_point_name='camera',
                             calibration_frame_name='paint', pixel_to_mm_mode='homography_residual')

    def test_diagnostic_conversion_matches_paint_conversion(self):
        service = self.converter()
        points = np.array([[20, 30], [90, 30], [90, 100], [20, 100]], float)
        settings = {'height_mm': 0, 'spraying_height': '0', 'rz_angle': '0'}
        diagnostic = service.convert_contour_to_robot(points, settings)
        np.testing.assert_allclose(diagnostic['poses'], service._transform_to_robot(points, settings))
        self.assertEqual(diagnostic['poses'][0][:2], [110, 185])
        self.assertEqual(diagnostic['calibration_frame'], 'paint')

    def test_missing_calibration_never_exports_pixels_as_mm(self):
        with self.assertRaisesRegex(RuntimeError, 'calibration is unavailable'):
            _make_service().convert_contour_to_robot([[1, 2], [3, 4], [5, 6]])

    def test_capture_saves_converted_points_and_mm_decomposition(self):
        from src.robot_systems.paint.processes.paint.planning.contours.interpolation import resample_contour_xy
        converter = self.converter()
        vision = Mock()
        vision.capture_corrected_image.return_value = np.full((160, 160, 3), 200, np.uint8)
        vision.detect_contours_for_image.return_value = [np.array([[20, 20], [120, 20], [120, 120], [20, 120]])]
        with TemporaryDirectory() as directory:
            service = ImageCaptureApplicationService(vision, directory,
                robot_converter=converter.convert_contour_to_robot, work_area_getter=lambda: 'paint',
                contour_sampler=resample_contour_xy)
            capture = service.capture()
            data = json.loads(capture.robot_result)
            self.assertEqual(data['units'], 'mm')
            self.assertEqual(data['contours'][0]['points'][0], [110, 190])
            self.assertEqual(data['contours'][0]['status'], 'ok')
            self.assertTrue(capture.robot_preview)
            destination = Path(service.save_image(capture))
            self.assertEqual(len(list(destination.iterdir())), 8)
            exported = json.loads((destination / f'{destination.name}_robot_mm.json').read_text())
            self.assertEqual(exported['contours'], data['contours'])
            sampled = json.loads((destination / f'{destination.name}_sampled_mm.json').read_text())
            self.assertTrue(sampled['contours'][0]['points'])
            self.assertTrue(capture.sampled_preview)
            area = Mock(side_effect=['paint', 'magazine'])
            service._work_area_getter = area
            with self.assertRaisesRegex(RuntimeError, 'Work area changed'):
                service.capture()
