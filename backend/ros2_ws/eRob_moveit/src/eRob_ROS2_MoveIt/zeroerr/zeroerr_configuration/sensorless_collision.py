"""Profile-owned sensorless settings; shared values are explicit includes, never saved copies."""
from __future__ import annotations

from copy import deepcopy
import json
import os
from pathlib import Path
import tempfile

import yaml


def _merge(base, override):
    result = deepcopy(base)
    for key, value in override.items():
        if isinstance(value, dict) and isinstance(result.get(key), dict):
            result[key] = _merge(result[key], value)
        else:
            result[key] = deepcopy(value)
    return result


def _raw(path):
    data = yaml.safe_load(Path(path).read_text(encoding='utf-8'))
    if not isinstance(data, dict):
        raise ValueError(f'Sensorless configuration must be a mapping: {path}')
    return data


def _load(path, stack=()):
    path = Path(path).resolve()
    if path in stack:
        raise ValueError(f'Sensorless configuration include cycle: {path}')
    data = _raw(path)
    includes = data.pop('RUNTIME_INCLUDES', [])
    if not isinstance(includes, list) or any(not isinstance(p, str) or not p for p in includes):
        raise ValueError(f'RUNTIME_INCLUDES must contain paths: {path}')
    result = {}
    for include in includes:
        result = _merge(result, _load(path.parent/include, (*stack, path)))
    return _merge(result, data)


def load_sensorless_config(path):
    data = _load(path)
    if type(data.get('schema_version')) is not int or data['schema_version'] != 1:
        raise ValueError(f'Unsupported sensorless schema_version: {path}')
    for section in ('controller', 'monitor', 'runtime'):
        if not isinstance(data.get(section), dict):
            raise ValueError(f'Missing sensorless section {section}: {path}')
    required = ('COLLISION_RESET_RECALIBRATE_ON_RELEASE',
                'EXECUTOR_COLLISION_STOP_ENABLED', 'EXECUTOR_COLLISION_STOP_STRATEGY',
                'EXECUTOR_COLLISION_STOP_SAMPLE_PERIOD_S', 'EXECUTOR_COLLISION_STOP_DURATION_S',
                'EXECUTOR_COLLISION_STOP_TRACKING_TOL_RAD', 'EXECUTOR_COLLISION_STOP_HOLD_JOINT_NAMES',
                'EXECUTOR_COLLISION_STOP_STATE_MAX_AGE_S',
                'EXECUTOR_COLLISION_STOP_GOAL_VELOCITY_TOL_RAD_S',
                'EXECUTOR_COLLISION_STOP_MAX_DURATION_S', 'EXECUTOR_COLLISION_STOP_MAX_TRAVEL_RAD')
    missing = set(required).difference(data['runtime'])
    if missing:
        raise ValueError(f'Missing sensorless runtime settings: {sorted(missing)}')
    return data


def profile_config_path(package_path, profile=None):
    package_path = Path(package_path)
    if profile is None:
        runtime = _raw(package_path/'config/runtime.yaml')
        profile = os.environ.get('ZEROERR_ACTIVE_PROFILE', runtime.get('ACTIVE_PROFILE'))
    if not isinstance(profile, str) or not profile or '/' in profile or '\\' in profile or '..' in profile:
        raise ValueError('Sensorless configuration requires a valid active profile')
    path = package_path/'config'/profile/'sensorless_collision.yaml'
    if not path.is_file():
        raise FileNotFoundError(f'Missing profile sensorless configuration: {path}')
    return path


def default_config_path():
    try:
        from ament_index_python.packages import get_package_share_directory
        package = Path(get_package_share_directory('zeroerr'))
    except ImportError:
        package = Path(__file__).resolve().parents[1]
    return profile_config_path(package)


def runtime_settings(package_path, profile=None):
    path = profile_config_path(package_path, profile)
    values = deepcopy(load_sensorless_config(path)['runtime'])
    values['SENSORLESS_COLLISION_CONFIG_PATH'] = str(path.resolve())
    return values


def read_monitor_config(path):
    """Preserve the established flat monitor API for GUI and fitting tools."""
    path = Path(path)
    if path.suffix.lower() == '.json':
        return json.loads(path.read_text(encoding='utf-8'))  # Explicit historical inputs only.
    return deepcopy(load_sensorless_config(path)['monitor'])


def _differences(values, inherited):
    result = {}
    for key, value in values.items():
        if key not in inherited:
            result[key] = deepcopy(value)
        elif isinstance(value, dict) and isinstance(inherited[key], dict):
            nested = _differences(value, inherited[key])
            if nested:
                result[key] = nested
        elif value != inherited[key]:
            result[key] = deepcopy(value)
    return result


def write_monitor_config(path, monitor):
    """Save only profile differences; inherited model values stay in their source file."""
    path = Path(path).resolve()
    if not isinstance(monitor, dict):
        raise ValueError('Monitor settings must be a mapping')
    if path.suffix.lower() == '.json':
        text = json.dumps(monitor, indent=2, allow_nan=False)+'\n'
    else:
        load_sensorless_config(path)  # Validate before writing.
        raw = _raw(path)
        inherited = {}
        for include in raw.get('RUNTIME_INCLUDES', []):
            inherited = _merge(inherited, _load(path.parent/include))
        baseline = inherited.get('monitor', {})
        overrides = _differences(monitor, baseline)
        if overrides:
            raw['monitor'] = overrides
        else:
            raw.pop('monitor', None)
        text = yaml.safe_dump(raw, sort_keys=False, allow_unicode=True)
    descriptor, temporary = tempfile.mkstemp(prefix='.'+path.name, dir=path.parent)
    try:
        with os.fdopen(descriptor, 'w', encoding='utf-8') as output:
            output.write(text)
            output.flush()
            os.fsync(output.fileno())
        os.chmod(temporary, path.stat().st_mode & 0o777)
        os.replace(temporary, path)
    finally:
        Path(temporary).unlink(missing_ok=True)
