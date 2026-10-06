# Module reference: `src/robot_systems/paint/applications/paint_process_settings/service`

[Package guide](README.md) · [Complete source index](../../../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [i_paint_process_settings_service.py](#i_paint_process_settings_servicepy)
- [paint_process_settings_application_service.py](#paint_process_settings_application_servicepy)
- [stub_paint_process_settings_service.py](#stub_paint_process_settings_servicepy)

## `i_paint_process_settings_service.py`

Source: [src/robot_systems/paint/applications/paint_process_settings/service/i_paint_process_settings_service.py](../../../../../../src/robot_systems/paint/applications/paint_process_settings/service/i_paint_process_settings_service.py).

Imports (including optional/function-local imports; not a startup dependency list): `abc`, `src.robot_systems.paint.processes.paint.config`.

### `IPaintProcessSettingsService`

```python
class IPaintProcessSettingsService(ABC):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
@abstractmethod
def load_settings(self) -> PaintProcessConfig
```

```python
@abstractmethod
def save_settings(self, settings: PaintProcessConfig) -> None
```

```python
@abstractmethod
def is_dropoff_movement_group_configured(self) -> bool
```

```python
@abstractmethod
def dropoff_movement_group_configuration_error(self) -> str
```

```python
@abstractmethod
def get_current_robot_position(self) -> list[float] | None
```

```python
@abstractmethod
def get_current_robot_frame(self) -> tuple[int, int]
```

```python
@abstractmethod
def move_to_waypoint(self, waypoint: dict) -> bool
```

```python
@abstractmethod
def get_pickup_safety_enabled(self) -> tuple[bool, bool]
```

Return persisted (vacuum pump enabled, vacuum sensor enabled) flags.

## `paint_process_settings_application_service.py`

Source: [src/robot_systems/paint/applications/paint_process_settings/service/paint_process_settings_application_service.py](../../../../../../src/robot_systems/paint/applications/paint_process_settings/service/paint_process_settings_application_service.py).

Imports (including optional/function-local imports; not a startup dependency list): `src.robot_systems.paint.applications.paint_process_settings.service.i_paint_process_settings_service`, `src.robot_systems.paint.processes.paint.config`, `src.robot_systems.paint.processes.paint.paint_process_config_service`, `typing`.

### `PaintProcessSettingsApplicationService`

```python
class PaintProcessSettingsApplicationService(IPaintProcessSettingsService):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, process_config_service: IPaintProcessConfigService, dropoff_group_provider: Callable[[], object | None] | None=None, current_position_provider: Callable[[], list[float] | None] | None=None, robot_service_provider: Callable[[], object | None] | None=None, robot_config_provider: Callable[[], object | None] | None=None, robot_tool: int=0, robot_user: int=0, peripherals_provider: Callable[[], object | None] | None=None)
```

```python
def load_settings(self) -> PaintProcessConfig
```

```python
def save_settings(self, settings: PaintProcessConfig) -> None
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

Return the live tool/user configured in Robot Settings.

```python
def get_pickup_safety_enabled(self) -> tuple[bool, bool]
```

```python
def move_to_waypoint(self, waypoint: dict) -> bool
```

## `stub_paint_process_settings_service.py`

Source: [src/robot_systems/paint/applications/paint_process_settings/service/stub_paint_process_settings_service.py](../../../../../../src/robot_systems/paint/applications/paint_process_settings/service/stub_paint_process_settings_service.py).

Imports (including optional/function-local imports; not a startup dependency list): `src.robot_systems.paint.applications.paint_process_settings.service.i_paint_process_settings_service`, `src.robot_systems.paint.processes.paint.config`.

### `StubPaintProcessSettingsService`

```python
class StubPaintProcessSettingsService(IPaintProcessSettingsService):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, initial_settings: PaintProcessConfig | None=None, dropoff_movement_group_configured: bool=True, current_position: list[float] | None=None, vacuum_pump_enabled: bool=True, vacuum_sensor_enabled: bool=True, robot_tool: int=0, robot_user: int=0)
```

```python
def load_settings(self) -> PaintProcessConfig
```

```python
def save_settings(self, settings: PaintProcessConfig) -> None
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
