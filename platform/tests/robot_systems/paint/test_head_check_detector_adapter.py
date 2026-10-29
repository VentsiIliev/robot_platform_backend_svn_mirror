"""The detector backend must not leak its types or exceptions into policies."""

import unittest
from dataclasses import replace

import cv2
import numpy as np
from numpy.typing import NDArray

from src.robot_systems.paint.contracts.paint_head_check.errors import HeadInspectionFailureCode
from src.robot_systems.paint.contracts.paint_head_check.guidance import HeadRotationCorrection
from src.robot_systems.paint.contracts.paint_head_check.models import (
    PaintHeadObservationReason,
    PaintHeadState,
)
from src.robot_systems.paint.contracts.paint_head_check.results import (
    ObservationFailed,
    ObservationReceived,
)
from src.robot_systems.paint.paint_head_check.adapters.detector import PaintHeadDetectorAdapter
from src.robot_systems.paint.paint_head_detection import (
    AlignmentMeasurement,
    DetectionProcessingError,
    DetectionReason,
    DetectionResult,
    ErrorReason,
    HeadStatus,
    InvalidImageError,
    PaintHeadDetector,
    Point2D,
    PoseEstimate,
)


class FakeDetector:
    def __init__(self, result: DetectionResult, error: Exception | None = None) -> None:
        self.result = result
        self.error = error
        self.reset_count = 0

    def reset(self) -> None:
        self.reset_count += 1

    def get_status(self, image: NDArray[np.uint8]) -> DetectionResult:
        if self.error is not None:
            raise self.error
        return self.result


class DetectorAdapterTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        detector = PaintHeadDetector()
        cls.image = detector.reference_images.present
        cls.backend_result = detector.get_status(cls.image)

    def test_all_backend_states_and_reasons_are_mapped_explicitly(self) -> None:
        states = (
            (HeadStatus.HEAD_PRESENT, PaintHeadState.PRESENT),
            (HeadStatus.HEAD_MISSING, PaintHeadState.MISSING),
            (HeadStatus.HEAD_MISALIGNED, PaintHeadState.MISALIGNED),
            (HeadStatus.UNKNOWN, PaintHeadState.UNKNOWN),
        )
        for backend_state, domain_state in states:
            for reason in DetectionReason:
                with self.subTest(state=backend_state, reason=reason):
                    backend = FakeDetector(
                        replace(
                            self.backend_result,
                            status=backend_state,
                            observed_status=HeadStatus.UNKNOWN,
                            reason=reason,
                        )
                    )
                    result = PaintHeadDetectorAdapter(backend).evaluate(
                        self.image,
                        frame_sequence=12,
                        frame_captured_at=19.9,
                        frame_received_at=20.0,
                    )
                    self.assertIsInstance(result, ObservationReceived)
                    if not isinstance(result, ObservationReceived):
                        self.fail("Expected an observation")
                    self.assertIs(domain_state, result.observation.state)
                    self.assertIs(PaintHeadState.UNKNOWN, result.observation.observed_state)
                    self.assertIsInstance(result.observation.reason, PaintHeadObservationReason)
                    self.assertEqual(reason.name, result.observation.reason.name)
                    self.assertEqual(12, result.observation.frame_sequence)
                    self.assertEqual(20.0, result.observation.frame_received_at)
                    self.assertEqual(
                        self.backend_result.configuration_revision,
                        result.observation.calibration_revision,
                    )

    def test_placement_and_held_warning_survive_the_boundary(self) -> None:
        measurement = AlignmentMeasurement(False, 12.0, -3.0, 10.0, 2.0, 8.0, 1.0, True)
        backend = FakeDetector(
            replace(
                self.backend_result,
                status=HeadStatus.HEAD_MISALIGNED,
                reason=DetectionReason.RECHECKING_POSITION,
                alignment=measurement,
                held_warning=True,
            )
        )
        result = PaintHeadDetectorAdapter(backend).evaluate(
            self.image,
            frame_sequence=1,
            frame_captured_at=19.9,
            frame_received_at=20.0,
        )
        self.assertIsInstance(result, ObservationReceived)
        if not isinstance(result, ObservationReceived) or result.observation.alignment is None:
            self.fail("Expected placement measurements")
        self.assertEqual(12.0, result.observation.alignment.translation_pixels)
        self.assertEqual(-3.0, result.observation.alignment.rotation_degrees)
        self.assertTrue(result.observation.alignment.recovering)
        self.assertTrue(result.observation.held_warning)
        self.assertIsNot(measurement, result.observation.alignment)

    def test_known_backend_exceptions_become_typed_failures(self) -> None:
        cases = (
            (
                InvalidImageError(ErrorReason.IMAGE_SIZE_MISMATCH, "Unexpected resolution"),
                HeadInspectionFailureCode.IMAGE_INVALID,
            ),
            (
                DetectionProcessingError(ErrorReason.PROCESSING_FAILED, "Vision backend failed"),
                HeadInspectionFailureCode.PROCESSING_FAILED,
            ),
        )
        for error, code in cases:
            with self.subTest(code=code):
                adapter = PaintHeadDetectorAdapter(FakeDetector(self.backend_result, error))
                result = adapter.evaluate(
                    self.image,
                    frame_sequence=1,
                    frame_captured_at=19.9,
                    frame_received_at=20.0,
                )
                self.assertIsInstance(result, ObservationFailed)
                if not isinstance(result, ObservationFailed):
                    self.fail("Expected typed inspection failure")
                self.assertIs(code, result.failure.code)
                self.assertEqual(str(error), result.failure.message)

    def test_unexpected_bugs_propagate_instead_of_becoming_unknown(self) -> None:
        adapter = PaintHeadDetectorAdapter(
            FakeDetector(
                self.backend_result,
                RuntimeError("unexpected implementation bug"),
            )
        )
        with self.assertRaisesRegex(RuntimeError, "implementation bug"):
            adapter.evaluate(
                self.image,
                frame_sequence=1,
                frame_captured_at=19.9,
                frame_received_at=20.0,
            )

    def test_reset_is_explicit_at_each_inspection_boundary(self) -> None:
        backend = FakeDetector(self.backend_result)
        adapter = PaintHeadDetectorAdapter(backend)
        adapter.reset()
        adapter.reset()
        self.assertEqual(2, backend.reset_count)

    def test_real_detector_can_confirm_presence_through_the_domain_adapter(self) -> None:
        detector = PaintHeadDetector()
        adapter = PaintHeadDetectorAdapter(detector)
        adapter.reset()
        states = []
        for sequence in range(1, 4):
            result = adapter.evaluate(
                detector.reference_images.present,
                frame_sequence=sequence,
                frame_captured_at=19.9 + sequence,
                frame_received_at=20.0 + sequence,
            )
            self.assertIsInstance(result, ObservationReceived)
            if isinstance(result, ObservationReceived):
                states.append(result.observation.state)
        self.assertEqual(
            [PaintHeadState.UNKNOWN, PaintHeadState.UNKNOWN, PaintHeadState.PRESENT],
            states,
        )

    def test_corrections_point_back_to_reference_for_real_translation_and_both_rotations(
        self,
    ) -> None:
        for angle, dx, dy in ((4.0, 15, -10), (-4.0, -15, 10)):
            with self.subTest(angle=angle):
                pivot = (686.0, 393.5)
                transform = cv2.getRotationMatrix2D(pivot, angle, 1.0)
                transform[:, 2] += (dx, dy)
                moved = cv2.warpAffine(
                    self.image, transform, (self.image.shape[1], self.image.shape[0])
                )
                adapter = PaintHeadDetectorAdapter(PaintHeadDetector())
                for sequence in range(3):
                    result = adapter.evaluate(
                        moved,
                        frame_sequence=sequence,
                        frame_captured_at=1.0,
                        frame_received_at=2.0,
                    )
                self.assertIsInstance(result, ObservationReceived)
                guide = result.observation.correction
                self.assertIsNotNone(guide)
                self.assertIs(result.observation.state, PaintHeadState.MISALIGNED)
                self.assertEqual((1280, 720), (guide.image_width, guide.image_height))
                direction = guide.translation_direction
                self.assertLess(direction.x * dx, 0)
                self.assertLess(direction.y * dy, 0)
                self.assertAlmostEqual(
                    dx / dy,
                    direction.x * guide.image_width / (direction.y * guide.image_height),
                    delta=0.15,
                )
                self.assertIs(
                    HeadRotationCorrection.CLOCKWISE
                    if angle > 0
                    else HeadRotationCorrection.COUNTERCLOCKWISE,
                    guide.rotation_direction,
                )

    def test_held_misalignment_without_current_pose_has_no_direction_guide(self) -> None:
        backend = FakeDetector(
            replace(
                self.backend_result,
                status=HeadStatus.HEAD_MISALIGNED,
                observed_status=HeadStatus.UNKNOWN,
                alignment=None,
                held_warning=True,
            )
        )
        result = PaintHeadDetectorAdapter(backend).evaluate(
            self.image,
            frame_sequence=1,
            frame_captured_at=1.0,
            frame_received_at=2.0,
        )
        self.assertIsNone(result.observation.correction)

    def test_recovery_limits_control_correction_cues(self) -> None:
        for recovering, translation, rotation in ((False, False, False), (True, True, True)):
            backend = FakeDetector(
                replace(
                    self.backend_result,
                    alignment=AlignmentMeasurement(
                        False, 9.0, -1.5, 10.0, 2.0, 8.0, 1.0, recovering
                    ),
                    diagnostics=replace(
                        self.backend_result.diagnostics, pose=PoseEstimate(-1.5, Point2D(9, 0))
                    ),
                )
            )
            result = PaintHeadDetectorAdapter(backend).evaluate(
                self.image,
                frame_sequence=1,
                frame_captured_at=1.0,
                frame_received_at=2.0,
            )
            guide = result.observation.correction
            self.assertEqual(translation, guide.translation_direction is not None)
            self.assertEqual(rotation, guide.rotation_direction is not HeadRotationCorrection.NONE)

    def test_correction_does_not_export_landmarks_or_error_magnitudes(self) -> None:
        corrections = []
        for multiplier in (1, 2):
            backend = FakeDetector(
                replace(
                    self.backend_result,
                    alignment=AlignmentMeasurement(
                        False,
                        20.0 * multiplier,
                        4.0 * multiplier,
                        10.0,
                        2.0,
                        8.0,
                        1.0,
                        False,
                    ),
                    diagnostics=replace(
                        self.backend_result.diagnostics,
                        # Guidance consumes the measured pose, with no dependency on matching features.
                        present=replace(self.backend_result.diagnostics.present, matches=()),
                        pose=PoseEstimate(
                            4.0 * multiplier, Point2D(12.0 * multiplier, -16.0 * multiplier)
                        ),
                    ),
                )
            )
            result = PaintHeadDetectorAdapter(backend).evaluate(
                self.image,
                frame_sequence=1,
                frame_captured_at=1.0,
                frame_received_at=2.0,
            )
            corrections.append(result.observation.correction)
        self.assertIsNotNone(corrections[0])
        self.assertEqual(corrections[0].translation_direction, corrections[1].translation_direction)
        self.assertEqual(corrections[0].rotation_direction, corrections[1].rotation_direction)
        self.assertLessEqual(corrections[0].translation_extent, corrections[1].translation_extent)
        self.assertTrue(0 <= corrections[1].rotation_extent <= 1)

    def test_operator_adjustment_reduces_the_visual_offset_without_resetting_confirmation(
        self,
    ) -> None:
        adapter = PaintHeadDetectorAdapter(PaintHeadDetector())
        extents = []
        sequence = 0
        for dx in (30, 20, 12, 0):
            shifted = cv2.warpAffine(
                self.image,
                np.float32([[1, 0, dx], [0, 1, 0]]),
                (self.image.shape[1], self.image.shape[0]),
            )
            for _ in range(3):
                sequence += 1
                result = adapter.evaluate(
                    shifted,
                    frame_sequence=sequence,
                    frame_captured_at=sequence,
                    frame_received_at=sequence,
                )
            self.assertIsNotNone(result.observation.correction)
            extents.append(result.observation.correction.translation_extent)
        self.assertTrue(all(left > right for left, right in zip(extents, extents[1:])), extents)
        self.assertEqual(0, extents[-1])
        self.assertIs(PaintHeadState.PRESENT, result.observation.state)


if __name__ == "__main__":
    unittest.main()
