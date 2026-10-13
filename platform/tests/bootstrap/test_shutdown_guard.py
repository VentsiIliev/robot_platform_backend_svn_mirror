import os
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import unittest
from unittest.mock import Mock, patch

from PyQt6.QtWidgets import QApplication

from src.bootstrap.shutdown_guard import ShutdownGuard


class TestShutdownGuard(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    @patch("src.bootstrap.shutdown_guard.show_warning")
    def test_active_state_blocks_before_password_guard(self, warning):
        password_guard = Mock(return_value=True)
        guard = ShutdownGuard(lambda: "process_active", password_guard)

        self.assertFalse(guard())

        password_guard.assert_not_called()
        warning.assert_called_once()

    @patch("src.bootstrap.shutdown_guard.show_warning")
    def test_idle_state_delegates_to_password_guard(self, warning):
        password_guard = Mock(return_value=True)
        guard = ShutdownGuard(lambda: None, password_guard)

        self.assertTrue(guard())

        password_guard.assert_called_once_with()
        warning.assert_not_called()

    @patch("src.bootstrap.shutdown_guard.show_warning")
    def test_readiness_failure_blocks_shutdown(self, warning):
        guard = ShutdownGuard(Mock(side_effect=RuntimeError("unavailable")))

        with self.assertLogs("src.bootstrap.shutdown_guard", level="ERROR"):
            self.assertFalse(guard())

        warning.assert_called_once()
