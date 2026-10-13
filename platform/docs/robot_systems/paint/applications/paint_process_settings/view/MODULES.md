# Module reference: `src/robot_systems/paint/applications/paint_process_settings/view`

[Package guide](README.md) · [Complete source index](../../../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [paint_process_settings_schema.py](#paint_process_settings_schemapy)
- [paint_process_settings_view.py](#paint_process_settings_viewpy)

## `paint_process_settings_schema.py`

Source: [src/robot_systems/paint/applications/paint_process_settings/view/paint_process_settings_schema.py](../../../../../../src/robot_systems/paint/applications/paint_process_settings/view/paint_process_settings_schema.py).

Imports (including optional/function-local imports; not a startup dependency list): `PyQt6.QtCore`, `pl_gui.settings.settings_view.schema`, `src.engine.robot.path_preparation`, `src.robot_systems.paint.processes.paint.configuration.models`.

### `_t`

```python
def _t(text: str) -> str
```

### `_percent_field`

```python
def _percent_field(key: str, label: str, default: float=0.0, min_val: float=0.0) -> SettingField
```

### `_mm_field`

```python
def _mm_field(key: str, label: str, default: float=0.0, min_val: float=-500.0) -> SettingField
```

### `_deg_field`

```python
def _deg_field(key: str, label: str, default: float=0.0, min_val: float=0.0) -> SettingField
```

### `_seconds_field`

```python
def _seconds_field(key: str, label: str, default: float=0.0) -> SettingField
```

### `_mm_per_second_field`

```python
def _mm_per_second_field(key: str, label: str, default: float=10.0) -> SettingField
```

### `_toggle`

```python
def _toggle(key: str, label: str, default: bool=False) -> SettingField
```

### `_count_field`

```python
def _count_field(key: str, label: str, default: int=1, max_val: int=20) -> SettingField
```

### `_profile`

```python
def _profile(key: str, label: str, vel: float, acc: float, motion_type: str='ptp', blend_r: float=0.0) -> dict
```

### `_profile_table`

```python
def _profile_table(key: str, label: str, rows: list[dict]) -> SettingField
```

### `build_process_groups`

```python
def build_process_groups(dropoff_strategies: tuple[str, ...]=('movement_group', 'plate_layout')) -> list[SettingGroup]
```

### `build_motion_speed_groups`

```python
def build_motion_speed_groups() -> list[SettingGroup]
```

### `build_distance_offset_groups`

```python
def build_distance_offset_groups() -> list[SettingGroup]
```

### `build_paint_path_groups`

```python
def build_paint_path_groups() -> list[SettingGroup]
```

### `build_cleanup_groups`

```python
def build_cleanup_groups() -> list[SettingGroup]
```

### `build_diagnostics_groups`

```python
def build_diagnostics_groups() -> list[SettingGroup]
```

### `build_paint_process_settings_tabs`

```python
def build_paint_process_settings_tabs(dropoff_strategies: tuple[str, ...]=('movement_group', 'plate_layout')) -> list[tuple[str, list[SettingGroup]]]
```

## `paint_process_settings_view.py`

Source: [src/robot_systems/paint/applications/paint_process_settings/view/paint_process_settings_view.py](../../../../../../src/robot_systems/paint/applications/paint_process_settings/view/paint_process_settings_view.py).

Imports (including optional/function-local imports; not a startup dependency list): `PyQt6.QtCore`, `PyQt6.QtWidgets`, `pl_gui.settings.settings_view`, `pl_gui.settings.settings_view.styles`, `pl_gui.settings.settings_view.widget_factory`, `src.applications.base.app_dialog`, `src.applications.base.i_application_view`, `src.applications.base.keyboard_settings_view`, `src.applications.base.styled_message_box`, `src.applications.base.widgets.custom_virtual_keyboard`, `src.robot_systems.paint.applications.paint_process_settings.view.paint_process_settings_schema`, `src.robot_systems.paint.processes.paint.configuration.models`.

### `_t`

```python
def _t(text: str) -> str
```

### `_MagazineOrderTable`

```python
class _MagazineOrderTable(QWidget):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, emit, parent=None) -> None
```

```python
def set_sources(self, value: object) -> None
```

```python
def get_sources(self) -> list[dict]
```

```python
def add_current_position(self, position: list[float]) -> None
```

### `_WaypointTable`

```python
class _WaypointTable(QWidget):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, label: str, emit, default_vel: float=50.0, default_acc: float=20.0, parent=None)
```

```python
def set_waypoints(self, value: object) -> None
```

```python
def get_waypoints(self) -> list[dict]
```

```python
def add_waypoint(self, pose: list[float]) -> None
```

### `_MotionProfileTable`

```python
class _MotionProfileTable(QWidget):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, rows: list[dict], emit, parent=None)
```

```python
def set_profiles(self, value: object) -> None
```

```python
def get_profiles(self) -> list[dict]
```

### `_MotionProfileDialog`

```python
class _MotionProfileDialog(AppDialog):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, profile: dict, parent=None)
```

```python
def profile(self) -> dict
```

```python
def accept(self) -> None
```

### `_WaypointDialog`

```python
class _WaypointDialog(AppDialog):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, waypoint: object=None, default_vel: float=50.0, default_acc: float=20.0, parent=None)
```

```python
def pose(self) -> list[float]
```

```python
def waypoint(self) -> dict
```

```python
def accept(self) -> None
```

### `_ActionButton`

```python
class _ActionButton(QPushButton):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, text: str, emit, parent=None)
```

### `_PlateCornerTable`

```python
class _PlateCornerTable(QWidget):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, emit, parent=None) -> None
```

```python
def set_corners(self, value: object) -> None
```

```python
def get_corners(self) -> dict[str, str]
```

### `PaintProcessSettingsView`

```python
class PaintProcessSettingsView(IApplicationView):
```

Declared fields/defaults:

```python
SHOW_JOG_WIDGET = True
JOG_LIVE_POSITION_ENABLED = True
save_requested = pyqtSignal(dict)
value_changed = pyqtSignal(str, object)
set_safe_travel_current_requested = pyqtSignal()
set_dropoff_safe_travel_current_requested = pyqtSignal()
set_plate_route_pose_current_requested = pyqtSignal(str)
add_fixed_magazine_current_requested = pyqtSignal()
capture_plate_corner_requested = pyqtSignal(str)
clear_plate_corners_requested = pyqtSignal()
move_to_plate_corner_requested = pyqtSignal(dict)
move_to_safe_travel_waypoint_requested = pyqtSignal(dict)
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, dropoff_strategies: tuple[str, ...]=('movement_group', 'plate_layout'), parent=None)
```

```python
def setup_ui(self) -> None
```

```python
def clean_up(self) -> None
```

```python
def set_values(self, values: dict) -> None
```

```python
def add_fixed_magazine_position(self, position: list[float]) -> None
```

```python
def set_safe_travel_position(self, position: list[float]) -> None
```

```python
def set_dropoff_safe_travel_position(self, position: list[float]) -> None
```

```python
def set_plate_route_pose(self, key: str, position: list[float]) -> None
```

```python
def set_plate_corner(self, corner_key: str, position: list[float], tool: int, user: int) -> None
```

```python
def clear_plate_corners(self) -> None
```

```python
def values(self) -> dict
```

```python
def set_status(self, message: str) -> None
```

```python
def retranslateUi(self) -> None
```

```python
def changeEvent(self, event) -> None
```
