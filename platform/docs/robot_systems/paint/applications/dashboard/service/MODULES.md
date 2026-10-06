# Module reference: `src/robot_systems/paint/applications/dashboard/service`

[Package guide](README.md) · [Complete source index](../../../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [i_paint_dashboard_service.py](#i_paint_dashboard_servicepy)
- [paint_dashboard_service.py](#paint_dashboard_servicepy)
- [stub_paint_dashboard_service.py](#stub_paint_dashboard_servicepy)

## `i_paint_dashboard_service.py`

Source: [src/robot_systems/paint/applications/dashboard/service/i_paint_dashboard_service.py](../../../../../../src/robot_systems/paint/applications/dashboard/service/i_paint_dashboard_service.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `abc`, `dataclasses`, `src.robot_systems.paint.applications.dashboard.dashboard_state`.

### `ContourTransformDebugResult`

```python
@dataclass(frozen=True)
class ContourTransformDebugResult:
```

Declared fields/defaults:

```python
success: bool
message: str
image_path: str | None = None
```

### `DashboardCommandResult`

```python
@dataclass(frozen=True)
class DashboardCommandResult:
```

Declared fields/defaults:

```python
success: bool
message: str
device_id: str | None = None
enabled: bool | None = None
```

### `IPaintDashboardService`

```python
class IPaintDashboardService(ABC):
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

```python
@abstractmethod
def retry_unmatched_workpiece(self) -> bool
```

```python
@abstractmethod
def get_unmatched_paint_settings(self) -> dict
```

```python
@abstractmethod
def save_unmatched_paint_settings(self, settings: dict) -> DashboardCommandResult
```

```python
@abstractmethod
def get_acceleration_scale(self) -> float
```

```python
@abstractmethod
def save_acceleration_scale(self, scale_percent: float) -> DashboardCommandResult
```

```python
@abstractmethod
def is_paint_head_available(self) -> bool
```

```python
@abstractmethod
def adjust_paint_head(self, direction: str, units: int) -> DashboardCommandResult
```

```python
@abstractmethod
def relieve_cable(self) -> DashboardCommandResult
```

```python
@abstractmethod
def get_auxiliary_states(self) -> dict[str, bool]
```

```python
@abstractmethod
def set_auxiliary_enabled(self, device_id: str, enabled: bool) -> DashboardCommandResult
```

```python
@abstractmethod
def get_drying_mode(self) -> str
```

```python
@abstractmethod
def set_drying_mode(self, mode: str) -> DashboardCommandResult
```

```python
@abstractmethod
def get_production_start_guard_state(self, mode: str) -> dict[str, object]
```

```python
@abstractmethod
def prepare_production_start(self, mode: str) -> DashboardCommandResult
```

```python
@abstractmethod
def get_plate_layout_state(self) -> dict[str, object]
```

```python
@abstractmethod
def clear_plate_layout(self) -> DashboardCommandResult
```

```python
@abstractmethod
def remove_plate_placement(self, placement_id: int) -> DashboardCommandResult
```

```python
@abstractmethod
def capture_latest_contour_transform_debug(self) -> ContourTransformDebugResult
```

## `paint_dashboard_service.py`

Source: [src/robot_systems/paint/applications/dashboard/service/paint_dashboard_service.py](../../../../../../src/robot_systems/paint/applications/dashboard/service/paint_dashboard_service.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `cv2`, `dataclasses`, `logging`, `numpy`, `os`, `pathlib`, `src.engine.robot.path_interpolation.new_interpolation.debug_plotting`, `src.engine.robot.path_preparation`, `src.engine.robot.path_preparation.pixel_to_mm`, `src.robot_systems.paint.applications.dashboard.dashboard_state`, `src.robot_systems.paint.applications.dashboard.service.i_paint_dashboard_service`, `src.robot_systems.paint.hardware.paint_head_device`, `src.shared_contracts.events.process_events`, `typing`.

### `PaintDashboardService`

```python
class PaintDashboardService(IPaintDashboardService):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, process, *, capture_snapshot_service=None, path_preparation_service=None, resolver_getter=None, robot_service=None, vision_service=None, vacuum_pump=None, fan_control=None, tray_fan_control=None, allow_running_paint_settings_updates: bool=False, production_start_guard=None, paint_process_config_service=None, paint_head_available: Callable[[], bool] | None=None, paint_head_adjust: Callable[[str, int], object] | None=None, matching_selection=None, plate_layout_service=None, target_point_name: str='camera', frame_name: str='calibration') -> None
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
def resume_vision_for_dashboard_exit(self) -> None
```

Safety release until all vision consumers own acquisition leases.

```python
def reset_errors(self) -> None
```

```python
def retry_unmatched_workpiece(self) -> bool
```

```python
def get_unmatched_paint_settings(self) -> dict[str, float | bool]
```

```python
def save_unmatched_paint_settings(self, settings: dict | float, acceleration_percent: float | None=None, offset_mm: float | None=None) -> DashboardCommandResult
```

```python
def get_acceleration_scale(self) -> float
```

```python
def save_acceleration_scale(self, scale_percent: float) -> DashboardCommandResult
```

```python
def is_paint_head_available(self) -> bool
```

```python
def adjust_paint_head(self, direction: str, units: int) -> DashboardCommandResult
```

Move the configured number of register units regardless of process state.

```python
def relieve_cable(self) -> DashboardCommandResult
```

```python
def get_auxiliary_states(self) -> dict[str, bool]
```

```python
def set_auxiliary_enabled(self, device_id: str, enabled: bool) -> DashboardCommandResult
```

```python
def get_drying_mode(self) -> str
```

```python
def set_drying_mode(self, mode: str) -> DashboardCommandResult
```

```python
def get_plate_layout_state(self) -> dict[str, object]
```

```python
def clear_plate_layout(self) -> DashboardCommandResult
```

```python
def remove_plate_placement(self, placement_id: int) -> DashboardCommandResult
```

```python
def get_production_start_guard_state(self, mode: str) -> dict[str, object]
```

```python
def prepare_production_start(self, mode: str) -> DashboardCommandResult
```

```python
def capture_latest_contour_transform_debug(self) -> ContourTransformDebugResult
```

## `stub_paint_dashboard_service.py`

Source: [src/robot_systems/paint/applications/dashboard/service/stub_paint_dashboard_service.py](../../../../../../src/robot_systems/paint/applications/dashboard/service/stub_paint_dashboard_service.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `src.robot_systems.paint.applications.dashboard.dashboard_state`, `src.robot_systems.paint.applications.dashboard.service.i_paint_dashboard_service`.

### `StubPaintDashboardService`

```python
class StubPaintDashboardService(IPaintDashboardService):
```

In-memory fake dashboard service for the standalone runner and tests. No hardware, robot, vision, or process wiring — every command mutates a local ``idle / running / paused / stopped`` state machine and ``load_state`` renders it back into a :class:`DashboardState`.

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, process_id: str='paint') -> None
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

```python
def retry_unmatched_workpiece(self) -> bool
```

```python
def get_unmatched_paint_settings(self) -> dict
```

```python
def save_unmatched_paint_settings(self, settings: dict | float, acceleration_percent: float | None=None, offset_mm: float | None=None) -> DashboardCommandResult
```

```python
def get_acceleration_scale(self) -> float
```

```python
def save_acceleration_scale(self, scale_percent: float) -> DashboardCommandResult
```

```python
def relieve_cable(self) -> DashboardCommandResult
```

```python
def is_paint_head_available(self) -> bool
```

```python
def adjust_paint_head(self, direction: str, units: int) -> DashboardCommandResult
```

```python
def get_auxiliary_states(self) -> dict[str, bool]
```

```python
def set_auxiliary_enabled(self, device_id: str, enabled: bool) -> DashboardCommandResult
```

```python
def get_drying_mode(self) -> str
```

```python
def set_drying_mode(self, mode: str) -> DashboardCommandResult
```

```python
def get_production_start_guard_state(self, mode: str) -> dict[str, object]
```

```python
def prepare_production_start(self, mode: str) -> DashboardCommandResult
```

```python
def get_plate_layout_state(self) -> dict[str, object]
```

```python
def clear_plate_layout(self) -> DashboardCommandResult
```

```python
def remove_plate_placement(self, placement_id: int) -> DashboardCommandResult
```

```python
def capture_latest_contour_transform_debug(self) -> ContourTransformDebugResult
```
