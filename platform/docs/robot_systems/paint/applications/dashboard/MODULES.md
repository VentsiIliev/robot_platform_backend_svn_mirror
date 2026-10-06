# Module reference: `src/robot_systems/paint/applications/dashboard`

[Package guide](README.md) · [Complete source index](../../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [config.py](#configpy)
- [dashboard_state.py](#dashboard_statepy)
- [example_usage.py](#example_usagepy)
- [paint_dashboard_factory.py](#paint_dashboard_factorypy)

## `__init__.py`

Source: [src/robot_systems/paint/applications/dashboard/__init__.py](../../../../../src/robot_systems/paint/applications/dashboard/__init__.py).

Imports (including optional/function-local imports; not a startup dependency list): `src.robot_systems.paint.applications.dashboard.paint_dashboard_factory`.

Package-level import/export surface:

```python
from src.robot_systems.paint.applications.dashboard.paint_dashboard_factory import PaintDashboardFactory
```

Module declarations (expressions are shown without evaluating them):

```python
__all__ = ['PaintDashboardFactory']
```

## `config.py`

Source: [src/robot_systems/paint/applications/dashboard/config.py](../../../../../src/robot_systems/paint/applications/dashboard/config.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `dataclasses`, `pl_gui.dashboard.config`.

Module declarations (expressions are shown without evaluating them):

```python
PAINT_DASHBOARD_AUXILIARY_TOGGLES = [AuxiliaryToggleConfig(device_id='pump', label='Vacuum Pump'), AuxiliaryToggleConfig(device_id='fan', label='Fan')]
PAINT_DASHBOARD_CARDS: list[CardConfig] = [CardConfig(card_id=1, label='Robot Status'), CardConfig(card_id=2, label='Vision Status'), CardConfig(card_id=3, label='Process Status')]
PAINT_DASHBOARD_ACTIONS: list[ActionButtonConfig] = [ActionButtonConfig(action_id='reset_errors', label='Reset', row=0, col=0)]
```

### `AuxiliaryToggleConfig`

```python
@dataclass(frozen=True)
class AuxiliaryToggleConfig:
```

Declared fields/defaults:

```python
device_id: str
label: str
```

### `PaintDashboardUiConfig`

```python
@dataclass(frozen=True)
class PaintDashboardUiConfig:
```

Feature visibility supplied by the owning robot system.

Declared fields/defaults:

```python
show_jog_widget: bool = True
show_left_drawer: bool = True
show_manual_controls: bool = False
show_unmatched_paint_controls: bool = True
show_paint_head_control: bool = True
show_acceleration_scale_control: bool = True
show_bottom_quick_controls: bool = True
show_drying_mode_control: bool = True
show_camera_preview: bool = True
show_tray_camera_tab: bool = False
use_collapsible_settings_panel: bool = True
use_combined_paint_speed_control: bool = False
combined_paint_speed_minimum_percent: float = 1.0
combined_paint_speed_maximum_percent: float = 100.0
combined_paint_acceleration_minimum_percent: float = 0.01
combined_paint_acceleration_maximum_percent: float = 100.0
show_resolved_paint_speed_values: bool = False
allow_running_paint_settings_updates: bool = False
use_tray_dry_duration: bool = False
tray_dry_duration_minutes: int = 30
show_application_shortcuts: bool = False
shortcut_application_names: tuple[str, ...] = ()
```

### `PaintDashboardConfig`

```python
@dataclass
class PaintDashboardConfig(DashboardConfig):
```

Declared fields/defaults:

```python
show_placeholders: bool = False
card_grid_rows: int = 1
card_grid_cols: int = 3
card_grid_min_width: int = 400
card_grid_max_width: int = 460
action_grid_rows: int = 1
action_grid_cols: int = 1
bottom_section_height: int = 380
status_column_height: int = 458
```

## `dashboard_state.py`

Source: [src/robot_systems/paint/applications/dashboard/dashboard_state.py](../../../../../src/robot_systems/paint/applications/dashboard/dashboard_state.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `dataclasses`.

### `DashboardCardState`

```python
@dataclass(frozen=True)
class DashboardCardState:
```

Declared fields/defaults:

```python
title: str
value: str
note: str
```

### `DashboardState`

```python
@dataclass
class DashboardState:
```

Declared fields/defaults:

```python
process_state: str = 'idle'
mode_label: str = 'Paint Mode'
active_job_label: str = 'No active job'
status_lines: list[str] = field(default_factory=list)
card_states: dict[int, DashboardCardState] = field(default_factory=dict)
can_start: bool = True
can_stop: bool = False
can_pause: bool = False
pause_label: str = 'Pause'
```

## `example_usage.py`

Source: [src/robot_systems/paint/applications/dashboard/example_usage.py](../../../../../src/robot_systems/paint/applications/dashboard/example_usage.py).

Imports (including optional/function-local imports; not a startup dependency list): `PyQt6.QtCore`, `PyQt6.QtWidgets`, `cv2`, `numpy`, `pathlib`, `src.engine.core.messaging_service`, `src.robot_systems.paint.applications.dashboard.paint_dashboard_factory`, `src.robot_systems.paint.applications.dashboard.service.stub_paint_dashboard_service`, `src.shared_contracts.events.process_events`, `src.shared_contracts.events.robot_events`, `src.shared_contracts.events.vision_events`, `sys`.

### `_make_demo_frame`

```python
def _make_demo_frame(tick: int) -> np.ndarray
```

### `_DemoHarness`

```python
class _DemoHarness(QMainWindow):
```

Adds broker-event injection buttons so the dashboard can be tested live.

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, widget, messaging: MessagingService) -> None
```

### `run_standalone`

```python
def run_standalone() -> None
```

## `paint_dashboard_factory.py`

Source: [src/robot_systems/paint/applications/dashboard/paint_dashboard_factory.py](../../../../../src/robot_systems/paint/applications/dashboard/paint_dashboard_factory.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `src.applications.base.application_factory`, `src.applications.base.i_application_controller`, `src.applications.base.i_application_model`, `src.applications.base.i_application_view`, `src.robot_systems.paint.applications.dashboard.config`, `src.robot_systems.paint.applications.dashboard.controller.paint_dashboard_controller`, `src.robot_systems.paint.applications.dashboard.model.paint_dashboard_model`, `src.robot_systems.paint.applications.dashboard.service.i_paint_dashboard_service`, `src.robot_systems.paint.applications.dashboard.ui.paint_card_factory`, `src.robot_systems.paint.applications.dashboard.view.paint_dashboard_view`.

### `PaintDashboardFactory`

```python
class PaintDashboardFactory(ApplicationFactory):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, ui_config: PaintDashboardUiConfig | None=None, camera_roles=())
```

```python
def build(self, service, messaging=None, jog_service=None)
```
