# Module reference: `src/applications/workpiece_editor/model`

[Package guide](README.md) · [Complete source index](../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [workpiece_editor_model.py](#workpiece_editor_modelpy)

## `__init__.py`

Source: [src/applications/workpiece_editor/model/__init__.py](../../../../src/applications/workpiece_editor/model/__init__.py).

Imports (including optional/function-local imports; not a startup dependency list): `src.applications.workpiece_editor.model.workpiece_editor_model`.

Package-level import/export surface:

```python
from src.applications.workpiece_editor.model.workpiece_editor_model import WorkpieceEditorModel
```

No top-level functions, classes or public value declarations; inspect the source for imports or entry-point statements.

## `workpiece_editor_model.py`

Source: [src/applications/workpiece_editor/model/workpiece_editor_model.py](../../../../src/applications/workpiece_editor/model/workpiece_editor_model.py).

Imports (including optional/function-local imports; not a startup dependency list): `src.applications.base.i_application_model`, `src.applications.workpiece_editor.editor_core.adapters.i_workpiece_data_adapter`, `src.applications.workpiece_editor.service`, `src.applications.workpiece_editor.service.i_workpiece_path_executor`.

### `WorkpieceEditorModel`

```python
class WorkpieceEditorModel(IApplicationModel):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, service: IWorkpieceEditorService)
```

```python
def load(self) -> None
```

```python
def get_workpiece_data_adapter(self) -> IWorkpieceDataAdapter
```

```python
def save(self, *args, **kwargs) -> None
```

```python
def get_contours(self) -> list
```

```python
def save_workpiece(self, data: dict) -> tuple[bool, str]
```

```python
def execute_workpiece(self, data: dict, skip_debug_plot: bool=False) -> tuple[bool, str]
```

```python
def get_last_sampled_preview_paths(self) -> list
```

```python
def get_last_raw_preview_paths(self) -> list
```

```python
def get_last_raw_pixel_preview_paths(self) -> list
```

```python
def get_last_raw_homography_preview_paths(self) -> list
```

```python
def get_last_prepared_preview_paths(self) -> list
```

```python
def get_last_curve_preview_paths(self) -> list
```

```python
def get_last_execution_preview_paths(self) -> list
```

```python
def get_last_projection_source_camera_paths(self) -> list
```

```python
def get_last_projection_source_paths(self) -> list
```

```python
def get_last_camera_preview_paths(self) -> dict[str, list]
```

```python
def get_last_pivot_preview_paths(self) -> tuple[list[list[list[float]]], list[float] | None]
```

```python
def get_last_pivot_motion_preview(self)
```

```python
def get_process_actions(self) -> tuple[WorkpieceProcessAction, ...]
```

```python
def execute_process_action(self, action_id: str) -> tuple[bool, str]
```

```python
def set_editing(self, storage_id) -> None
```

```python
def can_match_saved_workpieces(self) -> bool
```

```python
def match_saved_workpieces(self, contour) -> tuple[bool, dict | None, str]
```
