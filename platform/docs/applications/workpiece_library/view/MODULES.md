# Module reference: `src/applications/workpiece_library/view`

[Package guide](README.md) · [Complete source index](../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [workpiece_library_view.py](#workpiece_library_viewpy)

## `__init__.py`

Source: [src/applications/workpiece_library/view/__init__.py](../../../../src/applications/workpiece_library/view/__init__.py).

Imports (including optional/function-local imports; not a startup dependency list): `.workpiece_library_view`.

Package-level import/export surface:

```python
from .workpiece_library_view import WorkpieceLibraryView
```

No top-level functions, classes or public value declarations; inspect the source for imports or entry-point statements.

## `workpiece_library_view.py`

Source: [src/applications/workpiece_library/view/workpiece_library_view.py](../../../../src/applications/workpiece_library/view/workpiece_library_view.py).

Imports (including optional/function-local imports; not a startup dependency list): `PyQt6.QtCore`, `PyQt6.QtGui`, `PyQt6.QtWidgets`, `logging`, `pl_gui.settings.settings_view.styles`, `pl_gui.utils.utils_widgets.table_helpers`, `qtawesome`, `src.applications.base.i_application_view`, `src.applications.base.widgets.custom_virtual_keyboard`, `src.applications.workpiece_library.domain.workpiece_schema`, `typing`.

### `WorkpieceLibraryView`

```python
class WorkpieceLibraryView(IApplicationView):
```

Declared fields/defaults:

```python
delete_requested = pyqtSignal(str)
refresh_requested = pyqtSignal()
search_changed = pyqtSignal(str)
selection_changed = pyqtSignal(object)
edit_requested = pyqtSignal(object, dict)
open_in_editor_requested = pyqtSignal(object)
selection_requested = pyqtSignal(object)
show_selected_changed = pyqtSignal(bool)
visible_thumbnails_requested = pyqtSignal(object)
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, schema: WorkpieceSchema, parent=None, *, selection_enabled: bool=False, show_thumbnails: bool=False)
```

```python
def setup_ui(self) -> None
```

```python
def clean_up(self) -> None
```

```python
def showEvent(self, event) -> None
```

```python
def set_records(self, records: List[WorkpieceRecord]) -> None
```

```python
def set_table_thumbnail(self, storage_id: str, image_bytes: Optional[bytes]) -> None
```

```python
def set_selection(self, ids: tuple[str, ...] | None) -> None
```

```python
def set_available_ids(self, ids: list[str]) -> None
```

```python
def checked_ids(self) -> set[str]
```

```python
def set_detail(self, record: Optional[WorkpieceRecord]) -> None
```

```python
def set_thumbnail(self, image_bytes: Optional[bytes]) -> None
```

```python
def set_status(self, msg: str) -> None
```

```python
def selected_record(self) -> Optional[WorkpieceRecord]
```

```python
def set_schema(self, schema: WorkpieceSchema) -> None
```

```python
def retranslateUi(self) -> None
```

```python
def changeEvent(self, event: QEvent) -> None
```
