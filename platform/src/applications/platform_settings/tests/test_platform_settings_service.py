import json
from pathlib import Path
import tempfile
import unittest

from src.applications.platform_settings.service.platform_settings_service import (
    PlatformSettingsService,
)
from src.applications.base.config.virtual_keyboard_config import (
    is_custom_virtual_keyboard_enabled,
    set_custom_virtual_keyboard_enabled,
)


class PlatformSettingsServiceTest(unittest.TestCase):
    def test_persists_virtual_keyboard_without_losing_other_config(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "platform.json"
            path.write_text(
                json.dumps({"robot_system": "paint", "ui": {"fullscreen": True}}),
                encoding="utf-8",
            )
            service = PlatformSettingsService(path)

            service.set_virtual_keyboard_enabled(False)

            payload = json.loads(path.read_text(encoding="utf-8"))
            self.assertEqual(payload["robot_system"], "paint")
            self.assertTrue(payload["ui"]["fullscreen"])
            self.assertFalse(service.is_virtual_keyboard_enabled())

    def test_updates_runtime_policy_immediately(self) -> None:
        original = is_custom_virtual_keyboard_enabled()
        try:
            with tempfile.TemporaryDirectory() as directory:
                service = PlatformSettingsService(Path(directory) / "platform.json")
                service.set_virtual_keyboard_enabled(not original)
                self.assertEqual(
                    is_custom_virtual_keyboard_enabled(),
                    not original,
                )
        finally:
            set_custom_virtual_keyboard_enabled(original)


if __name__ == "__main__":
    unittest.main()
