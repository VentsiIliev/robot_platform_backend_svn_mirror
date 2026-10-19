from __future__ import annotations

import json
import logging
import os
from pathlib import Path
from typing import Callable


_LOGGER = logging.getLogger(__name__)
_DEFAULT_ENABLED = True
_CONFIG_PATH = Path(__file__).resolve().parents[4] / "config" / "platform.json"
_CHANGE_LISTENERS: list[Callable[[bool], None]] = []


def writable_ui_config_path() -> Path:
    """Return the durable UI override, or the source config during development."""
    data_root = os.environ.get("ROBOT_PLATFORM_DATA_ROOT")
    if data_root:
        return Path(data_root) / "platform" / "ui.json"
    return _CONFIG_PATH


def _read_enabled(config_path: Path) -> bool | None:
    try:
        payload = json.loads(config_path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return None
    except json.JSONDecodeError:
        _LOGGER.exception("Invalid platform UI configuration: %s", config_path)
        return None

    if not isinstance(payload, dict):
        return None
    ui_config = payload.get("ui", {})
    if not isinstance(ui_config, dict):
        return None
    value = ui_config.get("custom_virtual_keyboard_enabled")
    return value if isinstance(value, bool) else None


def load_custom_virtual_keyboard_enabled() -> bool:
    override_path = writable_ui_config_path()
    if override_path != _CONFIG_PATH:
        override = _read_enabled(override_path)
        if override is not None:
            return override
    configured = _read_enabled(_CONFIG_PATH)
    if configured is not None:
        return configured
    _LOGGER.warning("Virtual keyboard setting is unavailable; it remains enabled")
    return _DEFAULT_ENABLED


ENABLE_CUSTOM_VIRTUAL_KEYBOARD = load_custom_virtual_keyboard_enabled()


def is_custom_virtual_keyboard_enabled() -> bool:
    return ENABLE_CUSTOM_VIRTUAL_KEYBOARD


def set_custom_virtual_keyboard_enabled(enabled: bool) -> None:
    """Update the process-wide policy and notify active keyboard widgets."""
    if not isinstance(enabled, bool):
        raise ValueError("Virtual keyboard setting must be boolean")
    global ENABLE_CUSTOM_VIRTUAL_KEYBOARD
    if ENABLE_CUSTOM_VIRTUAL_KEYBOARD == enabled:
        return
    ENABLE_CUSTOM_VIRTUAL_KEYBOARD = enabled
    for callback in tuple(_CHANGE_LISTENERS):
        callback(enabled)


def register_virtual_keyboard_policy_listener(
    callback: Callable[[bool], None],
) -> None:
    if callback not in _CHANGE_LISTENERS:
        _CHANGE_LISTENERS.append(callback)
