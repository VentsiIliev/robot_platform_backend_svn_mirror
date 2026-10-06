# Module reference: `src/robot_systems/welding/domain`

[Package guide](README.md) · [Complete source index](../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [contour_editor_schema.py](#contour_editor_schemapy)

## `__init__.py`

Source: [src/robot_systems/welding/domain/__init__.py](../../../../src/robot_systems/welding/domain/__init__.py).

No top-level functions, classes or public value declarations; inspect the source for imports or entry-point statements.

## `contour_editor_schema.py`

Source: [src/robot_systems/welding/domain/contour_editor_schema.py](../../../../src/robot_systems/welding/domain/contour_editor_schema.py).

Imports (including optional/function-local imports; not a startup dependency list): `src.applications.workpiece_editor.editor_core.config.segment_settings_schema`, `src.applications.workpiece_editor.editor_core.config.workpiece_form_schema`.

### `build_welding_contour_form_schema`

```python
def build_welding_contour_form_schema() -> WorkpieceFormSchema
```

### `build_welding_segment_settings_schema`

```python
def build_welding_segment_settings_schema() -> SegmentSettingsSchema
```
