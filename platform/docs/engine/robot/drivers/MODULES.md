# Module reference: `src/engine/robot/drivers`

[Package guide](README.md) · [Complete source index](../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [ros2_robot.py](#ros2_robotpy)
- [zeroerr_robot.py](#zeroerr_robotpy)

## `__init__.py`

Source: [src/engine/robot/drivers/__init__.py](../../../../src/engine/robot/drivers/__init__.py).

Imports (including optional/function-local imports; not a startup dependency list): `src.engine.robot.drivers.ros2_robot`.

Package-level import/export surface:

```python
from src.engine.robot.drivers.ros2_robot import Ros2Robot
```

Module declarations (expressions are shown without evaluating them):

```python
__all__ = ['Ros2Robot']
```

## `ros2_robot.py`

Source: [src/engine/robot/drivers/ros2_robot.py](../../../../src/engine/robot/drivers/ros2_robot.py).

Imports (including optional/function-local imports; not a startup dependency list): `logging`, `math`, `src.engine.robot.drivers.client_adapters`, `src.engine.robot.enums.axis`, `src.engine.robot.interfaces.i_robot`, `src.engine.robot.motion_sequence`, `typing`.

Module declarations (expressions are shown without evaluating them):

```python
logger = logging.getLogger(__name__)
```

### `Ros2Robot`

```python
class Ros2Robot(IRobot):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, server_url: str)
```

```python
def move_ptp(self, position: List[float], tool: int, user: int, vel: float, acc: float, blocking: bool=True) -> int
```

```python
def move_linear(self, position: List[float], tool: int, user: int, vel: float, acc: float, blend_radius: float=0.0, blocking: bool=True, allow_collision_recovery: bool=False) -> int
```

```python
def start_jog(self, axis: RobotAxis, direction: Direction, step: float, vel: float, acc: float) -> int
```

```python
def start_servo_jog(self, axis: RobotAxis, direction: Direction, linear_mm_s: float | None=None, angular_deg_s: float | None=None, *, frame: str | int='user', tool: int=0, user: int=0, disable_collision_checking: bool=False) -> int
```

```python
def start_joint_jog(self, joint: str, direction: Direction, step: float, vel: float, acc: float) -> int
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
def set_motion_passage_closed(self, passage_id: str, closed: bool) -> bool
```

```python
def stop_motion(self) -> int
```

```python
def controlled_stop(self, expected_task_id, *, stop_duration_s=None) -> dict
```

```python
def get_state_snapshot(self) -> dict | None
```

```python
def get_current_position(self) -> List[float]
```

```python
def get_current_position_fresh(self) -> List[float]
```

Bypass websocket/state caches and query the runtime pose endpoint.

```python
def get_current_flange_position(self) -> List[float] | None
```

```python
def get_current_base_tcp_position(self) -> List[float] | None
```

```python
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
def get_current_velocity(self) -> float
```

```python
def get_current_acceleration(self) -> float
```

```python
def get_execution_status(self)
```

```python
def get_ordered_motion_chain_status(self)
```

```python
def get_last_trajectory_command_info(self)
```

```python
def unwind_joint6(self, blocking: bool=True, queue_if_busy: bool=True, vel: float | None=None, acc: float | None=None) -> int
```

```python
def get_connection_state(self) -> str
```

```python
def get_connection_details(self) -> dict
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
def get_drive_status(self) -> dict
```

```python
def validate_pose(self, start_position, target_position, tool: int=0, user: int=0, start_joint_state: dict | None=None) -> dict
```

```python
def enable(self) -> None
```

```python
def disable(self) -> None
```

```python
def execute_trajectory(self, path, rx=180, ry=0, rz=0, vel=0.1, acc=0.1, blocking=False, orientation_mode: str='constant') -> int
```

```python
def execute_motion_sequence(self, segments: List[MotionSequenceSegment], tool: int, user: int, blocking: bool=False) -> int
```

```python
def execute_custom_motion_sequence(self, segments: List[MotionSequenceSegment], tool: int, user: int, blocking: bool=False) -> int
```

```python
def execute_ordered_motion_chain(self, segments: list[OrderedMotionInput], tool: int, user: int, blocking: bool=False) -> int
```

```python
def get_last_motion_error(self)
```

```python
def reset_all_errors(self) -> int
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
def set_digital_output(self, port_id: int, value: bool) -> None
```

```python
def clone(self) -> 'IRobot'
```

```python
def prefers_incremental_jog(self) -> bool
```

## `zeroerr_robot.py`

Source: [src/engine/robot/drivers/zeroerr_robot.py](../../../../src/engine/robot/drivers/zeroerr_robot.py).

No top-level functions, classes or public value declarations; inspect the source for imports or entry-point statements.
