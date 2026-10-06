# Module reference: `src/engine/robot/safety`

[Package guide](README.md) · [Complete source index](../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [motion_corridor.py](#motion_corridorpy)
- [safety_checker.py](#safety_checkerpy)

## `__init__.py`

Source: [src/engine/robot/safety/__init__.py](../../../../src/engine/robot/safety/__init__.py).

Imports (including optional/function-local imports; not a startup dependency list): `.motion_corridor`, `.safety_checker`.

Package-level import/export surface:

```python
from .safety_checker import SafetyChecker
from .motion_corridor import MotionCorridor, MotionCorridorRegistry
```

Module declarations (expressions are shown without evaluating them):

```python
__all__ = ['MotionCorridor', 'MotionCorridorRegistry', 'SafetyChecker']
```

## `motion_corridor.py`

Source: [src/engine/robot/safety/motion_corridor.py](../../../../src/engine/robot/safety/motion_corridor.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `dataclasses`, `threading`.

### `MotionCorridor`

```python
@dataclass(frozen=True)
class MotionCorridor:
```

A bounded Cartesian tunnel for explicitly constrained linear motion.

Declared fields/defaults:

```python
corridor_id: str
x_min: float
x_max: float
y_min: float
y_max: float
z_min: float
entry_z_max: float
maximum_velocity: float
maximum_acceleration: float
allow_planar_transit: bool = False
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def validate(self) -> None
```

```python
def contains_xy(self, pose: list[float]) -> bool
```

```python
def contains_xyz(self, pose: list[float]) -> bool
```

### `MotionCorridorRegistry`

```python
class MotionCorridorRegistry:
```

Thread-safe registry of installation-specific reusable motion corridors.

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self) -> None
```

```python
def register(self, corridor: MotionCorridor) -> None
```

```python
def get(self, corridor_id: str) -> MotionCorridor | None
```

## `safety_checker.py`

Source: [src/engine/robot/safety/safety_checker.py](../../../../src/engine/robot/safety/safety_checker.py).

Imports (including optional/function-local imports; not a startup dependency list): `..interfaces.i_safety_checker`, `enum`, `logging`, `typing`.

### `SafetyChecker`

```python
class SafetyChecker(ISafetyChecker):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, settings_key, settings_service=None)
```

```python
def get_violations(self, position: List[float]) -> List[str]
```

```python
def is_within_safety_limits(self, position: List[float]) -> bool
```

```python
def is_escape_move(self, current: List[float], target: List[float]) -> bool
```
