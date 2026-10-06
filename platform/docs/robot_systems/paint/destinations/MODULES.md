# Module reference: `src/robot_systems/paint/destinations`

[Package guide](README.md) · [Complete source index](../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [automatic_dryer_destination.py](#automatic_dryer_destinationpy)
- [automatic_dryer_start_guard.py](#automatic_dryer_start_guardpy)

## `__init__.py`

Source: [src/robot_systems/paint/destinations/__init__.py](../../../../src/robot_systems/paint/destinations/__init__.py).

Imports (including optional/function-local imports; not a startup dependency list): `.automatic_dryer_destination`, `.automatic_dryer_start_guard`.

Package-level import/export surface:

```python
from .automatic_dryer_destination import AutomaticDryerDestination
from .automatic_dryer_start_guard import AutomaticDryerStartGuard
```

Module declarations (expressions are shown without evaluating them):

```python
__all__ = ['AutomaticDryerDestination', 'AutomaticDryerStartGuard']
```

## `automatic_dryer_destination.py`

Source: [src/robot_systems/paint/destinations/automatic_dryer_destination.py](../../../../src/robot_systems/paint/destinations/automatic_dryer_destination.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `src.robot_systems.paint.processes.paint.destination`.

### `AutomaticDryerDestination`

```python
class AutomaticDryerDestination(IWorkpieceDestination):
```

Adapt automatic-dryer coordination to the shared destination contract.

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, coordinator) -> None
```

```python
def check_ready_for_release(self) -> tuple[bool, str]
```

```python
def on_release_verified(self) -> bool
```

## `automatic_dryer_start_guard.py`

Source: [src/robot_systems/paint/destinations/automatic_dryer_start_guard.py](../../../../src/robot_systems/paint/destinations/automatic_dryer_start_guard.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `src.robot_systems.paint.applications.dashboard.service.i_paint_dashboard_service`.

### `AutomaticDryerStartGuard`

```python
class AutomaticDryerStartGuard:
```

Autodryer-specific production-start policy kept outside the dashboard.

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, dryer, persist_enabled=None, *, development_mode=False) -> None
```

```python
def state(self, mode: str) -> dict[str, object]
```

```python
def prepare(self, mode: str) -> DashboardCommandResult
```
