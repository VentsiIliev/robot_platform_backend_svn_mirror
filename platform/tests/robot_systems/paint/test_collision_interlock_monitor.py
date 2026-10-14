import unittest
from unittest.mock import MagicMock

from src.robot_systems.paint.diagnostics.collision_interlock_monitor import (
    PaintCollisionInterlockMonitor,
)
from src.shared_contracts.events.notification_events import NotificationTopics, UserNotificationEvent


class TestPaintCollisionInterlockMonitor(unittest.TestCase):
    def test_live_backend_hold_publishes_actionable_notification_once(self):
        robot = MagicMock()
        robot.get_execution_status.return_value = {
            "motion_interlock": {"active": True, "reason": "collision on Joint_2"},
            "collision_event": {"timestamp": 12.5},
        }
        messaging = MagicMock()
        vacuum_pump = MagicMock()
        vacuum_pump.turn_off_nonblocking.return_value = True
        monitor = PaintCollisionInterlockMonitor(
            robot,
            messaging,
            vacuum_pump=vacuum_pump,
        )

        monitor._poll_once()
        monitor._poll_once()

        messaging.publish.assert_called_once()
        topic, event = messaging.publish.call_args.args
        self.assertEqual(topic, NotificationTopics.USER)
        self.assertIsInstance(event, UserNotificationEvent)
        self.assertIn("release the collision hold", event.fallback_message)
        self.assertEqual(
            [action.key for action in event.actions],
            [monitor.ACTION_KEEP_HELD, monitor.ACTION_RELEASE],
        )
        vacuum_pump.turn_off_nonblocking.assert_called_once_with()

    def test_release_action_acknowledges_backend_interlock(self):
        robot = MagicMock()
        robot.acknowledge_collision_interlock.return_value = {"success": True}
        monitor = PaintCollisionInterlockMonitor(robot, MagicMock())

        monitor._release_collision_hold()

        robot.acknowledge_collision_interlock.assert_called_once_with()
