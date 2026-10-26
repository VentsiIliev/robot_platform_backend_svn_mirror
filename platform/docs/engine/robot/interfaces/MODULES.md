# Module reference: `src/engine/robot/interfaces`

[Package guide](README.md) · [Complete source index](../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [i_motion_service.py](#i_motion_servicepy)
- [i_robot.py](#i_robotpy)
- [i_robot_lifecycle.py](#i_robot_lifecyclepy)
- [i_robot_service.py](#i_robot_servicepy)
- [i_robot_state_provider.py](#i_robot_state_providerpy)
- [i_safety_checker.py](#i_safety_checkerpy)
- [i_state_publisher.py](#i_state_publisherpy)
- [i_tool_changer.py](#i_tool_changerpy)
- [i_tool_service.py](#i_tool_servicepy)
- [tool_definition.py](#tool_definitionpy)

- [tool_operation_result.py](#tool_operation_resultpy)

## `__init__.py`

Source: [src/engine/robot/interfaces/__init__.py](../../../../src/engine/robot/interfaces/__init__.py).

Imports (including optional/function-local imports; not a startup dependency list): `.i_motion_service`, `.i_robot`, `.i_robot_lifecycle`, `.i_robot_service`, `.i_robot_state_provider`, `.i_safety_checker`, `.i_tool_service`.

Package-level import/export surface:

```python
from .i_robot import IRobot
from .i_motion_service import IMotionService
from .i_robot_lifecycle import IRobotLifecycle
from .i_robot_service import IRobotService
from .i_safety_checker import ISafetyChecker
from .i_robot_state_provider import IRobotStateProvider
from .i_tool_service import IToolService
```

Module declarations (expressions are shown without evaluating them):

```python
__all__ = ['IRobot', 'IMotionService', 'IRobotLifecycle', 'IRobotService', 'ISafetyChecker', 'IRobotStateProvider', 'IToolService']
```

## `i_motion_service.py`

Source: [src/engine/robot/interfaces/i_motion_service.py](../../../../src/engine/robot/interfaces/i_motion_service.py).

Imports (including optional/function-local imports; not a startup dependency list): `..enums`, `..motion_sequence`, `abc`, `typing`.

### `IMotionService`

```python
class IMotionService(ABC):
```

Low-level motion control interface.

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
@abstractmethod
def move_ptp(self, position: List[float], tool: int, user: int, velocity: float, acceleration: float, wait_to_reach: bool=False, wait_cancelled: Callable[[], bool] | None=None) -> bool
```

Point-to-point motion (joint/cartesian PTP). Fastest path, not guaranteed straight TCP path.

```python
@abstractmethod
def move_linear(self, position: List[float], tool: int, user: int, velocity: float, acceleration: float, blendR: float, wait_to_reach: bool=False, wait_cancelled: Callable[[], bool] | None=None, allow_subzero_step_recovery: bool=False, allow_collision_recovery: bool=False, bypass_safety_limits: bool=False) -> bool
```

Linear TCP motion (straight-line in Cartesian space).

```python
@abstractmethod
def move_sequence(self, segments: List[MotionSequenceSegment], tool: int, user: int, wait_to_reach: bool=False, wait_cancelled: Callable[[], bool] | None=None) -> bool
```

Execute an ordered sequence of explicitly parameterized motion segments.

```python
@abstractmethod
def move_custom_sequence(self, segments: List[MotionSequenceSegment], tool: int, user: int, wait_to_reach: bool=False, wait_cancelled: Callable[[], bool] | None=None) -> bool
```

Execute a custom queued sequence of explicitly parameterized motion segments.

```python
@abstractmethod
def start_jog(self, axis: axis.RobotAxis, direction: axis.Direction, step: float, velocity: float | None=None, acceleration: float | None=None) -> int
```

```python
def start_servo_jog(self, axis: axis.RobotAxis, direction: axis.Direction, linear_mm_s: float | None=None, angular_deg_s: float | None=None, *, frame: str | int='user', tool: int=0, user: int=0, allow_subzero_descent: bool=False, allow_subzero_retract_settle: bool=False, disable_collision_checking: bool=False) -> int
```

```python
def start_joint_jog(self, joint: str, direction: axis.Direction, step: float, velocity: float | None=None, acceleration: float | None=None) -> int
```

```python
def stop_servo_jog(self, *, restore_collision_checking: bool=True, timing_trace_id: str | None=None) -> int
```

```python
def servo_jog_to_z(self, **kwargs) -> dict | None
```

```python
def start_conditional_servo(self, request: dict) -> dict | None
```

```python
def publish_conditional_servo_sensor(self, **event) -> bool
```

```python
def get_conditional_servo_status(self) -> dict | None
```

```python
def cancel_conditional_servo(self) -> dict | None
```

```python
def move_fast_linear(self, **kwargs) -> dict | None
```

Optionally execute a blocking Pilz LIN move and return its final outcome.

```python
@abstractmethod
def stop_motion(self) -> bool
```

```python
@abstractmethod
def get_current_position(self) -> List[float]
```

```python
def get_current_position_fresh(self) -> List[float]
```

Return a fresh pose when a safety-critical motion loop requires it.

```python
def register_motion_corridor(self, corridor) -> None
```

Register one installation-specific constrained linear-motion region.

```python
def set_motion_passage_closed(self, passage_id: str, closed: bool) -> bool
```

Add or remove a configured planning-scene passage lid.

```python
def move_linear_in_corridor(self, corridor_id: str, position: List[float], tool: int, user: int, velocity: float, acceleration: float, blendR: float=0.0, wait_to_reach: bool=False) -> bool
```

Execute a LIN move constrained by a registered corridor.

## `i_robot.py`

Source: [src/engine/robot/interfaces/i_robot.py](../../../../src/engine/robot/interfaces/i_robot.py).

Imports (including optional/function-local imports; not a startup dependency list): `..enums.axis`, `..motion_sequence`, `abc`, `typing`.

### `IRobot`

```python
class IRobot(ABC):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
@abstractmethod
def move_ptp(self, position: List[float], tool: int, user: int, vel: float, acc: float, blocking: bool=True) -> int
```

Point-to-point motion (fastest path). Returns 0 on success.

```python
@abstractmethod
def move_linear(self, position: List[float], tool: int, user: int, vel: float, acc: float, blend_radius: float=0.0, blocking: bool=True, allow_collision_recovery: bool=False) -> int
```

Straight-line TCP motion. Returns 0 on success.

```python
@abstractmethod
def start_jog(self, axis: RobotAxis, direction: Direction, step: float, vel: float, acc: float) -> int
```

```python
def start_servo_jog(self, axis: RobotAxis, direction: Direction, linear_mm_s: float | None=None, angular_deg_s: float | None=None, *, frame: str | int='user', tool: int=0, user: int=0, disable_collision_checking: bool=False) -> int
```

Optional continuous ServoJog. Intended for UI press/release jog.

```python
def start_joint_jog(self, joint: str, direction: Direction, step: float, vel: float, acc: float) -> int
```

Optional incremental joint jog. Step is in degrees.

```python
def stop_servo_jog(self, *, restore_collision_checking: bool=True, timing_trace_id: str | None=None) -> int
```

Optional stop for continuous ServoJog.

```python
def servo_jog_to_z(self, **kwargs) -> dict | None
```

Optional blocking target-bounded +Z ServoJog operation.

```python
def move_fast_linear(self, **kwargs) -> dict | None
```

Optional blocking Pilz LIN operation with a final outcome payload.

```python
def set_motion_passage_closed(self, passage_id: str, closed: bool) -> bool
```

Optionally add/remove a configured ROS planning-scene passage lid.

```python
def set_active_workobject(self, user: int) -> bool
```

Optional active workobject selection for state/current-position reporting.

```python
def get_workobject_registry(self)
```

```python
def update_workobject_registry(self, user_id, name=None, transform=None, persist=False)
```

```python
@abstractmethod
def stop_motion(self) -> int
```

```python
@abstractmethod
def get_current_position(self) -> List[float]
```

```python
@abstractmethod
def get_current_velocity(self) -> float
```

```python
@abstractmethod
def get_current_acceleration(self) -> float
```

```python
@abstractmethod
def execute_trajectory(self, path, rx: float=180, ry: float=0, rz: float=0, vel: float=0.1, acc: float=0.1, blocking: bool=False, orientation_mode: str='constant') -> int
```

```python
def execute_motion_sequence(self, segments: List[MotionSequenceSegment], tool: int, user: int, blocking: bool=False) -> int
```

Optional explicit segmented motion sequence. Returns >=0 on success/queued.

```python
def execute_custom_motion_sequence(self, segments: List[MotionSequenceSegment], tool: int, user: int, blocking: bool=False) -> int
```

Optional custom queued segmented motion sequence. Returns >=0 on success/queued.

```python
def execute_ordered_motion_chain(self, segments: list[OrderedMotionInput], tool: int, user: int, blocking: bool=False) -> int
```

Optional ordered motion chain with mixed segment types.

```python
def prepare_ordered_motion_chain(self, segments: list[OrderedMotionInput], start_position: list[float], tool: int, user: int, *, allow_servo_during_prepare: bool=False) -> dict | None
```

```python
def execute_prepared_ordered_motion_chain(self, plan_id: str) -> dict | None
```

```python
def discard_prepared_ordered_motion_chain(self, plan_id: str) -> dict | None
```

```python
def get_prepared_ordered_motion_chain(self, plan_id: str) -> dict | None
```

```python
@abstractmethod
def enable(self) -> None
```

```python
@abstractmethod
def disable(self) -> None
```

```python
def clone(self) -> 'IRobot'
```

Return a new independent connection to the same robot endpoint. Default: returns self (safe for stateless/HTTP transports). Override in drivers that hold exclusive connections (e.g. TCP SDK).

```python
def get_execution_status(self)
```

Optional execution/queue status from the underlying robot bridge.

```python
def get_last_trajectory_command_info(self)
```

Optional metadata about the last submitted trajectory command.

```python
def unwind_joint6(self, blocking: bool=True, queue_if_busy: bool=True, vel: float | None=None, acc: float | None=None) -> int
```

Optional explicit Joint_6 unwind.

```python
def get_connection_state(self) -> str
```

Optional lifecycle/availability state for the underlying transport.

```python
def get_connection_details(self) -> dict
```

Optional diagnostic details about the underlying transport state.

```python
def enable_safety_walls(self) -> bool
```

Optional remote safety-wall control.

```python
def disable_safety_walls(self) -> bool
```

Optional remote safety-wall control.

```python
def are_safety_walls_enabled(self)
```

Optional remote safety-wall status.

```python
def get_safety_walls_status(self) -> dict
```

Optional remote safety-wall status payload.

```python
def validate_pose(self, start_position: List[float], target_position: List[float], tool: int=0, user: int=0, start_joint_state: dict | None=None) -> dict
```

Optional remote pose reachability validation.

```python
def set_active_tool(self, tool: int) -> bool
```

Optional remote active TCP selection for status/current-pose reporting.

```python
def get_tool_registry(self)
```

Return the remote tool registry payload when supported.

```python
def prefers_incremental_jog(self) -> bool
```

Whether jog should prefer the robot's native incremental jog API over synthesized move commands.

```python
def set_digital_output(self, port_id: int, value: bool) -> int
```

Optional robot-side digital output control.

## `i_robot_lifecycle.py`

Source: [src/engine/robot/interfaces/i_robot_lifecycle.py](../../../../src/engine/robot/interfaces/i_robot_lifecycle.py).

Imports (including optional/function-local imports; not a startup dependency list): `abc`.

### `IRobotLifecycle`

```python
class IRobotLifecycle(ABC):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
@abstractmethod
def enable_robot(self) -> None
```

```python
@abstractmethod
def disable_robot(self) -> None
```

## `i_robot_service.py`

Source: [src/engine/robot/interfaces/i_robot_service.py](../../../../src/engine/robot/interfaces/i_robot_service.py).

Imports (including optional/function-local imports; not a startup dependency list): `..motion_sequence`, `.i_motion_service`, `.i_robot_lifecycle`, `abc`, `src.engine.core.i_health_checkable`, `typing`.

### `IRobotService`

```python
class IRobotService(IMotionService, IRobotLifecycle, IHealthCheckable, ABC):
```

Full robot service interface.

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
@abstractmethod
def get_current_velocity(self) -> float
```

```python
@abstractmethod
def get_current_acceleration(self) -> float
```

```python
@abstractmethod
def get_state(self) -> str
```

```python
@abstractmethod
def get_state_topic(self) -> str
```

```python
@abstractmethod
def execute_trajectory(self, path, rx: float=180, ry: float=0, rz: float=0, vel: float=0.1, acc: float=0.1, blocking: bool=False, orientation_mode: str='constant') -> int
```

```python
def execute_ordered_motion_chain(self, segments: list[OrderedMotionInput], tool: int, user: int, blocking: bool=False) -> int
```

```python
def prepare_ordered_motion_chain(self, segments: list[OrderedMotionInput], start_position, tool, user, *, allow_servo_during_prepare=False)
```

```python
def execute_prepared_ordered_motion_chain(self, plan_id)
```

```python
def discard_prepared_ordered_motion_chain(self, plan_id)
```

```python
def get_prepared_ordered_motion_chain(self, plan_id)
```

```python
def get_execution_status(self)
```

```python
def get_last_trajectory_command_info(self)
```

```python
def unwind_joint6(self, blocking: bool=True, queue_if_busy: bool=True, vel: float | None=None, acc: float | None=None) -> bool
```

```python
@abstractmethod
def enable_safety_walls(self) -> bool
```

```python
@abstractmethod
def disable_safety_walls(self) -> bool
```

```python
@abstractmethod
def are_safety_walls_enabled(self) -> Optional[bool]
```

```python
@abstractmethod
def get_safety_walls_status(self) -> dict
```

```python
@abstractmethod
def validate_pose(self, start_position, target_position, tool: int=0, user: int=0, start_joint_state: dict | None=None) -> dict
```

```python
@abstractmethod
def set_active_tool(self, tool: int) -> bool
```

```python
def get_tool_registry(self)
```

```python
def set_active_workobject(self, user: int) -> bool
```

```python
def get_workobject_registry(self)
```

```python
def update_workobject_registry(self, user_id, name=None, transform=None, persist=False)
```

```python
def is_healthy(self) -> bool
```

Healthy = robot is not in error state.

```python
def get_connection_state(self) -> str
```

Optional lifecycle/availability state for the underlying transport.

```python
def get_connection_details(self) -> dict
```

Optional diagnostic details about the underlying transport state.

```python
def get_drive_status(self) -> dict
```

Optional drive/fieldbus status from the underlying robot transport.

```python
@abstractmethod
def set_digital_output(self, port_id: int, value: bool) -> bool
```

## `i_robot_state_provider.py`

Source: [src/engine/robot/interfaces/i_robot_state_provider.py](../../../../src/engine/robot/interfaces/i_robot_state_provider.py).

Imports (including optional/function-local imports; not a startup dependency list): `abc`, `typing`.

### `IRobotStateProvider`

```python
class IRobotStateProvider(ABC):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
@property
@abstractmethod
def position(self) -> List[float]
```

```python
@property
@abstractmethod
def velocity(self) -> float
```

```python
@property
@abstractmethod
def acceleration(self) -> float
```

```python
@property
@abstractmethod
def state(self) -> str
```

```python
@property
@abstractmethod
def state_topic(self) -> str
```

```python
@abstractmethod
def start_monitoring(self) -> None
```

```python
@abstractmethod
def stop_monitoring(self) -> None
```

## `i_safety_checker.py`

Source: [src/engine/robot/interfaces/i_safety_checker.py](../../../../src/engine/robot/interfaces/i_safety_checker.py).

Imports (including optional/function-local imports; not a startup dependency list): `abc`, `typing`.

### `ISafetyChecker`

```python
class ISafetyChecker(ABC):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
@abstractmethod
def is_within_safety_limits(self, position: List[float]) -> bool
```

```python
@abstractmethod
def is_escape_move(self, current: List[float], target: List[float]) -> bool
```

True when already outside limits and target moves toward valid range.

```python
@abstractmethod
def get_violations(self, position: List[float]) -> List[str]
```

Returns a list of human-readable violation strings, empty if within limits.

## `i_state_publisher.py`

Source: [src/engine/robot/interfaces/i_state_publisher.py](../../../../src/engine/robot/interfaces/i_state_publisher.py).

Imports (including optional/function-local imports; not a startup dependency list): `abc`, `src.engine.robot.services.robot_state_snapshot`.

### `IStatePublisher`

```python
class IStatePublisher(ABC):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
@abstractmethod
def publish(self, snapshot: RobotStateSnapshot) -> None
```

## `i_tool_changer.py`

Source: [src/engine/robot/interfaces/i_tool_changer.py](../../../../src/engine/robot/interfaces/i_tool_changer.py).

Imports (including optional/function-local imports; not a startup dependency list): `abc`, `src.engine.robot.interfaces.tool_definition`, `typing`.

### `IToolChanger`

```python
class IToolChanger(ABC):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
@abstractmethod
def get_slot_id_by_tool_id(self, tool_id: int) -> Optional[int]
```

```python
@abstractmethod
def is_slot_occupied(self, slot_id: int) -> bool
```

```python
@abstractmethod
def set_slot_available(self, slot_id: int) -> None
```

```python
@abstractmethod
def set_slot_not_available(self, slot_id: int) -> None
```

```python
@abstractmethod
def list_tools(self) -> List[ToolDefinition]
```

## `i_tool_service.py`

Source: [src/engine/robot/interfaces/i_tool_service.py](../../../../src/engine/robot/interfaces/i_tool_service.py).

### `IToolService`

```python
class IToolService(ABC):
```

Tool commands return typed results; legacy tuple unpacking is supported.

```python
@property
def current_tool(self) -> Optional[int]
```

Generic name for the attached tool; current_gripper remains compatible.

```python
@property
@abstractmethod
def current_gripper(self) -> Optional[int]
```

```python
@abstractmethod
def pickup_gripper(self, gripper_id: int) -> ToolOperationResult
```

```python
@abstractmethod
def drop_off_gripper(self, gripper_id: int) -> ToolOperationResult
```

```python
@abstractmethod
def get_tools(self) -> List[ToolDefinition]
```

```python
def pickup_tool(self, tool_id: int, *, cancelled: Event | None=None) -> ToolOperationResult
```

```python
def drop_off_tool(self, tool_id: int, *, cancelled: Event | None=None) -> ToolOperationResult
```

```python
def execute_sequence(self, slot_id: int, steps: Sequence[ToolChangeStep | dict[str, object]], cancelled: Event | None=None) -> ToolOperationResult
```

Run a taught editor draft without committing physical slot occupancy.

```python
def confirm_attached_tool(self, tool_id: int | None) -> ToolOperationResult
```

Acknowledge manually inspected attachment; None means an empty flange.


## `tool_definition.py`

Source: [src/engine/robot/interfaces/tool_definition.py](../../../../src/engine/robot/interfaces/tool_definition.py).

Imports (including optional/function-local imports; not a startup dependency list): `dataclasses`, `typing`.

### `ToolDefinition`

```python
@dataclass
class ToolDefinition:
```

Declared fields/defaults:

```python
id: int
name: str
reference_tool_id: Optional[int] = None
relative_transform: list[float] = field(default_factory=lambda: [0.0, 0.0, 0.0, 0.0, 0.0, 0.0])
collision_profile: str = ''
```

## `tool_operation_result.py`

Source: [src/engine/robot/interfaces/tool_operation_result.py](../../../../src/engine/robot/interfaces/tool_operation_result.py).

### `ToolErrorCode`

```python
class ToolErrorCode(str, Enum):
```

Declared fields/defaults:

```python
BUSY = 'BUSY'
RECOVERY_REQUIRED = 'RECOVERY_REQUIRED'
TOOL_NOT_FOUND = 'TOOL_NOT_FOUND'
SLOT_NOT_FOUND = 'SLOT_NOT_FOUND'
TOOL_ALREADY_HELD = 'TOOL_ALREADY_HELD'
TOOL_NOT_HELD = 'TOOL_NOT_HELD'
SLOT_ASSIGNMENT_CHANGED = 'SLOT_ASSIGNMENT_CHANGED'
SLOT_OCCUPIED = 'SLOT_OCCUPIED'
SEQUENCE_NOT_CONFIGURED = 'SEQUENCE_NOT_CONFIGURED'
INVALID_SEQUENCE = 'INVALID_SEQUENCE'
CONFIRMATION_REQUIRED = 'CONFIRMATION_REQUIRED'
CONFIRMATION_DECLINED = 'CONFIRMATION_DECLINED'
CONFIRMATION_FAILED = 'CONFIRMATION_FAILED'
ACTIVATION_UNAVAILABLE = 'ACTIVATION_UNAVAILABLE'
ACTIVATION_FAILED = 'ACTIVATION_FAILED'
ROBOT_UNAVAILABLE = 'ROBOT_UNAVAILABLE'
ROBOT_NOT_READY = 'ROBOT_NOT_READY'
POSITION_NOT_CONFIGURED = 'POSITION_NOT_CONFIGURED'
POSE_UNAVAILABLE = 'POSE_UNAVAILABLE'
NOT_AT_TOOL_CHANGER = 'NOT_AT_TOOL_CHANGER'
CANCELLED = 'CANCELLED'
MOTION_FAILED = 'MOTION_FAILED'
CONFIGURATION_ERROR = 'CONFIGURATION_ERROR'
UNSUPPORTED = 'UNSUPPORTED'
UNEXPECTED_ERROR = 'UNEXPECTED_ERROR'
```

### `ToolErrorInfo`

```python
class ToolErrorInfo:
```

Declared fields/defaults:

```python
code: ToolErrorCode
message: str
step_number: int | None = None
detail: str | None = None
```

### `ToolOperationFailure`

```python
class ToolOperationFailure(Exception):
```

Internal validation/execution exception carrying an already classified error.

```python
def __init__(self, code: ToolErrorCode, message: str, *, step_number: int | None=None, detail: str | None=None) -> None
```

### `ToolOperationResult`

```python
class ToolOperationResult:
```

Declared fields/defaults:

```python
message: str | None = None
error: ToolErrorInfo | None = None
```

```python
@property
def success(self) -> bool
```

```python
@classmethod
def failure(cls, code: ToolErrorCode, message: str, *, step_number: int | None=None, detail: str | None=None) -> ToolOperationResult
```

```python
def __bool__(self) -> bool
```

```python
def as_tuple(self) -> tuple[bool, str | None]
```

Compatibility boundary for existing (ok, message) callers.

```python
def __iter__(self) -> Iterator[bool | str | None]
```

```python
@overload
def __getitem__(self, index: Literal[0, -2]) -> bool
```

```python
@overload
def __getitem__(self, index: Literal[1, -1]) -> str | None
```

```python
@overload
def __getitem__(self, index: int) -> bool | str | None
```

```python
def __getitem__(self, index: int) -> bool | str | None
```
