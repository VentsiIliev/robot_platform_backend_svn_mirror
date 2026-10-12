"""GitHub discovery and credential boundaries without remote writes."""
from dataclasses import replace
import io
import json
from pathlib import Path
import unittest
from unittest.mock import patch
from urllib.request import Request

from src.engine.updates.config import UpdateConfig
from src.engine.updates.github_source import repository_api
from src.engine.updates.updater import PlatformUpdater, _HttpsRedirect
from tests.engine.updates import test_robot_updates as fixtures


class GitHubSourceTests(unittest.TestCase):
    def setUp(self):
        self.fixture = fixtures.RobotUpdateTests()
        self.fixture.setUp()
        self.addCleanup(self.fixture.doCleanups)
        self.fixture.install()
        self.manifest = self.fixture.feed_release()
        self.config = replace(self.fixture.config, repository_type='github',
                              repository_url='https://github.com/owner/robot/', allow_insecure_http=True)
        self.updater = PlatformUpdater(self.config)
        self.base = 'https://api.github.com/repos/owner/robot'
        self.listing = [{'tag_name': 'paint_tray_dry/robot/v1.1.0', 'assets': [
            {'name': name, 'id': index, 'url': f'{self.base}/releases/assets/{index}',
             'browser_download_url': f'https://github.com/owner/robot/releases/download/tag/{name}'}
            for index, name in enumerate(('manifest.json', self.manifest['archive'], 'manifest.json.sig'), 1)]}]

    def fetch(self, url, destination, limit):
        destination.write_text(json.dumps(self.listing if '/releases?' in url else self.manifest))

    def test_only_published_complete_releases_for_installed_target_are_selected(self):
        self.listing += [
            {'tag_name': 'v1.4.9-plproject.1', 'assets': []},
            {'tag_name': 'glue/robot/v99.0.0', 'assets': []},
            {'tag_name': 'paint_tray_dry/platform/v99.0.0', 'assets': []},
            {'tag_name': 'paint_tray_dry/robot/v99.0.0', 'draft': True},
            {'tag_name': 'paint_tray_dry/robot/v98.0.0', 'prerelease': True},
        ]
        with patch.object(self.updater, '_fetch', side_effect=self.fetch):
            result = self.updater.check()
        self.assertTrue(result['available'])
        self.assertEqual(result['version'], '1.1.0')
        self.assertEqual(result['_download_url'], 'https://github.com/owner/robot/releases/download/tag/1.1.0.tar.gz')

    def test_paginates_past_unrelated_releases(self):
        calls = []
        def fetch(url, destination, limit):
            calls.append(url)
            listing = [{'tag_name': 'unrelated'}] * 50 if 'page=1' in url else self.listing
            destination.write_text(json.dumps(listing if '/releases?' in url else self.manifest))
        with patch.object(self.updater, '_fetch', side_effect=fetch):
            self.updater.check()
        self.assertIn(f'{self.base}/releases?per_page=50&page=2', calls)

    def test_private_repository_uses_api_asset_urls(self):
        token = self.fixture.directory / 'token'
        token.write_text('test-token')
        self.updater = PlatformUpdater(replace(self.config, token_file=token))
        with patch.object(self.updater, '_fetch', side_effect=self.fetch):
            result = self.updater.check()
        self.assertEqual(result['_download_url'], self.base + '/releases/assets/2')

    def test_signature_is_verified_before_returning_candidate(self):
        self.updater = PlatformUpdater(replace(self.config, public_key=Path('/installed/key.pem')))
        with patch.object(self.updater, '_fetch', side_effect=self.fetch), patch.object(self.updater, '_verify_signature') as verify:
            self.updater.check()
        self.assertEqual(verify.call_args.args[1], 'https://github.com/owner/robot/releases/download/tag/manifest.json.sig')

    def test_assets_cannot_leave_configured_repository(self):
        self.listing[0]['assets'][0]['browser_download_url'] = 'https://github.com/other/robot/releases/download/tag/manifest.json'
        with patch.object(self.updater, '_fetch', side_effect=self.fetch):
            with self.assertRaisesRegex(ValueError, 'configured repository'):
                self.updater.check()

    def test_tag_manifest_version_mismatch_is_rejected(self):
        self.listing[0]['tag_name'] = 'paint_tray_dry/robot/v2.0.0'
        with patch.object(self.updater, '_fetch', side_effect=self.fetch):
            with self.assertRaisesRegex(ValueError, 'tag and manifest'):
                self.updater.check()

    def test_missing_archive_and_wrong_channel_are_rejected(self):
        self.listing[0]['assets'] = self.listing[0]['assets'][:1]
        with patch.object(self.updater, '_fetch', side_effect=self.fetch):
            with self.assertRaisesRegex(ValueError, 'asset missing'):
                self.updater.check()
        self.manifest['channel'] = 'testing'
        with patch.object(self.updater, '_fetch', side_effect=self.fetch):
            with self.assertRaisesRegex(ValueError, 'channel'):
                self.updater.check()

    def test_api_token_headers_and_scope(self):
        token = self.fixture.directory / 'token'
        token.write_text('test-token')
        updater = PlatformUpdater(replace(self.config, token_file=token))
        destination = self.fixture.directory / 'download'
        with patch('urllib.request.build_opener') as build:
            build.return_value.open.return_value = io.BytesIO(b'asset')
            updater._fetch(self.base + '/releases/assets/2', destination, 100)
            request = build.return_value.open.call_args.args[0]
            self.assertEqual(request.get_header('Authorization'), 'Bearer test-token')
            self.assertEqual(request.get_header('Accept'), 'application/octet-stream')
            with self.assertRaisesRegex(ValueError, 'configured server'):
                updater._fetch('https://api.github.com/repos/other/robot/releases', destination, 100)

    def test_github_redirect_strips_credentials_and_rejects_http(self):
        request = Request(self.base + '/releases/assets/2', headers={'Authorization': 'Bearer secret'})
        redirect = _HttpsRedirect(strip_cross_origin_auth=True)
        result = redirect.redirect_request(request, None, 302, 'redirect', {}, 'https://release-assets.githubusercontent.com/file')
        self.assertIsNone(result.get_header('Authorization'))
        self.assertEqual(request.get_header('Authorization'), 'Bearer secret')
        with self.assertRaisesRegex(ValueError, 'HTTPS'):
            redirect.redirect_request(request, None, 302, 'redirect', {}, 'http://host/file')

    def test_invalid_repositories_rejected_at_config_load(self):
        for url in ('http://github.com/owner/robot', 'https://evil.test/owner/robot',
                    'https://github.com/a/../robot', 'https://user:pass@github.com/a/robot'):
            with self.subTest(url=url), self.assertRaises(ValueError):
                repository_api(url)
        path = self.fixture.directory / 'config.json'
        path.write_text(json.dumps({'install_root': str(self.fixture.root), 'enabled': False,
                                    'repository_type': 'github', 'repository_url': 'https://evil.test/a/b'}))
        with self.assertRaises(ValueError):
            UpdateConfig.load(path)
