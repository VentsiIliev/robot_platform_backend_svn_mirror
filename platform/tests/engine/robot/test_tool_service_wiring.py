"""Verify the live settings builder and application share one tool executor."""
import unittest
from threading import Event
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from src.engine.common_service_ids import CommonServiceID
from src.engine.common_settings_ids import CommonSettingsID
from src.engine.robot.configuration import ToolChangerSettings
from src.engine.robot.interfaces.tool_definition import ToolDefinition
from src.engine.robot.tool_changer import SlotConfig, ToolChangeStep
from src.engine.robot.tool_manager import ToolManager
from src.robot_systems.default_service_builders import build_tool_service


class ToolServiceWiringTests(unittest.TestCase):
    def test_builder_reads_replaced_settings_before_execution(self):
        robot = MagicMock()
        robot.is_healthy.return_value = True
        robot.get_state.return_value = 'idle'
        robot.get_current_velocity.return_value = 0.0
        motion = MagicMock()
        motion.move_linear.return_value = True
        values = {
            CommonSettingsID.TOOL_CHANGER_CONFIG: ToolChangerSettings(),
            CommonSettingsID.ROBOT_CONFIG: SimpleNamespace(robot_tool=0, robot_user=1),
            CommonSettingsID.MOVEMENT_GROUPS: SimpleNamespace(movement_groups={}),
        }
        settings = MagicMock()
        settings.get.side_effect = values.__getitem__
        manager = build_tool_service(SimpleNamespace(
            settings=settings, motion=motion, system_class=SimpleNamespace(tool_slots=[]),
            services={CommonServiceID.ROBOT: robot}))
        self.assertIsInstance(manager, ToolManager)
        slot = SlotConfig(10, 7, pickup_sequence=[ToolChangeStep(kind='attach')],
                          dropoff_sequence=[ToolChangeStep(kind='detach')])
        values[CommonSettingsID.TOOL_CHANGER_CONFIG] = ToolChangerSettings(
            tools=[ToolDefinition(7, 'New')], slots=[slot])
        values[CommonSettingsID.ROBOT_CONFIG] = SimpleNamespace(robot_tool=0, robot_user=4)
        self.assertTrue(manager.execute_sequence(10, [{'pose': [5] * 6}], Event())[0])
        self.assertEqual(motion.move_linear.call_args.kwargs['user'], 4)
        self.assertTrue(manager.pickup_tool(7)[0])
        self.assertTrue(manager.drop_off_tool(7)[0])
        self.assertFalse(slot.occupied, 'Manager must not mutate settings occupancy')
        self.assertTrue(manager._tool_changer.is_slot_occupied(10))

    def test_paint_app_receives_registered_tool_service(self):
        from src.robot_systems.paint.application_wiring import _build_tool_settings_application
        system = MagicMock()
        robot, manager = MagicMock(), MagicMock()
        system.get_optional_service.side_effect = {
            CommonServiceID.ROBOT: robot, CommonServiceID.TOOLS: manager,
        }.__getitem__
        with patch('src.applications.tool_settings.ToolSettingsApplicationService') as service, \
             patch('src.applications.base.robot_jog_service_builder.build_robot_system_jog_service'):
            _build_tool_settings_application(system)
        self.assertIs(service.call_args.kwargs['tool_service'], manager)
        self.assertIs(service.call_args.kwargs['robot_service'], robot)

    def test_paint_declares_staging_group_and_builder_enforces_it(self):
        from src.robot_systems.paint.paint_robot_system import PaintRobotSystem
        from src.engine.robot.configuration.robot_settings import MovementGroup
        self.assertEqual(PaintRobotSystem.tool_change_group, "Tool Changer")
        robot = MagicMock()
        robot.is_healthy.return_value = True
        robot.get_state.return_value = "idle"
        robot.get_current_velocity.return_value = 0.0
        robot.get_current_position_fresh.return_value = [99] * 6
        motion = MagicMock()
        motion.move_linear.return_value = True
        values = {
            CommonSettingsID.TOOL_CHANGER_CONFIG: ToolChangerSettings(
                tools=[ToolDefinition(7, "Vacuum")],
                slots=[SlotConfig(2, 7, pickup_sequence=[ToolChangeStep(pose=[1] * 6)])]),
            CommonSettingsID.ROBOT_CONFIG: SimpleNamespace(robot_tool=0, robot_user=0),
            CommonSettingsID.MOVEMENT_GROUPS: SimpleNamespace(movement_groups={
                "Tool Changer": MovementGroup(position="[0, 0, 0, 0, 0, 0]")}),
        }
        settings = MagicMock()
        settings.get.side_effect = values.__getitem__
        manager = build_tool_service(SimpleNamespace(
            settings=settings, motion=motion, system_class=PaintRobotSystem,
            services={CommonServiceID.ROBOT: robot}))
        self.assertFalse(manager.pickup_tool(7)[0])
        self.assertFalse(manager.execute_sequence(2, [{"pose": [1] * 6}])[0])
        motion.move_linear.assert_not_called()
        robot.get_current_position_fresh.return_value = [0] * 6
        self.assertTrue(manager.pickup_tool(7)[0])

    def test_builder_routes_endpoint_moves_through_registered_navigation(self):
        from src.engine.robot.configuration.robot_settings import MovementGroup
        robot, navigation, motion = MagicMock(), MagicMock(), MagicMock()
        robot.is_healthy.return_value = True
        robot.get_state.return_value = 'idle'
        robot.get_current_velocity.return_value = 0.0
        robot.get_current_position_fresh.return_value = [0] * 6
        values = {
            CommonSettingsID.TOOL_CHANGER_CONFIG: ToolChangerSettings(
                tools=[ToolDefinition(7, 'Tool')], slots=[SlotConfig(2, 7)]),
            CommonSettingsID.ROBOT_CONFIG: SimpleNamespace(robot_tool=0, robot_user=4),
            CommonSettingsID.MOVEMENT_GROUPS: SimpleNamespace(movement_groups={
                'Tool Changer': MovementGroup(position='[0, 0, 0, 0, 0, 0]', velocity=10,
                                              acceleration=10, motion_type='fast_lin')}),
        }
        settings = MagicMock()
        settings.get.side_effect = values.__getitem__
        manager = build_tool_service(SimpleNamespace(
            settings=settings, motion=motion,
            system_class=SimpleNamespace(tool_slots=[], tool_change_group='Tool Changer'),
            services={CommonServiceID.ROBOT: robot, CommonServiceID.NAVIGATION: navigation}))
        cancelled = Event()
        result = manager.execute_sequence(2, [{'kind': 'start_at_tool_changer'}, {'kind': 'wait'}], cancelled)
        self.assertTrue(result.success, result.message)
        navigation.move_to_group.assert_called_once()
        self.assertEqual(navigation.move_to_group.call_args.args, ('Tool Changer',))
        kwargs = navigation.move_to_group.call_args.kwargs
        self.assertEqual((kwargs['tool'], kwargs['user']), (0, 4))
        self.assertFalse(kwargs['wait_cancelled']())
        cancelled.set()
        self.assertTrue(kwargs['wait_cancelled']())
        motion.move_ptp.assert_not_called()
        motion.move_linear.assert_not_called()
