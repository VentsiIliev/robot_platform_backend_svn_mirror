# Module reference: `src/robot_systems/glue/processes/pick_and_place/planning`

[Package guide](README.md) · [Complete source index](../../../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [models.py](#modelspy)
- [pickup_calculator.py](#pickup_calculatorpy)
- [placement_calculator.py](#placement_calculatorpy)
- [placement_strategy.py](#placement_strategypy)
- [selection_policy.py](#selection_policypy)

## `__init__.py`

Source: [src/robot_systems/glue/processes/pick_and_place/planning/__init__.py](../../../../../../src/robot_systems/glue/processes/pick_and_place/planning/__init__.py).

Imports (including optional/function-local imports; not a startup dependency list): `.models`, `.pickup_calculator`, `.placement_calculator`, `.placement_strategy`, `.selection_policy`.

Package-level import/export surface:

```python
from .models import DropOffPositions, PickupPositions, PlacementResult, PlacementTarget, Position, WorkpieceDimensions, WorkpiecePlacement
from .pickup_calculator import PickupCalculator
from .placement_calculator import PlacementCalculator
from .placement_strategy import PlacementStrategy
from .selection_policy import SelectedWorkpiece, WorkpieceSelectionPolicy
```

Module declarations (expressions are shown without evaluating them):

```python
__all__ = ['DropOffPositions', 'PickupCalculator', 'PickupPositions', 'PlacementCalculator', 'PlacementResult', 'PlacementStrategy', 'PlacementTarget', 'Position', 'SelectedWorkpiece', 'WorkpieceDimensions', 'WorkpiecePlacement', 'WorkpieceSelectionPolicy']
```

## `models.py`

Source: [src/robot_systems/glue/processes/pick_and_place/planning/models.py](../../../../../../src/robot_systems/glue/processes/pick_and_place/planning/models.py).

Imports (including optional/function-local imports; not a startup dependency list): `dataclasses`, `typing`.

### `Position`

```python
@dataclass
class Position:
```

Declared fields/defaults:

```python
x: float
y: float
z: float
rx: float
ry: float
rz: float
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def to_list(self) -> List[float]
```

### `PickupPositions`

```python
@dataclass
class PickupPositions:
```

Declared fields/defaults:

```python
descent: Position
pickup: Position
lift: Position
```

### `DropOffPositions`

```python
@dataclass
class DropOffPositions:
```

Declared fields/defaults:

```python
approach: Position
drop: Position
```

### `WorkpieceDimensions`

```python
@dataclass
class WorkpieceDimensions:
```

Declared fields/defaults:

```python
width: float
height: float
bbox_center: Tuple[float, float]
```

### `PlacementTarget`

```python
@dataclass
class PlacementTarget:
```

Declared fields/defaults:

```python
x: float
y: float
```

### `WorkpiecePlacement`

```python
@dataclass
class WorkpiecePlacement:
```

Declared fields/defaults:

```python
dimensions: WorkpieceDimensions
target_position: PlacementTarget
pickup_positions: PickupPositions
drop_off_positions: DropOffPositions
pickup_height: float
```

### `PlacementResult`

```python
@dataclass
class PlacementResult:
```

Declared fields/defaults:

```python
success: bool
placement: Optional[WorkpiecePlacement]
plane_full: bool
message: str
```

## `pickup_calculator.py`

Source: [src/robot_systems/glue/processes/pick_and_place/planning/pickup_calculator.py](../../../../../../src/robot_systems/glue/processes/pick_and_place/planning/pickup_calculator.py).

Imports (including optional/function-local imports; not a startup dependency list): `logging`, `src.robot_systems.glue.processes.pick_and_place.config`, `src.robot_systems.glue.processes.pick_and_place.planning.models`.

### `PickupCalculator`

```python
class PickupCalculator:
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, config: PickAndPlaceConfig)
```

```python
def calculate(self, robot_x: float, robot_y: float, workpiece_height: float, gripper_id: int, orientation: float) -> PickupPositions
```

## `placement_calculator.py`

Source: [src/robot_systems/glue/processes/pick_and_place/planning/placement_calculator.py](../../../../../../src/robot_systems/glue/processes/pick_and_place/planning/placement_calculator.py).

Imports (including optional/function-local imports; not a startup dependency list): `src.engine.vision.implementation.VisionSystem.core.models.contour`, `src.robot_systems.glue.processes.pick_and_place.config`, `src.robot_systems.glue.processes.pick_and_place.plane`, `src.robot_systems.glue.processes.pick_and_place.planning.models`.

### `PlacementCalculator`

```python
class PlacementCalculator:
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, plane_mgr: PlaneManagementService, config: PickAndPlaceConfig)
```

```python
def calculate(self, cnt_obj: Contour, orientation: float, workpiece_height: float, gripper_id: int) -> PlacementResult
```

## `placement_strategy.py`

Source: [src/robot_systems/glue/processes/pick_and_place/planning/placement_strategy.py](../../../../../../src/robot_systems/glue/processes/pick_and_place/planning/placement_strategy.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `src.engine.vision.implementation.VisionSystem.core.models.contour`, `src.robot_systems.glue.processes.pick_and_place.planning.models`, `src.robot_systems.glue.processes.pick_and_place.planning.placement_calculator`.

### `PlacementStrategy`

```python
class PlacementStrategy:
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, calculator: PlacementCalculator) -> None
```

```python
def plan(self, contour: Contour, orientation: float, workpiece_height: float, gripper_id: int) -> PlacementResult
```

## `selection_policy.py`

Source: [src/robot_systems/glue/processes/pick_and_place/planning/selection_policy.py](../../../../../../src/robot_systems/glue/processes/pick_and_place/planning/selection_policy.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `dataclasses`, `typing`.

### `SelectedWorkpiece`

```python
@dataclass(frozen=True)
class SelectedWorkpiece:
```

Declared fields/defaults:

```python
workpiece: object
orientation: float
```

### `WorkpieceSelectionPolicy`

```python
class WorkpieceSelectionPolicy:
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def select(self, workpieces: Sequence[object], orientations: Sequence[float]) -> List[SelectedWorkpiece]
```
