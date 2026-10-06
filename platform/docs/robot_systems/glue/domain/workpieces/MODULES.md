# Module reference: `src/robot_systems/glue/domain/workpieces`

[Package guide](README.md) · [Complete source index](../../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [glue_workpiece_library_service.py](#glue_workpiece_library_servicepy)
- [workpiece_thumbnail.py](#workpiece_thumbnailpy)

## `__init__.py`

Source: [src/robot_systems/glue/domain/workpieces/__init__.py](../../../../../src/robot_systems/glue/domain/workpieces/__init__.py).

Imports (including optional/function-local imports; not a startup dependency list): `src.robot_systems.glue.domain.workpieces.glue_workpiece_library_service`, `src.robot_systems.glue.domain.workpieces.model.glue_workpiece`, `src.robot_systems.glue.domain.workpieces.repository.i_workpiece_repository`, `src.robot_systems.glue.domain.workpieces.repository.json_workpiece_repository`, `src.robot_systems.glue.domain.workpieces.service.i_workpiece_service`, `src.robot_systems.glue.domain.workpieces.service.workpiece_service`.

Package-level import/export surface:

```python
from src.robot_systems.glue.domain.workpieces.model.glue_workpiece import GlueWorkpiece
from src.robot_systems.glue.domain.workpieces.repository.i_workpiece_repository import IWorkpieceRepository
from src.robot_systems.glue.domain.workpieces.repository.json_workpiece_repository import JsonWorkpieceRepository
from src.robot_systems.glue.domain.workpieces.service.i_workpiece_service import IWorkpieceService
from src.robot_systems.glue.domain.workpieces.service.workpiece_service import WorkpieceService
from src.robot_systems.glue.domain.workpieces.glue_workpiece_library_service import GlueWorkpieceLibraryService, build_glue_workpiece_library_schema
```

No top-level functions, classes or public value declarations; inspect the source for imports or entry-point statements.

## `glue_workpiece_library_service.py`

Source: [src/robot_systems/glue/domain/workpieces/glue_workpiece_library_service.py](../../../../../src/robot_systems/glue/domain/workpieces/glue_workpiece_library_service.py).

Imports (including optional/function-local imports; not a startup dependency list): `json`, `logging`, `src.applications.workpiece_library.domain.workpiece_schema`, `src.applications.workpiece_library.service.i_workpiece_library_service`, `src.robot_systems.glue.domain.workpieces.model.glue_workpiece_filed`, `src.robot_systems.glue.domain.workpieces.service.i_workpiece_service`, `typing`.

Module declarations (expressions are shown without evaluating them):

```python
F = GlueWorkpieceField
```

### `build_glue_workpiece_library_schema`

```python
def build_glue_workpiece_library_schema(glue_types: List[str], tool_names) -> WorkpieceSchema
```

### `GlueWorkpieceLibraryService`

```python
class GlueWorkpieceLibraryService(IWorkpieceLibraryService):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, workpiece_service: IWorkpieceService, glue_types_fn: Callable[[], List[str]], tools_fn=None)
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

Patch only the editable fields in the stored JSON file.

```python
def load_raw(self, storage_id: str) -> Optional[dict]
```

## `workpiece_thumbnail.py`

Source: [src/robot_systems/glue/domain/workpieces/workpiece_thumbnail.py](../../../../../src/robot_systems/glue/domain/workpieces/workpiece_thumbnail.py).

Compatibility import for the shared workpiece thumbnail renderer.

Imports (including optional/function-local imports; not a startup dependency list): `src.applications.workpiece_library.workpiece_thumbnail`.

Module declarations (expressions are shown without evaluating them):

```python
__all__ = ['generate_thumbnail_bytes']
```
