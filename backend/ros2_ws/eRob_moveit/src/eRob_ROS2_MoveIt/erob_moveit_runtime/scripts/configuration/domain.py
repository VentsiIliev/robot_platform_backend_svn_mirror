"""Configuration schemas and tool-frame resolution; independent of storage and transport."""
from copy import deepcopy
import math
import re

LIVE_MONITOR_FIELDS = frozenset({
    'detection_enabled', 'active_stop_enabled', 'diagnostics_enabled', 'dynamic_threshold_enabled',
    'collision_sensitivity_percent', 'confirm_duration_ms', 'dynamic_threshold_max_ratio',
    'dynamic_threshold_decay_sec', 'external_torque_thresholds',
})



class ConfigurationError(ValueError):
    code = 'invalid_configuration'
    status = 400


class Conflict(ConfigurationError):
    code = 'configuration_conflict'
    status = 409


class Unavailable(ConfigurationError):
    code = 'configuration_unavailable'
    status = 503


def identifier(value, label='id'):
    if type(value) is not int or value < 0:
        raise ConfigurationError(f'{label} must be a non-negative integer')
    return value


def transform(value):
    if not isinstance(value, (list, tuple)) or len(value) != 6:
        raise ConfigurationError('Transform must contain six numbers [mm, mm, mm, deg, deg, deg]')
    if any((isinstance(x, bool) or not isinstance(x, (int, float)) or (not math.isfinite(x)) for x in value)):
        raise ConfigurationError('Transform values must be finite numbers')
    return [float(x) for x in value]


def name(value):
    if not isinstance(value, str) or not re.fullmatch('[A-Za-z0-9_]+', value):
        raise ConfigurationError('Names must contain only letters, digits and underscores')
    return value


def rotation(angles):
    x, y, z = map(math.radians, angles)
    cx, sx, cy, sy, cz, sz = (math.cos(x), math.sin(x), math.cos(y), math.sin(y), math.cos(z), math.sin(z))
    return [[cy * cz, cz * sx * sy - cx * sz, cx * cz * sy + sx * sz], [cy * sz, cx * cz + sx * sy * sz, -cz * sx + cx * sy * sz], [-sy, cy * sx, cx * cy]]


def compose(reference, relative):
    """Preserve the existing platform translation-relative / Euler-offset convention."""
    matrix = rotation(reference[3:])
    return [reference[i] + sum((matrix[i][j] * relative[j] for j in range(3))) for i in range(3)] + [reference[i] + relative[i] for i in range(3, 6)]


def relative_to(reference, absolute):
    matrix = rotation(reference[3:])
    delta = [absolute[i] - reference[i] for i in range(3)]
    return [sum((matrix[j][i] * delta[j] for j in range(3))) for i in range(3)] + [absolute[i] - reference[i] for i in range(3, 6)]


def canonical_calibration(document):
    """Convert legacy absolute registries on explicit save, without changing any TCP."""
    if not isinstance(document, dict):
        raise ConfigurationError('Calibration must be a mapping')
    data = deepcopy(document)
    if 'TOOL_DEFINITIONS' in data and 'TOOL_REGISTRY' in data:
        raise ConfigurationError('Both canonical and legacy tool definitions are present')
    if 'TOOL_DEFINITIONS' not in data:
        if not isinstance(data.get('TOOL_REGISTRY'), dict):
            raise ConfigurationError('Tool registry must be a mapping')
        bindings = data.get('TOOL_COLLISION_PROFILE_MAP', {})
        if not isinstance(bindings, dict):
            raise ConfigurationError('Tool collision profile bindings must be a mapping')
        data['TOOL_DEFINITIONS'] = {key: {'transform': value, 'collision_profile': bindings.get(key, '')} for key, value in data.get('TOOL_REGISTRY', {}).items()}
    data.pop('TOOL_REGISTRY', None)
    data.pop('TOOL_COLLISION_PROFILE_MAP', None)
    ids = data.get('TOOL_ID_MAP', {})
    if not isinstance(ids, dict) or any((isinstance(k, bool) or not str(k).isdigit() for k in ids)):
        raise ConfigurationError('Tool ID map requires non-negative integer keys')
    data['TOOL_ID_MAP'] = {int(k): v for k, v in ids.items()}
    data['REFERENCE_TOOL_ID'] = data.get('REFERENCE_TOOL_ID', 1 if 1 in data['TOOL_ID_MAP'] else 0)
    objects = data.get('WORKOBJECT_ID_MAP', {})
    if not isinstance(objects, dict) or any((isinstance(k, bool) or not str(k).isdigit() for k in objects)):
        raise ConfigurationError('Work-object ID map requires non-negative integer keys')
    data['WORKOBJECT_ID_MAP'] = {int(k): v for k, v in objects.items()}
    validate_calibration(data)
    return data


