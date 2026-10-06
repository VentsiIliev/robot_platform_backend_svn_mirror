# Module reference: `src/applications/workpiece_editor/editor_core/handlers`

[Package guide](README.md) · [Complete source index](../../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [CaptureDataHandler.py](#capturedatahandlerpy)
- [CaptureHandler.py](#capturehandlerpy)
- [SaveWorkpieceHandler.py](#saveworkpiecehandlerpy)
- [StartHandler.py](#starthandlerpy)
- [__init__.py](#__init__py)
- [workpiece_loader.py](#workpiece_loaderpy)

## `CaptureDataHandler.py`

Source: [src/applications/workpiece_editor/editor_core/handlers/CaptureDataHandler.py](../../../../../src/applications/workpiece_editor/editor_core/handlers/CaptureDataHandler.py).

Imports (including optional/function-local imports; not a startup dependency list): `PyQt6.QtCore`, `contour_editor`, `contour_editor.models.segment`, `contour_editor.persistence.data.editor_data_model`, `numpy`, `typing`.

### `CaptureDataHandler`

```python
class CaptureDataHandler:
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
@classmethod
def workpiece_layer_name(cls) -> str
```

```python
@classmethod
def contour_layer_name(cls) -> str
```

```python
@classmethod
def fill_layer_name(cls) -> str
```

```python
@classmethod
def handle_capture_data(cls, workpiece_manager, capture_data: Dict[str, Any], close_contour: bool=True) -> Optional[ContourEditorData]
```

```python
@classmethod
def from_capture_data(cls, contours: Any, metadata: Optional[Dict[str, Any]]=None) -> ContourEditorData
```

```python
@classmethod
def create_from_legacy_dict(cls, contours_by_layer: Dict[str, Any]) -> ContourEditorData
```

```python
@classmethod
def print_capture_summary(cls, editor_data: ContourEditorData)
```

## `CaptureHandler.py`

Source: [src/applications/workpiece_editor/editor_core/handlers/CaptureHandler.py](../../../../../src/applications/workpiece_editor/editor_core/handlers/CaptureHandler.py).

CaptureHandler - Handles workpiece-specific capture data loading This handler implements workpiece-specific capture logic using CaptureDataHandler. It's connected to the capture_data_received signal.

Imports (including optional/function-local imports; not a startup dependency list): `.CaptureDataHandler`, `PyQt6.QtCore`, `traceback`.

### `CaptureHandler`

```python
class CaptureHandler(QObject):
```

Handles workpiece-specific capture data loading. This class should be instantiated and connected to MainApplicationFrame's capture_data_received signal in workpiece-aware applications.

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, editor_frame, parent=None)
```

```python
def handle_capture_data(self, capture_data, close_contour=True)
```

Handle capture data using workpiece-specific logic. Uses CaptureDataHandler to process the capture data and load it into the editor using the workpiece manager. Args: capture_data: Dictionary with capture data close_contour: Whether to close the contour

## `SaveWorkpieceHandler.py`

Source: [src/applications/workpiece_editor/editor_core/handlers/SaveWorkpieceHandler.py](../../../../../src/applications/workpiece_editor/editor_core/handlers/SaveWorkpieceHandler.py).

Imports (including optional/function-local imports; not a startup dependency list): `typing`.

### `SaveWorkpieceHandler`

```python
class SaveWorkpieceHandler:
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
@classmethod
def validate_form_data(cls, data: Dict[str, Any], required_keys: List[str]) -> tuple[bool, List[str]]
```

## `StartHandler.py`

Source: [src/applications/workpiece_editor/editor_core/handlers/StartHandler.py](../../../../../src/applications/workpiece_editor/editor_core/handlers/StartHandler.py).

Imports (including optional/function-local imports; not a startup dependency list): `..adapters.i_workpiece_data_adapter`, `PyQt6.QtCore`, `contour_editor.persistence.data.editor_data_model`, `logging`.

### `StartHandler`

```python
class StartHandler(QObject):
```

Intercepts the editor's start_requested signal, validates material type assignments on all segments, then re-emits execute_requested. System-agnostic — validates that a material_type_key field is set on every segment, but knows nothing about GlueType or any specific type.

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, editor_frame, adapter: IWorkpieceDataAdapter, parent=None)
```

```python
def handle_start(self) -> None
```

## `__init__.py`

Source: [src/applications/workpiece_editor/editor_core/handlers/__init__.py](../../../../../src/applications/workpiece_editor/editor_core/handlers/__init__.py).

Imports (including optional/function-local imports; not a startup dependency list): `.CaptureDataHandler`, `.CaptureHandler`, `.SaveWorkpieceHandler`, `.StartHandler`, `.workpiece_loader`.

Package-level import/export surface:

```python
from .CaptureDataHandler import CaptureDataHandler
from .CaptureHandler import CaptureHandler
from .SaveWorkpieceHandler import SaveWorkpieceHandler
from .StartHandler import StartHandler
from .workpiece_loader import load_workpiece
```

Module declarations (expressions are shown without evaluating them):

```python
__all__ = ['CaptureDataHandler', 'CaptureHandler', 'SaveWorkpieceHandler', 'StartHandler', 'load_workpiece']
```

## `workpiece_loader.py`

Source: [src/applications/workpiece_editor/editor_core/handlers/workpiece_loader.py](../../../../../src/applications/workpiece_editor/editor_core/handlers/workpiece_loader.py).

Imports (including optional/function-local imports; not a startup dependency list): `..adapters.i_workpiece_data_adapter`.

### `load_workpiece`

```python
def load_workpiece(workpiece, adapter: IWorkpieceDataAdapter)
```
