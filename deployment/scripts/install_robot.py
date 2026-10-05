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
    (root / 'updates.json').write_text(json.dumps(dict(install_root=str(root), product=product, enabled=False)))
    # Hold a shared lock throughout the GUI lifetime; installation needs exclusive access.
    wrapper = root / 'launch.sh'
    wrapper.write_text('#!/usr/bin/env bash\nset -euo pipefail\nROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"\nexec 9>"$ROOT/runtime.lock"\nflock -s 9\nexport ROBOT_PLATFORM_DATA_ROOT="$ROOT/data"\nexport ROBOT_PLATFORM_UPDATE_CONFIG="$ROOT/updates.json"\nexec "$ROOT/current/launch.sh" "$@"\n')
    wrapper.chmod(0o755)
    (root / 'data').mkdir(exist_ok=True)
    activate(root, manifest['version'])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, help='Optional installation directory')
    parser.add_argument('--activate', help='Switch to a previously installed version')
    args = parser.parse_args()
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
                install(bundle, root, manifest)
        print(f'Installed launcher: {root / "launch.sh"}')
    except (ValueError, FileNotFoundError) as exc:
        parser.error(str(exc))


if __name__ == '__main__':
    main()
