from __future__ import annotations

import json
import os
from src.engine.diagnostics.config import DiagnosticsConfig
import re
from dataclasses import dataclass, field
from importlib import import_module
from pathlib import Path

from src.robot_systems.robot_system_bootstrap_provider import (
    RobotSystemBootstrapProvider,
)


_SYSTEM_NAME_PATTERN = re.compile(r"^[a-z][a-z0-9_]*$")
_PROVIDER_FACTORY_NAME = "create_bootstrap_provider"
DEFAULT_CONFIG_PATH = Path(__file__).resolve().parents[2] / "config" / "platform.json"


@dataclass(frozen=True)
class RosBackendConfig:
    auto_launch: bool = True
    auto_stop: bool = True
    launch_script: str | None = None
    stop_script: str | None = None
    startup_delay_s: float | None = None
    log_file: str | None = None
    status_urls: tuple[str, ...] | None = None
    status_timeout_s: float | None = None


@dataclass(frozen=True)
class UiStartupConfig:
    dev_skip_login: bool = False
    skip_splash: bool = False
    show_account_button_when_dev_skip_login: bool = False
    show_power_off_button: bool = False
    custom_virtual_keyboard_enabled: bool = True
    kiosk_mode: bool = False
    kiosk_password_file: str = "/etc/robot-platform/kiosk-password.json"
    fullscreen: bool = True
    window_width: int = 1280
    window_height: int = 1024


@dataclass(frozen=True)
class StartupConfig:
    robot_system: str
    supported_robot_systems: tuple[str, ...]
    ros_backend: RosBackendConfig = field(default_factory=RosBackendConfig)
    ui: UiStartupConfig = field(default_factory=UiStartupConfig)
    system_config: dict = field(default_factory=dict)
    diagnostics: DiagnosticsConfig = field(default_factory=DiagnosticsConfig)


def load_startup_config(config_path: Path = DEFAULT_CONFIG_PATH) -> StartupConfig:
    try:
        payload = json.loads(config_path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise RuntimeError(f"Startup configuration not found: {config_path}") from exc
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"Invalid startup configuration JSON: {config_path}") from exc

    if not isinstance(payload, dict):
        raise RuntimeError("Startup configuration must contain a JSON object")

    robot_system = _validate_system_name(payload.get("robot_system"), "robot_system")
    raw_supported = payload.get("supported_robot_systems")
    if not isinstance(raw_supported, list) or not raw_supported:
        raise RuntimeError(
            "'supported_robot_systems' must be a non-empty list"
        )

    supported_robot_systems = tuple(
        _validate_system_name(name, "supported_robot_systems")
        for name in raw_supported
    )
    if len(set(supported_robot_systems)) != len(supported_robot_systems):
        raise RuntimeError("'supported_robot_systems' must not contain duplicates")
    if robot_system not in supported_robot_systems:
        raise RuntimeError(
            f"Robot system '{robot_system}' is not listed in "
            "'supported_robot_systems'"
        )

    selected = load_robot_system_config(payload, robot_system)
    return StartupConfig(
        robot_system=robot_system,
        system_config=selected,
        supported_robot_systems=supported_robot_systems,
        ros_backend=_load_ros_backend_config(payload.get("ros_backend")),
        ui=_load_ui_startup_config(payload.get("ui")),
        diagnostics=DiagnosticsConfig.from_mapping(payload.get('diagnostics')),
    )


def load_robot_system_config(payload: dict, robot_system: str) -> dict:
    """Require an explicit, complete configuration for the selected system."""
    systems = payload.get("robot_systems")
    if not isinstance(systems, dict) or robot_system not in systems:
        raise RuntimeError(f"Missing configuration: robot_systems.{robot_system}")
    selected = systems[robot_system]
    if not isinstance(selected, dict):
        raise RuntimeError(f"robot_systems.{robot_system} must be a JSON object")
    for key in ("robot_driver", "backend", "backend_profile"):
        _validate_system_name(selected.get(key), f"robot_systems.{robot_system}.{key}")
    for key in ("release_version", "platform_version", "backend_version"):
        value = selected.get(key)
        if not isinstance(value, str) or not re.fullmatch(r"[0-9]+\.[0-9]+\.[0-9]+", value):
            raise RuntimeError(f"robot_systems.{robot_system}.{key} must be major.minor.patch")
    if selected["robot_driver"] not in ("zeroerr", "fairino"):
        raise RuntimeError(f"Unknown robot_driver for robot_systems.{robot_system}")
    if selected["backend"] not in ("zeroerr", "fairino"):
        raise RuntimeError(f"Unknown backend for robot_systems.{robot_system}")
    if selected["robot_driver"] != selected["backend"]:
        raise RuntimeError(f"robot_systems.{robot_system}: robot_driver must match backend")
    return dict(selected)


def _load_ros_backend_config(raw_config: object) -> RosBackendConfig:
    if raw_config is None:
        return RosBackendConfig()
    if not isinstance(raw_config, dict):
        raise RuntimeError("'ros_backend' must be a JSON object")
    return RosBackendConfig(
        auto_launch=_read_bool(raw_config, "auto_launch", default=True),
        auto_stop=_read_bool(raw_config, "auto_stop", default=True),
        launch_script=_read_optional_str(raw_config, "launch_script"),
        stop_script=_read_optional_str(raw_config, "stop_script"),
        startup_delay_s=_read_optional_float(raw_config, "startup_delay_s", minimum=0.0),
        log_file=_read_optional_str(raw_config, "log_file"),
        status_urls=_read_optional_str_tuple(raw_config, "status_urls"),
        status_timeout_s=_read_optional_float(raw_config, "status_timeout_s", minimum=0.0),
    )


