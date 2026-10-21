"""Typed motion requests and normalization. No HTTP or ROS transport dependencies."""
from __future__ import annotations
from copy import deepcopy
from dataclasses import dataclass
from functools import wraps
import math
from typing import Any, TypedDict
from enums import Direction, RobotAxis
from motion.servo.cartesian_servo.i_cartesian_servo import CartesianServoFrame

@dataclass(frozen=True)
class MotionDefaults:
    velocity_percent: float = 30.0
    acceleration_percent: float = 30.0
    joint_names: tuple[str, ...] = tuple(f"Joint_{index}" for index in range(1, 7))

class MoveRequest(TypedDict):
    position: list[float]
    tool: int
    user: int
    vel: float
    acc: float
    blocking: bool
    trajectory_optimizer: str | None
    allow_collision_recovery: bool

class PathRequest(TypedDict):
    path: list[list[float]]
    rx: float | None
    ry: float | None
    rz: float | None
    vel: float
    acc: float
    blocking: bool
    trajectory_optimizer: str | None
    orientation_mode: str

class SequenceRequest(TypedDict):
    segments: list[dict[str, Any]]
    tool: int
    user: int
    blocking: bool

class OrderedChainRequest(SequenceRequest):
    trajectory_optimizer: str | None

class PreparedChainRequest(OrderedChainRequest):
    start_position: list[float]
    allow_servo_during_prepare: bool

class JogRequest(TypedDict):
    axis: RobotAxis
    direction: Direction
    step: float
    vel: float
    acc: float
    frame: CartesianServoFrame
    tool: int
    user: int

class JointJogRequest(TypedDict):
    joint: str
    direction: Direction
    step: float
    vel: float
    acc: float
    blocking: bool

class ServoJogRequest(TypedDict):
    axis: RobotAxis
    direction: Direction
    vel: float | None
    acc: float | None
    frame: CartesianServoFrame
    tool: int
    user: int
    linear_mm_s: float | None
    angular_deg_s: float | None
    disable_collision_checking: bool

class BoundedJogRequest(TypedDict):
    target_z_mm: float
    fast_linear_mm_s: float
    final_linear_mm_s: float
    slowdown_distance_mm: float
    tolerance_mm: float
    maximum_distance_mm: float
    timeout_s: float
    poll_interval_s: float
    frame: str
    tool: int
    user: int
    disable_collision_checking: bool

class CartesianServoStartRequest(TypedDict):
    frame: CartesianServoFrame
    tool: int
    user: int

class CartesianServoUpdateRequest(TypedDict):
    linear_mm_s: list[float]
    angular_deg_s: list[float]


def _finite_number(value, label: str) -> float:
    if isinstance(value, bool):
        raise ValueError(f'{label} must be a finite number, not a boolean')
    try:
        number = float(value)
    except (TypeError, ValueError, OverflowError) as error:
        raise ValueError(f'{label} must be a finite number') from error
    if not math.isfinite(number):
        raise ValueError(f'{label} must be a finite number')
    return number


def _identifier(value, label):
    if isinstance(value, str) and value.isascii() and value.isdigit():
        value = int(value)
    if type(value) is not int or value < 0:
        raise ValueError(f'{label} must be a non-negative integer')
    return value


