import unittest
from types import SimpleNamespace
from unittest.mock import MagicMock

from src.applications.robot_settings.service.robot_settings_application_service import RobotSettingsApplicationService
from src.engine.common_settings_ids import CommonSettingsID


def _make_svc(robot=None, nav=None, tool_key=None, tool_settings=None, actions=None):
    ss = MagicMock()
    if tool_key and tool_settings is not None:
        ss.get.side_effect = lambda k: tool_settings if k == tool_key else None
    return RobotSettingsApplicationService(
        ss,
        config_key=CommonSettingsID.ROBOT_CONFIG,
        movement_groups_key=CommonSettingsID.MOVEMENT_GROUPS,
        calibration_key=CommonSettingsID.ROBOT_CALIBRATION,
        robot_service=robot,
        tool_settings_key=tool_key,
        navigation_service=nav,
        diagnostic_actions=actions,
    )


class TestGetCurrentPosition(unittest.TestCase):

    def test_returns_none_when_no_robot(self):
        self.assertIsNone(_make_svc().get_current_position())

    def test_area_tcp_mode_change_preserves_newer_global_calibration(self):
        settings = MagicMock()
        config = SimpleNamespace(
            camera_to_tcp_mode="global", camera_to_tcp_by_area={},
            camera_to_tcp_x_offset=42.0, camera_to_tcp_y_offset=43.0,
        )
        settings.get.return_value = config
        service = RobotSettingsApplicationService(
            settings,
            config_key=CommonSettingsID.ROBOT_CONFIG,
            movement_groups_key=CommonSettingsID.MOVEMENT_GROUPS,
            calibration_key=CommonSettingsID.ROBOT_CALIBRATION,
            save_targeting_definitions_fn=lambda data: None,
        )
        service.save_targeting_definitions({
            "camera_to_tcp_changed": True,
            "camera_to_tcp_mode": "per_area",
            "camera_to_tcp_global": {"x_mm": 1.0, "y_mm": 2.0},
            "camera_to_tcp_by_area": {"paint": {"x_mm": 10.0, "y_mm": 11.0}},
        })
        self.assertEqual((config.camera_to_tcp_x_offset, config.camera_to_tcp_y_offset), (42.0, 43.0))
        self.assertEqual(config.camera_to_tcp_by_area["paint"]["x_mm"], 10.0)

    def test_delegates_to_robot(self):
        robot = MagicMock()
        robot.get_current_position.return_value = [1.0, 2.0, 3.0, 4.0, 5.0, 6.0]
        self.assertEqual(_make_svc(robot=robot).get_current_position(), [1.0, 2.0, 3.0, 4.0, 5.0, 6.0])

    def test_returns_none_on_robot_exception(self):
        robot = MagicMock()
        robot.get_current_position.side_effect = RuntimeError("disconnected")
        self.assertIsNone(_make_svc(robot=robot).get_current_position())


