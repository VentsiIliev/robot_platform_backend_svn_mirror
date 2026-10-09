"""Discover complete robot release assets from a Gitea repository."""
import json
from urllib.parse import urlsplit, quote
from .releases import version_tuple, validate_manifest


def latest_robot_release(updater):
    config = updater.config
    parsed = urlsplit(config.repository_url.rstrip('/').removesuffix('.git'))
    parts = parsed.path.strip('/').split('/')
    if len(parts) != 2 or not all(parts):
        raise ValueError('Gitea repository_url must name owner/repository')
    installed = updater.installed()
    if not installed or installed.get('component') != 'robot':
        raise ValueError('Gitea robot updates require a complete robot installation')
    base = f'{parsed.scheme}://{parsed.netloc}/api/v1/repos/' + '/'.join(quote(p, safe='') for p in parts)
    import tempfile
    from pathlib import Path
    candidates = []
    with tempfile.TemporaryDirectory() as temporary:
        path = Path(temporary) / 'releases.json'
        # Paginate rather than relying on the server's default page size.
        for page in range(1, 101):
            updater._fetch(f'{base}/releases?limit=50&page={page}', path, 4 * 1024**2)
            releases = json.loads(path.read_text())
            if not isinstance(releases, list):
                raise ValueError('Invalid Gitea release listing')
            for release in releases:
                if release.get('draft') or release.get('prerelease'):
                    continue
                tag = release.get('tag_name', '')
                prefix = installed['target'] + '/robot/v'
                if not tag.startswith(prefix):
                    continue
                try:
                    version = version_tuple(tag[len(prefix):])
                except ValueError:
                    continue
                assets = {a['name']: a for a in release.get('assets', [])}
                if 'manifest.json' in assets:
                    candidates.append((version, assets, tag[len(prefix):]))
            if len(releases) < 50:
                break
        else:
            raise ValueError('Gitea release listing exceeds pagination limit')
        if not candidates:
            raise ValueError('No published complete release exists for this robot system')
        _, assets, version = max(candidates, key=lambda item: item[0])
        def asset_url(name):
            if name not in assets:
                raise ValueError('Gitea release asset missing: ' + name)
            url = assets[name].get('browser_download_url', '')
            target = urlsplit(url)
            if (target.scheme, target.netloc) != (parsed.scheme, parsed.netloc):
                raise ValueError('Gitea release asset leaves the configured server')
            return url
        manifest_path = Path(temporary) / 'manifest.json'
        updater._fetch(asset_url('manifest.json'), manifest_path, 1024**2)
        updater._verify_signature(manifest_path, asset_url('manifest.json.sig') if config.public_key else None)
        manifest = validate_manifest(json.loads(manifest_path.read_text()), config.product)
        if manifest.get('component') != 'robot' or manifest['target'] != installed['target'] or manifest['version'] != version:
            raise ValueError('Gitea release tag and manifest do not match')
        if manifest['channel'] != config.channel:
            raise ValueError('Release channel mismatch')
        manifest['_download_url'] = asset_url(manifest.get('archive', ''))
        return manifest
