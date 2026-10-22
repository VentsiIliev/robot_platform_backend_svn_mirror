"""Public import and serializer error contracts for settings repositories."""
import unittest
from unittest.mock import Mock
from src.engine.repositories.interfaces import SettingsSaveError
from src.engine.repositories.json import BaseJsonSettingsRepository


class TestBaseJsonSettingsRepository(unittest.TestCase):
    def test_serializer_failure_is_save_error_without_file_creation(self):
        serializer = Mock()
        serializer.to_dict.side_effect = ValueError('bad value')
        repo = BaseJsonSettingsRepository(serializer, '/not-used/config.json')
        with self.assertRaises(SettingsSaveError):
            repo.save(object())

    def test_exists_without_path(self):
        self.assertFalse(BaseJsonSettingsRepository(Mock()).exists())