def _load_ui_startup_config(raw_config: object) -> UiStartupConfig:
    if raw_config is None:
        return UiStartupConfig()
    if not isinstance(raw_config, dict):
        raise RuntimeError("'ui' must be a JSON object")
    kiosk_mode = _read_bool(raw_config, "kiosk_mode", default=False, prefix="ui")
    kiosk_override = os.environ.get("ROBOT_PLATFORM_KIOSK_MODE")
    if kiosk_override is not None:
        if kiosk_override != "1":
            raise RuntimeError("ROBOT_PLATFORM_KIOSK_MODE must be '1' when set")
        kiosk_mode = True
    return UiStartupConfig(
        dev_skip_login=_read_bool(raw_config, "dev_skip_login", default=False, prefix="ui"),
        skip_splash=_read_bool(raw_config, "skip_splash", default=False, prefix="ui"),
        show_account_button_when_dev_skip_login=_read_bool(
            raw_config,
            "show_account_button_when_dev_skip_login",
            default=False,
            prefix="ui",
        ),
        show_power_off_button=_read_bool(
            raw_config,
            "show_power_off_button",
            default=False,
            prefix="ui",
        ),
        custom_virtual_keyboard_enabled=_read_bool(
            raw_config,
            "custom_virtual_keyboard_enabled",
            default=True,
            prefix="ui",
        ),
        kiosk_password_file=_read_password_path(raw_config),
        kiosk_mode=kiosk_mode,
        fullscreen=_read_bool(raw_config, "fullscreen", default=True, prefix="ui"),
        window_width=_read_positive_int(raw_config, "window_width", default=1280, prefix="ui"),
        window_height=_read_positive_int(raw_config, "window_height", default=1024, prefix="ui"),
    )


def _read_bool(payload: dict, field_name: str, *, default: bool, prefix: str = "ros_backend") -> bool:
    value = payload.get(field_name, default)
    if not isinstance(value, bool):
        raise RuntimeError(f"'{prefix}.{field_name}' must be a boolean")
    return value


def _read_positive_int(payload: dict, field_name: str, *, default: int, prefix: str) -> int:
    value = payload.get(field_name, default)
    if not isinstance(value, int) or isinstance(value, bool) or value <= 0:
        raise RuntimeError(f"'{prefix}.{field_name}' must be a positive integer")
    return value


def _read_optional_str(payload: dict, field_name: str, *, prefix: str = "ros_backend") -> str | None:
    value = payload.get(field_name)
    if value is None:
        return None
    if not isinstance(value, str) or not value.strip():
        raise RuntimeError(f"'{prefix}.{field_name}' must be a non-empty string")
    return value


def _read_optional_float(
    payload: dict,
    field_name: str,
    *,
    prefix: str = "ros_backend",
    minimum: float,
) -> float | None:
    value = payload.get(field_name)
    if value is None:
        return None
    if not isinstance(value, (int, float)) or isinstance(value, bool) or value < minimum:
        raise RuntimeError(f"'{prefix}.{field_name}' must be a number >= {minimum:g}")
    return float(value)


def _read_optional_str_tuple(
    payload: dict,
    field_name: str,
    *,
    prefix: str = "ros_backend",
) -> tuple[str, ...] | None:
    value = payload.get(field_name)
    if value is None:
        return None
    if not isinstance(value, list) or not value:
        raise RuntimeError(f"'{prefix}.{field_name}' must be a non-empty list of strings")
    items = []
    for item in value:
        if not isinstance(item, str) or not item.strip():
            raise RuntimeError(f"'{prefix}.{field_name}' must be a non-empty list of strings")
        items.append(item.strip())
    return tuple(items)


def _validate_system_name(value: object, field_name: str) -> str:
    if not isinstance(value, str) or not _SYSTEM_NAME_PATTERN.fullmatch(value):
        raise RuntimeError(
            f"'{field_name}' entries must be lowercase identifiers containing only "
            "letters, numbers, and underscores"
        )
    return value


def load_bootstrap_provider(
    config: StartupConfig,
) -> RobotSystemBootstrapProvider:
    module_name = f"src.robot_systems.{config.robot_system}.bootstrap_provider"
    try:
        module = import_module(module_name)
    except ModuleNotFoundError as exc:
        if exc.name == module_name or (
            exc.name is not None and module_name.startswith(f"{exc.name}.")
        ):
            raise RuntimeError(
                f"Robot system '{config.robot_system}' is not installed"
            ) from exc
        raise

    factory = getattr(module, _PROVIDER_FACTORY_NAME, None)
    if not callable(factory):
        raise RuntimeError(
            f"Robot system '{config.robot_system}' must expose "
            f"{_PROVIDER_FACTORY_NAME}()"
        )

    provider = factory()
    if not isinstance(provider, RobotSystemBootstrapProvider):
        raise RuntimeError(
            f"{module_name}.{_PROVIDER_FACTORY_NAME}() returned an invalid provider"
        )
    return provider


def build_configured_robot(config: StartupConfig):
    """Both supported ROS backends expose the same platform bridge contract."""
    load_robot_system_config({"robot_systems": {config.robot_system: config.system_config}}, config.robot_system)
    from src.engine.robot.drivers.ros2_robot import Ros2Robot
    return Ros2Robot()


def _read_password_path(payload: dict) -> str:
    value = payload.get("kiosk_password_file", "/etc/robot-platform/kiosk-password.json")
    if not isinstance(value, str) or not Path(value).is_absolute():
        raise RuntimeError("ui.kiosk_password_file must be an absolute path")
    return value
