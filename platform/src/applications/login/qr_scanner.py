"""QR decoding from an injected fresh-image source; no camera settings mutation."""
from typing import Callable

import cv2
import numpy as np

from src.applications.login.i_qr_scanner import IQrScanner


class OpenCvQrScanner(IQrScanner):
    def __init__(self, capture_image: Callable[[], np.ndarray | None]) -> None:
        self._capture_image = capture_image
        self._detector = cv2.QRCodeDetector()

    def scan(self) -> str | None:
        """Decode one fresh owned image; acquisition failures remain visible to the adapter."""
        image = self._capture_image()
        if image is None:
            return None
        payload, _points, _straight = self._detector.detectAndDecode(image.copy())
        return payload or None
