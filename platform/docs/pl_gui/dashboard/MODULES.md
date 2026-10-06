# Module reference: `pl_gui/dashboard`

[Package guide](README.md) · [Complete source index](../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [DashboardWidget.py](#dashboardwidgetpy)
- [__init__.py](#__init__py)
- [config.py](#configpy)

## `DashboardWidget.py`

Source: [pl_gui/dashboard/DashboardWidget.py](../../../pl_gui/dashboard/DashboardWidget.py).

Imports (including optional/function-local imports; not a startup dependency list): `PyQt6.QtCore`, `PyQt6.QtWidgets`, `pl_gui.dashboard.config`, `pl_gui.dashboard.layout.layout_manager`, `pl_gui.dashboard.widgets.ControlButtonsWidget`, `pl_gui.dashboard.widgets.RobotTrajectoryWidget`, `pl_gui.utils.utils_widgets.MaterialButton`.

### `DashboardWidget`

```python
class DashboardWidget(QWidget):
```

Pure UI facade for the dashboard. Accepts pre-built card widgets, places them in the configured grid, and routes typed setter calls to the correct card by card_id. Has zero knowledge of MessageBroker, topics, factories, or any external vision_service.

Declared fields/defaults:

```python
start_requested = pyqtSignal()
stop_requested = pyqtSignal()
pause_requested = pyqtSignal()
action_requested = pyqtSignal(str)
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, config: DashboardConfig=None, action_buttons: list=None, cards: list=None, parent=None)
```

```python
def set_cell_weight(self, card_id: int, grams: float) -> None
```

```python
def set_cell_state(self, card_id: int, state: str) -> None
```

```python
def set_cell_glue_type(self, card_id: int, glue_type: str) -> None
```

```python
def set_trajectory_image(self, image) -> None
```

```python
def update_trajectory_point(self, point) -> None
```

```python
def break_trajectory(self, _=None) -> None
```

```python
def enable_trajectory_drawing(self, _=None) -> None
```

```python
def disable_trajectory_drawing(self, _=None) -> None
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
def set_pause_text(self, text: str) -> None
```

```python
def set_action_button_enabled(self, action_id: str, enabled: bool) -> None
```

```python
def set_action_button_text(self, action_id: str, text: str) -> None
```

```python
def init_ui(self)
```

```python
def clean_up(self)
```

Release resources. Broker subscriptions are managed by DashboardAdapter.

```python
def retranslateUi(self) -> None
```

```python
def changeEvent(self, event) -> None
```

## `__init__.py`

Source: [pl_gui/dashboard/__init__.py](../../../pl_gui/dashboard/__init__.py).

No top-level functions, classes or public value declarations; inspect the source for imports or entry-point statements.

## `config.py`

Source: [pl_gui/dashboard/config.py](../../../pl_gui/dashboard/config.py).

Imports (including optional/function-local imports; not a startup dependency list): `dataclasses`.

### `DashboardConfig`

```python
@dataclass
class DashboardConfig:
```

Declared fields/defaults:

```python
trajectory_width: int = 800
trajectory_height: int = 450
card_min_height: int = 75
card_grid_rows: int = 3
card_grid_cols: int = 1
card_grid_min_width: int = 350
card_grid_max_width: int = 450
display_fps_ms: int = 30
trajectory_trail_length: int = 100
action_grid_rows: int = 2
action_grid_cols: int = 2
bottom_section_height: int = 300
preview_aux_rows: int = 2
preview_aux_cols: int = 3
show_placeholders: bool = True
```

### `ActionButtonConfig`

```python
@dataclass
class ActionButtonConfig:
```

Declared fields/defaults:

```python
action_id: str
label: str
font_size: int = 20
enabled: bool = True
row: int | None = None
col: int | None = None
row_span: int = 1
col_span: int = 1
```

### `CardConfig`

```python
@dataclass
class CardConfig:
```

Declared fields/defaults:

```python
card_id: int
label: str
row: int | None = None
col: int | None = None
```
