# Module reference: `src/robot_systems/paint/domain`

[Package guide](README.md) · [Complete source index](../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [contour_editor_schema.py](#contour_editor_schemapy)
- [paint_segment_selection.py](#paint_segment_selectionpy)
- [paint_workpiece_editor_adapter.py](#paint_workpiece_editor_adapterpy)

## `__init__.py`

Source: [src/robot_systems/paint/domain/__init__.py](../../../../src/robot_systems/paint/domain/__init__.py).

No top-level functions, classes or public value declarations; inspect the source for imports or entry-point statements.

## `contour_editor_schema.py`

Source: [src/robot_systems/paint/domain/contour_editor_schema.py](../../../../src/robot_systems/paint/domain/contour_editor_schema.py).

Imports (including optional/function-local imports; not a startup dependency list): `contour_editor`, `src.applications.workpiece_editor.editor_core.config.segment_settings_schema`, `src.applications.workpiece_editor.editor_core.config.workpiece_form_schema`.

### `build_paint_layer_config`

```python
def build_paint_layer_config() -> ContourEditorLayerConfig
```

### `build_paint_contour_form_schema`

```python
def build_paint_contour_form_schema() -> WorkpieceFormSchema
```

### `build_paint_segment_settings_schema`

```python
def build_paint_segment_settings_schema() -> SegmentSettingsSchema
```

## `paint_segment_selection.py`

Source: [src/robot_systems/paint/domain/paint_segment_selection.py](../../../../src/robot_systems/paint/domain/paint_segment_selection.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `copy`.

Module declarations (expressions are shown without evaluating them):

```python
APPLY_PAINT_SELECTION_ACTION = 'paint.apply_rectangle_selection'
OPEN_PATH_SETTING = 'closed_path'
SELECTION_SOURCE_SETTING = 'paint_selection_source'
```

### `apply_selected_paint_segments`

```python
def apply_selected_paint_segments(editor) -> tuple[bool, str]
```

Append open Paint sections selected from the canonical Workpiece outline.

### `_contiguous_runs`

```python
def _contiguous_runs(indices: set[int]) -> list[list[int]]
```

Return ascending neighboring index runs; isolated points remain runs.

## `paint_workpiece_editor_adapter.py`

Source: [src/robot_systems/paint/domain/paint_workpiece_editor_adapter.py](../../../../src/robot_systems/paint/domain/paint_workpiece_editor_adapter.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `contour_editor.persistence.data.editor_data_model`, `logging`, `src.applications.workpiece_editor.editor_core.adapters.adapter_utils`, `src.applications.workpiece_editor.editor_core.adapters.i_workpiece_data_adapter`, `src.robot_systems.paint.domain.paint_segment_selection`, `typing`.

### `PaintWorkpieceEditorAdapter`

```python
class PaintWorkpieceEditorAdapter(IWorkpieceDataAdapter):
```

Paint-specific editor adapter. Paint owns the mapping between editor layers and persisted process geometry. The generic editor no longer needs to know that paint currently stores optional execution paths under ``sprayPattern``.

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def from_workpiece(self, workpiece) -> ContourEditorData
```

```python
def to_workpiece_data(self, editor_data: ContourEditorData, default_settings: Optional[Dict[str, Any]]=None) -> Dict[str, Any]
```

```python
def from_raw(self, raw: dict) -> ContourEditorData
```

```python
def print_summary(self, editor_data: ContourEditorData) -> None
```
