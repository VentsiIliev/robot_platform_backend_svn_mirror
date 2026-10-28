"""Installer ordering, OS-user isolation and fail-closed commissioning checks."""
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

from src.engine.updates import account_provisioning as provisioning
from src.engine.updates.files import lock


class AccountProvisioningTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        current = self.root / 'current'
        payload = current / 'platform/installation/account-maintenance'
        payload.mkdir(parents=True)
        (payload / 'account-maintenance.pyz').write_bytes(b'verified-release-fixture')
        (current / 'manifest.json').write_text(json.dumps({
            'component': 'robot', 'components': {'platform': {'executable': 'test-platform'}},
        }))
        self.database = self.root / 'data/test-system/storage/users/accounts.sqlite3'
        self.database.parent.mkdir(parents=True)
        self.database.touch()
        self.locations = dict(database=str(self.database), platform_uid=os.getuid(), installation_id='new-install')
        self.calls = []
        self.run = patch.object(provisioning.subprocess, 'run', side_effect=self.run_command).start()
        self.addCleanup(patch.stopall)
        patch.object(provisioning.os, 'geteuid', return_value=1000).start()

    def run_command(self, arguments, **options):
        self.calls.append((arguments, options))
        if any(flag in arguments for flag in ('--account-locations', '--account-setup', '--check-installation')):
            # Mirrors the real frozen entrypoint. This must succeed even while
            # the outer installation runtime lease is held by the caller.
            with lock(self.root / 'update-state/runtime.lock', shared=True):
                pass
        return subprocess.CompletedProcess(arguments, 0, stdout=json.dumps(self.locations))

    def test_fresh_install_initializes_as_desktop_user_before_root_manufacturer_prompt(self):
        with lock(self.root / 'runtime.lock'):
            provisioning.provision_installation_accounts(self.root, None, initialize=True)
        commands = [arguments for arguments, _ in self.calls]
        self.assertEqual(commands[0], [str(self.root / 'current/platform/test-platform'), '--account-setup'])
        self.assertEqual(commands[1][-1], '--account-locations')
        self.assertEqual(commands[2][-1], '--check-installation')
        self.assertTrue(all(command[0] == 'sudo' for command in commands[3:]))
        self.assertEqual(commands[-1], ['sudo', '/usr/local/sbin/robot-account-maintenance',
                                        '--database', str(self.database), 'ensure-manufacturer'])
        for arguments, options in self.calls[:3]:
            self.assertEqual(options['env']['ROBOT_PLATFORM_DATA_ROOT'], str(self.root / 'data'))
            self.assertEqual(options['env']['ROBOT_PLATFORM_UPDATE_CONFIG'], str(self.root / 'updates.json'))
        self.assertNotIn('capture_output', self.calls[-1][1])
        installer = commands[-2]
        self.assertEqual(installer[:3], ['sudo', '/usr/bin/python3', '-I'])
        self.assertTrue(installer[-1].startswith('/root/robot-account-maintenance/'))

    def test_existing_install_never_initializes_or_resets_accounts(self):
        provisioning.provision_installation_accounts(self.root, self.root / 'custom-updates.json')
        commands = [arguments for arguments, _ in self.calls]
        self.assertFalse(any('--account-setup' in command for command in commands))
        self.assertEqual(commands[-1][-1], 'ensure-manufacturer')
        self.assertFalse(any('reset-manufacturer' in command for command in commands))

    def test_root_installer_is_refused_before_creating_root_owned_account_material(self):
        with patch.object(provisioning.os, 'geteuid', return_value=0):
            with self.assertRaisesRegex(RuntimeError, 'without sudo'):
                provisioning.provision_installation_accounts(self.root, None, initialize=True)
        self.run.assert_not_called()

    def test_missing_or_invalid_established_record_stops_before_root_tool(self):
        for change in ({'installation_id': None}, {'platform_uid': -1},
                       {'database': '/tmp/another-installation/accounts.sqlite3'}):
            with self.subTest(change=change), patch.dict(self.locations, change):
                self.calls.clear()
                with self.assertRaises(RuntimeError):
                    provisioning.provision_installation_accounts(self.root, None)
                self.assertEqual(len(self.calls), 1)

    def test_setup_or_manufacturer_cancellation_propagates_failure(self):
        for flag in ('--account-setup', '--check-installation', 'ensure-manufacturer'):
            def fail(arguments, **options):
                if flag in arguments:
                    raise subprocess.CalledProcessError(130, arguments)
                return self.run_command(arguments, **options)
            with self.subTest(flag=flag), patch.object(provisioning.subprocess, 'run', side_effect=fail):
                with self.assertRaises(subprocess.CalledProcessError):
                    provisioning.provision_installation_accounts(self.root, None, initialize=True)

    def test_settings_failure_prevents_manufacturer_or_system_setup(self):
        def fail(arguments, **options):
            if '--check-installation' in arguments:
                raise subprocess.CalledProcessError(1, arguments)
            return self.run_command(arguments, **options)
        with patch.object(provisioning.subprocess, 'run', side_effect=fail):
            with self.assertRaises(subprocess.CalledProcessError):
                provisioning.provision_installation_accounts(self.root, None, initialize=True)
        self.assertFalse(any(arguments[0] == 'sudo' for arguments, _ in self.calls))


if __name__ == '__main__':
    unittest.main()
