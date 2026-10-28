"""Required settings from a packaged clean data root, without starting services."""
import importlib.util
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from src.engine.updates.factory_defaults import seed_factory_defaults
from src.engine.repositories.interfaces.settings_repository import SettingsLoadError

ROOT = Path(__file__).resolve().parents[2]


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


targets = load('fresh_settings_targets', ROOT / 'packaging/platform/targets.py')
entry = load('fresh_settings_entry', ROOT / 'packaging/platform/platform_entrypoint.py')


class FreshInstallSettingsTests(unittest.TestCase):
    def prepare(self, name, root):
        original = Path.read_text
        config_path = ROOT / 'config/platform.json'
        config = json.loads(config_path.read_text())
        config['robot_systems'][name] = dict(robot_driver='zeroerr', backend='zeroerr',
            backend_profile='paint_short_links', release_version='1.0.20',
            platform_version='1.0.20', backend_version='1.0.1')
        def read(path, *args, **kwargs):
            return json.dumps(config) if path == config_path else original(path, *args, **kwargs)
        with patch.object(Path, 'read_text', read):
            return targets.prepare_target(name, root / 'config')

    def test_every_required_paint_setting_loads_from_empty_packaged_storage(self):
        for name in ('paint', 'paint_tray_dry', 'paint_auto_dry'):
            with self.subTest(name=name), tempfile.TemporaryDirectory() as temporary:
                root = Path(temporary)
                target = self.prepare(name, root)
                before = os.environ.get('ROBOT_PLATFORM_DATA_ROOT')
                entry.check_fresh_settings(root, target)
                self.assertEqual(os.environ.get('ROBOT_PLATFORM_DATA_ROOT'), before)
                document = json.loads((root / 'config/factory-defaults.json').read_text())
                self.assertEqual(document['files']['tools/tool_changer.json'], {
                    'tools': [{'id': 1, 'name': 'Calibration Tool'}], 'slots': [],
                })
                self.assertEqual(document['files']['robot/movement_groups.json'], {'MOVEMENT_GROUPS': {}})
                self.assertEqual(document['files']['robot/calibration.json']['workobject_calibrations'], {})
                authored = json.loads((ROOT / f'config/factory_defaults/{name}.json').read_text())
                for key, value in authored['files'].items():
                    self.assertEqual(document['files'][key], value)

    def test_frozen_self_test_rejects_original_missing_tool_changer_regression(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            target = self.prepare('paint_tray_dry', root)
            path = root / 'config/factory-defaults.json'
            document = json.loads(path.read_text())
            del document['files']['tools/tool_changer.json']
            path.write_text(json.dumps(document))
            before = os.environ.get('ROBOT_PLATFORM_DATA_ROOT')
            with self.assertRaisesRegex(SettingsLoadError, 'tool_changer.json'):
                entry.check_fresh_settings(root, target)
            self.assertEqual(os.environ.get('ROBOT_PLATFORM_DATA_ROOT'), before)

    def test_existing_machine_settings_are_preserved_and_missing_files_still_require_recovery(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            target = self.prepare('paint_tray_dry', root)
            data = root / 'data'
            seed_factory_defaults(root, data, target)
            settings = data / 'paint_tray_dry/storage/settings'
            tool = settings / 'tools/tool_changer.json'
            tool.write_text('{"tools": [{"id": 9, "name": "Customer tool"}], "slots": []}')
            before = tool.read_bytes()
            self.assertEqual(seed_factory_defaults(root, data, target), [])
            self.assertEqual(tool.read_bytes(), before)
            tool.unlink()
            with self.assertRaisesRegex(RuntimeError, 'established storage'):
                seed_factory_defaults(root, data, target)
            self.assertFalse(tool.exists())

    def test_installer_check_uses_real_data_before_hardware_and_preserves_accounts(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            target = self.prepare('paint_tray_dry', root / 'resources')
            data = root / 'data'
            users = data / 'paint_tray_dry/storage/users'
            users.mkdir(parents=True)
            account = users / 'accounts.sqlite3'
            account.write_bytes(b'account sentinel untouched by settings check')
            environment = {'ROBOT_PLATFORM_DATA_ROOT': str(data)}
            with patch.dict(os.environ, environment), \
                    patch.object(entry.sys, '_MEIPASS', str(root / 'resources'), create=True), \
                    patch.object(entry.sys, 'argv', ['platform', '--check-installation']), \
                    patch.object(entry, 'default_config_path', return_value=root / 'absent-config'), \
                    patch.object(entry, 'default_install_root', return_value=root / 'installed'), \
                    patch('src.bootstrap.run_main.main') as start:
                entry.main()
                start.assert_not_called()
            settings = data / 'paint_tray_dry/storage/settings'
            self.assertEqual(len(list(settings.rglob('*.json'))), 15)
            self.assertEqual(account.read_bytes(), b'account sentinel untouched by settings check')
            # Missing established storage must fail here, not after hardware starts.
            (settings / 'tools/tool_changer.json').unlink()
            with self.assertRaisesRegex(RuntimeError, 'established storage'):
                entry.prepare_installed_settings(root / 'resources', data, target)
