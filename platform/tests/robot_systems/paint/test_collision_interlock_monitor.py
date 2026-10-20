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
        self.assertTrue(event.actions[0].close_dialog)
        vacuum_pump.turn_off_nonblocking.assert_called_once_with()

        monitor._last_publish_monotonic = 0.0
        monitor._poll_once()
        messaging.publish.assert_called_once()

    def test_release_action_acknowledges_backend_interlock(self):
        robot = MagicMock()
        robot.acknowledge_collision_interlock.return_value = {"success": True}
        monitor = PaintCollisionInterlockMonitor(robot, MagicMock())

        monitor._release_collision_hold()

        robot.acknowledge_collision_interlock.assert_called_once_with()

    def test_release_clears_process_and_backend_through_one_owner(self):
        from src.robot_systems.paint.processes.paint.paint_process import PaintProcess
        from src.robot_systems.paint.processes.paint.results import PaintOperationResult, PaintFailureCode
        from src.shared_contracts.events.process_events import ProcessState
        robot = MagicMock()
        robot.get_execution_status.return_value = {"motion_interlock": {"active": False}}
        robot.acknowledge_collision_interlock.return_value = {"success": True}
        process = PaintProcess(MagicMock(), MagicMock(), robot_service=robot)
        process._state = ProcessState.ERROR
        process._last_failure = PaintOperationResult.failed(
            PaintFailureCode.MOTION, "collision_monitor", "collision").failure
        monitor = PaintCollisionInterlockMonitor(
            robot, MagicMock(), acknowledge_collision=process.acknowledge_collision)

        monitor._release_collision_hold()

        self.assertEqual(process.state, ProcessState.IDLE)
        self.assertIsNone(process.last_failure)
        self.assertFalse(process.collision_acknowledgement_required())
        robot.acknowledge_collision_interlock.assert_called_once_with()
        # A stale second dialog is harmless and does not reset the observer again.
        self.assertTrue(process.acknowledge_collision()[0])
        robot.acknowledge_collision_interlock.assert_called_once_with()

    def test_failed_recovery_keeps_fault_and_offers_retry_in_same_notice(self):
        from src.robot_systems.paint.processes.paint.paint_process import PaintProcess
        from src.robot_systems.paint.processes.paint.results import PaintOperationResult, PaintFailureCode
        from src.shared_contracts.events.process_events import ProcessState
        robot = MagicMock()
        robot.acknowledge_collision_interlock.return_value = {"success": False, "error": "Joint_5 not clear"}
        process = PaintProcess(MagicMock(), MagicMock(), robot_service=robot)
        process._state = ProcessState.ERROR
        process._last_failure = PaintOperationResult.failed(
            PaintFailureCode.MOTION, "collision_monitor", "collision").failure
        messaging = MagicMock()
        monitor = PaintCollisionInterlockMonitor(
            robot, messaging, acknowledge_collision=process.acknowledge_collision)
        monitor._last_event_key = "collision-1"

        monitor._release_collision_hold()

        self.assertEqual(process.state, ProcessState.ERROR)
        self.assertIsNotNone(process.last_failure)
        event = next(call.args[1] for call in messaging.publish.call_args_list
                     if isinstance(call.args[1], UserNotificationEvent) and not call.args[1].busy)
        self.assertIsNone(event.detail)
        self.assertEqual(event.fallback_title, "Reset not completed")
        self.assertIn("Motion remains held", event.fallback_message)
        self.assertEqual(event.actions[1].key, monitor.ACTION_RELEASE)

    def test_progress_visible_for_entire_release_and_dismissed_on_success(self):
        messaging = MagicMock()
        monitor = None
        def acknowledge():
            events = [call.args[1] for call in messaging.publish.call_args_list]
            self.assertTrue(any(isinstance(event, UserNotificationEvent) and event.busy for event in events))
            self.assertTrue(monitor._release_in_progress.is_set())
            # A poll seeing the backend cleared must not close progress before
            # local process recovery finishes.
            monitor._robot.get_execution_status.return_value = {"motion_interlock": {"active": False}}
            monitor._poll_once()
            self.assertFalse(any(getattr(event, "dedupe_key", None) == monitor.PROGRESS_KEY
                                 and not isinstance(event, UserNotificationEvent) for event in events))
            return True, "cleared"
        monitor = PaintCollisionInterlockMonitor(MagicMock(), messaging, acknowledge_collision=acknowledge)
        monitor._release_collision_hold()
        topic, event = messaging.publish.call_args.args
        self.assertEqual(topic, NotificationTopics.DISMISS)
        self.assertEqual(event.dedupe_key, monitor.PROGRESS_KEY)
        self.assertFalse(monitor._release_in_progress.is_set())

    def test_progress_dismissed_on_exception_and_retry_offered(self):
        messaging = MagicMock()
        monitor = PaintCollisionInterlockMonitor(
            MagicMock(), messaging, acknowledge_collision=MagicMock(side_effect=RuntimeError("offline")))
        monitor._last_event_key = "collision-1"
        monitor._release_collision_hold()
        self.assertFalse(monitor._release_in_progress.is_set())
        notices = [call.args[1] for call in messaging.publish.call_args_list
                   if isinstance(call.args[1], UserNotificationEvent)]
        self.assertTrue(notices[0].busy)
        self.assertFalse(notices[-1].busy)
        self.assertEqual(notices[-1].actions[1].key, monitor.ACTION_RELEASE)

    def test_raw_detector_details_are_logged_not_shown_to_operator(self):
        messaging = MagicMock()
        monitor = PaintCollisionInterlockMonitor(MagicMock(), messaging)
        raw = "collision detected on Joint_3 by cpp_realtime_dynamics; operator acknowledgement required"
        with self.assertLogs("PaintCollisionInterlockMonitor", level="WARNING") as logs:
            monitor._publish_collision_notice(raw, "event-1")
        event = messaging.publish.call_args.args[1]
        self.assertIsNone(event.detail)
        self.assertNotIn("cpp_realtime_dynamics", event.fallback_message)
        self.assertNotIn("Joint_3", event.fallback_message)
        self.assertIn(raw, "\n".join(logs.output))
