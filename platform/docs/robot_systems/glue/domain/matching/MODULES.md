# Module reference: `src/robot_systems/glue/domain/matching`

[Package guide](README.md) · [Complete source index](../../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [i_matching_service.py](#i_matching_servicepy)
- [matching_service.py](#matching_servicepy)

## `__init__.py`

Source: [src/robot_systems/glue/domain/matching/__init__.py](../../../../../src/robot_systems/glue/domain/matching/__init__.py).

No top-level functions, classes or public value declarations; inspect the source for imports or entry-point statements.

## `i_matching_service.py`

Source: [src/robot_systems/glue/domain/matching/i_matching_service.py](../../../../../src/robot_systems/glue/domain/matching/i_matching_service.py).

Imports (including optional/function-local imports; not a startup dependency list): `abc`, `src.applications.workpiece_editor.i_workpiece_matcher`, `src.engine.vision.i_capture_snapshot_service`, `typing`.

### `IMatchingService`

```python
class IMatchingService(IWorkpieceMatcher, ABC):
```

Glue matching workflow, extending the editor's narrow matching port.

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
@abstractmethod
def run_matching(self) -> Tuple[dict, int, List, List]
```

Load workpieces, get latest contours, run matching. Returns (match_results_dict, no_match_count, matched, unmatched).

```python
@abstractmethod
def get_last_capture_snapshot(self) -> VisionCaptureSnapshot | None
```

Return the most recent capture snapshot used for matching, if any.

## `matching_service.py`

Source: [src/robot_systems/glue/domain/matching/matching_service.py](../../../../../src/robot_systems/glue/domain/matching/matching_service.py).

Imports (including optional/function-local imports; not a startup dependency list): `logging`, `numpy`, `src.engine.vision.i_capture_snapshot_service`, `src.engine.vision.i_vision_service`, `src.robot_systems.glue.domain.matching.i_matching_service`, `src.robot_systems.glue.domain.workpieces.service.i_workpiece_service`, `typing`.

### `_close_contour`

```python
def _close_contour(contour: np.ndarray) -> np.ndarray
```

### `MatchingService`

```python
class MatchingService(IMatchingService):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, vision_service: IVisionService, workpiece_service: IWorkpieceService, capture_snapshot_service: ICaptureSnapshotService)
```

```python
def can_match_saved_workpieces(self) -> bool
```

```python
def match_saved_workpieces(self, contour) -> Tuple[bool, dict | None, str]
```

```python
def run_matching(self) -> Tuple[dict, int, List, List]
```

```python
def get_last_capture_snapshot(self) -> VisionCaptureSnapshot | None
```
