"""Gitea publication checks without contacting SVN, Gitea, or hardware."""
import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch, MagicMock

MODULE = Path(__file__).resolve().parents[3] / 'packaging/shared/gitea_release.py'
spec = importlib.util.spec_from_file_location('gitea_release_tests', MODULE)
gitea = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gitea)


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


class GiteaReleaseTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.directory = Path(temporary.name)
        archive = self.directory / 'robot.tar.gz'
        archive.write_bytes(b'verified archive')
        self.manifest = dict(target='paint_tray_dry', version='1.0.1', archive=archive.name,
                             sha256=digest(archive), source_git_commit='abc', source_svn_revision='28',
                             selection=dict(platform_version='1.0.1', backend_version='1.0.0'))
        (self.directory / 'manifest.json').write_text(json.dumps(self.manifest))
        (self.directory / 'robot.tar.gz.sha256').write_text(f'{digest(archive)}  {archive.name}\n')
        self.publisher = gitea.GiteaPublisher('http://gitea.test/admin/robot.git', 'secret-token')
        self.calls = []
        self.existing = None

    def request(self, method, path, **kwargs):
        self.calls.append((method, path, kwargs))
        if path.startswith('/tags/'):
            return dict(commit=dict(sha='abc'))
        if path.startswith('/releases/tags/'):
            return self.existing
        if method == 'POST' and path == '/releases':
            return dict(id=1, draft=True)
        if method == 'GET' and path.endswith('/assets'):
            return []
        if method == 'PATCH':
            return dict(html_url='http://gitea.test/release/1')
        return dict(id=2)

    def publish(self):
        with patch.object(self.publisher, 'request', side_effect=self.request):
            return self.publisher.publish(self.directory, self.manifest, 'Changes', digest)

    def test_creates_draft_uploads_three_assets_then_publishes(self):
        self.assertEqual('http://gitea.test/release/1', self.publish())
        creation = next(c for c in self.calls if c[:2] == ('POST', '/releases'))
        self.assertTrue(creation[2]['json']['draft'])
        self.assertEqual(3, sum(method == 'POST' and path.endswith('/assets') for method, path, _ in self.calls))
        self.assertEqual(('PATCH', '/releases/1'), self.calls[-1][:2])
        self.assertIn('paint_tray_dry%2Frobot%2Fv1.0.1', self.calls[0][1])

    def test_failed_upload_leaves_release_as_draft(self):
        original = self.request
        def fail(method, path, **kwargs):
            if method == 'POST' and path.endswith('/assets'):
                raise ValueError('upload failed')
            return original(method, path, **kwargs)
        with patch.object(self.publisher, 'request', side_effect=fail):
            with self.assertRaisesRegex(ValueError, 'upload failed'):
                self.publisher.publish(self.directory, self.manifest, '', digest)
        self.assertFalse(any(method == 'PATCH' for method, _, _ in self.calls))

    def test_mismatched_existing_release_is_never_overwritten(self):
        self.existing = dict(id=1, draft=False, body='different release')
        with self.assertRaisesRegex(ValueError, 'refusing to replace'):
            self.publish()
        self.assertTrue(all(method == 'GET' for method, _, _ in self.calls))

    def test_corrupt_archive_fails_before_network(self):
        (self.directory / 'robot.tar.gz').write_bytes(b'corrupted')
        with self.assertRaisesRegex(ValueError, 'checksum mismatch'):
            self.publish()
        self.assertEqual([], self.calls)

    def test_wrong_remote_tag_blocks_release_creation(self):
        self.manifest['source_git_commit'] = 'wrong'
        with self.assertRaisesRegex(ValueError, 'packaged source commit'):
            self.publish()
        self.assertTrue(all(method == 'GET' for method, _, _ in self.calls))

    def test_published_release_missing_assets_is_not_modified(self):
        self.existing = dict(id=1, draft=False, body=f'Robot archive SHA256: {self.manifest["sha256"]}')
        with self.assertRaisesRegex(ValueError, 'missing an asset'):
            self.publish()
        self.assertTrue(all(method == 'GET' for method, _, _ in self.calls))

    def test_multipart_upload_length_matches_streamed_body(self):
        import requests
        upload = gitea.MultipartUpload(self.directory / 'robot.tar.gz')
        body = b''.join(upload)
        self.assertEqual(len(upload), len(body))
        self.assertIn(b'name="attachment"', body)
        self.assertIn(b'verified archive', body)
        prepared = requests.Request('POST', 'http://gitea.test/assets', data=upload).prepare()
        self.assertEqual(str(len(upload)), prepared.headers['Content-Length'])
        self.assertNotIn('Transfer-Encoding', prepared.headers)

    def test_retry_checks_existing_asset_bytes_and_uploads_only_missing_files(self):
        self.existing = dict(id=1, draft=True, body=f'Robot archive SHA256: {self.manifest["sha256"]}')
        original = self.request
        def resumed(method, path, **kwargs):
            if method == 'GET' and path.endswith('/assets'):
                return [dict(name='robot.tar.gz', browser_download_url='http://gitea.test/attachment')]
            return original(method, path, **kwargs)
        response = MagicMock(status_code=200)
        response.__enter__.return_value = response
        response.iter_content.return_value = [b'verified archive']
        with patch.object(self.publisher, 'request', side_effect=resumed), patch.object(self.publisher.session, 'get', return_value=response):
            self.publisher.publish(self.directory, self.manifest, '', digest)
        uploads = [kwargs['params']['name'] for method, path, kwargs in self.calls if method == 'POST' and path.endswith('/assets')]
        self.assertEqual(['robot.tar.gz.sha256', 'manifest.json'], uploads)

    def test_retry_rejects_different_uploaded_bytes(self):
        self.existing = dict(id=1, draft=True, body=f'Robot archive SHA256: {self.manifest["sha256"]}')
        original = self.request
        def resumed(method, path, **kwargs):
            if method == 'GET' and path.endswith('/assets'):
                return [dict(name='robot.tar.gz', browser_download_url='http://gitea.test/attachment')]
            return original(method, path, **kwargs)
        response = MagicMock(status_code=200)
        response.__enter__.return_value = response
        response.iter_content.return_value = [b'different bytes']
        with patch.object(self.publisher, 'request', side_effect=resumed), patch.object(self.publisher.session, 'get', return_value=response):
            with self.assertRaisesRegex(ValueError, 'asset differs'):
                self.publisher.publish(self.directory, self.manifest, '', digest)
        self.assertFalse(any(method == 'PATCH' for method, _, _ in self.calls))

    def test_remote_urls_with_credentials_are_rejected(self):
        with self.assertRaises(ValueError):
            gitea.GiteaPublisher('http://user:password@gitea.test/admin/robot', 'token')

    def test_http_errors_do_not_expose_server_response_or_token(self):
        response = MagicMock(status_code=403, ok=False, text='secret-token')
        with patch.object(self.publisher.session, 'request', return_value=response):
            with self.assertRaisesRegex(ValueError, 'HTTP 403') as raised:
                self.publisher.request('POST', '/releases')
        self.assertNotIn('secret-token', str(raised.exception))
