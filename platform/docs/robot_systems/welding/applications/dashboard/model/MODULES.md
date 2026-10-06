# Module reference: `src/robot_systems/welding/applications/dashboard/model`

[Package guide](README.md) · [Complete source index](../../../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [welding_dashboard_model.py](#welding_dashboard_modelpy)

## `welding_dashboard_model.py`

Source: [src/robot_systems/welding/applications/dashboard/model/welding_dashboard_model.py](../../../../../../src/robot_systems/welding/applications/dashboard/model/welding_dashboard_model.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `src.applications.base.i_application_model`, `src.robot_systems.welding.applications.dashboard.dashboard_state`, `src.robot_systems.welding.applications.dashboard.service.i_welding_dashboard_service`.

### `WeldingDashboardModel`

```python
class WeldingDashboardModel(IApplicationModel):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, service: IWeldingDashboardService)
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
