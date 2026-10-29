"""Standalone camera preview for development, without detector construction."""

import sys
import time

import cv2

from ..errors import PaintHeadError
from ..models import ImageSize
from .camera_session import CameraSession
from .settings import DevelopmentSettingsRepository
from .view import FrameRateMeter


def main() -> int:
    settings = DevelopmentSettingsRepository().load()
    meter = FrameRateMeter(settings.view.fps_window)
    try:
        with CameraSession(
            settings.camera, ImageSize(settings.camera.width, settings.camera.height)
        ) as camera:
            started = time.monotonic()
            while True:
                image = camera.read()
                cv2.putText(
                    image,
                    f"FPS: {meter.update():.1f}",
                    (20, 40),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.8,
                    (0, 255, 0),
                    2,
                )
                cv2.imshow("Camera Preview", image)
                key = cv2.waitKey(1) & 0xFF
                if key == ord("q"):
                    break
                if key == ord("p"):
                    print(camera.properties)
                if key == ord("t"):
                    camera.set_automatic_exposure(
                        camera.automatic_exposure not in settings.camera.automatic_exposure_modes
                    )
                if (
                    settings.runtime.duration
                    and time.monotonic() - started >= settings.runtime.duration
                ):
                    break
        return 0
    except PaintHeadError as error:
        print(f"{error.reason.value}: {error.message}", file=sys.stderr)
        return 2
    finally:
        cv2.destroyAllWindows()
