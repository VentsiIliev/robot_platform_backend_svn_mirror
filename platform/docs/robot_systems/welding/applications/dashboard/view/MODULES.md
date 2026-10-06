# Module reference: `src/robot_systems/welding/applications/dashboard/view`

[Package guide](README.md) · [Complete source index](../../../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [welding_dashboard_view.py](#welding_dashboard_viewpy)

## `welding_dashboard_view.py`

Source: [src/robot_systems/welding/applications/dashboard/view/welding_dashboard_view.py](../../../../../../src/robot_systems/welding/applications/dashboard/view/welding_dashboard_view.py).

Imports (including optional/function-local imports; not a startup dependency list): `PyQt6.QtCore`, `PyQt6.QtWidgets`, `__future__`, `pl_gui.dashboard.DashboardWidget`, `src.applications.base.i_application_view`.

### `WeldingDashboardView`

```python
class WeldingDashboardView(IApplicationView):
```

Declared fields/defaults:

```python
start_requested = pyqtSignal()
stop_requested = pyqtSignal()
pause_requested = pyqtSignal()
reset_requested = pyqtSignal()
action_requested = pyqtSignal(str)
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, config, action_buttons: list, cards: list, parent=None)
```

```python
def setup_ui(self) -> None
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
def apply_dashboard_state(self, state) -> None
```

```python
def clean_up(self) -> None
```
