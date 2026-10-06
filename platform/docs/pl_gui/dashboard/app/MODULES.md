# Module reference: `pl_gui/dashboard/app`

[Package guide](README.md) · [Complete source index](../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [BasicDashboardAppWidget.py](#basicdashboardappwidgetpy)
- [__init__.py](#__init__py)

## `BasicDashboardAppWidget.py`

Source: [pl_gui/dashboard/app/BasicDashboardAppWidget.py](../../../../pl_gui/dashboard/app/BasicDashboardAppWidget.py).

Imports (including optional/function-local imports; not a startup dependency list): `PyQt6.QtCore`, `PyQt6.QtWidgets`, `pl_gui.dashboard.DashboardWidget`, `pl_gui.shell.base_app_widget.AppWidget`.

### `BasicDashboardAppWidget`

```python
class BasicDashboardAppWidget(AppWidget):
```

Level 3 — generic UI shell for any dashboard adapter. Responsibilities: - Builds and owns DashboardWidget internally - Re-emits DashboardWidget signals as its own public API - Exposes setter methods that the adapter calls to update the UI - Forwards Qt LanguageChange to retranslateUi() Has zero knowledge of any adapter, container, or backend. The adapter receives this widget and wires itself to it.

Declared fields/defaults:

```python
LOGOUT_REQUEST = pyqtSignal()
start_requested = pyqtSignal()
pause_requested = pyqtSignal()
stop_requested = pyqtSignal()
action_requested = pyqtSignal(str)
language_changed = pyqtSignal()
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, parent=None)
```

```python
def setup_ui(self)
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
def set_action_button_text(self, action_id: str, text: str) -> None
```

```python
def set_action_button_enabled(self, action_id: str, enabled: bool) -> None
```

```python
def get_card(self, card_id: int)
```

Return the card widget for *card_id* (used by adapter for sub-signals).

```python
def retranslateUi(self) -> None
```

```python
def changeEvent(self, event) -> None
```

```python
def closeEvent(self, event)
```

```python
def clean_up(self)
```

## `__init__.py`

Source: [pl_gui/dashboard/app/__init__.py](../../../../pl_gui/dashboard/app/__init__.py).

No top-level functions, classes or public value declarations; inspect the source for imports or entry-point statements.
