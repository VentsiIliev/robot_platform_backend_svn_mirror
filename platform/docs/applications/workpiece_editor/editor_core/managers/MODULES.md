# Module reference: `src/applications/workpiece_editor/editor_core/managers`

[Package guide](README.md) · [Complete source index](../../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [workpiece_manager.py](#workpiece_managerpy)

## `__init__.py`

Source: [src/applications/workpiece_editor/editor_core/managers/__init__.py](../../../../../src/applications/workpiece_editor/editor_core/managers/__init__.py).

Imports (including optional/function-local imports; not a startup dependency list): `.workpiece_manager`.

Package-level import/export surface:

```python
from .workpiece_manager import WorkpieceManager
```

Module declarations (expressions are shown without evaluating them):

```python
__all__ = ['WorkpieceManager']
```

## `workpiece_manager.py`

Source: [src/applications/workpiece_editor/editor_core/managers/workpiece_manager.py](../../../../../src/applications/workpiece_editor/editor_core/managers/workpiece_manager.py).

WorkpieceManager - Manages workpiece data for the contour editor. This manager provides an abstraction layer between the editor and workpiece data. It supports both: 1. Loading Workpiece objects (via WorkpieceAdapter) 2. Loading/exporting domain-agnostic ContourEditorData

Imports (including optional/function-local imports; not a startup dependency list): `..adapters.i_workpiece_data_adapter`, `..handlers.workpiece_loader`, `contour_editor`, `contour_editor.models.segment`, `contour_editor.persistence.data.editor_data_model`.

### `WorkpieceManager`

```python
class WorkpieceManager:
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, editor, adapter: IWorkpieceDataAdapter, default_settings: dict=None)
```

```python
def load_workpiece(self, workpiece)
```

Load a workpiece and initialize its contours

```python
def init_contour(self, contours_by_layer, close_contour=True)
```

Initialize contours. Supports both legacy format: { layer_name: [contour1, contour2, ...] } and new format (with settings): { layer_name: { "contours": [...], "settings": [...] } }

```python
def apply_defaults_to_segments_without_settings(self) -> None
```

Assign default settings to any segment that has none (newly drawn segments).

```python
def get_current_workpiece(self)
```

Get the currently loaded workpiece

```python
def set_current_workpiece(self, workpiece)
```

Set the current workpiece

```python
def get_contours(self)
```

Get the current contours data

```python
def clear_workpiece(self)
```

Clear the current workpiece and all segments

```python
def get_workpiece_statistics(self)
```

Get statistics about the current workpiece

```python
def validate_workpiece_data(self)
```

Validate the current workpiece data for consistency

```python
def load_editor_data(self, editor_data: ContourEditorData, close_contour=True)
```

Load domain-agnostic ContourEditorData into the editor. This method allows loading contour data without any workpiece dependency. Args: editor_data: ContourEditorData instance close_contour: Whether to close contours when converting to Bezier Returns: ContourEditorData instance (passed through)

```python
def export_editor_data(self) -> ContourEditorData
```

```python
def export_to_workpiece_data(self) -> dict
```

Export the current editor state to a workpiece-compatible data structure. This uses the WorkpieceAdapter to convert the editor data to the format needed for creating or updating Workpiece objects. Returns: Dictionary with main_contour, main_settings, and spray_pattern data
