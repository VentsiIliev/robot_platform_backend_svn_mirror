import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PyQt6.QtCore import QTimer
from PyQt6.QtWidgets import QApplication, QDialog, QLabel, QPushButton

from src.applications.base.widgets.custom_virtual_keyboard import KeyboardLineEdit
from src.bootstrap.connection_information_access import ConnectionInformationAccess
from src.bootstrap.kiosk_exit_guard import KioskExitGuard
from src.bootstrap.kiosk_password import KioskPassword, write_password_file


class TestConnectionInformationAccess(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def test_same_credential_and_lockout_as_exit(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "password.json"
            write_password_file(path, "test-password-123")
            auth = KioskPassword(path)
            access = ConnectionInformationAccess(path, auth)
            exit_guard = KioskExitGuard(auth)
            with patch.object(QDialog, "exec", return_value=QDialog.DialogCode.Rejected):
                self.assertFalse(access(None))
            self.assertIs(auth, access._authentication)
            self.assertTrue(exit_guard.verify("test-password-123"))
            for _ in range(5):
                self.assertFalse(exit_guard.verify("wrong"))
            self.assertFalse(access._authentication.verify("test-password-123"))

    def test_missing_credential_fails_closed(self):
        with patch("src.bootstrap.connection_information_access.show_warning") as warning:
            with self.assertLogs("src.bootstrap.connection_information_access", level="ERROR"):
                self.assertFalse(ConnectionInformationAccess(Path("/missing/credential"))(None))
        warning.assert_called_once()

    def test_wrong_password_does_not_close_prompt_and_correct_password_opens(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "password.json"
            write_password_file(path, "test-password-123")
            access = ConnectionInformationAccess(path)
            observed = []

            def enter():
                dialog = self.app.activeModalWidget()
                field = dialog.findChild(KeyboardLineEdit)
                button = next(button for button in dialog.findChildren(QPushButton) if button.text() == "Open")
                field.setText("wrong")
                button.click()
                observed.append(dialog.result() != QDialog.DialogCode.Accepted)
                observed.append(any("Incorrect password" in label.text() for label in dialog.findChildren(QLabel)))
                observed.append(field.text() == "")
                field.setText("test-password-123")
                button.click()

            QTimer.singleShot(0, enter)
            self.assertTrue(access(None))
            self.assertEqual([True, True, True], observed)
