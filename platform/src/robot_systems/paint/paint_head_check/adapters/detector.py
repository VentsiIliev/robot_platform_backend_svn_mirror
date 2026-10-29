"""Translate the existing image detector into paint-owned observations."""

from math import hypot, isfinite
from typing import Protocol

import numpy as np
from numpy.typing import NDArray

from src.robot_systems.paint.contracts.paint_head_check.errors import (
    HeadInspectionFailure,
    HeadInspectionFailureCode,
)
from src.robot_systems.paint.contracts.paint_head_check.guidance import (
    HeadCorrectionDirection,
    HeadRotationCorrection,
    PaintHeadCorrection,
)
from src.robot_systems.paint.contracts.paint_head_check.models import (
    PaintHeadAlignment,
    PaintHeadObservation,
    PaintHeadObservationReason,
    PaintHeadState,
)
from src.robot_systems.paint.contracts.paint_head_check.results import (
    HeadObservationResult,
    ObservationFailed,
    ObservationReceived,
)
from src.robot_systems.paint.paint_head_detection import (
    DetectionProcessingError,
    DetectionReason,
    DetectionResult,
    HeadStatus,
    InvalidImageError,
)

from .frames import IHeadFrameEvaluator


class IImageHeadDetector(Protocol):
    """Backend seam local to this adapter; policies never import this protocol."""

    def reset(self) -> None: ...

    def get_status(self, image: NDArray[np.uint8]) -> DetectionResult: ...


_STATES = {
    HeadStatus.HEAD_PRESENT: PaintHeadState.PRESENT,
    HeadStatus.HEAD_MISSING: PaintHeadState.MISSING,
    HeadStatus.HEAD_MISALIGNED: PaintHeadState.MISALIGNED,
    HeadStatus.UNKNOWN: PaintHeadState.UNKNOWN,
}

_REASONS = {
    DetectionReason.ALIGNED: PaintHeadObservationReason.ALIGNED,
    DetectionReason.MISALIGNED: PaintHeadObservationReason.MISALIGNED,
    DetectionReason.EMPTY_MOUNT: PaintHeadObservationReason.EMPTY_MOUNT,
    DetectionReason.INSUFFICIENT_EVIDENCE: PaintHeadObservationReason.INSUFFICIENT_EVIDENCE,
    DetectionReason.CONFLICTING_EVIDENCE: PaintHeadObservationReason.CONFLICTING_EVIDENCE,
    DetectionReason.POSE_UNDETERMINED: PaintHeadObservationReason.POSE_UNDETERMINED,
    DetectionReason.TOO_DARK: PaintHeadObservationReason.TOO_DARK,
    DetectionReason.OVEREXPOSED: PaintHeadObservationReason.OVEREXPOSED,
    DetectionReason.LOW_CONTRAST: PaintHeadObservationReason.LOW_CONTRAST,
    DetectionReason.CONFIRMING_STATUS: PaintHeadObservationReason.CONFIRMING_STATUS,
    DetectionReason.RECHECKING_POSITION: PaintHeadObservationReason.RECHECKING_POSITION,
}


class PaintHeadDetectorAdapter(IHeadFrameEvaluator):
    def __init__(self, detector: IImageHeadDetector) -> None:
        self._detector = detector

    def reset(self) -> None:
        self._detector.reset()

    def evaluate(
        self,
        image: NDArray[np.uint8],
        *,
        frame_sequence: int,
        frame_captured_at: float,
        frame_received_at: float,
    ) -> HeadObservationResult:
        try:
            result = self._detector.get_status(image)
        except InvalidImageError as error:
            return ObservationFailed(
                HeadInspectionFailure(
                    HeadInspectionFailureCode.IMAGE_INVALID,
                    error.message,
                )
            )
        except DetectionProcessingError as error:
            return ObservationFailed(
                HeadInspectionFailure(
                    HeadInspectionFailureCode.PROCESSING_FAILED,
                    error.message,
                )
            )

        alignment = None
        if result.alignment is not None:
            measured = result.alignment
            alignment = PaintHeadAlignment(
                aligned=measured.aligned,
                translation_pixels=measured.translation_pixels,
                rotation_degrees=measured.rotation_degrees,
                max_translation_pixels=measured.max_translation_pixels,
                max_rotation_degrees=measured.max_rotation_degrees,
                recovery_pixel_limit=measured.recovery_pixel_limit,
                recovery_degree_limit=measured.recovery_degree_limit,
                recovering=measured.recovering,
            )
        return ObservationReceived(
            PaintHeadObservation(
                state=_STATES[result.status],
                observed_state=_STATES[result.observed_status],
                reason=_REASONS[result.reason],
                frame_sequence=frame_sequence,
                frame_captured_at=frame_captured_at,
                frame_received_at=frame_received_at,
                evaluated_at=result.timestamp,
                calibration_revision=result.configuration_revision,
                alignment=alignment,
                held_warning=result.held_warning,
                correction=_correction(result, image),
            )
        )


def _correction(result: DetectionResult, image: NDArray[np.uint8]) -> PaintHeadCorrection | None:
    measurement = result.alignment
    if measurement is None:
        return None
    pose = result.diagnostics.pose
    if not all(
        isfinite(value)
        for value in (
            pose.offset.x,
            pose.offset.y,
            measurement.translation_pixels,
            measurement.rotation_degrees,
        )
    ):
        return None
    pixel_limit = (
        measurement.recovery_pixel_limit
        if measurement.recovering
        else measurement.max_translation_pixels
    )
    degree_limit = (
        measurement.recovery_degree_limit
        if measurement.recovering
        else measurement.max_rotation_degrees
    )
    direction = None
    if measurement.translation_pixels > pixel_limit + 1e-6:
        x, y = -pose.offset.x / image.shape[1], -pose.offset.y / image.shape[0]
        length = hypot(x, y)
        if length <= 1e-12:
            return None
        direction = HeadCorrectionDirection(x / length, y / length)
    rotation = HeadRotationCorrection.NONE
    if abs(measurement.rotation_degrees) > degree_limit + 1e-6:
        rotation = (
            HeadRotationCorrection.CLOCKWISE
            if measurement.rotation_degrees > 0
            else HeadRotationCorrection.COUNTERCLOCKWISE
        )
    return PaintHeadCorrection(
        image_width=int(image.shape[1]),
        image_height=int(image.shape[0]),
        translation_direction=direction,
        rotation_direction=rotation,
        # Dimensionless visual extents: zero at tolerance, bounded above it.
        # Neither actual distances/angles nor the calibrated feature geometry leave this adapter.
        translation_extent=(
            _visual_extent(measurement.translation_pixels, pixel_limit)
            if direction is not None
            else 0.0
        ),
        rotation_extent=(
            _visual_extent(abs(measurement.rotation_degrees), degree_limit)
            if rotation is not HeadRotationCorrection.NONE
            else 0.0
        ),
    )


def _visual_extent(error: float, limit: float) -> float:
    excess = max(0.0, error - limit)
    return excess / (excess + max(limit, 1e-6))