def _typed_request(parser):
    @wraps(parser)
    def parse(data, *, defaults=MotionDefaults()):
        if data is not None and not isinstance(data, dict):
            raise ValueError('Request body must be a JSON object')
        original = data or {}
        def check_nested(value, path='request'):
            if isinstance(value, dict):
                for key, item in value.items():
                    check_nested(item, f'{path}.{key}')
            elif isinstance(value, (list, tuple)):
                for index, item in enumerate(value):
                    check_nested(item, f'{path}[{index}]')
            elif isinstance(value, (float, int)) and not isinstance(value, bool):
                _finite_number(value, path)
        check_nested(original)
        for name in ('axis', 'direction', 'frame'):
            if isinstance(original.get(name), bool):
                raise ValueError(f'{name} cannot be a boolean')
        for name in ('blocking', 'allow_collision_recovery', 'disable_collision_checking',
                     'restore_collision_checking', 'allow_servo_during_prepare', 'queue_if_busy'):
            if name in original and type(original[name]) is not bool:
                raise ValueError(f'{name} must be a boolean')
        for name in ('tool', 'user'):
            if name in original:
                _identifier(original[name], name)
        result = parser(data, defaults=defaults)
        for name in ('tool', 'user'):
            if name in result:
                result[name] = _identifier(result[name], name)
        for name in ('vel', 'acc'):
            if result.get(name) is not None:
                raw = original.get(name, result[name])
                result[name] = _finite_number(raw, name)
                if not 0 < result[name] <= 100:
                    raise ValueError(f'{name} must be greater than zero and at most 100 percent')
        for name in ('step', 'linear_mm_s', 'angular_deg_s', 'target_z', 'tolerance_mm', 'timeout_s', 'rx', 'ry', 'rz', 'target_z_mm', 'fast_linear_mm_s',
                     'final_linear_mm_s', 'slowdown_distance_mm', 'maximum_distance_mm', 'poll_interval_s'):
            if result.get(name) is not None and not isinstance(result[name], (list, tuple)):
                result[name] = _finite_number(original.get(name, result[name]), name)
                if name == 'step' and parser.__name__ == 'parse_jog_request' and result.get('axis') == RobotAxis.Z:
                    result[name] = -result[name]
        for name in ('position', 'start_position'):
            if result.get(name) is not None:
                result[name] = _coerce_pose6(original.get(name, result[name]), name)
        for name in ('linear_mm_s', 'angular_deg_s'):
            if isinstance(result.get(name), (list, tuple)):
                result[name] = [_finite_number(v, name) for v in original.get(name, result[name])]
        return result
    return parse

@_typed_request
def parse_jog_request(data: dict[str, Any] | None, *, defaults: MotionDefaults=MotionDefaults()) -> JogRequest:
    payload = data or {}
    axis_val = payload.get('axis')
    if axis_val is None:
        raise ValueError("Missing 'axis'")
    try:
        axis = RobotAxis.get_by_string(axis_val) if isinstance(axis_val, str) else RobotAxis(axis_val)
    except ValueError as exc:
        valid_axes = [axis.name for axis in RobotAxis]
        raise ValueError(f"Invalid 'axis': {axis_val}. Valid axes: {valid_axes}") from exc
    direction_val = payload.get('direction')
    if direction_val is None:
        raise ValueError("Missing 'direction'")
    try:
        if isinstance(direction_val, str):
            direction_name = direction_val.strip().upper()
            direction_aliases = {'POSITIVE': 'PLUS', 'NEGATIVE': 'MINUS'}
            direction = Direction.get_by_string(direction_aliases.get(direction_name, direction_name))
        else:
            direction = Direction(direction_val)
    except ValueError as exc:
        valid_directions = [direction.name for direction in Direction]
        raise ValueError(f"Invalid 'direction': {direction_val}. Valid directions: {valid_directions}") from exc
    try:
        step = float(payload.get('step'))
        vel = float(payload.get('vel'))
        acc = float(payload.get('acc'))
    except (TypeError, ValueError) as exc:
        raise ValueError('Invalid step/vel/acc') from exc
    if axis == RobotAxis.Z:
        step = -step
    frame_value = payload.get('frame', 'user')
    try:
        if isinstance(frame_value, int) or (isinstance(frame_value, str) and frame_value.strip().lstrip('-').isdigit()):
            frame = CartesianServoFrame.USER
            user = int(frame_value)
        else:
            frame = CartesianServoFrame(str(frame_value).strip().lower())
            user = int(payload.get('user', 0))
    except (TypeError, ValueError) as exc:
        valid_frames = [frame.value for frame in CartesianServoFrame]
        raise ValueError(f"Invalid 'frame': {frame_value}. Valid frames: {valid_frames} or numeric user frame id") from exc
    try:
        tool = int(payload.get('tool', 0))
    except (TypeError, ValueError) as exc:
        raise ValueError("Invalid 'tool'") from exc
    return {'axis': axis, 'direction': direction, 'step': step, 'vel': vel, 'acc': acc, 'frame': frame, 'tool': tool, 'user': user}

