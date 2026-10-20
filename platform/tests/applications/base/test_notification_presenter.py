import unittest
from unittest.mock import MagicMock, patch

from src.applications.base.notification_presenter import (
    NotificationTextResolver,
    UserNotificationPresenter,
)
from src.shared_contracts.events.notification_events import (
    DismissNotificationEvent,
    NotificationAction,
    NotificationActionEvent,
    NotificationSeverity,
    NotificationTopics,
    UserNotificationEvent,
)


class TestNotificationTextResolver(unittest.TestCase):

    def test_uses_fallback_when_translation_missing(self):
        resolver = NotificationTextResolver(translate=lambda key: key)

        text = resolver.resolve_text(
            key="notification.test.message",
            fallback="Fallback message",
            params={},
        )

        self.assertEqual(text, "Fallback message")

    def test_uses_translated_template_and_formats_params(self):
        resolver = NotificationTextResolver(
            translate=lambda key: {
                "notification.test.title": "Localized {name}",
            }.get(key, key)
        )

        text = resolver.resolve_text(
            key="notification.test.title",
            fallback="Fallback {name}",
            params={"name": "Glue"},
        )

        self.assertEqual(text, "Localized Glue")


class TestUserNotificationPresenter(unittest.TestCase):

    def _make_event(self, **overrides):
        payload = {
            "source": "tests",
            "severity": NotificationSeverity.CRITICAL,
            "title_key": "notification.test.title",
            "message_key": "notification.test.message",
            "fallback_title": "Fallback Title",
            "fallback_message": "Fallback Message",
            "params": {},
            "dedupe_key": None,
        }
        payload.update(overrides)
        return UserNotificationEvent(**payload)

    @patch("src.applications.base.notification_presenter.show_critical")
    def test_present_shows_critical_message(self, mock_show_critical):
        presenter = UserNotificationPresenter(
            parent=MagicMock(),
            messaging_service=MagicMock(),
            translate=lambda key: key,
        )

        presenter.present(self._make_event())

        mock_show_critical.assert_called_once_with(
            presenter._parent,
            "Fallback Title",
            "Fallback Message",
        )


    @patch("src.applications.base.notification_presenter.make_warning")
    def test_dedupes_consecutive_notifications_with_same_key(self, mock_make_warning):
        dialog = MagicMock()
        mock_make_warning.return_value = dialog
        presenter = UserNotificationPresenter(
            parent=MagicMock(),
            messaging_service=MagicMock(),
            translate=lambda key: key,
        )
        event = self._make_event(
            severity=NotificationSeverity.WARNING,
            dedupe_key="same-warning",
        )

        presenter.present(event)
        presenter.present(event)

        mock_make_warning.assert_called_once()
        dialog.open.assert_called_once_with()

    @patch("src.applications.base.notification_presenter.make_warning")
    def test_dismiss_closes_matching_keyed_notification(self, mock_make_warning):
        dialog = MagicMock()
        mock_make_warning.return_value = dialog
        presenter = UserNotificationPresenter(
            parent=MagicMock(),
            messaging_service=MagicMock(),
            translate=lambda key: key,
        )

        presenter.present(self._make_event(
            severity=NotificationSeverity.WARNING,
            dedupe_key="robot-disconnected",
        ))
        presenter._dismiss_notification(DismissNotificationEvent("robot-disconnected"))

        dialog.close.assert_called_once_with()
        self.assertNotIn("robot-disconnected", presenter._active_dialogs)

    def test_start_and_stop_manage_broker_subscription(self):
        broker = MagicMock()
        presenter = UserNotificationPresenter(
            parent=MagicMock(),
            messaging_service=broker,
            translate=lambda key: key,
        )

        presenter.start()
        presenter.stop()

        self.assertEqual(
            broker.subscribe.call_args_list,
            [
                unittest.mock.call(NotificationTopics.USER, presenter._on_notification),
                unittest.mock.call(NotificationTopics.DISMISS, presenter._on_dismiss),
            ],
        )
        self.assertEqual(
            broker.unsubscribe.call_args_list,
            [
                unittest.mock.call(NotificationTopics.USER, presenter._on_notification),
                unittest.mock.call(NotificationTopics.DISMISS, presenter._on_dismiss),
            ],
        )

    def test_action_selection_publishes_global_notification_action(self):
        broker = MagicMock()
        presenter = UserNotificationPresenter(
            parent=MagicMock(),
            messaging_service=broker,
            translate=lambda key: key,
        )
        dialog = MagicMock()
        event = self._make_event(
            dedupe_key="collision-1",
            actions=(NotificationAction(
                key="release_collision_hold",
                fallback_title="Release Collision Hold",
            ),),
        )
        presenter._action_dialog_events[dialog] = event

        with patch.object(presenter, "sender", return_value=dialog):
            presenter._on_action_selected("release_collision_hold")

        topic, payload = broker.publish.call_args.args
        self.assertEqual(topic, NotificationTopics.ACTION)
        self.assertIsInstance(payload, NotificationActionEvent)
        self.assertEqual(payload.action_key, "release_collision_hold")
        self.assertEqual(payload.dedupe_key, "collision-1")


class TestBusyNotification(unittest.TestCase):
    @patch("src.applications.base.notification_presenter.RecoveryProgressDialog")
    def test_busy_popup_is_nonblocking_deduplicated_and_dismissible(self, dialog_class):
        dialog = dialog_class.return_value
        presenter = UserNotificationPresenter(MagicMock(), MagicMock())
        event = UserNotificationEvent(source="test", severity=NotificationSeverity.INFO,
                                      fallback_title="Resetting collision hold", fallback_message="Please wait",
                                      dedupe_key="reset-progress", busy=True)
        presenter.present(event)
        presenter.present(event)
        dialog_class.assert_called_once_with(presenter._parent, "Resetting collision hold", "Please wait")
        dialog.open.assert_called_once()
        presenter._dismiss_notification(DismissNotificationEvent(dedupe_key="reset-progress"))
        dialog.close.assert_called_once()
        self.assertNotIn("reset-progress", presenter._active_dialogs)
