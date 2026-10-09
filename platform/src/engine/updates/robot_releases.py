"""Validate and extract complete robot releases without running backend hardware."""
import json
import platform
import re
import shutil
import tarfile
from pathlib import Path, PurePosixPath


def validate_robot_manifest(raw, product):
    from .releases import version_tuple
    if not isinstance(raw, dict) or raw.get('format') != 1 or raw.get('component') != 'robot':
        raise ValueError('Expected a complete robot release')
    target = raw.get('target', '')
    if not isinstance(target, str) or not re.fullmatch(r'[a-z][a-z0-9_]*', target):
        raise ValueError('Invalid robot release target')
    version_tuple(raw.get('version'))
    components = raw.get('components', {})
    selection = raw.get('selection', {})
    if not isinstance(components, dict) or not isinstance(selection, dict):
        raise ValueError('Invalid robot component selection')
    for kind in ('platform', 'backend'):
        component = components.get(kind)
        if not isinstance(component, dict):
            raise ValueError('Robot release must contain platform and backend components')
        for key, expected in {'component': kind, 'target': target,
                              'version': selection.get(kind + '_version'),
                              'architecture': platform.machine(), 'os': 'ubuntu-24.04',
                              'backend': selection.get('backend'),
                              'profile': selection.get('backend_profile')}.items():
            if component.get(key) != expected or expected is None:
                raise ValueError(f'Robot {kind} component mismatch: {key}')
        version_tuple(component['version'])
    executable = components['platform'].get('executable', '')
    if not isinstance(executable, str) or not re.fullmatch(r'[a-z][a-z0-9_-]*', executable):
        raise ValueError('Invalid robot platform executable')
    if executable != product or raw.get('product', product) != product:
        raise ValueError('Wrong robot release product')
    if components['platform'].get('robot_driver') != selection.get('robot_driver'):
        raise ValueError('Robot driver selection mismatch')
    if selection.get('release_version') != raw['version']:
        raise ValueError('Robot release version selection mismatch')
    if raw.get('architecture') != platform.machine() or raw.get('os') != 'ubuntu-24.04':
        raise ValueError('Robot release requires matching CPU architecture and Ubuntu 24.04')
    info = platform.freedesktop_os_release()
    if info.get('ID') != 'ubuntu' or info.get('VERSION_ID') != '24.04':
        raise ValueError('This release requires Ubuntu 24.04')
    # Old combined manifests have no platform-updater identity fields.
    # Normalize in memory; never rewrite the packaged or installed configuration.
    result = dict(raw, product=product, robot_system=target,
                  profile=selection['backend_profile'], storage_system=target,
                  executable=executable, storage_schema=raw.get('storage_schema', 1),
                  channel=raw.get('channel', 'stable'))
    if not isinstance(result['storage_schema'], int) or isinstance(result['storage_schema'], bool) or result['storage_schema'] < 1:
        raise ValueError('storage_schema must be a positive integer')
    return result


def validate_robot_payload(root, manifest):
    marker = json.loads((root / 'platform/_internal/config/release-target.json').read_text())
    if marker.get('product') != manifest['product'] or marker.get('robot_system') != manifest['target']:
        raise ValueError('Bundled robot target mismatch')
    startup = json.loads((root / 'platform/_internal/config/platform.json').read_text())
    if startup.get('robot_system') != manifest['target'] or startup.get('supported_robot_systems') != [manifest['target']]:
        raise ValueError('Bundled startup target mismatch')
    if startup.get('robot_systems', {}).get(manifest['target']) != manifest['selection']:
        raise ValueError('Bundled robot component selection mismatch')
    backend = json.loads((root / 'backend/manifest.json').read_text())
    for key in ('component', 'target', 'version', 'architecture', 'os', 'backend', 'profile', 'ros_distro'):
        if backend.get(key) != manifest['components']['backend'].get(key):
            raise ValueError('Bundled backend identity mismatch: ' + key)
    for name in ('launch.sh', 'backend/launch.sh', 'backend/stop.sh',
                 'platform/' + manifest['executable']):
        path = root / name
        if not path.is_file() or not path.stat().st_mode & 0o111:
            raise ValueError('Missing robot executable: ' + name)


def extract_robot_release(archive: Path, destination: Path, max_bytes: int):
    """Allow only confined relative runtime links; reject mutable platform data."""
    destination.mkdir(parents=True, exist_ok=False)
    try:
        links = []
        seen = set()
        total = 0
        with tarfile.open(archive, 'r:gz') as bundle:
            for member in bundle:
                path = PurePosixPath(member.name)
                if path.is_absolute() or '..' in path.parts or not path.parts or '\\' in member.name:
                    raise ValueError('Unsafe robot archive path')
                if path.parts[0] != 'robot':
                    raise ValueError('Unexpected robot archive root')
                relative = path.parts[1:]
                if not relative:
                    if not member.isdir():
                        raise ValueError('Invalid robot archive root')
                    continue
                if relative[0] not in {'platform', 'backend', 'manifest.json', 'launch.sh', 'install.py', 'migrations'}:
                    raise ValueError('Unexpected robot archive content')
                if member.name in seen or not (member.isdir() or member.isfile() or member.issym()):
                    raise ValueError('Robot archive duplicates, hard links and special files are forbidden')
                seen.add(member.name)
                total += member.size
                if total > max_bytes or len(seen) > 100000:
                    raise ValueError('Release extraction limit exceeded')
                if relative[0] == 'platform' and any(p in {'storage', 'profiles'} for p in relative) and 'translations' not in relative and not member.isdir():
                    raise ValueError('Robot release contains mutable platform storage')
                target = destination.joinpath(*relative)
                if member.issym():
                    link = PurePosixPath(member.linkname)
                    if link.is_absolute() or '\\' in member.linkname:
                        raise ValueError('Unsafe robot runtime link')
                    links.append((target, member.linkname))
                elif member.isdir():
                    target.mkdir(parents=True, exist_ok=True)
                else:
                    target.parent.mkdir(parents=True, exist_ok=True)
                    with bundle.extractfile(member) as source, target.open('xb') as output:
                        shutil.copyfileobj(source, output)
                    target.chmod(0o755 if member.mode & 0o111 else 0o644)
        for target, link in links:
            target.parent.mkdir(parents=True, exist_ok=True)
            target.symlink_to(link)
        for target, _ in links:
            if not target.resolve(strict=True).is_relative_to(destination.resolve()):
                raise ValueError('Robot runtime link leaves release')
    except BaseException:
        shutil.rmtree(destination)
        raise
