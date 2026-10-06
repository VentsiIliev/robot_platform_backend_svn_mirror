# Module reference: `src/engine/robot/services`

[Package guide](README.md) · [Complete source index](../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [motion_service.py](#motion_servicepy)
- [robot_service.py](#robot_servicepy)
- [robot_service_factory.py](#robot_service_factorypy)
- [robot_state_manager.py](#robot_state_managerpy)
- [robot_state_publisher.py](#robot_state_publisherpy)
- [robot_state_snapshot.py](#robot_state_snapshotpy)

## `__init__.py`

Source: [src/engine/robot/services/__init__.py](../../../../src/engine/robot/services/__init__.py).

Imports (including optional/function-local imports; not a startup dependency list): `.motion_service`, `.robot_service`.

Package-level import/export surface:

```python
from .motion_service import MotionService
from .robot_service import RobotService
```

Module declarations (expressions are shown without evaluating them):

```python
__all__ = ['MotionService', 'RobotService']
```

## `motion_service.py`

Source: [src/engine/robot/services/motion_service.py](../../../../src/engine/robot/services/motion_service.py).

Imports (including optional/function-local imports; not a startup dependency list): `..enums.axis`, `..interfaces.i_motion_service`, `..interfaces.i_robot`, `..interfaces.i_safety_checker`, `..motion_sequence`, `..safety.motion_corridor`, `logging`, `math`, `src.shared_contracts.events.robot_events`, `threading`, `time`, `typing`.

### `MotionService`

```python
class MotionService(IMotionService):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, robot: IRobot, safety_checker: ISafetyChecker, jog_velocity: float=10.0, jog_acceleration: float=10.0, messaging_service=None)
```

```python
def set_motion_passage_closed(self, passage_id: str, closed: bool) -> bool
```

Forward planning-scene passage state changes to the robot driver.

```python
def move_ptp(self, position, tool, user, velocity, acceleration, wait_to_reach=False, wait_cancelled: Callable[[], bool] | None=None) -> bool
```

```python
def move_linear(self, position, tool, user, velocity, acceleration, blendR=0.0, wait_to_reach=False, wait_cancelled: Callable[[], bool] | None=None, allow_subzero_step_recovery: bool=False, allow_collision_recovery: bool=False, bypass_safety_limits: bool=False) -> bool
```

```python
def move_sequence(self, segments: List[MotionSequenceSegment], tool: int, user: int, wait_to_reach=False, wait_cancelled: Callable[[], bool] | None=None) -> bool
```

```python
def move_custom_sequence(self, segments: List[MotionSequenceSegment], tool: int, user: int, wait_to_reach=False, wait_cancelled: Callable[[], bool] | None=None) -> bool
```

```python
def start_jog(self, axis: RobotAxis, direction: Direction, step: float, velocity: float | None=None, acceleration: float | None=None) -> int
```

```python
def start_servo_jog(self, axis: RobotAxis, direction: Direction, linear_mm_s: float | None=None, angular_deg_s: float | None=None, *, frame: str | int='user', tool: int=0, user: int=0, allow_subzero_descent: bool=False, allow_subzero_retract_settle: bool=False, disable_collision_checking: bool=False) -> int
```

```python
def start_joint_jog(self, joint: str, direction: Direction, step: float, velocity: float | None=None, acceleration: float | None=None) -> int
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

```python
def stop_motion(self) -> bool
```

```python
def controlled_stop(self, expected_task_id, *, stop_duration_s=None) -> dict
```

```python
def get_current_position(self) -> List[float]
```

```python
def get_execution_status(self)
```

```python
def register_motion_corridor(self, corridor: MotionCorridor) -> None
```

```python
def move_linear_in_corridor(self, corridor_id: str, position: List[float], tool: int, user: int, velocity: float, acceleration: float, blendR: float=0.0, wait_to_reach: bool=False) -> bool
```

## `robot_service.py`

Source: [src/engine/robot/services/robot_service.py](../../../../src/engine/robot/services/robot_service.py).

Imports (including optional/function-local imports; not a startup dependency list): `..enums.axis`, `..interfaces.i_motion_service`, `..interfaces.i_robot`, `..interfaces.i_robot_service`, `..interfaces.i_robot_state_provider`, `..interfaces.i_tool_service`, `..motion_sequence`, `logging`, `typing`.

### `RobotService`

```python
class RobotService(IRobotService):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, motion: IMotionService, robot: IRobot, state_provider: IRobotStateProvider, tool_service: Optional[IToolService]=None)
```

```python
@property
def tools(self) -> Optional[IToolService]
```

```python
def stop(self) -> None
```

```python
def move_ptp(self, position, tool, user, velocity, acceleration, wait_to_reach=False) -> bool
```

```python
def move_linear(self, position, tool, user, velocity, acceleration, blendR=0.0, wait_to_reach=False, allow_subzero_step_recovery=False, allow_collision_recovery=False, bypass_safety_limits=False) -> bool
```

```python
def register_motion_corridor(self, corridor) -> None
```

```python
def set_motion_passage_closed(self, passage_id: str, closed: bool) -> bool
```

```python
def move_linear_in_corridor(self, corridor_id, position, tool, user, velocity, acceleration, blendR=0.0, wait_to_reach=False) -> bool
```

```python
def move_sequence(self, segments: List[MotionSequenceSegment], tool: int, user: int, wait_to_reach=False) -> bool
```

```python
def move_custom_sequence(self, segments: List[MotionSequenceSegment], tool: int, user: int, wait_to_reach=False) -> bool
```

```python
def start_jog(self, axis: RobotAxis, direction: Direction, step: float, velocity: float | None=None, acceleration: float | None=None) -> int
```

```python
def start_servo_jog(self, axis: RobotAxis, direction: Direction, linear_mm_s: float | None=None, angular_deg_s: float | None=None, *, frame: str | int='user', tool: int=0, user: int=0, allow_subzero_descent: bool=False, allow_subzero_retract_settle: bool=False, disable_collision_checking: bool=False) -> int
```

```python
def start_joint_jog(self, joint: str, direction: Direction, step: float, velocity: float | None=None, acceleration: float | None=None) -> int
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

```python
def stop_motion(self) -> bool
```

```python
def controlled_stop(self, expected_task_id, *, stop_duration_s=None) -> dict
```

```python
def get_current_position(self) -> List[float]
```

```python
def get_current_position_fresh(self) -> List[float]
```

Bypass the state-manager cache for safety-critical live monitoring.

```python
def get_current_flange_position(self) -> List[float]
```

```python
def get_current_base_tcp_position(self) -> List[float] | None
```

```python
def set_active_tool(self, tool: int) -> bool
```

```python
def set_active_workobject(self, user: int) -> bool
```

```python
def get_tool_registry(self)
```

```python
def get_workobject_registry(self)
```

```python
def update_workobject_registry(self, user_id, name=None, transform=None, persist=False)
```

```python
def enable_robot(self) -> None
```

```python
def disable_robot(self) -> None
```

```python
def get_current_velocity(self) -> float
```

```python
def get_current_acceleration(self) -> float
```

```python
def get_state(self) -> str
```

```python
def get_connection_state(self) -> str
```

```python
def get_connection_details(self) -> dict
```

```python
def get_drive_status(self) -> dict
```

```python
def get_state_topic(self) -> str
```

```python
def execute_trajectory(self, path, rx=180, ry=0, rz=0, vel=0.1, acc=0.1, blocking=False, orientation_mode: str='constant') -> int
```

Send a Cartesian path to the robot driver as a trajectory (not safety-checked).

```python
def execute_ordered_motion_chain(self, segments: list[OrderedMotionInput], tool: int, user: int, blocking: bool=False) -> int
```

```python
def get_last_motion_error(self)
```

```python
def get_execution_status(self)
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
def get_last_trajectory_command_info(self)
```

```python
def unwind_joint6(self, blocking: bool=True, queue_if_busy: bool=True, vel: float | None=None, acc: float | None=None) -> bool
```

```python
def enable_safety_walls(self) -> bool
```

```python
def disable_safety_walls(self) -> bool
```

```python
def are_safety_walls_enabled(self)
```

```python
def get_safety_walls_status(self) -> dict
```

```python
def validate_pose(self, start_position, target_position, tool: int=0, user: int=0, start_joint_state: dict | None=None) -> dict
```

```python
def set_digital_output(self, port_id: int, value: bool) -> bool
```

## `robot_service_factory.py`

Source: [src/engine/robot/services/robot_service_factory.py](../../../../src/engine/robot/services/robot_service_factory.py).

Imports (including optional/function-local imports; not a startup dependency list): `src.engine.core.i_messaging_service`, `src.engine.robot.features.tool_service`, `src.engine.robot.interfaces.i_robot`, `src.engine.robot.interfaces.i_robot_service`, `src.engine.robot.interfaces.i_tool_service`, `src.engine.robot.safety.safety_checker`, `src.engine.robot.services.motion_service`, `src.engine.robot.services.robot_service`, `src.engine.robot.services.robot_state_manager`, `src.engine.robot.services.robot_state_publisher`, `typing`.

### `create_robot_service`

```python
def create_robot_service(robot: IRobot, messaging_service: IMessagingService, robot_settings_key, settings_service=None, tool_changer=None) -> IRobotService
```

## `robot_state_manager.py`

Source: [src/engine/robot/services/robot_state_manager.py](../../../../src/engine/robot/services/robot_state_manager.py).

Imports (including optional/function-local imports; not a startup dependency list): `..interfaces.i_robot`, `..interfaces.i_robot_state_provider`, `..interfaces.i_state_publisher`, `.robot_state_snapshot`, `logging`, `threading`, `time`, `typing`.

### `_coerce_joint_snapshot`

```python
def _coerce_joint_snapshot(value: Any) -> dict | None
```

### `RobotStateManager`

```python
class RobotStateManager(IRobotStateProvider):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, robot: IRobot, publisher: Optional[IStatePublisher]=None, state_topic: str='robot/state', active_tool_getter: Callable[[], int] | None=None, active_workobject_getter: Callable[[], int] | None=None)
```

```python
@property
def position(self) -> List[float]
```

```python
@property
def velocity(self) -> float
```

```python
@property
def acceleration(self) -> float
```

```python
@property
def state(self) -> str
```

```python
@property
def state_topic(self) -> str
```

```python
def start_monitoring(self) -> None
```

```python
def refresh_once(self) -> None
```

Synchronously refresh cached robot state once.

```python
def stop_monitoring(self) -> None
```

## `robot_state_publisher.py`

Source: [src/engine/robot/services/robot_state_publisher.py](../../../../src/engine/robot/services/robot_state_publisher.py).

Imports (including optional/function-local imports; not a startup dependency list): `logging`, `src.engine.core.i_messaging_service`, `src.engine.robot.interfaces.i_state_publisher`, `src.engine.robot.services.robot_state_snapshot`, `src.shared_contracts.events.robot_events`.

### `RobotStatePublisher`

```python
class RobotStatePublisher(IStatePublisher):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, broker: IMessagingService)
```

```python
def publish(self, snapshot: RobotStateSnapshot) -> None
```

## `robot_state_snapshot.py`

Source: [src/engine/robot/services/robot_state_snapshot.py](../../../../src/engine/robot/services/robot_state_snapshot.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `dataclasses`, `typing`.

### `RobotStateSnapshot`

```python
@dataclass(frozen=True)
class RobotStateSnapshot:
```

Declared fields/defaults:

```python
state: str
position: List[float]
velocity: float
acceleration: float
extra: Dict[str, Any] = field(default_factory=dict)
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def with_extra(self, **kwargs) -> RobotStateSnapshot
```

Return a new snapshot with additional fields merged into extra.
