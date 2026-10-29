"""Typed development adapter around the existing Camera.py component."""

from __future__ import annotations

from dataclasses import replace
from types import TracebackType

from Camera import Camera

from ..errors import CameraError, ErrorReason
from ..models import Image, ImageSize
from .settings import CameraProperties, CameraSettings


class CameraSession:
    def __init__(self, settings: CameraSettings, size: ImageSize) -> None:
        self._settings = replace(settings, width=size.width, height=size.height)
        self._camera: Camera | None = None

    def __enter__(self) -> CameraSession:
        self._camera = Camera(settings=self._settings)
        if not self._camera.isOpened():
            self._camera.close()
            self._camera = None
            raise CameraError(
                ErrorReason.CAMERA_UNAVAILABLE,
                f"Cannot open camera {self._settings.device}; check the connection and other camera applications",
            )
        properties = self.properties
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
        if self._camera is not None:
            self._camera.close()
            self._camera = None

    def _require_camera(self) -> Camera:
        if self._camera is None:
            raise CameraError(ErrorReason.CAMERA_UNAVAILABLE, "Camera session has not been opened")
        return self._camera

    @property
    def properties(self) -> CameraProperties:
        return self._require_camera().get_properties()

    @property
    def exposure(self) -> float:
        return self._require_camera().get_exposure()

    @property
    def automatic_exposure(self) -> float:
        return self._require_camera().get_auto_exposure()

    def set_automatic_exposure(self, enabled: bool) -> float:
        return self._require_camera().set_auto_exposure(enabled)

    def set_exposure(self, exposure: float) -> float:
        if not self._require_camera().set_exposure(exposure):
            raise CameraError(
                ErrorReason.CAMERA_CONTROL_FAILED, f"Camera rejected exposure {exposure}"
            )
        return self.exposure

    def read(self) -> Image:
        image = self._require_camera().capture()
        if image is None:
            raise CameraError(
                ErrorReason.CAMERA_READ_FAILED,
                f"Camera {self._settings.device} did not provide an image",
            )
        return image

    def settled_frame(self, frames: int) -> Image:
        if frames < 1:
            raise CameraError(
                ErrorReason.CONFIGURATION_INVALID, "Camera warm-up frame count must be positive"
            )
        image = self.read()
        for _ in range(frames - 1):
            image = self.read()
        return image
