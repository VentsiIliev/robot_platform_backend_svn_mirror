import json
import grp
import os
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import Mock, patch
from src.bootstrap.kiosk_password import KioskPassword, write_password_file, main
from src.bootstrap.startup_config import _load_ui_startup_config

PASSWORD = 'Test-only password 123!'

class TestKioskPassword(unittest.TestCase):
    def setUp(self):
        self.directory = TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.path = Path(self.directory.name) / 'password.json'
        write_password_file(self.path, PASSWORD)

    def test_hash_roundtrip_and_no_plaintext(self):
        self.assertNotIn(PASSWORD, self.path.read_text())
        self.assertEqual(self.path.stat().st_mode & 0o777, 0o600)
        verifier = KioskPassword(self.path)
        self.assertTrue(verifier.verify(PASSWORD))
        self.assertFalse(verifier.verify('wrong'))
        self.assertFalse(verifier.verify(''))

    def test_salt_is_random_and_rotation(self):
        old = json.loads(self.path.read_text())
        write_password_file(self.path, PASSWORD)
        new = json.loads(self.path.read_text())
        self.assertNotEqual(old['salt'], new['salt'])
        write_password_file(self.path, 'Different test password!')
        verifier = KioskPassword(self.path)
        self.assertFalse(verifier.verify(PASSWORD))
        self.assertTrue(verifier.verify('Different test password!'))

    def test_missing_corrupt_and_permissions_fail_closed(self):
        for content in ('{}', 'not json'):
            self.path.write_text(content)
            with self.assertRaises((ValueError, KeyError)):
                KioskPassword(self.path)
        write_password_file(self.path, PASSWORD)
        self.path.chmod(0o666)
        with self.assertRaises(ValueError):
            KioskPassword(self.path)
        self.path.unlink()
        with self.assertRaises(FileNotFoundError):
            KioskPassword(self.path)

    def test_symlink_rejected(self):
        link = Path(self.directory.name) / 'link'
        link.symlink_to(self.path)
        with self.assertRaises(OSError):
            KioskPassword(link)

    def test_throttle_survives_new_dialog_and_expires(self):
        clock = Mock(return_value=10)
        verifier = KioskPassword(self.path, clock=clock)
        for _ in range(5):
            self.assertFalse(verifier.verify('wrong'))
        self.assertFalse(verifier.verify(PASSWORD))
        clock.return_value = 41
        self.assertTrue(verifier.verify(PASSWORD))

    def test_short_password_preserves_existing_hash(self):
        before = self.path.read_bytes()
        with self.assertRaises(ValueError):
            write_password_file(self.path, 'short')
        self.assertEqual(self.path.read_bytes(), before)

    def test_absolute_path_required(self):
        self.assertEqual(_load_ui_startup_config({}).kiosk_password_file,
                         '/etc/robot-platform/kiosk-password.json')
        for value in ('relative.json', '', None):
            with self.assertRaises(RuntimeError):
                _load_ui_startup_config({'kiosk_password_file': value})

    def test_cli_refuses_redirected_password_input(self):
        with patch('os.isatty', return_value=False), patch('getpass.getpass') as prompt:
            with self.assertRaises(SystemExit):
                main([])
            prompt.assert_not_called()

    def test_group_readable_file(self):
        group = grp.getgrgid(os.getgid()).gr_name
        write_password_file(self.path, PASSWORD, read_group=group)
        self.assertEqual(self.path.stat().st_mode & 0o777, 0o640)
        self.assertTrue(KioskPassword(self.path).verify(PASSWORD))

    def test_interactive_cli(self):
        with (patch('os.isatty', return_value=True),
              patch('getpass.getpass', side_effect=[PASSWORD, PASSWORD]),
              patch('builtins.print')):
            main(['--file', str(self.path)])
        self.assertTrue(KioskPassword(self.path).verify(PASSWORD))