def resolve_tools(data):
    definitions = data['TOOL_DEFINITIONS']
    ids = data['TOOL_ID_MAP']
    resolved = {}

    def resolve(key, stack=()):
        if key in stack:
            raise ConfigurationError('Tool reference cycle: ' + ' -> '.join((*stack, key)))
        if key in resolved:
            return resolved[key]
        if key not in definitions:
            raise ConfigurationError(f'Unknown tool reference {key}')
        item = definitions[key]
        if 'transform' in item:
            value = transform(item['transform'])
        else:
            ref = identifier(item.get('reference_tool_id'), 'reference_tool_id')
            if ref not in ids:
                raise ConfigurationError(f'Unknown reference tool id {ref}')
            value = compose(resolve(ids[ref], (*stack, key)), transform(item.get('relative_transform')))
        resolved[key] = transform(value)
        return value
    for key in definitions:
        resolve(key)
    return resolved


def validate_calibration(data):
    definitions = data.get('TOOL_DEFINITIONS')
    if not isinstance(definitions, dict) or not definitions:
        raise ConfigurationError('Tool definitions are required')
    ids = data.get('TOOL_ID_MAP')
    if not isinstance(ids, dict):
        raise ConfigurationError('Tool ID map is required')
    for key, item in definitions.items():
        name(key)
        if not isinstance(item, dict):
            raise ConfigurationError('Invalid tool definition')
        unknown = set(item) - {'transform', 'reference_tool_id', 'relative_transform', 'collision_profile'}
        if unknown:
            raise ConfigurationError(f'Unknown tool fields: {sorted(unknown)}')
        absolute = 'transform' in item
        relative = 'relative_transform' in item or 'reference_tool_id' in item
        if absolute == relative:
            raise ConfigurationError('Tool must have either absolute or relative geometry')
        if not isinstance(item.get('collision_profile', ''), str):
            raise ConfigurationError('collision_profile must be a string')
    for key, value in ids.items():
        identifier(key, 'tool_id')
        if not isinstance(value, str) or value not in definitions:
            raise ConfigurationError(f'Tool ID {key} references unknown tool {value}')
    if 0 not in ids or any((not isinstance(v, str) for v in ids.values())):
        raise ConfigurationError('Tool zero and valid tool names are required')
    reference = identifier(data.get('REFERENCE_TOOL_ID'), 'REFERENCE_TOOL_ID')
    if reference not in ids:
        raise ConfigurationError('Reference tool is not registered')
    resolve_tools(data)
    objects = data.get('WORKOBJECT_REGISTRY', {})
    if not isinstance(objects, dict):
        raise ConfigurationError('Work-object registry must be a mapping')
    for key, value in objects.items():
        name(key)
        transform(value)
    for key, value in data.get('WORKOBJECT_ID_MAP', {}).items():
        if isinstance(key, bool) or not str(key).isdigit():
            raise ConfigurationError('Invalid work-object id')
        if not isinstance(value, str) or value not in objects:
            raise ConfigurationError(f'Unknown work-object {value}')
    if 'DEFAULT_WORKOBJECT' in data:
        transform(data['DEFAULT_WORKOBJECT'])
    if 'DEFAULT_WORKOBJECT_ID' in data:
        default = identifier(data['DEFAULT_WORKOBJECT_ID'], 'DEFAULT_WORKOBJECT_ID')
        if default not in data.get('WORKOBJECT_ID_MAP', {}):
            raise ConfigurationError('Default work-object is not registered')


