#!/usr/bin/env python3
"""Install an extracted robot release atomically; never start robot hardware."""
import argparse
import fcntl
import json
import os
from pathlib import Path
import platform
import re
import shutil
import subprocess
import tempfile


def activate(root, version):
    release = root / 'releases' / version
    if not (release / 'manifest.json').is_file():
        raise ValueError(f'Release not installed: {version}')
    temporary = root / '.current-new'
    temporary.unlink(missing_ok=True)
    temporary.symlink_to(Path('releases') / version)
    os.replace(temporary, root / 'current')


def install(bundle, root, manifest):
    output = root / 'releases' / manifest['version']
    if output.exists():
        if json.loads((output / 'manifest.json').read_text()) != manifest:
            raise ValueError('Installed version has a different manifest; choose a new version')
        activate(root, manifest['version'])
        return
    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=output.parent, prefix='.install-') as temporary:
        staging = Path(temporary) / 'robot'
        shutil.copytree(bundle, staging, symlinks=True)
        for path in staging.rglob('*'):
            if path.is_symlink() and not path.resolve(strict=True).is_relative_to(staging):
                raise ValueError(f'External runtime link: {path}')
        if not (staging / 'launch.sh').is_file() or not (staging / 'backend/launch.sh').is_file():
            raise ValueError('Incomplete robot release')
        staging.rename(output)
    product = json.loads((bundle / 'platform/_internal/config/release-target.json').read_text())['product']
    config = root / 'updates.json'
    if not config.exists():
        source = bundle / 'platform/_internal/config/update-source' / (manifest['target'] + '.json')
        seed = json.loads(source.read_text()) if source.is_file() else {'enabled': False}
        seed.update(install_root=str(root), product=product)
        config.write_text(json.dumps(seed, indent=2) + '\n')
    # Install a release-owned supervisor: it activates pending updates after GUI exit.
    payload = bundle / 'platform/installation/updater'
    if payload.is_dir():
        versions = root / 'updater-tools'
        versions.mkdir(exist_ok=True)
        with tempfile.TemporaryDirectory(dir=versions, prefix='.tools-') as temporary:
            staged = Path(temporary) / 'tools'
            shutil.copytree(payload, staged)
            destination = versions / manifest['version']
            if not destination.exists():
                staged.rename(destination)
        tools = root / 'tools'
        if tools.exists() and not tools.is_symlink():
            raise ValueError('Unexpected updater tools directory')
        pointer = root / '.tools-new'
        pointer.unlink(missing_ok=True)
        pointer.symlink_to(destination.relative_to(root))
        os.replace(pointer, tools)
    # Hold a shared lock throughout the GUI lifetime; installation needs exclusive access.
    wrapper = root / 'launch.sh'
    wrapper.write_text('#!/usr/bin/env bash\nset -euo pipefail\nROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"\nexec 9>"$ROOT/runtime.lock"\nflock -s 9\nexport ROBOT_PLATFORM_DATA_ROOT="$ROOT/data"\nexport ROBOT_PLATFORM_UPDATE_CONFIG="$ROOT/updates.json"\nexec "$ROOT/current/launch.sh" "$@"\n')
    if (root / 'tools/manage.py').is_file():
        wrapper.write_text('#!/usr/bin/env bash\nset -euo pipefail\nROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"\nexport ROBOT_PLATFORM_DATA_ROOT="$ROOT/data"\nexport ROBOT_PLATFORM_UPDATE_CONFIG="$ROOT/updates.json"\nif [[ $# -gt 0 ]]; then\n  exec 9>"$ROOT/runtime.lock"\n  flock -s 9\n  exec "$ROOT/current/launch.sh" "$@"\nfi\nexec /usr/bin/python3 "$ROOT/tools/manage.py" --config "$ROOT/updates.json" launch\n')
    wrapper.chmod(0o755)
    (root / 'data').mkdir(exist_ok=True)
    activate(root, manifest['version'])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, help='Optional installation directory')
    parser.add_argument('--activate', help='Switch to a previously installed version')
    parser.add_argument('--kiosk', choices=('enabled', 'manual', 'off'))
    parser.add_argument('--setup-system', action='store_true')
    parser.add_argument('--skip-system-setup', action='store_true',
                        help='Install software only, for isolated release verification')
    args = parser.parse_args()
    if args.skip_system_setup and (args.setup_system or args.kiosk is not None):
        parser.error('--skip-system-setup cannot be combined with system setup options')
    bundle = Path(__file__).resolve().parent
    manifest = json.loads((bundle / 'manifest.json').read_text())
    for key in ('target', 'version'):
        pattern = r'[a-z][a-z0-9_]*' if key == 'target' else r'[0-9]+\.[0-9]+\.[0-9]+'
        if not re.fullmatch(pattern, manifest[key]):
            parser.error(f'Invalid {key}')
    if manifest['architecture'] != platform.machine():
        parser.error('CPU architecture mismatch')
    if manifest['os'] != 'ubuntu-24.04' or 'VERSION_ID="24.04"' not in Path('/etc/os-release').read_text():
        parser.error('Ubuntu 24.04 is required')
    root = (args.root or Path.home() / '.local/share/robot-releases' / manifest['target']).resolve()
    root.mkdir(parents=True, exist_ok=True)
    try:
        with (root / 'runtime.lock').open('a') as guard:
            try:
                fcntl.flock(guard, fcntl.LOCK_EX | fcntl.LOCK_NB)
            except BlockingIOError:
                raise ValueError('Robot application is running; close it before installing or activating a release')
            if args.activate:
                if not re.fullmatch(r'[0-9]+\.[0-9]+\.[0-9]+', args.activate):
                    raise ValueError('Activation version must be major.minor.patch')
                installed = json.loads((root / 'releases' / args.activate / 'manifest.json').read_text())
                if installed['target'] != manifest['target']:
                    raise ValueError('Installed target mismatch')
                activate(root, args.activate)
            else:
                first_install = not (root / 'current').exists()
                if not args.skip_system_setup:
                    # Persist setup intent before activation so a failed install is retryable.
                    setup_state = root / 'update-state/system-setup.json'
                    if first_install and not setup_state.exists():
                        setup_state.parent.mkdir(parents=True, exist_ok=True)
                        temporary_state = setup_state.with_suffix('.tmp')
                        temporary_state.write_text(json.dumps({'complete': False, 'kiosk': args.kiosk or 'enabled'}))
                        os.replace(temporary_state, setup_state)
                    pending_setup = json.loads(setup_state.read_text()) if setup_state.exists() else None
                    retrying_choice = (pending_setup is not None and not pending_setup['complete']
                                       and pending_setup['kiosk'] == args.kiosk)
                    if args.kiosk is not None and not (first_install or args.setup_system or retrying_choice):
                        raise ValueError('Use --setup-system to change kiosk on an existing installation')
                install(bundle, root, manifest)
                if not args.skip_system_setup:
                    helper = root / 'current/platform/installation/system-setup.py'
                    if not helper.is_file():
                        raise ValueError('System setup payload missing; rebuild the platform release')
                    # Provision under the existing exclusive runtime lock.
                    import importlib.util
                    spec = importlib.util.spec_from_file_location('robot_system_setup', helper)
                    setup = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(setup)
                    state = setup.prepare_system_setup(root, first_install=first_install,
                                                       mode=args.kiosk, setup_system=args.setup_system)
                    setup.finish_system_setup(root, None, state, launcher=root / 'launch.sh')
        if not args.skip_system_setup and (root / 'tools/src/engine/updates/service_install.py').is_file():
            subprocess.run(['/usr/bin/python3', str(root / 'tools/manage.py'),
                            '--config', str(root / 'updates.json'), 'install-service'], check=True)
        print(f'Installed launcher: {root / "launch.sh"}')
    except (ValueError, RuntimeError, OSError, subprocess.SubprocessError) as exc:
        parser.error(str(exc))


if __name__ == '__main__':
    main()
