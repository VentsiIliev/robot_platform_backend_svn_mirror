import importlib.util
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

from src.bootstrap.kiosk_password import KioskPassword, write_password_file


ROOT = Path(__file__).resolve().parents[3]
PLATFORM_PACKAGING = ROOT / "packaging/platform"
sys.path.insert(0, str(PLATFORM_PACKAGING))
try:
    spec = importlib.util.spec_from_file_location(
        "platform_build", PLATFORM_PACKAGING / "build.py"
    )
    platform_build = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(platform_build)
finally:
    sys.path.remove(str(PLATFORM_PACKAGING))


class PlatformBuildKioskPasswordTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.directory = Path(temporary.name)
        self.source = self.directory / "source.json"
        self.destination = self.directory / "bundle/password.json"
        self.destination.parent.mkdir()
        write_password_file(self.source, "Shared kiosk password")

    def test_interactive_build_requires_explicit_use_choice(self):
        with patch.object(platform_build.sys.stdin, "isatty", return_value=True), \
             patch("builtins.input", return_value="u"):
            platform_build.confirm_kiosk_password(self.source)

        with patch.object(platform_build.sys.stdin, "isatty", return_value=True), \
             patch("builtins.input", return_value="q"):
            with self.assertRaisesRegex(RuntimeError, "cancelled"):
                platform_build.confirm_kiosk_password(self.source)

    def test_noninteractive_build_fails_closed_without_confirmation(self):
        with patch.object(platform_build.sys.stdin, "isatty", return_value=False), \
             patch.dict(os.environ, {}, clear=True):
            with self.assertRaisesRegex(RuntimeError, "PL_KIOSK_PASSWORD_CONFIRMED"):
                platform_build.confirm_kiosk_password(self.source)

    def test_confirmed_hash_is_staged_and_remains_valid(self):
        with patch.object(platform_build, "DEFAULT_KIOSK_PASSWORD_FILE", self.source), \
             patch.object(platform_build.sys.stdin, "isatty", return_value=False), \
             patch.dict(os.environ, {"PL_KIOSK_PASSWORD_CONFIRMED": "1"}, clear=True):
            password_source = platform_build.prepare_kiosk_password()
            platform_build.stage_kiosk_password(self.destination, password_source)

        self.assertEqual(self.destination.read_bytes(), self.source.read_bytes())
        self.assertTrue(KioskPassword(self.destination).verify("Shared kiosk password"))


if __name__ == "__main__":
    unittest.main()
