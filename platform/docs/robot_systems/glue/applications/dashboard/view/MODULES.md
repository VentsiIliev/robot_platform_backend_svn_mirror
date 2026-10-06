# Module reference: `src/robot_systems/glue/applications/dashboard/view`

[Package guide](README.md) · [Complete source index](../../../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [glue_dashboard_view.py](#glue_dashboard_viewpy)

## `__init__.py`

Source: [src/robot_systems/glue/applications/dashboard/view/__init__.py](../../../../../../src/robot_systems/glue/applications/dashboard/view/__init__.py).

No top-level functions, classes or public value declarations; inspect the source for imports or entry-point statements.

## `glue_dashboard_view.py`

Source: [src/robot_systems/glue/applications/dashboard/view/glue_dashboard_view.py](../../../../../../src/robot_systems/glue/applications/dashboard/view/glue_dashboard_view.py).

Imports (including optional/function-local imports; not a startup dependency list): `PyQt6.QtCore`, `PyQt6.QtWidgets`, `__future__`, `logging`, `pl_gui.dashboard.DashboardWidget`, `src.applications.base.i_application_view`, `src.robot_systems.glue.applications.dashboard.ui.dashboard_preview_widget`, `src.robot_systems.glue.applications.dashboard.ui.system_status_widget`.

### `GlueDashboardView`

```python
class GlueDashboardView(IApplicationView):
```

View — pure Qt widget. No broker, no services, no business logic.

Declared fields/defaults:

```python
LOGOUT_REQUEST = pyqtSignal()
start_requested = pyqtSignal()
pause_requested = pyqtSignal()
stop_requested = pyqtSignal()
action_requested = pyqtSignal(str)
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, config, action_buttons: list, cards: list, parent=None)
```

```python
def setup_ui(self)
```

```python
def set_process_state(self, state: str) -> None
```

```python
def set_active_process(self, process_id: str) -> None
```

```python
def set_system_state(self, state: str) -> None
```

```python
def set_service_warning(self, message: str) -> None
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
def set_preview_overlay(self, image, segments: list[dict]) -> None
```

```python
def set_preview_progress(self, snapshot: dict | None) -> None
```

```python
def set_preview_robot_point(self, point) -> None
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
def set_action_button_text(self, action_id: str, text: str) -> None
```

```python
def set_action_button_enabled(self, action_id: str, enabled: bool)
```

```python
def get_card(self, card_id: int)
```

```python
def minimumSizeHint(self) -> QSize
```

```python
def sizeHint(self) -> QSize
```
