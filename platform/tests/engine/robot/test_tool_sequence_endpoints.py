"""Optional endpoint moves share normal execution, cancellation, and position guards."""
import unittest
from threading import Event
from types import SimpleNamespace
from unittest.mock import MagicMock

from src.engine.robot.configuration.robot_settings import MovementGroup
from src.engine.robot.configuration.tool_changer_settings import ToolChangerSettings, ToolChangerSettingsSerializer
from src.engine.robot.interfaces.tool_definition import ToolDefinition
from src.engine.robot.interfaces.tool_operation_result import ToolErrorCode
from src.engine.robot.tool_changer import SlotConfig, ToolChangeStep, ToolChanger
from src.engine.robot.tool_manager import ToolManager


class ToolSequenceEndpointTests(unittest.TestCase):
    def setUp(self):
        self.actual = [99.0] * 6
        self.staging = [10, 20, 30, 0, 0, 0]
        self.config = SimpleNamespace(robot_tool=0, robot_user=3)
        self.robot = MagicMock()
        self.robot.is_healthy.return_value = True
        self.robot.get_state.return_value = 'idle'
        self.robot.get_current_velocity.return_value = 0.0
        self.robot.get_current_position_fresh.side_effect = lambda: list(self.actual)
        self.robot.set_active_tool.return_value = True
        self.motion = MagicMock()
        def move(**kwargs):
            self.actual = list(kwargs['position'])
            return True
        self.motion.move_linear.side_effect = move
        self.motion.move_ptp.side_effect = move
        self.group = MovementGroup(position=str(self.staging), velocity=12, acceleration=18,
                                   motion_type='linear')
        self.groups = SimpleNamespace(movement_groups={'Tool Changer': self.group})
        self.slot = SlotConfig(2, 7)
        self.manager = ToolManager(self.motion, ToolChanger([self.slot], [ToolDefinition(7, 'Vacuum')]),
                                   self.config, self.groups, tool_activator=self.robot,
                                   tool_change_group='Tool Changer')

    @staticmethod
    def steps(start=True, finish=True):
        result = [{'kind': 'motion', 'pose': [1] * 6}]
        if start:
            result.insert(0, {'kind': 'start_at_tool_changer'})
        if finish:
            result.append({'kind': 'finish_at_tool_changer'})
        return result

    def test_start_and_finish_add_moves_around_taught_steps(self):
        result = self.manager.execute_sequence(2, self.steps())
        self.assertTrue(result.success, result.message)
        calls = self.motion.move_linear.call_args_list
        self.assertEqual([call.kwargs['position'] for call in calls], [self.staging, [1] * 6, self.staging])
        self.assertEqual(calls[0].kwargs['velocity'], 12)
        self.assertEqual(calls[-1].kwargs['acceleration'], 18)
        self.assertTrue(all(call.kwargs['wait_to_reach'] for call in calls))
        self.assertEqual(self.actual, self.staging)

    def test_start_off_keeps_position_guard_even_if_finish_is_on(self):
        result = self.manager.execute_sequence(2, self.steps(start=False))
        self.assertEqual(result.error.code, ToolErrorCode.NOT_AT_TOOL_CHANGER)
        self.motion.move_linear.assert_not_called()

    def test_finish_off_leaves_robot_at_last_taught_step(self):
        self.assertTrue(self.manager.execute_sequence(2, self.steps(finish=False)).success)
        self.assertEqual(self.motion.move_linear.call_count, 2)
        self.assertEqual(self.actual, [1] * 6)

    def test_both_off_add_no_moves_when_already_at_staging(self):
        self.actual = list(self.staging)
        self.assertTrue(self.manager.execute_sequence(2, self.steps(False, False)).success)
        self.motion.move_linear.assert_called_once()

    def test_arrival_is_verified_before_taught_steps(self):
        self.motion.move_linear.side_effect = None
        self.motion.move_linear.return_value = True  # Command succeeds but feedback never arrives there.
        result = self.manager.execute_sequence(2, self.steps())
        self.assertEqual(result.error.code, ToolErrorCode.NOT_AT_TOOL_CHANGER)
        self.assertEqual(result.error.step_number, 1)
        self.assertEqual(self.motion.move_linear.call_count, 1)

    def test_missing_feedback_blocks_start_move(self):
        self.robot.get_current_position_fresh.side_effect = TimeoutError('offline')
        result = self.manager.execute_sequence(2, self.steps())
        self.assertEqual(result.error.code, ToolErrorCode.POSE_UNAVAILABLE)
        self.motion.move_linear.assert_not_called()

    def test_invalid_finish_configuration_blocks_the_whole_sequence(self):
        self.group.velocity = 0
        result = self.manager.execute_sequence(2, self.steps())
        self.assertEqual(result.error.code, ToolErrorCode.INVALID_SEQUENCE)
        self.motion.move_linear.assert_not_called()

    def test_changed_staging_settings_are_used_on_the_next_run(self):
        self.group.position = '[20, 30, 40, 0, 0, 0]'
        self.assertTrue(self.manager.execute_sequence(2, self.steps()).success)
        self.assertEqual(self.motion.move_linear.call_args_list[0].kwargs['position'], [20, 30, 40, 0, 0, 0])

    def test_endpoint_moves_use_configured_ptp_type(self):
        self.group.motion_type = 'ptp'
        self.assertTrue(self.manager.execute_sequence(2, self.steps()).success)
        self.assertEqual(self.motion.move_ptp.call_count, 2)
        self.assertEqual(self.motion.move_linear.call_count, 1)

    def test_cancellation_after_start_prevents_taught_steps_and_finish(self):
        cancelled = Event()
        def move(**kwargs):
            self.actual = list(kwargs['position'])
            cancelled.set()
            return True
        self.motion.move_linear.side_effect = move
        result = self.manager.execute_sequence(2, self.steps(), cancelled)
        self.assertEqual(result.error.code, ToolErrorCode.CANCELLED)
        self.assertEqual(self.motion.move_linear.call_count, 1)

    def test_saved_pickup_and_dropoff_use_endpoint_options_and_current_tcp(self):
        self.slot.pickup_sequence = [ToolChangeStep(kind='start_at_tool_changer'),
                                     ToolChangeStep(kind='attach'), ToolChangeStep(kind='finish_at_tool_changer')]
        self.slot.dropoff_sequence = [ToolChangeStep(kind='start_at_tool_changer'),
                                      ToolChangeStep(kind='detach'), ToolChangeStep(kind='finish_at_tool_changer')]
        self.assertTrue(self.manager.pickup_tool(7).success)
        self.assertEqual([c.kwargs['tool'] for c in self.motion.move_linear.call_args_list], [0, 7])
        self.motion.reset_mock()
        self.assertTrue(self.manager.drop_off_tool(7).success)
        self.assertEqual([c.kwargs['tool'] for c in self.motion.move_linear.call_args_list], [7, 0])

    def test_serialization_preserves_options_without_freezing_a_pose(self):
        self.slot.pickup_sequence = [ToolChangeStep.from_dict(step) for step in self.steps()]
        serializer = ToolChangerSettingsSerializer()
        saved = serializer.to_dict(ToolChangerSettings(slots=[self.slot]))
        restored = serializer.from_dict(saved)
        self.assertEqual([s.kind for s in restored.slots[0].pickup_sequence],
                         ['start_at_tool_changer', 'motion', 'finish_at_tool_changer'])
        self.assertNotIn('pose', saved['slots'][0]['pickup_sequence'][0])

    def test_misplaced_start_is_rejected_before_any_motion(self):
        result = self.manager.execute_sequence(2, list(reversed(self.steps())))
        self.assertEqual(result.error.code, ToolErrorCode.INVALID_SEQUENCE)
        self.motion.move_linear.assert_not_called()

    def test_endpoint_navigation_callback_uses_current_tcp_and_supports_fast_linear(self):
        self.group.motion_type = 'fast_lin'
        calls = []
        def navigate(group_name, cancelled, tool, user):
            calls.append((group_name, cancelled, tool, user))
            self.actual = list(self.staging)
            return True
        self.manager._tool_change_mover = navigate
        self.slot.pickup_sequence = [ToolChangeStep(kind='start_at_tool_changer'),
                                     ToolChangeStep(kind='attach'), ToolChangeStep(kind='finish_at_tool_changer')]
        cancelled = Event()
        self.assertTrue(self.manager.pickup_tool(7, cancelled=cancelled).success)
        self.assertEqual(calls, [('Tool Changer', cancelled, 0, 3), ('Tool Changer', cancelled, 7, 3)])
        self.motion.move_linear.assert_not_called()
        self.motion.move_ptp.assert_not_called()

    def test_failed_finish_preserves_attachment_and_requires_recovery(self):
        self.slot.pickup_sequence = [ToolChangeStep(kind='start_at_tool_changer'),
                                     ToolChangeStep(kind='attach'), ToolChangeStep(kind='finish_at_tool_changer')]
        def move(**kwargs):
            if self.motion.move_linear.call_count == 2:
                return False
            self.actual = list(kwargs['position'])
            return True
        self.motion.move_linear.side_effect = move
        result = self.manager.pickup_tool(7)
        self.assertEqual(result.error.code, ToolErrorCode.MOTION_FAILED)
        self.assertEqual(result.error.step_number, 3)
        self.assertEqual(self.manager.current_tool, 7)
        self.assertTrue(self.manager.recovery_required)
