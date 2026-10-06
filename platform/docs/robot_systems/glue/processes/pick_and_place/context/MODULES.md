# Module reference: `src/robot_systems/glue/processes/pick_and_place/context`

[Package guide](README.md) · [Complete source index](../../../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [pick_and_place_context.py](#pick_and_place_contextpy)

## `__init__.py`

Source: [src/robot_systems/glue/processes/pick_and_place/context/__init__.py](../../../../../../src/robot_systems/glue/processes/pick_and_place/context/__init__.py).

Imports (including optional/function-local imports; not a startup dependency list): `.pick_and_place_context`.

Package-level import/export surface:

```python
from .pick_and_place_context import PickAndPlaceContext
```

Module declarations (expressions are shown without evaluating them):

```python
__all__ = ['PickAndPlaceContext']
```

## `pick_and_place_context.py`

Source: [src/robot_systems/glue/processes/pick_and_place/context/pick_and_place_context.py](../../../../../../src/robot_systems/glue/processes/pick_and_place/context/pick_and_place_context.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `dataclasses`, `src.robot_systems.glue.processes.pick_and_place.errors`, `typing`.

### `PickAndPlaceContext`

```python
@dataclass
class PickAndPlaceContext:
```

Declared fields/defaults:

```python
stage: PickAndPlaceStage = PickAndPlaceStage.STARTUP
match_attempt: int = 0
processed_count: int = 0
current_workpiece_id: Optional[str] = None
current_workpiece_name: Optional[str] = None
current_gripper_id: Optional[int] = None
current_orientation: Optional[float] = None
current_pickup_point_px: Optional[tuple[float, float]] = None
current_pickup_point_robot_mapped: Optional[tuple[float, float]] = None
current_pickup_point_robot: Optional[tuple[float, float]] = None
current_pickup_reference_delta: Optional[tuple[float, float]] = None
current_pickup_rz: Optional[float] = None
current_capture_pose: Optional[tuple[float, float, float, float, float, float]] = None
active_height_source: str = 'zero'
current_height_mm: Optional[float] = None
last_message: str = ''
last_error: Optional[PickAndPlaceErrorInfo] = None
holding_gripper_id: Optional[int] = None
vacuum_active: bool = False
simulation: bool = False
plane: dict[str, Any] = field(default_factory=dict)
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def update_plane(self, plane_state) -> None
```

```python
def set_stage(self, stage: PickAndPlaceStage, message: str='') -> None
```

```python
def set_current_workpiece(self, workpiece_id: Optional[str], workpiece_name: Optional[str], gripper_id: Optional[int], orientation: Optional[float], pickup_point_px: Optional[tuple[float, float]]=None) -> None
```

```python
def clear_current_workpiece(self) -> None
```

```python
def mark_error(self, error: PickAndPlaceErrorInfo) -> None
```

```python
def snapshot(self) -> dict[str, Any]
```
