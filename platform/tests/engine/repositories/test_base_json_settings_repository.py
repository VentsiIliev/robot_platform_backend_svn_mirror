import json
from pathlib import Path
import tempfile
import unittest
from dataclasses import dataclass
from unittest.mock import patch

from src.engine.repositories.interfaces import ISettingsSerializer, SettingsLoadError, SettingsSaveError
from src.engine.repositories.json.base_json_settings_repository import BaseJsonSettingsRepository
from src.engine.repositories.json.json_store import StoreStatus


@dataclass
class _Config:
    name: str = 'default'
    count: int = 0


class _Serializer(ISettingsSerializer):
    settings_type = 'test_config'
    def get_default(self):
        return _Config()
    def to_dict(self, value):
        return dict(name=value.name, count=value.count)
    def from_dict(self, data):
        return _Config(data.get('name', 'default'), data.get('count', 0))


class TestJsonSettings(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.path = Path(temp.name) / 'config.json'
        self.repo = BaseJsonSettingsRepository(_Serializer(), str(self.path))

    def test_required_missing_never_creates_defaults(self):
        with self.assertRaises(SettingsLoadError):
            self.repo.load()
        self.assertFalse(self.path.exists())
        self.assertEqual(self.repo.load_result().status, StoreStatus.MISSING)

    def test_optional_missing_returns_defaults_without_writing(self):
        repo = BaseJsonSettingsRepository(_Serializer(), str(self.path), required=False)
        self.assertEqual(repo.load(), _Config())
        self.assertFalse(self.path.exists())

    def test_unconfigured_required_rejected(self):
        with self.assertRaises(SettingsLoadError):
            BaseJsonSettingsRepository(_Serializer()).load()
        self.assertEqual(BaseJsonSettingsRepository(_Serializer(), required=False).load(), _Config())

    def test_invalid_files_preserved_and_never_fall_back(self):
        for content, status in [('', StoreStatus.EMPTY), ('{bad', StoreStatus.CORRUPT),
                                ('[]', StoreStatus.CORRUPT), ('null', StoreStatus.CORRUPT),
                                ('{"count": NaN}', StoreStatus.CORRUPT),
                                ('{"count":1,"count":2}', StoreStatus.CORRUPT)]:
            for required in (False, True):
                with self.subTest(content=content, required=required):
                    self.path.write_text(content)
                    repo = BaseJsonSettingsRepository(_Serializer(), str(self.path), required=required)
                    self.assertEqual(repo.load_result().status, status)
                    with self.assertRaises(SettingsLoadError):
                        repo.load()
                    self.assertEqual(self.path.read_text(), content)

    def test_inaccessible_and_invalid_encoding(self):
        with patch('pathlib.Path.read_text', side_effect=PermissionError('denied')):
            self.assertEqual(self.repo.load_result().status, StoreStatus.INACCESSIBLE)
            with self.assertRaises(SettingsLoadError):
                self.repo.load()
        self.path.write_bytes(b'\xff')
        self.assertEqual(self.repo.load_result().status, StoreStatus.CORRUPT)

    def test_round_trip_and_parent_creation(self):
        self.repo.file_path = str(self.path.parent / 'a/b/config.json')
        self.repo.save(_Config('saved', 7))
        self.assertEqual(self.repo.load(), _Config('saved', 7))
        self.assertTrue(self.repo.exists())

    def test_save_failure_preserves_previous_file(self):
        self.repo.save(_Config('old'))
        before = self.path.read_bytes()
        with patch('src.engine.core.durable_files.os.replace', side_effect=OSError('failed')):
            with self.assertRaises(SettingsSaveError) as error:
                self.repo.save(_Config('new'))
        self.assertFalse(error.exception.published)
        self.assertEqual(self.path.read_bytes(), before)

    def test_post_replace_failure_is_explicit(self):
        self.repo.save(_Config('old'))
        with patch('src.engine.core.durable_files.sync_directory', side_effect=OSError('sync failed')):
            with self.assertRaises(SettingsSaveError) as error:
                self.repo.save(_Config('new'))
        self.assertTrue(error.exception.published)
        self.assertEqual(self.repo.load().name, 'new')

    def test_serializer_failure_is_corrupt(self):
        self.path.write_text('{}')
        with patch.object(self.repo._serializer, 'from_dict', side_effect=ValueError('bad schema')):
            self.assertEqual(self.repo.load_result().status, StoreStatus.CORRUPT)

    def test_save_without_path_rejected(self):
        with self.assertRaises(SettingsSaveError):
            BaseJsonSettingsRepository(_Serializer()).save(_Config())
