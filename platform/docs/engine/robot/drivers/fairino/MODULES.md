# Module reference: `src/engine/robot/drivers/fairino`

[Package guide](README.md) · [Complete source index](../../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [fairino_robot.py](#fairino_robotpy)
- [test_robot.py](#test_robotpy)

## `__init__.py`

Source: [src/engine/robot/drivers/fairino/__init__.py](../../../../../src/engine/robot/drivers/fairino/__init__.py).

Imports (including optional/function-local imports; not a startup dependency list): `src.engine.robot.drivers.fairino.fairino_robot`, `src.engine.robot.interfaces.i_robot`.

Package-level import/export surface:

```python
from src.engine.robot.interfaces.i_robot import IRobot
from src.engine.robot.drivers.fairino.fairino_robot import FairinoRobot
```

Module declarations (expressions are shown without evaluating them):

```python
__all__ = ['IRobot', 'FairinoRobot']
```

## `fairino_robot.py`

Source: [src/engine/robot/drivers/fairino/fairino_robot.py](../../../../../src/engine/robot/drivers/fairino/fairino_robot.py).

Imports (including optional/function-local imports; not a startup dependency list): `.fairino.linux.fairino`, `.test_robot`, `src.engine.robot.enums.axis`, `src.engine.robot.interfaces.i_robot`, `traceback`, `typing`.

### `FairinoRobot`

```python
class FairinoRobot(IRobot):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, ip: str)
```

```python
def move_ptp(self, position: List[float], tool: int, user: int, vel: float, acc: float, blocking: bool=True) -> int
```

```python
def move_linear(self, position: List[float], tool: int, user: int, vel: float, acc: float, blend_radius: float=0.0, blocking: bool=True) -> int
```

```python
def start_jog(self, axis: RobotAxis, direction: Direction, step: float, vel: float, acc: float) -> int
```

```python
def stop_motion(self) -> int
```

```python
def get_current_position(self) -> List[float]
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
def get_last_trajectory_command_info(self)
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
def reset_all_errors(self) -> int
```

```python
def set_digital_output(self, port_id: int, value: bool) -> None
```

```python
def clone(self) -> 'IRobot'
```

## `test_robot.py`

Source: [src/engine/robot/drivers/fairino/test_robot.py](../../../../../src/engine/robot/drivers/fairino/test_robot.py).

Imports (including optional/function-local imports; not a startup dependency list): `logging`, `src.engine.robot.drivers.client_adapters`, `src.engine.robot.enums.axis`, `src.engine.robot.interfaces.i_robot`, `src.engine.robot.motion_sequence`, `typing`.

### `TestRobotWrapper`

```python
class TestRobotWrapper(IRobot):
```

A full mock of the Fairino Robot interface. Implements every method used by FairinoRobot and returns safe dummy values.

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def execute_trajectory(self, path, rx: float=180, ry: float=0, rz: float=0, vel: float=0.1, acc: float=0.1, blocking: bool=False, orientation_mode: str='constant') -> int
```

```python
def __init__(self)
```

```python
def move_ptp(self, position: List[float], tool: int, user: int, vel: float, acc: float, blocking: bool=True) -> int
```

```python
def move_linear(self, position: List[float], tool: int, user: int, vel: float, acc: float, blend_radius: float=0.0, blocking: bool=True) -> int
```

```python
def start_jog(self, axis: RobotAxis, direction: Direction, step: float, vel: float, acc: float) -> int
```

```python
def stop_motion(self) -> int
```

```python
def get_current_position(self) -> List[float]
```

```python
def get_current_velocity(self) -> float
```

```python
def get_current_acceleration(self) -> float
```

```python
def enable(self) -> None
```

```python
def disable(self) -> None
```

```python
def MoveCart(self, position, tool, user, vel, acc)
```

```python
def MoveL(self, position, tool, user, vel, acc, blendR=0)
```

```python
def StartJOG(self, ref, nb, dir, vel, acc, max_dis)
```

```python
def StopMotion(self)
```

```python
def GetActualTCPPose(self)
```

```python
def RobotEnable(self, param)
```

```python
def ResetAllError(self)
```

```python
def SetDO(self, port_id, value)
```

```python
def set_digital_output(self, port_id: int, value: bool) -> int
```

```python
def execute_path(self, path, rx, ry, rz, vel, acc, blocking) -> int
```

```python
def execute_motion_sequence(self, segments: List[MotionSequenceSegment], tool: int, user: int, blocking: bool=False) -> int
```

```python
def execute_custom_motion_sequence(self, segments: List[MotionSequenceSegment], tool: int, user: int, blocking: bool=False) -> int
```

```python
def GetSDKVersion(self)
```
