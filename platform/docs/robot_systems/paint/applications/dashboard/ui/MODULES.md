# Module reference: `src/robot_systems/paint/applications/dashboard/ui`

[Package guide](README.md) · [Complete source index](../../../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [paint_card_factory.py](#paint_card_factorypy)
- [paint_controls_drawer.py](#paint_controls_drawerpy)
- [paint_info_card.py](#paint_info_cardpy)
- [paint_plate_layout.py](#paint_plate_layoutpy)
- [paint_quick_access_panel.py](#paint_quick_access_panelpy)
- [paint_quick_controls_panel.py](#paint_quick_controls_panelpy)
- [paint_status_card.py](#paint_status_cardpy)

## `paint_card_factory.py`

Source: [src/robot_systems/paint/applications/dashboard/ui/paint_card_factory.py](../../../../../../src/robot_systems/paint/applications/dashboard/ui/paint_card_factory.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `pathlib`, `pl_gui.dashboard.config`, `src.robot_systems.paint.applications.dashboard.ui.paint_info_card`.

### `PaintCardFactory`

```python
class PaintCardFactory:
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def build_cards(self, card_configs: list[CardConfig]) -> list[tuple]
```

## `paint_controls_drawer.py`

Source: [src/robot_systems/paint/applications/dashboard/ui/paint_controls_drawer.py](../../../../../../src/robot_systems/paint/applications/dashboard/ui/paint_controls_drawer.py).

Imports (including optional/function-local imports; not a startup dependency list): `PyQt6.QtCore`, `PyQt6.QtWidgets`, `__future__`, `math`, `pl_gui.settings.settings_view.styles`, `pl_gui.shell.ui.icon_loader`, `pl_gui.utils.utils_widgets.SwitchButton`, `src.applications.base.widgets.custom_virtual_keyboard`.

### `PaintControlsDrawer`

```python
class PaintControlsDrawer(QWidget):
```

Data-driven manual controls hosted by the dashboard drawer.

Declared fields/defaults:

```python
cable_relief_requested = pyqtSignal()
device_toggle_requested = pyqtSignal(str, bool)
application_shortcut_requested = pyqtSignal(str)
unmatched_paint_settings_requested = pyqtSignal(object)
acceleration_scale_requested = pyqtSignal(float)
drying_mode_requested = pyqtSignal(str)
paint_head_adjust_requested = pyqtSignal(str, int)
paint_head_adjust_released = pyqtSignal()
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, toggle_configs: list, *, show_manual_controls: bool=True, show_unmatched_paint_controls: bool=True, show_paint_head_control: bool=True, show_acceleration_scale_control: bool=True, show_shortcuts: bool=True, compact_layout: bool=False, concise_layout: bool=False, use_combined_speed_control: bool=False, combined_speed_minimum_percent: float=1.0, combined_speed_maximum_percent: float=100.0, combined_acceleration_minimum_percent: float=0.01, combined_acceleration_maximum_percent: float=100.0, show_resolved_speed_values: bool=False, show_drying_mode_control: bool=True, parent=None) -> None
```

```python
def set_unmatched_paint_settings(self, settings: dict) -> None
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
def set_drying_mode(self, mode: str) -> None
```

```python
def set_drying_mode_busy(self, busy: bool) -> None
```

```python
def set_device_state(self, device_id: str, enabled: bool) -> None
```

```python
def set_device_busy(self, device_id: str, busy: bool) -> None
```

```python
def set_cable_relief_busy(self, busy: bool) -> None
```

```python
def set_application_shortcuts(self, shortcuts: list) -> None
```

```python
def retranslateUi(self) -> None
```

```python
def set_acceleration_scale(self, value: float) -> None
```

```python
def set_acceleration_scale_editable(self, editable: bool) -> None
```

## `paint_info_card.py`

Source: [src/robot_systems/paint/applications/dashboard/ui/paint_info_card.py](../../../../../../src/robot_systems/paint/applications/dashboard/ui/paint_info_card.py).

Imports (including optional/function-local imports; not a startup dependency list): `PyQt6.QtCore`, `PyQt6.QtGui`, `PyQt6.QtWidgets`, `__future__`, `os`, `pl_gui.settings.settings_view.styles`, `pl_gui.shell.ui.icon_loader`.

### `PaintInfoCard`

```python
class PaintInfoCard(QWidget):
```

Operator-facing placeholder card for paint dashboard expo data.

Declared fields/defaults:

```python
expansion_changed = pyqtSignal(bool)
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, title: str, value: str, note: str, *, icon_name: str='fa5s.circle', parent=None)
```

```python
def set_content(self, title: str, value: str, note: str) -> None
```

```python
def set_status_value(self, value: str) -> None
```

Update semantic color from the untranslated service status.

```python
def set_compact(self, compact: bool=True) -> None
```

```python
def set_expanded(self, expanded: bool) -> None
```

```python
def is_expanded(self) -> bool
```

```python
def mouseReleaseEvent(self, event) -> None
```

## `paint_plate_layout.py`

Source: [src/robot_systems/paint/applications/dashboard/ui/paint_plate_layout.py](../../../../../../src/robot_systems/paint/applications/dashboard/ui/paint_plate_layout.py).

Imports (including optional/function-local imports; not a startup dependency list): `PyQt6.QtCore`, `PyQt6.QtGui`, `PyQt6.QtWidgets`, `__future__`, `datetime`, `pl_gui.settings.settings_view.styles`, `src.applications.base.widgets.custom_virtual_keyboard`.

### `_PlateCanvas`

```python
class _PlateCanvas(QWidget):
```

Declared fields/defaults:

```python
placement_held = pyqtSignal(int)
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, parent=None) -> None
```

```python
def set_state(self, state: dict[str, object]) -> None
```

```python
def clear_selection(self) -> None
```

```python
def set_drying_duration(self, duration_seconds: int | None) -> None
```

```python
def paintEvent(self, _event) -> None
```

```python
def mousePressEvent(self, event) -> None
```

### `PaintPlateLayout`

```python
class PaintPlateLayout(QWidget):
```

Declared fields/defaults:

```python
new_tray_requested = pyqtSignal()
remove_requested = pyqtSignal(int)
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, parent=None, *, use_dry_duration: bool=False, drying_duration_minutes: int=30) -> None
```

```python
def set_state(self, state: dict[str, object]) -> None
```

```python
def set_editable(self, editable: bool, *, removal_editable: bool | None=None) -> None
```

```python
def set_new_tray_button_visible(self, visible: bool) -> None
```

```python
def clear_selection(self) -> None
```

```python
def retranslateUi(self) -> None
```

```python
def changeEvent(self, event: QEvent) -> None
```

## `paint_quick_access_panel.py`

Source: [src/robot_systems/paint/applications/dashboard/ui/paint_quick_access_panel.py](../../../../../../src/robot_systems/paint/applications/dashboard/ui/paint_quick_access_panel.py).

Imports (including optional/function-local imports; not a startup dependency list): `PyQt6.QtCore`, `PyQt6.QtWidgets`, `__future__`, `pl_gui.settings.settings_view.styles`.

### `PaintQuickAccessPanel`

```python
class PaintQuickAccessPanel(QWidget):
```

Always-visible device and drying controls for the expanded dashboard.

Declared fields/defaults:

```python
device_toggle_requested = pyqtSignal(str, bool)
cable_relief_requested = pyqtSignal()
drying_mode_requested = pyqtSignal(str)
new_tray_requested = pyqtSignal()
select_workpieces_requested = pyqtSignal()
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, toggle_configs: list, *, show_drying_mode_control: bool=True, parent=None) -> None
```

```python
def set_workpiece_matching_enabled(self, enabled: bool) -> None
```

```python
def set_workpiece_selection_count(self, count: int | None) -> None
```

```python
def set_drying_mode(self, mode: str) -> None
```

```python
def set_drying_mode_busy(self, busy: bool) -> None
```

```python
def set_device_state(self, device_id: str, enabled: bool) -> None
```

```python
def set_device_busy(self, device_id: str, busy: bool) -> None
```

```python
def set_cable_relief_busy(self, busy: bool) -> None
```

```python
def set_new_tray_enabled(self, enabled: bool) -> None
```

```python
def use_compact_footer_layout(self) -> None
```

Arrange quick actions as a shallow touch-friendly footer grid.

```python
def retranslateUi(self) -> None
```

```python
def changeEvent(self, event: QEvent) -> None
```

## `paint_quick_controls_panel.py`

Source: [src/robot_systems/paint/applications/dashboard/ui/paint_quick_controls_panel.py](../../../../../../src/robot_systems/paint/applications/dashboard/ui/paint_quick_controls_panel.py).

Imports (including optional/function-local imports; not a startup dependency list): `PyQt6.QtCore`, `PyQt6.QtWidgets`, `__future__`, `math`, `pl_gui.settings.settings_view.styles`, `src.applications.base.widgets.custom_virtual_keyboard`.

### `PaintQuickControlsPanel`

```python
class PaintQuickControlsPanel(QWidget):
```

Touch-oriented paint settings and safe OFF commands for the dashboard.

Declared fields/defaults:

```python
unmatched_paint_settings_requested = pyqtSignal(object)
device_off_requested = pyqtSignal(str)
cable_relief_requested = pyqtSignal()
drying_mode_requested = pyqtSignal(str)
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, toggle_configs: list, *, use_combined_speed_control: bool=False, combined_speed_minimum_percent: float=1.0, combined_speed_maximum_percent: float=100.0, combined_acceleration_minimum_percent: float=0.01, combined_acceleration_maximum_percent: float=100.0, show_resolved_speed_values: bool=False, show_drying_mode_control: bool=True, parent=None) -> None
```

```python
def set_drying_mode(self, mode: str) -> None
```

```python
def set_drying_mode_busy(self, busy: bool) -> None
```

```python
def set_unmatched_paint_settings(self, settings: dict) -> None
```

```python
def set_settings_editable(self, editable: bool) -> None
```

```python
def set_device_state(self, device_id: str, enabled: bool) -> None
```

```python
def set_device_busy(self, device_id: str, busy: bool) -> None
```

```python
def set_cable_relief_busy(self, busy: bool) -> None
```

```python
def retranslateUi(self) -> None
```

## `paint_status_card.py`

Source: [src/robot_systems/paint/applications/dashboard/ui/paint_status_card.py](../../../../../../src/robot_systems/paint/applications/dashboard/ui/paint_status_card.py).

Imports (including optional/function-local imports; not a startup dependency list): `PyQt6.QtCore`, `PyQt6.QtWidgets`, `__future__`, `pl_gui.settings.settings_view.styles`.

### `_badge_style`

```python
def _badge_style(color: str) -> str
```

### `PaintStatusCard`

```python
class PaintStatusCard(QWidget):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, label: str, parent=None)
```

```python
def set_state(self, state: str) -> None
```

```python
def apply_dashboard_state(self, state) -> None
```
