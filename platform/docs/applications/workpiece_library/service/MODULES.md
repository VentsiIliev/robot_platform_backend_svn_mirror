# Module reference: `src/applications/workpiece_library/service`

[Package guide](README.md) · [Complete source index](../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [i_workpiece_library_service.py](#i_workpiece_library_servicepy)
- [i_workpiece_selection.py](#i_workpiece_selectionpy)
- [stub_workpiece_library_service.py](#stub_workpiece_library_servicepy)

## `__init__.py`

Source: [src/applications/workpiece_library/service/__init__.py](../../../../src/applications/workpiece_library/service/__init__.py).

Imports (including optional/function-local imports; not a startup dependency list): `.i_workpiece_library_service`.

Package-level import/export surface:

```python
from .i_workpiece_library_service import IWorkpieceLibraryService
```

No top-level functions, classes or public value declarations; inspect the source for imports or entry-point statements.

## `i_workpiece_library_service.py`

Source: [src/applications/workpiece_library/service/i_workpiece_library_service.py](../../../../src/applications/workpiece_library/service/i_workpiece_library_service.py).

Imports (including optional/function-local imports; not a startup dependency list): `abc`, `src.applications.workpiece_library.domain.workpiece_schema`, `typing`.

### `IWorkpieceLibraryService`

```python
class IWorkpieceLibraryService(ABC):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
@abstractmethod
def get_schema(self) -> WorkpieceSchema
```

```python
@abstractmethod
def list_all(self) -> List[WorkpieceRecord]
```

```python
@abstractmethod
def update(self, storage_id: str, updates: dict) -> tuple[bool, str]
```

```python
@abstractmethod
def delete(self, workpiece_id: str) -> tuple[bool, str]
```

```python
@abstractmethod
def get_thumbnail(self, workpiece_id: str) -> Optional[bytes]
```

```python
@abstractmethod
def load_raw(self, storage_id: str) -> Optional[dict]
```

Return the raw stored dict for a workpiece by its storage (timestamp) ID.

## `i_workpiece_selection.py`

Source: [src/applications/workpiece_library/service/i_workpiece_selection.py](../../../../src/applications/workpiece_library/service/i_workpiece_selection.py).

Optional selection contract for a workpiece library.

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `typing`.

### `IWorkpieceSelection`

```python
class IWorkpieceSelection(Protocol):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def get_selected_ids(self) -> tuple[str, ...] | None
```

Return selected storage IDs, or None when all are selected.

```python
def set_selected_ids(self, ids: tuple[str, ...] | None) -> None
```

Save selected IDs; an empty tuple selects none, None selects all.

## `stub_workpiece_library_service.py`

Source: [src/applications/workpiece_library/service/stub_workpiece_library_service.py](../../../../src/applications/workpiece_library/service/stub_workpiece_library_service.py).

Imports (including optional/function-local imports; not a startup dependency list): `logging`, `src.applications.workpiece_library.domain.workpiece_schema`, `src.applications.workpiece_library.service.i_workpiece_library_service`, `typing`.

### `StubWorkpieceLibraryService`

```python
class StubWorkpieceLibraryService(IWorkpieceLibraryService):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, schema: WorkpieceSchema=_STUB_SCHEMA)
```

```python
def get_schema(self) -> WorkpieceSchema
```

```python
def list_all(self) -> List[WorkpieceRecord]
```

```python
def delete(self, workpiece_id: str) -> tuple[bool, str]
```

```python
def get_thumbnail(self, workpiece_id: str) -> Optional[bytes]
```

```python
def update(self, storage_id: str, updates: dict) -> tuple[bool, str]
```

```python
def load_raw(self, storage_id: str) -> Optional[dict]
```
