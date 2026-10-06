# Module reference: `src/applications/tool_settings/controller`

[Package guide](README.md) · [Complete source index](../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [tool_settings_controller.py](#tool_settings_controllerpy)

## `__init__.py`

Source: [src/applications/tool_settings/controller/__init__.py](../../../../src/applications/tool_settings/controller/__init__.py).

No top-level functions, classes or public value declarations; inspect the source for imports or entry-point statements.

## `tool_settings_controller.py`

Source: [src/applications/tool_settings/controller/tool_settings_controller.py](../../../../src/applications/tool_settings/controller/tool_settings_controller.py).

Imports (including optional/function-local imports; not a startup dependency list): `..model.tool_settings_model`, `..view.tool_settings_view`, `PyQt6.QtCore`, `PyQt6.QtWidgets`, `logging`, `pl_gui.settings.settings_view.styles`, `src.applications.base.app_dialog`, `src.applications.base.i_application_controller`, `src.applications.base.styled_message_box`, `src.applications.base.widgets.custom_virtual_keyboard`, `src.applications.base.widgets.keyboard_number_field`.

### `_Worker`

```python
class _Worker(QObject):
```

Declared fields/defaults:

```python
finished = pyqtSignal(object)
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, fn)
```

```python
def run(self)
```

### `_lbl`

```python
def _lbl(text: str) -> QLabel
```

### `ToolSettingsController`

```python
class ToolSettingsController(IApplicationController):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, model: ToolSettingsModel, view: ToolSettingsView)
```

```python
def load(self) -> None
```

```python
def stop(self) -> None
```

### `_ToolDialog`

```python
class _ToolDialog(AppDialog):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, tool_id=None, name: str='', parent=None)
```

```python
def get_values(self)
```

### `_SlotDialog`

```python
class _SlotDialog(AppDialog):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, tools, slot_id=None, current_tool_id=None, parent=None)
```

```python
def get_values(self)
```

### `_ToolGeometryDialog`

```python
class _ToolGeometryDialog(AppDialog):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, tool, parent=None)
```

```python
def get_values(self)
```

### `_SequencePage`

```python
class _SequencePage(QWidget):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, steps, pose_provider, parent=None)
```

```python
def values(self)
```

```python
def set_values(self, steps)
```

### `_SequenceDialog`

```python
class _SequenceDialog(AppDialog):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, slot, pose_provider, parent=None)
```

```python
def get_values(self)
```
