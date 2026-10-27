"""Compose pre-login access with the same credential and lockout as kiosk exit."""

import logging
from pathlib import Path

from PyQt6.QtCore import QCoreApplication

from src.applications.base.styled_message_box import show_warning
from src.bootstrap.kiosk_exit_guard import KioskExitGuard
from src.bootstrap.kiosk_password import KioskPassword


class ConnectionInformationAccess:
    def __init__(self, password_file: Path, authentication: KioskPassword | None = None):
        self._password_file = password_file
        self._authentication = authentication

    def __call__(self, parent) -> bool:
        try:
            if self._authentication is None:
                self._authentication = KioskPassword(self._password_file)
            guard = KioskExitGuard(
                self._authentication,
                title="Connection information",
                message="Enter the platform exit password to view connection information.",
                action="Open", context="Login",
            )
            guard.parent = parent
            return guard()
        except (OSError, ValueError, KeyError, TypeError):
            logging.getLogger(__name__).exception("Connection information credential is unavailable")
            translate = QCoreApplication.translate
            title = "Connection information"
            message = "The platform exit password is unavailable. Contact an administrator."
            show_warning(parent, translate("Login", title) or title,
                         translate("Login", message) or message)
            return False
