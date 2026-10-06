# Module reference: `src/robot_systems/twin_robot/applications/dashboard/service`

[Package guide](README.md) · [Complete source index](../../../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [i_twin_dashboard_service.py](#i_twin_dashboard_servicepy)
- [twin_dashboard_service.py](#twin_dashboard_servicepy)

## `__init__.py`

Source: [src/robot_systems/twin_robot/applications/dashboard/service/__init__.py](../../../../../../src/robot_systems/twin_robot/applications/dashboard/service/__init__.py).

Imports (including optional/function-local imports; not a startup dependency list): `src.robot_systems.twin_robot.applications.dashboard.service.i_twin_dashboard_service`, `src.robot_systems.twin_robot.applications.dashboard.service.twin_dashboard_service`.

Package-level import/export surface:

```python
from src.robot_systems.twin_robot.applications.dashboard.service.i_twin_dashboard_service import ITwinDashboardService
from src.robot_systems.twin_robot.applications.dashboard.service.twin_dashboard_service import TwinDashboardService
```

Module declarations (expressions are shown without evaluating them):

```python
__all__ = ['ITwinDashboardService', 'TwinDashboardService']
```

## `i_twin_dashboard_service.py`

Source: [src/robot_systems/twin_robot/applications/dashboard/service/i_twin_dashboard_service.py](../../../../../../src/robot_systems/twin_robot/applications/dashboard/service/i_twin_dashboard_service.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `abc`, `typing`.

### `ITwinDashboardService`

```python
class ITwinDashboardService(ABC):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
@abstractmethod
def list_choreographies(self) -> List[Dict[str, Any]]
```

```python
@abstractmethod
def select(self, choreography_id: str) -> Dict[str, Any]
```

```python
@abstractmethod
def plan_selected(self) -> Dict[str, Any]
```

```python
@abstractmethod
def prepared_status(self) -> Dict[str, Any]
```

```python
@abstractmethod
def start(self, loop_count: int | None=None) -> Dict[str, Any]
```

```python
@abstractmethod
def stop(self) -> Dict[str, Any]
```

## `twin_dashboard_service.py`

Source: [src/robot_systems/twin_robot/applications/dashboard/service/twin_dashboard_service.py](../../../../../../src/robot_systems/twin_robot/applications/dashboard/service/twin_dashboard_service.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `src.robot_systems.twin_robot.applications.dashboard.service.i_twin_dashboard_service`, `src.robot_systems.twin_robot.domain`, `src.robot_systems.twin_robot.storage`, `typing`.

### `TwinDashboardService`

```python
class TwinDashboardService(ITwinDashboardService):
```

Operator-facing choreography selection and execution coordinator.

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, repository: ChoreographyRepository, runtime: Any | None=None)
```

```python
def set_runtime(self, runtime: Any | None) -> None
```

```python
def list_choreographies(self) -> List[Dict[str, Any]]
```

```python
def select(self, choreography_id: str) -> Dict[str, Any]
```

```python
def plan_selected(self) -> Dict[str, Any]
```

```python
def prepared_status(self) -> Dict[str, Any]
```

```python
def start(self, loop_count: int | None=None) -> Dict[str, Any]
```

```python
def stop(self) -> Dict[str, Any]
```