class TestCollisionMonitorConfiguration(unittest.TestCase):

    def test_pending_application_retains_separate_save_and_runtime_evidence(self):
        robot = MagicMock()
        response = {'success': False, 'saved': {'monitor': {'active_stop_enabled': False}},
                    'applied': {'monitor': {'active_stop_enabled': True}},
                    'revision': 'revision-2', 'pending_application': True}
        robot.update_collision_monitor_config.return_value = response
        actions = MagicMock()
        token = {'action_id': 'action-1', 'actor': {'user_id': '42'}}

        self.assertIs(_make_svc(robot=robot, actions=actions).save_collision_monitor_config(
            {'active_stop_enabled': False}, token), response)

        calls = actions.record.call_args_list
        self.assertEqual([call.args[0] for call in calls], [
            'settings.collision.persistence_reported',
            'settings.collision.application_reported', 'settings.collision.save_result'])
        self.assertEqual(calls[0].kwargs['configuration'], response['saved'])
        self.assertEqual(calls[1].kwargs['configuration'], response['applied'])
        self.assertEqual(calls[2].kwargs['persistence'], 'reported_saved')
        self.assertEqual(calls[2].kwargs['application'], 'pending')
        self.assertTrue(all(call.kwargs['context'] == token for call in calls))

    def test_broken_audit_adapter_does_not_change_save_result_or_exception(self):
        robot, actions = MagicMock(), MagicMock()
        actions.record.side_effect = RuntimeError('recorder adapter failed')
        response = {'success': True, 'saved': {'active_stop_enabled': False}}
        robot.update_collision_monitor_config.return_value = response
        service = _make_svc(robot=robot, actions=actions)
        self.assertIs(service.save_collision_monitor_config({'active_stop_enabled': False}), response)
        original = OSError('device connection failed')
        robot.update_collision_monitor_config.side_effect = original
        with self.assertRaises(OSError) as caught:
            service.save_collision_monitor_config({'active_stop_enabled': False})
        self.assertIs(caught.exception, original)

    def test_legacy_success_does_not_establish_persistence_or_application(self):
        robot, actions = MagicMock(), MagicMock()
        robot.update_collision_monitor_config.return_value = {'success': True, 'applied': False}
        _make_svc(robot=robot, actions=actions).save_collision_monitor_config(
            {'active_stop_enabled': False}, {'action_id': 'action-1'})
        result = actions.record.call_args.kwargs
        self.assertEqual(result['outcome'], 'succeeded')
        self.assertEqual(result['persistence'], 'unknown')
        self.assertEqual(result['application'], 'unknown')

    def test_load_delegates_to_robot(self):
        robot = MagicMock()
        robot.get_collision_monitor_config.return_value = {
            "success": True, "config": {"detection_enabled": True}}

        result = _make_svc(robot=robot).load_collision_monitor_config()

        self.assertTrue(result["success"])
        robot.get_collision_monitor_config.assert_called_once_with()

    def test_save_delegates_to_robot(self):
        robot = MagicMock()
        robot.update_collision_monitor_config.return_value = {"success": True}
        payload = {"collision_sensitivity_percent": 125.0}

        result = _make_svc(robot=robot).save_collision_monitor_config(payload)

        self.assertTrue(result["success"])
        robot.update_collision_monitor_config.assert_called_once_with(payload)

    def test_reports_unavailable_without_robot(self):
        self.assertFalse(_make_svc().load_collision_monitor_config()["success"])

    def test_open_diagnostics_delegates_to_robot(self):
        robot = MagicMock()
        robot.open_collision_monitor_diagnostics.return_value = {"success": True}

        result = _make_svc(robot=robot).open_collision_monitor_diagnostics()

        self.assertTrue(result["success"])
        robot.open_collision_monitor_diagnostics.assert_called_once_with()


class TestGetSlotInfo(unittest.TestCase):

    def test_returns_empty_when_no_tool_settings_key(self):
        self.assertEqual(_make_svc().get_slot_info(), [])

    def test_returns_empty_when_settings_returns_none(self):
        ss = MagicMock()
        ss.get.return_value = None
        svc = RobotSettingsApplicationService(
            ss,
            config_key=CommonSettingsID.ROBOT_CONFIG,
            movement_groups_key=CommonSettingsID.MOVEMENT_GROUPS,
            calibration_key=CommonSettingsID.ROBOT_CALIBRATION,
            tool_settings_key="tool_key",
        )
        self.assertEqual(svc.get_slot_info(), [])

    def test_returns_slot_with_assigned_tool_name(self):
        slot = MagicMock(); slot.id = 10; slot.tool_id = 1
        tool = MagicMock(); tool.id = 1;  tool.name = "Gripper"
        tc   = MagicMock(); tc.slots = [slot]; tc.tools = [tool]
        result = _make_svc(tool_key="k", tool_settings=tc).get_slot_info()
        self.assertEqual(result, [(10, "Gripper")])

    def test_returns_none_tool_name_for_unassigned_slot(self):
        slot = MagicMock(); slot.id = 5; slot.tool_id = None
        tc   = MagicMock(); tc.slots = [slot]; tc.tools = []
        result = _make_svc(tool_key="k", tool_settings=tc).get_slot_info()
        self.assertEqual(result, [(5, None)])

    def test_multiple_slots_mixed_assignment(self):
        s1 = MagicMock(); s1.id = 1; s1.tool_id = 2
        s2 = MagicMock(); s2.id = 2; s2.tool_id = None
        t  = MagicMock(); t.id = 2; t.name = "Drill"
        tc = MagicMock(); tc.slots = [s1, s2]; tc.tools = [t]
        result = _make_svc(tool_key="k", tool_settings=tc).get_slot_info()
        self.assertEqual(result, [(1, "Drill"), (2, None)])

    def test_returns_empty_on_exception(self):
        ss = MagicMock()
        ss.get.side_effect = RuntimeError("boom")
        svc = RobotSettingsApplicationService(
            ss,
            config_key=CommonSettingsID.ROBOT_CONFIG,
            movement_groups_key=CommonSettingsID.MOVEMENT_GROUPS,
            calibration_key=CommonSettingsID.ROBOT_CALIBRATION,
            tool_settings_key="tool_key",
        )
        self.assertEqual(svc.get_slot_info(), [])


