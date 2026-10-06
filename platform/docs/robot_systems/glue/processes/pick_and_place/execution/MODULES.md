# Module reference: `src/robot_systems/glue/processes/pick_and_place/execution`

[Package guide](README.md) · [Complete source index](../../../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [height_resolution_service.py](#height_resolution_servicepy)
- [motion_executor.py](#motion_executorpy)

## `__init__.py`

Source: [src/robot_systems/glue/processes/pick_and_place/execution/__init__.py](../../../../../../src/robot_systems/glue/processes/pick_and_place/execution/__init__.py).

Imports (including optional/function-local imports; not a startup dependency list): `.height_resolution_service`, `.motion_executor`.

Package-level import/export surface:

```python
from .height_resolution_service import HeightResolutionResult, HeightResolutionService
from .motion_executor import MotionExecutionResult, PickAndPlaceMotionExecutor
```

Module declarations (expressions are shown without evaluating them):

```python
__all__ = ['HeightResolutionResult', 'HeightResolutionService', 'MotionExecutionResult', 'PickAndPlaceMotionExecutor']
```

## `height_resolution_service.py`

Source: [src/robot_systems/glue/processes/pick_and_place/execution/height_resolution_service.py](../../../../../../src/robot_systems/glue/processes/pick_and_place/execution/height_resolution_service.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `dataclasses`, `logging`, `src.engine.robot.height_measuring.i_height_measuring_service`, `src.robot_systems.glue.processes.pick_and_place.config`, `src.robot_systems.glue.processes.pick_and_place.errors`, `typing`.

### `HeightResolutionResult`

```python
@dataclass(frozen=True)
class HeightResolutionResult:
```

Declared fields/defaults:

```python
value_mm: Optional[float]
source: str
error: Optional[PickAndPlaceErrorInfo] = None
```

### `HeightResolutionService`

```python
class HeightResolutionService:
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, config: PickAndPlaceConfig, height_service: Optional[IHeightMeasuringService], logger: logging.Logger) -> None
```

```python
def resolve(self, fallback_height_mm: float, robot_x: float, robot_y: float) -> HeightResolutionResult
```

## `motion_executor.py`

Source: [src/robot_systems/glue/processes/pick_and_place/execution/motion_executor.py](../../../../../../src/robot_systems/glue/processes/pick_and_place/execution/motion_executor.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `dataclasses`, `logging`, `src.engine.hardware.vacuum_pump.interfaces.i_vacuum_pump_controller`, `src.engine.robot.interfaces.i_robot_service`, `src.engine.robot.interfaces.i_tool_service`, `src.robot_systems.glue.navigation`, `src.robot_systems.glue.processes.pick_and_place.config`, `src.robot_systems.glue.processes.pick_and_place.errors`, `src.robot_systems.glue.processes.pick_and_place.planning.models`, `typing`.

### `MotionExecutionResult`

```python
@dataclass(frozen=True)
class MotionExecutionResult:
```

Declared fields/defaults:

```python
success: bool
error: Optional[PickAndPlaceErrorInfo] = None
tool_changed: bool = False
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
@classmethod
def ok(cls, tool_changed: bool=False) -> 'MotionExecutionResult'
```

```python
@classmethod
def fail(cls, code: PickAndPlaceErrorCode, stage: PickAndPlaceStage, message: str, detail: Optional[str]=None, recoverable: bool=False) -> 'MotionExecutionResult'
```

### `PickAndPlaceMotionExecutor`

```python
class PickAndPlaceMotionExecutor:
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, robot: IRobotService, navigation: GlueNavigationService, tools: IToolService, logger: logging.Logger, pick_motion: MotionProfile, place_motion: MotionProfile, vacuum_pump: Optional[IVacuumPumpController]=None, simulation: bool=False) -> None
```

```python
def move_home(self) -> MotionExecutionResult
```

```python
def ensure_gripper(self, gripper_id: int) -> MotionExecutionResult
```

```python
def execute_pick(self, positions: PickupPositions) -> MotionExecutionResult
```

```python
def execute_place(self, positions: DropOffPositions) -> MotionExecutionResult
```

```python
def execute_pick_descent(self, positions: PickupPositions) -> MotionExecutionResult
```

```python
def execute_pickup_contact(self, positions: PickupPositions) -> MotionExecutionResult
```

```python
def execute_pick_lift(self, positions: PickupPositions) -> MotionExecutionResult
```

```python
def execute_place_approach(self, positions: DropOffPositions) -> MotionExecutionResult
```

```python
def execute_place_drop(self, positions: DropOffPositions) -> MotionExecutionResult
```

```python
def move_to_calibration_position(self) -> MotionExecutionResult
```

```python
def drop_gripper_if_held(self) -> MotionExecutionResult
```
