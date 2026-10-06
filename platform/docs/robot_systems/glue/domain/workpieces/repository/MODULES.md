# Module reference: `src/robot_systems/glue/domain/workpieces/repository`

[Package guide](README.md) · [Complete source index](../../../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [i_workpiece_repository.py](#i_workpiece_repositorypy)
- [json_workpiece_repository.py](#json_workpiece_repositorypy)

## `__init__.py`

Source: [src/robot_systems/glue/domain/workpieces/repository/__init__.py](../../../../../../src/robot_systems/glue/domain/workpieces/repository/__init__.py).

Imports (including optional/function-local imports; not a startup dependency list): `src.robot_systems.glue.domain.workpieces.repository.i_workpiece_repository`, `src.robot_systems.glue.domain.workpieces.repository.json_workpiece_repository`.

Package-level import/export surface:

```python
from src.robot_systems.glue.domain.workpieces.repository.i_workpiece_repository import IWorkpieceRepository
from src.robot_systems.glue.domain.workpieces.repository.json_workpiece_repository import JsonWorkpieceRepository
```

No top-level functions, classes or public value declarations; inspect the source for imports or entry-point statements.

## `i_workpiece_repository.py`

Source: [src/robot_systems/glue/domain/workpieces/repository/i_workpiece_repository.py](../../../../../../src/robot_systems/glue/domain/workpieces/repository/i_workpiece_repository.py).

Imports (including optional/function-local imports; not a startup dependency list): `abc`, `typing`.

### `IWorkpieceRepository`

```python
class IWorkpieceRepository(ABC):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
@abstractmethod
def save(self, workpiece) -> str
```

Persist workpiece. Returns the saved file path.

```python
@abstractmethod
def load(self, workpiece_id: str)
```

Load a single workpiece by its timestamp ID. Returns GlueWorkpiece or None.

```python
@abstractmethod
def list_all(self) -> List[dict]
```

Return list of metadata dicts: {id, name, date, path}.

```python
@abstractmethod
def delete(self, workpiece_id: str) -> bool
```

Delete workpiece folder by timestamp ID. Returns True on success.

```python
@abstractmethod
def get_thumbnail_bytes(self, workpiece_id: str) -> Optional[bytes]
```

```python
@abstractmethod
def workpiece_id_exists(self, workpiece_id: str) -> bool
```

Return True if any stored workpiece has workpieceId == workpiece_id.

## `json_workpiece_repository.py`

Source: [src/robot_systems/glue/domain/workpieces/repository/json_workpiece_repository.py](../../../../../../src/robot_systems/glue/domain/workpieces/repository/json_workpiece_repository.py).

Imports (including optional/function-local imports; not a startup dependency list): `datetime`, `json`, `logging`, `numpy`, `os`, `shutil`, `src.applications.workpiece_library.workpiece_thumbnail`, `src.robot_systems.glue.domain.workpieces.model.glue_workpiece`, `src.robot_systems.glue.domain.workpieces.repository.i_workpiece_repository`, `traceback`, `typing`.

### `_numpy_to_python`

```python
def _numpy_to_python(obj)
```

### `JsonWorkpieceRepository`

```python
class JsonWorkpieceRepository(IWorkpieceRepository):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, storage_root: str)
```

```python
def save(self, workpiece) -> str
```

```python
def load(self, workpiece_id: str)
```

```python
def list_all(self) -> List[dict]
```

```python
def get_thumbnail_bytes(self, workpiece_id: str) -> Optional[bytes]
```

Return PNG bytes for the workpiece thumbnail, generating lazily if missing.

```python
def delete(self, workpiece_id: str) -> bool
```

```python
def workpiece_id_exists(self, workpiece_id: str) -> bool
```

```python
def update(self, storage_id: str, data: dict) -> str
```
