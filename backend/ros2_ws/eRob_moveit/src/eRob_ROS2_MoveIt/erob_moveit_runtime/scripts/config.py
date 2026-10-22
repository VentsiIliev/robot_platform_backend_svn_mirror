#!/usr/bin/env python3
"""Runtime configuration loader for eRob MoveIt packages.

Robot-specific values live in <robot_config_package>/config/runtime.yaml and
dedicated motion configuration files beside it. Active-profile overrides live
under config/<profile>/. ZeroErr profiles explicitly compose component files,
expand a profile-owned Xacro and persist calibration separately. This module
preserves the cfg.CONSTANT access pattern.
"""

from __future__ import annotations

import os
import math
from pathlib import Path
from typing import Any

import yaml


REQUIRED_KEYS = frozenset({
    'ROBOT_BACKEND',
    'NUM_JOINTS',
    'JOINT_NAMES',
    'PLANNING_GROUP',
    'BASE_LINK',
    'EE_LINK',
    'WRIST_LINK',
    'CARTESIAN_SOURCE_LINK',
    'COLLISION_TIP_LINK',
    'URDF_PATH',
    'ACTION_FOLLOW_TRAJECTORY',
    'REST_LOG',
})


def _config_package() -> str:
    package_name = os.environ.get('EROB_CONFIG_PACKAGE', '').strip()
    if not package_name:
        raise RuntimeError(
            'EROB_CONFIG_PACKAGE is not set. '
            'Launch the runtime through a robot-specific launch file or set '
            'EROB_CONFIG_PACKAGE explicitly.'
        )
    return package_name


def _runtime_yaml_path() -> Path | None:
    package_name = _config_package()
    try:
        from ament_index_python.packages import get_package_share_directory
        return Path(get_package_share_directory(package_name)) / 'config' / 'runtime.yaml'
    except Exception:
        source_root = Path(__file__).resolve().parents[2]
        candidate = source_root / package_name / 'config' / 'runtime.yaml'
        return candidate if candidate.exists() else None


def _profile_runtime_yaml_path(profile: str) -> Path | None:
    package_name = _config_package()
    try:
        from ament_index_python.packages import get_package_share_directory
        candidate = Path(get_package_share_directory(package_name)) / 'config' / profile / 'runtime.yaml'
        return candidate if candidate.exists() else None
    except Exception:
        source_root = Path(__file__).resolve().parents[2]
        candidate = source_root / package_name / 'config' / profile / 'runtime.yaml'
        return candidate if candidate.exists() else None


def _config_yaml_path(filename: str) -> Path | None:
    package_name = _config_package()
    try:
        from ament_index_python.packages import get_package_share_directory
        candidate = Path(get_package_share_directory(package_name)) / 'config' / filename
        return candidate if candidate.exists() else None
    except Exception:
        source_root = Path(__file__).resolve().parents[2]
        candidate = source_root / package_name / 'config' / filename
        return candidate if candidate.exists() else None


def _profile_config_yaml_path(profile: str, filename: str) -> Path | None:
    package_name = _config_package()
    try:
        from ament_index_python.packages import get_package_share_directory
        candidate = Path(get_package_share_directory(package_name)) / 'config' / profile / filename
        return candidate if candidate.exists() else None

    except Exception:
        source_root = Path(__file__).resolve().parents[2]
        candidate = source_root / package_name / 'config' / profile / filename
        return candidate if candidate.exists() else None


def resolve_limit_profile(profile_name: str) -> dict[str, float]:
    """Load a named per-segment joint-rate profile from the active config package."""
    name = str(profile_name or '').strip()
    if not name:
        return {}
    active_profile = str(_CONFIG.get('ACTIVE_PROFILE', globals().get('ACTIVE_PROFILE', '')) or '').strip()
    path = _profile_config_yaml_path(active_profile, 'trajectory_limits.yaml') if active_profile else None
    if not path or not path.exists():
        raise RuntimeError(
            f"Requested limit_profile '{name}', but trajectory_limits.yaml is missing "
            f"for active profile '{active_profile or '<none>'}'"
        )
    document = _load_yaml_file(path)
    profiles = document.get('profiles')
    if not isinstance(profiles, dict) or name not in profiles:
        raise RuntimeError(f"Requested limit_profile '{name}' is not defined in {path}")
    entry = profiles[name]
    if not isinstance(entry, dict) or not isinstance(entry.get('joint_rate_limits_rad_s'), dict):
        raise RuntimeError(f"Limit profile '{name}' in {path} must define joint_rate_limits_rad_s")
    limits = {}
    for joint, raw_limit in entry['joint_rate_limits_rad_s'].items():
        try:
            limit = float(raw_limit)
        except (TypeError, ValueError):
            raise RuntimeError(f"Limit profile '{name}' has invalid rate for joint '{joint}'") from None
        if limit <= 0.0 or not math.isfinite(limit):
            raise RuntimeError(f"Limit profile '{name}' has non-positive rate for joint '{joint}'")
        limits[str(joint)] = limit
    if not limits:
        raise RuntimeError(f"Limit profile '{name}' contains no joint rate limits")
    return limits


