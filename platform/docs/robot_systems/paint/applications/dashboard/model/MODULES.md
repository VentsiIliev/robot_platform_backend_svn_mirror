# Module reference: `src/robot_systems/paint/applications/dashboard/model`

[Package guide](README.md) · [Complete source index](../../../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [paint_dashboard_model.py](#paint_dashboard_modelpy)

## `paint_dashboard_model.py`

Source: [src/robot_systems/paint/applications/dashboard/model/paint_dashboard_model.py](../../../../../../src/robot_systems/paint/applications/dashboard/model/paint_dashboard_model.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `src.applications.base.i_application_model`, `src.robot_systems.paint.applications.dashboard.dashboard_state`, `src.robot_systems.paint.applications.dashboard.service.i_paint_dashboard_service`.

### `PaintDashboardModel`

```python
class PaintDashboardModel(IApplicationModel):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, service: IPaintDashboardService)
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
def resume_vision_for_dashboard_exit(self) -> None
```

```python
def toggle_pause(self) -> DashboardState
```

```python
def reset_errors(self) -> DashboardState
```

```python
def retry_unmatched_workpiece(self) -> bool
```

```python
def get_unmatched_paint_settings(self) -> dict
```

```python
def save_unmatched_paint_settings(self, settings: dict | float, acceleration_percent: float | None=None, offset_mm: float | None=None)
```

```python
def relieve_cable(self)
```

```python
def get_acceleration_scale(self) -> float
```

```python
def save_acceleration_scale(self, scale_percent: float)
```

```python
def is_paint_head_available(self) -> bool
```

```python
def adjust_paint_head(self, direction: str, units: int)
```

```python
def get_auxiliary_states(self) -> dict[str, bool]
```

```python
def set_auxiliary_enabled(self, device_id: str, enabled: bool)
```

```python
def get_drying_mode(self) -> str
```

```python
def set_drying_mode(self, mode: str)
```

```python
def get_production_start_guard_state(self, mode: str) -> dict[str, object]
```

```python
def prepare_production_start(self, mode: str)
```

```python
def get_plate_layout_state(self) -> dict[str, object]
```

```python
def clear_plate_layout(self)
```

```python
def remove_plate_placement(self, placement_id: int)
```

```python
def capture_latest_contour_transform_debug(self) -> ContourTransformDebugResult
```