class TestMoveToGroup(unittest.TestCase):

    def test_returns_false_without_navigation(self):
        ok, _ = _make_svc().move_to_group("HOME")
        self.assertFalse(ok)

    def test_delegates_to_navigation_and_returns_true(self):
        nav = MagicMock(); nav.move_to_group.return_value = True
        ok, _ = _make_svc(nav=nav).move_to_group("HOME")
        self.assertTrue(ok)
        nav.move_to_group.assert_called_once_with("HOME")

    def test_delegates_to_navigation_and_returns_false(self):
        nav = MagicMock(); nav.move_to_group.return_value = False
        ok, _ = _make_svc(nav=nav).move_to_group("HOME")
        self.assertFalse(ok)

    def test_returns_false_on_exception(self):
        nav = MagicMock(); nav.move_to_group.side_effect = RuntimeError("fail")
        ok, _ = _make_svc(nav=nav).move_to_group("HOME")
        self.assertFalse(ok)


class TestExecuteGroup(unittest.TestCase):

    def test_returns_false_without_navigation(self):
        ok, _ = _make_svc().execute_group("TRAJ")
        self.assertFalse(ok)

    def test_calls_move_linear_group_on_navigation(self):
        nav = MagicMock(); nav.move_linear_group.return_value = True
        ok, _ = _make_svc(nav=nav).execute_group("TRAJ")
        self.assertTrue(ok)
        nav.move_linear_group.assert_called_once_with("TRAJ")

    def test_returns_false_on_exception(self):
        nav = MagicMock(); nav.move_linear_group.side_effect = RuntimeError("fail")
        ok, _ = _make_svc(nav=nav).execute_group("TRAJ")
        self.assertFalse(ok)


class TestMoveToPoint(unittest.TestCase):

    def test_returns_false_without_navigation(self):
        ok, _ = _make_svc().move_to_point("HOME", "[0,0,0,0,0,0]")
        self.assertFalse(ok)

    def test_parses_and_delegates_six_values(self):
        nav = MagicMock(); nav.move_to_position.return_value = True
        ok, _ = _make_svc(nav=nav).move_to_point("HOME", "[1.0, 2.0, 3.0, 4.0, 5.0, 6.0]")
        self.assertTrue(ok)
        nav.move_to_position.assert_called_once_with([1.0, 2.0, 3.0, 4.0, 5.0, 6.0], "HOME")

    def test_returns_false_for_wrong_arg_count(self):
        nav = MagicMock()
        ok, _ = _make_svc(nav=nav).move_to_point("HOME", "[1.0, 2.0, 3.0]")
        self.assertFalse(ok)

    def test_returns_false_for_invalid_format(self):
        nav = MagicMock()
        ok, _ = _make_svc(nav=nav).move_to_point("HOME", "not_a_list")
        self.assertFalse(ok)

    def test_returns_false_on_navigation_exception(self):
        nav = MagicMock(); nav.move_to_position.side_effect = RuntimeError("fail")
        ok, _ = _make_svc(nav=nav).move_to_point("HOME", "[1.0, 2.0, 3.0, 4.0, 5.0, 6.0]")
        self.assertFalse(ok)


if __name__ == "__main__":
    unittest.main()
