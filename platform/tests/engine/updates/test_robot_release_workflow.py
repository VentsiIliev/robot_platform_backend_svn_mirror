"""Release orchestration checks using temporary fake components, without hardware."""
import importlib.util
import json
import os
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

PLATFORM = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PLATFORM / 'packaging/robot'))
sys.path.insert(0, str(PLATFORM / 'packaging/shared'))
import release_common as common
import package_robot
from tests.packaging import test_packaging as packaging_tests

spec = importlib.util.spec_from_file_location('robot_release_workflow', PLATFORM / 'packaging/robot/release_robot.py')
workflow = importlib.util.module_from_spec(spec)
spec.loader.exec_module(workflow)


class RobotReleaseWorkflowTests(unittest.TestCase):
    def setUp(self):
        packaging_tests.PackagingTests.setUp(self)
        self.workflow = workflow.Workflow(self.target, self.selected, self.root / 'report.json')

    def archive(self):
        bundle = self.root / 'robot'
        bundle.mkdir()
        manifest = package_robot.assemble(self.target, self.selected, bundle)
        directory = self.root / 'releases' / self.target / 'robot' / self.selected['release_version']
        directory.mkdir(parents=True)
        archive = directory / 'robot.tar.gz'
        common.archive_bundle(bundle, archive, 'robot')
        manifest.update(archive=archive.name, sha256=common.digest(archive))
        common.write_json(directory / 'manifest.json', manifest)
        return archive, manifest, bundle

    def test_actual_archive_installs_and_self_tests_in_temporary_root(self):
        archive, _, _ = self.archive()
        self.workflow.verify()
        self.assertEqual(self.workflow.report['archive'], str(archive))
        self.assertEqual([stage['status'] for stage in self.workflow.report['stages']], ['passed', 'passed'])
        installed_command = self.workflow.report['stages'][1]['command']
        self.assertEqual(installed_command[1:], ['--self-test'])
        self.assertFalse(Path(installed_command[0]).exists())

    def test_bad_checksum_stops_before_installation(self):
        archive, _, _ = self.archive()
        with archive.open('ab') as stream:
            stream.write(b'corruption')
        with patch.object(self.workflow, 'run') as run:
            with self.assertRaisesRegex(ValueError, 'checksum mismatch'):
                self.workflow.verify()
            run.assert_not_called()

    def test_embedded_manifest_mismatch_stops_before_installation(self):
        archive, manifest, bundle = self.archive()
        common.write_json(bundle / 'manifest.json', {**manifest, 'version': '9.9.9'})
        common.archive_bundle(bundle, archive, 'robot')
        manifest['sha256'] = common.digest(archive)
        common.write_json(archive.parent / 'manifest.json', manifest)
        with patch.object(self.workflow, 'run') as run:
            with self.assertRaisesRegex(ValueError, 'differs from published'):
                self.workflow.verify()
            run.assert_not_called()

    def test_existing_components_are_reused_without_rebuild(self):
        with patch.object(common, 'source_identity'), patch.object(self.workflow, 'run') as run:
            self.workflow.build()
        self.assertEqual(run.call_count, 1)
        self.assertEqual(Path(run.call_args.args[1][2]).name, 'package_robot.py')

    def test_invalid_existing_component_does_not_trigger_rebuild(self):
        path = self.root / 'releases' / self.target / 'platform' / self.selected['platform_version'] / 'manifest.json'
        manifest = json.loads(path.read_text())
        common.write_json(path, {**manifest, 'sha256': 'bad'})
        with patch.object(common, 'source_identity'), patch.object(self.workflow, 'run') as run:
            with self.assertRaisesRegex(ValueError, 'checksum mismatch'):
                self.workflow.build()
            run.assert_not_called()

    def test_only_missing_component_is_built(self):
        self.workflow.selected = {**self.selected, 'backend_version': '1.0.1'}
        with patch.object(common, 'source_identity'), patch.object(self.workflow, 'run') as run:
            self.workflow.build()
        scripts = [Path(call.args[1][2]).name for call in run.call_args_list]
        self.assertEqual(scripts, ['package_backend.py', 'package_robot.py'])

    def test_dirty_source_blocks_all_build_commands(self):
        with patch.object(common, 'source_identity', side_effect=ValueError('working tree is dirty')):
            with patch.object(self.workflow, 'run') as run:
                with self.assertRaisesRegex(ValueError, 'working tree is dirty'):
                    self.workflow.build()
                run.assert_not_called()

    def test_existing_robot_release_cannot_be_overwritten(self):
        self.archive()
        with patch.object(common, 'source_identity'), patch.object(self.workflow, 'run') as run:
            with self.assertRaisesRegex(ValueError, 'Release already exists'):
                self.workflow.build()
            run.assert_not_called()

    def test_failed_stage_is_recorded_and_propagated(self):
        import subprocess
        failure = subprocess.CalledProcessError(1, ['fake-test'])
        with patch.object(workflow.subprocess, 'run', side_effect=failure):
            with self.assertRaises(subprocess.CalledProcessError):
                self.workflow.run('Failing test', ['fake-test'])
        report = json.loads(self.workflow.report_path.read_text())
        self.assertEqual(report['stages'][0]['status'], 'failed')

    def test_publish_orders_svn_before_tests_build_verify_and_upload(self):
        stages = []
        with (patch.object(workflow, 'Workflow', return_value=self.workflow),
              patch.object(workflow.common, 'source_identity'),
              patch.object(workflow.subprocess, 'check_output', side_effect=['master\n', 'git@github.com:owner/robot.git\n']),
              patch.object(workflow, 'GitHubPublisher') as publisher,
              patch.object(self.workflow, 'run', side_effect=lambda *a, **kw: stages.append('svn')),
              patch.object(self.workflow, 'tests', side_effect=lambda: stages.append('tests')),
              patch.object(self.workflow, 'build', side_effect=lambda: stages.append('build')),
              patch.object(self.workflow, 'verify', side_effect=lambda: stages.append('verify')),
              patch.object(self.workflow, 'publish', side_effect=lambda *a: stages.append('publish')),
              patch.dict(os.environ, {'GITHUB_TOKEN': 'private-token'}),
              patch.object(sys, 'argv', ['release_robot.py', 'publish', self.target])):
            publisher.return_value.request.return_value = {'permissions': {'push': True}}
            workflow.main()
        self.assertEqual(['svn', 'tests', 'build', 'verify', 'publish'], stages)
        self.assertNotIn('private-token', self.workflow.report_path.read_text())

    def test_failed_svn_publication_blocks_build_and_gitea_upload(self):
        import subprocess
        with (patch.object(workflow, 'Workflow', return_value=self.workflow),
              patch.object(workflow.common, 'source_identity'),
              patch.object(workflow.subprocess, 'check_output', side_effect=['master\n', 'git@github.com:owner/robot.git\n']),
              patch.object(workflow, 'GitHubPublisher') as publisher,
              patch.object(self.workflow, 'run', side_effect=subprocess.CalledProcessError(1, ['git', 'svn', 'dcommit'])),
              patch.object(self.workflow, 'tests') as tests,
              patch.object(self.workflow, 'publish') as publish,
              patch.dict(os.environ, {'GITHUB_TOKEN': 'private-token'}),
              patch.object(sys, 'argv', ['release_robot.py', 'publish', self.target])):
            publisher.return_value.request.return_value = {'permissions': {'push': True}}
            with self.assertRaises(SystemExit):
                workflow.main()
            tests.assert_not_called()
            publish.assert_not_called()

    def test_actions_rejects_source_without_svn_revision_before_network(self):
        with (patch.object(workflow, 'Workflow', return_value=self.workflow),
              patch.object(workflow.common, 'source_identity', return_value={'source_svn_revision': None}),
              patch.object(workflow, 'GitHubPublisher') as publisher,
              patch.object(self.workflow, 'run') as run,
              patch.dict(os.environ, {'GITHUB_TOKEN': 'private-token'}),
              patch.object(sys, 'argv', ['release_robot.py', 'publish', self.target, '--svn-synced'])):
            with self.assertRaises(SystemExit):
                workflow.main()
            run.assert_not_called()
            publisher.assert_not_called()


if __name__ == '__main__':
    unittest.main()
