#!/usr/bin/env python3
"""Run the existing platform build wrapper and publish its verified artifacts."""
import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
from urllib.parse import quote

PLATFORM = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(PLATFORM.parent / 'deployment/scripts'))
import release_common as common
from gitea_release import GiteaPublisher
from src.engine.updates.releases import version_tuple


def prepare_artifacts(output, target, version, identity):
    directory = output / target / 'stable'
    latest = directory / 'latest.json'
    manifest = json.loads(latest.read_text())
    if (manifest.get('robot_system'), manifest.get('version'), str(manifest.get('source_svn_revision'))) != (target, version, str(identity['source_svn_revision'])):
        raise ValueError('Packaged release does not match the selected system/version/SVN revision')
    if Path(manifest['archive']).name != manifest['archive']:
        raise ValueError('Invalid archive filename')
    archive = directory / manifest['archive']
    if common.digest(archive) != manifest['sha256']:
        raise ValueError('Platform archive checksum mismatch')
    kit = output / target / f'{manifest["product"]}-installer-{version}-{manifest["architecture"]}.tar.gz'
    files = [archive, kit, latest]
    signature = latest.with_name('latest.json.sig')
    if signature.exists():
        files.append(signature)
    hashes = {path.name: common.digest(path) for path in files}
    receipt = directory / 'release-manifest.json'
    payload = dict(target=target, version=version, **identity, files=hashes)
    if receipt.exists():
        if json.loads(receipt.read_text()) != payload:
            raise ValueError('Cached release differs from its recorded source/artifacts')
    else:
        receipt.write_text(json.dumps(payload, indent=2) + '\n')
    sums = directory / 'SHA256SUMS'
    sums.write_text(''.join(f'{value}  {name}\n' for name, value in hashes.items()))
    return [*files, receipt, sums]


def publish(target, output, repository_url, token, notes='', signing_key=None):
    identity = common.source_identity()
    if not identity.get('source_svn_revision'):
        raise ValueError('Publish source to SVN first, then push the SVN-generated commit to Gitea')
    version = (PLATFORM / 'src/robot_systems' / target / 'VERSION').read_text().strip()
    version_tuple(version)
    tag = f'{target}/platform/v{version}'
    publisher = GiteaPublisher(repository_url, token)
    repository = publisher.request('GET', '')
    if not repository or not repository.get('permissions', {}).get('push'):
        raise ValueError('Gitea repository write access is required')
    remote_tag = publisher.request('GET', '/tags/' + quote(tag, safe=''))
    if remote_tag and remote_tag['commit']['sha'] != identity['source_git_commit']:
        raise ValueError('Release version is already tagged at another commit; increment VERSION')
    cached = output / target / 'stable/release-manifest.json'
    if not cached.exists():
        command = [str(PLATFORM / 'src/robot_systems' / target / 'build_release.sh'),
                   '--output', str(output), '--svn-revision', str(identity['source_svn_revision'])]
        if signing_key:
            command += ['--signing-key', str(signing_key)]
        subprocess.run(command, cwd=PLATFORM, check=True)
    files = prepare_artifacts(output, target, version, identity)
    if not remote_tag:
        publisher.request('POST', '/tags', json=dict(tag_name=tag, target=identity['source_git_commit'], message=f'{tag}; SVN r{identity["source_svn_revision"]}'))
    marker = f'Platform release SHA256: {common.digest(output / target / "stable/release-manifest.json")}'
    body = f'{notes.strip()}\n\nPlatform-only release built by `{target}/build_release.sh`.\nSVN revision: {identity["source_svn_revision"]}\nSource commit: {identity["source_git_commit"]}\n{marker}\n'
    return publisher.publish_assets(tag, f'{target} platform {version}', body, marker, files, common.digest)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('target', choices=('paint_tray_dry',))
    parser.add_argument('--output', type=Path, default=PLATFORM / 'dist/gitea-platform-release')
    parser.add_argument('--repository-url', default=os.environ.get('GITEA_REPOSITORY_URL'))
    parser.add_argument('--notes-file', type=Path)
    parser.add_argument('--signing-key', type=Path, help='Optional existing OpenSSL signing key for remote-update metadata')
    args = parser.parse_args()
    try:
        token = os.environ.get('GITEA_TOKEN')
        if not token or not args.repository_url:
            raise ValueError('GITEA_TOKEN and GITEA_REPOSITORY_URL are required')
        notes = args.notes_file.read_text() if args.notes_file else ''
        print(publish(args.target, args.output.resolve(), args.repository_url, token, notes, args.signing_key))
    except (ValueError, OSError, KeyError, subprocess.CalledProcessError) as exc:
        parser.exit(1, f'Platform publication failed: {exc}\n')


if __name__ == '__main__':
    main()
