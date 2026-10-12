"""Discover complete robot releases from the configured GitHub repository."""
import re
from urllib.parse import quote, urlsplit

from .repository_releases import latest_release


def repository_api(repository_url):
    parsed = urlsplit(repository_url.rstrip('/').removesuffix('.git'))
    parts = parsed.path.strip('/').split('/')
    if (parsed.scheme != 'https' or parsed.netloc != 'github.com' or
            parsed.query or parsed.fragment or len(parts) != 2 or
            any(not re.fullmatch(r'[A-Za-z0-9_.-]+', part) or part in ('.', '..') for part in parts)):
        raise ValueError('GitHub repository_url must be https://github.com/owner/repository')
    return 'https://api.github.com/repos/' + '/'.join(quote(part, safe='') for part in parts)


def latest_robot_release(updater):
    config = updater.config
    base = repository_api(config.repository_url)
    repository = urlsplit(config.repository_url.rstrip('/').removesuffix('.git'))

    def assets(release):
        return {asset['name']: asset for asset in release.get('assets', [])}

    def asset_url(asset):
        if config.token_file is not None:
            url = asset.get('url', '')
            if not re.fullmatch(re.escape(base) + r'/releases/assets/[0-9]+', url):
                raise ValueError('GitHub release asset leaves the configured repository')
        else:
            url = asset.get('browser_download_url', '')
            parsed = urlsplit(url)
            prefix = repository.path.rstrip('/') + '/releases/download/'
            if (parsed.scheme != 'https' or parsed.netloc != 'github.com' or
                    not parsed.path.startswith(prefix) or parsed.fragment):
                raise ValueError('GitHub release asset leaves the configured repository')
        return url

    return latest_release(updater, base, 'GitHub', assets, asset_url)
