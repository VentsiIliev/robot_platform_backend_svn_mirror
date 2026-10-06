# Module reference: `src/robot_systems/ROBOT_SYSTEM_BLUEPRINT/applications/dashboard/service`

[Package guide](README.md) · [Complete source index](../../../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [demo_my_dashboard_service.py](#demo_my_dashboard_servicepy)
- [i_my_dashboard_service.py](#i_my_dashboard_servicepy)

## `demo_my_dashboard_service.py`

Source: [src/robot_systems/ROBOT_SYSTEM_BLUEPRINT/applications/dashboard/service/demo_my_dashboard_service.py](../../../../../../src/robot_systems/ROBOT_SYSTEM_BLUEPRINT/applications/dashboard/service/demo_my_dashboard_service.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `src.robot_systems.ROBOT_SYSTEM_BLUEPRINT.applications.dashboard.dashboard_state`, `src.robot_systems.ROBOT_SYSTEM_BLUEPRINT.applications.dashboard.service.i_my_dashboard_service`, `src.shared_contracts.events.process_events`.

### `DemoMyDashboardService`

```python
class DemoMyDashboardService(IMyDashboardService):
```

Runnable blueprint dashboard service. TODO: Replace this with a service backed by your real coordinator/process. Recommended replacement order: 1. inject your coordinator or main process 2. map process states into DashboardState 3. delegate start/stop/pause/resume to the coordinator 4. expose any system-specific status lines from settings/services 5. publish/subscribe live updates through the broker if needed

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

## `i_my_dashboard_service.py`

Source: [src/robot_systems/ROBOT_SYSTEM_BLUEPRINT/applications/dashboard/service/i_my_dashboard_service.py](../../../../../../src/robot_systems/ROBOT_SYSTEM_BLUEPRINT/applications/dashboard/service/i_my_dashboard_service.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `abc`, `src.robot_systems.ROBOT_SYSTEM_BLUEPRINT.applications.dashboard.dashboard_state`.

### `IMyDashboardService`

```python
class IMyDashboardService(ABC):
```

Standard dashboard contract for a robot-system-specific process.

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
