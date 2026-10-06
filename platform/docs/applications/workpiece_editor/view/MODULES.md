# Module reference: `src/applications/workpiece_editor/view`

[Package guide](README.md) · [Complete source index](../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [workpiece_editor_view.py](#workpiece_editor_viewpy)

## `__init__.py`

Source: [src/applications/workpiece_editor/view/__init__.py](../../../../src/applications/workpiece_editor/view/__init__.py).

No top-level functions, classes or public value declarations; inspect the source for imports or entry-point statements.

## `workpiece_editor_view.py`

Source: [src/applications/workpiece_editor/view/workpiece_editor_view.py](../../../../src/applications/workpiece_editor/view/workpiece_editor_view.py).

Imports (including optional/function-local imports; not a startup dependency list): `PyQt6.QtCore`, `PyQt6.QtWidgets`, `contour_editor`, `logging`, `src.applications.base.i_application_view`, `src.applications.base.widgets.virtual_keyboard_widget_factory`, `src.applications.workpiece_editor.editor_core`, `src.applications.workpiece_editor.editor_core.adapters.i_workpiece_data_adapter`, `src.applications.workpiece_editor.editor_core.config`.

### `WorkpieceEditorView`

```python
class WorkpieceEditorView(IApplicationView):
```

Declared fields/defaults:

```python
save_requested = pyqtSignal(dict)
execute_requested = pyqtSignal(dict)
custom_action_requested = pyqtSignal(str)
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, schema: WorkpieceFormSchema, segment_config: SegmentEditorConfig, workpiece_data_adapter: IWorkpieceDataAdapter, ui_config=None, parent=None)
```

```python
def setup_ui(self) -> None
```

```python
def clean_up(self) -> None
```

```python
def set_capture_handler(self, handler) -> None
```

```python
def set_save_callback(self, callback) -> None
```

```python
def update_camera_feed(self, image) -> None
```

```python
def update_contours(self, contours: list) -> None
```
