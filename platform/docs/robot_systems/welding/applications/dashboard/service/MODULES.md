# Module reference: `src/robot_systems/welding/applications/dashboard/service`

[Package guide](README.md) · [Complete source index](../../../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [i_welding_dashboard_service.py](#i_welding_dashboard_servicepy)
- [welding_dashboard_service.py](#welding_dashboard_servicepy)

## `i_welding_dashboard_service.py`

Source: [src/robot_systems/welding/applications/dashboard/service/i_welding_dashboard_service.py](../../../../../../src/robot_systems/welding/applications/dashboard/service/i_welding_dashboard_service.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `abc`, `src.robot_systems.welding.applications.dashboard.dashboard_state`.

### `IWeldingDashboardService`

```python
class IWeldingDashboardService(ABC):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
@abstractmethod
def get_process_id(self) -> str
```

```python
@abstractmethod
def load_state(self) -> DashboardState
```

```python
@abstractmethod
def start(self) -> None
```

```python
@abstractmethod
def stop(self) -> None
```

```python
@abstractmethod
def pause(self) -> None
```

```python
@abstractmethod
def resume(self) -> None
```

```python
@abstractmethod
def reset_errors(self) -> None
```

## `welding_dashboard_service.py`

Source: [src/robot_systems/welding/applications/dashboard/service/welding_dashboard_service.py](../../../../../../src/robot_systems/welding/applications/dashboard/service/welding_dashboard_service.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `src.robot_systems.welding.applications.dashboard.dashboard_state`, `src.robot_systems.welding.applications.dashboard.service.i_welding_dashboard_service`, `src.shared_contracts.events.process_events`.

### `WeldingDashboardService`

```python
class WeldingDashboardService(IWeldingDashboardService):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, process) -> None
```

```python
def get_process_id(self) -> str
```

```python
def load_state(self) -> DashboardState
```

```python
def start(self) -> None
```

```python
def stop(self) -> None
```

```python
def pause(self) -> None
```

```python
def resume(self) -> None
```

```python
def reset_errors(self) -> None
```
