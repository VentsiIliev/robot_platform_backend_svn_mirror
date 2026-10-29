"""Development window lifecycle and FPS measurement."""

import time
from collections import deque
from collections.abc import Callable
from enum import Enum

import cv2

from ..errors import ErrorReason, PaintHeadError
from ..models import DetectionResult, Image
from .renderer import OverlayRenderer
from .settings import ViewSettings


class ViewAction(Enum):
    NONE = "none"
    QUIT = "quit"
    SAVE = "save"


class FrameRateMeter:
    def __init__(self, window: int, clock: Callable[[], float] = time.monotonic) -> None:
        self._timestamps: deque[float] = deque(maxlen=window)
        self._clock = clock

    def update(self) -> float:
        self._timestamps.append(self._clock())
        elapsed = self._timestamps[-1] - self._timestamps[0]
        return (len(self._timestamps) - 1) / elapsed if elapsed > 0 else 0.0


class DevelopmentView:
    def __init__(self, renderer: OverlayRenderer, settings: ViewSettings) -> None:
        self._renderer = renderer
        self._settings = settings
        self._opened = False

    def open(self) -> None:
        try:
            settings = self._settings
            cv2.namedWindow(settings.main_title, cv2.WINDOW_NORMAL)
            cv2.resizeWindow(settings.main_title, settings.main_width, settings.main_height)
            if settings.show_edges:
                cv2.namedWindow(settings.edges_title, cv2.WINDOW_NORMAL)
                cv2.resizeWindow(settings.edges_title, settings.edges_width, settings.edges_height)
            self._opened = True
        except cv2.error as error:
            cv2.destroyAllWindows()
            raise PaintHeadError(
                ErrorReason.DEVELOPMENT_UI_FAILED, f"Could not open development windows: {error}"
            ) from error

    def display(self, image: Image, result: DetectionResult, fps: float) -> ViewAction:
        if not self._opened:
            self.open()
        try:
            cv2.imshow(self._settings.main_title, self._renderer.draw(image, result, fps=fps))
            if self._settings.show_edges:
                cv2.imshow(self._settings.edges_title, result.diagnostics.edges)
            key = cv2.waitKey(1) & 0xFF
        except cv2.error as error:
            raise PaintHeadError(
                ErrorReason.DEVELOPMENT_UI_FAILED, f"Could not update development windows: {error}"
            ) from error
        if key == ord("q"):
            return ViewAction.QUIT
        if key == ord("s"):
            return ViewAction.SAVE
        return ViewAction.NONE

    def close(self) -> None:
        if self._opened:
            cv2.destroyAllWindows()
            self._opened = False
