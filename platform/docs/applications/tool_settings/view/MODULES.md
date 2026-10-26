# Module reference: `src/applications/tool_settings/view`

[Package guide](README.md) · [Complete source index](../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [tool_settings_view.py](#tool_settings_viewpy)

- [sequence_editor.py](#sequence_editorpy)

## `__init__.py`

Source: [src/applications/tool_settings/view/__init__.py](../../../../src/applications/tool_settings/view/__init__.py).

No top-level functions, classes or public value declarations; inspect the source for imports or entry-point statements.

## `tool_settings_view.py`

Source: [src/applications/tool_settings/view/tool_settings_view.py](../../../../src/applications/tool_settings/view/tool_settings_view.py).

Imports (including optional/function-local imports; not a startup dependency list): `PyQt6.QtCore`, `PyQt6.QtWidgets`, `logging`, `pl_gui.settings.settings_view.styles`, `pl_gui.utils.utils_widgets.table_helpers`, `src.applications.base.i_application_view`.

### `ToolSettingsView`

```python
class ToolSettingsView(IApplicationView):
```

Declared fields/defaults:

```python
SHOW_JOG_WIDGET = True
add_tool_requested = pyqtSignal()
edit_tool_requested = pyqtSignal(int, str)
remove_tool_requested = pyqtSignal(int)
update_slot_requested = pyqtSignal(int, int)
add_slot_requested = pyqtSignal()
edit_slot_requested = pyqtSignal(int, object)
remove_slot_requested = pyqtSignal(int)
save_slots_requested = pyqtSignal(list)
edit_geometry_requested = pyqtSignal(int)
activate_tool_requested = pyqtSignal(int)
capture_reference_requested = pyqtSignal()
capture_candidate_requested = pyqtSignal()
reset_calibration_requested = pyqtSignal()
solve_calibration_requested = pyqtSignal(int)
edit_sequences_requested = pyqtSignal(int)
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, parent=None)
```

```python
def setup_ui(self) -> None
```

```python
def set_tools(self, tools) -> None
```

```python
def set_slots(self, slots, tools) -> None
```

```python
def set_status(self, msg: str) -> None
```

```python
def set_calibration_progress(self, *, reference_captured: bool, candidate_samples: int) -> None
```

Show calibration progress and make the next valid action obvious.

```python
def selected_tool(self)
```

```python
def selected_slot_id(self)
```

```python
def selected_slot(self)
```

```python
def selected_slot_id(self)
```

```python
def clean_up(self) -> None
```

```python
def retranslateUi(self) -> None
```

```python
def changeEvent(self, event) -> None
```

## `sequence_editor.py`

Source: [src/applications/tool_settings/view/sequence_editor.py](../../../../src/applications/tool_settings/view/sequence_editor.py).

### `SequenceEditor`

```python
class SequenceEditor(QWidget):
```

Declared fields/defaults:

```python
capture_requested = pyqtSignal(int, dict)
save_requested = pyqtSignal(list, list)
cancel_requested = pyqtSignal()
reverse_requested = pyqtSignal(list)
execute_requested = pyqtSignal(int, list)
stop_requested = pyqtSignal()
```

```python
def __init__(self, parent=None)
```

```python
def set_slot(self, slot) -> None
```

```python
def append_step(self, page: int, step: dict) -> None
```

```python
def set_busy(self, busy: bool) -> None
```

```python
def set_executing(self, executing: bool) -> None
```

```python
def set_dropoff(self, steps: list) -> None
```

```python
def set_message(self, message: str) -> None
```

```python
def retranslateUi(self) -> None
```

```python
def changeEvent(self, event) -> None
```
