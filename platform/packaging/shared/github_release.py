"""Publish complete robot archives to the SVN-backed GitHub mirror."""
import hashlib
from urllib.parse import quote, urlsplit

from src.engine.updates.github_source import repository_api
from src.engine.updates.updater import _HttpsRedirect


class GitHubPublisher:
    def __init__(self, repository_url, token):
        import requests
        if repository_url.startswith('git@github.com:'):
            repository_url = 'https://github.com/' + repository_url.split(':', 1)[1]
        self.base = repository_api(repository_url)
        self.session = requests.Session()
        self.session.headers.update({'Authorization': 'Bearer ' + token,
                                     'Accept': 'application/vnd.github+json',
                                     'X-GitHub-Api-Version': '2022-11-28'})

    def username(self):
        return 'x-access-token'

    def request(self, method, path, **kwargs):
        response = self.session.request(method, self.base + path, timeout=(10, 300),
                                        allow_redirects=False, **kwargs)
        if response.status_code == 404 and method == 'GET':
            return None
        if not response.ok or 300 <= response.status_code < 400:
            raise ValueError(f'GitHub {method} {path} failed (HTTP {response.status_code})')
        return response.json()

    def publish(self, directory, manifest, notes, digest):
        tag = f'{manifest["target"]}/robot/v{manifest["version"]}'
        archive = directory / manifest['archive']
        checksum = archive.with_name(archive.name + '.sha256')
        files = (archive, checksum, directory / 'manifest.json')
        signature = directory / 'manifest.json.sig'
        if signature.is_file():
            files += (signature,)
        if any(not path.is_file() for path in files):
            raise ValueError('Release archive, checksum, and manifest are required')
        if digest(archive) != manifest['sha256'] or checksum.read_text().strip() != f'{manifest["sha256"]}  {archive.name}':
            raise ValueError('Release archive/checksum mismatch')
        reference = self.request('GET', '/git/ref/tags/' + quote(tag, safe=''))
        if not reference:
            raise ValueError('Remote release tag does not exist')
        obj = reference['object']
        for _ in range(8):
            if obj['type'] != 'tag':
                break
            obj = self.request('GET', '/git/tags/' + quote(obj['sha'], safe=''))['object']
        if obj['type'] != 'commit' or obj['sha'] != manifest['source_git_commit']:
            raise ValueError('Remote release tag does not match the packaged source commit')
        marker = f'Robot archive SHA256: {manifest["sha256"]}'
        body = (f'{notes.strip()}\n\n{marker}\nSVN revision: {manifest["source_svn_revision"]}\n'
                f'Platform: {manifest["selection"]["platform_version"]}\n'
                f'Backend: {manifest["selection"]["backend_version"]}\n')
        release = self.request('GET', '/releases/tags/' + quote(tag, safe=''))
        if release is None:
            release = self.request('POST', '/releases', json={
                'tag_name': tag, 'name': f'{manifest["target"]} {manifest["version"]}',
                'body': body, 'draft': True, 'make_latest': 'false'})
        elif marker not in release.get('body', '').splitlines():
            raise ValueError('Existing release has different or unverified artifacts; refusing to replace it')
        assets = self._assets(release['id'])
        upload_url = release['upload_url'].split('{', 1)[0]
        expected = self.base.replace('api.github.com', 'uploads.github.com') + f'/releases/{release["id"]}/assets'
        if upload_url != expected:
            raise ValueError('GitHub upload URL leaves the configured repository')
        for path in files:
            asset = assets.get(path.name)
            if asset:
                remote_digest = self._asset_digest(asset)
                if remote_digest != digest(path):
                    raise ValueError(f'Existing release asset differs: {path.name}')
            else:
                if not release['draft']:
                    raise ValueError('Published release is missing an asset; refusing to modify it')
                with path.open('rb') as stream:
                    response = self.session.post(upload_url, params={'name': path.name}, data=stream,
                                                 headers={'Content-Type': 'application/octet-stream'},
                                                 timeout=(10, 300), allow_redirects=False)
                if not response.ok or 300 <= response.status_code < 400:
                    raise ValueError(f'GitHub asset upload failed (HTTP {response.status_code})')
                uploaded = response.json()
                if self._asset_digest(uploaded) != digest(path):
                    raise ValueError(f'Uploaded release asset differs: {path.name}')
        if release['draft']:
            release = self.request('PATCH', f'/releases/{release["id"]}', json={'draft': False, 'make_latest': 'false'})
        return release['html_url']

    def _assets(self, release_id):
        result = {}
        for page in range(1, 101):
            assets = self.request('GET', f'/releases/{release_id}/assets?per_page=100&page={page}')
            for asset in assets:
                result[asset['name']] = asset
            if len(assets) < 100:
                return result
        raise ValueError('GitHub release assets exceed pagination limit')

    def _asset_digest(self, asset):
        digest = asset.get('digest')
        if digest and digest.startswith('sha256:'):
            return digest.removeprefix('sha256:')
        import urllib.request
        expected = self.base + '/releases/assets/' + str(asset['id'])
        if asset.get('url') != expected:
            raise ValueError('GitHub asset URL leaves the configured repository')
        request = urllib.request.Request(expected, headers={
            'Authorization': self.session.headers['Authorization'], 'Accept': 'application/octet-stream',
            'User-Agent': 'robot-release-publisher'})
        opener = urllib.request.build_opener(_HttpsRedirect(strip_cross_origin_auth=True))
        hasher = hashlib.sha256()
        with opener.open(request, timeout=300) as response:
            while chunk := response.read(1024 * 1024):
                hasher.update(chunk)
        return hasher.hexdigest()
