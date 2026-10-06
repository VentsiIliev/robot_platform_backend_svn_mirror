# Module reference: `src/applications/workpiece_editor/editor_core/models`

[Package guide](README.md) · [Complete source index](../../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [base_workpiece.py](#base_workpiecepy)
- [workpiece.py](#workpiecepy)
- [workpiece_field.py](#workpiece_fieldpy)
- [workpiece_field_provider.py](#workpiece_field_providerpy)

## `__init__.py`

Source: [src/applications/workpiece_editor/editor_core/models/__init__.py](../../../../../src/applications/workpiece_editor/editor_core/models/__init__.py).

Imports (including optional/function-local imports; not a startup dependency list): `.base_workpiece`, `.workpiece`, `.workpiece_field`.

Package-level import/export surface:

```python
from .base_workpiece import BaseWorkpiece
from .workpiece import GenericWorkpiece, WorkpieceFactory
from .workpiece_field import WorkpieceField
```

Module declarations (expressions are shown without evaluating them):

```python
__all__ = ['BaseWorkpiece', 'GenericWorkpiece', 'WorkpieceFactory', 'WorkpieceField']
```

## `base_workpiece.py`

Source: [src/applications/workpiece_editor/editor_core/models/base_workpiece.py](../../../../../src/applications/workpiece_editor/editor_core/models/base_workpiece.py).

Imports (including optional/function-local imports; not a startup dependency list): `abc`, `typing`.

### `BaseWorkpiece`

```python
class BaseWorkpiece(ABC):
```

Abstract base class for workpiece objects. Application-agnostic interface for contour editor.

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, workpiece_id: str, name: str='')
```

```python
@abstractmethod
def to_dict(self) -> Dict[str, Any]
```

Convert workpiece to dictionary representation

```python
@classmethod
@abstractmethod
def from_dict(cls, data: Dict[str, Any]) -> 'BaseWorkpiece'
```

Create workpiece from dictionary data

### `GenericWorkpiece`

```python
class GenericWorkpiece(BaseWorkpiece):
```

Generic workpiece implementation for contour editor. Can be extended by application-specific workpiece classes.

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, workpiece_id: str, name: str='', **kwargs)
```

```python
def to_dict(self) -> Dict[str, Any]
```

Convert to dictionary

```python
@classmethod
def from_dict(cls, data: Dict[str, Any]) -> 'GenericWorkpiece'
```

Create from dictionary

### `WorkpieceFactory`

```python
class WorkpieceFactory:
```

Factory for creating application-specific workpiece instances. Allows contour editor to remain decoupled from specific implementations.

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
@classmethod
def set_workpiece_class(cls, workpiece_class: type)
```

Set the workpiece class to use for creating instances. Args: workpiece_class: Class that implements BaseWorkpiece interface

```python
@classmethod
def create_workpiece(cls, data: Dict[str, Any]) -> BaseWorkpiece
```

Create a workpiece instance from data dictionary. Args: data: Dictionary with workpiece data Returns: Instance of configured workpiece class

```python
@classmethod
def get_workpiece_class(cls) -> type
```

Get the currently configured workpiece class

## `workpiece.py`

Source: [src/applications/workpiece_editor/editor_core/models/workpiece.py](../../../../../src/applications/workpiece_editor/editor_core/models/workpiece.py).

Imports (including optional/function-local imports; not a startup dependency list): `.base_workpiece`, `__future__`, `typing`.

### `GenericWorkpiece`

```python
class GenericWorkpiece(BaseWorkpiece):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, workpiece_id: str, name: str='', **kwargs)
```

```python
def to_dict(self) -> Dict[str, Any]
```

```python
@classmethod
def from_dict(cls, data: Dict[str, Any]) -> 'GenericWorkpiece'
```

### `WorkpieceFactory`

```python
class WorkpieceFactory:
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
@classmethod
def set_workpiece_class(cls, workpiece_class: type)
```

```python
@classmethod
def create_workpiece(cls, data: Dict[str, Any]) -> BaseWorkpiece
```

```python
@classmethod
def get_workpiece_class(cls) -> type
```

## `workpiece_field.py`

Source: [src/applications/workpiece_editor/editor_core/models/workpiece_field.py](../../../../../src/applications/workpiece_editor/editor_core/models/workpiece_field.py).

Imports (including optional/function-local imports; not a startup dependency list): `enum`.

### `WorkpieceField`

```python
class WorkpieceField(Enum):
```

Generic workpiece field enum for contour editor. Application-agnostic field definitions.

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

## `workpiece_field_provider.py`

Source: [src/applications/workpiece_editor/editor_core/models/workpiece_field_provider.py](../../../../../src/applications/workpiece_editor/editor_core/models/workpiece_field_provider.py).

Imports (including optional/function-local imports; not a startup dependency list): `.workpiece_field`.

### `WorkpieceFieldProvider`

```python
class WorkpieceFieldProvider:
```

Singleton provider for workpiece field configuration. Provides access to field enum and defines required fields.

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
@classmethod
def get_instance(cls)
```

Get singleton instance

```python
def get_field_enum(self)
```

Get the WorkpieceField enum class

```python
def get_required_fields(self)
```

Get list of required field names (as enum attribute names)

```python
def is_field_required(self, field_name: str) -> bool
```

Check if a field is required
