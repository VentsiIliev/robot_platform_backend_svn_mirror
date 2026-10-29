"""Typed development boundary around the shared engine vision camera."""

from __future__ import annotations

import math
from dataclasses import replace
from types import TracebackType
from typing import cast

import cv2

from src.engine.vision.implementation.plvision.PLVision.Camera import Camera

from ..errors import CameraError, ErrorReason
from ..models import Image, ImageSize
from .settings import CameraBackend, CameraProperties, CameraSettings


class CameraSession:
    def __init__(self, settings: CameraSettings, size: ImageSize) -> None:
        self._settings = replace(settings, width=size.width, height=size.height)
        self._camera: Camera | None = None

    def __enter__(self) -> CameraSession:
        settings = self._settings
        backend = None if settings.backend is CameraBackend.AUTO else settings.backend.value
        try:
            self._camera = Camera(
                device=settings.device,
                width=settings.width,
                height=settings.height,
                backend=backend,
                fourcc=settings.fourcc,
                fps=settings.fps,
                open_timeout=settings.open_timeout,
                retries=settings.retries,
                retry_delay=settings.retry_delay,
                configuration_settle_delay=settings.configuration_settle_delay,
                control_settle_delay=settings.control_settle_delay,
                stream_release_delay=settings.stream_release_delay,
                automatic_exposure_values=settings.automatic_exposure_values,
                manual_exposure_values=settings.manual_exposure_values,
            )
            if not self._camera.isOpened():
                raise CameraError(
                    ErrorReason.CAMERA_UNAVAILABLE,
                    f"Cannot open camera {settings.device}; check the connection and other camera applications",
                ) from self._camera.last_open_error
            properties = self.properties
        except CameraError:
            self._close()
            raise
        except (cv2.error, OSError, RuntimeError, TypeError, ValueError) as error:
            self._close()
            raise CameraError(
                ErrorReason.CAMERA_UNAVAILABLE,
                f"Cannot initialize camera {settings.device}: {error}",
            ) from error
        code = properties.fourcc
        fourcc = "".join(chr((code >> (8 * index)) & 255) for index in range(4))
        print(f"Camera stream: {fourcc}, reported {properties.fps:g} FPS", flush=True)
        return self

    def __exit__(
        self,
        error_type: type[BaseException] | None,
        error: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        self._close()

    def _close(self) -> None:
        camera, self._camera = self._camera, None
        if camera is not None:
            camera.close()

    def _require_camera(self) -> Camera:
        if self._camera is None:
            raise CameraError(ErrorReason.CAMERA_UNAVAILABLE, "Camera session has not been opened")
        return self._camera

    @staticmethod
    def _control_value(value: object, label: str) -> float:
        if not isinstance(value, (float, int)) or not math.isfinite(value):
            raise CameraError(
                ErrorReason.CAMERA_CONTROL_FAILED, f"Camera did not report a finite {label} value"
            )
        return float(value)

    @property
    def properties(self) -> CameraProperties:
        try:
            properties = self._require_camera().read_properties()
            return CameraProperties(
                int(properties.width),
                int(properties.height),
                float(properties.fps),
                int(properties.fourcc),
                str(properties.backend_name),
            )
        except (cv2.error, OSError, RuntimeError, TypeError, ValueError) as error:
            raise CameraError(
                ErrorReason.CAMERA_CONTROL_FAILED, f"Cannot read camera properties: {error}"
            ) from error

    @property
    def exposure(self) -> float:
        try:
            return self._control_value(self._require_camera().get_exposure(), "exposure")
        except (cv2.error, OSError, RuntimeError) as error:
            raise CameraError(
                ErrorReason.CAMERA_CONTROL_FAILED, f"Cannot read camera exposure: {error}"
            ) from error

    @property
    def automatic_exposure(self) -> float:
        try:
            return self._control_value(
                self._require_camera().get_auto_exposure(), "automatic exposure"
            )
        except (cv2.error, OSError, RuntimeError) as error:
            raise CameraError(
                ErrorReason.CAMERA_CONTROL_FAILED, f"Cannot read automatic exposure: {error}"
            ) from error

    def set_automatic_exposure(self, enabled: bool) -> float:
        try:
            actual = self._control_value(
                self._require_camera().set_auto_exposure(enabled), "automatic exposure"
            )
        except (cv2.error, OSError, RuntimeError) as error:
            raise CameraError(
                ErrorReason.CAMERA_CONTROL_FAILED, f"Cannot change automatic exposure: {error}"
            ) from error
        expected_modes = (
            self._settings.automatic_exposure_modes
            if enabled
            else self._settings.manual_exposure_modes
        )
        if actual not in expected_modes:
            raise CameraError(
                ErrorReason.CAMERA_CONTROL_FAILED,
                f"Camera did not enter {'automatic' if enabled else 'manual'} exposure mode: {actual}",
            )
        return actual

    def set_exposure(self, exposure: float) -> float:
        try:
            accepted = self._require_camera().set_exposure(exposure)
        except (cv2.error, OSError, RuntimeError) as error:
            raise CameraError(
                ErrorReason.CAMERA_CONTROL_FAILED, f"Cannot set camera exposure: {error}"
            ) from error
        if not accepted:
            raise CameraError(
                ErrorReason.CAMERA_CONTROL_FAILED, f"Camera rejected exposure {exposure}"
            )
        return self.exposure

    def read(self) -> Image:
        try:
            image = self._require_camera().capture(
                timeout=self._settings.read_timeout, max_attempts=self._settings.retries
            )
        except (cv2.error, OSError, RuntimeError) as error:
            raise CameraError(
                ErrorReason.CAMERA_READ_FAILED, f"Camera read failed: {error}"
            ) from error
        if image is None:
            raise CameraError(
                ErrorReason.CAMERA_READ_FAILED,
                f"Camera {self._settings.device} did not provide an image",
            )
        return cast(Image, image)

    def settled_frame(self, frames: int) -> Image:
        if frames < 1:
            raise CameraError(
                ErrorReason.CONFIGURATION_INVALID, "Camera warm-up frame count must be positive"
            )
        image = self.read()
        for _ in range(frames - 1):
            image = self.read()
        return image
