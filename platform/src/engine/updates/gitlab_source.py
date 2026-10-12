"""GitLab release links for a configured project, including nested namespaces."""
import re
from urllib.parse import quote, urlsplit

from .repository_releases import latest_release


def repository_api(repository_url, api_url=None):
    parsed = urlsplit(repository_url.rstrip('/').removesuffix('.git'))
    parts = parsed.path.strip('/').split('/')
    if (parsed.scheme not in ('https', 'http') or not parsed.netloc or parsed.username or
            parsed.query or parsed.fragment or len(parts) < 2 or
            any(not re.fullmatch(r'[A-Za-z0-9_.-]+', part) or part in ('.', '..') for part in parts)):
        raise ValueError('GitLab repository_url must name a server and namespace/project')
    origin = f'{parsed.scheme}://{parsed.netloc}'
    api = (api_url or origin + '/api/v4').rstrip('/')
    api_parsed = urlsplit(api)
    if ((api_parsed.scheme, api_parsed.netloc) != (parsed.scheme, parsed.netloc) or
            api_parsed.username or api_parsed.query or api_parsed.fragment):
        raise ValueError('GitLab api_url must remain on the configured server')
    # A subpath deployment such as /gitlab has its API at /gitlab/api/v4.
    prefix = api_parsed.path.removesuffix('/api/v4')
    if not api_parsed.path.endswith('/api/v4'):
        raise ValueError('GitLab api_url must end in /api/v4')
    path = parsed.path
    if prefix:
        if not path.startswith(prefix + '/'):
            raise ValueError('GitLab project must belong to the configured API installation')
        path = path[len(prefix):]
    return api + '/projects/' + quote(path.strip('/'), safe='')


def latest_robot_release(updater):
    config = updater.config
    base = repository_api(config.repository_url, config.api_url)
    origin = urlsplit(config.repository_url)

    def assets(release):
        return {asset['name']: asset for asset in release.get('assets', {}).get('links', [])}

    def asset_url(asset):
        url = asset.get('direct_asset_url') or asset.get('url', '')
        parsed = urlsplit(url)
        if ((parsed.scheme, parsed.netloc) != (origin.scheme, origin.netloc) or
                parsed.username or parsed.fragment):
            raise ValueError('GitLab release asset leaves the configured server')
        return url

    return latest_release(updater, base, 'GitLab', assets, asset_url)
