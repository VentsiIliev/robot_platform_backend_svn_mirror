# Module reference: `src/robot_systems/glue/applications/glue_process_driver/view`

[Package guide](README.md) · [Complete source index](../../../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [glue_process_driver_view.py](#glue_process_driver_viewpy)

## `__init__.py`

Source: [src/robot_systems/glue/applications/glue_process_driver/view/__init__.py](../../../../../../src/robot_systems/glue/applications/glue_process_driver/view/__init__.py).

Imports (including optional/function-local imports; not a startup dependency list): `src.robot_systems.glue.applications.glue_process_driver.view.glue_process_driver_view`.

Package-level import/export surface:

```python
from src.robot_systems.glue.applications.glue_process_driver.view.glue_process_driver_view import GlueProcessDriverView
```

Module declarations (expressions are shown without evaluating them):

```python
__all__ = ['GlueProcessDriverView']
```

## `glue_process_driver_view.py`

Source: [src/robot_systems/glue/applications/glue_process_driver/view/glue_process_driver_view.py](../../../../../../src/robot_systems/glue/applications/glue_process_driver/view/glue_process_driver_view.py).

Imports (including optional/function-local imports; not a startup dependency list): `PyQt6.QtCore`, `PyQt6.QtWidgets`, `__future__`, `json`, `pl_gui.settings.settings_view.styles`, `src.applications.base.i_application_view`.

### `GlueProcessDriverView`

```python
class GlueProcessDriverView(IApplicationView):
```

Declared fields/defaults:

```python
SHOW_JOG_WIDGET = True
JOG_FRAME_SELECTOR_ENABLED = True
capture_match_requested = pyqtSignal()
build_job_requested = pyqtSignal()
load_job_requested = pyqtSignal(bool)
manual_mode_toggled = pyqtSignal(bool)
step_requested = pyqtSignal()
start_requested = pyqtSignal()
pause_requested = pyqtSignal()
resume_requested = pyqtSignal()
stop_requested = pyqtSignal()
reset_errors_requested = pyqtSignal()
refresh_requested = pyqtSignal()
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, parent=None)
```

```python
def setup_ui(self) -> None
```

```python
def set_process_snapshot(self, snapshot: dict) -> None
```

```python
def set_match_summary(self, summary: dict) -> None
```

```python
def set_matched_workpieces(self, workpieces: list) -> None
```

```python
def get_selected_match_indexes(self) -> list[int]
```

```python
def set_job_summary(self, job_summary) -> None
```

```python
def set_manual_mode_enabled(self, enabled: bool) -> None
```

```python
def clean_up(self) -> None
```
