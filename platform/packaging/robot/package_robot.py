#!/usr/bin/env python3
"""Assemble the exact published platform/backend pair from platform.json."""
import argparse
import json
from pathlib import Path
import platform
import shutil
import subprocess
import tempfile

import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / 'shared'))
from release_common import ROOT, selection, component, extract, write_json, digest, archive_bundle, source_identity


def assemble(target, selected, bundle):
    manifests = {}
    for kind in ('platform', 'backend'):
        manifest, archive = component(target, kind, selected)
        manifests[kind] = manifest
        extract(archive, bundle)
    executable = manifests['platform']['executable']
    if Path(executable).name != executable or not (bundle / 'platform' / executable).is_file():
        raise ValueError('Missing platform executable')
    runtime_path = bundle / 'platform/_internal/config/platform.json'
    runtime = json.loads(runtime_path.read_text())
    entry = runtime.get('robot_systems', {}).get(target)
    # Component version pins are independent of the eventual overall release version.
    for key in ('robot_driver', 'backend', 'backend_profile'):
        if not entry or entry.get(key) != selected[key]:
            raise ValueError(f'Packaged platform configuration mismatch: {key}')
    if runtime.get('robot_system') != target or runtime.get('supported_robot_systems') != [target]:
        raise ValueError('Packaged platform system selection mismatch')
    runtime['robot_systems'] = {target: selected}
    runtime['ros_backend'] = {**runtime.get('ros_backend', {}), 'auto_launch': True, 'auto_stop': True}
    runtime['ros_backend'].pop('launch_script', None)
    runtime['ros_backend'].pop('stop_script', None)
    write_json(runtime_path, runtime)
    backend = json.loads((bundle / 'backend/manifest.json').read_text())
    for key in ('target', 'version', 'backend', 'profile', 'ros_distro'):
        if backend.get(key) != manifests['backend'].get(key):
            raise ValueError(f'Backend archive identity mismatch: {key}')
    for action in ('launch', 'stop'):
        if not (bundle / 'backend' / (action + '.sh')).is_file():
            raise ValueError(f'Missing backend {action} script')
    launcher = bundle / 'launch.sh'
    launcher.write_text('#!/usr/bin/env bash\nset -euo pipefail\nROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"\nexec "$ROOT/platform/' + executable + '" "$@"\n')
    launcher.chmod(0o755)
    shutil.copy2(Path(__file__).with_name('install_robot.py'), bundle / 'install.py')
    manifest = dict(format=1, component='robot', target=target, version=selected['release_version'],
                    architecture=platform.machine(), os='ubuntu-24.04', selection=selected, components=manifests)
    write_json(bundle / 'manifest.json', manifest)
    subprocess.run(['bash', '-n', str(launcher)], check=True)
    return manifest


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('target')
    parser.add_argument('--verify-only', action='store_true')
    args = parser.parse_args()
    try:
        selected = selection(args.target)
        output = ROOT / 'releases' / args.target / 'robot' / selected['release_version']
        if output.exists() and not args.verify_only:
            raise ValueError(f'Release already exists: {output}')
        identity = {} if args.verify_only else source_identity()
        with tempfile.TemporaryDirectory(prefix='robot-release-') as temporary:
            bundle = Path(temporary) / 'robot'
            bundle.mkdir()
            manifest = assemble(args.target, selected, bundle)
            manifest.update(identity)
            write_json(bundle / "manifest.json", manifest)
            if args.verify_only:
                print('Exact component pair verified; no robot release created')
                return
            output.parent.mkdir(parents=True, exist_ok=True)
            with tempfile.TemporaryDirectory(dir=output.parent, prefix='.release-') as staging:
                staged = Path(staging)
                archive = staged / f'{args.target}-robot-{selected["release_version"]}-{platform.machine()}.tar.gz'
                archive_bundle(bundle, archive, 'robot')
                manifest.update(archive=archive.name, sha256=digest(archive))
                write_json(staged / 'manifest.json', manifest)
                (staged / (archive.name + '.sha256')).write_text(f'{manifest["sha256"]}  {archive.name}\n')
                staged.rename(output)
        print(output)
    except (ValueError, RuntimeError, FileNotFoundError) as exc:
        parser.error(str(exc))


if __name__ == '__main__':
    main()
