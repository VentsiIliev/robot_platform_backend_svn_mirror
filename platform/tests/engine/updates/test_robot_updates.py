"""Complete-system discovery, transactional activation and launcher checks."""
import importlib.util
import io
import json
import os
from pathlib import Path
import platform
import shutil
import subprocess
import tarfile
import tempfile
import unittest
from unittest.mock import patch
from dataclasses import replace

from src.engine.updates.config import UpdateConfig
from src.engine.updates.files import atomic_json, lock
from src.engine.updates.updater import PlatformUpdater

ROOT = Path(__file__).resolve().parents[3]


class RobotUpdateTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.directory = Path(self.temp.name)
        self.root = self.directory / 'installed'
        self.feed = self.directory / 'feed'
        self.config = UpdateConfig(self.root, str(self.feed), None,
                                   product='paint-tray-dry-robot', enabled=True)
        self.os_patch = patch('platform.freedesktop_os_release',
                              return_value={'ID': 'ubuntu', 'VERSION_ID': '24.04'})
        self.os_patch.start()
        self.addCleanup(self.os_patch.stop)
        self.updater = PlatformUpdater(self.config)

    def bundle(self, version, backend_version, target='paint_tray_dry', bad_backend=False):
        root = self.directory / ('bundle-' + version) / 'robot'
        root.mkdir(parents=True)
        selection = dict(release_version=version, platform_version=version,
                         backend_version=backend_version, robot_driver='zeroerr',
                         backend='zeroerr', backend_profile='paint_short_links')
        base = dict(format=1, target=target, architecture=platform.machine(),
                    os='ubuntu-24.04', backend='zeroerr', profile='paint_short_links')
        components = {
            'platform': dict(base, component='platform', version=version,
                             executable='paint-tray-dry-robot', robot_driver='zeroerr'),
            'backend': dict(base, component='backend', version=backend_version, ros_distro='jazzy'),
        }
        manifest = dict(format=1, component='robot', target=target, version=version,
                        architecture=platform.machine(), os='ubuntu-24.04',
                        selection=selection, components=components)
        atomic_json(root / 'manifest.json', manifest)
        marker = root / 'platform/_internal/config'
        atomic_json(marker / 'release-target.json', dict(product='paint-tray-dry-robot', robot_system=target))
        atomic_json(marker / 'platform.json', dict(robot_system=target,
                    supported_robot_systems=[target], robot_systems={target: selection}))
        backend = dict(components['backend'])
        if bad_backend:
            backend['version'] = '99.0.0'
        atomic_json(root / 'backend/manifest.json', backend)
        executable = root / 'platform/paint-tray-dry-robot'
        executable.write_text('''#!/usr/bin/python3
import json, os, sys
from pathlib import Path
if '--self-test' not in sys.argv and os.environ.get('UPDATE_TEST_LOG'):
    with open(os.environ['UPDATE_TEST_LOG'], 'a') as stream:
        stream.write('GUI VERSION\\n')
    if os.environ.get('UPDATE_TEST_QUEUE') and 'VERSION' == '1.0.0':
        root = Path(os.environ['ROBOT_PLATFORM_DATA_ROOT']).parent
        (root/'update-state/pending.json').write_text(json.dumps({'version':'1.1.0'}))
'''.replace('VERSION', version))
        executable.chmod(0o755)
        scripts = {
            'launch.sh': '#!/bin/bash\nROOT="$(cd "$(dirname "$0")" && pwd)"\nexec "$ROOT/platform/paint-tray-dry-robot" "$@"\n',
            'backend/launch.sh': '#!/bin/sh\nexit 0\n',
            'backend/stop.sh': '#!/bin/sh\n[ -z "$UPDATE_TEST_LOG" ] || echo "backend stopped" >> "$UPDATE_TEST_LOG"\n',
        }
        for name, source in scripts.items():
            path = root / name
            path.write_text(source)
            path.chmod(0o755)
        (root / 'platform/libfake.so.1').write_bytes(b'library')
        (root / 'platform/libfake.so').symlink_to('libfake.so.1')
        archive = self.directory / (version + '.tar.gz')
        with tarfile.open(archive, 'w:gz') as output:
            output.add(root, arcname='robot')
        return archive, manifest

    def install(self):
        archive, _ = self.bundle('1.0.0', '1.0.0')
        self.updater.stage_local(archive)
        self.updater.queue()
        self.updater.apply_pending()
        atomic_json(self.root / 'updates.json', {'machine': 'keep'})
        atomic_json(self.root / 'update-state/system-setup.json', {'complete': True, 'kiosk': 'enabled'})
        atomic_json(self.root / 'data/calibration.json', {'offset': 12.5})

    def feed_release(self):
        archive, manifest = self.bundle('1.1.0', '2.0.0')
        feed = self.feed / 'stable'
        feed.mkdir(parents=True)
        shutil.copy2(archive, feed / archive.name)
        manifest.update(archive=archive.name, sha256=self.updater._digest(archive))
        atomic_json(feed / 'latest.json', manifest)
        return manifest

    def test_ui_checks_downloads_queues_and_activates_both_components(self):
        from src.applications.software_update.service.software_update_service import SoftwareUpdateService
        self.install()
        self.feed_release()
        service = SoftwareUpdateService(lambda: True)
        with patch.object(service, '_updater', return_value=self.updater):
            self.assertTrue(service.check()['available'])
            self.assertEqual(service.download()['version'], '1.1.0')
            service.schedule_installation()
        self.assertEqual(self.updater.installed()['version'], '1.0.0')
        before = {p: p.read_bytes() for p in (self.root/'updates.json', self.root/'update-state/system-setup.json', self.root/'data/calibration.json')}
        self.assertTrue(self.updater.apply_pending())
        current = self.updater.installed()
        self.assertEqual(current['selection']['platform_version'], '1.1.0')
        self.assertEqual(current['selection']['backend_version'], '2.0.0')
        self.assertEqual(json.loads((self.root/'current/backend/manifest.json').read_text())['version'], '2.0.0')
        for path, data in before.items():
            self.assertEqual(path.read_bytes(), data)
        self.assertTrue((self.root/'current/platform/libfake.so').is_symlink())

    def test_incompatible_backend_and_target_are_rejected_before_activation(self):
        self.install()
        for options in ({'bad_backend': True}, {'target': 'paint_auto_dry'}):
            archive, _ = self.bundle('1.1.0', '2.0.0', **options)
            with self.assertRaises(ValueError):
                self.updater.stage_local(archive)
            shutil.rmtree(self.directory/'bundle-1.1.0')
            self.assertEqual(self.updater.installed()['version'], '1.0.0')

    def test_runtime_lock_prevents_pair_switch(self):
        self.install()
        self.updater.stage_local(self.bundle('1.1.0', '2.0.0')[0])
        self.updater.queue()
        with lock(self.root/'runtime.lock', shared=True):
            with self.assertRaises(RuntimeError):
                self.updater.apply_pending()
        self.assertEqual(self.updater.installed()['version'], '1.0.0')

    def test_activation_failure_and_rollback_restore_entire_pair(self):
        self.install()
        self.updater.stage_local(self.bundle('1.1.0', '2.0.0')[0])
        self.updater.queue()
        original = self.updater._pointer
        def fail_once(version):
            original(version)
            if version == '1.1.0':
                raise OSError('power failure')
        with patch.object(self.updater, '_pointer', side_effect=fail_once):
            with self.assertRaises(OSError):
                self.updater.apply_pending()
        self.assertEqual(self.updater.installed()['selection']['backend_version'], '1.0.0')
        self.updater.queue()
        self.updater.apply_pending()
        self.updater.rollback()
        self.assertEqual(self.updater.installed()['selection']['platform_version'], '1.0.0')
        self.assertEqual(self.updater.installed()['selection']['backend_version'], '1.0.0')

    def test_supervisor_applies_after_gui_exit_stops_old_backend_and_reopens(self):
        self.install()
        self.updater.stage_local(self.bundle('1.1.0', '2.0.0')[0])
        spec = importlib.util.spec_from_file_location('robot_update_manager', ROOT/'packaging/runtime/manage.py')
        manager = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(manager)
        log = self.directory/'launch.log'
        with patch.dict(os.environ, {'UPDATE_TEST_LOG': str(log), 'UPDATE_TEST_QUEUE': 'yes'}):
            self.assertEqual(manager.launch(self.updater, self.root/'updates.json'), 0)
        self.assertEqual(log.read_text().splitlines(), ['GUI 1.0.0', 'backend stopped', 'GUI 1.1.0'])

    def test_archive_escape_link_and_checksum_are_rejected(self):
        self.install()
        manifest = self.feed_release()
        (self.feed/'stable'/manifest['archive']).write_bytes(b'corrupt')
        with self.assertRaisesRegex(ValueError, 'checksum'):
            self.updater.stage_latest()
        malicious = self.directory/'malicious.tar.gz'
        with tarfile.open(malicious, 'w:gz') as output:
            entry = tarfile.TarInfo('robot/platform/link')
            entry.type = tarfile.SYMTYPE
            entry.linkname = '../../outside'
            output.addfile(entry)
        with self.assertRaises((ValueError, FileNotFoundError)):
            self.updater.stage_local(malicious)
        self.assertEqual(self.updater.installed()['version'], '1.0.0')

    def test_gitea_discovers_latest_published_complete_system_only(self):
        self.install()
        candidate = self.feed_release()
        config = UpdateConfig(self.root, 'http://gitea.test/owner/repo/', None,
                              product=self.config.product, enabled=True,
                              repository_type='gitea', allow_insecure_http=True)
        updater = PlatformUpdater(config)
        listing = [
            dict(tag_name='paint_tray_dry/platform/v9.0.0', assets=[]),
            dict(tag_name='paint_tray_dry/robot/v3.0.0', draft=True, assets=[]),
            dict(tag_name='paint_tray_dry/robot/v1.1.0', assets=[
                dict(name=name, browser_download_url='http://gitea.test/assets/'+name)
                for name in ('manifest.json', candidate['archive'])]),
        ]
        def fetch(url, destination, limit):
            value = listing if '/releases?' in url else candidate
            destination.write_text(json.dumps(value))
        with patch.object(updater, '_fetch', side_effect=fetch):
            result = updater.check()
        self.assertTrue(result['available'])
        self.assertEqual(result['selection']['backend_version'], '2.0.0')
        self.assertEqual(result['_download_url'], 'http://gitea.test/assets/1.1.0.tar.gz')

    def test_http_requires_explicit_machine_opt_in(self):
        path = self.directory/'config.json'
        raw = dict(install_root=str(self.root), repository_url='http://host/feed/', enabled=True)
        atomic_json(path, raw)
        with self.assertRaises(ValueError):
            UpdateConfig.load(path)
        atomic_json(path, dict(raw, allow_insecure_http=True))
        self.assertTrue(UpdateConfig.load(path).allow_insecure_http)

    def test_token_is_sent_only_to_configured_server(self):
        token = self.directory / 'gitea-token'
        token.write_text('test-token\n')
        updater = PlatformUpdater(replace(self.config, repository_url='http://gitea.test/owner/repo/',
                                         allow_insecure_http=True, token_file=token))
        destination = self.directory / 'download'
        with patch('urllib.request.build_opener') as build:
            build.return_value.open.return_value = io.BytesIO(b'asset')
            updater._fetch('http://gitea.test/assets/file', destination, 100)
            request = build.return_value.open.call_args.args[0]
            self.assertEqual(request.get_header('Authorization'), 'token test-token')
            with self.assertRaisesRegex(ValueError, 'configured server'):
                updater._fetch('http://other.test/asset', destination, 100)
            self.assertEqual(build.return_value.open.call_count, 1)
        self.assertEqual(destination.read_bytes(), b'asset')

    def test_authenticated_redirect_cannot_leak_token(self):
        from urllib.request import Request
        from src.engine.updates.updater import _HttpsRedirect
        request = Request('http://gitea.test/asset', headers={'Authorization': 'token test-token'})
        with self.assertRaisesRegex(ValueError, 'configured server'):
            _HttpsRedirect(True).redirect_request(request, None, 302, 'redirect', {}, 'http://other.test/file')

    def test_packaged_gitea_source_can_seed_new_install(self):
        raw = json.loads((ROOT / 'config/update_sources/paint_tray_dry.json').read_text())
        raw['install_root'] = str(self.root)
        path = self.directory / 'updates.json'
        atomic_json(path, raw)
        config = UpdateConfig.load(path)
        self.assertTrue(config.enabled)
        self.assertEqual(config.repository_type, 'gitea')
