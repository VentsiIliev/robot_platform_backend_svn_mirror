import importlib.util
from pathlib import Path
import signal
import subprocess
import unittest
from concurrent.futures import ThreadPoolExecutor
from unittest.mock import MagicMock, patch

path = Path(__file__).resolve().parents[1] / 'scripts/runtime_gateway/adapters/rviz_process.py'
spec = importlib.util.spec_from_file_location('rviz_process_under_test', path)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class RvizProcessTests(unittest.TestCase):
    def process(self):
        process = MagicMock(pid=4321, returncode=None)
        process.poll.return_value = None
        process.wait.side_effect = subprocess.TimeoutExpired('rviz', 0.2)
        return process

    def test_parallel_start_requests_share_one_process_and_stop_only_its_group(self):
        process = self.process()
        builder = MagicMock(return_value=['ros2', 'launch', 'zeroerr', 'moveit_rviz.launch.py'])
        manager = module.RvizProcessManager(command_builder=builder)
        with patch.dict(module.os.environ, {'DISPLAY': ':1'}), patch.object(module.subprocess, 'Popen', return_value=process) as spawn, patch.object(module.os, 'killpg') as kill:
            with ThreadPoolExecutor(max_workers=4) as pool:
                results = list(pool.map(manager.set_enabled, [True] * 4))
            self.assertTrue(all(result['running'] for result in results))
            spawn.assert_called_once()
            builder.assert_called_once()
            self.assertTrue(spawn.call_args.kwargs['start_new_session'])
            process.wait.side_effect = None
            process.wait.return_value = 0
            self.assertFalse(manager.set_enabled(False)['running'])
            kill.assert_called_once_with(4321, signal.SIGINT)
            manager.close()
            kill.assert_called_once()

    def test_manual_window_close_updates_status_and_allows_restart(self):
        process = self.process()
        states = []
        manager = module.RvizProcessManager(on_state_changed=states.append, command_builder=lambda: ['rviz'])
        with patch.dict(module.os.environ, {'DISPLAY': ':1'}), patch.object(module.subprocess, 'Popen', return_value=process) as spawn:
            manager.set_enabled(True)
            process.poll.return_value = 0
            process.returncode = 0
            self.assertEqual(manager.status(), {'success': True, 'running': False})
            self.assertFalse(states[-1])
            replacement = self.process()
            spawn.return_value = replacement
            manager.set_enabled(True)
            self.assertEqual(spawn.call_count, 2)
            replacement.poll.return_value = 0
            replacement.returncode = 0
            manager.close()

    def test_missing_display_and_invalid_boolean_do_not_spawn(self):
        manager = module.RvizProcessManager(command_builder=lambda: ['rviz'])
        with patch.dict(module.os.environ, {}, clear=True), patch.object(module.subprocess, 'Popen') as spawn:
            result = manager.set_enabled(True)
            self.assertFalse(result['success'])
            self.assertFalse(result['running'])
            self.assertIn('graphical display', result['error'])
            self.assertFalse(manager.set_enabled('false')['success'])
            spawn.assert_not_called()

    def test_early_launch_failure_returns_log_and_can_be_retried(self):
        failed = MagicMock(pid=4321, returncode=2)
        failed.poll.return_value = 2
        failed.wait.return_value = 2
        manager = module.RvizProcessManager(command_builder=lambda: ['rviz'])
        def spawn(*args, **kwargs):
            kwargs['stdout'].write(b'robot description could not be loaded')
            return failed
        with patch.dict(module.os.environ, {'DISPLAY': ':1'}), patch.object(module.subprocess, 'Popen', side_effect=spawn):
            result = manager.set_enabled(True)
            self.assertFalse(result['success'])
            self.assertFalse(result['running'])
            self.assertIn('robot description', result['error'])
            self.assertTrue(manager.status()['success'])
            manager.close()

    def test_stop_escalates_within_owned_group_when_launch_will_not_exit(self):
        process = self.process()
        manager = module.RvizProcessManager(command_builder=lambda: ['rviz'])
        with patch.dict(module.os.environ, {'DISPLAY': ':1'}), patch.object(module.subprocess, 'Popen', return_value=process), patch.object(module.os, 'killpg') as kill:
            manager.set_enabled(True)
            process.wait.side_effect = [subprocess.TimeoutExpired('rviz', 3), subprocess.TimeoutExpired('rviz', 1), 0]
            self.assertTrue(manager.close()['success'])
            self.assertEqual([call.args for call in kill.call_args_list], [(4321, signal.SIGINT), (4321, signal.SIGTERM), (4321, signal.SIGKILL)])


class RvizRouteTests(unittest.TestCase):
    def setUp(self):
        # Exercise the real HTTP -> ControlApi -> gateway adapter path without starting a process.
        from flask import Flask
        from runtime_api.control.api import ControlApi
        from runtime_gateway.base import RuntimeGateway
        from runtime_gateway.adapters.diagnostics import RuntimeDiagnostics
        from rest.routes.control import control_blueprint
        from rest.routes.common import install_http_contract
        app = Flask(__name__)
        install_http_contract(app)
        self.manager = MagicMock()
        self.manager.status.return_value = {'success': True, 'running': False}
        self.manager.set_enabled.return_value = {'success': True, 'running': True}
        self.env = {'node': object()}
        diagnostics = RuntimeDiagnostics(lambda: self.env['node'], MagicMock(), self.manager)
        gateway = MagicMock(spec=RuntimeGateway)
        gateway.rviz_status.side_effect = diagnostics.rviz_status
        gateway.set_rviz_enabled.side_effect = diagnostics.set_rviz_enabled
        app.register_blueprint(control_blueprint(ControlApi(gateway)))
        self.client = app.test_client()

    def test_status_start_stop_and_strict_boolean_validation(self):
        self.assertFalse(self.client.get('/visualization/rviz').json['running'])
        self.assertEqual(self.client.post('/visualization/rviz', json={'enabled': True}).status_code, 200)
        self.manager.set_enabled.assert_called_with(True)
        self.client.post('/visualization/rviz', json={'enabled': False})
        self.manager.set_enabled.assert_called_with(False)
        calls = self.manager.set_enabled.call_count
        for bad in ({'enabled': 'false'}, {'enabled': 0}, []):
            self.assertEqual(self.client.post('/visualization/rviz', json=bad).status_code, 400)
        self.assertEqual(self.client.post('/visualization/rviz', data='null', content_type='application/json').status_code, 400)
        self.assertEqual(self.client.post('/visualization/rviz').status_code, 415)
        self.assertEqual(self.manager.set_enabled.call_count, calls)

    def test_initializing_backend_cannot_launch_and_start_failure_is_reported(self):
        self.env['node'] = None
        self.assertEqual(self.client.post('/visualization/rviz', json={'enabled': True}).status_code, 503)
        self.manager.set_enabled.assert_not_called()
        self.env['node'] = object()
        self.manager.set_enabled.return_value = {'success': False, 'running': False, 'error': 'missing display'}
        result = self.client.post('/visualization/rviz', json={'enabled': True})
        self.assertEqual(result.status_code, 503)
        self.assertFalse(result.json['running'])


if __name__ == '__main__':
    unittest.main()
