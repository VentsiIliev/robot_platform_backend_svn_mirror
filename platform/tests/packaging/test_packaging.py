"""Hardware-free integration checks for component assembly and installation."""
import fcntl
import importlib.util
import io
import json
from pathlib import Path
import platform
import subprocess
import sys
import tarfile
import tempfile
import unittest
from unittest.mock import patch

PLATFORM = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PLATFORM / 'packaging/shared'))
sys.path.insert(0, str(PLATFORM / 'packaging/robot'))
import release_common as common
import package_robot
import install_robot


class PackagingTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.selected = dict(robot_driver='zeroerr', backend='zeroerr', backend_profile='paint_short_links',
                             release_version='2.0.0', platform_version='1.1.0', backend_version='1.0.0')
        self.target = 'paint_tray_dry'
        config = self.root / 'platform/config'
        config.mkdir(parents=True)
        common.write_json(config / 'platform.json', dict(robot_system=self.target, supported_robot_systems=[self.target], robot_systems={self.target: self.selected}))
        self.patcher = patch.object(common, 'ROOT', self.root)
        self.patcher.start()
        self.addCleanup(self.patcher.stop)
        for kind in ('platform', 'backend'):
            directory = self.root / 'releases' / self.target / kind / self.selected[kind + '_version']
            directory.mkdir(parents=True)
            archive = directory / 'component.tar.gz'
            manifest = dict(format=1, component=kind, target=self.target, version=self.selected[kind + '_version'],
                            backend='zeroerr', profile='paint_short_links', architecture=platform.machine(), os='ubuntu-24.04', ros_distro='jazzy', robot_driver='zeroerr', executable='app')
            if kind == 'platform':
                runtime = dict(robot_system=self.target, supported_robot_systems=[self.target], robot_systems={self.target:self.selected})
                files = {'platform/app': b'#!/bin/sh\nexit 0\n', 'platform/_internal/config/release-target.json': b'{"product":"paint-tray-dry-robot"}', 'platform/_internal/config/platform.json': json.dumps(runtime).encode()}
            else:
                files = {'backend/launch.sh': b'#!/bin/sh\nexit 0\n', 'backend/stop.sh': b'#!/bin/sh\nexit 0\n', 'backend/manifest.json': json.dumps(manifest).encode()}
            with tarfile.open(archive, 'w:gz') as dest:
                for name, data in files.items():
                    item = tarfile.TarInfo(name)
                    item.mode=0o755
                    item.size=len(data)
                    dest.addfile(item, io.BytesIO(data))
            manifest.update(archive=archive.name, sha256=common.digest(archive))
            common.write_json(directory / 'manifest.json', manifest)

    def test_missing_exact_version_fails(self):
        selected = {**self.selected, 'backend_version': '9.0.0'}
        with self.assertRaisesRegex(ValueError, 'Missing backend version 9.0.0'):
            common.component(self.target, 'backend', selected)

    def test_checksum_and_profile_mismatch_fail(self):
        path = self.root / 'releases' / self.target / 'backend/1.0.0/manifest.json'
        manifest = json.loads(path.read_text())
        for key, value, message in [('sha256', 'bad', 'checksum mismatch'), ('profile', 'wrong', 'manifest mismatch: profile')]:
            common.write_json(path, {**manifest, key: value})
            with self.assertRaisesRegex(ValueError, message):
                common.component(self.target, 'backend', self.selected)

    def test_assembly_install_and_rollback_preserve_data(self):
        bundle = self.root / 'bundle'
        bundle.mkdir()
        manifest = package_robot.assemble(self.target, self.selected, bundle)
        runtime = json.loads((bundle / 'platform/_internal/config/platform.json').read_text())
        self.assertEqual(runtime['robot_systems'][self.target], self.selected)
        install_root = self.root / 'installed'
        install_root.mkdir()
        install_robot.install(bundle, install_root, manifest)
        data = install_root / 'data/calibration.json'
        data.write_text('machine calibration')
        next_manifest = {**manifest, 'version': '2.0.1'}
        common.write_json(bundle / 'manifest.json', next_manifest)
        install_robot.install(bundle, install_root, next_manifest)
        self.assertEqual((install_root / 'current').resolve().name, '2.0.1')
        install_robot.activate(install_root, '2.0.0')
        self.assertEqual((install_root / 'current').resolve().name, '2.0.0')
        self.assertEqual(data.read_text(), 'machine calibration')
        with (install_root / 'runtime.lock').open('a') as guard:
            fcntl.flock(guard, fcntl.LOCK_SH)
            result = subprocess.run([sys.executable, str(bundle / 'install.py'), '--root', str(install_root)], capture_output=True, text=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('application is running', result.stderr)

    def test_archive_traversal_rejected(self):
        archive = self.root / 'evil.tar.gz'
        with tarfile.open(archive, 'w:gz') as dest:
            item = tarfile.TarInfo('../escape')
            item.size=1
            dest.addfile(item, io.BytesIO(b'x'))
        with self.assertRaises(tarfile.FilterError):
            common.extract(archive, self.root / 'destination')


if __name__ == '__main__':
    unittest.main()
