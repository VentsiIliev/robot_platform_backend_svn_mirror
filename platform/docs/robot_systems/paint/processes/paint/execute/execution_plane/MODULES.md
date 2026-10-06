# Module reference: `src/robot_systems/paint/processes/paint/execute/execution_plane`

[Package guide](README.md) · [Complete source index](../../../../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [strategies.py](#strategiespy)

## `__init__.py`

Source: [src/robot_systems/paint/processes/paint/execute/execution_plane/__init__.py](../../../../../../../src/robot_systems/paint/processes/paint/execute/execution_plane/__init__.py).

Imports (including optional/function-local imports; not a startup dependency list): `.strategies`.

Package-level import/export surface:

```python
from .strategies import ExecutionPlaneStrategy, get_execution_plane_strategy
```

No top-level functions, classes or public value declarations; inspect the source for imports or entry-point statements.

## `strategies.py`

Source: [src/robot_systems/paint/processes/paint/execute/execution_plane/strategies.py](../../../../../../../src/robot_systems/paint/processes/paint/execute/execution_plane/strategies.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `dataclasses`, `src.engine.geometry.planar`.

### `ExecutionPlaneStrategy`

```python
@dataclass(frozen=True)
class ExecutionPlaneStrategy:
```

Behavioral strategy for one pivot execution plane.

Declared fields/defaults:

```python
motion_plane: str
pivot_offset_position_index: int
rotation_axis_label: str
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def compute_pickup_align_rotation(self, *, pickup_rz: float, pickup_ry: float, first_pivot_pose: list[float], paint_pivot_pose: list[float], mirrored_handoff: bool=False) -> float
```

```python
def maybe_flip_execution_rotation_direction(self, *, pivot_path: list[list[float]], enabled: bool) -> list[list[float]]
```

### `XyZRzExecutionPlaneStrategy`

```python
@dataclass(frozen=True)
class XyZRzExecutionPlaneStrategy(ExecutionPlaneStrategy):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self) -> None
```

```python
def compute_pickup_align_rotation(self, *, pickup_rz: float, pickup_ry: float, first_pivot_pose: list[float], paint_pivot_pose: list[float], mirrored_handoff: bool=False) -> float
```

### `XzYRyExecutionPlaneStrategy`

```python
@dataclass(frozen=True)
class XzYRyExecutionPlaneStrategy(ExecutionPlaneStrategy):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self) -> None
```

```python
def compute_pickup_align_rotation(self, *, pickup_rz: float, pickup_ry: float, first_pivot_pose: list[float], paint_pivot_pose: list[float], mirrored_handoff: bool=False) -> float
```

```python
def maybe_flip_execution_rotation_direction(self, *, pivot_path: list[list[float]], enabled: bool) -> list[list[float]]
```

### `get_execution_plane_strategy`

```python
def get_execution_plane_strategy(motion_plane: str) -> ExecutionPlaneStrategy
```

Return the strategy object for a configured execution plane.
