"""Verify target dispatch and build failures without starting robot hardware."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / 'packaging/platform'))
import build_and_release


class TargetScriptTests(unittest.TestCase):
    def test_build_verifies_before_packaging_and_forwards_options(self):
        with patch.object(build_and_release.subprocess, 'run') as run:
            build_and_release.main(['glue', '1.2.3', '--channel', 'testing'])
        self.assertEqual(len(run.call_args_list), 3)
        self.assertEqual(run.call_args_list[0].args[0][-1], 'glue')
        self.assertEqual(run.call_args_list[1].args[0][-1], '--self-test')
        self.assertEqual(run.call_args_list[1].kwargs['env']['QT_QPA_PLATFORM'], 'offscreen')
        self.assertEqual(run.call_args_list[2].args[0][-4:], ['glue', '1.2.3', '--channel', 'testing'])

    def test_failed_self_test_never_packages_release(self):
        failure = subprocess.CalledProcessError(1, ['bundle', '--self-test'])
        with patch.object(build_and_release.subprocess, 'run', side_effect=[None, failure]) as run:
            with self.assertRaises(subprocess.CalledProcessError):
                build_and_release.main(['glue', '1.2.3'])
        self.assertEqual(run.call_count, 2)

    def test_invalid_arguments_do_not_start_build(self):
        with patch.object(build_and_release.subprocess, 'run') as run:
            for arguments in (['glue', 'invalid'], ['glue', '1.2.3', '--unknown']):
                with self.assertRaises(SystemExit):
                    build_and_release.main(arguments)
            run.assert_not_called()

    def test_each_target_uses_its_own_version_file_and_forwards_options(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            for index, target in enumerate(json.loads((ROOT / 'config/release_targets.json').read_text())):
                folder = root / 'src/robot_systems' / target
                folder.mkdir(parents=True)
                version = f"2.{index}.1"
                (folder / 'VERSION').write_text(version + '\n')
                with patch.object(build_and_release, 'ROOT', root), patch.object(build_and_release.subprocess, 'run') as run:
                    build_and_release.main([target, '--channel', 'testing'])
                self.assertEqual(run.call_args_list[-1].args[0][-4:], [target, version, '--channel', 'testing'])

    def test_missing_or_invalid_version_file_stops_before_build(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            folder = root / 'src/robot_systems/glue'
            folder.mkdir(parents=True)
            with patch.object(build_and_release, 'ROOT', root), patch.object(build_and_release.subprocess, 'run') as run:
                with self.assertRaises(SystemExit):
                    build_and_release.main(['glue'])
                (folder / 'VERSION').write_text('invalid')
                with self.assertRaises(SystemExit):
                    build_and_release.main(['glue'])
                run.assert_not_called()
