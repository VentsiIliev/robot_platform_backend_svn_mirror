# Module reference: `src/robot_systems/paint/applications/dashboard/view`

[Package guide](README.md) · [Complete source index](../../../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [paint_dashboard_view.py](#paint_dashboard_viewpy)

## `paint_dashboard_view.py`

Source: [src/robot_systems/paint/applications/dashboard/view/paint_dashboard_view.py](../../../../../../src/robot_systems/paint/applications/dashboard/view/paint_dashboard_view.py).

Imports (including optional/function-local imports; not a startup dependency list): `PyQt6.QtCore`, `PyQt6.QtGui`, `PyQt6.QtWidgets`, `__future__`, `collections`, `datetime`, `pl_gui.dashboard.DashboardWidget`, `pl_gui.settings.settings_view.styles`, `pl_gui.shell.ui.icon_loader`, `src.applications.base.drawer_toggle`, `src.applications.base.i_application_view`, `src.applications.base.styled_message_box`, `src.robot_systems.paint.applications.dashboard.config`, `src.robot_systems.paint.applications.dashboard.ui.paint_controls_drawer`, `src.robot_systems.paint.applications.dashboard.ui.paint_plate_layout`, `src.robot_systems.paint.applications.dashboard.ui.paint_quick_access_panel`, `src.robot_systems.paint.applications.dashboard.ui.paint_quick_controls_panel`.

### `_ClickableHeader`

```python
class _ClickableHeader(QWidget):
```

Declared fields/defaults:

```python
clicked = pyqtSignal()
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def mouseReleaseEvent(self, event) -> None
```

### `PaintDashboardView`

```python
class PaintDashboardView(IApplicationView):
```

Declared fields/defaults:

```python
SHOW_JOG_WIDGET = True
JOG_DRAWER_SIDE = 'right'
start_requested = pyqtSignal()
stop_requested = pyqtSignal()
pause_requested = pyqtSignal()
reset_requested = pyqtSignal()
scan_again_requested = pyqtSignal()
action_requested = pyqtSignal(str)
cable_relief_requested = pyqtSignal()
auxiliary_toggle_requested = pyqtSignal(str, bool)
application_shortcut_requested = pyqtSignal(str)
unmatched_paint_settings_requested = pyqtSignal(object)
paint_head_adjust_requested = pyqtSignal(str, int)
paint_head_adjust_released = pyqtSignal()
acceleration_scale_requested = pyqtSignal(float)
drying_mode_requested = pyqtSignal(str)
new_tray_requested = pyqtSignal()
remove_plate_placement_requested = pyqtSignal(int)
camera_selected = pyqtSignal(str)
camera_feed_visible = pyqtSignal(bool)
dashboard_shown = pyqtSignal()
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, config, action_buttons: list, cards: list, auxiliary_toggles=None, ui_config: PaintDashboardUiConfig | None=None, camera_roles=(), parent=None)
```

```python
@property
def action_button_configs(self) -> list
```

```python
@property
def application_shortcuts_enabled(self) -> bool
```

```python
@property
def shortcut_application_names(self) -> tuple[str, ...]
```

```python
def setup_ui(self) -> None
```

```python
def is_camera_feed_visible(self) -> bool
```

```python
def showEvent(self, event) -> None
```

```python
def hideEvent(self, event) -> None
```

```python
def set_trajectory_image(self, image) -> None
```

```python
def set_state(self, state: str) -> None
```

```python
def set_mode(self, mode: str) -> None
```

```python
def set_active_job(self, label: str) -> None
```

```python
def set_notes(self, lines: list[str]) -> None
```

```python
def set_start_enabled(self, enabled: bool) -> None
```

```python
def set_stop_enabled(self, enabled: bool) -> None
```

```python
def set_pause_enabled(self, enabled: bool) -> None
```

```python
def set_pause_label(self, text: str) -> None
```

```python
def set_action_enabled(self, action_id: str, enabled: bool) -> None
```

```python
def set_action_button_text(self, action_id: str, text: str) -> None
```

```python
def set_auxiliary_state(self, device_id: str, enabled: bool) -> None
```

```python
def set_auxiliary_busy(self, device_id: str, busy: bool) -> None
```

```python
def set_cable_relief_busy(self, busy: bool) -> None
```

```python
def set_drying_mode(self, mode: str) -> None
```

```python
def set_plate_layout_state(self, state: dict[str, object]) -> None
```

```python
def clear_plate_selection(self) -> None
```

```python
def set_drying_mode_busy(self, busy: bool) -> None
```

```python
def ask_production_start_confirmation(self, title: str, message: str) -> bool
```

```python
def set_application_shortcuts(self, shortcuts: list) -> None
```

```python
def set_unmatched_paint_settings(self, settings: dict) -> None
```

```python
def set_workpiece_selection_indicator(self, matching_enabled: bool, count: int | None) -> None
```

```python
def set_unmatched_paint_settings_editable(self, editable: bool) -> None
```

```python
def set_paint_head_available(self, available: bool) -> None
```

```python
def set_paint_head_busy(self, busy: bool) -> None
```

```python
def set_paint_head_status(self, message: str, success: bool) -> None
```

```python
def set_acceleration_scale(self, value: float) -> None
```

```python
def set_acceleration_scale_editable(self, editable: bool) -> None
```

```python
def show_info(self, title: str, message: str) -> None
```

```python
def show_warning(self, title: str, message: str) -> None
```

```python
def show_warning_dialog(self, title: str, message: str) -> None
```

Record a warning in the dashboard and show the shared modal warning.

```python
def show_unknown_workpiece_dialog(self, title: str, message: str) -> None
```

```python
def show_debug_plot(self, title: str, image_path: str, message: str='') -> None
```

```python
def apply_dashboard_state(self, state) -> None
```

```python
def retranslateUi(self) -> None
```

```python
def clean_up(self) -> None
```
