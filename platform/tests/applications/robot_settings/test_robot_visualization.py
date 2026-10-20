import unittest
from unittest.mock import MagicMock

from PyQt6 import sip
from PyQt6.QtWidgets import QApplication

from src.applications.robot_settings.controller.robot_settings_controller import RobotSettingsController
from src.applications.robot_settings.model.robot_settings_model import RobotSettingsModel
from src.applications.robot_settings.view.robot_settings_view import RobotSettingsView
from src.applications.robot_settings.view.robot_visualization_tab import RobotVisualizationTab
from src.engine.robot.drivers.client_adapters import HttpWebSocketRobotClient
from src.engine.robot.drivers.ros2_robot import Ros2Robot
from src.engine.robot.services.motion_service import MotionService
from src.engine.robot.services.robot_service import RobotService


class RobotVisualizationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def test_buttons_follow_confirmed_state_and_disable_during_requests(self):
        tab = RobotVisualizationTab()
        requests = []
        tab.rviz_enabled_requested.connect(requests.append)
        self.assertFalse(tab._start.isEnabled())
        self.assertFalse(tab._stop.isEnabled())
        tab.set_state(False)
        tab._start.click()
        self.assertEqual(requests, [True])
        tab.set_busy(True)
        self.assertFalse(tab._start.isEnabled())
        self.assertFalse(tab._refresh.isEnabled())
        tab.set_state(True)
        self.assertFalse(tab._start.isEnabled())
        tab._stop.click()
        self.assertEqual(requests, [True, False])
        tab.set_state(False, 'failed to start')
        self.assertTrue(tab._start.isEnabled())
        self.assertIn('failed to start', tab._status.text())
        sip.delete(tab)

    def test_lazy_tab_preserves_existing_indices_and_polls_only_while_visible(self):
        for collision in (False, True):
            view = RobotSettingsView(show_sensorless_collision_tab=collision)
            self.assertIsNone(view._visualization_tab)
            view.show()
            view._settings_view._tabs.setCurrentIndex(view._visualization_tab_index)
            self.app.processEvents()
            tab = view._visualization_tab
            self.assertIsInstance(tab, RobotVisualizationTab)
            self.assertIsNone(view._collision_tab)
            self.assertTrue(tab._timer.isActive())
            view._settings_view._tabs.setCurrentIndex(0)
            self.app.processEvents()
            self.assertFalse(tab._timer.isActive())
            sip.delete(view)

    def test_controller_serializes_requests_and_ignores_late_results_after_stop(self):
        model = MagicMock(spec=RobotSettingsModel)
        view = MagicMock(spec=RobotSettingsView)
        controller = RobotSettingsController(model, view, None)
        controller._run_in_thread = MagicMock()
        controller._on_rviz_refresh()
        controller._on_rviz_enabled(True)
        self.assertEqual(controller._run_in_thread.call_count, 1)
        model.get_rviz_status.assert_not_called()
        controller._on_rviz_result({'success': True, 'running': False})
        view.set_rviz_state.assert_called_with(False, None)
        controller._on_rviz_enabled(True)
        fn = controller._run_in_thread.call_args.args[0]
        fn()
        model.set_rviz_enabled.assert_called_once_with(True)
        controller._on_rviz_result({'success': False, 'running': False, 'error': 'missing display'})
        view.set_rviz_state.assert_called_with(False, 'missing display')
        controller.stop()
        view.set_rviz_state.reset_mock()
        controller._on_rviz_result({'success': True, 'running': True})
        view.set_rviz_state.assert_not_called()

    def test_transport_status_start_stop_unsupported_and_malformed_responses(self):
        client = object.__new__(HttpWebSocketRobotClient)
        client.server_url = 'http://backend:5000'
        client._session = MagicMock()
        for response in (client._session.get.return_value, client._session.post.return_value):
            response.status_code = 200
            response.json.return_value = {'success': True, 'running': True}
        self.assertTrue(client.get_rviz_status()['running'])
        client._session.get.assert_called_once_with('http://backend:5000/visualization/rviz', timeout=8)
        client.set_rviz_enabled(False)
        client._session.post.assert_called_once_with('http://backend:5000/visualization/rviz', json={'enabled': False}, timeout=8)
        client._session.get.return_value.status_code = 404
        self.assertEqual(client.get_rviz_status()['error'], 'rviz_control_unsupported')
        client._session.get.return_value.status_code = 200
        client._session.get.return_value.json.return_value = []
        self.assertFalse(client.get_rviz_status()['success'])
        with self.assertRaises(ValueError):
            client.set_rviz_enabled('false')

    def test_engine_layers_forward_rviz_without_motion_commands(self):
        for cls, attribute in ((RobotService, '_motion'), (MotionService, '_robot'), (Ros2Robot, '_client')):
            service = object.__new__(cls)
            delegate = MagicMock()
            setattr(service, attribute, delegate)
            delegate.get_rviz_status.return_value = {'success': True, 'running': False}
            delegate.set_rviz_enabled.return_value = {'success': True, 'running': True}
            self.assertFalse(service.get_rviz_status()['running'])
            self.assertTrue(service.set_rviz_enabled(True)['running'])
            self.assertEqual([call[0] for call in delegate.method_calls], ['get_rviz_status', 'set_rviz_enabled'])


if __name__ == '__main__':
    unittest.main()
