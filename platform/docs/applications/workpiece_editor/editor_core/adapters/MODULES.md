# Module reference: `src/applications/workpiece_editor/editor_core/adapters`

[Package guide](README.md) · [Complete source index](../../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [adapter_utils.py](#adapter_utilspy)
- [i_workpiece_data_adapter.py](#i_workpiece_data_adapterpy)
- [workpiece_adapter.py](#workpiece_adapterpy)

## `__init__.py`

Source: [src/applications/workpiece_editor/editor_core/adapters/__init__.py](../../../../../src/applications/workpiece_editor/editor_core/adapters/__init__.py).

Imports (including optional/function-local imports; not a startup dependency list): `.i_workpiece_data_adapter`, `.workpiece_adapter`.

Package-level import/export surface:

```python
from .i_workpiece_data_adapter import IWorkpieceDataAdapter
```

Module declarations (expressions are shown without evaluating them):

```python
__all__ = ['IWorkpieceDataAdapter', 'WorkpieceAdapter']
```

### `__getattr__`

```python
def __getattr__(name)
```

## `adapter_utils.py`

Source: [src/applications/workpiece_editor/editor_core/adapters/adapter_utils.py](../../../../../src/applications/workpiece_editor/editor_core/adapters/adapter_utils.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `contour_editor`, `contour_editor.models.segment`, `contour_editor.persistence.data.editor_data_model`, `logging`, `math`, `numpy`, `typing`.

### `workpiece_layer_name`

```python
def workpiece_layer_name() -> str
```

### `contour_layer_name`

```python
def contour_layer_name() -> str
```

### `fill_layer_name`

```python
def fill_layer_name() -> str
```

### `ensure_complete_settings`

```python
def ensure_complete_settings(segment_settings: Optional[Dict[str, Any]], defaults: Optional[Dict[str, Any]]=None) -> Dict[str, Any]
```

### `unwrap_raw_contour_entry`

```python
def unwrap_raw_contour_entry(raw_contour)
```

### `segments_to_contour_array`

```python
def segments_to_contour_array(segments) -> np.ndarray
```

### `normalize_layer_data`

```python
def normalize_layer_data(layer_data)
```

### `segment_to_contour_array`

```python
def segment_to_contour_array(segment: Segment) -> Optional[np.ndarray]
```

### `sample_segment_points`

```python
def sample_segment_points(segment: Segment, samples_per_curve: int=12) -> list[list[float]]
```

### `is_effective_control_point`

```python
def is_effective_control_point(p0, cp, p1, threshold: float=1.0) -> bool
```

### `print_summary`

```python
def print_summary(editor_data: ContourEditorData) -> None
```

## `i_workpiece_data_adapter.py`

Source: [src/applications/workpiece_editor/editor_core/adapters/i_workpiece_data_adapter.py](../../../../../src/applications/workpiece_editor/editor_core/adapters/i_workpiece_data_adapter.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `abc`, `contour_editor.persistence.data.editor_data_model`, `typing`.

### `IWorkpieceDataAdapter`

```python
class IWorkpieceDataAdapter(ABC):
```

Convert between system-specific workpiece payloads/objects and editor data.

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
@abstractmethod
def from_workpiece(self, workpiece) -> ContourEditorData
```

```python
@abstractmethod
def to_workpiece_data(self, editor_data: ContourEditorData, default_settings: Optional[Dict[str, Any]]=None) -> Dict[str, Any]
```

```python
@abstractmethod
def from_raw(self, raw: dict) -> ContourEditorData
```

```python
@abstractmethod
def print_summary(self, editor_data: ContourEditorData) -> None
```

## `workpiece_adapter.py`

Source: [src/applications/workpiece_editor/editor_core/adapters/workpiece_adapter.py](../../../../../src/applications/workpiece_editor/editor_core/adapters/workpiece_adapter.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `logging`, `src.robot_systems.paint.domain.paint_workpiece_editor_adapter`.

### `WorkpieceAdapter`

```python
class WorkpieceAdapter(PaintWorkpieceEditorAdapter):
```

Legacy compatibility shim. New code should inject a system-specific ``IWorkpieceDataAdapter`` instead of importing a global adapter. This alias remains only for older editor entry points that still expect ``WorkpieceAdapter``.

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self)
```

```python
@classmethod
def from_workpiece(cls, workpiece)
```

```python
@classmethod
def to_workpiece_data(cls, editor_data, default_settings=None)
```

```python
@classmethod
def from_raw(cls, raw: dict)
```

```python
@classmethod
def print_summary(cls, editor_data)
```
