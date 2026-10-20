import unittest
from unittest.mock import MagicMock

from src.engine.robot.calibration.robot_tool_registry_client import RobotToolRegistryClient
from src.engine.robot.tool_activation_service import ToolActivationService
from src.engine.robot.configuration.tool_changer_settings import ToolChangerSettingsSerializer, ToolChangerSettings
from src.engine.robot.interfaces.tool_definition import ToolDefinition


class BackendConfigurationTests(unittest.TestCase):
    def test_adapter_uses_configured_robot_and_revision(self):
        robot = MagicMock()
        robot.get_backend_configuration.return_value = {'revision': 'abc'}
        robot.update_backend_configuration.return_value = {'success': True, 'pending_application': False}
        client = RobotToolRegistryClient(robot)
        self.assertTrue(client.update_tool(2, None, [1]*6, persist=True)[0])
        robot.update_backend_configuration.assert_called_once_with(
            'calibration', {'transform': [1]*6}, 'abc', tool_id=2)

    def test_saved_but_not_applied_is_not_reported_as_ready(self):
        robot = MagicMock()
        robot.update_backend_configuration.return_value = {'pending_application': True, 'application_error': 'Saved; busy'}
        self.assertEqual(RobotToolRegistryClient(robot).update_definition(2, {}, 'abc'), (False, 'Saved; busy'))

    def test_missing_backend_definition_does_not_activate_or_upload(self):
        registry = MagicMock()
        registry.get_tool_registry.return_value = {'tool_id_map': {}, 'tool_registry': {}}
        robot = MagicMock()
        self.assertFalse(ToolActivationService(registry, robot).activate(tool_id=2)[0])
        robot.set_active_tool.assert_not_called()
        registry.update_tool.assert_not_called()

    def test_platform_serializer_stores_metadata_not_operational_geometry(self):
        serializer = ToolChangerSettingsSerializer()
        settings = ToolChangerSettings(tools=[ToolDefinition(2, 'Vacuum', relative_transform=[99]*6)])
        payload = serializer.to_dict(settings)
        self.assertEqual(payload['tools'], [{'id': 2, 'name': 'Vacuum'}])
        self.assertNotIn('reference_tool_id', payload)


class CollisionConfigurationRevisionTests(unittest.TestCase):
    def test_collision_editor_keeps_loaded_revision_for_save(self):
        from src.engine.robot.drivers.client_adapters.http_websocket import HttpWebSocketRobotClient
        client = HttpWebSocketRobotClient.__new__(HttpWebSocketRobotClient)
        client.get_backend_configuration = MagicMock(return_value={
            'success': True, 'revision': 'loaded', 'saved': {'monitor': {'diagnostics_enabled': True}}})
        client.update_backend_configuration = MagicMock(return_value={
            'success': True, 'revision': 'updated', 'pending_application': False,
            'saved': {'monitor': {'diagnostics_enabled': False}}})
        self.assertTrue(client.get_collision_monitor_config()['success'])
        self.assertTrue(client.update_collision_monitor_config({'diagnostics_enabled': False})['success'])
        client.update_backend_configuration.assert_called_once_with(
            'sensorless_collision', {'monitor': {'diagnostics_enabled': False}}, 'loaded')

    def test_collision_save_without_load_is_rejected(self):
        from src.engine.robot.drivers.client_adapters.http_websocket import HttpWebSocketRobotClient
        client = HttpWebSocketRobotClient.__new__(HttpWebSocketRobotClient)
        self.assertFalse(client.update_collision_monitor_config({})['success'])
