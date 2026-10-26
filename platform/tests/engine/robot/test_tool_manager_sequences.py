import unittest
from threading import Event
from types import SimpleNamespace
from unittest.mock import MagicMock

from src.engine.robot.interfaces.tool_definition import ToolDefinition
from src.engine.robot.tool_changer import SlotConfig, ToolChangeStep, ToolChanger
from src.engine.robot.tool_manager import ToolManager


class ToolManagerSequenceTests(unittest.TestCase):
    def _manager(self, pickup, dropoff=None):
        motion = MagicMock()
        motion.move_linear.return_value = True
        activator = MagicMock()
        activator.set_active_tool.return_value = True
        activator.is_healthy.return_value = True
        activator.get_state.return_value = "idle"
        activator.get_current_velocity.return_value = 0.0
        slot = SlotConfig(
            id=2,
            tool_id=7,
            pickup_sequence=pickup,
            dropoff_sequence=dropoff or [],
        )
        changer = ToolChanger([slot], [ToolDefinition(7, "Vacuum")])
        config = SimpleNamespace(robot_tool=1, robot_user=0)
        manager = ToolManager(
            motion_service=motion,
            tool_changer=changer,
            robot_config=config,
            movement_groups=SimpleNamespace(movement_groups={}),
            tool_activator=activator,
        )
        return manager, motion, activator, config

    def test_pickup_executes_taught_motion_and_activation_boundary(self):
        manager, motion, activator, config = self._manager([
            ToolChangeStep(kind="motion", pose=[1, 2, 3, 4, 5, 6]),
            ToolChangeStep(kind="attach", label="Attach"),
        ])
        ok, error = manager.pickup_gripper(7)
        self.assertTrue(ok, error)
        motion.move_linear.assert_called_once()
        activator.set_active_tool.assert_called_once_with(7)
        self.assertEqual(config.robot_tool, 7)
        self.assertEqual(manager.current_gripper, 7)

    def test_operator_confirmation_fails_closed_without_callback(self):
        manager, _, _, _ = self._manager([
            ToolChangeStep(kind="operator_confirm", label="Lock the tool"),
        ])
        ok, error = manager.pickup_gripper(7)
        self.assertFalse(ok)
        self.assertIn("Operator confirmation required", error)

    def test_confirmation_is_validated_before_any_motion(self):
        manager, motion, _, _ = self._manager([
            ToolChangeStep(pose=[0] * 6), ToolChangeStep(kind="operator_confirm")])
        self.assertFalse(manager.pickup_tool(7)[0])
        motion.move_linear.assert_not_called()

    def test_invalid_final_motion_is_rejected_before_any_motion(self):
        for change in ({"velocity": 0}, {"acceleration": float("nan")},
                       {"motion_type": "unknown"}, {"blend_radius": -1}):
            with self.subTest(change=change):
                manager, motion, _, _ = self._manager([
                    ToolChangeStep(pose=[0] * 6), ToolChangeStep(pose=[1] * 6, **change)])
                self.assertFalse(manager.pickup_tool(7)[0])
                motion.move_linear.assert_not_called()

    def test_pickup_cannot_replace_a_held_tool(self):
        manager, motion, _, _ = self._manager([ToolChangeStep(pose=[0] * 6)])
        self.assertTrue(manager.pickup_tool(7)[0])
        motion.reset_mock()
        manager._current_gripper = 9
        self.assertFalse(manager.pickup_tool(7)[0])
        motion.move_linear.assert_not_called()

    def test_dropoff_records_empty_flange_at_detach_even_if_retreat_fails(self):
        manager, motion, _, config = self._manager(
            [ToolChangeStep(kind="attach")],
            [ToolChangeStep(kind="detach"), ToolChangeStep(pose=[0] * 6)])
        self.assertTrue(manager.pickup_tool(7)[0])
        motion.move_linear.return_value = False
        self.assertFalse(manager.drop_off_tool(7)[0])
        self.assertIsNone(manager.current_tool)
        self.assertEqual(config.robot_tool, 0)
        self.assertTrue(manager._tool_changer.is_slot_occupied(2))
        self.assertTrue(manager.recovery_required)

    def test_failed_retreat_preserves_attachment_and_requires_inspection(self):
        manager, motion, _, config = self._manager([
            ToolChangeStep(kind="attach"), ToolChangeStep(pose=[0] * 6)])
        motion.move_linear.return_value = False
        self.assertFalse(manager.pickup_tool(7)[0])
        self.assertEqual(manager.current_tool, 7)
        self.assertEqual(config.robot_tool, 7)
        self.assertFalse(manager._tool_changer.is_slot_occupied(2))
        self.assertTrue(manager.recovery_required)
        self.assertFalse(manager.drop_off_tool(7)[0])
        self.assertTrue(manager.confirm_attached_tool(7)[0])
        self.assertFalse(manager.recovery_required)

    def test_failed_motion_is_not_retried_and_blocks_automatic_replay(self):
        manager, motion, _, _ = self._manager([ToolChangeStep(pose=[0] * 6)])
        motion.move_linear.side_effect = RuntimeError("Request-sent")
        self.assertFalse(manager.pickup_tool(7)[0])
        self.assertFalse(manager.pickup_tool(7)[0])
        self.assertEqual(motion.move_linear.call_count, 1)

    def test_activation_failure_does_not_update_tcp_or_attachment(self):
        manager, _, activator, config = self._manager([ToolChangeStep(kind="attach")])
        activator.set_active_tool.return_value = False
        self.assertFalse(manager.pickup_tool(7)[0])
        self.assertEqual(config.robot_tool, 1)
        self.assertIsNone(manager.current_tool)
        self.assertTrue(manager.recovery_required)

    def test_cancellation_interrupts_wait_and_prevents_later_motion(self):
        manager, motion, _, _ = self._manager([
            ToolChangeStep(pose=[0] * 6), ToolChangeStep(kind="wait", wait_seconds=30),
            ToolChangeStep(pose=[1] * 6)])
        cancelled = Event()
        motion.move_linear.side_effect = lambda **_: cancelled.set() or True
        self.assertFalse(manager.pickup_tool(7, cancelled=cancelled)[0])
        self.assertEqual(motion.move_linear.call_count, 1)

    def test_pre_cancelled_pickup_does_not_require_recovery(self):
        manager, motion, _, _ = self._manager([ToolChangeStep(pose=[0] * 6)])
        cancelled = Event()
        cancelled.set()
        self.assertFalse(manager.pickup_tool(7, cancelled=cancelled)[0])
        motion.move_linear.assert_not_called()
        self.assertFalse(manager.recovery_required)

    def test_concurrent_operation_is_rejected_instead_of_queued(self):
        manager, motion, _, _ = self._manager([ToolChangeStep(pose=[0] * 6)])
        with manager._lock:
            self.assertFalse(manager.pickup_tool(7)[0])
            self.assertFalse(manager.execute_sequence(2, [{"pose": [0] * 6}])[0])
        motion.move_linear.assert_not_called()

    def test_unhealthy_or_moving_robot_prevents_motion(self):
        for state, velocity, healthy in [("moving", 0, True), ("idle", 1, True),
                                          ("idle", 0, False), ("fault", 0, True)]:
            with self.subTest(state=state, velocity=velocity, healthy=healthy):
                manager, motion, activator, _ = self._manager([ToolChangeStep(pose=[0] * 6)])
                activator.get_state.return_value = state
                activator.get_current_velocity.return_value = velocity
                activator.is_healthy.return_value = healthy
                self.assertFalse(manager.pickup_tool(7)[0])
                motion.move_linear.assert_not_called()

    def test_editor_preview_does_not_commit_physical_attachment(self):
        manager, _, _, config = self._manager([])
        self.assertTrue(manager.execute_sequence(2, [{"kind": "attach"}])[0])
        self.assertEqual(config.robot_tool, 7)
        self.assertIsNone(manager.current_tool)

    def test_pickup_and_dropoff_roundtrip(self):
        manager, _, _, _ = self._manager([ToolChangeStep(kind="attach")],
                                          [ToolChangeStep(kind="detach")])
        self.assertTrue(manager.pickup_tool(7)[0])
        self.assertEqual(manager.current_tool, 7)
        self.assertTrue(manager.drop_off_tool(7)[0])
        self.assertIsNone(manager.current_tool)
        self.assertTrue(manager._tool_changer.is_slot_occupied(2))

    def test_latest_settings_are_used_and_runtime_occupancy_is_preserved(self):
        manager, motion, _, _ = self._manager([ToolChangeStep(kind="attach")])
        config = SimpleNamespace(robot_tool=3, robot_user=4)
        slot = SlotConfig(2, 7, pickup_sequence=[ToolChangeStep(kind="attach")],
                          dropoff_sequence=[ToolChangeStep(pose=[9] * 6), ToolChangeStep(kind="detach")])
        def latest():
            from copy import deepcopy
            return (ToolChanger([deepcopy(slot)], [ToolDefinition(7, "Updated")]), config,
                    SimpleNamespace(movement_groups={}))
        manager._configuration_provider = latest
        self.assertTrue(manager.pickup_tool(7)[0])
        self.assertTrue(manager.drop_off_tool(7)[0])
        self.assertEqual(motion.move_linear.call_args.kwargs["position"], [9] * 6)
        self.assertEqual(motion.move_linear.call_args.kwargs["user"], 4)
        self.assertEqual(manager.get_tools()[0].name, "Updated")
        self.assertTrue(manager._tool_changer.is_slot_occupied(2))

    def test_wait_uses_cancellation_event_instead_of_uninterruptible_sleep(self):
        manager, motion, _, _ = self._manager([
            ToolChangeStep(kind="wait", wait_seconds=30), ToolChangeStep(pose=[0] * 6)])
        cancelled = MagicMock()
        cancelled.is_set.return_value = False
        cancelled.wait.return_value = True
        self.assertFalse(manager.pickup_tool(7, cancelled=cancelled)[0])
        cancelled.wait.assert_called_once_with(30)
        motion.move_linear.assert_not_called()

    def test_changed_held_tool_slot_is_not_used_for_dropoff(self):
        manager, motion, _, config = self._manager([ToolChangeStep(kind="attach")])
        self.assertTrue(manager.pickup_tool(7)[0])
        manager._configuration_provider = lambda: (
            ToolChanger([SlotConfig(3, 7, dropoff_sequence=[ToolChangeStep(pose=[1] * 6)])],
                        [ToolDefinition(7, "Vacuum")]), config, SimpleNamespace(movement_groups={}))
        self.assertFalse(manager.drop_off_tool(7)[0])
        motion.move_linear.assert_not_called()

    def test_legacy_movement_groups_use_same_validated_executor(self):
        manager, motion, _, _ = self._manager([])
        group = SimpleNamespace(points=[], parse_position=lambda: [1] * 6,
                                velocity=5, acceleration=10)
        manager._movement_groups.movement_groups = {"SLOT 2 PICKUP": group}
        self.assertTrue(manager.pickup_tool(7)[0])
        motion.move_linear.assert_called_once()
        self.assertEqual(manager.current_tool, 7)


if __name__ == "__main__":
    unittest.main()