@_typed_request
def parse_joint_jog_request(data: dict[str, Any] | None, *, defaults: MotionDefaults=MotionDefaults()) -> JointJogRequest:
    payload = data or {}
    joint_value = payload.get('joint')
    if joint_value is None:
        raise ValueError("Missing 'joint'")
    joint = str(joint_value).strip()
    if not joint:
        raise ValueError("Invalid 'joint'")
    aliases = {f'J{index}': f'Joint_{index}' for index in range(1, 7)}
    joint = aliases.get(joint.upper(), joint)
    valid_joints = list(defaults.joint_names)
    if joint not in valid_joints:
        raise ValueError(f"Invalid 'joint': {joint_value}. Valid joints: {valid_joints}")
    direction_val = payload.get('direction')
    if direction_val is None:
        raise ValueError("Missing 'direction'")
    try:
        if isinstance(direction_val, str):
            direction_name = direction_val.strip().upper()
            direction_aliases = {'POSITIVE': 'PLUS', 'NEGATIVE': 'MINUS'}
            direction = Direction.get_by_string(direction_aliases.get(direction_name, direction_name))
        else:
            direction = Direction(direction_val)
    except ValueError as exc:
        valid_directions = [direction.name for direction in Direction]
        raise ValueError(f"Invalid 'direction': {direction_val}. Valid directions: {valid_directions}") from exc
    try:
        step = float(payload.get('step'))
        vel = float(payload.get('vel', defaults.velocity_percent))
        acc = float(payload.get('acc', defaults.acceleration_percent))
    except (TypeError, ValueError) as exc:
        raise ValueError('Invalid step/vel/acc') from exc
    return {'joint': joint, 'direction': direction, 'step': step, 'vel': vel, 'acc': acc, 'blocking': bool(payload.get('blocking', True))}

@_typed_request
def parse_servo_jog_start_request(data: dict[str, Any] | None, *, defaults: MotionDefaults=MotionDefaults()) -> ServoJogRequest:
    payload = data or {}
    axis_val = payload.get('axis')
    if axis_val is None:
        raise ValueError("Missing 'axis'")
    try:
        axis = RobotAxis.get_by_string(axis_val) if isinstance(axis_val, str) else RobotAxis(axis_val)
    except ValueError as exc:
        valid_axes = [axis.name for axis in RobotAxis]
        raise ValueError(f"Invalid 'axis': {axis_val}. Valid axes: {valid_axes}") from exc
    direction_val = payload.get('direction')
    if direction_val is None:
        raise ValueError("Missing 'direction'")
    try:
        if isinstance(direction_val, str):
            direction_name = direction_val.strip().upper()
            direction_aliases = {'POSITIVE': 'PLUS', 'NEGATIVE': 'MINUS'}
            direction = Direction.get_by_string(direction_aliases.get(direction_name, direction_name))
        else:
            direction = Direction(direction_val)
    except ValueError as exc:
        valid_directions = [direction.name for direction in Direction]
        raise ValueError(f"Invalid 'direction': {direction_val}. Valid directions: {valid_directions}") from exc
    linear_mm_s = payload.get('linear_mm_s')
    angular_deg_s = payload.get('angular_deg_s')
    vel = payload.get('vel')
    acc = payload.get('acc')
    try:
        linear_mm_s = None if linear_mm_s is None else float(linear_mm_s)
        angular_deg_s = None if angular_deg_s is None else float(angular_deg_s)
        vel = None if vel is None else float(vel)
        acc = None if acc is None else float(acc)
    except (TypeError, ValueError) as exc:
        raise ValueError('Invalid linear_mm_s/angular_deg_s/vel/acc') from exc
    if linear_mm_s is None and angular_deg_s is None and (vel is None):
        raise ValueError('Missing speed; provide linear_mm_s/angular_deg_s or vel')
    frame_value = payload.get('frame', 'user')
    try:
        if isinstance(frame_value, int) or (isinstance(frame_value, str) and frame_value.strip().lstrip('-').isdigit()):
            frame = CartesianServoFrame.USER
            user = int(frame_value)
        else:
            frame = CartesianServoFrame(str(frame_value).strip().lower())
            user = int(payload.get('user', 0))
    except (TypeError, ValueError) as exc:
        valid_frames = [frame.value for frame in CartesianServoFrame]
        raise ValueError(f"Invalid 'frame': {frame_value}. Valid frames: {valid_frames} or numeric user frame id") from exc
    try:
        tool = int(payload.get('tool', 0))
    except (TypeError, ValueError) as exc:
        raise ValueError("Invalid 'tool'") from exc
    disable_collision_checking = payload.get('disable_collision_checking', False)
    if not isinstance(disable_collision_checking, bool):
        raise ValueError("Invalid 'disable_collision_checking'; expected boolean")
    return {'axis': axis, 'direction': direction, 'vel': vel, 'acc': acc, 'linear_mm_s': linear_mm_s, 'angular_deg_s': angular_deg_s, 'frame': frame, 'tool': tool, 'user': user, 'disable_collision_checking': disable_collision_checking}