def tool_snapshot(data):
    data = canonical_calibration(data)
    absolute = resolve_tools(data)
    ids = data['TOOL_ID_MAP']
    refid = data['REFERENCE_TOOL_ID']
    reference = absolute[ids[refid]]
    definitions = {}
    for key, item in data['TOOL_DEFINITIONS'].items():
        definitions[key] = {**deepcopy(item), 'absolute_transform': absolute[key], 'reference_tool_id': item.get('reference_tool_id', refid), 'relative_transform': item.get('relative_transform', relative_to(reference, absolute[key]))}
    return dict(tool_registry=absolute, tool_id_map=ids, reference_tool_id=refid, tool_definitions=definitions, tool_collision_profile_map={k: v.get('collision_profile', '') for k, v in data['TOOL_DEFINITIONS'].items() if v.get('collision_profile')})


def edit_tool(data, tool_id, changes):
    identifier(tool_id, 'tool_id')
    if not isinstance(changes, dict) or not changes:
        raise ConfigurationError('Tool changes are required')
    unknown = set(changes) - {'name', 'transform', 'reference_tool_id', 'relative_transform', 'collision_profile'}
    if unknown:
        raise ConfigurationError(f'Unknown tool fields: {sorted(unknown)}')
    result = canonical_calibration(data)
    ids = result['TOOL_ID_MAP']
    old = ids.get(tool_id, f'TOOL_{tool_id}')
    key = name(changes['name'] if 'name' in changes else old)
    if key != old and key in result['TOOL_DEFINITIONS']:
        raise Conflict('Tool name already belongs to another definition')
    item = deepcopy(result['TOOL_DEFINITIONS'].get(old, {}))
    if 'transform' in changes:
        if 'reference_tool_id' in changes or 'relative_transform' in changes:
            raise ConfigurationError('Mixed absolute/relative geometry')
        item = {'transform': transform(changes['transform']), 'collision_profile': item.get('collision_profile', '')}
    elif 'relative_transform' in changes or 'reference_tool_id' in changes:
        if 'relative_transform' not in changes:
            raise ConfigurationError('relative_transform is required')
        item = {'reference_tool_id': identifier(changes.get('reference_tool_id', result['REFERENCE_TOOL_ID'])), 'relative_transform': transform(changes['relative_transform']), 'collision_profile': item.get('collision_profile', '')}
    if 'collision_profile' in changes:
        item['collision_profile'] = changes['collision_profile']
    if key != old:
        result['TOOL_DEFINITIONS'].pop(old, None)
        for mapped_id, mapped_name in list(ids.items()):
            if mapped_name == old:
                ids[mapped_id] = key
    result['TOOL_DEFINITIONS'][key] = item
    ids[tool_id] = key
    validate_calibration(result)
    return result


def edit_workobject(data, user_id, changes):
    identifier(user_id, 'user_id')
    if not isinstance(changes, dict) or set(changes) - {'name', 'transform'} or 'transform' not in changes:
        raise ConfigurationError('Work-object edits require transform and optional name')
    result = canonical_calibration(data)
    ids = {int(k): v for k, v in result.get('WORKOBJECT_ID_MAP', {}).items()}
    old = ids.get(user_id, f'WOBJ_{user_id}')
    key = name(changes['name'] if 'name' in changes else old)
    registry = result.setdefault('WORKOBJECT_REGISTRY', {})
    if key != old and key in registry:
        raise Conflict('Work-object name is already registered')
    registry[key] = transform(changes['transform'])
    if key != old:
        registry.pop(old, None)
        ids = {k: key if v == old else v for k, v in ids.items()}
    ids[user_id] = key
    result['WORKOBJECT_ID_MAP'] = ids
    validate_calibration(result)
    return result


