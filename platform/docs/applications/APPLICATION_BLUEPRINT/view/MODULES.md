# Module reference: `src/applications/APPLICATION_BLUEPRINT/view`

[Package guide](README.md) · [Complete source index](../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [my_view.py](#my_viewpy)

## `__init__.py`

Source: [src/applications/APPLICATION_BLUEPRINT/view/__init__.py](../../../../src/applications/APPLICATION_BLUEPRINT/view/__init__.py).

Step 7 — View. Extends AppWidget — required by the shell (provides app_closed signal). Rule: pure Qt only — no services, no model, no business logic. Exposes pyqtSignals for every user action. Exposes setter methods for every piece of data the controller pushes.

Imports (including optional/function-local imports; not a startup dependency list): `PyQt6.QtCore`, `PyQt6.QtWidgets`, `pl_gui.shell.base_app_widget.AppWidget`.

Package-level import/export surface:

```python
from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QLabel, QVBoxLayout
from pl_gui.shell.base_app_widget.AppWidget import AppWidget
```

### `MyView`

```python
class MyView(AppWidget):
```

Pure Qt widget — zero knowledge of services or models.

Declared fields/defaults:

```python
save_requested = pyqtSignal(str)
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, parent=None)
```

```python
def setup_ui(self) -> None
```

Override AppWidget.setup_ui() to replace the default placeholder.

```python
def set_value(self, value: str) -> None
```

```python
def retranslateUi(self) -> None
```

```python
def clean_up(self) -> None
```

Called by shell when the app is closed. Stop timers, threads etc.

## `my_view.py`

Source: [src/applications/APPLICATION_BLUEPRINT/view/my_view.py](../../../../src/applications/APPLICATION_BLUEPRINT/view/my_view.py).

Imports (including optional/function-local imports; not a startup dependency list): `PyQt6.QtCore`, `PyQt6.QtWidgets`, `src.applications.base.i_application_view`.

### `MyView`

```python
class MyView(IApplicationView):
```

Pure Qt widget — no services, no model, no business logic.

Declared fields/defaults:

```python
SHOW_JOG_WIDGET = False
JOG_FRAME_SELECTOR_ENABLED = False
save_requested = pyqtSignal(str)
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, parent=None)
```

```python
def setup_ui(self) -> None
```

```python
def set_value(self, value: str) -> None
```

```python
def retranslateUi(self) -> None
```

```python
def clean_up(self) -> None
```
