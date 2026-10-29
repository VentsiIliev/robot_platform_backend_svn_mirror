"""Contract tests for external calibration, atomic updates, and the second integration."""

from __future__ import annotations

import io
import shutil
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from dataclasses import replace
from pathlib import Path
from typing import cast
from unittest.mock import patch

import cv2
import numpy as np
from examples.get_status import HeadlessApplication, InputImageError, main
from examples.settings import ExampleSettings

from paint_head_detector import (
    CalibrationError,
    ConfigurationError,
    ConfigurationRepository,
    ErrorReason,
    FeatureRole,
    HeadStatus,
    Image,
    PaintHeadDetector,
    ReferenceImages,
    Region,
)
from paint_head_detector.calibration import CalibrationLoader
from paint_head_detector.configuration import DEFAULT_CONFIG_DIRECTORY
from paint_head_detector.development.application import prepare_configuration
from paint_head_detector.development.options import parse_options
from paint_head_detector.development.selection import (
    FeatureSelectionResult,
    FeatureSelector,
    SelectionOutcome,
)


class ExternalConfigurationTests(unittest.TestCase):
    def setUp(self) -> None:
        cv2.setNumThreads(1)
        self.configuration = ConfigurationRepository().load()
        loaded = CalibrationLoader().load(self.configuration)
        self.references = ReferenceImages(loaded.present_reference, loaded.missing_reference)
        self.calibration = replace(self.configuration.calibration, references=self.references)
        self.detector = PaintHeadDetector(self.configuration, calibration=self.calibration)

    def confirm_present(self) -> None:
        for _ in range(self.configuration.alignment.stable_frames):
            result = self.detector.get_status(self.references.present)
        self.assertIs(HeadStatus.HEAD_PRESENT, result.status)

    def test_external_calibration_requires_only_algorithm_files(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            config_dir = Path(directory)
            for filename in ("matching.json", "preprocessing.json", "alignment.json"):
                shutil.copy2(DEFAULT_CONFIG_DIRECTORY / filename, config_dir / filename)
            with patch("cv2.imread", side_effect=AssertionError("Unexpected reference file I/O")):
                detector = PaintHeadDetector(
                    config_directory=config_dir, calibration=self.calibration
                )
                result = detector.get_status(self.references.present)
        self.assertIs(HeadStatus.HEAD_PRESENT, result.observed_status)
        self.assertEqual(1, result.configuration_revision)

    def test_typed_configuration_needs_no_configuration_files(self) -> None:
        configuration = replace(self.configuration, calibration=self.calibration)
        with patch.object(ConfigurationRepository, "load", side_effect=AssertionError("File I/O")):
            detector = PaintHeadDetector(configuration)
            result = detector.get_status(self.references.missing)
        self.assertIs(HeadStatus.HEAD_MISSING, result.observed_status)

    def test_caller_references_are_owned_immutable_snapshots(self) -> None:
        present, missing = self.references.present.copy(), self.references.missing.copy()
        detector = PaintHeadDetector(
            self.configuration,
            calibration=replace(self.calibration, references=ReferenceImages(present, missing)),
        )
        self.assertTrue(present.flags.writeable)
        self.assertTrue(missing.flags.writeable)
        present.fill(0)
        missing.fill(255)
        np.testing.assert_array_equal(self.references.present, detector.reference_images.present)
        np.testing.assert_array_equal(self.references.missing, detector.reference_images.missing)
        for image in (detector.reference_images.present, detector.reference_images.missing):
            with self.assertRaises(ValueError):
                image.setflags(write=True)
        self.assertIs(
            detector.reference_images.present, detector.configuration.calibration.references.present
        )

    def test_invalid_references_preserve_revision_configuration_and_state(self) -> None:
        self.confirm_present()
        original = self.detector.configuration
        cases = (
            (cast(Image, None), ErrorReason.REFERENCE_IMAGE_INVALID),
            (
                cast(Image, self.references.present.astype(np.float32)),
                ErrorReason.REFERENCE_IMAGE_INVALID,
            ),
            (self.references.present[:, :, 0], ErrorReason.REFERENCE_IMAGE_INVALID),
            (self.references.present[:-1], ErrorReason.REFERENCE_SIZE_MISMATCH),
        )
        for image, reason in cases:
            with self.subTest(reason=reason):
                with self.assertRaises(CalibrationError) as caught:
                    self.detector.set_reference_images(
                        ReferenceImages(image, self.references.missing)
                    )
                self.assertIs(reason, caught.exception.reason)
                self.assertTrue(caught.exception.message)
                self.assertIs(original, self.detector.configuration)
                self.assertEqual(1, self.detector.configuration_revision)
                self.assertIs(
                    HeadStatus.HEAD_PRESENT,
                    self.detector.get_status(self.references.present).status,
                )

    def test_roi_and_features_reuse_references_and_reset_confirmation(self) -> None:
        self.confirm_present()
        features = [replace(f, name=f"host_{f.name}") for f in self.calibration.present_features]
        with patch("cv2.imread", side_effect=AssertionError("Unexpected reference reload")):
            update = self.detector.set_features(features, missing=self.calibration.missing_features)
            features.clear()
            self.assertEqual(2, update.revision)
            self.assertEqual(3, update.present_feature_count)
            self.assertEqual(len(self.calibration.missing_features), update.missing_feature_count)
            result = self.detector.get_status(self.references.present)
            self.assertIs(HeadStatus.UNKNOWN, result.status)
            self.assertIs(HeadStatus.HEAD_PRESENT, result.observed_status)
            self.assertTrue(
                all(m.feature.name.startswith("host_") for m in result.diagnostics.present.matches)
            )
            roi = self.calibration.inspection_region
            replacement_roi = replace(roi, x=roi.x + 5, width=roi.width - 5)
            update = self.detector.set_roi(
                replacement_roi,
                empty_mount_region=self.calibration.empty_mount_region,
                ignored_regions=list(self.calibration.ignored_regions),
            )
            self.assertEqual(3, update.revision)
            self.assertEqual(replacement_roi, update.configuration.calibration.inspection_region)
            self.assertIs(
                self.detector.reference_images.present,
                self.detector.configuration.calibration.references.present,
            )
            result = self.detector.get_status(self.references.present)
            self.assertEqual(3, result.configuration_revision)
            self.assertFalse(np.any(result.diagnostics.edges[:, : replacement_roi.x]))

    def test_invalid_settings_and_features_are_atomic(self) -> None:
        self.confirm_present()
        original = self.detector.configuration
        feature = self.calibration.present_features[0]
        invalid_feature_groups = (
            (feature,),
            (replace(feature, role=FeatureRole.MISSING), *self.calibration.present_features[1:]),
            (
                replace(feature, max_template_rotation=float("nan")),
                *self.calibration.present_features[1:],
            ),
            (replace(feature, region=Region(0, 0, 20, 20)), *self.calibration.present_features[1:]),
        )
        for features in invalid_feature_groups:
            with self.subTest(features=features), self.assertRaises(ConfigurationError):
                self.detector.set_features(features)
        with self.assertRaises(ConfigurationError):
            self.detector.set_roi(Region(0, 0, 10, 10))
        with self.assertRaises(ConfigurationError):
            self.detector.configure(
                replace(original, alignment=replace(original.alignment, stable_frames=0))
            )
        self.assertEqual(1, self.detector.configuration_revision)
        self.assertIs(original, self.detector.configuration)
        self.assertIs(
            HeadStatus.HEAD_PRESENT, self.detector.get_status(self.references.present).status
        )

    def test_preparation_failure_is_atomic_and_reports_cause(self) -> None:
        self.confirm_present()
        original = self.detector.configuration
        with patch("cv2.Canny", side_effect=cv2.error("reference preparation failed")):
            with self.assertRaises(CalibrationError) as caught:
                self.detector.set_roi(self.calibration.inspection_region)
        self.assertIs(ErrorReason.PROCESSING_FAILED, caught.exception.reason)
        self.assertIsInstance(caught.exception.__cause__, cv2.error)
        self.assertIs(original, self.detector.configuration)
        self.assertEqual(1, self.detector.configuration_revision)
        self.assertIs(
            HeadStatus.HEAD_PRESENT, self.detector.get_status(self.references.present).status
        )

    def test_full_configuration_and_reference_updates(self) -> None:
        self.confirm_present()
        changed = replace(
            self.detector.configuration,
            alignment=replace(
                self.configuration.alignment, stable_frames=1, max_rotation_degrees=7
            ),
        )
        updated = self.detector.configure(changed)
        self.assertEqual(2, updated.revision)
        self.assertEqual(7, updated.configuration.alignment.max_rotation_degrees)
        updated = self.detector.set_reference_images(self.configuration.calibration.references)
        self.assertEqual(3, updated.revision)
        result = self.detector.get_status(self.references.present)
        self.assertIs(HeadStatus.HEAD_PRESENT, result.status)
        self.assertEqual(updated.revision, result.configuration_revision)

    def test_headless_integration_uses_no_camera_or_gui(self) -> None:
        configuration = replace(
            self.configuration,
            alignment=replace(self.configuration.alignment, stable_frames=1),
        )
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "frame.png"
            self.assertTrue(cv2.imwrite(str(path), self.references.present))
            with (
                patch("cv2.VideoCapture", side_effect=AssertionError("Camera access")),
                patch("cv2.namedWindow", side_effect=AssertionError("GUI access")),
                patch("cv2.imshow", side_effect=AssertionError("GUI access")),
                patch("cv2.waitKey", side_effect=AssertionError("GUI access")),
            ):
                app = HeadlessApplication(configuration, calibration=self.calibration)
                inspections = app.run([path, path], independent_images=True)
                self.assertEqual(2, len(inspections))
                for inspected in inspections:
                    self.assertEqual(path, inspected.path)
                    self.assertIs(HeadStatus.HEAD_PRESENT, inspected.detection.status)
                app.detector.set_features(self.calibration.present_features)
                self.assertEqual(2, app.detector.configuration_revision)
                with self.assertRaises(InputImageError) as caught:
                    app.run([Path(directory) / "absent.png"])
                self.assertIs(ErrorReason.IMAGE_UNREADABLE, caught.exception.reason)

    def test_headless_settings_accept_external_calibration_without_calibration_files(self) -> None:
        roi = self.calibration.inspection_region
        calibration = replace(
            self.calibration, inspection_region=replace(roi, x=roi.x + 5, width=roi.width - 5)
        )
        with tempfile.TemporaryDirectory() as directory:
            config_dir = Path(directory)
            for filename in ("matching.json", "preprocessing.json", "alignment.json"):
                shutil.copy2(DEFAULT_CONFIG_DIRECTORY / filename, config_dir / filename)
            image_path = config_dir / "input.png"
            self.assertTrue(cv2.imwrite(str(image_path), self.references.present))
            settings = ExampleSettings(
                config_directory=config_dir,
                image_paths=(image_path,),
                independent_images=True,
                calibration=calibration,
            )
            with redirect_stdout(io.StringIO()) as output, redirect_stderr(io.StringIO()):
                code = main(settings)
        self.assertEqual(0, code)
        self.assertIn("HEAD_PRESENT", output.getvalue())
        self.assertIn("configuration 1", output.getvalue())

    def test_headless_stream_keeps_temporal_confirmation(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "frame.png"
            self.assertTrue(cv2.imwrite(str(path), self.references.present))
            app = HeadlessApplication(self.configuration, calibration=self.calibration)
            results = app.run([path] * self.configuration.alignment.stable_frames)
            self.assertIs(HeadStatus.UNKNOWN, results[0].detection.status)
            self.assertIs(HeadStatus.HEAD_PRESENT, results[-1].detection.status)

    def test_headless_entrypoint_supports_file_and_module_execution(self) -> None:
        project = Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory() as directory:
            modes = (
                ((sys.executable, str(project / "examples/get_status.py")), Path(directory)),
                ((sys.executable, "-m", "examples.get_status"), project),
            )
            for command, working_directory in modes:
                with self.subTest(command=command):
                    completed = subprocess.run(
                        command,
                        cwd=working_directory,
                        capture_output=True,
                        text=True,
                        timeout=30,
                        check=False,
                    )
                    self.assertEqual(0, completed.returncode, completed.stderr)
                    self.assertIn("head_present.png: HEAD_PRESENT", completed.stdout)
                    self.assertIn("head_missing.png: HEAD_MISSING", completed.stdout)

    def test_development_selection_consumes_typed_external_calibration(self) -> None:
        features = tuple(
            replace(f, name=f"selected_{f.name}") for f in self.calibration.present_features
        )
        options = replace(
            parse_options([]),
            configuration=replace(self.configuration, calibration=self.calibration),
            select_present=True,
        )
        selection = FeatureSelectionResult(
            SelectionOutcome.SAVED, Path("present_features.json"), features
        )
        with (
            patch.object(FeatureSelector, "select", return_value=selection),
            patch.object(
                ConfigurationRepository, "load", side_effect=AssertionError("Unexpected reload")
            ),
            patch("cv2.imread", side_effect=AssertionError("Unexpected reference file I/O")),
            redirect_stdout(io.StringIO()),
        ):
            configured = prepare_configuration(options)
        self.assertEqual(features, configured.calibration.present_features)
        self.assertIs(self.calibration.references, configured.calibration.references)


if __name__ == "__main__":
    unittest.main()