@_typed_request
def parse_servo_jog_to_z_request(data: dict[str, Any] | None, *, defaults: MotionDefaults=MotionDefaults()) -> BoundedJogRequest:
    payload = data or {}
    required = ('target_z_mm', 'fast_linear_mm_s', 'final_linear_mm_s', 'slowdown_distance_mm', 'tolerance_mm', 'maximum_distance_mm', 'timeout_s', 'poll_interval_s')
    try:
        values = {key: float(payload[key]) for key in required}
        values['tool'] = int(payload.get('tool', 0))
        values['user'] = int(payload.get('user', 0))
    except KeyError as exc:
        raise ValueError(f"Missing '{exc.args[0]}'") from exc
    except (TypeError, ValueError) as exc:
        raise ValueError('Invalid target-bounded ServoJog value') from exc
    values['frame'] = str(payload.get('frame', 'user')).strip().lower()
    collision = payload.get('disable_collision_checking', False)
    if not isinstance(collision, bool):
        raise ValueError("Invalid 'disable_collision_checking'; expected boolean")
    values['disable_collision_checking'] = collision
    return values

@_typed_request
def parse_move_linear_request(data: dict[str, Any] | None, *, defaults: MotionDefaults=MotionDefaults()) -> MoveRequest:
    payload = data or {}
    position = payload.get('position')
    if not position or len(position) != 6:
        raise ValueError('Invalid position format')
    trajectory_optimizer = payload.get('trajectory_optimizer')
    if trajectory_optimizer is not None:
        trajectory_optimizer = str(trajectory_optimizer).strip().upper()
        if trajectory_optimizer not in {'TOTG', 'RUCKIG'}:
            raise ValueError('Invalid trajectory_optimizer; expected TOTG or RUCKIG')
    return {'position': position, 'tool': payload.get('tool', 0), 'user': payload.get('user', 0), 'vel': payload.get('vel', defaults.velocity_percent), 'acc': payload.get('acc', defaults.acceleration_percent), 'blocking': payload.get('blocking', True), 'trajectory_optimizer': trajectory_optimizer, 'allow_collision_recovery': bool(payload.get('allow_collision_recovery', False))}

