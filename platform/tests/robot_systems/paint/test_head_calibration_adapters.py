"""Image and camera boundary checks using bundled fixtures and fake pub/sub only."""

from dataclasses import replace
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase
from unittest.mock import patch

import numpy as np

from src.robot_systems.paint.component_ids import CameraRoleID, MovementGroupID
from src.robot_systems.paint.contracts.paint_head_calibration.errors import (
    CalibrationFailureCode, PaintHeadCalibrationError,
)
from src.robot_systems.paint.contracts.paint_head_calibration.models import (
    ImageFrame, ImagePixels, ImageSize, InspectionBinding, References,
)
from src.robot_systems.paint.contracts.paint_head_check.models import PaintHeadState
from src.robot_systems.paint.paint_head_calibration.assets import FileReferenceAssetRepository
from src.robot_systems.paint.paint_head_calibration.detector_adapter import (
    CalibrationDetectorAdapter, CalibrationEditorEvaluator, encode_reference,
)
from src.robot_systems.paint.paint_head_calibration.frame_source import PrimaryVisionSetupFrameSource
from src.shared_contracts.events.vision_events import CameraFrameMetadata


class CalibrationDetectorAdapterTests(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temporary = TemporaryDirectory()
        cls.assets = FileReferenceAssetRepository(Path(cls.temporary.name) / "references")
        cls.adapter = CalibrationDetectorAdapter(cls.assets)
        cls.binding = InspectionBinding(
            CameraRoleID.PRIMARY_VISION, MovementGroupID.VERTICAL_SHAFT_ALIGNMENT
        )
        definition, cls.present, cls.missing = cls.adapter.bundled_template(cls.binding)
        present_asset = cls.assets.put_png(encode_reference(cls.present), cls.present.size)
        missing_asset = cls.assets.put_png(encode_reference(cls.missing), cls.missing.size)
        cls.definition = replace(definition, references=References(present_asset, missing_asset))

    @classmethod
    def tearDownClass(cls):
        cls.temporary.cleanup()

    def test_existing_detector_can_be_prepared_from_system_owned_assets(self):
        detector = self.adapter.create_detector(self.definition)
        self.assertEqual(detector.reference_size.width, self.present.size.width)
        self.assertEqual(detector.reference_size.height, self.present.size.height)
        for asset in self.definition.references.assets():
            self.assertTrue((Path(self.temporary.name) / "references" / (asset.asset_id.value + ".png")).is_file())

    def test_profile_conversion_preserves_every_detector_tuning_and_feature_property(self):
        detector = self.adapter.create_detector(self.definition)
        configuration = detector.configuration
        self.assertEqual(configuration.alignment.stable_frames, self.definition.tuning.alignment.stable_frames)
        expected = {item.name: item for item in self.definition.landmarks}
        for feature in (*configuration.calibration.present_features, *configuration.calibration.missing_features):
            source = expected[feature.name]
            self.assertEqual(feature.threshold, source.threshold)
            self.assertEqual(feature.required, source.required)
            self.assertEqual(feature.orientation_invariant, source.orientation_invariant)
            self.assertEqual(feature.max_template_rotation, source.max_template_rotation)
            self.assertEqual(feature.support.value, source.support.value)

    def test_new_profile_has_no_implicit_reference_images_or_inspection_region(self):
        definition = self.adapter.empty_template(self.binding)
        self.assertIsNone(definition.references.present)
        self.assertIsNone(definition.references.missing)
        self.assertIsNone(definition.inspection_region)
        with self.assertRaises(PaintHeadCalibrationError) as raised:
            self.adapter.validate(definition)
        self.assertEqual(raised.exception.failure.code, CalibrationFailureCode.INVALID_CALIBRATION)

    def test_incompatible_reference_sizes_are_a_typed_validation_failure(self):
        small = ImagePixels(ImageSize(8, 8), bytes(8 * 8 * 3))
        asset = self.assets.put_png(encode_reference(small), small.size)
        definition = replace(self.definition, references=replace(self.definition.references, missing=asset))
        with self.assertRaises(PaintHeadCalibrationError) as raised:
            self.adapter.create_detector(definition)
        self.assertEqual(raised.exception.failure.code, CalibrationFailureCode.INVALID_CALIBRATION)
        self.assertIn("same dimensions", raised.exception.failure.detail)

    def test_development_stream_rejects_duplicate_frames_but_new_session_resets_confirmation(self):
        evaluator = CalibrationEditorEvaluator(self.adapter)
        frame = ImageFrame(self.present, 1, 10)
        first = evaluator.evaluate(self.definition, frame, 1)
        self.assertIsInstance(first.state, PaintHeadState)
        self.assertEqual(first.frame_sequence, 1)
        self.assertGreater(len(first.evidence), 0)
        with self.assertRaises(PaintHeadCalibrationError) as raised:
            evaluator.evaluate(self.definition, frame, 1)
        self.assertEqual(raised.exception.failure.code, CalibrationFailureCode.FRAME_STALE)
        restarted = evaluator.evaluate(self.definition, frame, 2)
        self.assertEqual(restarted.generation, 2)
        self.assertEqual(restarted.state, first.state)

    def test_reference_preview_returns_owned_immutable_bytes(self):
        preview = self.adapter.reference_preview(self.definition.references.present)
        self.assertIsInstance(preview.bgr, bytes)
        self.assertEqual(preview.size, self.present.size)
        self.assertEqual(preview.bgr, self.present.bgr)


class _Subscriptions:
    def __init__(self):
        self.callbacks = []
        self.subscribe_count = 0
        self.unsubscribe_count = 0

    def subscribe(self, topic, callback):
        self.callbacks.append((topic, callback))
        self.subscribe_count += 1

    def unsubscribe(self, topic, callback):
        self.callbacks.remove((topic, callback))
        self.unsubscribe_count += 1

    def publish(self, message):
        for _, callback in tuple(self.callbacks):
            callback(message)


class PrimaryVisionSetupFrameSourceTests(TestCase):
    def setUp(self):
        self.subscriptions = _Subscriptions()
        self.now = 10.0
        self.activations = 0
        self.source = PrimaryVisionSetupFrameSource(
            self.subscriptions, self.activate, max_age_seconds=1.0, clock=self.clock,
        )
        self.addCleanup(self.source.stop)

    def clock(self):
        return self.now

    def activate(self):
        self.activations += 1

    def frame(self, sequence=1, captured=10.0, value=0):
        return {
            "camera": CameraRoleID.PRIMARY_VISION.value,
            "image": np.full((8, 8, 3), value, dtype=np.uint8),
            "metadata": CameraFrameMetadata(sequence, captured),
        }

    def test_start_stop_are_idempotent_and_do_not_open_a_camera(self):
        self.source.start()
        self.source.start()
        self.assertEqual(self.activations, 1)
        self.assertEqual(len(self.subscriptions.callbacks), 1)
        self.source.stop()
        self.source.stop()
        self.assertEqual(len(self.subscriptions.callbacks), 0)
        self.source.start()
        self.assertEqual(len(self.subscriptions.callbacks), 1)

    def test_activation_failure_releases_subscription_and_returns_typed_camera_failure(self):
        def fail():
            raise RuntimeError('Primary camera disconnected')
        source = PrimaryVisionSetupFrameSource(self.subscriptions, fail, max_age_seconds=1)
        with self.assertRaises(PaintHeadCalibrationError) as raised:
            source.start()
        self.assertEqual(raised.exception.failure.code, CalibrationFailureCode.CAMERA_UNAVAILABLE)
        self.assertEqual(self.subscriptions.callbacks, [])

    def test_subscription_failure_returns_typed_camera_failure_and_allows_retry(self):
        with patch.object(self.subscriptions, 'subscribe', side_effect=RuntimeError('Broker unavailable')):
            with self.assertRaises(PaintHeadCalibrationError) as raised:
                self.source.start()
        self.assertEqual(raised.exception.failure.code, CalibrationFailureCode.CAMERA_UNAVAILABLE)
        self.source.start()
        self.assertEqual(len(self.subscriptions.callbacks), 1)

    def test_broker_capture_snapshot_is_not_aliased_to_the_publisher_array(self):
        self.source.start()
        message = self.frame()
        self.subscriptions.publish(message)
        message["image"].fill(255)
        self.assertEqual(self.source.latest().image.bgr, bytes(8 * 8 * 3))

    def test_duplicate_and_out_of_order_captures_cannot_advance_identity(self):
        self.source.start()
        self.subscriptions.publish(self.frame(2))
        self.subscriptions.publish(self.frame(2, 10.0, 255))
        self.now = 10.1
        self.subscriptions.publish(self.frame(1, 10.1, 255))
        frame = self.source.latest()
        self.assertEqual(frame.sequence, 2)
        self.assertEqual(frame.image.bgr, bytes(8 * 8 * 3))

    def test_capture_time_is_not_replaced_with_message_receipt_time(self):
        self.source.start()
        self.subscriptions.publish(self.frame(1, 7.0))
        with self.assertRaises(PaintHeadCalibrationError) as raised:
            self.source.latest()
        self.assertEqual(raised.exception.failure.code, CalibrationFailureCode.FRAME_STALE)

    def test_stale_and_future_frames_are_not_reported_as_current(self):
        self.source.start()
        self.subscriptions.publish(self.frame(1, 11.0))
        with self.assertRaises(PaintHeadCalibrationError):
            self.source.latest()
        self.now = 11.0
        self.subscriptions.publish(self.frame(2, 11.0))
        self.assertEqual(self.source.latest().sequence, 2)
        self.now = 12.1
        with self.assertRaises(PaintHeadCalibrationError):
            self.source.latest()

    def test_invalid_frame_clears_previous_pixels_and_recovers_on_a_new_capture(self):
        self.source.start()
        self.subscriptions.publish(self.frame())
        self.subscriptions.publish({"camera": CameraRoleID.PRIMARY_VISION.value})
        with self.assertRaises(PaintHeadCalibrationError) as raised:
            self.source.latest()
        self.assertEqual(raised.exception.failure.code, CalibrationFailureCode.FRAME_INVALID)
        self.now = 10.1
        self.subscriptions.publish(self.frame(2, 10.1))
        self.assertEqual(self.source.latest().sequence, 2)

    def test_stopped_source_cannot_deliver_a_cached_result(self):
        self.source.start()
        self.subscriptions.publish(self.frame())
        self.source.stop()
        with self.assertRaises(PaintHeadCalibrationError) as raised:
            self.source.latest()
        self.assertEqual(raised.exception.failure.code, CalibrationFailureCode.CANCELLED)
