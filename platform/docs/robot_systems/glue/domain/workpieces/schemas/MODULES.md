# Module reference: `src/robot_systems/glue/domain/workpieces/schemas`

[Package guide](README.md) · [Complete source index](../../../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [glue_segment_settings_schema.py](#glue_segment_settings_schemapy)
- [glue_workpiece_form_schema.py](#glue_workpiece_form_schemapy)

## `__init__.py`

Source: [src/robot_systems/glue/domain/workpieces/schemas/__init__.py](../../../../../../src/robot_systems/glue/domain/workpieces/schemas/__init__.py).

Imports (including optional/function-local imports; not a startup dependency list): `.glue_segment_settings_schema`, `.glue_workpiece_form_schema`.

Package-level import/export surface:

```python
from .glue_workpiece_form_schema import build_glue_workpiece_form_schema
from .glue_segment_settings_schema import build_glue_segment_settings_schema
```

No top-level functions, classes or public value declarations; inspect the source for imports or entry-point statements.

## `glue_segment_settings_schema.py`

Source: [src/robot_systems/glue/domain/workpieces/schemas/glue_segment_settings_schema.py](../../../../../../src/robot_systems/glue/domain/workpieces/schemas/glue_segment_settings_schema.py).

Imports (including optional/function-local imports; not a startup dependency list): `src.applications.workpiece_editor.editor_core.config.segment_settings_schema`, `src.robot_systems.glue.settings.glue`.

### `build_glue_segment_settings_schema`

```python
def build_glue_segment_settings_schema(glue_types: list) -> SegmentSettingsSchema
```

## `glue_workpiece_form_schema.py`

Source: [src/robot_systems/glue/domain/workpieces/schemas/glue_workpiece_form_schema.py](../../../../../../src/robot_systems/glue/domain/workpieces/schemas/glue_workpiece_form_schema.py).

Imports (including optional/function-local imports; not a startup dependency list): `os`, `src.applications.workpiece_editor.editor_core.config.workpiece_form_schema`, `src.engine.robot.interfaces.tool_definition`, `src.robot_systems.glue.domain.workpieces.model.glue_workpiece_filed`.

Module declarations (expressions are shown without evaluating them):

```python
WORKPIECE_ID_ICON = FieldIcon.from_qta('fa5s.barcode', color=_COLOR)
WORKPIECE_NAME_ICON = FieldIcon.from_qta('fa5s.tag', color=_COLOR)
DESCRIPTION_ICON = FieldIcon.from_qta('fa5s.align-left', color=_COLOR)
HEIGHT_ICON = FieldIcon.from_qta('fa5s.ruler-vertical', color=_COLOR)
GLUE_QTY_ICON = FieldIcon.from_qta('fa5s.weight-hanging', color=_COLOR)
GRIPPER_ID_ICON = FieldIcon.from_qta('mdi.robot-industrial', color=_COLOR)
GLUE_TYPE_ICON = FieldIcon.from_qta('fa5s.eye-dropper', color=_COLOR)
```

### `_path`

```python
def _path(name: str) -> FieldIcon
```

### `build_glue_workpiece_form_schema`

```python
def build_glue_workpiece_form_schema(glue_types=None, tools=None) -> WorkpieceFormSchema
```
