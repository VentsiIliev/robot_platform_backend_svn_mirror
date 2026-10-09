#!/usr/bin/env python3
"""Install or run a combined robot release using platform.json selection."""
import argparse
import json
from pathlib import Path
import subprocess
import tempfile
from release_common import ROOT, selection, digest, extract


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=('install', 'run'))
    parser.add_argument('target')
    args, remaining = parser.parse_known_args()
    try:
        selected = selection(args.target)
        root = Path.home() / '.local/share/robot-releases' / args.target
        if args.action == 'run':
            launcher = root / 'launch.sh'
            if not launcher.is_file():
                raise ValueError(f'Combined robot release is not installed. Extract a combined robot archive and run python3 robot/install.py first. Expected: {launcher}')
            manifest = json.loads((root / 'current/manifest.json').read_text())
            if manifest.get('target') != args.target or manifest.get('component') != 'robot':
                raise ValueError('Installed combined release target mismatch')
            subprocess.run([str(launcher), *remaining], check=True)
            return
        directory = ROOT / 'releases' / args.target / 'robot' / selected['release_version']
        manifest = json.loads((directory / 'manifest.json').read_text())
        if manifest.get('target') != args.target or manifest.get('component') != 'robot' or manifest.get('version') != selected['release_version']:
            raise ValueError('Combined release manifest mismatch')
        name = manifest['archive']
        if Path(name).name != name:
            raise ValueError('Invalid archive name')
        archive = directory / name
        if digest(archive) != manifest['sha256']:
            raise ValueError('Combined release archive checksum mismatch')
        with tempfile.TemporaryDirectory(prefix='install-robot-release-') as temporary:
            destination = Path(temporary)
            extract(archive, destination)
            subprocess.run(['/usr/bin/python3', '-B', str(destination / 'robot/install.py'), *remaining], check=True)
    except (ValueError, RuntimeError, FileNotFoundError) as exc:
        parser.error(str(exc))


if __name__ == '__main__':
    main()