def apply_limit_profiles(segments, logger=None):
    """Validate and attach requested profiles before ordered planning starts."""
    for index, segment in enumerate(segments):
        name = segment.get('limit_profile')
        if not name:
            continue
        limits = resolve_limit_profile(name)
        segment['_joint_rate_limits_rad_s'] = limits
        if logger:
            logger.info(f"[OrderedLimits] segment={index + 1} profile={name} limits={limits}")
def _load_yaml_file(path: Path) -> dict[str, Any]:
    if _config_package() == 'zeroerr':
        from zeroerr_configuration import load_yaml_layers
        return load_yaml_layers(path)
    with path.open('r', encoding='utf-8') as handle:
        return yaml.safe_load(handle) or {}


def _merge(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    result = dict(base)
    for key, value in override.items():
        if isinstance(value, dict) and isinstance(result.get(key), dict):
            merged = dict(result[key])
            merged.update(value)
            result[key] = merged
        else:
            result[key] = value
    return result


def _resolve_config_path(config_yaml: Path, value: Any) -> str:
    path = str(value or '').strip()
    if not path:
        return ''
    if path.startswith('package://'):
        package_and_rel = path[len('package://'):]
        package_name, _, rel_path = package_and_rel.partition('/')
        if package_name and rel_path:
            from ament_index_python.packages import get_package_share_directory
            return str(Path(get_package_share_directory(package_name)) / rel_path)
    candidate = Path(path).expanduser()
    if candidate.is_absolute():
        return str(candidate)
    return str((config_yaml.parent / candidate).resolve())


PATH_KEYS = frozenset({
    'URDF_PATH',
    'SRDF_PATH',
})


def _load_runtime_config() -> dict[str, Any]:
    defaults_path = _config_yaml_path('runtime_defaults.yaml')
    defaults = (
        _load_yaml_file(defaults_path)
        if defaults_path and defaults_path.exists()
        else {}
    )
    path = _runtime_yaml_path()
    if not path or not path.exists():
        return defaults
    active_path = path
    loaded = _load_yaml_file(path)
    config = _merge(defaults, loaded)

    for filename in (
        'contour_ik_config.yaml',
        'ptp_config.yaml',
        'jacobian_config.yaml',
        'unwind_config.yaml',
        'cartesian_servo_config.yaml',
    ):
        config_path = _config_yaml_path(filename)
        if config_path and config_path.exists():
            config = _merge(config, _load_yaml_file(config_path))

    if _config_package() == 'zeroerr' and 'ZEROERR_ACTIVE_PROFILE' in os.environ:
        requested = os.environ['ZEROERR_ACTIVE_PROFILE']
        if not requested or '/' in requested or '..' in requested:
            raise RuntimeError('Invalid ZEROERR_ACTIVE_PROFILE')
        config['ACTIVE_PROFILE'] = requested
    profile = str(config.get('ACTIVE_PROFILE', '')).strip()
    if profile:
        profile_path = _profile_runtime_yaml_path(profile)
        if not profile_path or not profile_path.exists():
            raise RuntimeError(
                f"Runtime config {path} requested ACTIVE_PROFILE '{profile}', "
                "but no profile runtime.yaml was found"
            )
        config = _merge(config, _load_yaml_file(profile_path))
        active_path = profile_path
        for filename in (
            'contour_ik_config.yaml',
            'ptp_config.yaml',
            'jacobian_config.yaml',
            'unwind_config.yaml',
            'cartesian_servo_config.yaml',
        ):
            profile_config_path = _profile_config_yaml_path(profile, filename)
            if profile_config_path and profile_config_path.exists():
                config = _merge(config, _load_yaml_file(profile_config_path))

    if _config_package() == 'zeroerr':
        from zeroerr_configuration.sensorless_collision import runtime_settings, load_sensorless_config
        sensorless = runtime_settings(path.parent.parent, profile)
        duplicates = set(config).intersection(sensorless)
        if duplicates:
            raise ValueError(f'Sensorless settings must live in the profile sensorless_collision.yaml: {sorted(duplicates)}')
        config = _merge(config, sensorless)
        config['_SENSORLESS_COLLISION_STARTUP'] = load_sensorless_config(sensorless['SENSORLESS_COLLISION_CONFIG_PATH'])

    for key in PATH_KEYS:
        if key in config and config[key]:
            config[key] = _resolve_config_path(active_path, config[key])

    if str(config.get('URDF_PATH', '')).endswith('.xacro'):
        from zeroerr_configuration import resolve_robot_description
        config['URDF_PATH'] = resolve_robot_description(active_path, config)
    if config.get('CALIBRATION_PATH'):
        config['_CALIBRATION_CONFIG_PATH'] = _resolve_config_path(active_path, config['CALIBRATION_PATH'])

    missing = sorted(key for key in REQUIRED_KEYS if key not in config or config[key] in (None, ''))
    if missing:
        raise RuntimeError(
            f"Runtime config {path} is missing required keys: {', '.join(missing)}"
        )
    config['_RUNTIME_CONFIG_PATH'] = str(path)
    config['_ACTIVE_RUNTIME_CONFIG_PATH'] = str(active_path)
    config['WALL_BYPASS_LINKS'] = frozenset(config.get('WALL_BYPASS_LINKS', []))
    config['SAFETY_WALL_NAMES'] = frozenset(config.get('SAFETY_WALL_NAMES', []))
    if 'TOOL_DEFINITIONS' in config:
        from configuration.domain import tool_snapshot
        canonical = {key: value for key, value in config.items()
                     if key not in {'TOOL_REGISTRY', 'TOOL_COLLISION_PROFILE_MAP'}}
        tools = tool_snapshot(canonical)
        config['TOOL_REGISTRY'] = tools['tool_registry']
        config['TOOL_COLLISION_PROFILE_MAP'] = tools['tool_collision_profile_map']
    config['TOOL_ID_MAP'] = {int(k): v for k, v in dict(config.get('TOOL_ID_MAP', {})).items()}
    config['WORKOBJECT_ID_MAP'] = {int(k): v for k, v in dict(config.get('WORKOBJECT_ID_MAP', {})).items()}
    default_workobject = list(config.get('DEFAULT_WORKOBJECT', [0, 0, 0, 0, 0, 0]) or [0, 0, 0, 0, 0, 0])
    if not config.get('WORKOBJECT_REGISTRY'):
        default_user_id = int(config.get('DEFAULT_WORKOBJECT_ID', 0) or 0)
        default_name = f'WOBJ_{default_user_id}'
        config['WORKOBJECT_REGISTRY'] = {default_name: default_workobject}
        config['WORKOBJECT_ID_MAP'] = {default_user_id: default_name}
    if 0 not in config['WORKOBJECT_ID_MAP']:
        config['WORKOBJECT_ID_MAP'][0] = 'WOBJ_0'
    if 'WOBJ_0' not in config['WORKOBJECT_REGISTRY']:
        config['WORKOBJECT_REGISTRY']['WOBJ_0'] = [0, 0, 0, 0, 0, 0]
    return config


_CONFIG = _load_runtime_config()
# Transport endpoints are installation-level settings, never robot/profile overrides.
from backend_network import load_backend_network
_NETWORK = load_backend_network()
_CONFIG.update({
    'REST_HOST': _NETWORK.bind_host,
    'REST_PORT': _NETWORK.http_port,
    'REST_WS_STATE_HOST': _NETWORK.bind_host,
    'REST_WS_STATE_PORT': _NETWORK.state_ws_port,
    'REST_WS_EXECUTION_HOST': _NETWORK.bind_host,
    'REST_WS_EXECUTION_PORT': _NETWORK.execution_ws_port,
    'REST_WS_SENSOR_HOST': _NETWORK.bind_host,
    'REST_WS_SENSOR_PORT': _NETWORK.sensor_ws_port,
})
globals().update(_CONFIG)


def resolve_avoid_collisions(requested_value):
    """Resolve avoid_collisions flag based on global ENABLE_COLLISION_CHECKING.

    If ENABLE_COLLISION_CHECKING is False, always return False (disable all collision checks).
    Otherwise, use the requested_value (which may be None for default behavior).
    """
    if not _CONFIG.get('ENABLE_COLLISION_CHECKING', True):
        return False
    if requested_value is None:
        return _CONFIG.get('JOG_AVOID_COLLISIONS', True)
    return requested_value


def get_tool_registry_snapshot() -> dict[str, Any]:
    return {
        'tool_registry': {
            str(name): [float(v) for v in values]
            for name, values in dict(TOOL_REGISTRY).items()
        },
        'tool_id_map': {
            int(tool_id): str(name)
            for tool_id, name in dict(TOOL_ID_MAP).items()
        },
        'tool_collision_profile_map': dict(
            _CONFIG.get('TOOL_COLLISION_PROFILE_MAP', {}) or {}
        ),
        'tool_collision_profiles': dict(
            _CONFIG.get('TOOL_COLLISION_PROFILES', {}) or {}
        ),
        'active_runtime_config_path': _CONFIG.get('_ACTIVE_RUNTIME_CONFIG_PATH'),
        'calibration_config_path': _CONFIG.get('_CALIBRATION_CONFIG_PATH') or _CONFIG.get('_ACTIVE_RUNTIME_CONFIG_PATH'),
    }


def resolve_tool_name(tool_id: int | str) -> str:
    try:
        resolved_tool_id = int(tool_id)
    except (TypeError, ValueError):
        raise ValueError('tool_id must be an integer') from None
    if resolved_tool_id < 0:
        raise ValueError('tool_id must be non-negative')
    tool_name = TOOL_ID_MAP.get(resolved_tool_id, f'TOOL_{resolved_tool_id}')
    if tool_name not in TOOL_REGISTRY:
        raise ValueError(f'tool_id {resolved_tool_id} maps to unknown tool {tool_name!r}')
    return tool_name


def _validate_tool_transform(transform) -> list[float]:
    if not isinstance(transform, (list, tuple)) or len(transform) != 6:
        raise ValueError('transform must contain exactly 6 values [x, y, z, rx, ry, rz]')
    values = []
    for value in transform:
        try:
            parsed = float(value)
        except (TypeError, ValueError):
            raise ValueError('transform values must be numeric') from None
        if not (parsed == parsed and parsed not in (float('inf'), float('-inf'))):
            raise ValueError('transform values must be finite')
        values.append(parsed)
    return values


def _validate_tool_name(name: str) -> str:
    cleaned = str(name or '').strip()
    if not cleaned:
        raise ValueError('tool name must not be empty')
    if not all(ch.isalnum() or ch == '_' for ch in cleaned):
        raise ValueError('tool name may contain only letters, numbers, and underscores')
    return cleaned


def update_tool_registry(tool_id, name, transform, persist=False, collision_profile=None):
    """Compatibility entry point. Profile writes use the configuration application."""
    if not persist:
        raise ValueError('Volatile registry edits are unsupported; use the profile configuration API')
    from configuration.bootstrap import build_configuration_service
    from types import SimpleNamespace
    service = build_configuration_service(SimpleNamespace(_CONFIG=_CONFIG, **_CONFIG))
    changes = {'transform': transform}
    if name is not None:
        changes['name'] = name
    if collision_profile is not None:
        changes['collision_profile'] = collision_profile
    view = service.get('calibration')
    return service.update('calibration', changes, view['revision'], tool_id=tool_id)


def get_workobject_registry_snapshot() -> dict[str, Any]:
    return {
        'workobject_registry': {
            str(name): [float(v) for v in values]
            for name, values in dict(WORKOBJECT_REGISTRY).items()
        },
        'workobject_id_map': {
            int(user_id): str(name)
            for user_id, name in dict(WORKOBJECT_ID_MAP).items()
        },
        'default_workobject_id': int(_CONFIG.get('DEFAULT_WORKOBJECT_ID', 0) or 0),
        'active_runtime_config_path': _CONFIG.get('_ACTIVE_RUNTIME_CONFIG_PATH'),
        'calibration_config_path': _CONFIG.get('_CALIBRATION_CONFIG_PATH') or _CONFIG.get('_ACTIVE_RUNTIME_CONFIG_PATH'),
    }


def resolve_workobject_name(user_id: int | str) -> str:
    try:
        resolved_user_id = int(user_id)
    except (TypeError, ValueError):
        raise ValueError('user_id must be an integer') from None
    if resolved_user_id < 0:
        raise ValueError('user_id must be non-negative')
    workobject_name = WORKOBJECT_ID_MAP.get(resolved_user_id, f'WOBJ_{resolved_user_id}')
    if workobject_name not in WORKOBJECT_REGISTRY:
        raise ValueError(f'user_id {resolved_user_id} maps to unknown workobject {workobject_name!r}')
    return workobject_name


def _validate_workobject_transform(transform) -> list[float]:
    return _validate_tool_transform(transform)


def _validate_workobject_name(name: str) -> str:
    cleaned = str(name or '').strip()
    if not cleaned:
        raise ValueError('workobject name must not be empty')
    if not all(ch.isalnum() or ch == '_' for ch in cleaned):
        raise ValueError('workobject name may contain only letters, numbers, and underscores')
    return cleaned


def update_workobject_registry(user_id, name, transform, persist=False):
    """Compatibility entry point. Save only; live application belongs to the runtime adapter."""
    if not persist:
        raise ValueError('Volatile registry edits are unsupported; use the profile configuration API')
    from configuration.bootstrap import build_configuration_service
    from types import SimpleNamespace
    service = build_configuration_service(SimpleNamespace(_CONFIG=_CONFIG, **_CONFIG))
    changes = {'transform': transform}
    if name is not None:
        changes['name'] = name
    view = service.get('calibration')
    return service.update('calibration', changes, view['revision'], user_id=user_id)
