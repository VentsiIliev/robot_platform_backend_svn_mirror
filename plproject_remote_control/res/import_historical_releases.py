#!/usr/bin/env python3
"""Copy pinned historical release assets into the enclosing GitHub mirror."""
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import urllib.request


def run(*args):
    return subprocess.run(args, check=True, text=True, capture_output=True).stdout


def verify(path, digest):
    with path.open('rb') as stream:
        actual = hashlib.file_digest(stream, 'sha256').hexdigest()
    if actual != digest:
        raise ValueError(f'Checksum mismatch for {path.name}')


def main():
    repository = os.environ['GITHUB_REPOSITORY']
    if repository != 'VentsiIliev/robot_platform_backend_svn_mirror':
        raise ValueError('Release import is restricted to the SVN GitHub mirror')
    manifest = json.loads((Path(__file__).resolve().parents[1] / 'release-import.json').read_text())
    for release in manifest['releases']:
        with tempfile.TemporaryDirectory(prefix='plproject-release-import-') as folder:
            directory = Path(folder)
            # Validate every original asset before publishing any of this release.
            for asset in release['assets']:
                target = directory / asset['name']
                with urllib.request.urlopen(asset['source_url'], timeout=120) as response:
                    with target.open('wb') as output:
                        shutil.copyfileobj(response, output)
                verify(target, asset['sha256'])
            result = subprocess.run(['gh', 'release', 'view', release['tag'],
                                     '--repo', repository, '--json', 'assets'],
                                    text=True, capture_output=True)
            if result.returncode:
                notes = directory / 'notes.md'
                notes.write_text(
                    'Historical PL PROJECT release imported into the SVN GitHub mirror.\n\n'
                    f"Original source commit: `{release['original_source_commit']}`.\n"
                    'Binary assets were copied unchanged and their SHA-256 hashes verified.\n'
                    'The mirror tag identifies the SVN source import; the original build '
                    'commit belongs to the historical standalone repository.\n')
                run('gh', 'release', 'create', release['tag'], '--repo', repository,
                    '--target', os.environ['GITHUB_SHA'], '--latest=false',
                    '--title', release['title'], '--notes-file', str(notes))
                existing = set()
            else:
                existing = {item['name'] for item in json.loads(result.stdout)['assets']}
            for asset in release['assets']:
                if asset['name'] in existing:
                    saved = directory / 'existing'
                    saved.mkdir(exist_ok=True)
                    run('gh', 'release', 'download', release['tag'], '--repo', repository,
                        '--pattern', asset['name'], '--dir', str(saved))
                    verify(saved / asset['name'], asset['sha256'])
                else:
                    run('gh', 'release', 'upload', release['tag'],
                        str(directory / asset['name']), '--repo', repository)
            print(f"Verified imported release {release['tag']}", flush=True)


if __name__ == '__main__':
    main()
