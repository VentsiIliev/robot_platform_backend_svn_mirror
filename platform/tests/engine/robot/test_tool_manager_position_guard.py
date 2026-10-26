"""Tool changes must start at the configured staging position, never travel there."""
import unittest
from types import SimpleNamespace
from unittest.mock import MagicMock

from src.engine.robot.configuration.robot_settings import MovementGroup
from src.engine.robot.interfaces.tool_definition import ToolDefinition
from src.engine.robot.tool_changer import SlotConfig, ToolChangeStep, ToolChanger
from src.engine.robot.tool_manager import ToolManager


class ToolManagerPositionGuardTests(unittest.TestCase):
    def setUp(self):
        self.robot = MagicMock()
        self.robot.is_healthy.return_value = True
        self.robot.get_state.return_value = "idle"
        self.robot.get_current_velocity.return_value = 0.0
        self.robot.get_current_position_fresh.return_value = [100, 200, 300, 0, 0, 179]
        self.robot.get_current_position.return_value = [100, 200, 300, 0, 0, 179]
        self.robot.set_active_tool.return_value = True
        self.motion = MagicMock()
        self.motion.move_linear.return_value = True
        self.config = SimpleNamespace(robot_tool=0, robot_user=3)
        self.group = MovementGroup(position="[100, 200, 300, 0, 0, 179]")
        self.groups = SimpleNamespace(movement_groups={"Tool Changer": self.group})
        self.slot = SlotConfig(2, 7,
                               pickup_sequence=[ToolChangeStep(kind="attach"), ToolChangeStep(pose=[1] * 6)],
                               dropoff_sequence=[ToolChangeStep(kind="detach"), ToolChangeStep(pose=[2] * 6)])
        self.manager = ToolManager(
            self.motion, ToolChanger([self.slot], [ToolDefinition(7, "Vacuum")]),
            self.config, self.groups, tool_activator=self.robot, tool_change_group="Tool Changer")

    def assert_no_execution(self):
        self.motion.move_linear.assert_not_called()
        self.motion.move_ptp.assert_not_called()
        self.robot.set_active_tool.assert_not_called()
        self.assertFalse(self.manager.recovery_required)

    def test_pickup_away_from_staging_pose_has_no_side_effects(self):
        self.robot.get_current_position_fresh.return_value = [0] * 6
        ok, error = self.manager.pickup_tool(7)
        self.assertFalse(ok)
        self.assertIn("not at", error)
        self.assert_no_execution()
        self.assertEqual(self.config.robot_tool, 0)
        self.assertIsNone(self.manager.current_tool)
        self.assertFalse(self.slot.occupied)
        self.robot.get_current_position.assert_not_called()

    def test_every_position_and_rotation_axis_is_checked(self):
        expected = [100, 200, 300, 0, 0, 179]
        for index in range(6):
            with self.subTest(axis=index):
                pose = list(expected)
                pose[index] += 10.01 if index < 3 else 5.01
                self.robot.get_current_position_fresh.return_value = pose
                self.assertFalse(self.manager.pickup_gripper(7)[0])
                self.assert_no_execution()

    def test_dropoff_away_from_staging_pose_does_not_detach(self):
        self.assertTrue(self.manager.confirm_attached_tool(7)[0])
        self.robot.reset_mock()
        self.robot.get_current_position_fresh.return_value = [0] * 6
        self.assertFalse(self.manager.drop_off_tool(7)[0])
        self.assert_no_execution()
        self.assertEqual(self.manager.current_tool, 7)
        self.assertEqual(self.config.robot_tool, 7)
        self.assertFalse(self.slot.occupied)

    def test_editor_draft_cannot_bypass_guard(self):
        self.robot.get_current_position_fresh.return_value = [0] * 6
        self.assertFalse(self.manager.execute_sequence(2, [{"kind": "attach"}, {"pose": [1] * 6}])[0])
        self.assert_no_execution()

    def test_matching_pose_allows_pickup_and_dropoff(self):
        self.assertTrue(self.manager.pickup_tool(7)[0])
        self.assertEqual(self.manager.current_tool, 7)
        self.assertTrue(self.manager.drop_off_gripper(7)[0])
        self.assertIsNone(self.manager.current_tool)
        self.assertTrue(self.slot.occupied)
        self.assertEqual(self.robot.get_current_position_fresh.call_count, 2)

    def test_tolerance_boundaries_and_rotation_wrap_are_accepted(self):
        self.robot.get_current_position_fresh.return_value = [110, 190, 310, 5, -5, -179]
        self.assertTrue(self.manager.pickup_tool(7)[0])

    def test_missing_or_invalid_configured_position_fails_closed(self):
        for position in (None, "[]", "[1, 2, 3]", "invalid", "[1, 2, 3, 0, 0, NaN]",
                         "[1, 2, 3, 0, 0, Infinity]"):
            with self.subTest(position=position):
                self.group.position = position
                self.assertFalse(self.manager.pickup_tool(7)[0])
                self.assert_no_execution()
        self.groups.movement_groups.clear()
        self.assertFalse(self.manager.pickup_tool(7)[0])
        self.assert_no_execution()

    def test_missing_invalid_or_nonfinite_feedback_fails_closed(self):
        for pose in (None, [], [1, 2, 3], [100, 200, 300, 0, 0, float("nan")],
                     [100, 200, float("inf"), 0, 0, 179]):
            with self.subTest(pose=pose):
                self.robot.get_current_position_fresh.return_value = pose
                self.assertFalse(self.manager.pickup_tool(7)[0])
                self.assert_no_execution()

    def test_pose_read_exception_does_not_fall_back_to_cached_feedback(self):
        self.robot.get_current_position_fresh.side_effect = RuntimeError("feedback unavailable")
        self.assertFalse(self.manager.pickup_tool(7)[0])
        self.robot.get_current_position.assert_not_called()
        self.assert_no_execution()

    def test_missing_fresh_pose_reader_fails_closed(self):
        self.robot.get_current_position_fresh = None
        self.assertFalse(self.manager.pickup_tool(7)[0])
        self.assert_no_execution()

    def test_newly_configured_position_is_used_on_next_attempt(self):
        self.robot.get_current_position_fresh.return_value = [0] * 6
        self.assertFalse(self.manager.pickup_tool(7)[0])
        self.groups.movement_groups["Tool Changer"] = MovementGroup(position="[0, 0, 0, 0, 0, 0]")
        self.assertTrue(self.manager.pickup_tool(7)[0])
