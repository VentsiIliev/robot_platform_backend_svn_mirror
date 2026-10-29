"""On-demand inspection of frames published by the existing primary camera owner."""

from collections.abc import Callable
from dataclasses import dataclass
from math import isfinite
from threading import Condition
from time import monotonic
from typing import cast

import numpy as np
from numpy.typing import NDArray

from src.robot_systems.paint.component_ids import CameraRoleID
from src.robot_systems.paint.contracts.paint_head_check.errors import (
    HeadInspectionFailure,
    HeadInspectionFailureCode,
    PaintHeadContractError,
)
from src.robot_systems.paint.contracts.paint_head_check.interfaces import (
    IHeadInspectionControl,
    IPaintHeadInspector,
)
from src.robot_systems.paint.contracts.paint_head_check.models import HeadInspectionWindow
from src.robot_systems.paint.contracts.paint_head_check.results import (
    HeadObservationResult,
    ObservationCancelled,
    ObservationFailed,
    ObservationPaused,
)
from src.shared_contracts.events.vision_events import CameraFrameMetadata, CameraTopics

from .frames import ICameraFrameSubscriptions, IHeadFrameEvaluator


@dataclass(frozen=True, slots=True)
class _ReceivedFrame:
    image: NDArray[np.uint8]
    sequence: int
    captured_at: float
    received_at: float


class PrimaryVisionPaintHeadInspector(IPaintHeadInspector):
    """Subscribe only during checks; process images on the requesting worker.

    Capture metadata prevents a delayed pre-arrival frame from satisfying a
    check. Repeated or out-of-order capture sequences cannot confirm a head.
    """

    def __init__(
        self,
        subscriptions: ICameraFrameSubscriptions,
        evaluator_factory: Callable[[], IHeadFrameEvaluator],
        *,
        clock: Callable[[], float] = monotonic,
        activate_frames: Callable[[], None] | None = None,
    ) -> None:
        self._subscriptions = subscriptions
        self._evaluator_factory = evaluator_factory
        self._clock = clock
        self._activate_frames = activate_frames
        self._topic = CameraTopics.frame(CameraRoleID.PRIMARY_VISION.value)
        self._condition = Condition()
        self._active = False
        self._evaluator: IHeadFrameEvaluator | None = None
        self._pending: _ReceivedFrame | HeadInspectionFailure | None = None
        self._sequence = 0

    def begin_inspection(self) -> None:
        with self._condition:
            if self._active:
                raise PaintHeadContractError("A paint-head inspection is already active")
            self._active = True
            self._pending = None
            self._sequence = 0
        try:
            if self._evaluator is None:
                self._evaluator = self._evaluator_factory()
            self._evaluator.reset()
            if self._activate_frames is not None:
                self._activate_frames()
            self._subscriptions.subscribe(self._topic, self._on_frame)
        except Exception:
            # Lifecycle cleanup preserves the original expected or unexpected error.
            with self._condition:
                self._active = False
                self._pending = None
                self._condition.notify_all()
            raise

    def end_inspection(self) -> None:
        with self._condition:
            was_active = self._active
            self._active = False
            self._pending = None
            self._condition.notify_all()
        if was_active:
            self._subscriptions.unsubscribe(self._topic, self._on_frame)

    def next_observation(
        self,
        window: HeadInspectionWindow,
        control: IHeadInspectionControl,
    ) -> HeadObservationResult:
        with self._condition:
            if not self._active:
                raise PaintHeadContractError("Begin inspection before requesting an observation")
            while True:
                if control.should_stop() or not self._active:
                    return ObservationCancelled()
                if control.pause_requested():
                    return ObservationPaused()
                remaining = window.deadline_at - self._clock()
                if remaining <= 0:
                    return _timeout()
                pending = self._pending
                self._pending = None
                if pending is not None:
                    break
                self._condition.wait(timeout=min(remaining, 0.05))

        if isinstance(pending, HeadInspectionFailure):
            return ObservationFailed(pending)
        if (
            pending.captured_at < window.started_at
            or pending.captured_at > self._clock()
            or self._clock() - pending.captured_at > window.max_frame_age_seconds
        ):
            return ObservationFailed(
                HeadInspectionFailure(
                    HeadInspectionFailureCode.FRAME_STALE,
                    "Primary-vision frame predates this inspection or exceeded its maximum age",
                )
            )
        evaluator = self._evaluator
        if evaluator is None:
            raise PaintHeadContractError("Active inspection has no frame evaluator")
        result = evaluator.evaluate(
            pending.image,
            frame_sequence=pending.sequence,
            frame_captured_at=pending.captured_at,
            frame_received_at=pending.received_at,
        )
        with self._condition:
            still_active = self._active
        if control.should_stop() or not still_active:
            return ObservationCancelled()
        if control.pause_requested():
            return ObservationPaused()
        if self._clock() >= window.deadline_at:
            return _timeout()
        if self._clock() - pending.captured_at > window.max_frame_age_seconds:
            return ObservationFailed(
                HeadInspectionFailure(
                    HeadInspectionFailureCode.FRAME_STALE,
                    "Primary-vision frame exceeded its maximum age during head detection",
                )
            )
        return result

    def _on_frame(self, message: object) -> None:
        with self._condition:
            if not self._active:
                return
            received_at = self._clock()
            if (
                not isinstance(message, dict)
                or message.get("camera") != CameraRoleID.PRIMARY_VISION.value
            ):
                self._pending = HeadInspectionFailure(
                    HeadInspectionFailureCode.CAMERA_READ_FAILED,
                    "Primary-vision inspection received an invalid camera message",
                )
            else:
                image = message.get("image")
                metadata = message.get("metadata")
                if (
                    not isinstance(metadata, CameraFrameMetadata)
                    or type(metadata.sequence) is not int
                    or metadata.sequence < 1
                    or not isfinite(metadata.captured_at_monotonic)
                ):
                    self._pending = HeadInspectionFailure(
                        HeadInspectionFailureCode.CAMERA_READ_FAILED,
                        "Primary-vision inspection requires valid capture sequence "
                        "and timing metadata",
                    )
                elif not isinstance(image, np.ndarray) or image.dtype != np.uint8:
                    self._pending = HeadInspectionFailure(
                        HeadInspectionFailureCode.IMAGE_INVALID,
                        "Primary-vision inspection requires a uint8 image",
                    )
                elif metadata.sequence > self._sequence:
                    self._sequence = metadata.sequence
                    self._pending = _ReceivedFrame(
                        cast(NDArray[np.uint8], image).copy(),
                        metadata.sequence,
                        metadata.captured_at_monotonic,
                        received_at,
                    )
            self._condition.notify_all()


def _timeout() -> ObservationFailed:
    return ObservationFailed(
        HeadInspectionFailure(
            HeadInspectionFailureCode.TIMEOUT,
            "Paint-head inspection timed out waiting for a fresh primary-vision observation",
        )
    )
