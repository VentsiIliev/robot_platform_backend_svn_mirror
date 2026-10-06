# Module reference: `src/robot_systems/paint/domain/workpieces/repository`

[Package guide](README.md) · [Complete source index](../../../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [json_paint_workpiece_repository.py](#json_paint_workpiece_repositorypy)

## `json_paint_workpiece_repository.py`

Source: [src/robot_systems/paint/domain/workpieces/repository/json_paint_workpiece_repository.py](../../../../../../src/robot_systems/paint/domain/workpieces/repository/json_paint_workpiece_repository.py).

Imports (including optional/function-local imports; not a startup dependency list): `datetime`, `json`, `logging`, `numpy`, `os`, `shutil`, `src.applications.workpiece_library.workpiece_thumbnail`, `typing`.

### `_numpy_to_python`

```python
def _numpy_to_python(obj)
```

### `JsonPaintWorkpieceRepository`

```python
class JsonPaintWorkpieceRepository:
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, storage_root: str)
```

```python
def save(self, workpiece: dict) -> str
```

```python
def list_all(self) -> List[dict]
```

```python
def delete(self, storage_id: str) -> bool
```

```python
def get_thumbnail_bytes(self, storage_id: str) -> Optional[bytes]
```

```python
def workpiece_id_exists(self, workpiece_id: str) -> bool
```

```python
def update(self, storage_id: str, data: dict) -> str
```

```python
def load_raw(self, storage_id: str) -> Optional[dict]
```