@_typed_request
def parse_execute_path_request(data: dict[str, Any] | None, *, defaults: MotionDefaults=MotionDefaults()) -> PathRequest:
    payload = data or {}
    path = payload.get('path')
    if not path:
        raise ValueError('No path provided')
    if isinstance(path, list) and path and isinstance(path[0], list) and path[0] and isinstance(path[0][0], list):
        path = path[0]
    trajectory_optimizer = payload.get('trajectory_optimizer')
    if trajectory_optimizer is not None:
        trajectory_optimizer = str(trajectory_optimizer).strip().upper()
        if trajectory_optimizer not in {'TOTG', 'RUCKIG'}:
            raise ValueError('Invalid trajectory_optimizer; expected TOTG or RUCKIG')
    orientation_mode = str(payload.get('orientation_mode', 'constant')).strip().lower()
    if orientation_mode not in {'constant', 'per_waypoint'}:
        raise ValueError('Invalid orientation_mode; expected constant or per_waypoint')
    return {'path': path, 'rx': payload.get('rx', payload.get('rx_degrees')), 'ry': payload.get('ry', payload.get('ry_degrees')), 'rz': payload.get('rz', payload.get('rz_degrees')), 'vel': payload.get('vel', defaults.velocity_percent), 'acc': payload.get('acc', defaults.acceleration_percent), 'blocking': payload.get('blocking', False), 'trajectory_optimizer': trajectory_optimizer, 'orientation_mode': orientation_mode}

@_typed_request
def parse_execute_sequence_request(data: dict[str, Any] | None, *, defaults: MotionDefaults=MotionDefaults()) -> SequenceRequest:
    payload = data or {}
    raw_segments = payload.get('segments')
    if not isinstance(raw_segments, list) or not raw_segments:
        raise ValueError("Missing non-empty 'segments'")
    segments = []
    for index, raw_segment in enumerate(raw_segments):
        if not isinstance(raw_segment, dict):
            raise ValueError(f'Invalid segment {index}: expected object')
        position = raw_segment.get('position')
        if not position or len(position) != 6:
            raise ValueError(f'Invalid segment {index}: position must have 6 values')
        motion_type = str(raw_segment.get('motion_type', 'linear')).strip().lower()
        if motion_type not in {'linear', 'ptp'}:
            raise ValueError(f'Invalid segment {index}: motion_type must be linear or ptp')
        try:
            vel = float(raw_segment.get('vel'))
            acc = float(raw_segment.get('acc'))
            blend_radius = float(raw_segment.get('blend_radius', 0.0))
        except (TypeError, ValueError) as exc:
            raise ValueError(f'Invalid segment {index}: vel/acc/blend_radius must be numeric') from exc
        segments.append({'position': deepcopy(position), 'vel': vel, 'acc': acc, 'motion_type': motion_type, 'blend_radius': blend_radius})
    return {'segments': segments, 'tool': int(payload.get('tool', 0)), 'user': int(payload.get('user', 0)), 'blocking': bool(payload.get('blocking', False))}

