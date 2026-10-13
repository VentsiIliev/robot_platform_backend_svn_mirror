import importlib.util
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

ROOT = Path(__file__).resolve().parents[3]
spec = importlib.util.spec_from_file_location('platform_installer', ROOT / 'packaging/runtime/manage.py')
manager = importlib.util.module_from_spec(spec)
spec.loader.exec_module(manager)


class RemoteSupportInstallTests(unittest.TestCase):
    def test_packaged_vendor_loads_config_beside_script_from_another_directory(self):
        spec = importlib.util.spec_from_file_location(
            'remote_support_payload', ROOT / 'packaging/remote_support/build_payload.py')
        builder = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(builder)
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            payload = root / 'payload'
            builder.build_payload(payload)
            for name in ('install_openssh.sh', 'install_rustdesk.sh',
                         'install_auto_login.sh', 'install_update_helper.sh'):
                self.assertTrue((payload / name).is_file(), name)
            self.assertEqual((payload / 'release.conf').read_bytes(),
                             (ROOT / 'packaging/remote_support/release.conf').read_bytes())
            (payload / 'release.conf').write_text(
                'DOWNLOAD_BASE_URL="https://example.org/support/"\n'
                'RELEASE="v2.0.0"\nPACKAGE="support.deb"\nEXPECTED_VERSION="2.0.0"\n')
            commands = root / 'commands'
            commands.mkdir()
            # Stop before any provisioning commands; the EXIT trap observes
            # the actual installer configuration after it has been loaded.
            (commands / 'mktemp').write_text('#!/bin/bash\nexit 73\n')
            (commands / 'mktemp').chmod(0o755)
            probe = '''trap 'printf "%s\\n" "$DOWNLOAD_URL" "$EXPECTED_VERSION"' EXIT
source "$1" --provision-only
'''
            result = subprocess.run(
                ['bash', '-c', probe, 'probe', str(payload / 'install_pl_remote_support.sh')],
                cwd=root, env={**os.environ, 'PATH': str(commands) + ':' + os.environ['PATH']},
                capture_output=True, text=True)
            self.assertEqual(result.returncode, 73, result.stderr)
            self.assertEqual(result.stdout.splitlines(),
                             ['https://example.org/support/v2.0.0/support.deb', '2.0.0'])
            (payload / 'release.conf').unlink()
            result = subprocess.run(['bash', str(payload / 'install_pl_remote_support.sh')],
                                    cwd=root, capture_output=True, text=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn('Remote support configuration is missing', result.stderr)

    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.payload = self.root / 'current/platform/installation/remote-support'
        self.payload.mkdir(parents=True)
        for name in ('install.sh', 'install_pl_remote_support.sh'):
            (self.payload / name).touch()

    def test_desktop_install_elevates_only_support_step_and_passes_vendor(self):
        with patch.object(manager.os, 'geteuid', return_value=1000), patch.object(manager.pwd, 'getpwuid', return_value=SimpleNamespace(pw_name='operator')), patch.object(manager.subprocess, 'run') as run:
            manager.install_remote_support(self.root)
        self.assertEqual(run.call_args.args[0], ['sudo', 'bash', str(self.payload / 'install.sh'), 'operator', '--vendor-installer', str(self.payload / 'install_pl_remote_support.sh')])
        self.assertTrue(run.call_args.kwargs['check'])

    def test_privileged_install_uses_original_desktop_user(self):
        with patch.object(manager.os, 'geteuid', return_value=0), patch.dict(manager.os.environ, SUDO_USER='operator'), patch.object(manager.subprocess, 'run') as run:
            manager.install_remote_support(self.root)
        self.assertEqual(run.call_args.args[0][:3], ['bash', str(self.payload / 'install.sh'), 'operator'])

    def test_failed_support_step_reports_retry_without_success(self):
        with patch.object(manager.os, 'geteuid', return_value=1000), patch.object(manager.subprocess, 'run', side_effect=subprocess.CalledProcessError(1, 'sudo')):
            with self.assertRaisesRegex(RuntimeError, 'rerun the installer to retry'):
                manager.install_remote_support(self.root)

    def test_missing_payload_does_not_run_privileged_command(self):
        (self.payload / 'install.sh').unlink()
        with patch.object(manager.subprocess, 'run') as run:
            with self.assertRaisesRegex(RuntimeError, 'payload is missing'):
                manager.install_remote_support(self.root)
            run.assert_not_called()

    def test_boot_provisioning_retires_gate_before_starting_services(self):
        # Run the component scripts with command doubles and isolated paths.
        # No package manager, host service, or host configuration is touched.
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            commands = root / 'commands'
            commands.mkdir()
            log = root / 'calls'
            gate = root / 'gate.conf'
            ssh_runtime = root / 'run' / 'sshd'
            gate.write_text('ExecCondition=old-controller\n')
            stub = '#!/bin/bash\necho "$(basename "$0") $*" >> "$CALL_LOG"\n'
            for name in ('id', 'apt-get', 'systemctl', 'sshd'):
                extra = 'if [[ $1 == show ]]; then echo loaded; fi\n' if name == 'systemctl' else ''
                if name == 'sshd':
                    extra = f'test -d "{ssh_runtime}" || exit 255\n'
                path = commands / name
                path.write_text(stub + extra)
                path.chmod(0o755)
            source_dir = ROOT / 'packaging/remote_support'
            for name in ('install.sh', 'install_openssh.sh', 'install_rustdesk.sh',
                         'install_auto_login.sh'):
                source = (source_dir / name).read_text()
                source = source.replace('[[ ${EUID} -ne 0 ]]', '[[ 0 -ne 0 ]]')
                source = source.replace('[[ ${EUID} -ne 0 ||', '[[ 0 -ne 0 ||')
                source = source.replace(
                    '/etc/systemd/system/rustdesk.service.d/plproject-remote-support.conf',
                    str(gate))
                source = source.replace('/usr/sbin/sshd', str(commands / 'sshd'))
                source = source.replace('install -d -o root -g root -m 0755 /run/sshd',
                                        f'install -d -m 0755 "{ssh_runtime}"')
                source = source.replace('install -o root -g root -m 0755', 'install -m 0755')
                source = source.replace('/usr/local/bin/auto_login.sh',
                                        str(root / 'installed-auto-login.sh'))
                (root / name).write_text(source)
            (root / 'auto_login.sh').write_text('#!/bin/bash\n')
            (root / 'install_update_helper.sh').write_text('#!/bin/bash\necho "install-update-helper $*" >> "$CALL_LOG"\n')
            subprocess.run(['bash', str(root / 'install.sh'), 'operator'], check=True,
                           env={**os.environ, 'PATH': str(commands) + ':' + os.environ['PATH'], 'CALL_LOG': str(log)},
                           capture_output=True)
            calls = log.read_text()
            self.assertFalse(gate.exists())
            self.assertIn('apt-get -o DPkg::Lock::Timeout=600 install -y openssh-server', calls)
            self.assertIn('apt-get -o DPkg::Lock::Timeout=600 install -y libzbar0 libxcb-cursor0', calls)
            self.assertIn('sshd -t', calls)
            self.assertEqual(ssh_runtime.stat().st_mode & 0o777, 0o755)
            self.assertIn('systemctl enable --now ssh.service', calls)
            self.assertIn('systemctl enable --now rustdesk.service', calls)
            self.assertIn('install-update-helper operator', calls)
            self.assertLess(calls.index('disable --now plproject-remote-support-expiry.timer'),
                            calls.index('enable --now rustdesk.service'))


class LauncherRefreshTests(unittest.TestCase):
    def test_launcher_executes_new_helper_after_activation(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            old = root / "updater-tools/old"
            new = root / "updater-tools/new"
            old.mkdir(parents=True)
            new.mkdir()
            (new / "manage.py").touch()
            (root / "tools").symlink_to(new)
            updater = MagicMock(root=root)
            config = root / "machine-config.json"
            with patch.object(manager, "HERE", old), patch.object(manager, "__file__", str(old / "manage.py")), patch.object(manager.os, "execv", side_effect=SystemExit) as execute:
                with self.assertRaises(SystemExit):
                    manager.launch(updater, config)
            execute.assert_called_once_with("/usr/bin/python3", ["/usr/bin/python3", str(root / "tools/manage.py"), "--config", str(config), "launch"])
            updater.recover.assert_called_once()
            updater.apply_pending.assert_called_once()


class FirstInstallSetupTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.config = self.root / 'updates.json'

    def test_first_install_sets_up_once_and_maintenance_preserves_settings(self):
        state = manager.prepare_system_setup(self.root, first_install=True)
        with patch.object(manager, 'install_remote_support') as support, patch.object(manager, 'install_kiosk') as kiosk:
            manager.finish_system_setup(self.root, self.config, state)
            state = manager.prepare_system_setup(self.root, first_install=False)
            manager.finish_system_setup(self.root, self.config, state)
        support.assert_called_once_with(self.root)
        kiosk.assert_called_once_with(self.root, self.config, 'enabled', launcher=None)

    def test_failed_initial_setup_remains_pending_and_retries_after_activation(self):
        state = manager.prepare_system_setup(self.root, first_install=True, mode='manual')
        with patch.object(manager, 'install_remote_support'), patch.object(manager, 'install_kiosk', side_effect=RuntimeError('GDM unavailable')):
            with self.assertRaisesRegex(RuntimeError, 'rerun the installer'):
                manager.finish_system_setup(self.root, self.config, state)
        state = manager.prepare_system_setup(self.root, first_install=False, mode='manual')
        self.assertFalse(state['complete'])
        self.assertEqual(state['kiosk'], 'manual')
        with patch.object(manager, 'install_remote_support'), patch.object(manager, 'install_kiosk') as kiosk:
            manager.finish_system_setup(self.root, self.config, state)
        kiosk.assert_called_once_with(self.root, self.config, 'manual', launcher=None)

    def test_retry_before_activation_keeps_original_kiosk_choice(self):
        manager.prepare_system_setup(self.root, first_install=True, mode='off')
        self.assertEqual(manager.prepare_system_setup(self.root, first_install=True)['kiosk'], 'off')

    def test_legacy_install_does_not_automatically_change_system_configuration(self):
        self.assertIsNone(manager.prepare_system_setup(self.root, first_install=False))
        with self.assertRaisesRegex(ValueError, '--setup-system'):
            manager.prepare_system_setup(self.root, first_install=False, mode='enabled')
        state = manager.prepare_system_setup(self.root, first_install=False, setup_system=True, mode='off')
        with patch.object(manager, 'install_remote_support') as support, patch.object(manager, 'install_kiosk') as kiosk:
            manager.finish_system_setup(self.root, self.config, state)
        support.assert_called_once()
        kiosk.assert_called_once_with(self.root, self.config, 'off', launcher=None)

    def test_kiosk_uses_stable_launcher_and_explicit_update_configuration(self):
        installer = self.root / 'current/platform/installation/kiosk/setup_kiosk.sh'
        installer.parent.mkdir(parents=True)
        installer.touch()
        with patch.object(manager.os, 'geteuid', return_value=1000), patch.object(manager, 'desktop_user', return_value='operator'), patch.object(manager, 'provision_kiosk_password') as provision, patch.object(manager.subprocess, 'run') as run:
            manager.install_kiosk(self.root, self.config, 'manual')
            provision.assert_called_once_with(self.root)
            command = run.call_args.args[0]
            self.assertEqual(command[:5], ['sudo', 'bash', str(installer), 'install', '--user'])
            self.assertEqual(command[command.index('--autologin') + 1], 'no')
            self.assertEqual(command[command.index('--') + 1:], ['/usr/bin/python3', str(self.root / 'tools/manage.py'), '--config', str(self.config), 'launch'])
            manager.install_kiosk(self.root, None, 'enabled', launcher=self.root / 'launch.sh')
            self.assertEqual(run.call_args.args[0][-2:], ['--', str(self.root / 'launch.sh')])
            run.reset_mock()
            manager.install_kiosk(self.root, self.config, 'off')
            run.assert_not_called()

    def test_kiosk_password_is_provisioned_once_and_validated_for_operator(self):
        manifest = self.root / 'current/manifest.json'
        executable = self.root / 'current/platform/paint-robot'
        executable.parent.mkdir(parents=True)
        executable.touch()
        manifest.write_text('{"executable": "paint-robot"}')
        password = self.root / 'etc/kiosk-password.json'
        with patch.object(manager, 'KIOSK_PASSWORD_FILE', password), \
             patch.object(manager.os, 'geteuid', return_value=1000), \
             patch.object(manager, 'desktop_user', return_value='operator'), \
             patch.object(manager.subprocess, 'run') as run:
            run.return_value.returncode = 1
            manager.provision_kiosk_password(self.root)
        commands = [call.args[0] for call in run.call_args_list]
        self.assertIn(['sudo', str(executable), '--set-kiosk-password', '--read-group',
                       'robot-kiosk'], commands)
        self.assertEqual(commands[-1], ['sudo', 'runuser', '-u', 'operator', '--',
                                        'test', '-r', str(password)])

    def test_kiosk_password_resolves_combined_robot_platform_executable(self):
        manifest = self.root / 'current/manifest.json'
        executable = self.root / 'current/platform/paint-robot'
        executable.parent.mkdir(parents=True)
        executable.touch()
        manifest.write_text('{"components": {"platform": {"executable": "paint-robot"}}}')
        password = self.root / 'etc/kiosk-password.json'
        with patch.object(manager, 'KIOSK_PASSWORD_FILE', password), \
             patch.object(manager.os, 'geteuid', return_value=0), \
             patch.object(manager, 'desktop_user', return_value='operator'), \
             patch.object(manager.subprocess, 'run') as run:
            run.return_value.returncode = 1
            manager.provision_kiosk_password(self.root)
        self.assertIn(
            [str(executable), '--set-kiosk-password', '--read-group', 'robot-kiosk'],
            [call.args[0] for call in run.call_args_list],
        )

    def test_existing_kiosk_password_is_preserved(self):
        password = self.root / 'etc/kiosk-password.json'
        with patch.object(manager, 'KIOSK_PASSWORD_FILE', password), \
             patch.object(manager.os, 'geteuid', return_value=0), \
             patch.object(manager, 'desktop_user', return_value='operator'), \
             patch.object(manager.subprocess, 'run') as run:
            run.return_value.returncode = 0
            manager.provision_kiosk_password(self.root)
        commands = [call.args[0] for call in run.call_args_list]
        self.assertFalse(any('--set-kiosk-password' in command for command in commands))
        self.assertEqual(commands[-1], ['runuser', '-u', 'operator', '--', 'test', '-r',
                                        str(password)])

    def test_packaged_kiosk_password_is_installed_without_prompt(self):
        password = self.root / 'etc/kiosk-password.json'
        packaged = self.root / 'current/platform/installation/kiosk/kiosk-password.json'
        packaged.parent.mkdir(parents=True)
        packaged.write_text('{"version": 1}')
        with patch.object(manager, 'KIOSK_PASSWORD_FILE', password), \
             patch.object(manager.os, 'geteuid', return_value=0), \
             patch.object(manager, 'desktop_user', return_value='operator'), \
             patch.object(manager.subprocess, 'run') as run:
            run.return_value.returncode = 1
            manager.provision_kiosk_password(self.root)
        commands = [call.args[0] for call in run.call_args_list]
        self.assertIn(['install', '-o', 'root', '-g', 'robot-kiosk', '-m', '0640',
                       str(packaged), str(password)], commands)
        self.assertFalse(any('--set-kiosk-password' in command for command in commands))

    def test_kiosk_session_requires_password_and_enables_application_guard(self):
        source = (ROOT / 'packaging/kiosk/setup_kiosk.sh').read_text()
        self.assertIn('test -r "$password_file"', source)
        self.assertIn("printf 'export ROBOT_PLATFORM_KIOSK_MODE=1", source)
        self.assertIn('Option "DontVTSwitch" "true"', source)
        self.assertIn('Option "DontZap" "true"', source)

    def test_combined_installer_provisions_first_install_only(self):
        source = ROOT / 'packaging/robot/install_robot.py'
        if not source.is_file():
            self.skipTest('Combined deployment installer is not in this checkout')
        spec = importlib.util.spec_from_file_location('combined_robot_installer', source)
        combined = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(combined)
        bundle = self.root / 'bundle'
        (bundle / 'backend').mkdir(parents=True)
        (bundle / 'launch.sh').touch()
        (bundle / 'backend/launch.sh').touch()
        marker = bundle / 'platform/_internal/config/release-target.json'
        marker.parent.mkdir(parents=True)
        marker.write_text('{"product":"paint-robot"}')
        helper = bundle / 'platform/installation/system-setup.py'
        helper.parent.mkdir(parents=True)
        helper.write_text('from tests.engine.updates.test_installer_remote_support import manager\n'
                          'prepare_system_setup = manager.prepare_system_setup\n'
                          'finish_system_setup = manager.finish_system_setup\n')
        manifest = {'version': '1.0.0', 'target': 'paint', 'architecture': combined.platform.machine(),
                    'os': 'ubuntu-24.04'}
        (bundle / 'manifest.json').write_text(__import__('json').dumps(manifest))
        installed = self.root / 'combined'
        original_read = Path.read_text
        def read(path, *args, **kwargs):
            return 'VERSION_ID="24.04"' if str(path) == '/etc/os-release' else original_read(path, *args, **kwargs)
        with patch.object(combined, '__file__', str(bundle / 'install.py')), patch.object(Path, 'read_text', read), patch.object(manager, 'install_remote_support') as support, patch.object(manager, 'install_kiosk') as kiosk:
            with patch.object(sys, 'argv', ['install.py', '--root', str(self.root / 'verification'), '--skip-system-setup']):
                combined.main()
            support.assert_not_called()
            kiosk.assert_not_called()
            self.assertFalse((self.root / 'verification/update-state/system-setup.json').exists())
            with patch.object(sys, 'argv', ['install.py', '--root', str(installed), '--kiosk', 'manual']):
                combined.main()
            with patch.object(sys, 'argv', ['install.py', '--root', str(installed)]):
                combined.main()
        support.assert_called_once_with(installed)
        kiosk.assert_called_once_with(installed, None, 'manual', launcher=installed / 'launch.sh')
