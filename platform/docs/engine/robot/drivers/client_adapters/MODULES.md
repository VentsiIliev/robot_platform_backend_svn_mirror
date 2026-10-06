# Module reference: `src/engine/robot/drivers/client_adapters`

[Package guide](README.md) · [Complete source index](../../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [base.py](#basepy)
- [factory.py](#factorypy)
- [fake.py](#fakepy)
- [http_websocket.py](#http_websocketpy)

## `__init__.py`

Source: [src/engine/robot/drivers/client_adapters/__init__.py](../../../../../src/engine/robot/drivers/client_adapters/__init__.py).

Imports (including optional/function-local imports; not a startup dependency list): `src.engine.robot.drivers.client_adapters.base`, `src.engine.robot.drivers.client_adapters.factory`, `src.engine.robot.drivers.client_adapters.fake`, `src.engine.robot.drivers.client_adapters.http_websocket`.

Package-level import/export surface:

```python
from src.engine.robot.drivers.client_adapters.base import RobotClientAdapter
from src.engine.robot.drivers.client_adapters.http_websocket import HttpWebSocketRobotClient
from src.engine.robot.drivers.client_adapters.fake import FakeRobotClient
from src.engine.robot.drivers.client_adapters.factory import build_robot_client, should_use_fake_robot_client
```

Module declarations (expressions are shown without evaluating them):

```python
__all__ = ['RobotClientAdapter', 'HttpWebSocketRobotClient', 'FakeRobotClient', 'build_robot_client', 'should_use_fake_robot_client']
```

## `base.py`

Source: [src/engine/robot/drivers/client_adapters/base.py](../../../../../src/engine/robot/drivers/client_adapters/base.py).

### `RobotClientAdapter`

```python
class RobotClientAdapter:
```

Base marker for robot client transports.

Declared fields/defaults:

```python
transport_name = 'unknown'
```

## `factory.py`

Source: [src/engine/robot/drivers/client_adapters/factory.py](../../../../../src/engine/robot/drivers/client_adapters/factory.py).

Imports (including optional/function-local imports; not a startup dependency list): `os`, `src.engine.robot.drivers.client_adapters.fake`, `src.engine.robot.drivers.client_adapters.http_websocket`.

### `should_use_fake_robot_client`

```python
def should_use_fake_robot_client(server_url: str | None) -> bool
```

### `build_robot_client`

```python
def build_robot_client(server_url='http://localhost:5000', ip=None, transport=None)
```

## `fake.py`

Source: [src/engine/robot/drivers/client_adapters/fake.py](../../../../../src/engine/robot/drivers/client_adapters/fake.py).

Imports (including optional/function-local imports; not a startup dependency list): `copy`, `logging`, `src.engine.robot.drivers.client_adapters.base`.

Module declarations (expressions are shown without evaluating them):

```python
logger = logging.getLogger(__name__)
```

### `FakeRobotClient`

```python
class FakeRobotClient(RobotClientAdapter):
```

Declared fields/defaults:

```python
transport_name = 'fake'
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, server_url='fake://robot', ip=None)
```

```python
def health_check(self)
```

```python
def get_connection_state(self)
```

```python
def get_connection_details(self)
```

```python
def move_cartesian(self, position, tool=0, user=0, vel=30, acc=30, blendR=0)
```

```python
def move_liner(self, position, tool=0, user=0, vel=30, acc=30, blendR=0, blocking=True, trajectory_optimizer='TOTG', allow_collision_recovery=False)
```

```python
def move_ptp(self, position, tool=0, user=0, vel=30, acc=30, blendR=0, blocking=True, trajectory_optimizer='TOTG')
```

```python
def set_active_tool(self, tool: int) -> bool
```

```python
def execute_path(self, path, rx=None, ry=None, rz=None, vel=0.6, acc=0.4, blocking=False, trajectory_optimizer=None, orientation_mode='constant') -> int
```

```python
def get_last_execute_path_response(self)
```

```python
def execute_sequence(self, segments, tool=0, user=0, blocking=False) -> int
```

```python
def execute_ordered_motion_chain(self, segments, tool=0, user=0, blocking=False, trajectory_optimizer='TOTG') -> int
```

```python
def unwind_joint6(self, blocking=True, queue_if_busy=True, vel=None, acc=None)
```

```python
def start_jog(self, axis, direction, step, vel, acc)
```

```python
def start_servo_jog(self, axis, direction, *, linear_mm_s=None, angular_deg_s=None, frame='user', tool=0, user=0, disable_collision_checking=False)
```

```python
def stop_servo_jog(self, *, restore_collision_checking: bool=True, timing_trace_id: str | None=None)
```

```python
def stop_motion(self)
```

```python
def get_last_stop_response(self)
```

```python
def get_state_snapshot(self)
```

```python
def get_current_position(self)
```

```python
def get_current_flange_position(self)
```

```python
def GetActualTCPPose(self)
```

```python
def get_status(self)
```

```python
def get_safety_walls_status(self)
```

```python
def get_drive_status(self)
```

```python
def validate_pose(self, start_position, target_position, tool=0, user=0, start_joint_state: dict | None=None) -> dict
```

```python
def are_safety_walls_enabled(self)
```

```python
def enable_safety_walls(self) -> bool
```

```python
def disable_safety_walls(self) -> bool
```

```python
def get_current_velocity(self)
```

```python
def enable(self)
```

```python
def RobotEnable(self, state)
```

```python
def disable(self)
```

```python
def setDigitalOutput(self, portId, value)
```

```python
def resetAllErrors(self)
```

```python
def ResetAllError(self)
```

```python
def set_workobject(self, origin, user_id=0)
```

## `http_websocket.py`

Source: [src/engine/robot/drivers/client_adapters/http_websocket.py](../../../../../src/engine/robot/drivers/client_adapters/http_websocket.py).

Imports (including optional/function-local imports; not a startup dependency list): `asyncio`, `copy`, `json`, `logging`, `os`, `requests`, `src.engine.robot.drivers.client_adapters.base`, `threading`, `time`, `urllib.parse`, `websockets`.

Module declarations (expressions are shown without evaluating them):

```python
logger = logging.getLogger(__name__)
```

### `HttpWebSocketRobotClient`

```python
class HttpWebSocketRobotClient(RobotClientAdapter):
```

Current robot transport: HTTP commands with WebSocket state/status streams.

Declared fields/defaults:

```python
transport_name = 'http_websocket'
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, server_url='http://localhost:5000', ip=None)
```

```python
def reconnect(self)
```

```python
def get_connection_state(self)
```

```python
def get_connection_details(self)
```

```python
def publish_sensor_state(self, *, sensor: str, state: bool, stream_id: str, sequence: int, detected_monotonic_ns: int | None=None) -> bool
```

```python
def get_conditional_servo_status(self) -> dict | None
```

```python
def health_check(self)
```

```python
def move_cartesian(self, position, tool=0, user=0, vel=30, acc=30, blendR=0)
```

```python
def move_liner(self, position, tool=0, user=0, vel=30, acc=30, blendR=0, blocking=True, trajectory_optimizer='TOTG', allow_collision_recovery=False)
```

```python
def move_ptp(self, position, tool=0, user=0, vel=30, acc=30, blendR=0, blocking=True, trajectory_optimizer='TOTG')
```

```python
def execute_path(self, path, rx=None, ry=None, rz=None, vel=0.6, acc=0.4, blocking=False, trajectory_optimizer=None, orientation_mode='constant') -> int
```

```python
def get_last_execute_path_response(self)
```

```python
def get_last_motion_error(self)
```

Return the backend's latest motion error text, when available.

```python
def execute_sequence(self, segments, tool=0, user=0, blocking=False) -> int
```

```python
def execute_ordered_motion_chain(self, segments, tool=0, user=0, blocking=False, trajectory_optimizer='TOTG') -> int
```

```python
def prepare_ordered_motion_chain(self, segments, start_position, tool=0, user=0, trajectory_optimizer='TOTG', allow_servo_during_prepare=False)
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
def unwind_joint6(self, blocking=True, queue_if_busy=True, vel=None, acc=None)
```

```python
def start_jog(self, axis, direction, step, vel, acc)
```

```python
def start_joint_jog(self, joint, direction, step, vel, acc)
```

```python
def start_servo_jog(self, axis, direction, *, linear_mm_s=None, angular_deg_s=None, frame='user', tool=0, user=0, disable_collision_checking=False)
```

```python
def stop_servo_jog(self, *, restore_collision_checking: bool=True, timing_trace_id: str | None=None)
```

```python
def start_conditional_servo(self, request: dict) -> dict
```

```python
def cancel_conditional_servo(self) -> dict
```

```python
def servo_jog_to_z(self, **kwargs)
```

```python
def move_fast_linear(self, **kwargs)
```

```python
def set_motion_passage_closed(self, passage_id: str, closed: bool) -> bool
```

```python
def stop_motion(self)
```

```python
def controlled_stop(self, expected_task_id, *, stop_duration_s=None) -> dict
```

```python
def get_last_stop_response(self)
```

```python
def get_state_snapshot(self)
```

```python
def get_current_position(self)
```

```python
def get_current_flange_position(self)
```

```python
def get_current_base_tcp_position(self)
```

Return active TCP pose in robot-base coordinates, without WOBJ conversion.

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
def GetActualTCPPose(self)
```

```python
def get_status(self)
```

```python
def get_ordered_motion_chain_status(self)
```

```python
def get_safety_walls_status(self)
```

```python
def get_drive_status(self)
```

```python
def validate_pose(self, start_position, target_position, tool=0, user=0, start_joint_state: dict | None=None) -> dict
```

```python
def are_safety_walls_enabled(self)
```

```python
def enable_safety_walls(self) -> bool
```

```python
def disable_safety_walls(self) -> bool
```

```python
def get_current_velocity(self)
```

```python
def enable(self)
```

```python
def RobotEnable(self, state)
```

```python
def disable(self)
```

```python
def setDigitalOutput(self, portId, value)
```

```python
def resetAllErrors(self)
```

```python
def ResetAllError(self)
```

```python
def get_workobject_registry(self)
```

```python
def update_workobject_registry(self, user_id, name=None, transform=None, persist=False)
```

```python
def set_workobject(self, origin, user_id=0)
```