@_typed_request
def parse_execute_ordered_motion_chain_request(data: dict[str, Any] | None, *, defaults: MotionDefaults=MotionDefaults()) -> OrderedChainRequest:
    payload = data or {}
    raw_segments = payload.get('segments')
    if not isinstance(raw_segments, list) or not raw_segments:
        raise ValueError("Missing non-empty 'segments'")
    trajectory_optimizer = payload.get('trajectory_optimizer')
    if trajectory_optimizer is not None:
        trajectory_optimizer = str(trajectory_optimizer).strip().upper()
        if trajectory_optimizer not in {'TOTG', 'RUCKIG'}:
            raise ValueError('Invalid trajectory_optimizer; expected TOTG or RUCKIG')
    segments = []
    for index, raw_segment in enumerate(raw_segments):
        if not isinstance(raw_segment, dict):
            raise ValueError(f'Invalid segment {index}: expected object')
        segment_type = str(raw_segment.get('type') or raw_segment.get('kind') or '').strip().lower()
        if segment_type not in {'linear', 'ptp', 'path', 'unwind_joint6'}:
            raise ValueError(f'Invalid segment {index}: unsupported type {segment_type!r}')
        segment = {'type': segment_type, 'label': str(raw_segment.get('label') or f'segment_{index + 1}')}
        segment['protected'] = bool(raw_segment.get('protected', False))
        readiness_group = raw_segment.get('readiness_group')
        if readiness_group is not None:
            readiness_group = str(readiness_group).strip()
            if not readiness_group or any((ch not in 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_-' for ch in readiness_group)):
                raise ValueError(f'Invalid segment {index}: readiness_group must be a safe group name')
            segment['readiness_group'] = readiness_group
        execution_group = raw_segment.get('execution_group')
        if execution_group is not None:
            execution_group = str(execution_group).strip()
            if not execution_group or any((ch not in 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_-' for ch in execution_group)):
                raise ValueError(f'Invalid segment {index}: execution_group must be a safe group name')
            segment['execution_group'] = execution_group
        execution_policy = raw_segment.get('execution_policy')
        if execution_policy is not None:
            execution_policy = str(execution_policy).strip().lower()
            if execution_policy != 'concatenate':
                raise ValueError(f"Invalid segment {index}: execution_policy must be 'concatenate'")
            segment['execution_policy'] = execution_policy
        limit_profile = raw_segment.get('limit_profile')
        if limit_profile is not None:
            limit_profile = str(limit_profile).strip()
            if not limit_profile or any((ch not in 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_-' for ch in limit_profile)):
                raise ValueError(f'Invalid segment {index}: limit_profile must be a safe profile name')
            segment['limit_profile'] = limit_profile
        if segment_type in {'linear', 'ptp'}:
            position = raw_segment.get('position')
            if not position or len(position) != 6:
                raise ValueError(f'Invalid segment {index}: linear position must have 6 values')
            blend_r = float(raw_segment.get('blendR', 0.0) or 0.0)
            if blend_r < 0.0:
                raise ValueError(f'Invalid segment {index}: blendR must be >= 0')
            segment.update({'position': deepcopy(position), 'vel': float(raw_segment.get('vel', defaults.velocity_percent)), 'acc': float(raw_segment.get('acc', defaults.acceleration_percent)), 'blendR': blend_r})
        elif segment_type == 'path':
            path = raw_segment.get('path')
            if not path:
                raise ValueError(f'Invalid segment {index}: path is required')
            segment.update({'path': deepcopy(path), 'vel': float(raw_segment.get('vel', defaults.velocity_percent)), 'acc': float(raw_segment.get('acc', defaults.acceleration_percent))})
        elif segment_type == 'unwind_joint6':
            segment.update({'vel': float(raw_segment.get('vel', defaults.velocity_percent)), 'acc': float(raw_segment.get('acc', defaults.acceleration_percent)), 'queue_if_busy': bool(raw_segment.get('queue_if_busy', True))})
        segments.append(segment)
    return {'segments': segments, 'tool': int(payload.get('tool', 0)), 'user': int(payload.get('user', 0)), 'blocking': bool(payload.get('blocking', True)), 'trajectory_optimizer': trajectory_optimizer}

@_typed_request
def parse_prepare_ordered_motion_chain_request(data: dict[str, Any] | None, *, defaults: MotionDefaults=MotionDefaults()) -> PreparedChainRequest:
    payload = parse_execute_ordered_motion_chain_request(data, defaults=defaults)
    raw_start = (data or {}).get('start_position')
    if not isinstance(raw_start, (list, tuple)) or len(raw_start) != 6:
        raise ValueError("Missing 6-value 'start_position'")
    payload['start_position'] = [float(value) for value in raw_start]
    allow_servo = (data or {}).get('allow_servo_during_prepare', False)
    if not isinstance(allow_servo, bool):
        raise ValueError("Invalid 'allow_servo_during_prepare'; expected boolean")
    payload['allow_servo_during_prepare'] = allow_servo
    payload['blocking'] = True
    return payload

@_typed_request
def parse_cartesian_servo_start_request(data: dict[str, Any] | None, *, defaults: MotionDefaults=MotionDefaults()) -> CartesianServoStartRequest:
    payload = data or {}
    frame_value = payload.get('frame')
    if frame_value is None:
        raise ValueError("Missing 'frame'")
    try:
        if isinstance(frame_value, int) or (isinstance(frame_value, str) and frame_value.strip().lstrip('-').isdigit()):
            frame = CartesianServoFrame.USER
            user = int(frame_value)
        else:
            frame = CartesianServoFrame(str(frame_value).strip().lower())
            user = int(payload.get('user', 0))
    except (TypeError, ValueError) as exc:
        valid_frames = [frame.value for frame in CartesianServoFrame]
        raise ValueError(f"Invalid 'frame': {frame_value}. Valid frames: {valid_frames} or numeric user frame id") from exc
    try:
        tool = int(payload.get('tool', 0))
    except (TypeError, ValueError) as exc:
        raise ValueError("Invalid 'tool'") from exc
    return {'frame': frame, 'tool': tool, 'user': user}

@_typed_request
def parse_cartesian_servo_update_request(data: dict[str, Any] | None, *, defaults: MotionDefaults=MotionDefaults()) -> CartesianServoUpdateRequest:
    payload = data or {}
    linear = payload.get('linear_mm_s')
    angular = payload.get('angular_deg_s')
    if not isinstance(linear, (list, tuple)) or len(linear) != 3:
        raise ValueError("Invalid 'linear_mm_s'; expected [vx, vy, vz]")
    if not isinstance(angular, (list, tuple)) or len(angular) != 3:
        raise ValueError("Invalid 'angular_deg_s'; expected [wx, wy, wz]")
    try:
        linear = [float(value) for value in linear]
        angular = [float(value) for value in angular]
    except (TypeError, ValueError) as exc:
        raise ValueError('Servo velocity values must be numeric') from exc
    return {'linear_mm_s': linear, 'angular_deg_s': angular}

def _state_validity_contact_pairs(validity_resp) -> list[str]:
    pairs = []
    for contact in list(getattr(validity_resp, 'contacts', []) or []):
        body_1 = str(getattr(contact, 'contact_body_1', '') or getattr(contact, 'body_name_1', ''))
        body_2 = str(getattr(contact, 'contact_body_2', '') or getattr(contact, 'body_name_2', ''))
        if body_1 or body_2:
            pair = f'{body_1}<->{body_2}' if body_1 and body_2 else body_1 or body_2
            if pair not in pairs:
                pairs.append(pair)
    return pairs

def _coerce_pose6(value, label: str) -> list[float]:
    if not isinstance(value, (list, tuple)) or len(value) != 6:
        raise ValueError(f'Invalid {label}; expected [x,y,z,rx,ry,rz]')
    try:
        return [_finite_number(v, label) for v in value]
    except (TypeError, ValueError) as exc:
        raise ValueError(f'Invalid {label}; all values must be numeric') from exc


class UnwindRequest(TypedDict):
    blocking: bool
    queue_if_busy: bool
    vel: float | None
    acc: float | None


@_typed_request
def parse_unwind_request(data: dict[str, Any] | None, *, defaults=MotionDefaults()) -> UnwindRequest:
    payload = data or {}
    return {'blocking': payload.get('blocking', True), 'queue_if_busy': payload.get('queue_if_busy', True),
            'vel': payload.get('vel'), 'acc': payload.get('acc')}


class ControlledStopRequest(TypedDict):
    expected_task_id: int | str
    stop_duration_s: float | None


def parse_controlled_stop_request(data: dict[str, Any] | None) -> ControlledStopRequest:
    payload = data or {}
    task_id = payload.get('expected_task_id')
    if isinstance(task_id, bool) or not isinstance(task_id, (str, int)) or isinstance(task_id, str) and not task_id.strip():
        raise ValueError('expected_task_id must be an integer or a non-empty string')
    duration = payload.get('stop_duration_s')
    if duration is not None:
        duration = _finite_number(duration, 'stop_duration_s')
        if not 0.05 <= duration <= 2.0:
            raise ValueError('stop_duration_s must be between 0.05 and 2.0 seconds')
    return {'expected_task_id': task_id, 'stop_duration_s': duration}
