import unittest
from unittest.mock import MagicMock

from src.applications.tool_settings.service.tool_settings_application_service import ToolSettingsApplicationService
from src.engine.common_settings_ids import CommonSettingsID
from src.engine.robot.configuration import ToolChangerSettings
from src.engine.robot.interfaces.tool_definition import ToolDefinition
from src.engine.robot.tool_changer import SlotConfig
from src.engine.robot.tool_changer import ToolChangeStep


def _make_tc(tools=None, slots=None):
    return ToolChangerSettings(tools=tools or [], slots=slots or [])


def _make_svc(tc=None):
    ss = MagicMock()
    ss.get.return_value = tc or _make_tc()
    svc = ToolSettingsApplicationService(ss)
    return svc, ss


class TestToolSettingsApplicationServiceTools(unittest.TestCase):

    def test_get_tools_delegates_to_settings(self):
        tc = _make_tc(tools=[ToolDefinition(1, "G")])
        svc, ss = _make_svc(tc)
        result = svc.get_tools()
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].id, 1)
        ss.get.assert_called_with(CommonSettingsID.TOOL_CHANGER_CONFIG)

    def test_add_tool_duplicate_id_returns_false_no_save(self):
        tc = _make_tc(tools=[ToolDefinition(1, "G")])
        svc, ss = _make_svc(tc)
        ok, msg = svc.add_tool(1, "Another")
        self.assertFalse(ok)
        self.assertIn("already exists", msg)
        ss.save.assert_not_called()

    def test_add_tool_new_id_returns_true_and_saves(self):
        svc, ss = _make_svc()
        ok, msg = svc.add_tool(5, "New")
        self.assertTrue(ok)
        self.assertEqual(msg, "Tool added")
        ss.save.assert_called_once()

    def test_add_tool_saves_with_correct_key(self):
        svc, ss = _make_svc()
        svc.add_tool(5, "New")
        self.assertEqual(ss.save.call_args[0][0], CommonSettingsID.TOOL_CHANGER_CONFIG)

    def test_update_tool_existing_returns_true_and_saves(self):
        tc = _make_tc(tools=[ToolDefinition(1, "Old")])
        svc, ss = _make_svc(tc)
        ok, msg = svc.update_tool(1, "New")
        self.assertTrue(ok)
        self.assertEqual(msg, "Tool updated")
        ss.save.assert_called_once()

    def test_update_tool_not_found_returns_false_no_save(self):
        svc, ss = _make_svc()
        ok, msg = svc.update_tool(99, "X")
        self.assertFalse(ok)
        self.assertIn("not found", msg)
        ss.save.assert_not_called()

    def test_remove_tool_assigned_to_slot_returns_false(self):
        tc = _make_tc(
            tools=[ToolDefinition(1, "G")],
            slots=[SlotConfig(id=10, tool_id=1)],
        )
        svc, ss = _make_svc(tc)
        ok, msg = svc.remove_tool(1)
        self.assertFalse(ok)
        self.assertIn("slot", msg)
        ss.save.assert_not_called()

    def test_remove_tool_not_found_returns_false(self):
        svc, ss = _make_svc()
        ok, msg = svc.remove_tool(99)
        self.assertFalse(ok)
        ss.save.assert_not_called()

    def test_remove_tool_success_returns_true_and_saves(self):
        tc = _make_tc(tools=[ToolDefinition(1, "G")])
        svc, ss = _make_svc(tc)
        ok, msg = svc.remove_tool(1)
        self.assertTrue(ok)
        self.assertEqual(msg, "Tool removed")
        ss.save.assert_called_once()


