# Module reference: `src/robot_systems/paint/domain/workpieces/service`

[Package guide](README.md) · [Complete source index](../../../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [paint_workpiece_service.py](#paint_workpiece_servicepy)

## `paint_workpiece_service.py`

Source: [src/robot_systems/paint/domain/workpieces/service/paint_workpiece_service.py](../../../../../../src/robot_systems/paint/domain/workpieces/service/paint_workpiece_service.py).

Imports (including optional/function-local imports; not a startup dependency list): `logging`, `src.robot_systems.paint.domain.workpieces.errors`, `src.robot_systems.paint.processes.paint.match.matchable_workpiece`, `typing`.

### `PaintWorkpieceService`

```python
class PaintWorkpieceService:
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, repository)
```

```python
def save(self, workpiece: dict) -> tuple[bool, str]
```

```python
def list_all(self) -> List[dict]
```

```python
def list_for_matching(self) -> List[dict]
```

Strict production read: failures propagate to the typed matching boundary.

```python
def delete(self, storage_id: str) -> tuple[bool, str]
```

```python
def get_thumbnail_bytes(self, storage_id: str) -> Optional[bytes]
```

```python
def workpiece_id_exists(self, workpiece_id: str) -> bool
```

```python
def update(self, storage_id: str, data: dict) -> tuple[bool, str]
```

```python
def load_raw(self, storage_id: str) -> Optional[dict]
```

```python
def load_for_matching(self, storage_id: str) -> Optional[dict]
```

None means absent; read/parse failures propagate rather than masquerading as absence.

```python
def load(self, storage_id: str)
```

Return a saved workpiece in the shared contour-matcher shape.
