"""Camera adapter tests use a fake driver; no device or window is opened."""

from __future__ import annotations

import sys
import tempfile
import unittest
from dataclasses import dataclass, field, replace
from pathlib import Path
from unittest.mock import patch

import cv2
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from paint_head_detector.calibration import read_image  # noqa: E402
from paint_head_detector.configuration import ConfigurationRepository  # noqa: E402
from paint_head_detector.development.camera_session import CameraSession  # noqa: E402
from paint_head_detector.development.capture_application import CaptureApplication  # noqa: E402
from paint_head_detector.development.exposure import ExposureController  # noqa: E402
from paint_head_detector.development.options import parse_options  # noqa: E402
from paint_head_detector.development.settings import DevelopmentSettingsRepository  # noqa: E402
from paint_head_detector.errors import CameraError, ErrorReason  # noqa: E402
from paint_head_detector.models import Image, ImageSize  # noqa: E402


@dataclass
class FakeDriver:
    image: Image = field(default_factory=lambda: np.zeros((6, 8, 3), dtype=np.uint8))
    properties: dict[int, float] = field(
        default_factory=lambda: {cv2.CAP_PROP_AUTO_EXPOSURE: 3.0, cv2.CAP_PROP_EXPOSURE: 166.0}
    )
    failures: set[int] = field(default_factory=set)
    fail_reads: bool = False
    fail_open: bool = False


class FakeCapture:
    def __init__(self, driver: FakeDriver) -> None:
        self.driver = driver
        self.opened = not driver.fail_open

    def isOpened(self) -> bool:
        return self.opened

    def set(self, property_id: int, value: float) -> bool:
        if property_id in self.driver.failures:
            return False
        self.driver.properties[property_id] = value
        return True

    def get(self, property_id: int) -> float:
        return self.driver.properties.get(property_id, 0.0)

    def getBackendName(self) -> str:
        return "FAKE"

    def read(self) -> tuple[bool, Image | None]:
        return (False, None) if self.driver.fail_reads else (True, self.driver.image.copy())

    def grab(self) -> bool:
        return not self.driver.fail_reads

    def retrieve(self) -> tuple[bool, Image | None]:
        return self.read()

    def release(self) -> None:
        self.opened = False


class FakeCaptureFactory:
    def __init__(self, driver: FakeDriver) -> None:
        self.driver = driver
        self.instances: list[FakeCapture] = []

    def __call__(self, device: int | str, backend: int) -> FakeCapture:
        capture = FakeCapture(self.driver)
        self.instances.append(capture)
        return capture


class CameraTests(unittest.TestCase):
    def setUp(self) -> None:
        self.development = DevelopmentSettingsRepository().load()
        self.settings = replace(
            self.development.camera,
            open_timeout=0.01,
            retry_delay=0.001,
            configuration_settle_delay=0,
            control_settle_delay=0,
            stream_release_delay=0,
        )
        self.driver = FakeDriver()
        self.factory = FakeCaptureFactory(self.driver)

    def test_configured_stream_typed_properties_and_release(self) -> None:
        with patch("Camera.cv2.VideoCapture", side_effect=self.factory):
            with CameraSession(self.settings, ImageSize(8, 6)) as camera:
                self.assertEqual(8, camera.properties.width)
                self.assertEqual(6, camera.properties.height)
                self.assertEqual(self.settings.fps, camera.properties.fps)
                self.assertEqual("FAKE", camera.properties.backend_name)
                np.testing.assert_array_equal(self.driver.image, camera.read())
        self.assertTrue(self.factory.instances)
        self.assertTrue(all(not instance.opened for instance in self.factory.instances))

    def test_read_failure_is_specific_and_releases_camera(self) -> None:
        self.driver.fail_reads = True
        with patch("Camera.cv2.VideoCapture", side_effect=self.factory):
            with self.assertRaises(CameraError) as caught:
                with CameraSession(self.settings, ImageSize(8, 6)) as camera:
                    camera.read()
        self.assertIs(ErrorReason.CAMERA_READ_FAILED, caught.exception.reason)
        self.assertTrue(all(not instance.opened for instance in self.factory.instances))

    def test_open_failure_has_clear_reason(self) -> None:
        self.driver.fail_open = True
        with patch("Camera.cv2.VideoCapture", side_effect=self.factory):
            with self.assertRaises(CameraError) as caught:
                with CameraSession(self.settings, ImageSize(8, 6)):
                    self.fail("unavailable camera opened")
        self.assertIs(ErrorReason.CAMERA_UNAVAILABLE, caught.exception.reason)

    def test_backend_open_exception_is_chained(self) -> None:
        with patch("Camera.cv2.VideoCapture", side_effect=cv2.error("driver failure")):
            with self.assertRaises(CameraError) as caught:
                with CameraSession(self.settings, ImageSize(8, 6)):
                    self.fail("unavailable camera opened")
        self.assertIs(ErrorReason.CAMERA_UNAVAILABLE, caught.exception.reason)
        self.assertIsInstance(caught.exception.__cause__, cv2.error)

    def test_exposure_changes_restore_original_controls(self) -> None:
        with patch("Camera.cv2.VideoCapture", side_effect=self.factory):
            with CameraSession(self.settings, ImageSize(8, 6)) as camera:
                controller = ExposureController(camera, self.settings, self.development.runtime)
                self.assertEqual(100, controller.apply(100))
                self.assertEqual(1, camera.automatic_exposure)
                restoration = controller.restore()
                self.assertTrue(restoration.restored)
                self.assertEqual(166, camera.exposure)
                self.assertEqual(3, camera.automatic_exposure)
        self.assertTrue(all(not instance.opened for instance in self.factory.instances))

    def test_restore_reports_failure_but_still_restores_auto_mode(self) -> None:
        with patch("Camera.cv2.VideoCapture", side_effect=self.factory):
            with CameraSession(self.settings, ImageSize(8, 6)) as camera:
                controller = ExposureController(camera, self.settings, self.development.runtime)
                controller.apply(100)
                self.driver.failures.add(cv2.CAP_PROP_EXPOSURE)
                restoration = controller.restore()
                self.assertFalse(restoration.restored)
                self.assertTrue(restoration.message)
                self.assertEqual(3, camera.automatic_exposure)

    def test_capture_runner_returns_typed_summary_without_a_real_device(self) -> None:
        configuration = ConfigurationRepository().load()
        if not configuration.calibration.references.present.exists():
            self.skipTest("Local reference image is required")
        self.driver.image = read_image(configuration.calibration.references.present)
        with tempfile.TemporaryDirectory() as directory:
            options = parse_options(
                ["--duration", ".01", "--capture-dir", directory], capture_mode=True
            )
            options = replace(
                options, development=replace(options.development, camera=self.settings)
            )
            with (
                patch("Camera.cv2.VideoCapture", side_effect=self.factory),
                patch("cv2.namedWindow", side_effect=AssertionError("headless window")),
            ):
                result = CaptureApplication(options).run()
            self.assertTrue(result.report_path.exists())
            self.assertTrue(result.restoration.restored)
            self.assertGreaterEqual(result.levels[0].frames, 1)
        self.assertTrue(all(not instance.opened for instance in self.factory.instances))


if __name__ == "__main__":
    unittest.main()
