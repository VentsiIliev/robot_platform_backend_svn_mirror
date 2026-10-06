# Module reference: `src/engine/vision/implementation/VisionSystem/features/contour_matching/matching`

[Package guide](README.md) · [Complete source index](../../../../../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [best_match_result.py](#best_match_resultpy)
- [match_info.py](#match_infopy)
- [normalized_mask_overlap.py](#normalized_mask_overlappy)

## `__init__.py`

Source: [src/engine/vision/implementation/VisionSystem/features/contour_matching/matching/__init__.py](../../../../../../../../src/engine/vision/implementation/VisionSystem/features/contour_matching/matching/__init__.py).

No top-level functions, classes or public value declarations; inspect the source for imports or entry-point statements.

## `best_match_result.py`

Source: [src/engine/vision/implementation/VisionSystem/features/contour_matching/matching/best_match_result.py](../../../../../../../../src/engine/vision/implementation/VisionSystem/features/contour_matching/matching/best_match_result.py).

Imports (including optional/function-local imports; not a startup dependency list): `dataclasses`, `numpy`, `typing`.

### `BestMatchResult`

```python
@dataclass
class BestMatchResult:
```

Declared fields/defaults:

```python
workpiece: Optional[Any]
confidence: float
result: str
centroid_diff: Optional[np.ndarray] = None
rotation_diff: Optional[float] = None
contour_angle: Optional[float] = None
workpiece_id: Optional[int] = None
reflected: bool = False
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
@property
def is_match(self) -> bool
```

Helper property to check if a valid match was found.

## `match_info.py`

Source: [src/engine/vision/implementation/VisionSystem/features/contour_matching/matching/match_info.py](../../../../../../../../src/engine/vision/implementation/VisionSystem/features/contour_matching/matching/match_info.py).

Imports (including optional/function-local imports; not a startup dependency list): `dataclasses`, `numpy`, `src.engine.vision.implementation.VisionSystem.core.models.contour`, `typing`.

### `MatchInfo`

```python
@dataclass
class MatchInfo:
```

Stores information about a matched contour and its corresponding workpiece.

Declared fields/defaults:

```python
workpiece: Any
new_contour: np.ndarray
centroid_diff: Optional[Any]
rotation_diff: Optional[Any]
contour_orientation: Optional[float]
contourObj: Optional[Contour] = None
sprayContourObjs: Optional[list[Contour]] = None
sprayFillObjs: Optional[list[Contour]] = None
mlConfidence: float = 0.0
mlResult: str = 'UNKNOWN'
reflected: bool = False
pickupObj: Optional[Contour] = None
```

## `normalized_mask_overlap.py`

Source: [src/engine/vision/implementation/VisionSystem/features/contour_matching/matching/normalized_mask_overlap.py](../../../../../../../../src/engine/vision/implementation/VisionSystem/features/contour_matching/matching/normalized_mask_overlap.py).

Compare contour silhouettes independently of position, rotation, and scale.

Imports (including optional/function-local imports; not a startup dependency list): `cv2`, `numpy`.

### `normalized_mask_overlap`

```python
def normalized_mask_overlap(first, second) -> float
```

Return the best filled-mask intersection over union over planar rotations.

### `_center_and_scale`

```python
def _center_and_scale(points: np.ndarray) -> np.ndarray | None
```

### `_filled_mask`

```python
def _filled_mask(points: np.ndarray, size: int, center: tuple[float, float]) -> np.ndarray
```

### `_rotated_overlap`

```python
def _rotated_overlap(first_mask: np.ndarray, second_mask: np.ndarray, center: tuple[float, float], angle: float) -> float
```
