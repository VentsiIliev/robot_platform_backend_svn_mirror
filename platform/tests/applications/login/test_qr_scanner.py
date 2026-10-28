import unittest
from unittest.mock import MagicMock

import numpy as np
import qrcode

from src.applications.login.qr_scanner import OpenCvQrScanner


class QrScannerTests(unittest.TestCase):
    def test_decodes_a_fresh_token_card_without_modifying_the_source_image(self):
        token = "robot-login-v1:" + "a" * 43
        image = np.array(qrcode.make(token).convert("RGB"))
        original = image.copy()
        capture = MagicMock(return_value=image)
        self.assertEqual(OpenCvQrScanner(capture).scan(), token)
        capture.assert_called_once_with()
        np.testing.assert_array_equal(image, original)

    def test_missing_frame_has_no_payload(self):
        self.assertIsNone(OpenCvQrScanner(lambda: None).scan())

    def test_fresh_capture_failure_is_not_replaced_with_an_old_frame(self):
        capture = MagicMock(side_effect=RuntimeError("fresh acquisition unavailable"))
        with self.assertRaises(RuntimeError):
            OpenCvQrScanner(capture).scan()
