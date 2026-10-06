# Module reference: `src/engine/vision/implementation/VisionSystem/features/contour_matching`

[Package guide](README.md) · [Complete source index](../../../../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [CompareContours.py](#comparecontourspy)
- [__init__.py](#__init__py)
- [contour_matcher.py](#contour_matcherpy)
- [example_usage.py](#example_usagepy)
- [matching_config.py](#matching_configpy)
- [utils.py](#utilspy)

## `CompareContours.py`

Source: [src/engine/vision/implementation/VisionSystem/features/contour_matching/CompareContours.py](../../../../../../../src/engine/vision/implementation/VisionSystem/features/contour_matching/CompareContours.py).

Imports (including optional/function-local imports; not a startup dependency list): `src.engine.vision.implementation.VisionSystem.features.contour_matching.contour_matcher`.

Module declarations (expressions are shown without evaluating them):

```python
__all__ = ['find_matching_workpieces', 'findMatchingWorkpieces', 'match_workpieces']
```

## `__init__.py`

Source: [src/engine/vision/implementation/VisionSystem/features/contour_matching/__init__.py](../../../../../../../src/engine/vision/implementation/VisionSystem/features/contour_matching/__init__.py).

Imports (including optional/function-local imports; not a startup dependency list): `src.engine.vision.implementation.VisionSystem.features.contour_matching.contour_matcher`, `src.engine.vision.implementation.VisionSystem.features.contour_matching.matching.best_match_result`, `src.engine.vision.implementation.VisionSystem.features.contour_matching.matching.match_info`, `src.engine.vision.implementation.VisionSystem.features.contour_matching.matching.strategies.geometric_matching_strategy`, `src.engine.vision.implementation.VisionSystem.features.contour_matching.matching.strategies.ml_matching_strategy`, `src.engine.vision.implementation.VisionSystem.features.contour_matching.matching_config`, `src.engine.vision.implementation.VisionSystem.features.contour_matching.settings.contour_matching_settings`, `src.engine.vision.implementation.VisionSystem.features.contour_matching.settings.contour_matching_settings_data`, `src.engine.vision.implementation.VisionSystem.features.contour_matching.settings.contour_matching_settings_serializer`.

Package-level import/export surface:

```python
from src.engine.vision.implementation.VisionSystem.features.contour_matching.contour_matcher import find_matching_workpieces, match_workpieces
from src.engine.vision.implementation.VisionSystem.features.contour_matching.matching.best_match_result import BestMatchResult
from src.engine.vision.implementation.VisionSystem.features.contour_matching.matching.match_info import MatchInfo
from src.engine.vision.implementation.VisionSystem.features.contour_matching.matching.strategies.geometric_matching_strategy import GeometricMatchingStrategy
from src.engine.vision.implementation.VisionSystem.features.contour_matching.matching.strategies.ml_matching_strategy import MLMatchingStrategy
from src.engine.vision.implementation.VisionSystem.features.contour_matching.matching_config import get_settings, reload_settings, configure
from src.engine.vision.implementation.VisionSystem.features.contour_matching.settings.contour_matching_settings import ContourMatchingSettings
from src.engine.vision.implementation.VisionSystem.features.contour_matching.settings.contour_matching_settings_data import ContourMatchingSettingsData
from src.engine.vision.implementation.VisionSystem.features.contour_matching.settings.contour_matching_settings_serializer import ContourMatchingSettingsSerializer
```

Module declarations (expressions are shown without evaluating them):

```python
__all__ = ['find_matching_workpieces', 'match_workpieces', 'BestMatchResult', 'MatchInfo', 'GeometricMatchingStrategy', 'MLMatchingStrategy', 'get_settings', 'reload_settings', 'configure', 'ContourMatchingSettings', 'ContourMatchingSettingsData', 'ContourMatchingSettingsSerializer']
```

## `contour_matcher.py`

Source: [src/engine/vision/implementation/VisionSystem/features/contour_matching/contour_matcher.py](../../../../../../../src/engine/vision/implementation/VisionSystem/features/contour_matching/contour_matcher.py).

Imports (including optional/function-local imports; not a startup dependency list): `copy`, `numpy`, `pathlib`, `src.engine.vision.implementation.VisionSystem.core.models.contour`, `src.engine.vision.implementation.VisionSystem.features.contour_matching.alignment.contour_aligner`, `src.engine.vision.implementation.VisionSystem.features.contour_matching.matching.best_match_result`, `src.engine.vision.implementation.VisionSystem.features.contour_matching.matching.match_info`, `src.engine.vision.implementation.VisionSystem.features.contour_matching.matching.strategies.geometric_matching_strategy`, `src.engine.vision.implementation.VisionSystem.features.contour_matching.matching.strategies.matching_strategy_interface`, `src.engine.vision.implementation.VisionSystem.features.contour_matching.matching.strategies.ml_matching_strategy`, `src.engine.vision.implementation.VisionSystem.features.contour_matching.matching_config`, `src.engine.vision.implementation.VisionSystem.features.contour_matching.utils`, `src.engine.vision.implementation.VisionSystem.features.shape_matching_training.utils.io_utils`, `typing`.

### `_load_ml_model`

```python
def _load_ml_model() -> Any
```

### `find_matching_workpieces`

```python
def find_matching_workpieces(workpieces: list, new_contours: list[np.ndarray], debug: bool=False) -> tuple[dict, list, list]
```

Top-level entry point: match detected contours to known workpieces and align them. Pipeline -------- 1. match_workpieces — find best workpiece per detected contour 2. prepare_data_for_alignment — attach Contour objects to each MatchInfo 3. _alignContours — rotate + translate + optional mask refinement, then call update_workpiece_data Args: workpieces: Objects implementing get_main_contour(), get_spray_pattern_contours(), get_spray_pattern_fills(). new_contours: Raw numpy contour arrays from the camera. debug: True → override all debug flags (saves plots to debug/output/). False → each flag follows ContourMatchingSettings. Returns: (final_matches dict, no_matches list, matched_contours list)

### `_reject_poor_alignment`

```python
def _reject_poor_alignment(final_matches, no_matches, matched_contours)
```

Reject shapes whose saved contour did not align with the camera contour.

### `match_workpieces`

```python
def match_workpieces(workpieces: list[Any], new_contours: list[np.ndarray], strategy: MatchingStrategy) -> Tuple[list[MatchInfo], list[Contour], list[Contour]]
```

Generic matching loop — strategy-agnostic. Returns (matched MatchInfos, unmatched Contours, matched Contours).

## `example_usage.py`

Source: [src/engine/vision/implementation/VisionSystem/features/contour_matching/example_usage.py](../../../../../../../src/engine/vision/implementation/VisionSystem/features/contour_matching/example_usage.py).

Standalone runner for the contour_matching package. Demonstrates the three layers of the pipeline: 1. Geometric matching — find the best workpiece for each detected contour 2. Difference calculator — compute centroid and rotation offsets 3. Full pipeline — findMatchingWorkpieces (match + prepare + align) No robot, no Qt, no platform required.

Imports (including optional/function-local imports; not a startup dependency list): `copy`, `numpy`, `pathlib`, `src.engine.vision.implementation.VisionSystem.core.models.contour`, `src.engine.vision.implementation.VisionSystem.features.contour_matching.alignment.difference_calculator`, `src.engine.vision.implementation.VisionSystem.features.contour_matching.contour_matcher`, `src.engine.vision.implementation.VisionSystem.features.contour_matching.matching.best_match_result`, `src.engine.vision.implementation.VisionSystem.features.contour_matching.matching.match_info`, `src.engine.vision.implementation.VisionSystem.features.contour_matching.matching.strategies.geometric_matching_strategy`, `sys`.

### `_StubWorkpiece`

```python
class _StubWorkpiece:
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, contour: np.ndarray, workpiece_id: int, name: str)
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

### `_make_circle`

```python
def _make_circle(cx=128.0, cy=128.0, r=60.0, n=64) -> np.ndarray
```

### `_make_rect`

```python
def _make_rect(cx=128.0, cy=128.0, w=100.0, h=70.0) -> np.ndarray
```

### `_make_triangle`

```python
def _make_triangle(cx=128.0, cy=128.0, r=70.0) -> np.ndarray
```

### `_perturb`

```python
def _perturb(contour: np.ndarray, tx=5.0, ty=3.0, angle_deg=8.0) -> np.ndarray
```

Apply rotation and translation to simulate a camera detection offset.

### `_demo_matching`

```python
def _demo_matching(workpieces: list, strategy: GeometricMatchingStrategy) -> list[MatchInfo]
```

### `_demo_difference_calculator`

```python
def _demo_difference_calculator() -> None
```

### `_demo_full_pipeline`

```python
def _demo_full_pipeline(workpieces: list, debug: bool=False) -> None
```

Exercises findMatchingWorkpieces — the top-level entry point. Pipeline inside that function: match_workpieces → BestMatchResult per detected contour prepare_data_for_alignment → attaches contourObj / sprayContourObjs / sprayFillObjs _alignContours → applies rotation + translation (+ optional mask refinement) and calls update_workpiece_data on each matched workpiece Pass debug=True to save similarity and alignment plots to contour_matching/debug/output/ for every comparison.

### `run`

```python
def run() -> None
```

## `matching_config.py`

Source: [src/engine/vision/implementation/VisionSystem/features/contour_matching/matching_config.py](../../../../../../../src/engine/vision/implementation/VisionSystem/features/contour_matching/matching_config.py).

Imports (including optional/function-local imports; not a startup dependency list): `pathlib`, `src.engine.vision.implementation.VisionSystem.features.contour_matching.settings.contour_matching_settings`.

### `configure`

```python
def configure(settings_file_path: Path) -> None
```

Override the settings storage path — call once before first use (e.g. for per-vision_service storage).

### `get_settings`

```python
def get_settings() -> ContourMatchingSettings
```

### `reload_settings`

```python
def reload_settings() -> None
```

## `utils.py`

Source: [src/engine/vision/implementation/VisionSystem/features/contour_matching/utils.py](../../../../../../../src/engine/vision/implementation/VisionSystem/features/contour_matching/utils.py).

Imports (including optional/function-local imports; not a startup dependency list): `cv2`, `numpy`.

### `standardize_contour`

```python
def standardize_contour(contour, dtype=np.float32)
```

Converts any OpenCV contour or list of points to a (N, 2) NumPy array. Handles shapes like (N, 1, 2), (N, 2), or nested Python lists.

### `to_cv_contour`

```python
def to_cv_contour(contour)
```

### `to_cv_contour_f32`

```python
def to_cv_contour_f32(contour)
```

### `standardize_point`

```python
def standardize_point(point, dtype=np.float32)
```

Standardize a single point or list of points into (2,) or (N, 2).

### `is_contour_inside_polygon`

```python
def is_contour_inside_polygon(contour, top_left, top_right, bottom_right, bottom_left)
```

Fixed version using a different approach - checking if contour bounding rect is inside polygon

### `flatten_and_convert_to_list`

```python
def flatten_and_convert_to_list(contour_array)
```

Ensure contour array is Nx2 list of floats.

### `close_contours_if_open`

```python
def close_contours_if_open(contours)
```

### `calculate_mask_overlap`

```python
def calculate_mask_overlap(contour1, contour2, canvas_size=None)
```

### `convexity_ratio`

```python
def convexity_ratio(contour)
```

Compute how concave a shape is (area vs convex hull area).
