# Module reference: `src/applications/workpiece_library/model`

[Package guide](README.md) · [Complete source index](../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [workpiece_library_model.py](#workpiece_library_modelpy)

## `__init__.py`

Source: [src/applications/workpiece_library/model/__init__.py](../../../../src/applications/workpiece_library/model/__init__.py).

Imports (including optional/function-local imports; not a startup dependency list): `.workpiece_library_model`.

Package-level import/export surface:

```python
from .workpiece_library_model import WorkpieceLibraryModel
```

No top-level functions, classes or public value declarations; inspect the source for imports or entry-point statements.

## `workpiece_library_model.py`

Source: [src/applications/workpiece_library/model/workpiece_library_model.py](../../../../src/applications/workpiece_library/model/workpiece_library_model.py).

Imports (including optional/function-local imports; not a startup dependency list): `src.applications.base.i_application_model`, `src.applications.workpiece_library.domain.workpiece_schema`, `src.applications.workpiece_library.service.i_workpiece_library_service`, `src.applications.workpiece_library.service.i_workpiece_selection`, `typing`.

### `WorkpieceLibraryModel`

```python
class WorkpieceLibraryModel(IApplicationModel):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, service: IWorkpieceLibraryService, selection: IWorkpieceSelection | None=None)
```

```python
@property
def schema(self) -> WorkpieceSchema
```

```python
@property
def selection_enabled(self) -> bool
```

```python
def load(self) -> List[WorkpieceRecord]
```

```python
def save(self, *args, **kwargs) -> None
```

```python
def get_all(self) -> List[WorkpieceRecord]
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

```python
def get_schema(self) -> WorkpieceSchema
```

```python
def get_selection(self) -> tuple[str, ...] | None
```

```python
def save_selection(self, ids: tuple[str, ...] | None) -> None
```
