"""Camera adapter checks with injected fake acquisition and persistence."""
import unittest
from unittest.mock import Mock
import numpy as np
from src.applications.contour_dxf.service.contour_dxf_service import ContourDXFService

class CameraAdapterTests(unittest.TestCase):
    def setUp(self):
        self.camera = Mock()
        self.factory = Mock(return_value=self.camera)
        self.processor = Mock(return_value=(np.zeros((20, 30, 3), dtype=np.uint8),
            np.array([[0, 0], [120, 0], [120, 100], [0, 100]]), None, (120, 100)))
        self.persist = Mock()
        self.service = ContourDXFService(self.factory, self.processor, self.persist,
            source='fake', base_scale=1, correction=1.1, output_dir='/tmp', calibration_path='/tmp/fake.json')

    def test_lazy_start_and_reference_always_uses_nominal_raw_scale(self):
        self.factory.assert_not_called()
        self.service.start()
        self.service.calibrate(120, 100, 2)
        self.processor.assert_called_once_with(self.camera, 1, False)
        self.persist.assert_called_once()
        self.assertEqual(self.service.get_info().correction, 1)
        self.assertFalse(self.service.get_capture().exportable)
        self.service.capture(True)
        self.processor.assert_called_with(self.camera, 1, True)
        self.assertTrue(self.service.get_capture().exportable)
        self.service.stop()
        self.camera.stop.assert_called_once()

    def test_failed_persistence_preserves_previous_scale_and_disables_export(self):
        self.service.start()
        self.service.capture(True)
        self.persist.side_effect = OSError('disk unavailable')
        with self.assertRaises(OSError):
            self.service.calibrate(120, 100, 2)
        self.assertEqual(self.service.get_info().correction, 1.1)
        self.assertFalse(self.service.get_capture().exportable)
        with self.assertRaises(ValueError):
            self.service.export('/tmp/unused.dxf')

    def test_camera_start_failure_releases_camera_and_can_retry(self):
        self.camera.start.side_effect = RuntimeError('camera unavailable')
        with self.assertRaises(RuntimeError):
            self.service.start()
        self.camera.stop.assert_called_once()
        self.assertIsNone(self.service.get_live_frame())
        self.camera.start.side_effect = None
        self.service.start()
        self.service.stop()