class TestToolSettingsApplicationServiceSlots(unittest.TestCase):

    def test_get_slots_delegates_to_settings(self):
        tc = _make_tc(slots=[SlotConfig(id=10, tool_id=None)])
        svc, ss = _make_svc(tc)
        result = svc.get_slots()
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].id, 10)

    def test_update_slot_unknown_tool_id_returns_false(self):
        tc = _make_tc(slots=[SlotConfig(id=10, tool_id=None)])
        svc, ss = _make_svc(tc)
        ok, msg = svc.update_slot(10, 99)
        self.assertFalse(ok)
        self.assertIn("does not exist", msg)
        ss.save.assert_not_called()

    def test_update_slot_unknown_slot_id_returns_false(self):
        tc = _make_tc(tools=[ToolDefinition(1, "G")])
        svc, ss = _make_svc(tc)
        ok, msg = svc.update_slot(999, 1)
        self.assertFalse(ok)
        self.assertIn("not found", msg)
        ss.save.assert_not_called()

    def test_update_slot_success_saves(self):
        tc = _make_tc(
            tools=[ToolDefinition(1, "G")],
            slots=[SlotConfig(id=10, tool_id=None)],
        )
        svc, ss = _make_svc(tc)
        ok, _ = svc.update_slot(10, 1)
        self.assertTrue(ok)
        ss.save.assert_called_once()

    def test_update_slot_none_unassigns(self):
        tc = _make_tc(slots=[SlotConfig(id=10, tool_id=1)])
        svc, ss = _make_svc(tc)
        ok, _ = svc.update_slot(10, None)
        self.assertTrue(ok)
        ss.save.assert_called_once()

    def test_add_slot_duplicate_id_returns_false(self):
        tc = _make_tc(slots=[SlotConfig(id=10, tool_id=None)])
        svc, ss = _make_svc(tc)
        ok, msg = svc.add_slot(10, None)
        self.assertFalse(ok)
        self.assertIn("already exists", msg)
        ss.save.assert_not_called()

    def test_add_slot_unknown_tool_id_returns_false(self):
        svc, ss = _make_svc()
        ok, msg = svc.add_slot(20, 5)
        self.assertFalse(ok)
        self.assertIn("does not exist", msg)
        ss.save.assert_not_called()

    def test_add_slot_with_valid_tool_saves(self):
        tc = _make_tc(tools=[ToolDefinition(1, "G")])
        svc, ss = _make_svc(tc)
        ok, msg = svc.add_slot(20, 1)
        self.assertTrue(ok)
        self.assertEqual(msg, "Slot added")
        ss.save.assert_called_once()

    def test_add_slot_with_none_tool_saves(self):
        svc, ss = _make_svc()
        ok, _ = svc.add_slot(20, None)
        self.assertTrue(ok)
        ss.save.assert_called_once()

    def test_remove_slot_not_found_returns_false(self):
        svc, ss = _make_svc()
        ok, _ = svc.remove_slot(999)
        self.assertFalse(ok)
        ss.save.assert_not_called()

    def test_remove_slot_success_returns_true_and_saves(self):
        tc = _make_tc(slots=[SlotConfig(id=10, tool_id=None)])
        svc, ss = _make_svc(tc)
        ok, msg = svc.remove_slot(10)
        self.assertTrue(ok)
        self.assertEqual(msg, "Slot removed")
        ss.save.assert_called_once()

    def test_update_slot_sequences_persists_typed_steps(self):
        tc = _make_tc(slots=[SlotConfig(id=10, tool_id=None)])
        svc, ss = _make_svc(tc)
        pickup = [{"kind": "motion", "pose": [1, 2, 3, 4, 5, 6]}]
        ok, _ = svc.update_slot_sequences(10, pickup, [{"kind": "attach"}])
        self.assertTrue(ok)
        self.assertIsInstance(tc.slots[0].pickup_sequence[0], ToolChangeStep)
        self.assertEqual(tc.slots[0].dropoff_sequence[0].kind, "attach")


class TestToolSettingsApplicationServiceCalibration(unittest.TestCase):
    def test_update_tool_geometry_edits_backend_with_loaded_revision(self):
        tc = ToolChangerSettings(tools=[ToolDefinition(2, "Vacuum")], reference_tool_id=99)
        ss = MagicMock()
        ss.get.return_value = tc
        robot = MagicMock()
        robot.get_state.return_value = 'idle'
        robot.get_current_velocity.return_value = 0.0
        registry = MagicMock()
        registry.get_configuration.return_value = {
            'revision': 'loaded_revision',
            'tools': {'reference_tool_id': 1, 'tool_id_map': {'2': 'TOOL_2'},
                      'tool_definitions': {'TOOL_2': {'relative_transform': [0]*6}}},
        }
        registry.update_definition.return_value = (True, 'Saved')
        service = ToolSettingsApplicationService(ss, robot, registry)
        service.get_tools()
        ok, _ = service.update_tool_geometry(2, [1, 2, 3, 0, 0, 0], 'vacuum')
        self.assertTrue(ok)
        registry.update_definition.assert_called_once_with(2, {
            'reference_tool_id': 1, 'relative_transform': [1, 2, 3, 0, 0, 0],
            'collision_profile': 'vacuum'}, 'loaded_revision')
        self.assertEqual(tc.tools[0].relative_transform, [0]*6)
        ss.save.assert_not_called()

    def test_unavailable_backend_cannot_save_platform_geometry(self):
        tc = ToolChangerSettings(tools=[ToolDefinition(2, "Vacuum")])
        service, settings = _make_svc(tc)
        ok, _ = service.update_tool_geometry(2, [1]*6)
        self.assertFalse(ok)
        settings.save.assert_not_called()


