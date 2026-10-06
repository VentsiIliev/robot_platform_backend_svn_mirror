# Module reference: `src/robot_systems/paint/processes/paint/match`

[Package guide](README.md) · [Complete source index](../../../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [matchable_workpiece.py](#matchable_workpiecepy)
- [matching_diagnostics.py](#matching_diagnosticspy)
- [workpiece_matching_service.py](#workpiece_matching_servicepy)

## `__init__.py`

Source: [src/robot_systems/paint/processes/paint/match/__init__.py](../../../../../../src/robot_systems/paint/processes/paint/match/__init__.py).

No top-level functions, classes or public value declarations; inspect the source for imports or entry-point statements.

## `matchable_workpiece.py`

Source: [src/robot_systems/paint/processes/paint/match/matchable_workpiece.py](../../../../../../src/robot_systems/paint/processes/paint/match/matchable_workpiece.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `copy`, `numpy`.

### `MatchableWorkpiece`

```python
class MatchableWorkpiece:
```

Adapter shape expected by the shared contour matching service.

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, raw: dict, storage_id: str | None=None)
```

```python
def get_main_contour(self)
```

```python
def get_spray_pattern_contours(self)
```

```python
def get_spray_pattern_fills(self)
```

```python
def to_raw(self) -> dict
```

## `matching_diagnostics.py`

Source: [src/robot_systems/paint/processes/paint/match/matching_diagnostics.py](../../../../../../src/robot_systems/paint/processes/paint/match/matching_diagnostics.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `cv2`, `datetime`, `json`, `numpy`, `pathlib`, `src.engine.vision.implementation.VisionSystem.features.contour_matching.matching.strategies.geometric_matching_strategy`.

### `save_matching_diagnostics`

```python
def save_matching_diagnostics(debug_dump_dir: str, captured_contour, candidates: list, *, matched: bool) -> Path
```

Persist machine-readable and visual contour comparisons for one match attempt.

### `_points`

```python
def _points(contour) -> np.ndarray
```

### `_measure`

```python
def _measure(points: np.ndarray) -> dict
```

### `_match_shapes`

```python
def _match_shapes(first: np.ndarray, second: np.ndarray, method: int) -> float | None
```

### `_geometric_similarity`

```python
def _geometric_similarity(first: np.ndarray, second: np.ndarray) -> float | None
```

### `_comparison_image`

```python
def _comparison_image(captured: np.ndarray, candidates: list) -> np.ndarray
```

### `_contour_panel`

```python
def _contour_panel(points: np.ndarray, color: tuple[int, int, int], label: str) -> np.ndarray
```

## `workpiece_matching_service.py`

Source: [src/robot_systems/paint/processes/paint/match/workpiece_matching_service.py](../../../../../../src/robot_systems/paint/processes/paint/match/workpiece_matching_service.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `logging`, `src.applications.workpiece_editor.i_workpiece_matcher`, `src.engine.vision.i_capture_snapshot_service`, `src.robot_systems.paint.processes.paint.match.matchable_workpiece`, `src.robot_systems.paint.processes.paint.match.matching_diagnostics`, `typing`.

### `PaintWorkpieceMatchingService`

```python
class PaintWorkpieceMatchingService(IWorkpieceMatcher):
```

Adapt paint workpiece storage to the shared contour-matching interface.

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, *, list_saved_workpieces_fn: Optional[Callable[[], list[dict]]]=None, load_saved_workpiece_fn: Optional[Callable[[str], Optional[dict]]]=None, selected_workpiece_ids_fn: Optional[Callable[[], tuple[str, ...] | None]]=None, run_matching_fn: Optional[Callable[[list, list], tuple]]=None, capture_snapshot_service=None, debug_dump_dir: str | None=None) -> None
```

Store repository, matching, and snapshot dependencies for paint matching.

```python
def can_match_saved_workpieces(self) -> bool
```

Report whether all dependencies needed for saved-workpiece matching are available.

```python
def match_saved_workpieces(self, contour) -> tuple[bool, dict | None, str]
```

Match one captured contour against saved paint workpieces and return raw payload metadata.

```python
def run_matching(self)
```

Run full-scene matching using a fresh snapshot, mirroring the shared matching workflow.

```python
def get_last_capture_snapshot(self)
```

Return the most recent snapshot captured during a matching run.
