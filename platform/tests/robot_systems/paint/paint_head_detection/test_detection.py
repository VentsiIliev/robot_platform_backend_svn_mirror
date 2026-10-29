"""Regression and integration tests for the typed, image-only detector API."""

from __future__ import annotations

import io
import json
import shutil
import tempfile
import unittest
from dataclasses import replace
from pathlib import Path
from typing import cast
from unittest.mock import patch

import cv2
import numpy as np

from src.robot_systems.paint.paint_head_detection import (  # noqa: E402
    CalibrationError,
    ConfigurationError,
    ConfigurationRepository,
    DetectionProcessingError,
    DetectionReason,
    DetectionResult,
    DetectorConfiguration,
    ErrorReason,
    HeadStatus,
    Image,
    InvalidImageError,
    PaintHeadDetector,
    Point2D,
    PoseEstimate,
    ReferencePaths,
)
from src.robot_systems.paint.paint_head_detection.calibration import CalibrationLoader, read_image  # noqa: E402
from src.robot_systems.paint.paint_head_detection.configuration import DEFAULT_CONFIG_DIRECTORY  # noqa: E402
from src.robot_systems.paint.paint_head_detection.decision import StatusStabilizer  # noqa: E402
from src.robot_systems.paint.paint_head_detection.development.artifacts import (  # noqa: E402
    ArtifactWriter,
    result_json,
)
from src.robot_systems.paint.paint_head_detection.development.options import parse_options  # noqa: E402
from src.robot_systems.paint.paint_head_detection.development.renderer import OverlayRenderer  # noqa: E402
from src.robot_systems.paint.paint_head_detection.development.settings import (
    DevelopmentSettingsRepository,  # noqa: E402
)
from src.robot_systems.paint.paint_head_detection.errors import ArtifactError  # noqa: E402
from src.robot_systems.paint.paint_head_detection.matching import FeatureMatcher
from src.robot_systems.paint.paint_head_detection.preprocessing import ImageProcessor  # noqa: E402
from src.robot_systems.paint.paint_head_detection.templates import _rotated_template  # noqa: E402


def test_configuration() -> DetectorConfiguration:
    config = ConfigurationRepository().load()
    return replace(
        config,
        alignment=replace(
            config.alignment,
            max_translation_pixels=10,
            max_rotation_degrees=5,
            hysteresis_pixels=2,
            hysteresis_degrees=1,
            unknown_grace_frames=3,
            unknown_grace_seconds=0.35,
            stable_frames=3,
        ),
    )


class DetectionRegressionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        config = test_configuration()
        if (
            not config.calibration.references.present.exists()
            or not config.calibration.references.missing.exists()
        ):
            raise unittest.SkipTest("Local calibration reference images are required")

    def setUp(self) -> None:
        self.configuration = test_configuration()
        self.references = CalibrationLoader().load(self.configuration)
        self.detector = PaintHeadDetector(self.configuration)
        cv2.setNumThreads(1)

    def raw_result(self, image: Image) -> DetectionResult:
        self.detector.reset()
        return self.detector.get_status(image)

    @staticmethod
    def signature(result: DetectionResult) -> tuple[object, ...]:
        return (
            result.status,
            result.observed_status,
            result.reason,
            result.alignment,
            result.held_warning,
            result.diagnostics.present,
            result.diagnostics.missing,
            result.diagnostics.pose,
            result.diagnostics.quality,
        )

    def moved_reference(self, dx: float = 0, dy: float = 0, angle: float = 0) -> Image:
        calibration = self.configuration.calibration
        x, y, width, height = calibration.inspection_region.coordinates
        center = np.mean(
            [feature.region.center for feature in calibration.present_features], axis=0
        ) - [x, y]
        matrix = cv2.getRotationMatrix2D((float(center[0]), float(center[1])), angle, 1)
        matrix[:, 2] += np.array([dx, dy])
        image = self.references.present_reference.copy()
        image[y : y + height, x : x + width] = cv2.warpAffine(
            image[y : y + height, x : x + width],
            matrix,
            (width, height),
            borderMode=cv2.BORDER_REPLICATE,
        )
        return image

    def test_presence_and_placement(self) -> None:
        cases = (
            (0, 0, 0, HeadStatus.HEAD_PRESENT),
            (6, 0, 0, HeadStatus.HEAD_PRESENT),
            (20, 0, 0, HeadStatus.HEAD_MISALIGNED),
            (0, -20, 0, HeadStatus.HEAD_MISALIGNED),
            (0, 0, 3, HeadStatus.HEAD_PRESENT),
            (0, 0, -10, HeadStatus.HEAD_MISALIGNED),
            (0, 0, 10, HeadStatus.HEAD_MISALIGNED),
        )
        for dx, dy, angle, expected in cases:
            with self.subTest(dx=dx, dy=dy, angle=angle):
                result = self.raw_result(self.moved_reference(dx, dy, angle))
                self.assertIs(expected, result.observed_status)
                self.assertIsNotNone(result.alignment)
                if result.alignment is not None:
                    self.assertEqual(expected is HeadStatus.HEAD_PRESENT, result.alignment.aligned)
        result = self.raw_result(self.references.missing_reference)
        self.assertIs(HeadStatus.HEAD_MISSING, result.observed_status)
        self.assertIsNone(result.alignment)

    def test_large_rotations_in_both_directions(self) -> None:
        for angle in (-175, -90, -60, -30, 30, 60, 90, 175):
            with self.subTest(angle=angle):
                result = self.raw_result(self.moved_reference(angle=angle))
                self.assertIs(HeadStatus.HEAD_MISALIGNED, result.observed_status)
                error = (result.diagnostics.pose.rotation_degrees - angle + 180) % 360 - 180
                self.assertLess(abs(error), 3)

    def test_configurable_limits(self) -> None:
        strict = PaintHeadDetector(
            replace(
                self.configuration,
                alignment=replace(
                    self.configuration.alignment, max_translation_pixels=5, max_rotation_degrees=2
                ),
            )
        )
        relaxed = PaintHeadDetector(
            replace(
                self.configuration,
                alignment=replace(
                    self.configuration.alignment, max_translation_pixels=25, max_rotation_degrees=12
                ),
            )
        )
        for image in (
            self.moved_reference(dx=6),
            self.moved_reference(angle=3),
            self.moved_reference(dx=20),
            self.moved_reference(angle=-10),
        ):
            strict.reset()
            relaxed.reset()
            self.assertIs(HeadStatus.HEAD_MISALIGNED, strict.get_status(image).observed_status)
            self.assertIs(HeadStatus.HEAD_PRESENT, relaxed.get_status(image).observed_status)

    def test_transition_and_confirmed_recovery(self) -> None:
        frames = self.configuration.alignment.stable_frames
        result = self.detector.get_status(self.references.present_reference)
        self.assertIs(HeadStatus.UNKNOWN, result.status)
        self.assertIs(DetectionReason.CONFIRMING_STATUS, result.reason)
        for _ in range(frames - 1):
            result = self.detector.get_status(self.references.present_reference)
        self.assertIs(HeadStatus.HEAD_PRESENT, result.status)
        shifted = self.moved_reference(dx=20)
        for index in range(frames):
            result = self.detector.get_status(shifted)
            self.assertIs(HeadStatus.HEAD_MISALIGNED, result.observed_status)
            self.assertIs(
                HeadStatus.HEAD_MISALIGNED if index == frames - 1 else HeadStatus.UNKNOWN,
                result.status,
            )
        self.assertIs(
            HeadStatus.HEAD_MISALIGNED,
            self.detector.get_status(self.references.present_reference).status,
        )
        for _ in range(frames - 1):
            result = self.detector.get_status(self.references.present_reference)
        self.assertIs(HeadStatus.HEAD_PRESENT, result.status)

    def test_hysteresis_clears_only_with_margin(self) -> None:
        frames = self.configuration.alignment.stable_frames
        for _ in range(frames):
            self.detector.get_status(self.moved_reference(dx=20))
        for _ in range(4):
            result = self.detector.get_status(self.moved_reference(dx=9))
            self.assertIs(HeadStatus.HEAD_MISALIGNED, result.status)
        for _ in range(frames):
            result = self.detector.get_status(self.moved_reference(dx=7))
        self.assertIs(HeadStatus.HEAD_PRESENT, result.status)
        self.detector.reset()
        with patch(
            "src.robot_systems.paint.paint_head_detection.decision.fitted_pose"
        ) as estimator:
            estimator.return_value = PoseEstimate(6, Point2D(0, 0))
            for _ in range(frames):
                result = self.detector.get_status(self.references.present_reference)
            self.assertIs(HeadStatus.HEAD_MISALIGNED, result.status)
            estimator.return_value = PoseEstimate(4.5, Point2D(0, 0))
            self.assertIs(
                HeadStatus.HEAD_MISALIGNED,
                self.detector.get_status(self.references.present_reference).observed_status,
            )
            estimator.return_value = PoseEstimate(3.5, Point2D(0, 0))
            for _ in range(frames):
                result = self.detector.get_status(self.references.present_reference)
            self.assertIs(HeadStatus.HEAD_PRESENT, result.status)

    def test_outside_pixels_and_camera_area_do_not_affect_results(self) -> None:
        calibration = self.configuration.calibration
        rng = np.random.default_rng(42)
        region = calibration.inspection_region.slices
        for reference in (self.references.present_reference, self.references.missing_reference):
            expected = self.signature(self.raw_result(reference))
            backgrounds = (
                np.zeros_like(reference),
                np.full_like(reference, 255),
                rng.integers(0, 256, reference.shape, dtype=np.uint8),
            )
            for image in backgrounds:
                image[region] = reference[region]
                for ignored in calibration.ignored_regions:
                    image[ignored.slices] = rng.integers(
                        0, 256, image[ignored.slices].shape, dtype=np.uint8
                    )
                self.assertEqual(expected, self.signature(self.raw_result(image)))

    def test_reference_background_is_ignored(self) -> None:
        calibration = self.configuration.calibration
        region = calibration.inspection_region.slices
        with tempfile.TemporaryDirectory() as directory:
            paths: list[Path] = []
            for name, original in (
                ("present", self.references.present_reference),
                ("missing", self.references.missing_reference),
            ):
                image = np.full_like(original, 255)
                image[region] = original[region]
                path = Path(directory) / f"{name}.png"
                self.assertTrue(cv2.imwrite(str(path), image))
                paths.append(path)
            configured = replace(
                self.configuration,
                calibration=replace(calibration, references=ReferencePaths(paths[0], paths[1])),
            )
            changed = PaintHeadDetector(configured)
            for image in (self.references.present_reference, self.references.missing_reference):
                changed.reset()
                self.assertEqual(
                    self.signature(self.raw_result(image)),
                    self.signature(changed.get_status(image)),
                )

    def test_lighting_changes(self) -> None:
        region = self.configuration.calibration.inspection_region
        x, y, width, height = region.coordinates
        for expected, reference in (
            (HeadStatus.HEAD_PRESENT, self.references.present_reference),
            (HeadStatus.HEAD_MISSING, self.references.missing_reference),
        ):
            roi = reference[region.slices].astype(float)
            variants = (
                roi,
                roi * 0.5,
                roi * 1.5,
                roi - 30,
                roi + 30,
                255 * (roi / 255) ** 0.7,
                255 * (roi / 255) ** 1.5,
                roi * np.linspace(0.6, 1.4, width)[None, :, None],
                roi * np.linspace(0.6, 1.4, height)[:, None, None],
                roi * np.where(np.arange(width) < width // 2, 0.6, 1.0)[None, :, None],
            )
            for index, altered in enumerate(variants):
                with self.subTest(status=expected, lighting=index):
                    image = reference.copy()
                    image[y : y + height, x : x + width] = np.clip(altered, 0, 255).astype(np.uint8)
                    self.detector.reset()
                    for _ in range(self.configuration.alignment.stable_frames):
                        result = self.detector.get_status(image)
                        self.assertIs(expected, result.observed_status)
                    self.assertIs(expected, result.status)

    def test_bad_exposure_clears_green(self) -> None:
        for value, reason in (
            (0, DetectionReason.TOO_DARK),
            (255, DetectionReason.OVEREXPOSED),
            (100, DetectionReason.LOW_CONTRAST),
        ):
            for _ in range(self.configuration.alignment.stable_frames):
                result = self.detector.get_status(self.references.present_reference)
            self.assertIs(HeadStatus.HEAD_PRESENT, result.status)
            image = self.references.present_reference.copy()
            image[self.configuration.calibration.inspection_region.slices] = value
            result = self.detector.get_status(image)
            self.assertIs(HeadStatus.UNKNOWN, result.status)
            self.assertIs(reason, result.reason)

    def test_search_candidates_stay_inside_roi(self) -> None:
        config = self.configuration
        processor = ImageProcessor(
            config.calibration,
            config.preprocessing,
            self.references.size,
            config.matching.edge_distance_sigma,
        )
        present = processor.process(self.references.present_reference)
        missing = processor.process(self.references.missing_reference)
        matcher = FeatureMatcher(present.edges, missing.edges, config.calibration, config.matching)
        bounds = config.calibration.inspection_region
        for feature in config.calibration.present_features:
            candidates = matcher.candidates(present.edges, present.proximity, feature)
            self.assertTrue(candidates)
            for candidate in candidates:
                template, _ = _rotated_template(present.edges, feature, candidate.angle_degrees)
                height, width = template.shape
                cx, cy = candidate.center
                self.assertGreaterEqual(cx - width / 2, bounds.x)
                self.assertGreaterEqual(cy - height / 2, bounds.y)
                self.assertLessEqual(cx + width / 2, bounds.x + bounds.width)
                self.assertLessEqual(cy + height / 2, bounds.y + bounds.height)

    def test_invalid_input_contract_has_specific_errors_and_resets_state(self) -> None:
        size = self.references.size
        cases: tuple[tuple[object, ErrorReason], ...] = (
            (None, ErrorReason.IMAGE_TYPE_INVALID),
            (np.zeros((size.height, size.width, 3), np.float32), ErrorReason.IMAGE_DTYPE_INVALID),
            (np.zeros((size.height, size.width), np.uint8), ErrorReason.IMAGE_SHAPE_INVALID),
            (np.zeros((5, 5, 3), np.uint8), ErrorReason.IMAGE_SIZE_MISMATCH),
        )
        for image, expected in cases:
            with self.subTest(reason=expected), self.assertRaises(InvalidImageError) as caught:
                self.detector.get_status(cast(Image, image))
            self.assertIs(expected, caught.exception.reason)
            self.assertTrue(caught.exception.message)
        for _ in range(self.configuration.alignment.stable_frames):
            self.detector.get_status(self.references.present_reference)
        with self.assertRaises(InvalidImageError):
            self.detector.get_status(cast(Image, None))
        self.assertIs(
            HeadStatus.UNKNOWN, self.detector.get_status(self.references.present_reference).status
        )

    def test_backend_failure_is_typed_chained_and_clears_state(self) -> None:
        with patch.object(ImageProcessor, "process", side_effect=cv2.error("test backend failure")):
            with self.assertRaises(DetectionProcessingError) as caught:
                self.detector.get_status(self.references.present_reference)
        self.assertIs(ErrorReason.PROCESSING_FAILED, caught.exception.reason)
        self.assertIsInstance(caught.exception.__cause__, cv2.error)
        self.assertIs(
            HeadStatus.UNKNOWN, self.detector.get_status(self.references.present_reference).status
        )

    def test_image_api_has_no_ui_camera_or_print_side_effects(self) -> None:
        output = io.StringIO()
        with (
            patch("cv2.VideoCapture", side_effect=AssertionError("camera access")),
            patch("cv2.namedWindow", side_effect=AssertionError("window access")),
            patch("cv2.imshow", side_effect=AssertionError("GUI access")),
            unittest.mock.patch("sys.stdout", output),
        ):
            detector = PaintHeadDetector(self.configuration)
            result = detector.get_status(self.references.present_reference)
        self.assertIsInstance(result, DetectionResult)
        self.assertEqual("", output.getvalue())

    def test_input_is_unchanged_and_diagnostic_edges_are_readonly(self) -> None:
        image = self.references.present_reference.copy()
        original = image.copy()
        result = self.detector.get_status(image)
        np.testing.assert_array_equal(original, image)
        self.assertFalse(result.diagnostics.edges.flags.writeable)
        self.assertIsInstance(result.status, HeadStatus)
        self.assertIsInstance(result.reason, DetectionReason)

    def test_development_artifacts_use_typed_results(self) -> None:
        view = DevelopmentSettingsRepository().load().view
        renderer = OverlayRenderer(self.configuration, view)
        result = self.raw_result(self.moved_reference(angle=-10))
        writer = ArtifactWriter(renderer)
        with tempfile.TemporaryDirectory() as directory:
            artifacts = writer.save(Path(directory), self.references.present_reference, result)
            self.assertTrue(artifacts.raw_image.exists())
            self.assertTrue(artifacts.overlay_image.exists())
            self.assertTrue(artifacts.metadata.exists())
            np.testing.assert_array_equal(
                self.references.present_reference, read_image(artifacts.raw_image)
            )
            payload = result_json(result)
            self.assertEqual(result.status.value, payload["state"])

    def test_artifact_failure_has_specific_error(self) -> None:
        renderer = OverlayRenderer(self.configuration, DevelopmentSettingsRepository().load().view)
        result = self.raw_result(self.references.present_reference)
        with tempfile.TemporaryDirectory() as directory, patch("cv2.imwrite", return_value=False):
            with self.assertRaises(ArtifactError) as caught:
                ArtifactWriter(renderer).save(
                    Path(directory), self.references.present_reference, result
                )
        self.assertIs(ErrorReason.ARTIFACT_WRITE_FAILED, caught.exception.reason)

    def test_external_config_has_no_development_dependency(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            config_directory = root / "settings"
            shutil.copytree(DEFAULT_CONFIG_DIRECTORY, config_directory)
            assets = root / "assets"
            assets.mkdir()
            shutil.copy2(self.configuration.calibration.references.present, assets / "present.png")
            shutil.copy2(self.configuration.calibration.references.missing, assets / "missing.png")
            (config_directory / "references.json").write_text(
                json.dumps({"present": "../assets/present.png", "missing": "../assets/missing.png"})
            )
            (config_directory / "development.json").unlink()
            detector = PaintHeadDetector(config_directory=config_directory)
            result = detector.get_status(self.references.present_reference)
            self.assertIs(HeadStatus.HEAD_PRESENT, result.observed_status)


class ConfigurationTests(unittest.TestCase):
    def test_invalid_typed_limits(self) -> None:
        config = test_configuration()
        for alignment in (
            replace(config.alignment, max_translation_pixels=-1),
            replace(config.alignment, max_rotation_degrees=float("nan")),
            replace(config.alignment, unknown_grace_seconds=float("inf")),
        ):
            with self.subTest(alignment=alignment), self.assertRaises(ConfigurationError) as caught:
                replace(config, alignment=alignment).validate()
            self.assertIs(ErrorReason.CONFIGURATION_INVALID, caught.exception.reason)

    def test_missing_and_malformed_files(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)
            with self.assertRaises(ConfigurationError) as missing:
                ConfigurationRepository(path).load()
            self.assertIs(ErrorReason.CONFIGURATION_NOT_FOUND, missing.exception.reason)
            (path / "matching.json").write_text("{ invalid", encoding="utf-8")
            with self.assertRaises(ConfigurationError) as malformed:
                ConfigurationRepository(path).load()
            self.assertIs(ErrorReason.CONFIGURATION_INVALID, malformed.exception.reason)

    def test_cli_overrides_are_typed_and_preserve_files(self) -> None:
        before = (DEFAULT_CONFIG_DIRECTORY / "alignment.json").read_text()
        options = parse_options(["--alignment-pixels", "25", "--alignment-degrees", "12"])
        self.assertEqual(25, options.configuration.alignment.max_translation_pixels)
        self.assertEqual(12, options.configuration.alignment.max_rotation_degrees)
        self.assertEqual(before, (DEFAULT_CONFIG_DIRECTORY / "alignment.json").read_text())

    def test_unreadable_calibration_has_specific_error(self) -> None:
        config = test_configuration()
        configured = replace(
            config,
            calibration=replace(
                config.calibration,
                references=ReferencePaths(
                    Path("/tmp/paint_head_missing_reference_test.png"),
                    config.calibration.references.missing,
                ),
            ),
        )
        with self.assertRaises(CalibrationError) as caught:
            PaintHeadDetector(configured)
        self.assertIs(ErrorReason.REFERENCE_UNREADABLE, caught.exception.reason)


class StatusStabilizerTests(unittest.TestCase):
    def make_filter(self) -> StatusStabilizer:
        return StatusStabilizer(test_configuration().alignment)

    def confirm_misalignment(self, filtering: StatusStabilizer) -> None:
        for now in (0.0, 0.05, 0.10):
            status = filtering.update(
                HeadStatus.HEAD_MISALIGNED, partial_presence=True, invalid=False, now=now
            )
        self.assertIs(HeadStatus.HEAD_MISALIGNED, status)

    def test_partial_dropouts_do_not_interrupt_warning(self) -> None:
        filtering = self.make_filter()
        self.confirm_misalignment(filtering)
        for now, observed in (
            (0.15, HeadStatus.UNKNOWN),
            (0.20, HeadStatus.HEAD_MISALIGNED),
            (0.25, HeadStatus.UNKNOWN),
            (0.30, HeadStatus.UNKNOWN),
        ):
            self.assertIs(
                HeadStatus.HEAD_MISALIGNED,
                filtering.update(observed, partial_presence=True, invalid=False, now=now),
            )
        self.assertIs(
            HeadStatus.UNKNOWN,
            filtering.update(HeadStatus.UNKNOWN, partial_presence=True, invalid=False, now=0.60),
        )

    def test_interleaved_partial_frames_can_confirm_warning(self) -> None:
        filtering = self.make_filter()
        for now, observed in (
            (0.0, HeadStatus.HEAD_MISALIGNED),
            (0.05, HeadStatus.UNKNOWN),
            (0.10, HeadStatus.HEAD_MISALIGNED),
            (0.15, HeadStatus.UNKNOWN),
            (0.20, HeadStatus.HEAD_MISALIGNED),
        ):
            status = filtering.update(observed, partial_presence=True, invalid=False, now=now)
        self.assertIs(HeadStatus.HEAD_MISALIGNED, status)

    def test_grace_is_bounded_by_frames_and_time(self) -> None:
        for times in ((0.11, 0.12, 0.13, 0.14), (0.50,)):
            filtering = self.make_filter()
            self.confirm_misalignment(filtering)
            for now in times:
                status = filtering.update(
                    HeadStatus.UNKNOWN, partial_presence=True, invalid=False, now=now
                )
            self.assertIs(HeadStatus.UNKNOWN, status)

    def test_invalid_or_absent_evidence_clears_warning(self) -> None:
        for partial, invalid in ((False, False), (True, True)):
            filtering = self.make_filter()
            self.confirm_misalignment(filtering)
            self.assertIs(
                HeadStatus.UNKNOWN,
                filtering.update(
                    HeadStatus.UNKNOWN, partial_presence=partial, invalid=invalid, now=0.15
                ),
            )

    def test_green_is_never_held_across_uncertainty(self) -> None:
        filtering = self.make_filter()
        for now in (0.0, 0.05, 0.10):
            status = filtering.update(
                HeadStatus.HEAD_PRESENT, partial_presence=True, invalid=False, now=now
            )
        self.assertIs(HeadStatus.HEAD_PRESENT, status)
        self.assertIs(
            HeadStatus.UNKNOWN,
            filtering.update(HeadStatus.UNKNOWN, partial_presence=True, invalid=False, now=0.15),
        )


if __name__ == "__main__":
    unittest.main()
