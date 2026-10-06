# Module reference: `src/applications/remote_support/view`

[Package guide](README.md) · [Complete source index](../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [remote_support_view.py](#remote_support_viewpy)

## `__init__.py`

Source: [src/applications/remote_support/view/__init__.py](../../../../src/applications/remote_support/view/__init__.py).

Step 7 — View. Extends AppWidget — required by the shell (provides app_closed signal). Rule: pure Qt only — no services, no model, no business logic. Exposes pyqtSignals for every user action. Exposes setter methods for every piece of data the controller pushes.

Imports (including optional/function-local imports; not a startup dependency list): `PyQt6.QtCore`, `PyQt6.QtWidgets`, `pl_gui.shell.base_app_widget.AppWidget`.

Package-level import/export surface:

```python
from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QLabel, QVBoxLayout
from pl_gui.shell.base_app_widget.AppWidget import AppWidget
```

### `RemoteSupportView`

```python
class RemoteSupportView(AppWidget):
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

## `remote_support_view.py`

Source: [src/applications/remote_support/view/remote_support_view.py](../../../../src/applications/remote_support/view/remote_support_view.py).

Imports (including optional/function-local imports; not a startup dependency list): `PyQt6.QtCore`, `PyQt6.QtWidgets`, `pl_gui.settings.settings_view.styles`, `pl_gui.utils.utils_widgets.SwitchButton`, `src.applications.base.app_dialog`, `src.applications.base.i_application_view`, `src.applications.base.widgets.custom_virtual_keyboard`, `time`.

### `RemoteSupportView`

```python
class RemoteSupportView(IApplicationView):
```

Declared fields/defaults:

```python
language_changed = pyqtSignal()
remote_support_requested = pyqtSignal(bool)
remote_support_refresh_requested = pyqtSignal()
password_change_requested = pyqtSignal(str, str, str, str)
password_remove_requested = pyqtSignal(str, str)
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, parent=None)
```

```python
def setup_ui(self) -> None
```

```python
def clear_password_fields(self) -> None
```

```python
def get_access_duration(self) -> int
```

```python
def set_password_status(self, status: dict) -> None
```

```python
def set_password_error(self, message: str) -> None
```

```python
def is_remote_support_visible(self) -> bool
```

```python
def set_remote_support_status(self, status: dict) -> None
```

```python
def set_remote_support_error(self, message: str) -> None
```

```python
def set_password_operation_busy(self, busy: bool) -> None
```

```python
def set_busy(self, kind: str, busy: bool) -> None
```

```python
def set_status(self, message: str) -> None
```

```python
def set_error(self, message: str) -> None
```

```python
def retranslateUi(self) -> None
```

```python
def changeEvent(self, event) -> None
```

```python
def clean_up(self) -> None
```
