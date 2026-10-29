"""Reversible camera exposure experiments for development only."""

import cv2
import numpy as np

from ..errors import CameraError, ErrorReason
from ..models import BoolMask
from .camera_session import CameraSession
from .capture_results import CameraRestoreResult, ExposureMeasurement
from .settings import CameraSettings, RuntimeSettings


class ExposureController:
    def __init__(
        self, camera: CameraSession, settings: CameraSettings, runtime: RuntimeSettings
    ) -> None:
        self._camera = camera
        self._settings = settings
        self._runtime = runtime
        self.original_auto_exposure = camera.automatic_exposure
        self.original_exposure = camera.exposure
        self._changed = False
        self._measurements: list[ExposureMeasurement] = []

    @property
    def measurements(self) -> tuple[ExposureMeasurement, ...]:
        return tuple(self._measurements)

    def apply(self, exposure: float) -> float:
        self._changed = True
        if self._camera.automatic_exposure not in self._settings.manual_exposure_modes:
            if (
                self._camera.set_automatic_exposure(False)
                not in self._settings.manual_exposure_modes
            ):
                raise CameraError(
                    ErrorReason.CAMERA_CONTROL_FAILED, "Camera could not enter manual exposure mode"
                )
        requested = round(exposure)
        actual = self._camera.set_exposure(requested)
        tolerance = max(
            self._settings.exposure_absolute_tolerance,
            self._settings.exposure_relative_tolerance * requested,
        )
        if abs(actual - requested) > tolerance:
            raise CameraError(
                ErrorReason.CAMERA_CONTROL_FAILED,
                f"Exposure request {requested} was not applied: {actual}",
            )
        return actual

    def calibrate(self, target_brightness: float, mask: BoolMask) -> float:
        exposure = self._camera.exposure
        if exposure <= 0:
            raise CameraError(
                ErrorReason.CAMERA_CONTROL_FAILED,
                "The exposure sweep requires positive V4L2 exposure values",
            )
        runtime = self._runtime
        for _ in range(runtime.exposure_calibration_attempts):
            actual = self.apply(exposure)
            image = self._camera.settled_frame(runtime.warmup_frames)
            brightness = float(np.median(cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)[mask]))
            measurement = ExposureMeasurement(actual, brightness)
            self._measurements.append(measurement)
            print(f"Exposure calibration: {measurement}", flush=True)
            if abs(brightness - target_brightness) <= max(
                runtime.exposure_brightness_floor,
                runtime.exposure_brightness_tolerance * target_brightness,
            ):
                return actual
            exposure = actual * float(
                np.clip(
                    target_brightness / max(brightness, 1),
                    runtime.exposure_ratio_min,
                    runtime.exposure_ratio_max,
                )
            )
        raise CameraError(
            ErrorReason.CAMERA_CONTROL_FAILED, "Could not match automatic brightness in manual mode"
        )

    def restore(self) -> CameraRestoreResult:
        if not self._changed:
            return CameraRestoreResult(True, "Exposure controls were unchanged")
        errors: list[str] = []
        try:
            self._camera.set_exposure(self.original_exposure)
        except CameraError as error:
            errors.append(error.message)
        try:
            actual = self._camera.set_automatic_exposure(
                self.original_auto_exposure in self._settings.automatic_exposure_modes
            )
            if actual != self.original_auto_exposure:
                errors.append(
                    f"Original automatic exposure mode {self.original_auto_exposure} was not restored: {actual}"
                )
        except CameraError as error:
            errors.append(error.message)
        return CameraRestoreResult(
            not errors, "; ".join(errors) if errors else "Original exposure controls restored"
        )
