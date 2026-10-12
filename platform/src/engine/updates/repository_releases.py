"""Shared complete-release selection for repository-specific API adapters."""
import json
from pathlib import Path
import tempfile

from .releases import validate_manifest, version_tuple


def latest_release(updater, base, provider, assets_for_release, asset_url):
    installed = updater.installed()
    if not installed or installed.get('component') != 'robot':
        raise ValueError(f'{provider} robot updates require a complete robot installation')
    candidates = []
    with tempfile.TemporaryDirectory() as temporary:
        path = Path(temporary) / 'releases.json'
        for page in range(1, 101):
            updater._fetch(f'{base}/releases?per_page=50&page={page}', path, 4 * 1024**2)
            releases = json.loads(path.read_text())
            if not isinstance(releases, list):
                raise ValueError(f'Invalid {provider} release listing')
            for release in releases:
                if release.get('draft') or release.get('prerelease') or release.get('upcoming_release'):
                    continue
                prefix = installed['target'] + '/robot/v'
                tag = release.get('tag_name', '')
                if not tag.startswith(prefix):
                    continue
                try:
                    version = version_tuple(tag[len(prefix):])
                except ValueError:
                    continue
                assets = assets_for_release(release)
                if 'manifest.json' in assets:
                    candidates.append((version, assets, tag[len(prefix):]))
            if len(releases) < 50:
                break
        else:
            raise ValueError(f'{provider} release listing exceeds pagination limit')
        if not candidates:
            raise ValueError('No published complete release exists for this robot system')
        _, assets, version = max(candidates, key=lambda candidate: candidate[0])

        def url_for(name):
            if name not in assets:
                raise ValueError(f'{provider} release asset missing: {name}')
            return asset_url(assets[name])

        manifest_path = Path(temporary) / 'manifest.json'
        updater._fetch(url_for('manifest.json'), manifest_path, 1024**2)
        updater._verify_signature(manifest_path, url_for('manifest.json.sig') if updater.config.public_key else None)
        manifest = validate_manifest(json.loads(manifest_path.read_text()), updater.config.product)
        if (manifest.get('component') != 'robot' or manifest['target'] != installed['target'] or
                manifest['version'] != version):
            raise ValueError(f'{provider} release tag and manifest do not match')
        if manifest['channel'] != updater.config.channel:
            raise ValueError('Release channel mismatch')
        manifest['_download_url'] = url_for(manifest.get('archive', ''))
        return manifest
