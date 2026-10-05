#!/usr/bin/env python3
"""Create local annotated Git tags for the exact released component commits."""
import argparse
import json
import subprocess
from release_common import ROOT, selection, digest


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('target')
    args = parser.parse_args()
    try:
        selected = selection(args.target)
        directory = ROOT / 'releases' / args.target / 'robot' / selected['release_version']
        manifest = json.loads((directory / 'manifest.json').read_text())
        if digest(directory / manifest['archive']) != manifest['sha256']:
            raise ValueError('Robot archive checksum mismatch')
        identities = {**manifest['components'], 'robot': manifest}
        tags = []
        for kind, identity in identities.items():
            name = f'{args.target}/{kind}/v{identity["version"]}'
            commit = identity['source_git_commit']
            subprocess.run(['git', 'cat-file', '-e', commit + '^{commit}'], cwd=ROOT, check=True)
            existing = subprocess.run(['git', 'rev-parse', '--verify', f'refs/tags/{name}^{{commit}}'], cwd=ROOT, capture_output=True, text=True)
            if existing.returncode == 0:
                if existing.stdout.strip() != commit:
                    raise ValueError(f'Tag already points to a different commit: {name}')
            else:
                tags.append((name, commit))
        for name, commit in tags:
            subprocess.run(['git', 'tag', '-a', name, commit, '-m', f'{name}\nRobot archive SHA256: {manifest["sha256"]}'], cwd=ROOT, check=True)
        print('Release tags verified/created locally; no remote publication performed')
    except (ValueError, FileNotFoundError, KeyError) as exc:
        parser.error(str(exc))


if __name__ == '__main__':
    main()