def validate_patch(candidate, current, path=''):
    """Check known fields and structural types against the selected profile schema."""
    if isinstance(current, dict):
        if not isinstance(candidate, dict) or set(candidate) != set(current):
            raise ConfigurationError(f'Unknown or missing configuration fields at {path}')
        for key, value in candidate.items():
            validate_patch(value, current[key], f'{path}.{key}')
    elif isinstance(current, bool):
        if type(candidate) is not bool:
            raise ConfigurationError(f'{path} must be a boolean')
    elif isinstance(current, (int, float)):
        if isinstance(candidate, bool) or not isinstance(candidate, (int, float)) or (not math.isfinite(candidate)):
            raise ConfigurationError(f'{path} must be a finite number')
        if type(current) is int and type(candidate) is not int:
            raise ConfigurationError(f'{path} must be an integer')
    elif isinstance(current, list):
        if not isinstance(candidate, list) or (current and len(candidate) != len(current)):
            raise ConfigurationError(f'{path} has an invalid array length')
        for index, value in enumerate(candidate):
            validate_patch(value, current[index] if current else '', f'{path}[{index}]')
    elif type(candidate) is not type(current):
        raise ConfigurationError(f'{path} has an invalid type')


def validate_sensorless(candidate, current):
    validate_patch(candidate, current)
    if candidate.get('schema_version') != 1:
        raise ConfigurationError('Unsupported sensorless schema version')
    monitor = candidate['monitor']
    if monitor.get('collision_detection_suppressed') != current['monitor'].get('collision_detection_suppressed'):
        raise ConfigurationError('Use the transient suppression command instead of saving suppression state')
    bounds = {'collision_sensitivity_percent': (50, 200), 'confirm_duration_ms': (0, None), 'dynamic_threshold_max_ratio': (1, 20), 'dynamic_threshold_decay_sec': (0.01, None)}
    for key, (low, high) in bounds.items():
        value = monitor[key]
        if value < low or (high is not None and value > high):
            raise ConfigurationError(f'{key} is outside the supported range')
    if monitor.get('effort_following_error_detection_enabled') is not False:
        raise ConfigurationError('Effort/following-error detection is not supported by this controller')
    for key in ('external_torque_thresholds', 'effort_thresholds', 'following_error_thresholds'):
        values = monitor.get(key, {})
        values = values.values() if isinstance(values, dict) else values
        if any((value <= 0 for value in values)):
            raise ConfigurationError(f'{key} must be positive')
    for key, value in candidate['controller'].items():
        if isinstance(value, (int, float)) and (not isinstance(value, bool)) and (value < 0):
            raise ConfigurationError(f'controller.{key} must be non-negative')
    runtime = candidate['runtime']
    if runtime['EXECUTOR_COLLISION_STOP_STRATEGY'] not in {'measured_ruckig', 'planned_path'}:
        raise ConfigurationError('Unknown collision stop strategy')
    for key, value in runtime.items():
        if key.startswith('EXECUTOR_COLLISION_STOP_') and type(value) in (int, float) and (value <= 0):
            raise ConfigurationError(f'{key} must be positive')
    if runtime['EXECUTOR_COLLISION_STOP_DURATION_S'] > runtime['EXECUTOR_COLLISION_STOP_MAX_DURATION_S']:
        raise ConfigurationError('Collision stop duration exceeds its maximum')
    if not 0 <= candidate['controller']['filter_alpha'] <= 1:
        raise ConfigurationError('controller.filter_alpha must be between zero and one')
    if candidate['controller']['warmup_min_samples'] < 1:
        raise ConfigurationError('controller.warmup_min_samples must be positive')
    if candidate['controller']['rearm_settle_sec'] < 0.1:
        raise ConfigurationError('controller.rearm_settle_sec must be at least 0.1')
    for key in ('observer_gain', 'plot_period_sec', 'timing_period_sec'):
        if candidate['controller'][key] <= 0:
            raise ConfigurationError(f'controller.{key} must be positive')
    if candidate['controller']['joints'] != current['controller']['joints']:
        raise ConfigurationError('Joint assignments belong to the robot description and cannot be edited here')
    names = candidate['controller']['joints']
    if any((value not in names for value in runtime['EXECUTOR_COLLISION_STOP_HOLD_JOINT_NAMES'])):
        raise ConfigurationError('Unknown joint in collision stop hold list')
