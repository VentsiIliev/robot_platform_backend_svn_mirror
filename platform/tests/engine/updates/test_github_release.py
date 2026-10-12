"""Draft-first GitHub publication, exact tags and resumable verified assets."""
import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import Mock, patch

MODULE = Path(__file__).resolve().parents[3] / 'packaging/shared/github_release.py'
spec = importlib.util.spec_from_file_location('github_release_tests', MODULE)
github = importlib.util.module_from_spec(spec)
spec.loader.exec_module(github)


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


class GitHubReleaseTests(unittest.TestCase):
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
        self.publisher = github.GitHubPublisher('git@github.com:owner/robot.git', 'secret-token')
        self.calls = []
        self.existing = None
        self.assets = []
        self.tag_object = {'type': 'commit', 'sha': 'abc'}

    def request(self, method, path, **kwargs):
        self.calls.append((method, path, kwargs))
        if path.startswith('/git/ref/tags/'):
            return {'object': self.tag_object}
        if path.startswith('/git/tags/'):
            return {'object': {'type': 'commit', 'sha': 'abc'}}
        if path.startswith('/releases/tags/'):
            return self.existing
        release = {'id': 1, 'draft': True,
                   'upload_url': 'https://uploads.github.com/repos/owner/robot/releases/1/assets{?name,label}',
                   'html_url': 'https://github.com/owner/robot/releases/tag/release'}
        if method == 'POST':
            return release
        if method == 'GET' and '/assets?' in path:
            return self.assets
        if method == 'PATCH':
            return dict(release, draft=False)
        raise AssertionError((method, path))

    def upload(self, url, **kwargs):
        content = kwargs['data'].read()
        return Mock(ok=True, status_code=201,
                    json=Mock(return_value={'digest': 'sha256:' + hashlib.sha256(content).hexdigest()}))

    def publish(self):
        with patch.object(self.publisher, 'request', side_effect=self.request), patch.object(self.publisher.session, 'post', side_effect=self.upload) as post:
            result = self.publisher.publish(self.directory, self.manifest, 'Changes', digest)
        return result, post

    def test_creates_draft_uploads_verified_raw_assets_then_publishes(self):
        result, post = self.publish()
        self.assertTrue(result.startswith('https://github.com/owner/robot/releases/'))
        self.assertEqual(post.call_count, 3)
        creation = next(call for call in self.calls if call[:2] == ('POST', '/releases'))
        self.assertTrue(creation[2]['json']['draft'])
        self.assertEqual(self.calls[-1][:2], ('PATCH', '/releases/1'))
        self.assertIn('paint_tray_dry%2Frobot%2Fv1.0.1', self.calls[0][1])
        self.assertEqual(self.publisher.session.headers['Authorization'], 'Bearer secret-token')
        self.assertEqual(post.call_args.kwargs['headers']['Content-Type'], 'application/octet-stream')

    def test_wrong_remote_tag_blocks_release_creation(self):
        self.tag_object['sha'] = 'other'
        with self.assertRaisesRegex(ValueError, 'packaged source'):
            self.publish()
        self.assertFalse(any(method == 'POST' for method, _, _ in self.calls))

    def test_annotated_tag_is_dereferenced(self):
        self.tag_object = {'type': 'tag', 'sha': 'annotated'}
        self.publish()
        self.assertIn(('GET', '/git/tags/annotated', {}), self.calls)

    def test_upload_failure_leaves_draft_unpublished(self):
        with patch.object(self.publisher, 'request', side_effect=self.request), patch.object(self.publisher.session, 'post', return_value=Mock(ok=False, status_code=500)):
            with self.assertRaisesRegex(ValueError, 'upload failed'):
                self.publisher.publish(self.directory, self.manifest, 'Changes', digest)
        self.assertFalse(any(method == 'PATCH' for method, _, _ in self.calls))

    def test_existing_release_marker_and_bytes_must_match(self):
        self.existing = {'id': 1, 'draft': True, 'body': 'different release'}
        with self.assertRaisesRegex(ValueError, 'refusing to replace'):
            self.publish()
        self.existing.update(body='Robot archive SHA256: ' + self.manifest['sha256'],
                             upload_url='https://uploads.github.com/repos/owner/robot/releases/1/assets{?name,label}')
        self.assets = [{'name': 'robot.tar.gz', 'digest': 'sha256:' + '0' * 64}]
        with self.assertRaisesRegex(ValueError, 'asset differs'):
            self.publish()

    def test_matching_published_release_is_not_modified(self):
        self.existing = {'id': 1, 'draft': False, 'body': 'Robot archive SHA256: ' + self.manifest['sha256'],
                         'upload_url': 'https://uploads.github.com/repos/owner/robot/releases/1/assets{?name,label}',
                         'html_url': 'https://github.com/owner/robot/releases/tag/release'}
        self.assets = [{'name': path.name, 'digest': 'sha256:' + digest(path)} for path in self.directory.iterdir()]
        _, post = self.publish()
        post.assert_not_called()
        self.assertFalse(any(method == 'PATCH' for method, _, _ in self.calls))

    def test_upload_url_must_remain_in_repository(self):
        self.existing = {'id': 1, 'draft': True, 'body': 'Robot archive SHA256: ' + self.manifest['sha256'],
                         'upload_url': 'https://other.example/upload'}
        with self.assertRaisesRegex(ValueError, 'configured repository'):
            self.publish()
