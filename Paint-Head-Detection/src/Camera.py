"""Typed development camera wrapper. The detector API never imports this module."""

from __future__ import annotations

import platform
import time
from dataclasses import replace
from threading import RLock
from typing import cast

import cv2

from paint_head_detector.development.settings import (
    CameraBackend,
    CameraProperties,
    CameraSettings,
    DevelopmentSettingsRepository,
)
from paint_head_detector.errors import CameraError, ErrorReason
from paint_head_detector.models import Image


class Camera:
    """Own one camera stream and serialize capture/control/restart operations."""

    def __init__(
        self,
        cameraIndex: int | None = None,
        width: int | None = None,
        height: int | None = None,
        *,
        settings: CameraSettings | None = None,
        device: int | str | None = None,
        backend: int | str | None = None,
        fourcc: str | None = None,
        fps: float | None = None,
        open_timeout: float | None = None,
        retries: int | None = None,
        mjpg_preferred: bool = True,
        verbose_ae: bool = False,
    ) -> None:
        base = settings if settings is not None else DevelopmentSettingsRepository().load().camera
        self._settings = replace(
            base,
            device=device
            if device is not None
            else cameraIndex
            if cameraIndex is not None
            else base.device,
            width=base.width if width is None else width,
            height=base.height if height is None else height,
            fourcc=base.fourcc if fourcc is None else fourcc,
            fps=base.fps if fps is None else fps,
            open_timeout=base.open_timeout if open_timeout is None else open_timeout,
            retries=base.retries if retries is None else retries,
        )
        self._backend_override: int | None = None
        if isinstance(backend, int):
            self._backend_override = backend
        elif isinstance(backend, str):
            try:
                self._settings = replace(self._settings, backend=CameraBackend(backend.upper()))
            except ValueError as error:
                raise CameraError(
                    ErrorReason.CONFIGURATION_INVALID, f"Unknown camera backend: {backend}"
                ) from error
        self._fourcc: str | None = (
            self._settings.fourcc if mjpg_preferred or fourcc is not None else None
        )
        self._verbose_ae = verbose_ae
        self._io_lock = RLock()
        self._capture_device: cv2.VideoCapture | None = None
        self._start_stream()

    @property
    def width(self) -> int:
        return self._settings.width

    @property
    def height(self) -> int:
        return self._settings.height

    @property
    def device(self) -> int | str:
        return self._settings.device

    @property
    def active(self) -> bool:
        return self.isOpened()

    def _backend(self) -> int:
        if isinstance(self.device, str) and self.device.startswith(("http://", "https://")):
            return cv2.CAP_FFMPEG
        if self._backend_override is not None:
            return self._backend_override
        backend = self._settings.backend
        if backend is CameraBackend.AUTO:
            backend = (
                CameraBackend.V4L2
                if platform.system() == "Linux"
                else CameraBackend.DSHOW
                if platform.system() == "Windows"
                else CameraBackend.ANY
            )
        return {
            CameraBackend.ANY: cv2.CAP_ANY,
            CameraBackend.V4L2: cv2.CAP_V4L2,
            CameraBackend.DSHOW: cv2.CAP_DSHOW,
            CameraBackend.FFMPEG: cv2.CAP_FFMPEG,
        }[backend]

    def _require_capture(self) -> cv2.VideoCapture:
        capture = self._capture_device
        if capture is None or not capture.isOpened():
            raise CameraError(ErrorReason.CAMERA_UNAVAILABLE, f"Camera {self.device} is not open")
        return capture

    def _configure(self, capture: cv2.VideoCapture) -> None:
        try:
            if self._fourcc is not None:
                capture.set(cv2.CAP_PROP_FOURCC, self._fourcc_code(self._fourcc))
            capture.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
            capture.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
            capture.set(cv2.CAP_PROP_BUFFERSIZE, 1)
            capture.set(cv2.CAP_PROP_FPS, self._settings.fps)
        except cv2.error as error:
            raise CameraError(
                ErrorReason.CAMERA_CONTROL_FAILED,
                f"Could not configure camera {self.device}: {error}",
            ) from error
        time.sleep(self._settings.configuration_settle_delay)

    @staticmethod
    def _fourcc_code(value: str) -> int:
        if len(value) != 4:
            raise CameraError(
                ErrorReason.CONFIGURATION_INVALID, "Camera format must have four characters"
            )
        return cv2.VideoWriter.fourcc(value[0], value[1], value[2], value[3])

    def _start_stream(self) -> None:
        deadline = time.monotonic() + self._settings.open_timeout
        backend = self._backend()
        while time.monotonic() <= deadline:
            try:
                capture = cv2.VideoCapture(self.device, backend)
            except cv2.error as error:
                raise CameraError(
                    ErrorReason.CAMERA_UNAVAILABLE, f"Could not open camera {self.device}: {error}"
                ) from error
            if capture.isOpened():
                self._capture_device = capture
                try:
                    self._configure(capture)
                except CameraError:
                    self.close()
                    raise
                return
            capture.release()
            time.sleep(self._settings.retry_delay)
        self._capture_device = None

    def isOpened(self) -> bool:
        with self._io_lock:
            return self._capture_device is not None and self._capture_device.isOpened()

    def _get_property(self, property_id: int) -> float:
        try:
            return float(self._require_capture().get(property_id))
        except cv2.error as error:
            raise CameraError(
                ErrorReason.CAMERA_CONTROL_FAILED,
                f"Cannot read camera property {property_id}: {error}",
            ) from error

    def _set_property(self, property_id: int, value: float) -> bool:
        try:
            return bool(self._require_capture().set(property_id, value))
        except cv2.error as error:
            raise CameraError(
                ErrorReason.CAMERA_CONTROL_FAILED,
                f"Cannot set camera property {property_id} to {value}: {error}",
            ) from error

    def get_properties(self) -> CameraProperties:
        with self._io_lock:
            capture = self._require_capture()
            try:
                backend_name = capture.getBackendName()
            except cv2.error as error:
                raise CameraError(
                    ErrorReason.CAMERA_CONTROL_FAILED, f"Cannot read camera backend name: {error}"
                ) from error
            return CameraProperties(
                int(self._get_property(cv2.CAP_PROP_FRAME_WIDTH)),
                int(self._get_property(cv2.CAP_PROP_FRAME_HEIGHT)),
                self._get_property(cv2.CAP_PROP_FPS),
                int(self._get_property(cv2.CAP_PROP_FOURCC)),
                backend_name,
            )

    def set_resolution(self, width: int, height: int) -> None:
        with self._io_lock:
            if not self._set_property(cv2.CAP_PROP_FRAME_WIDTH, width) or not self._set_property(
                cv2.CAP_PROP_FRAME_HEIGHT, height
            ):
                raise CameraError(
                    ErrorReason.CAMERA_CONTROL_FAILED,
                    f"Camera rejected resolution {width}x{height}",
                )
            self._settings = replace(self._settings, width=width, height=height)

    def set_fps(self, fps: float) -> None:
        with self._io_lock:
            if not self._set_property(cv2.CAP_PROP_FPS, fps):
                raise CameraError(
                    ErrorReason.CAMERA_CONTROL_FAILED, f"Camera rejected frame rate {fps}"
                )
            self._settings = replace(self._settings, fps=fps)

    def set_fourcc(self, fourcc_str: str | None) -> None:
        with self._io_lock:
            if fourcc_str is not None and (
                len(fourcc_str) != 4
                or not self._set_property(cv2.CAP_PROP_FOURCC, self._fourcc_code(fourcc_str))
            ):
                raise CameraError(
                    ErrorReason.CAMERA_CONTROL_FAILED, f"Camera rejected format {fourcc_str}"
                )
            self._fourcc = fourcc_str

    def set_auto_exposure(self, enabled: bool) -> float:
        with self._io_lock:
            self.stop_stream()
            time.sleep(self._settings.stream_release_delay)
            self._start_stream()
            self._require_capture()
            candidates = (
                self._settings.automatic_exposure_values
                if enabled
                else self._settings.manual_exposure_values
            )
            for value in candidates:
                if self._verbose_ae:
                    print(f"Auto-exposure candidate: {value}")
                if self._set_property(cv2.CAP_PROP_AUTO_EXPOSURE, value):
                    time.sleep(self._settings.control_settle_delay)
                    return self._get_property(cv2.CAP_PROP_AUTO_EXPOSURE)
            raise CameraError(
                ErrorReason.CAMERA_CONTROL_FAILED,
                f"Camera could not {'enable' if enabled else 'disable'} automatic exposure",
            )

    def get_auto_exposure(self) -> float:
        with self._io_lock:
            return self._get_property(cv2.CAP_PROP_AUTO_EXPOSURE)

    def set_exposure(self, exposure_value: float) -> bool:
        with self._io_lock:
            accepted = self._set_property(cv2.CAP_PROP_EXPOSURE, exposure_value)
            time.sleep(self._settings.control_settle_delay)
            return bool(accepted)

    def get_exposure(self) -> float:
        with self._io_lock:
            return self._get_property(cv2.CAP_PROP_EXPOSURE)

    def capture(self, grab_only: bool = False, timeout: float | None = None) -> Image | None:
        with self._io_lock:
            capture = self._require_capture()
            deadline = time.monotonic() + (
                self._settings.read_timeout if timeout is None else timeout
            )
            for _ in range(self._settings.retries):
                try:
                    if grab_only:
                        ok = capture.grab()
                        ok, frame = capture.retrieve() if ok else (False, None)
                    else:
                        ok, frame = capture.read()
                except cv2.error as error:
                    raise CameraError(
                        ErrorReason.CAMERA_READ_FAILED, f"Camera read failed: {error}"
                    ) from error
                if ok and frame is not None:
                    return cast(Image, frame)
                if time.monotonic() > deadline:
                    break
            return None

    def close(self) -> None:
        with self._io_lock:
            capture, self._capture_device = self._capture_device, None
            if capture is not None:
                try:
                    capture.release()
                except cv2.error as error:
                    raise CameraError(
                        ErrorReason.CAMERA_UNAVAILABLE,
                        f"Could not close camera {self.device}: {error}",
                    ) from error

    def stopCapture(self) -> None:
        self.close()

    def stop_stream(self) -> None:
        self.close()

    def start_stream(self) -> None:
        with self._io_lock:
            self.close()
            self._start_stream()


if __name__ == "__main__":
    from paint_head_detector.development.camera_preview import main

    raise SystemExit(main())
