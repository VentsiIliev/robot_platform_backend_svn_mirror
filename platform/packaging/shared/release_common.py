"""Shared configuration and immutable component archive handling."""
import hashlib
import json
from pathlib import Path
import platform
import subprocess
import sys
import tarfile

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / 'platform'))
from src.bootstrap.startup_config import load_robot_system_config


def selection(target):
    payload = json.loads((ROOT / 'platform/config/platform.json').read_text())
    if target not in payload['supported_robot_systems']:
        raise ValueError(f'Unsupported robot system: {target}')
    return load_robot_system_config(payload, target)


def source_identity():
    if subprocess.check_output(['git', 'status', '--porcelain'], cwd=ROOT, text=True).strip():
        raise ValueError('Commit source changes before producing a release; working tree is dirty')
    commit = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    import re
    message = subprocess.check_output(['git', 'log', '-1', '--format=%B'], cwd=ROOT, text=True)
    revision = re.search(r'git-svn-id: .*@(\d+) ', message)
    return dict(source_git_commit=commit, source_svn_revision=revision.group(1) if revision else None)


def digest(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def write_json(path, value):
    path.write_text(json.dumps(value, indent=2) + '\n')


def component(target, kind, selected):
    directory = ROOT / 'releases' / target / kind / selected[f'{kind}_version']
    path = directory / 'manifest.json'
    if not path.is_file():
        raise ValueError(f'Missing {kind} version {selected[kind + "_version"]}: {path}. Build this component first.')
    manifest = json.loads(path.read_text())
    for key, expected in dict(component=kind, target=target, version=selected[f'{kind}_version'], architecture=platform.machine(), os='ubuntu-24.04').items():
        if manifest.get(key) != expected:
            raise ValueError(f'{kind} manifest mismatch: {key}')
    for key in ('backend', 'profile'):
        expected = selected['backend' if key == 'backend' else 'backend_profile']
        if manifest.get(key) != expected:
            raise ValueError(f'{kind} manifest mismatch: {key}')
    if manifest.get('robot_driver') != selected['robot_driver'] and kind == 'platform':
        raise ValueError('Platform robot_driver mismatch')
    name = manifest['archive']
    if Path(name).name != name:
        raise ValueError('Invalid component archive name')
    archive = directory / name
    if digest(archive) != manifest['sha256']:
        raise ValueError(f'{kind} checksum mismatch: {archive}')
    return manifest, archive


def extract(archive, destination):
    # Python's data filter rejects traversal, devices and links outside destination.
    with tarfile.open(archive) as source:
        source.extractall(destination, filter='data')


def archive_bundle(bundle, archive, name):
    with tarfile.open(archive, 'w:gz') as destination:
        destination.add(bundle, arcname=name, filter=lambda member: None if '__pycache__' in Path(member.name).parts else member)
