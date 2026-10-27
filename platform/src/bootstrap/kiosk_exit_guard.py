"""Dedicated password verification for kiosk exit, independent of the operator session."""
import logging

from PyQt6.QtCore import QCoreApplication, QEvent, Qt
from PyQt6.QtWidgets import QDialog, QDialogButtonBox, QFormLayout, QLabel, QLineEdit

from src.applications.base.widgets.custom_virtual_keyboard import KeyboardLineEdit
from src.bootstrap.kiosk_password import KioskPassword
from pl_gui.settings.settings_view.styles import ACTION_BTN_STYLE, GHOST_BTN_STYLE

_LOGGER = logging.getLogger(__name__)


class KioskExitGuard:
    def __init__(self, authentication: KioskPassword, *, title="Exit kiosk mode",
                 message="Enter the kiosk exit password to close the application.",
                 action="Exit kiosk mode", context="KioskExitDialog"):
        self._authentication = authentication
        self._title = title
        self._message = message
        self._action = action
        self._context = context
        self.parent = None

    def _t(self, source):
        return QCoreApplication.translate(self._context, source) or source

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
        dialog.setMinimumWidth(480)
        dialog.setWindowTitle(self._t(self._title))
        layout = QFormLayout(dialog)
        password = KeyboardLineEdit()
        password.setEchoMode(QLineEdit.EchoMode.Password)
        message = QLabel(self._t(self._message))
        message.setWordWrap(True)
        layout.addRow(message)
        password_label = QLabel()
        layout.addRow(password_label, password)
        buttons = QDialogButtonBox()
        exit_button = buttons.addButton(self._t(self._action), QDialogButtonBox.ButtonRole.AcceptRole)
        cancel_button = buttons.addButton(self._t("Cancel"), QDialogButtonBox.ButtonRole.RejectRole)
        exit_button.setStyleSheet(ACTION_BTN_STYLE)
        cancel_button.setStyleSheet(GHOST_BTN_STYLE)
        for button in (exit_button, cancel_button):
            button.setCursor(Qt.CursorShape.PointingHandCursor)
        cancel_button.clicked.connect(dialog.reject)

        failed = False

        def retranslate():
            dialog.setWindowTitle(self._t(self._title))
            password_label.setText(self._t("Password"))
            exit_button.setText(self._t(self._action))
            cancel_button.setText(self._t("Cancel"))
            message.setText(self._t(
                "Incorrect password or temporarily locked. Try again later." if failed else
                self._message
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
