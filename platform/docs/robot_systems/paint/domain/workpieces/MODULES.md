# Module reference: `src/robot_systems/paint/domain/workpieces`

[Package guide](README.md) · [Complete source index](../../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [matching_selection.py](#matching_selectionpy)
- [paint_workpiece_library_service.py](#paint_workpiece_library_servicepy)

## `__init__.py`

Source: [src/robot_systems/paint/domain/workpieces/__init__.py](../../../../../src/robot_systems/paint/domain/workpieces/__init__.py).

Imports (including optional/function-local imports; not a startup dependency list): `src.robot_systems.paint.domain.workpieces.paint_workpiece_library_service`, `src.robot_systems.paint.domain.workpieces.repository.json_paint_workpiece_repository`, `src.robot_systems.paint.domain.workpieces.service.paint_workpiece_service`.

Package-level import/export surface:

```python
from src.robot_systems.paint.domain.workpieces.paint_workpiece_library_service import PaintWorkpieceLibraryService, build_paint_workpiece_library_schema
from src.robot_systems.paint.domain.workpieces.repository.json_paint_workpiece_repository import JsonPaintWorkpieceRepository
from src.robot_systems.paint.domain.workpieces.service.paint_workpiece_service import PaintWorkpieceService
```

Module declarations (expressions are shown without evaluating them):

```python
__all__ = ['PaintWorkpieceLibraryService', 'build_paint_workpiece_library_schema', 'JsonPaintWorkpieceRepository', 'PaintWorkpieceService']
```

## `matching_selection.py`

Source: [src/robot_systems/paint/domain/workpieces/matching_selection.py](../../../../../src/robot_systems/paint/domain/workpieces/matching_selection.py).

Persist the paint workpieces allowed as matching candidates.

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `json`, `os`, `pathlib`, `tempfile`, `threading`, `typing`.

### `PaintMatchingSelection`

```python
class PaintMatchingSelection:
```

None means all saved workpieces; an empty tuple means no candidates.

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, path: str) -> None
```

```python
def get_selected_ids(self) -> tuple[str, ...] | None
```

```python
def set_selected_ids(self, ids: Iterable[str] | None) -> None
```

## `paint_workpiece_library_service.py`

Source: [src/robot_systems/paint/domain/workpieces/paint_workpiece_library_service.py](../../../../../src/robot_systems/paint/domain/workpieces/paint_workpiece_library_service.py).

Imports (including optional/function-local imports; not a startup dependency list): `logging`, `src.applications.workpiece_library.domain.workpiece_schema`, `typing`.

### `build_paint_workpiece_library_schema`

```python
def build_paint_workpiece_library_schema() -> WorkpieceSchema
```

### `PaintWorkpieceLibraryService`

```python
class PaintWorkpieceLibraryService:
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, workpiece_service)
```

```python
def get_schema(self) -> WorkpieceSchema
```

```python
def list_all(self) -> List[WorkpieceRecord]
```

```python
def update(self, storage_id: str, updates: dict) -> tuple[bool, str]
```

```python
def delete(self, workpiece_id: str) -> tuple[bool, str]
```

```python
def get_thumbnail(self, workpiece_id: str) -> Optional[bytes]
```

```python
def load_raw(self, storage_id: str) -> Optional[dict]
```
