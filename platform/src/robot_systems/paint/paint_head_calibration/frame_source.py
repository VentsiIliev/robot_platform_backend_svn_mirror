"""Latest-only camera subscription owned by the developer screen."""

from collections.abc import Callable
from math import isfinite
from threading import RLock
from time import monotonic
from typing import cast

import numpy as np
from numpy.typing import NDArray

from src.robot_systems.paint.component_ids import CameraRoleID
from src.robot_systems.paint.contracts.paint_head_calibration.errors import (
    CalibrationFailure,
    CalibrationFailureCode,
    CalibrationValidationError,
    PaintHeadCalibrationError,
)
from src.robot_systems.paint.contracts.paint_head_calibration.models import ImageFrame
from src.robot_systems.paint.contracts.paint_head_calibration.validation import finite_number
from src.robot_systems.paint.paint_head_check.adapters.frames import ICameraFrameSubscriptions
from src.shared_contracts.events.vision_events import CameraFrameMetadata, CameraTopics

from .detector_adapter import image_pixels


class PrimaryVisionSetupFrameSource:
    def __init__(
        self,
        subscriptions: ICameraFrameSubscriptions,
        activate: Callable[[], None],
        *,
        max_age_seconds: float,
        clock: Callable[[], float] = monotonic,
    ) -> None:
        finite_number(max_age_seconds, "Preview frame age")
        if max_age_seconds == 0:
            raise CalibrationValidationError("Preview frame age must be positive")
        self._subscriptions = subscriptions
        self._activate = activate
        self._max_age = max_age_seconds
        self._clock = clock
        self._lock = RLock()
        self._active = False
        self._image: NDArray[np.uint8] | None = None
        self._metadata: CameraFrameMetadata | None = None
        self._failure: CalibrationFailure | None = None
        self._topic = CameraTopics.frame(CameraRoleID.PRIMARY_VISION.value)

    def start(self) -> None:
        with self._lock:
            if self._active:
                return
            self._active = True
            self._image = None
            self._metadata = None
            self._failure = None
            # Broker registration is nonblocking. Keep it paired with stop under
            # the same lock so cancellation cannot unsubscribe before subscribe.
            try:
                self._subscriptions.subscribe(self._topic, self._on_frame)
            except Exception as error:
                self._active = False
                raise PaintHeadCalibrationError(
                    CalibrationFailure(
                        CalibrationFailureCode.CAMERA_UNAVAILABLE,
                        f"Cannot subscribe to primary-camera frames: {error}",
                    )
                ) from error
        try:
            self._activate()
        except Exception as error:
            self.stop()
            raise PaintHeadCalibrationError(
                CalibrationFailure(
                    CalibrationFailureCode.CAMERA_UNAVAILABLE,
                    f"Cannot activate primary-camera frames: {error}",
                )
            ) from error

    def stop(self) -> None:
        with self._lock:
            active = self._active
            self._active = False
            self._image = None
            self._metadata = None
            self._failure = None
            if active:
                self._subscriptions.unsubscribe(self._topic, self._on_frame)

    def latest(self) -> ImageFrame:
        with self._lock:
            if not self._active:
                raise PaintHeadCalibrationError(
                    CalibrationFailure(
                        CalibrationFailureCode.CANCELLED, "Camera preview is stopped"
                    )
                )
            if self._failure is not None:
                raise PaintHeadCalibrationError(self._failure)
            image, metadata = self._image, self._metadata
        if image is None or metadata is None:
            raise PaintHeadCalibrationError(
                CalibrationFailure(
                    CalibrationFailureCode.CAMERA_UNAVAILABLE, "Waiting for a primary-camera frame"
                )
            )
        age = self._clock() - metadata.captured_at_monotonic
        if age < 0 or age > self._max_age:
            raise PaintHeadCalibrationError(
                CalibrationFailure(
                    CalibrationFailureCode.FRAME_STALE, "Primary-camera frame is stale"
                )
            )
        return ImageFrame(image_pixels(image), metadata.sequence, metadata.captured_at_monotonic)

    def _on_frame(self, message: object) -> None:
        with self._lock:
            if not self._active:
                return
            if (
                not isinstance(message, dict)
                or message.get("camera") != CameraRoleID.PRIMARY_VISION.value
            ):
                self._reject("Invalid primary-camera message")
                return
            image, metadata = message.get("image"), message.get("metadata")
            if (
                not isinstance(metadata, CameraFrameMetadata)
                or type(metadata.sequence) is not int
                or metadata.sequence < 1
                or type(metadata.captured_at_monotonic) not in (int, float)
                or not _finite_timestamp(metadata.captured_at_monotonic)
                or metadata.captured_at_monotonic < 0
                or metadata.captured_at_monotonic > self._clock()
                or not isinstance(image, np.ndarray)
                or image.dtype != np.uint8
                or image.ndim != 3
                or image.shape[2] != 3
                or image.shape[0] < 2
                or image.shape[1] < 2
            ):
                self._reject("Camera frame or capture metadata is invalid")
                return
            if self._metadata is not None and (
                metadata.sequence <= self._metadata.sequence
                or metadata.captured_at_monotonic <= self._metadata.captured_at_monotonic
            ):
                return
            self._image = cast(NDArray[np.uint8], image).copy()
            self._metadata = metadata
            self._failure = None

    def _reject(self, detail: str) -> None:
        self._image = None
        self._failure = CalibrationFailure(CalibrationFailureCode.FRAME_INVALID, detail)


def _finite_timestamp(value: int | float) -> bool:
    try:
        return isfinite(value)
    except OverflowError:
        return False
