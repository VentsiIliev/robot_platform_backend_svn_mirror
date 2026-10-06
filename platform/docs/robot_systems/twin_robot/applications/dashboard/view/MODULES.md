# Module reference: `src/robot_systems/twin_robot/applications/dashboard/view`

[Package guide](README.md) · [Complete source index](../../../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [twin_dashboard_view.py](#twin_dashboard_viewpy)

## `__init__.py`

Source: [src/robot_systems/twin_robot/applications/dashboard/view/__init__.py](../../../../../../src/robot_systems/twin_robot/applications/dashboard/view/__init__.py).

Imports (including optional/function-local imports; not a startup dependency list): `src.robot_systems.twin_robot.applications.dashboard.view.twin_dashboard_view`.

Package-level import/export surface:

```python
from src.robot_systems.twin_robot.applications.dashboard.view.twin_dashboard_view import TwinDashboardView
```

Module declarations (expressions are shown without evaluating them):

```python
__all__ = ['TwinDashboardView']
```

## `twin_dashboard_view.py`

Source: [src/robot_systems/twin_robot/applications/dashboard/view/twin_dashboard_view.py](../../../../../../src/robot_systems/twin_robot/applications/dashboard/view/twin_dashboard_view.py).

Imports (including optional/function-local imports; not a startup dependency list): `PyQt6.QtCore`, `PyQt6.QtWidgets`, `__future__`, `pl_gui.settings.settings_view.styles`, `src.applications.base.i_application_view`, `src.applications.base.widgets.custom_virtual_keyboard`.

### `TwinDashboardView`

```python
class TwinDashboardView(IApplicationView):
```

Declared fields/defaults:

```python
SHOW_JOG_WIDGET = False
choreography_selected = pyqtSignal(str)
plan_requested = pyqtSignal()
start_requested = pyqtSignal(int)
stop_requested = pyqtSignal()
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, parent=None)
```

```python
def setup_ui(self) -> None
```

```python
def set_choreographies(self, items) -> None
```

```python
def select_first_choreography(self) -> None
```

```python
def set_loop_count(self, value: int) -> None
```

```python
def set_busy(self, busy: bool, message: str='') -> None
```

```python
def set_plan_status(self, robot1_ready: bool, robot2_ready: bool, message: str='') -> None
```

```python
def set_message(self, message: str) -> None
```

```python
def retranslateUi(self) -> None
```

```python
def clean_up(self) -> None
```
