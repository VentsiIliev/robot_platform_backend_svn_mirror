from __future__ import annotations

import json
import os
from pathlib import Path
import tempfile

from src.applications.base.config.virtual_keyboard_config import (
    is_custom_virtual_keyboard_enabled,
    set_custom_virtual_keyboard_enabled,
    writable_ui_config_path,
)
from .i_platform_settings_service import IPlatformSettingsService


class PlatformSettingsService(IPlatformSettingsService):
    def __init__(self, config_path: Path | None = None) -> None:
        self._config_path = config_path or writable_ui_config_path()

    def is_virtual_keyboard_enabled(self) -> bool:
        if self._config_path == writable_ui_config_path():
            return is_custom_virtual_keyboard_enabled()
        return self._read_enabled(self._config_path)

    def set_virtual_keyboard_enabled(self, enabled: bool) -> None:
        if not isinstance(enabled, bool):
            raise ValueError("Virtual keyboard setting must be boolean")
        payload = self._load_destination_payload()
        ui = payload.setdefault("ui", {})
        if not isinstance(ui, dict):
            raise ValueError("Platform configuration field 'ui' must be an object")
        ui["custom_virtual_keyboard_enabled"] = enabled
        self._atomic_write(payload)
        set_custom_virtual_keyboard_enabled(enabled)

    def _load_destination_payload(self) -> dict:
        if not self._config_path.exists():
            return {"ui": {}}
        try:
            payload = json.loads(self._config_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            raise ValueError(f"Invalid platform configuration: {self._config_path}") from exc
        if not isinstance(payload, dict):
            raise ValueError("Platform configuration must contain a JSON object")
        return payload

    @staticmethod
    def _read_enabled(path: Path) -> bool:
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except FileNotFoundError:
            return is_custom_virtual_keyboard_enabled()
        except json.JSONDecodeError as exc:
            raise ValueError(f"Invalid platform configuration: {path}") from exc
        value = payload.get("ui", {}).get("custom_virtual_keyboard_enabled")
        if not isinstance(value, bool):
            raise ValueError("ui.custom_virtual_keyboard_enabled must be boolean")
        return value

    def _atomic_write(self, payload: dict) -> None:
        self._config_path.parent.mkdir(parents=True, exist_ok=True)
        descriptor, temporary_name = tempfile.mkstemp(
            prefix=".ui-", suffix=".json", dir=self._config_path.parent
        )
        temporary = Path(temporary_name)
        try:
            with os.fdopen(descriptor, "w", encoding="utf-8") as stream:
                json.dump(payload, stream, indent=2)
                stream.write("\n")
                stream.flush()
                os.fsync(stream.fileno())
            os.replace(temporary, self._config_path)
        finally:
            temporary.unlink(missing_ok=True)
