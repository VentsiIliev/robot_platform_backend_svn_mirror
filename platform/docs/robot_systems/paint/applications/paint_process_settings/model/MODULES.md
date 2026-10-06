# Module reference: `src/robot_systems/paint/applications/paint_process_settings/model`

[Package guide](README.md) · [Complete source index](../../../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [paint_process_settings_model.py](#paint_process_settings_modelpy)

## `paint_process_settings_model.py`

Source: [src/robot_systems/paint/applications/paint_process_settings/model/paint_process_settings_model.py](../../../../../../src/robot_systems/paint/applications/paint_process_settings/model/paint_process_settings_model.py).

Imports (including optional/function-local imports; not a startup dependency list): `src.applications.base.i_application_model`, `src.robot_systems.paint.applications.paint_process_settings.service.i_paint_process_settings_service`, `src.robot_systems.paint.processes.paint.config`.

### `PaintProcessSettingsModel`

```python
class PaintProcessSettingsModel(IApplicationModel):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, service: IPaintProcessSettingsService)
```

```python
def load(self) -> PaintProcessConfig
```

```python
def save(self, settings: PaintProcessConfig) -> None
```

```python
def is_dropoff_movement_group_configured(self) -> bool
```

```python
def dropoff_movement_group_configuration_error(self) -> str
```

```python
def get_current_robot_position(self) -> list[float] | None
```

```python
def get_current_robot_frame(self) -> tuple[int, int]
```

```python
def move_to_waypoint(self, waypoint: dict) -> bool
```

```python
def get_pickup_safety_enabled(self) -> tuple[bool, bool]
```

```python
@property
def current_settings(self) -> PaintProcessConfig
```
