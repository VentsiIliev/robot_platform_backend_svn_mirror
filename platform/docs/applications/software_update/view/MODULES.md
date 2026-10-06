# Module reference: `src/applications/software_update/view`

[Package guide](README.md) · [Complete source index](../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [software_update_view.py](#software_update_viewpy)

## `software_update_view.py`

Source: [src/applications/software_update/view/software_update_view.py](../../../../src/applications/software_update/view/software_update_view.py).

Imports (including optional/function-local imports; not a startup dependency list): `PyQt6.QtCore`, `PyQt6.QtWidgets`, `pl_gui.settings.settings_view.styles`, `src.applications.base.i_application_view`.

### `SoftwareUpdateView`

```python
class SoftwareUpdateView(IApplicationView):
```

Declared fields/defaults:

```python
SHOW_JOG_WIDGET = False
check_requested = pyqtSignal()
download_requested = pyqtSignal()
install_requested = pyqtSignal()
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, parent=None)
```

```python
def setup_ui(self)
```

```python
def set_details(self, details)
```

```python
def set_actions(self, busy: bool, enabled: bool, staged: bool)
```

```python
def set_status(self, source, **arguments)
```

```python
def set_error(self, error)
```

```python
def show_check_result(self, error=False)
```

Make an explicitly requested check result visible above the screen.

```python
def retranslateUi(self)
```

```python
def changeEvent(self, event)
```

```python
def clean_up(self)
```
