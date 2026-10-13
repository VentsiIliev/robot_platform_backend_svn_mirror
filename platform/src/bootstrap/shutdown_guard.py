"""Prevent platform exit until the robot system reports a safe idle state."""

import logging
from typing import Callable

from PyQt6.QtCore import QCoreApplication

from src.applications.base.styled_message_box import show_warning


_LOGGER = logging.getLogger(__name__)


class ShutdownGuard:
    """Run a non-mutating readiness check before any exit authentication."""

    def __init__(
        self,
        block_reason: Callable[[], str | None],
        next_guard: Callable[[], bool] | None = None,
        parent=None,
    ) -> None:
        self._block_reason = block_reason
        self._next_guard = next_guard
        self.parent = parent

    def __call__(self) -> bool:
        try:
            reason = self._block_reason()
        except Exception:
            _LOGGER.exception("Shutdown readiness check failed")
            reason = "state_unknown"

        if reason:
            show_warning(
                self.parent,
                self._t("Shutdown not allowed"),
                self._message(reason),
            )
            return False
        return self._next_guard() if self._next_guard is not None else True

    def _message(self, reason: str) -> str:
        messages = {
            "process_active": "Stop the active process before shutting down the platform.",
            "robot_moving": "Stop the robot and wait until motion has finished before shutting down the platform.",
            "state_unknown": "Robot state could not be verified. Check the robot connection before shutting down the platform.",
        }
        return self._t(messages.get(reason, messages["state_unknown"]))

    @staticmethod
    def _t(text: str) -> str:
        return QCoreApplication.translate("ShutdownGuard", text) or text