if __name__ == "__main__":
    unittest.main()


class TestSequenceExecution(unittest.TestCase):
    def setUp(self):
        from threading import Event
        from types import SimpleNamespace
        self.cancelled = Event()
        self.robot = MagicMock()
        self.robot.is_healthy.return_value = True
        self.robot.get_state.return_value = 'idle'
        self.robot.get_current_velocity.return_value = 0.0
        self.robot.move_linear.return_value = True
        self.robot.set_active_tool.return_value = True
        self.robot.stop_motion.return_value = True
        self.config = SimpleNamespace(robot_tool=0, robot_user=3)
        self.settings = MagicMock()
        tc = _make_tc(slots=[SlotConfig(id=10, tool_id=7)])
        self.settings.get.side_effect = lambda key: tc if key == CommonSettingsID.TOOL_CHANGER_CONFIG else self.config
        self.service = ToolSettingsApplicationService(self.settings, robot_service=self.robot)
        self.steps = [{'kind': 'motion', 'pose': [i] * 6} for i in (1, 2, 3)]

    def test_runs_draft_in_order_and_waits_for_each_move(self):
        ok, message = self.service.execute_sequence(10, self.steps, self.cancelled)
        self.assertTrue(ok, message)
        calls = self.robot.move_linear.call_args_list
        self.assertEqual([c.kwargs['position'] for c in calls], [[i] * 6 for i in (1, 2, 3)])
        self.assertTrue(all(c.kwargs['wait_to_reach'] for c in calls))
        self.assertTrue(all(c.kwargs['user'] == 3 for c in calls))
        self.settings.save.assert_not_called()

    def test_failed_step_prevents_following_moves(self):
        self.robot.move_linear.side_effect = [True, False]
        self.assertFalse(self.service.execute_sequence(10, self.steps, self.cancelled)[0])
        self.assertEqual(self.robot.move_linear.call_count, 2)

    def test_cancellation_prevents_next_step(self):
        def move(**kwargs):
            self.cancelled.set()
            return True
        self.robot.move_linear.side_effect = move
        self.assertFalse(self.service.execute_sequence(10, self.steps, self.cancelled)[0])
        self.assertEqual(self.robot.move_linear.call_count, 1)

    def test_confirmation_action_is_rejected_before_any_motion(self):
        self.steps.append({'kind': 'operator_confirm'})
        self.assertFalse(self.service.execute_sequence(10, self.steps, self.cancelled)[0])
        self.robot.move_linear.assert_not_called()

    def test_stationary_check_prevents_starting_while_jogging(self):
        self.robot.get_current_velocity.return_value = 2.0
        self.assertFalse(self.service.execute_sequence(10, self.steps, self.cancelled)[0])
        self.robot.move_linear.assert_not_called()

    def test_saved_tcp_changes_apply_to_subsequent_moves(self):
        steps = [self.steps[0], {'kind': 'attach'}, self.steps[1], {'kind': 'detach'}, self.steps[2]]
        self.assertTrue(self.service.execute_sequence(10, steps, self.cancelled)[0])
        self.assertEqual([c.kwargs['tool'] for c in self.robot.move_linear.call_args_list], [0, 7, 0])

    def test_empty_draft_does_not_move(self):
        self.assertFalse(self.service.execute_sequence(10, [], self.cancelled)[0])
        self.robot.move_linear.assert_not_called()

    def test_stop_requests_robot_stop(self):
        self.assertTrue(self.service.stop_sequence_motion()[0])
        self.robot.stop_motion.assert_called_once()
