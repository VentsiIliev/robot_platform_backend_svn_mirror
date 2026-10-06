# Module reference: `src/applications/contour_matching_tester/service`

[Package guide](README.md) · [Complete source index](../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [contour_matching_tester_service.py](#contour_matching_tester_servicepy)
- [i_contour_matching_tester_service.py](#i_contour_matching_tester_servicepy)
- [stub_contour_matching_tester_service.py](#stub_contour_matching_tester_servicepy)

## `__init__.py`

Source: [src/applications/contour_matching_tester/service/__init__.py](../../../../src/applications/contour_matching_tester/service/__init__.py).

No top-level functions, classes or public value declarations; inspect the source for imports or entry-point statements.

## `contour_matching_tester_service.py`

Source: [src/applications/contour_matching_tester/service/contour_matching_tester_service.py](../../../../src/applications/contour_matching_tester/service/contour_matching_tester_service.py).

Imports (including optional/function-local imports; not a startup dependency list): `logging`, `numpy`, `src.applications.contour_matching_tester.service.i_contour_matching_tester_service`, `src.engine.vision.i_capture_snapshot_service`, `typing`.

### `_close_contour`

```python
def _close_contour(contour: np.ndarray) -> np.ndarray
```

### `MatchingWorkpieceStore`

```python
class MatchingWorkpieceStore(Protocol):
```

Storage operations shared by glue and paint matching tests.

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def list_all(self) -> list[dict]
```

```python
def load(self, storage_id: str)
```

```python
def get_thumbnail_bytes(self, storage_id: str) -> Optional[bytes]
```

### `ContourMatchingTesterService`

```python
class ContourMatchingTesterService(IContourMatchingTesterService):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, vision_service=None, workpiece_service: MatchingWorkpieceStore | None=None, capture_snapshot_service: ICaptureSnapshotService | None=None)
```

```python
def get_workpieces(self) -> list
```

```python
def get_latest_contours(self) -> list
```

```python
def run_matching(self, workpieces: list, contours: list) -> Tuple[dict, int, List, List]
```

```python
def get_thumbnail(self, workpiece_index: int) -> Optional[bytes]
```

## `i_contour_matching_tester_service.py`

Source: [src/applications/contour_matching_tester/service/i_contour_matching_tester_service.py](../../../../src/applications/contour_matching_tester/service/i_contour_matching_tester_service.py).

Imports (including optional/function-local imports; not a startup dependency list): `abc`, `typing`.

### `IContourMatchingTesterService`

```python
class IContourMatchingTesterService(ABC):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
@abstractmethod
def get_workpieces(self) -> list
```

```python
@abstractmethod
def get_latest_contours(self) -> list
```

```python
@abstractmethod
def run_matching(self, workpieces: list, contours: list) -> Tuple[dict, int, List, List]
```

Returns (match_results_dict, no_match_count, matched_contours, unmatched_contours).

```python
@abstractmethod
def get_thumbnail(self, workpiece_index: int) -> Optional[bytes]
```

Return PNG bytes for the workpiece at the given index in the last get_workpieces() result.

## `stub_contour_matching_tester_service.py`

Source: [src/applications/contour_matching_tester/service/stub_contour_matching_tester_service.py](../../../../src/applications/contour_matching_tester/service/stub_contour_matching_tester_service.py).

Imports (including optional/function-local imports; not a startup dependency list): `numpy`, `src.applications.contour_matching_tester.service.i_contour_matching_tester_service`, `typing`.

### `_StubWorkpiece`

```python
class _StubWorkpiece:
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, wp_id: int, name: str, contour: np.ndarray)
```

```python
def get_main_contour(self) -> np.ndarray
```

```python
def get_spray_pattern_contours(self) -> list
```

```python
def get_spray_pattern_fills(self) -> list
```

### `StubContourMatchingTesterService`

```python
class StubContourMatchingTesterService(IContourMatchingTesterService):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def get_workpieces(self) -> list
```

```python
def get_latest_contours(self) -> list
```

```python
def run_matching(self, workpieces: list, contours: list) -> Tuple[dict, int, List, List]
```

```python
def get_thumbnail(self, workpiece_index: int) -> Optional[bytes]
```
