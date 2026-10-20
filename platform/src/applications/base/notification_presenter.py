from __future__ import annotations

import logging
from typing import Callable, Mapping

from PyQt6.QtCore import QObject, pyqtSignal
from PyQt6.QtWidgets import QMessageBox, QWidget

from src.applications.base.recovery_progress_dialog import RecoveryProgressDialog
from src.applications.base.styled_message_box import (
    ActionWarningDialog,
    DialogAction,
    make_critical,
    make_info,
    make_warning,
    show_critical,
    show_info,
    show_warning,
)
from src.engine.core.i_messaging_service import IMessagingService
from src.shared_contracts.events.notification_events import (
    DismissNotificationEvent,
    NotificationActionEvent,
    NotificationSeverity,
    NotificationTopics,
    UserNotificationEvent,
)


class _NotificationBridge(QObject):
    notification = pyqtSignal(object)
    dismiss = pyqtSignal(object)


class NotificationTextResolver:
    def __init__(self, translate: Callable[[str], str] | None = None) -> None:
        self._translate = translate or (lambda key: key)

    def resolve_text(self, key: str, fallback: str, params: Mapping[str, object]) -> str:
        template = ""
        if key:
            translated = self._translate(key)
            if translated and translated != key:
                template = translated
        if not template:
            template = fallback or key
        if not template:
            return ""
        try:
            return template.format(**dict(params))
        except Exception:
            return template


class UserNotificationPresenter(QObject):
    def __init__(
        self,
        parent: QWidget,
        messaging_service: IMessagingService,
        translate: Callable[[str], str] | None = None,
    ) -> None:
        super().__init__()
        self._parent = parent
        self._messaging = messaging_service
        self._resolver = NotificationTextResolver(translate=translate)
        self._bridge = _NotificationBridge()
        self._bridge.notification.connect(self._show_notification)
        self._bridge.dismiss.connect(self._dismiss_notification)
        self._active = False
        self._last_dedupe_key: str | None = None
        self._active_dialogs: dict[str, QWidget] = {}
        self._action_dialog_events: dict[ActionWarningDialog, UserNotificationEvent] = {}
        self._logger = logging.getLogger(self.__class__.__name__)

    def start(self) -> None:
        if self._active:
            return
        self._messaging.subscribe(NotificationTopics.USER, self._on_notification)
        self._messaging.subscribe(NotificationTopics.DISMISS, self._on_dismiss)
        self._active = True

    def stop(self) -> None:
        if not self._active:
            return
        try:
            self._messaging.unsubscribe(NotificationTopics.USER, self._on_notification)
            self._messaging.unsubscribe(NotificationTopics.DISMISS, self._on_dismiss)
        except Exception:
            self._logger.warning("Failed to unsubscribe notification presenter", exc_info=True)
        for dialog in list(self._active_dialogs.values()):
            dialog.close()
        self._active_dialogs.clear()
        self._action_dialog_events.clear()
        self._active = False

    def present(self, event: UserNotificationEvent) -> None:
        self._show_notification(event)

    def _on_notification(self, event: UserNotificationEvent) -> None:
        if not self._active:
            return
        self._bridge.notification.emit(event)

    def _on_dismiss(self, event: DismissNotificationEvent | str) -> None:
        if not self._active:
            return
        self._bridge.dismiss.emit(event)

    def _show_notification(self, event: UserNotificationEvent) -> None:
        if event.dedupe_key is not None and event.dedupe_key == self._last_dedupe_key:
            return

        title = self._resolver.resolve_text(event.title_key, event.fallback_title, event.params)
        message = self._resolver.resolve_text(event.message_key, event.fallback_message, event.params)
        if event.detail:
            message = f"{message}\n\n{event.detail}" if message else event.detail

        if event.dedupe_key:
            self._show_dismissible_notification(event, title, message)
            self._last_dedupe_key = event.dedupe_key
            return

        if event.severity == NotificationSeverity.INFO:
            show_info(self._parent, title, message)
        elif event.severity == NotificationSeverity.WARNING:
            show_warning(self._parent, title, message)
        else:
            show_critical(self._parent, title, message)

        self._last_dedupe_key = event.dedupe_key

    def _show_dismissible_notification(
        self,
        event: UserNotificationEvent,
        title: str,
        message: str,
    ) -> None:
        existing = self._active_dialogs.get(event.dedupe_key)
        if existing is not None:
            return

        if event.busy:
            dialog = RecoveryProgressDialog(self._parent, title, message)
            self._active_dialogs[event.dedupe_key] = dialog
            dialog.open()
            return

        if event.actions:
            actions = tuple(
                DialogAction(
                    key=action.key,
                    text=self._resolver.resolve_text(
                        action.title_key,
                        action.fallback_title,
                        event.params,
                    ),
                    primary=action.primary,
                    close_dialog=action.close_dialog,
                )
                for action in event.actions
            )
            dialog = ActionWarningDialog(
                self._parent,
                title,
                message,
                heading=title,
                actions=actions,
            )
            dialog.action_selected.connect(self._on_action_selected)
            dialog.finished.connect(self._on_action_dialog_finished)
            self._active_dialogs[event.dedupe_key] = dialog
            self._action_dialog_events[dialog] = event
            dialog.open()
            return

        if event.severity == NotificationSeverity.INFO:
            dialog = make_info(self._parent, title, message)
        elif event.severity == NotificationSeverity.WARNING:
            dialog = make_warning(self._parent, title, message)
        else:
            dialog = make_critical(self._parent, title, message)

        self._active_dialogs[event.dedupe_key] = dialog
        dialog.open()

    def _on_action_selected(self, action_key: str) -> None:
        dialog = self.sender()
        event = self._action_dialog_events.get(dialog)
        if event is None:
            return
        self._messaging.publish(
            NotificationTopics.ACTION,
            NotificationActionEvent(
                source=event.source,
                action_key=str(action_key),
                dedupe_key=event.dedupe_key,
            ),
        )

    def _on_action_dialog_finished(self, _result: int) -> None:
        dialog = self.sender()
        event = self._action_dialog_events.pop(dialog, None)
        if event is None or event.dedupe_key is None:
            return
        self._active_dialogs.pop(event.dedupe_key, None)
        if self._last_dedupe_key == event.dedupe_key:
            self._last_dedupe_key = None

    def _dismiss_notification(self, event: DismissNotificationEvent | str) -> None:
        dedupe_key = event.dedupe_key if isinstance(event, DismissNotificationEvent) else str(event)
        dialog = self._active_dialogs.pop(dedupe_key, None)
        if dialog is not None:
            self._action_dialog_events.pop(dialog, None)
            dialog.close()
        if self._last_dedupe_key == dedupe_key:
            self._last_dedupe_key = None
