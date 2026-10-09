"""Publish verified release artifacts through Gitea's release API."""
from urllib.parse import quote, urlsplit
import uuid

class MultipartUpload:
    """Stream a large archive with a known multipart content length."""
    def __init__(self, path):
        if any(char in path.name for char in '\r\n"'):
            raise ValueError('Invalid attachment filename')
        self.path = path
        self.boundary = uuid.uuid4().hex
        self.prefix = (f'--{self.boundary}\r\nContent-Disposition: form-data; name="attachment"; filename="{path.name}"\r\nContent-Type: application/octet-stream\r\n\r\n').encode()
        self.suffix = f'\r\n--{self.boundary}--\r\n'.encode()

    def __len__(self):
        return len(self.prefix) + self.path.stat().st_size + len(self.suffix)

    def __iter__(self):
        yield self.prefix
        with self.path.open('rb') as stream:
            while block := stream.read(1024 * 1024):
                yield block
        yield self.suffix


class GiteaPublisher:
    def __init__(self, repository_url, token):
        import requests
        parsed = urlsplit(repository_url)
        parts = parsed.path.strip('/').removesuffix('.git').split('/')
        if parsed.scheme not in ('http', 'https') or len(parts) != 2 or not all(parts) or parsed.username or parsed.query or parsed.fragment:
            raise ValueError('Gitea remote must be an HTTP(S) owner/repository URL without credentials')
        self.base = f'{parsed.scheme}://{parsed.netloc}/api/v1/repos/' + '/'.join(quote(p, safe='') for p in parts)
        self.session = requests.Session()
        self.session.headers['Authorization'] = 'token ' + token

    def username(self):
        response = self.session.get(self.base.split('/repos/')[0] + '/user', timeout=(10, 30), allow_redirects=False)
        if response.status_code != 200:
            raise ValueError(f'Gitea authentication failed (HTTP {response.status_code})')
        return response.json()['login']

    def request(self, method, path, **kwargs):
        response = self.session.request(method, self.base + path, timeout=(10, 300), allow_redirects=False, **kwargs)
        if response.status_code == 404 and method == 'GET':
            return None
        if not response.ok or 300 <= response.status_code < 400:
            raise ValueError(f'Gitea {method} {path} failed (HTTP {response.status_code})')
        return response.json()

    def publish(self, directory, manifest, notes, digest):
        tag = f'{manifest["target"]}/robot/v{manifest["version"]}'
        archive = directory / manifest['archive']
        checksum = archive.with_name(archive.name + '.sha256')
        files = (archive, checksum, directory / 'manifest.json')
        signature = directory / 'manifest.json.sig'
        if signature.is_file():
            files += (signature,)
        if any(not p.is_file() for p in files):
            raise ValueError('Release archive, checksum, and manifest are required')
        if digest(archive) != manifest['sha256'] or checksum.read_text().strip() != f'{manifest["sha256"]}  {archive.name}':
            raise ValueError('Release archive/checksum mismatch')
        tag_info = self.request('GET', '/tags/' + quote(tag, safe=''))
        if not tag_info or tag_info['commit']['sha'] != manifest['source_git_commit']:
            raise ValueError('Remote release tag does not match the packaged source commit')
        marker = f'Robot archive SHA256: {manifest["sha256"]}'
        body = f'{notes.strip()}\n\n{marker}\nSVN revision: {manifest["source_svn_revision"]}\nPlatform: {manifest["selection"]["platform_version"]}\nBackend: {manifest["selection"]["backend_version"]}\n'
        return self.publish_assets(tag, f'{manifest["target"]} {manifest["version"]}', body, marker, files, digest)

    def publish_assets(self, tag, title, body, marker, files, digest):
        """Resume matching drafts; publish only after every attachment is verified."""
        release = self.request('GET', '/releases/tags/' + quote(tag, safe=''))
        if release is None:
            release = self.request('POST', '/releases', json=dict(tag_name=tag, name=title, body=body, draft=True))
        elif marker not in release.get('body', '').splitlines():
            raise ValueError('Existing release has different or unverified artifacts; refusing to replace it')
        assets = {asset['name']: asset for asset in self.request('GET', f'/releases/{release["id"]}/assets')}
        for path in files:
            asset = assets.get(path.name)
            if asset:
                # Verify bytes, not only filenames, before resuming a partial upload.
                import hashlib
                url = asset['browser_download_url']
                if urlsplit(url).netloc != urlsplit(self.base).netloc or urlsplit(url).scheme != urlsplit(self.base).scheme:
                    raise ValueError('Release asset download leaves the configured Gitea server')
                with self.session.get(url, stream=True, timeout=(10, 300), allow_redirects=False) as response:
                    if response.status_code != 200:
                        raise ValueError(f'Unable to verify release asset (HTTP {response.status_code})')
                    hasher = hashlib.sha256()
                    for block in response.iter_content(1024 * 1024):
                        hasher.update(block)
                if hasher.hexdigest() != digest(path):
                    raise ValueError(f'Existing release asset differs: {path.name}')
            else:
                if not release['draft']:
                    raise ValueError('Published release is missing an asset; refusing to modify it')
                upload = MultipartUpload(path)
                self.request('POST', f'/releases/{release["id"]}/assets', params={'name': path.name},
                             data=upload, headers={'Content-Type': f'multipart/form-data; boundary={upload.boundary}'})
        if release['draft']:
            release = self.request('PATCH', f'/releases/{release["id"]}', json={'draft': False})
        return release['html_url']
