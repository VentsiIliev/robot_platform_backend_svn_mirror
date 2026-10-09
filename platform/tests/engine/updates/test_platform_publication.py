"""Platform Actions checks with fake artifacts and no external publication."""
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch, MagicMock

PLATFORM = Path(__file__).resolve().parents[3]
spec = importlib.util.spec_from_file_location('platform_publication', PLATFORM / 'packaging/platform/publish_platform.py')
pub = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pub)


class PlatformPublicationTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.target = 'paint_tray_dry'
        system = self.root / 'platform/src/robot_systems' / self.target
        system.mkdir(parents=True)
        (system / 'VERSION').write_text('1.0.6')
        self.output = self.root / 'artifacts'
        self.identity = dict(source_git_commit='abc', source_svn_revision='28')
        self.directory = self.output / self.target / 'stable'
        self.directory.mkdir(parents=True)
        self.archive = self.directory / 'update.tar.gz'
        self.archive.write_bytes(b'update')
        kit = self.output / self.target / 'paint-tray-dry-robot-installer-1.0.6-x86_64.tar.gz'
        kit.write_bytes(b'installer')
        self.manifest = dict(robot_system=self.target, version='1.0.6', source_svn_revision='28',
                             archive='update.tar.gz', sha256=pub.common.digest(self.archive),
                             product='paint-tray-dry-robot', architecture='x86_64')
        self.save()
        self.publisher = MagicMock()
        self.publisher.request.side_effect = lambda method, path, **kw: {'permissions': {'push': True}} if path == '' else None
        self.publisher.publish_assets.return_value = 'http://gitea/release'

    def save(self):
        (self.directory / 'latest.json').write_text(json.dumps(self.manifest))

    def invoke(self):
        with (patch.object(pub, 'PLATFORM', self.root / 'platform'),
              patch.object(pub.common, 'source_identity', return_value=self.identity),
              patch.object(pub, 'GiteaPublisher', return_value=self.publisher),
              patch.object(pub.subprocess, 'run') as build):
            result = pub.publish(self.target, self.output, 'http://gitea/admin/repo', 'private-token')
            return result, build

    def test_uses_component_builder_and_attaches_installer_update_and_checksums(self):
        result, build = self.invoke()
        self.assertEqual('http://gitea/release', result)
        self.assertEqual('build_and_release.py', Path(build.call_args.args[0][1]).name)
        self.assertEqual(['paint_tray_dry', '1.0.6'], build.call_args.args[0][2:4])
        self.assertIn('--svn-revision', build.call_args.args[0])
        files = self.publisher.publish_assets.call_args.args[4]
        self.assertEqual(5, len(files))
        self.assertTrue(any('installer' in path.name for path in files))
        self.assertTrue(any(path.name == 'SHA256SUMS' for path in files))
        self.assertEqual('paint_tray_dry/platform/v1.0.6', self.publisher.publish_assets.call_args.args[0])
        self.assertNotIn('private-token', (self.directory / 'release-manifest.json').read_text())

    def test_retry_reuses_verified_artifacts_without_rebuilding(self):
        self.invoke()
        _, build = self.invoke()
        build.assert_not_called()

    def test_cached_installer_corruption_is_rejected(self):
        self.invoke()
        kit = next(self.output.glob('paint_tray_dry/*installer*'))
        kit.write_bytes(b'corrupt')
        with self.assertRaisesRegex(ValueError, 'Cached release differs'):
            self.invoke()

    def test_missing_svn_revision_blocks_build_and_api(self):
        self.identity['source_svn_revision'] = None
        with self.assertRaisesRegex(ValueError, 'SVN first'):
            self.invoke()
        self.publisher.request.assert_not_called()

    def test_existing_tag_on_different_commit_blocks_build(self):
        self.publisher.request.side_effect = lambda method, path, **kw: {'permissions': {'push': True}} if path == '' else {'commit': {'sha': 'different'}}
        with self.assertRaisesRegex(ValueError, 'increment VERSION'):
            self.invoke()
        self.publisher.publish_assets.assert_not_called()

    def test_failed_build_blocks_tag_creation_and_upload(self):
        import subprocess
        with (patch.object(pub, 'PLATFORM', self.root / 'platform'),
              patch.object(pub.common, 'source_identity', return_value=self.identity),
              patch.object(pub, 'GiteaPublisher', return_value=self.publisher),
              patch.object(pub.subprocess, 'run', side_effect=subprocess.CalledProcessError(1, ['build']))):
            with self.assertRaises(subprocess.CalledProcessError):
                pub.publish(self.target, self.output, 'http://gitea/admin/repo', 'token')
        self.publisher.publish_assets.assert_not_called()
        self.assertFalse(any(call.args[0] == 'POST' for call in self.publisher.request.call_args_list))

    def test_wrong_manifest_revision_is_rejected(self):
        self.manifest['source_svn_revision'] = '27'
        self.save()
        with self.assertRaisesRegex(ValueError, 'SVN revision'):
            pub.prepare_artifacts(self.output, self.target, '1.0.6', self.identity)
