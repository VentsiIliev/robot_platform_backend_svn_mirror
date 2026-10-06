# Module reference: `src/robot_systems/twin_robot/applications/choreography_setup/view`

[Package guide](README.md) · [Complete source index](../../../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [choreography_setup_view.py](#choreography_setup_viewpy)

## `__init__.py`

Source: [src/robot_systems/twin_robot/applications/choreography_setup/view/__init__.py](../../../../../../src/robot_systems/twin_robot/applications/choreography_setup/view/__init__.py).

Imports (including optional/function-local imports; not a startup dependency list): `src.robot_systems.twin_robot.applications.choreography_setup.view.choreography_setup_view`.

Package-level import/export surface:

```python
from src.robot_systems.twin_robot.applications.choreography_setup.view.choreography_setup_view import ChoreographySetupView
```

Module declarations (expressions are shown without evaluating them):

```python
__all__ = ['ChoreographySetupView']
```

## `choreography_setup_view.py`

Source: [src/robot_systems/twin_robot/applications/choreography_setup/view/choreography_setup_view.py](../../../../../../src/robot_systems/twin_robot/applications/choreography_setup/view/choreography_setup_view.py).

Imports (including optional/function-local imports; not a startup dependency list): `PyQt6.QtCore`, `PyQt6.QtWidgets`, `__future__`, `pl_gui.settings.settings_view.styles`, `src.applications.base.i_application_view`, `src.applications.base.robot_jog_widget`, `src.applications.base.widgets.custom_virtual_keyboard`, `typing`.

### `ChoreographySetupView`

```python
class ChoreographySetupView(IApplicationView):
```

Declared fields/defaults:

```python
SHOW_JOG_WIDGET = False
new_requested = pyqtSignal(str, str)
save_requested = pyqtSignal()
load_requested = pyqtSignal(str)
add_step_requested = pyqtSignal()
delete_step_requested = pyqtSignal(int)
capture_robot_requested = pyqtSignal(str, int)
capture_both_requested = pyqtSignal(int)
robot_jog_requested = pyqtSignal(str, str, str, str, float)
robot_jog_stopped = pyqtSignal(str)
robot_joint_jog_requested = pyqtSignal(str, str, str, str, float)
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, parent=None)
```

```python
def setup_ui(self) -> None
```

```python
def selected_row(self) -> int
```

```python
def set_message(self, message: str) -> None
```

```python
def set_library(self, choreographies: List[Dict[str, Any]], selected_id: str | None=None) -> None
```

```python
def set_definition(self, choreography: Dict[str, Any], selected_row: int=0) -> None
```

```python
def editor_snapshot(self) -> Dict[str, Any]
```

```python
def set_robot_state(self, robot_name: str, pose: List[float], joints: List[float]) -> None
```

```python
def retranslateUi(self) -> None
```

```python
def clean_up(self) -> None
```
