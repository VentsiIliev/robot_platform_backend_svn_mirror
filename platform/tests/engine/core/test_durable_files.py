import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from src.engine.core.durable_files import atomic_write_json, DurabilityError


class TestDurableFiles(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        self.path = self.root / 'data.json'
        self.path.write_text('{"old":true}')
        self.path.chmod(0o640)

    def test_old_file_survives_write_sync_and_replace_failures(self):
        for operation in ('tempfile.mkstemp', 'os.fsync', 'os.replace'):
            with self.subTest(operation=operation):
                with patch('src.engine.core.durable_files.' + operation, side_effect=OSError('failure')):
                    with self.assertRaises(OSError):
                        atomic_write_json(self.path, {'new': True})
                self.assertEqual(json.loads(self.path.read_text()), {'old': True})
                self.assertEqual(list(self.root.iterdir()), [self.path])

    def test_serialization_failure_never_touches_destination(self):
        for value in ({'x': object()}, {'x': float('nan')}, {'x': float('inf')}):
            with self.assertRaises((TypeError, ValueError)):
                atomic_write_json(self.path, value)
            self.assertEqual(json.loads(self.path.read_text()), {'old': True})

    def test_directory_sync_failure_reports_visible_replacement(self):
        with patch('src.engine.core.durable_files.sync_directory', side_effect=OSError('failure')):
            with self.assertRaises(DurabilityError) as error:
                atomic_write_json(self.path, {'new': True})
        self.assertTrue(error.exception.published)
        self.assertEqual(json.loads(self.path.read_text()), {'new': True})
        self.assertEqual(list(self.root.iterdir()), [self.path])

    def test_mode_and_owner_preserved_and_new_file_private(self):
        before = self.path.stat()
        atomic_write_json(self.path, {'new': True})
        after = self.path.stat()
        self.assertEqual(after.st_mode & 0o777, 0o640)
        self.assertEqual((after.st_uid, after.st_gid), (before.st_uid, before.st_gid))
        new = self.root / 'new.json'
        atomic_write_json(new, {})
        self.assertEqual(new.stat().st_mode & 0o777, 0o600)

    def test_symlink_not_replaced(self):
        link = self.root / 'link.json'
        link.symlink_to(self.path)
        with self.assertRaises(ValueError):
            atomic_write_json(link, {})
        self.assertEqual(json.loads(self.path.read_text()), {'old': True})

    def test_new_directory_entries_are_synced(self):
        from src.engine.core import durable_files
        nested = self.root / 'a/b/data.json'
        with patch.object(durable_files, 'sync_directory', wraps=durable_files.sync_directory) as sync:
            atomic_write_json(nested, {})
        paths = [call.args[0] for call in sync.call_args_list]
        self.assertIn(self.root, paths)
        self.assertIn(self.root / 'a', paths)
        self.assertIn(self.root / 'a/b', paths)
