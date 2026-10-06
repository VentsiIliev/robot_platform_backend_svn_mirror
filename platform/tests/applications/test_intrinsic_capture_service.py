import unittest
from types import SimpleNamespace
from unittest.mock import MagicMock

from src.applications.intrinsic_calibration_capture.service.intrinsic_capture_service import (
    IntrinsicCaptureService,
)


class TestIntrinsicCaptureRawFrames(unittest.TestCase):
    def _service(self, vision):
        return IntrinsicCaptureService(
            robot_service=MagicMock(), vision_service=vision, robot_config=MagicMock(),
        )

    def test_capture_uses_raw_frame_without_processed_frame_fallback(self):
        frame = object()
        vision = SimpleNamespace(
            get_latest_raw_frame=MagicMock(return_value=frame),
            get_latest_frame=MagicMock(),
        )
        self.assertIs(self._service(vision)._get_capture_frame(), frame)
        vision.get_latest_raw_frame.assert_called_once_with()
        vision.get_latest_frame.assert_not_called()

    def test_capture_rejects_missing_vision_service(self):
        with self.assertRaisesRegex(RuntimeError, "Vision service unavailable"):
            self._service(None)._get_capture_frame()

    def test_capture_rejects_service_without_raw_frame_api(self):
        vision = SimpleNamespace(get_latest_frame=MagicMock())
        with self.assertRaisesRegex(RuntimeError, "requires raw images"):
            self._service(vision)._get_capture_frame()
        vision.get_latest_frame.assert_not_called()

    def test_capture_rejects_missing_raw_frame_without_processed_fallback(self):
        vision = SimpleNamespace(
            get_latest_raw_frame=MagicMock(return_value=None),
            get_latest_frame=MagicMock(),
        )
        with self.assertRaisesRegex(RuntimeError, "returned no raw frame"):
            self._service(vision)._get_capture_frame()
        vision.get_latest_frame.assert_not_called()


if __name__ == "__main__":
    unittest.main()
