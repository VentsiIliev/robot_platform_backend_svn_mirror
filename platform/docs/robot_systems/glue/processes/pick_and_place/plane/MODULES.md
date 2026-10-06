# Module reference: `src/robot_systems/glue/processes/pick_and_place/plane`

[Package guide](README.md) · [Complete source index](../../../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [plane.py](#planepy)
- [plane_management_service.py](#plane_management_servicepy)

## `__init__.py`

Source: [src/robot_systems/glue/processes/pick_and_place/plane/__init__.py](../../../../../../src/robot_systems/glue/processes/pick_and_place/plane/__init__.py).

Imports (including optional/function-local imports; not a startup dependency list): `.plane`, `.plane_management_service`.

Package-level import/export surface:

```python
from .plane import Plane
from .plane_management_service import PlaneManagementService
```

Module declarations (expressions are shown without evaluating them):

```python
__all__ = ['Plane', 'PlaneManagementService']
```

## `plane.py`

Source: [src/robot_systems/glue/processes/pick_and_place/plane/plane.py](../../../../../../src/robot_systems/glue/processes/pick_and_place/plane/plane.py).

Imports (including optional/function-local imports; not a startup dependency list): `src.robot_systems.glue.processes.pick_and_place.config`.

### `Plane`

```python
class Plane:
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, config: PlaneConfig)
```

## `plane_management_service.py`

Source: [src/robot_systems/glue/processes/pick_and_place/plane/plane_management_service.py](../../../../../../src/robot_systems/glue/processes/pick_and_place/plane/plane_management_service.py).

Imports (including optional/function-local imports; not a startup dependency list): `src.robot_systems.glue.processes.pick_and_place.plane.plane`, `src.robot_systems.glue.processes.pick_and_place.planning.models`.

### `PlaneManagementService`

```python
class PlaneManagementService:
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, plane: Plane)
```

```python
@property
def plane(self) -> Plane
```

```python
def next_target(self, width: float, height: float) -> PlacementTarget
```

```python
def handle_row_overflow(self, width: float, height: float, target: PlacementTarget) -> bool
```

```python
def update_tallest(self, height: float) -> None
```

```python
def advance_for_next(self, width: float) -> None
```

```python
@property
def is_full(self) -> bool
```
