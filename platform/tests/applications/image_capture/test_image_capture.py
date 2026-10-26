import json
import os
from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
import cv2
import numpy as np
from PyQt6.QtCore import QEvent, Qt
from PyQt6.QtWidgets import QApplication

from src.applications.image_capture.image_capture_application_factory import ImageCaptureApplicationFactory
from src.applications.image_capture.model.image_capture_model import ImageCaptureModel
from src.applications.image_capture.service.image_capture_application_service import ImageCaptureApplicationService
from src.applications.image_capture.service.stub_image_capture_service import StubImageCaptureService
from src.engine.localization.dict_translator import DictTranslator
from src.engine.vision.i_vision_service import VisionFrameUnavailableError
from src.engine.vision.implementation.VisionSystem.VisionSystem import VisionSystem


class CaptureTests(unittest.TestCase):
    def test_saved_png_is_frozen_capture_and_names_are_unique(self):
        with TemporaryDirectory() as directory:
            frame = np.full((12, 20, 3), (5, 15, 230), dtype=np.uint8)
            vision = Mock()
            vision.capture_corrected_image.return_value = frame
            contour = np.array([[[2.5, 2]], [[8, 2]], [[8, 9]]])
            vision.detect_contours_for_image.return_value = [contour]
            service = ImageCaptureApplicationService(vision, directory)
            model = ImageCaptureModel(service)
            image = model.capture()
            np.testing.assert_array_equal(vision.detect_contours_for_image.call_args.args[0], frame)
            self.assertNotEqual(image.image, image.preview)
            frame[:] = 0
            contour[:] = 0
            model.save()
            first = Path(model.saved_path)
            model.save()
            self.assertNotEqual(str(first), model.saved_path)
            png = first / f"{first.name}.png"
            metadata = json.loads((first / f"{first.name}.json").read_text())
            self.assertEqual(png.read_bytes(), image.image)
            self.assertEqual(metadata["image_file"], png.name)
            self.assertEqual(metadata["contours"][0]["points"], [[2.5, 2], [8, 2], [8, 9]])
            self.assertEqual(metadata["coordinate_space"], "calibrated_image_pixels")
            self.assertEqual((metadata["width"], metadata["height"]), (20, 12))
            self.assertEqual(cv2.imread(str(png))[0, 0].tolist(), [5, 15, 230])
            vision.detect_contours_for_image.assert_called_once()
            vision.capture_corrected_image.assert_called_once()

    def test_empty_contours_are_saved_as_a_valid_pair(self):
        with TemporaryDirectory() as directory:
            service = ImageCaptureApplicationService(None, directory)
            folder = Path(service.save_image(StubImageCaptureService().capture()))
            self.assertEqual(len(list(folder.iterdir())), 4)
            metadata = json.loads((folder / f"{folder.name}.json").read_text())
            self.assertEqual(metadata["contours"], [])
            self.assertEqual(metadata["contour_count"], 0)

    def test_failed_second_file_write_leaves_no_half_pair(self):
        with TemporaryDirectory() as directory:
            service = ImageCaptureApplicationService(None, directory)
            with patch.object(Path, "write_text", side_effect=OSError("disk full")):
                with self.assertRaisesRegex(OSError, "disk full"):
                    service.save_image(StubImageCaptureService().capture())
            self.assertEqual(list(Path(directory).iterdir()), [])

    def test_detection_failure_clears_previous_capture(self):
        vision = Mock()
        vision.capture_corrected_image.return_value = np.zeros((20, 20, 3), np.uint8)
        vision.detect_contours_for_image.side_effect = [[], RuntimeError("detection failed")]
        model = ImageCaptureModel(ImageCaptureApplicationService(vision, "/tmp/unused"))
        model.capture()
        with self.assertRaisesRegex(RuntimeError, "detection failed"):
            model.capture()
        with self.assertRaises(ValueError):
            model.save()

    def test_detection_uses_supplied_pixels_and_work_area_without_recalibration(self):
        from src.engine.vision.implementation.VisionSystem.core.settings.CameraSettings import CameraSettings
        from src.engine.vision.implementation.VisionSystem.services.contour_detection_service import ContourDetectionService
        vision = VisionSystem.__new__(VisionSystem)
        vision._work_area_service = Mock()
        vision._work_area_service.get_active_area_id.return_value = "paint"
        vision._work_area_service.get_detection_roi_pixels.return_value = np.array(
            [[0, 0], [199, 0], [199, 199], [0, 199]], dtype=np.float32,
        )
        vision._get_thresh_by_area = Mock(return_value=150)
        vision._get_area_points_by_region = Mock(return_value=None)
        vision._contour_service = ContourDetectionService(CameraSettings())
        vision.frame_grabber = Mock()
        vision.correctImage = Mock(side_effect=AssertionError("Image already calibrated"))
        image = np.full((200, 200, 3), 255, np.uint8)
        image[40:150, 50:160] = 0
        original = image.copy()
        contours = vision.detect_contours_for_image(image)
        self.assertEqual(len(contours), 1)
        self.assertGreater(cv2.contourArea(contours[0]), 10000)
        np.testing.assert_array_equal(image, original)
        vision._get_thresh_by_area.assert_called_once_with("paint")
        vision._work_area_service.get_detection_roi_pixels.assert_called_once_with("paint", 200, 200)
        vision.frame_grabber.get_latest_snapshot.assert_not_called()
        vision.correctImage.assert_not_called()
        vision._work_area_service.get_active_area_id.side_effect = ["paint", "pickup"]
        with self.assertRaisesRegex(RuntimeError, "Work area changed"):
            vision.detect_contours_for_image(image)

    def test_only_contours_fully_inside_actual_image_roi_are_returned(self):
        from src.engine.vision.implementation.VisionSystem.core.settings.CameraSettings import CameraSettings
        from src.engine.vision.implementation.VisionSystem.services.contour_detection_service import ContourDetectionService
        from src.engine.work_areas.work_area_service import WorkAreaService
        from src.engine.work_areas.work_area_settings import WorkAreaSettings, WorkAreaConfig
        settings = Mock()
        settings.get.return_value = WorkAreaSettings(areas={
            "paint": WorkAreaConfig(detection_roi=[[0, 0], [0.4, 0], [0.4, 1], [0, 1]]),
        })
        vision = VisionSystem.__new__(VisionSystem)
        vision._work_area_service = WorkAreaService(settings, default_active_area_id="paint")
        vision._get_thresh_by_area = Mock(return_value=150)
        vision._contour_service = ContourDetectionService(CameraSettings())
        image = np.full((300, 500, 3), 255, np.uint8)
        image[40:110, 40:110] = 0       # fully inside
        image[40:110, 300:370] = 0     # fully outside
        image[170:240, 170:240] = 0    # crosses x=200 boundary
        contours = vision.detect_contours_for_image(image)
        self.assertEqual(len(contours), 1)
        self.assertTrue((contours[0].reshape(-1, 2)[:, 0] < 120).all())

    def test_missing_active_area_or_roi_never_detects_the_whole_image(self):
        vision = VisionSystem.__new__(VisionSystem)
        vision._active_area_id = "paint"  # stale cached state must not be reused
        vision._work_area_service = Mock()
        vision._work_area_service.get_active_area_id.return_value = None
        vision._contour_service = Mock()
        image = np.zeros((100, 200, 3), np.uint8)
        with self.assertRaisesRegex(RuntimeError, "No active work area"):
            vision.detect_contours_for_image(image)
        vision._work_area_service.get_active_area_id.return_value = "paint"
        for roi in (None, np.empty((0, 2), np.float32), np.zeros((3, 2), np.float32)):
            vision._work_area_service.get_detection_roi_pixels.return_value = roi
            with self.assertRaisesRegex(RuntimeError, "no valid detection region"):
                vision.detect_contours_for_image(image)
        vision._contour_service.detect.assert_not_called()

    def test_failed_recapture_does_not_save_old_image(self):
        service = Mock()
        service.capture.side_effect = [b"image", RuntimeError("offline")]
        model = ImageCaptureModel(service)
        model.capture()
        with self.assertRaisesRegex(RuntimeError, "offline"):
            model.capture()
        with self.assertRaises(ValueError):
            model.save()
        service.save_image.assert_not_called()

    def test_missing_vision_is_reported(self):
        with self.assertRaisesRegex(RuntimeError, "Vision service"):
            ImageCaptureApplicationService(None, "/tmp/unused").capture()

    def test_capture_uses_owned_fresh_frame_without_detection(self):
        vision = VisionSystem.__new__(VisionSystem)
        frame = np.zeros((3, 4, 3), dtype=np.uint8)
        vision.frame_grabber = Mock()
        vision.frame_grabber.get_latest_snapshot.return_value = SimpleNamespace(frame=frame)
        vision.cameraMatrix = np.eye(3)
        def correct(image):
            image[:] = 42
            return image
        vision.correctImage = Mock(side_effect=correct)
        captured = vision.capture_corrected_image()
        self.assertTrue((captured == 42).all())
        self.assertTrue((frame == 0).all())
        vision.cameraMatrix = None
        with self.assertRaisesRegex(RuntimeError, "calibration"):
            vision.capture_corrected_image()
        vision.frame_grabber.get_latest_snapshot.return_value = None
        with self.assertRaises(VisionFrameUnavailableError):
            vision.capture_corrected_image()


class CaptureUiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if QApplication.instance() is None:
            QApplication.setAttribute(Qt.ApplicationAttribute.AA_ShareOpenGLContexts)
        cls.app = QApplication.instance() or QApplication([])

    def test_initial_and_runtime_translation_and_preview(self):
        catalog = json.loads(Path("src/applications/image_capture/localization/bg.json").read_text())
        translator = DictTranslator(catalog)
        self.app.installTranslator(translator)
        widget = ImageCaptureApplicationFactory().build(StubImageCaptureService())
        try:
            self.assertEqual(widget._title.text(), "Заснемане на изображения")
            self.assertFalse(widget._save.isEnabled())
            widget.set_image(StubImageCaptureService().capture().preview)
            self.assertTrue(widget._save.isEnabled())
            widget.set_status("Saved: {detail}", "/tmp/capture.png")
            self.assertIn("Запазено:", widget._status.text())
            self.app.removeTranslator(translator)
            self.app.sendEvent(widget, QEvent(QEvent.Type.LanguageChange))
            self.assertEqual(widget._title.text(), "Image Capture")
            self.assertEqual(widget._status.text(), "Saved: /tmp/capture.png")
        finally:
            self.app.removeTranslator(translator)
            widget.clean_up()
            widget.close()

    def test_capture_and_save_worker_lifecycle(self):
        from PyQt6.QtTest import QTest
        service = StubImageCaptureService()
        widget = ImageCaptureApplicationFactory().build(service)
        controller = widget._controller
        try:
            widget._capture.click()
            self.assertFalse(widget._capture.isEnabled())
            for _ in range(300):
                QTest.qWait(10)
                if not controller.has_running_workers():
                    break
            self.assertFalse(controller.has_running_workers())
            self.assertTrue(widget._save.isEnabled())
            widget._save.click()
            for _ in range(300):
                QTest.qWait(10)
                if not controller.has_running_workers():
                    break
            self.assertFalse(controller.has_running_workers())
            self.assertEqual(widget._status.text(), "Saved: stub/capture_pair")
        finally:
            widget.clean_up()
            widget.close()

    def test_paint_and_glue_wiring_use_their_own_vision_and_storage(self):
        from src.robot_systems.paint.paint_robot_system import PaintRobotSystem
        from src.robot_systems.glue.glue_robot_system import GlueRobotSystem
        from src.engine.common_service_ids import CommonServiceID
        for system in (PaintRobotSystem, GlueRobotSystem):
            spec = next(s for s in system.shell.applications if s.name == "ImageCapture")
            robot = Mock()
            robot.storage_path.return_value = f"/tmp/{system.__name__}/captures"
            widget = spec.factory(robot).create_widget()
            try:
                robot.get_optional_service.assert_called_once_with(CommonServiceID.VISION)
                robot.storage_path.assert_called_once_with("captures")
                self.assertIn(system.__name__, widget._destination.text())
            finally:
                widget.clean_up()
                widget.close()

    def test_tray_dry_bootstrap_wires_profile_vision_and_capture_directory(self):
        from src.robot_systems.paint_tray_dry.bootstrap_provider import create_bootstrap_provider
        from src.engine.common_service_ids import CommonServiceID

        system = create_bootstrap_provider().system_class
        spec = next(s for s in system.shell.applications if s.name == "ImageCapture")
        self.assertEqual(spec.folder_id, 4)
        directory = system.storage_path("captures")
        self.assertTrue(directory.endswith("paint_tray_dry/storage/captures"))
        robot = Mock()
        robot.storage_path = system.storage_path
        widget = spec.factory(robot).create_widget()
        try:
            robot.get_optional_service.assert_called_once_with(CommonServiceID.VISION)
            service = widget._controller._model._service
            self.assertIs(service._vision, robot.get_optional_service.return_value)
            self.assertEqual(service.output_directory(), directory)
        finally:
            widget.clean_up()
            widget.close()


if __name__ == "__main__":
    unittest.main()
