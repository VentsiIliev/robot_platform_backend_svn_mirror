"""Exercise the operator's sequence with real Qt signals and temporary history."""
import json
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import MagicMock

from PyQt6.QtWidgets import QApplication

from pl_gui.shell.AppShell import AppShell
from pl_gui.shell.base_app_widget.AppWidget import AppWidget
from src.bootstrap.application_loader import _ApplicationManager, _WidgetFactory
from src.bootstrap.navigation_diagnostics import NavigationDiagnostics
from src.bootstrap.shell_session_controller import ShellSessionController
from src.applications.robot_settings.controller.robot_settings_controller import RobotSettingsController
from src.applications.robot_settings.model.robot_settings_model import RobotSettingsModel
from src.applications.robot_settings.service.robot_settings_application_service import RobotSettingsApplicationService
from src.applications.robot_settings.view.robot_settings_view import RobotSettingsView
from src.engine.auth.user_session import UserSession
from src.engine.diagnostics.actions import ActionRecorder
from src.engine.diagnostics.runtime import DiagnosticsRuntime
from src.shared_contracts.declarations.system_specs import ApplicationSpec


class NavigationDiagnosticsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def setUp(self):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.directory = Path(directory.name)
        self.runtime = DiagnosticsRuntime(self.directory)
        self.assertTrue(self.runtime.start())
        self.addCleanup(self.runtime.close)
        self.session = UserSession()
        self.session.login(SimpleNamespace(user_id='42', role='engineer'))
        self.actions = ActionRecorder(self.session, authentication_mode='authenticated')
        self.actions.session_changed(True)

    def shell(self, factory):
        shell = AppShell([], factory)
        self.addCleanup(shell.deleteLater)
        adapter = NavigationDiagnostics(shell, self.actions)
        adapter.start()
        self.addCleanup(adapter.stop)
        return shell

    def records(self):
        self.runtime.close()
        return [json.loads(line) for line in (self.directory / 'events.jsonl').read_text().splitlines()]

    def test_dashboard_menu_settings_toggle_save_dashboard_sequence(self):
        robot = MagicMock()
        robot.get_collision_monitor_config.return_value = {
            'success': True, 'config': {'active_stop_enabled': True}}
        robot.update_collision_monitor_config.return_value = {
            'success': True, 'saved': {'monitor': {'active_stop_enabled': False}},
            'applied': {'monitor': {'active_stop_enabled': False}},
            'pending_application': False, 'revision': 'revision-2',
            'config': {'active_stop_enabled': False}}
        service = RobotSettingsApplicationService(MagicMock(), 'config', 'groups', 'calibration',
            robot_service=robot, diagnostic_actions=self.actions)
        view = RobotSettingsView(show_sensorless_collision_tab=True)
        controller = RobotSettingsController(RobotSettingsModel(service), view, None)
        self.addCleanup(controller.stop)
        # Keep this UI wiring test deterministic; worker-context survival is tested separately.
        def run_inline(fn, on_done, on_error=None):
            on_done(fn())
        controller._run_in_thread = run_inline
        def factory(name):
            return view if name == 'RobotSettings' else AppWidget(name)
        shell = self.shell(factory)
        shell.show_app('Dashboard')
        shell.close_current_app()
        shell.show_app('RobotSettings')
        view._settings_view._tabs.setCurrentIndex(4)
        view._collision_tab._active_stop.click()
        view._collision_tab._emit_save()
        shell.close_current_app()
        shell.show_app('Dashboard')
        events = [record for record in self.records() if record.get('event')]
        completed_nav = [record for record in events if record['event'].startswith('navigation.')
                         and record['fields']['outcome'] != 'started']
        self.assertEqual([(record['event'], record['fields'].get('application')) for record in completed_nav], [
            ('navigation.application', 'Dashboard'), ('navigation.main_menu', None),
            ('navigation.application', 'RobotSettings'), ('navigation.settings_tab', None),
            ('navigation.main_menu', None), ('navigation.application', 'Dashboard')])
        edits = [record for record in events if record['event'] == 'settings.collision.edited']
        self.assertEqual(len(edits), 1)  # Loading/confirmation must not invent user edits.
        self.assertEqual(edits[0]['fields']['before'], True)
        self.assertEqual(edits[0]['fields']['after'], False)
        self.assertFalse(edits[0]['fields']['persisted'])
        saves = [record for record in events if record['event'].startswith('settings.collision.')
                 and record['event'] != 'settings.collision.edited']
        self.assertEqual(len(saves), 4)
        self.assertEqual(len({record['context']['action_id'] for record in saves}), 1)
        self.assertEqual(saves[-1]['fields']['application'], 'reported_applied')
        self.assertTrue(all(record['context']['actor']['user_id'] == '42' for record in events))

    def test_displayed_fallback_is_failed_and_points_to_original_exception(self):
        manager = _ApplicationManager()
        manager.register_lazy(ApplicationSpec(name='Broken', folder_id=1, icon=''),
                              MagicMock(side_effect=RuntimeError('broken factory')))
        factory = _WidgetFactory(manager, MagicMock())
        shell = self.shell(factory.create_widget)
        widget = shell.show_app('Broken')
        records = self.records()
        result = [record for record in records if record.get('event') == 'navigation.application'][-1]
        self.assertEqual(result['fields']['outcome'], 'failed')
        self.assertTrue(result['fields']['displayed'])
        error_id = result['fields']['load_result']['error_id']
        original = next(record for record in records if record['context'].get('error_id') == error_id)
        self.assertIn('broken factory', original['traceback'])
        self.assertTrue(widget._application_load_result['fallback'])

    def test_close_and_folder_selection_vetoes_are_rejected(self):
        widget = AppWidget('Busy')
        widget.can_close = MagicMock(return_value=False)
        shell = self.shell(lambda name: widget)
        shell.show_app('Busy')
        shell.close_current_app()
        shell.on_app_selected('Other')
        events = [record for record in self.records() if record.get('event')]
        self.assertEqual(events[-1]['fields']['outcome'], 'rejected')
        self.assertEqual(events[-3]['fields']['outcome'], 'rejected')
        self.assertIn('Busy', shell.running_widgets)

    def test_login_and_logout_capture_actor_including_close_veto(self):
        shell = self.shell(lambda name: AppWidget(name))
        can_close = MagicMock(return_value=False)
        controller = ShellSessionController(shell=shell, session=self.session, dev_skip_login=False,
            show_account_button_when_dev_skip_login=False, show_login_view=MagicMock(),
            can_close_running_apps=can_close, can_expire_session=lambda: True, actions=self.actions)
        controller.login(SimpleNamespace(user_id='7', role='operator'))
        controller._on_logout_requested()
        self.assertTrue(self.session.is_authenticated())
        can_close.return_value = True
        controller._on_logout_requested()
        self.assertFalse(self.session.is_authenticated())
        events = [record for record in self.records() if record.get('event') in ('user.login', 'user.logout')]
        self.assertEqual([record['fields']['outcome'] for record in events], ['succeeded', 'rejected', 'succeeded'])
        self.assertTrue(all(record['context']['actor']['user_id'] == '7' for record in events))

    def test_adapter_stop_disconnects_signal(self):
        shell = AppShell([], lambda name: AppWidget(name))
        self.addCleanup(shell.deleteLater)
        adapter = NavigationDiagnostics(shell, self.actions)
        adapter.start()
        adapter.stop()
        shell.show_app('Dashboard')
        self.assertFalse(any(record.get('event') == 'navigation.application' for record in self.records()))

    def test_actor_snapshot_survives_logout_before_worker_completion(self):
        token = self.actions.record('settings.collision.save_requested', outcome='started')
        self.session.logout()
        self.actions.session_changed(False)
        self.actions.record('settings.collision.save_result', context=token)
        events = [record for record in self.records() if record.get('event')]
        self.assertEqual(events[0]['context'], events[1]['context'])
        self.assertEqual(events[1]['context']['actor']['user_id'], '42')
        self.assertIsNotNone(events[1]['context']['actor']['auth_session_id'])
