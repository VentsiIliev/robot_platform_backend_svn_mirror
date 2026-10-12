"""GitLab project routing, release links and token handling."""
from dataclasses import replace
import io
import json
import unittest
from unittest.mock import patch

from src.engine.updates.gitlab_source import repository_api
from src.engine.updates.updater import PlatformUpdater
from tests.engine.updates import test_robot_updates as fixtures


class GitLabSourceTests(unittest.TestCase):
    def setUp(self):
        self.fixture = fixtures.RobotUpdateTests()
        self.fixture.setUp()
        self.addCleanup(self.fixture.doCleanups)
        self.fixture.install()
        self.manifest = self.fixture.feed_release()
        self.config = replace(self.fixture.config, repository_type='gitlab',
                              repository_url='https://gitlab.example/group/subgroup/robot/', allow_insecure_http=True)
        self.updater = PlatformUpdater(self.config)
        self.listing = [{'tag_name': 'paint_tray_dry/robot/v1.1.0', 'assets': {'links': [
            {'name': name, 'direct_asset_url': f'https://gitlab.example/group/subgroup/robot/-/releases/tag/downloads/{name}'}
            for name in ('manifest.json', self.manifest['archive'])]}}]

    def fetch(self, url, destination, limit):
        destination.write_text(json.dumps(self.listing if '/releases?' in url else self.manifest))

    def test_nested_project_path_is_encoded_as_one_api_id(self):
        self.assertEqual(repository_api(self.config.repository_url),
                         'https://gitlab.example/api/v4/projects/group%2Fsubgroup%2Frobot')
        with patch.object(self.updater, '_fetch', side_effect=self.fetch):
            result = self.updater.check()
        self.assertTrue(result['available'])
        self.assertTrue(result['_download_url'].endswith('/1.1.0.tar.gz'))

    def test_custom_api_path_is_confined_to_its_gitlab_installation(self):
        self.assertEqual(repository_api('https://host/gitlab/group/robot', 'https://host/gitlab/api/v4'),
                         'https://host/gitlab/api/v4/projects/group%2Frobot')
        for api in ('https://other/api/v4', 'https://host/wrong', 'https://user:secret@host/api/v4'):
            with self.assertRaises(ValueError):
                repository_api('https://host/group/robot', api)

    def test_upcoming_releases_are_not_selected(self):
        self.listing.append({'tag_name': 'paint_tray_dry/robot/v9.0.0', 'upcoming_release': True,
                             'assets': self.listing[0]['assets']})
        with patch.object(self.updater, '_fetch', side_effect=self.fetch):
            self.assertEqual(self.updater.check()['version'], '1.1.0')

    def test_external_release_link_is_rejected(self):
        self.listing[0]['assets']['links'][0]['direct_asset_url'] = 'https://other/manifest.json'
        with patch.object(self.updater, '_fetch', side_effect=self.fetch):
            with self.assertRaisesRegex(ValueError, 'configured server'):
                self.updater.check()

    def test_token_is_bearer_and_never_sent_to_another_server(self):
        token = self.fixture.directory / 'token'
        token.write_text('test-token')
        updater = PlatformUpdater(replace(self.config, token_file=token))
        with patch('urllib.request.build_opener') as build:
            build.return_value.open.return_value = io.BytesIO(b'asset')
            updater._fetch('https://gitlab.example/api/v4/projects/group%2Frobot/releases',
                           self.fixture.directory / 'download', 100)
            self.assertEqual(build.return_value.open.call_args.args[0].get_header('Authorization'), 'Bearer test-token')
            with self.assertRaisesRegex(ValueError, 'configured server'):
                updater._fetch('https://other/api/v4/releases', self.fixture.directory / 'download', 100)
