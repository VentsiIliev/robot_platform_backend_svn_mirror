"""Dedicated password verification for kiosk exit, independent of the operator session."""
import logging

from PyQt6.QtCore import QCoreApplication, QEvent
from PyQt6.QtWidgets import QDialog, QDialogButtonBox, QFormLayout, QLabel, QLineEdit

from src.applications.base.widgets.custom_virtual_keyboard import KeyboardLineEdit
from src.bootstrap.kiosk_password import KioskPassword

_LOGGER = logging.getLogger(__name__)


class KioskExitGuard:
    def __init__(self, authentication: KioskPassword):
        self._authentication = authentication
        self.parent = None

    @staticmethod
    def _t(source):
        return QCoreApplication.translate("KioskExitDialog", source) or source

    def verify(self, password: str) -> bool:
        try:
            return self._authentication.verify(password)
        except Exception:
            _LOGGER.exception("Kiosk exit password verification failed")
            return False

    def __call__(self) -> bool:
        class ExitDialog(QDialog):
            def changeEvent(self, event):
                if event.type() == QEvent.Type.LanguageChange:
                    retranslate()
                super().changeEvent(event)

        dialog = ExitDialog(self.parent)
        dialog.setWindowTitle(self._t("Exit kiosk mode"))
        layout = QFormLayout(dialog)
        password = KeyboardLineEdit()
        password.setEchoMode(QLineEdit.EchoMode.Password)
        message = QLabel(self._t("Enter the kiosk exit password to close the application."))
        layout.addRow(message)
        password_label = QLabel()
        layout.addRow(password_label, password)
        buttons = QDialogButtonBox()
        exit_button = buttons.addButton(self._t("Exit kiosk mode"), QDialogButtonBox.ButtonRole.AcceptRole)
        cancel_button = buttons.addButton(self._t("Cancel"), QDialogButtonBox.ButtonRole.RejectRole)
        cancel_button.clicked.connect(dialog.reject)

        failed = False

        def retranslate():
            dialog.setWindowTitle(self._t("Exit kiosk mode"))
            password_label.setText(self._t("Password"))
            exit_button.setText(self._t("Exit kiosk mode"))
            cancel_button.setText(self._t("Cancel"))
            message.setText(self._t(
                "Incorrect password or temporarily locked. Try again later." if failed else
                "Enter the kiosk exit password to close the application."
            ))

        def attempt_exit():
            nonlocal failed
            allowed = self.verify(password.text())
            password.clear()
            if allowed:
                dialog.accept()
            else:
                failed = True
                retranslate()
                password.setFocus()

        exit_button.clicked.connect(attempt_exit)
        layout.addRow(buttons)
        retranslate()
        password.setFocus()
        try:
            return dialog.exec() == QDialog.DialogCode.Accepted
        finally:
            password.clear()
            dialog.deleteLater()
