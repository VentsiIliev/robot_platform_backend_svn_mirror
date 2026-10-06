# Module reference: `src/robot_systems/twin_robot/applications/dashboard/model`

[Package guide](README.md) · [Complete source index](../../../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [twin_dashboard_model.py](#twin_dashboard_modelpy)

## `__init__.py`

Source: [src/robot_systems/twin_robot/applications/dashboard/model/__init__.py](../../../../../../src/robot_systems/twin_robot/applications/dashboard/model/__init__.py).

Imports (including optional/function-local imports; not a startup dependency list): `src.robot_systems.twin_robot.applications.dashboard.model.twin_dashboard_model`.

Package-level import/export surface:

```python
from src.robot_systems.twin_robot.applications.dashboard.model.twin_dashboard_model import TwinDashboardModel
```

Module declarations (expressions are shown without evaluating them):

```python
__all__ = ['TwinDashboardModel']
```

## `twin_dashboard_model.py`

Source: [src/robot_systems/twin_robot/applications/dashboard/model/twin_dashboard_model.py](../../../../../../src/robot_systems/twin_robot/applications/dashboard/model/twin_dashboard_model.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `src.applications.base.i_application_model`, `src.robot_systems.twin_robot.applications.dashboard.service.i_twin_dashboard_service`, `typing`.

### `TwinDashboardModel`

```python
class TwinDashboardModel(IApplicationModel):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, service: ITwinDashboardService)
```

```python
def load(self) -> List[Dict[str, Any]]
```

```python
def select(self, choreography_id: str) -> Dict[str, Any]
```

```python
def plan(self) -> Dict[str, Any]
```

```python
def prepared_status(self) -> Dict[str, Any]
```

```python
def start(self, loop_count: int) -> Dict[str, Any]
```

```python
def stop_motion(self) -> Dict[str, Any]
```

```python
@property
def selected(self) -> Optional[Dict[str, Any]]
```
