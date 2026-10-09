import importlib.util
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

from src.engine.updates.remote_support import reconcile
from tests.engine.updates import test_robot_updates as fixtures
ROOT = fixtures.ROOT


class RemoteSupportTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.release = Path(self.temp.name)
        config = self.release / 'platform/installation/remote-support/release.conf'
        config.parent.mkdir(parents=True)
        config.write_text((ROOT / 'packaging/remote_support/release.conf').read_text())

    def test_matching_package_skips_privileged_work(self):
        with patch('src.engine.updates.remote_support.subprocess.run') as run:
            run.return_value = subprocess.CompletedProcess([], 0, 'install ok installed|1.4.9')
            reconcile(self.release)
            self.assertEqual(run.call_count, 1)

    def test_different_version_invokes_only_scoped_helper(self):
        with patch('src.engine.updates.remote_support.subprocess.run') as run:
            run.return_value = subprocess.CompletedProcess([], 0, 'install ok installed|1.4.8')
            reconcile(self.release)
            command = run.call_args.args[0]
            self.assertEqual(command[:4], ['sudo', '-n', '/usr/local/libexec/robot-remote-support-update', 'upgrade'])
            self.assertEqual(command[-1], '1.4.9')

    def test_upgrade_failure_prevents_activation(self):
        fixture = fixtures.RobotUpdateTests()
        fixture.setUp()
        self.addCleanup(fixture.doCleanups)
        fixture.install()
        fixture.feed_release()
        fixture.updater.stage_latest()
        fixture.updater.queue()
        previous = (fixture.root / 'current').resolve()
        with patch('src.engine.updates.remote_support.reconcile', side_effect=RuntimeError('upgrade failed')):
            with self.assertRaisesRegex(RuntimeError, 'upgrade failed'):
                fixture.updater.apply_pending()
        self.assertEqual((fixture.root / 'current').resolve(), previous)
        self.assertFalse((fixture.updater.state / 'pending.json').exists())

    def test_helper_rejects_unapproved_source_before_download(self):
        spec = importlib.util.spec_from_file_location('support_helper', ROOT / 'packaging/remote_support/update_package.py')
        helper = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(helper)
        policy = self.release / 'policy.json'
        policy.write_text('{"download_base_url": "https://trusted.example/releases"}')
        with patch.object(helper, 'POLICY', policy), patch.object(helper.urllib.request, 'urlopen') as download:
            with self.assertRaises(ValueError):
                helper.upgrade('https://other.example', 'v2', 'rustdesk.deb', '2')
            with self.assertRaises(ValueError):
                helper.upgrade('https://trusted.example/releases', '../escape', 'rustdesk.deb', '2')
            download.assert_not_called()
