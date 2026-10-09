"""Verify daemon IPC, offline activation and isolated user-service provisioning."""
import json
import os
from pathlib import Path
import subprocess
import sys
import time
import unittest
from unittest.mock import patch

from src.engine.updates.files import atomic_json, lock
from src.engine.updates.service import UpdateService, request
from src.engine.updates.service_install import install_service
from tests.engine.updates import test_robot_updates as fixtures
ROOT = fixtures.ROOT


class UpdateServiceTests(unittest.TestCase):
    def setUp(self):
        self.fixture = fixtures.RobotUpdateTests()
        self.fixture.setUp()
        self.addCleanup(self.fixture.doCleanups)
        self.fixture.install()
        self.fixture.feed_release()
        self.root = self.fixture.root
        self.config = self.root / 'updates.json'
        atomic_json(self.config, dict(install_root=str(self.root), repository_url=str(self.fixture.feed),
                                     product=self.fixture.config.product, enabled=True))

    def test_daemon_downloads_and_applies_only_after_gui_lock_is_released(self):
        process = subprocess.Popen([sys.executable, '-B', str(ROOT/'packaging/runtime/manage.py'),
                                    '--config', str(self.config), 'serve'],
                                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        def stop():
            if process.poll() is None:
                process.terminate()
            process.wait(timeout=10)
        self.addCleanup(stop)
        deadline = time.monotonic()+10
        while not (self.root/'update-state/service.sock').exists():
            self.assertIsNone(process.poll())
            self.assertLess(time.monotonic(), deadline)
            time.sleep(.05)
        self.assertEqual((self.root/'update-state/service.sock').stat().st_mode & 0o777, 0o600)
        self.assertTrue(request(self.config, 'check')['available'])
        self.assertEqual(request(self.config, 'download')['version'], '1.1.0')
        with lock(self.root/'runtime.lock', shared=True):
            request(self.config, 'queue')
            time.sleep(1.2)
            self.assertEqual(request(self.config, 'status')['installed'], '1.0.0')
        deadline = time.monotonic()+10
        while request(self.config, 'status')['installed'] != '1.1.0':
            self.assertLess(time.monotonic(),deadline)
            time.sleep(.1)
        self.assertEqual(self.fixture.updater.installed()['selection']['backend_version'], '2.0.0')
        self.assertEqual((self.root/'data/calibration.json').read_text(), '{\n  "offset": 12.5\n}')
        with self.assertRaisesRegex(RuntimeError, 'Unknown'):
            request(self.config, 'unknown')

    def test_ui_delegates_to_service_and_keeps_production_gate(self):
        from src.applications.software_update.service.software_update_service import SoftwareUpdateService
        atomic_json(self.root/'update-state/service.json', {'unit':'test.service'})
        service = SoftwareUpdateService(lambda: False)
        with patch('src.applications.software_update.service.software_update_service.default_config_path', return_value=self.config), patch('src.engine.updates.service.request', return_value={'available':True}) as ipc, patch.object(service,'_updater') as direct:
            self.assertTrue(service.check()['available'])
            ipc.assert_called_once_with(self.config,'check')
            direct.assert_not_called()
            with self.assertRaisesRegex(RuntimeError,'Stop the production'):
                service.schedule_installation()

    def test_provisioning_writes_user_unit_without_root_or_configuration_changes(self):
        before = self.config.read_bytes()
        with patch('pathlib.Path.home', return_value=self.fixture.directory), patch('src.engine.updates.service_install.subprocess.run') as run:
            install_service(self.root,self.config)
        unit = self.fixture.directory/'.config/systemd/user/robot-update-installed.service'
        content = unit.read_text()
        self.assertIn(' serve\n',content)
        self.assertNotIn('NoNewPrivileges=true',content)  # Narrow sudo helper must elevate.
        self.assertNotIn('sudo',content)
        self.assertEqual([call.args[0][:2] for call in run.call_args_list], [['systemctl','--user']]*3)
        self.assertEqual(self.config.read_bytes(),before)

    def test_service_refuses_activation_while_backend_platform_lock_held(self):
        service = UpdateService(self.config)
        service.dispatch('download')
        service.dispatch('queue')
        with lock(self.root/'runtime.lock',shared=True):
            with self.assertRaisesRegex(RuntimeError,'Platform is running'):
                service.apply_when_offline()
        self.assertEqual(self.fixture.updater.installed()['version'],'1.0.0')

    def test_launcher_waits_for_service_and_reopens_without_applying_itself(self):
        import importlib.util
        self.fixture.updater.stage_local(self.fixture.directory/'1.1.0.tar.gz')
        atomic_json(self.root/'update-state/service.json', {'unit':'test.service'})
        spec = importlib.util.spec_from_file_location('service_launcher', ROOT/'packaging/runtime/manage.py')
        manager = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(manager)
        daemon = UpdateService(self.config)
        log = self.fixture.directory/'service-launch.log'
        def service_request(path, operation, **kwargs):
            daemon.apply_when_offline()
            return daemon.dispatch(operation)
        with patch.dict(os.environ, {'UPDATE_TEST_LOG':str(log), 'UPDATE_TEST_QUEUE':'yes'}), patch('src.engine.updates.service.request',side_effect=service_request), patch.object(self.fixture.updater,'apply_pending',side_effect=AssertionError('Launcher must not apply updates')):
            self.assertEqual(manager.launch(self.fixture.updater,self.config),0)
        self.assertEqual(log.read_text().splitlines(),['GUI 1.0.0','backend stopped','GUI 1.1.0'])
