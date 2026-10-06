# Module reference: `src/robot_systems/glue/domain/workpieces/model`

[Package guide](README.md) · [Complete source index](../../../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [glue_workpiece.py](#glue_workpiecepy)
- [glue_workpiece_filed.py](#glue_workpiece_filedpy)

## `__init__.py`

Source: [src/robot_systems/glue/domain/workpieces/model/__init__.py](../../../../../../src/robot_systems/glue/domain/workpieces/model/__init__.py).

No top-level functions, classes or public value declarations; inspect the source for imports or entry-point statements.

## `glue_workpiece.py`

Source: [src/robot_systems/glue/domain/workpieces/model/glue_workpiece.py](../../../../../../src/robot_systems/glue/domain/workpieces/model/glue_workpiece.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `copy`, `numpy`, `src.applications.workpiece_editor.editor_core.models.base_workpiece`, `src.robot_systems.glue.domain.workpieces.model.glue_workpiece_filed`, `typing`.

### `GlueWorkpiece`

```python
class GlueWorkpiece(BaseWorkpiece):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, workpieceId: str, name: str, description: str, gripperID: int, glueType: str, contour, height: float, glueQty: float, pickupPoint: Optional[Any], sprayPattern: Optional[Dict]=None)
```

```python
def get_main_contour(self) -> np.ndarray
```

```python
def get_main_contour_settings(self) -> dict
```

```python
def set_main_contour(self, contour) -> None
```

```python
def get_spray_pattern_contours(self) -> List[dict]
```

```python
def get_spray_pattern_fills(self) -> List[dict]
```

```python
def to_dict(self) -> Dict[str, Any]
```

```python
@staticmethod
def from_dict(data: dict) -> GlueWorkpiece
```

```python
@staticmethod
def serialize(workpiece: GlueWorkpiece) -> dict
```

```python
@staticmethod
def deserialize(data: dict) -> GlueWorkpiece
```

### `_to_n12`

```python
def _to_n12(data) -> np.ndarray
```

### `_contour_to_list`

```python
def _contour_to_list(obj) -> Any
```

### `_spray_to_list`

```python
def _spray_to_list(spray) -> dict
```

### `_contour_from_list`

```python
def _contour_from_list(obj) -> Any
```

## `glue_workpiece_filed.py`

Source: [src/robot_systems/glue/domain/workpieces/model/glue_workpiece_filed.py](../../../../../../src/robot_systems/glue/domain/workpieces/model/glue_workpiece_filed.py).

Imports (including optional/function-local imports; not a startup dependency list): `enum`.

### `GlueWorkpieceField`

```python
class GlueWorkpieceField(Enum):
```

Enum representing standardized keys for workpieces fields. Used for consistency in shared communication and internal data structures.

Declared fields/defaults:

```python
WORKPIECE_ID = 'workpieceId'
NAME = 'name'
DESCRIPTION = 'description'
TOOL_ID = 'toolId'
GRIPPER_ID = 'gripperId'
GLUE_TYPE = 'glueType'
PROGRAM = 'program'
MATERIAL = 'material'
CONTOUR = 'contour'
OFFSET = 'offset'
HEIGHT = 'height'
SPRAY_PATTERN = 'sprayPattern'
CONTOUR_AREA = 'contourArea'
NOZZLES = 'nozzles'
GLUE_QTY = 'glue_qty'
SPRAY_WIDTH = 'spray_width'
PICKUP_POINT = 'pickup_point'
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def getAsLabel(self)
```

Returns a user-friendly label version of the enum name. Example: CONTOUR_AREA → "Contour area"

```python
def lower(self)
```

Returns the enum value in lowercase. Useful for JSON key consistency.
