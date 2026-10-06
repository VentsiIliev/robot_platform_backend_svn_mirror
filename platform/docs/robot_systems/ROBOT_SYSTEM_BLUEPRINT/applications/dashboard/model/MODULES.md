# Module reference: `src/robot_systems/ROBOT_SYSTEM_BLUEPRINT/applications/dashboard/model`

[Package guide](README.md) · [Complete source index](../../../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [my_dashboard_model.py](#my_dashboard_modelpy)

## `my_dashboard_model.py`

Source: [src/robot_systems/ROBOT_SYSTEM_BLUEPRINT/applications/dashboard/model/my_dashboard_model.py](../../../../../../src/robot_systems/ROBOT_SYSTEM_BLUEPRINT/applications/dashboard/model/my_dashboard_model.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `src.applications.base.i_application_model`, `src.robot_systems.ROBOT_SYSTEM_BLUEPRINT.applications.dashboard.dashboard_state`, `src.robot_systems.ROBOT_SYSTEM_BLUEPRINT.applications.dashboard.service.i_my_dashboard_service`.

### `MyDashboardModel`

```python
class MyDashboardModel(IApplicationModel):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, service: IMyDashboardService)
```

```python
def load(self) -> DashboardState
```

```python
def save(self, _data) -> None
```

```python
def start(self) -> DashboardState
```

```python
def stop_process(self) -> DashboardState
```

```python
def toggle_pause(self) -> DashboardState
```

```python
def reset_errors(self) -> DashboardState
```
