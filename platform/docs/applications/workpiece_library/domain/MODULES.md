# Module reference: `src/applications/workpiece_library/domain`

[Package guide](README.md) · [Complete source index](../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [workpiece_schema.py](#workpiece_schemapy)

## `__init__.py`

Source: [src/applications/workpiece_library/domain/__init__.py](../../../../src/applications/workpiece_library/domain/__init__.py).

Imports (including optional/function-local imports; not a startup dependency list): `.workpiece_schema`.

Package-level import/export surface:

```python
from .workpiece_schema import WorkpieceSchema, WorkpieceRecord, WorkpieceFieldDescriptor
```

No top-level functions, classes or public value declarations; inspect the source for imports or entry-point statements.

## `workpiece_schema.py`

Source: [src/applications/workpiece_library/domain/workpiece_schema.py](../../../../src/applications/workpiece_library/domain/workpiece_schema.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `dataclasses`, `typing`.

### `WorkpieceFieldDescriptor`

```python
@dataclass
class WorkpieceFieldDescriptor:
```

Declared fields/defaults:

```python
key: str
label: str
table_display: bool = True
detail_display: bool = True
editable: bool = False
widget: str = 'text'
options: List[Any] = field(default_factory=list)
```

### `WorkpieceSchema`

```python
@dataclass
class WorkpieceSchema:
```

Declared fields/defaults:

```python
fields: List[WorkpieceFieldDescriptor]
id_key: str = 'workpieceId'
name_key: str = 'name'
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def get_table_fields(self) -> List[WorkpieceFieldDescriptor]
```

```python
def get_table_headers(self) -> List[str]
```

```python
def get_detail_fields(self) -> List[WorkpieceFieldDescriptor]
```

```python
def get_editable_fields(self) -> List[WorkpieceFieldDescriptor]
```

### `WorkpieceRecord`

```python
class WorkpieceRecord:
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, data: Dict[str, Any])
```

```python
def get(self, key: str, default: Any='') -> Any
```

```python
def get_id(self, id_key: str) -> Any
```

```python
def with_updates(self, updates: Dict[str, Any]) -> 'WorkpieceRecord'
```

```python
def to_dict(self) -> Dict[str, Any]
```
