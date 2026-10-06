# Module reference: `src/engine/vision/implementation/VisionSystem/features/contour_matching/alignment`

[Package guide](README.md) · [Complete source index](../../../../../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [alignment_utils.py](#alignment_utilspy)
- [contour_aligner.py](#contour_alignerpy)
- [difference_calculator.py](#difference_calculatorpy)
- [mask_refinement.py](#mask_refinementpy)
- [workpiece_update.py](#workpiece_updatepy)

## `__init__.py`

Source: [src/engine/vision/implementation/VisionSystem/features/contour_matching/alignment/__init__.py](../../../../../../../../src/engine/vision/implementation/VisionSystem/features/contour_matching/alignment/__init__.py).

No top-level functions, classes or public value declarations; inspect the source for imports or entry-point statements.

## `alignment_utils.py`

Source: [src/engine/vision/implementation/VisionSystem/features/contour_matching/alignment/alignment_utils.py](../../../../../../../../src/engine/vision/implementation/VisionSystem/features/contour_matching/alignment/alignment_utils.py).

Imports (including optional/function-local imports; not a startup dependency list): `numpy`, `src.engine.vision.implementation.VisionSystem.core.models.contour`.

### `transform_pickup_point`

```python
def transform_pickup_point(workpiece, rotationDiff, centroidDiff, centroid)
```

## `contour_aligner.py`

Source: [src/engine/vision/implementation/VisionSystem/features/contour_matching/alignment/contour_aligner.py](../../../../../../../../src/engine/vision/implementation/VisionSystem/features/contour_matching/alignment/contour_aligner.py).

Imports (including optional/function-local imports; not a startup dependency list): `copy`, `logging`, `numpy`, `src.engine.vision.implementation.VisionSystem.core.models.contour`, `src.engine.vision.implementation.VisionSystem.features.contour_matching.alignment.mask_refinement`, `src.engine.vision.implementation.VisionSystem.features.contour_matching.alignment.workpiece_update`, `src.engine.vision.implementation.VisionSystem.features.contour_matching.debug.plot_generator`, `src.engine.vision.implementation.VisionSystem.features.contour_matching.matching.match_info`, `src.engine.vision.implementation.VisionSystem.features.contour_matching.matching_config`, `typing`.

### `get_contour_objects`

```python
def get_contour_objects(entries: list) -> list[Contour]
```

Convert a list of spray-pattern entry dicts to Contour objects.

### `get_pickup_object`

```python
def get_pickup_object(workpiece) -> Optional[Contour]
```

### `prepare_data_for_alignment`

```python
def prepare_data_for_alignment(matched: list[MatchInfo]) -> list[MatchInfo]
```

Attach contourObj / sprayContourObjs / sprayFillObjs to each MatchInfo so that _alignContours can operate on Contour objects instead of raw arrays. Deepcopies the workpiece to avoid mutating the original.

### `apply_rotation`

```python
def apply_rotation(contours, angle, pivot)
```

### `apply_translation`

```python
def apply_translation(contours, dx, dy)
```

### `align_single_contour`

```python
def align_single_contour(target: Contour, reference: np.ndarray, spray_contours: Optional[List[Contour]], spray_fills: Optional[List[Contour]], rotation_diff: float, translation_diff: Tuple[float, float], refine: bool, pickup_point: Optional[Contour]=None) -> None
```

Align a single target contour to a reference contour, optionally applying the same transformation to associated spray contours/fills and performing mask-based refinement. Works in-place. Args: target (Contour): Contour to align. reference (np.ndarray): Reference contour. spray_contours (Optional[List[Contour]]): Spray contours associated with the target. spray_fills (Optional[List[Contour]]): Spray fills associated with the target. rotation_diff (float): Initial rotation difference in degrees. translation_diff (Tuple[float, float]): Initial translation difference (dx, dy). refine (bool): Whether to perform mask-based refinement.

### `align_contours_generic`

```python
def align_contours_generic(target_contours: List[Contour], reference_contours: List[np.ndarray], spray_contours_list: List[List[Contour]], spray_fills_list: List[List[Contour]], rotation_diffs: List[float], translation_diffs: List[Tuple[float, float]], refine: bool, pickup_points_list: Optional[List[Optional[Contour]]]=None) -> None
```

Align multiple target contours to corresponding reference contours using `align_single_contour`.

### `_alignContours`

```python
def _alignContours(matched: List[MatchInfo], debug: bool=False) -> Dict[str, List[Any]]
```

Align matched contours to the workpieces using the workpiece-agnostic batch function. Args: matched (List[MatchInfo]): List of matched workpieces with contour info. debug (bool): Whether to generate debug plots. Returns: Dict[str, List[Any]]: Aligned workpieces, orientations, ML confidences, ML results.

## `difference_calculator.py`

Source: [src/engine/vision/implementation/VisionSystem/features/contour_matching/alignment/difference_calculator.py](../../../../../../../../src/engine/vision/implementation/VisionSystem/features/contour_matching/alignment/difference_calculator.py).

Imports (including optional/function-local imports; not a startup dependency list): `logging`, `numpy`, `pathlib`, `src.engine.vision.implementation.VisionSystem.core.models.contour`, `src.engine.vision.implementation.VisionSystem.features.contour_matching.debug.plot_generator`.

### `_calculateDifferences`

```python
def _calculateDifferences(workpieceContour: Contour, contour: Contour, debug: bool=False)
```

Calculate the centroid and rotation differences between two contours. Args: workpieceContour (Contour): Contour object representing the workpiece contour. contour (Contour): Contour object representing the new contour. debug (bool): Whether to generate debug plots. Returns: tuple: (centroidDiff, rotationDiff, contourAngle)

### `_ensure_closed`

```python
def _ensure_closed(contour: Contour) -> Contour
```

Ensure the contour is closed (first point = last point).

### `_debug_contours`

```python
def _debug_contours(workpieceContour, contour, wpAngle, contourAngle, rotationDiff, workpieceCentroid, contourCentroid, centroidDiff)
```

Handle debug output for contour differences.

## `mask_refinement.py`

Source: [src/engine/vision/implementation/VisionSystem/features/contour_matching/alignment/mask_refinement.py](../../../../../../../../src/engine/vision/implementation/VisionSystem/features/contour_matching/alignment/mask_refinement.py).

Imports (including optional/function-local imports; not a startup dependency list): `src.engine.vision.implementation.VisionSystem.core.models.contour`, `src.engine.vision.implementation.VisionSystem.features.contour_matching.utils`.

### `_refine_alignment_with_mask`

```python
def _refine_alignment_with_mask(workpiece_contour, target_contour)
```

Refine the alignment of a contour by rotating it to maximize mask overlap with a target contour. Performs three stages: coarse search, adaptive local refinement, and fine-tuning. Args: workpiece_contour (np.ndarray or Contour): The contour to rotate and align. target_contour (np.ndarray or Contour): The reference contour to align to. Returns: tuple: (best_rotation_angle, best_overlap_score) - best_rotation_angle (float): Optimal rotation angle in degrees [-180, 180]. - best_overlap_score (float): Maximum mask overlap achieved.

### `_coarse_search`

```python
def _coarse_search(workpiece_contour, target_contour, centroid, best_rotation, best_overlap)
```

Search every 10° so narrow peaks, including 180°, are always tested. Args: workpiece_contour (np.ndarray or Contour): Contour to rotate. target_contour (np.ndarray or Contour): Reference contour for overlap calculation. centroid (tuple): Pivot point for rotation. best_rotation (float): Current best rotation angle. best_overlap (float): Current best overlap score. Returns: tuple: Updated (best_rotation, best_overlap) after coarse search.

### `_local_refinement`

```python
def _local_refinement(workpiece_contour, target_contour, centroid, best_rotation, best_overlap)
```

Refine rotation in a local neighborhood around the coarse alignment to improve mask overlap. Uses adaptive step size and stops when no improvement is seen after several iterations. Args: workpiece_contour (np.ndarray or Contour): Contour to rotate. target_contour (np.ndarray or Contour): Reference contour. centroid (tuple): Pivot for rotation. best_rotation (float): Starting rotation angle. best_overlap (float): Starting overlap score. Returns: tuple: Updated (best_rotation, best_overlap) after local refinement.

### `_fine_tune`

```python
def _fine_tune(workpiece_contour, target_contour, centroid, best_rotation, best_overlap)
```

Perform very fine rotational adjustments (±2° in 0.5° steps) around the current best rotation to maximize mask overlap. Args: workpiece_contour (np.ndarray or Contour): Contour to rotate. target_contour (np.ndarray or Contour): Reference contour. centroid (tuple): Pivot point for rotation. best_rotation (float): Starting rotation angle. best_overlap (float): Starting overlap score. Returns: tuple: Updated (best_rotation, best_overlap) after fine-tuning.

### `_rotate_contour`

```python
def _rotate_contour(contour, angle, centroid)
```

Rotate a contour (np.ndarray or Contour) around a pivot point (centroid). Args: contour (np.ndarray or Contour): Contour to rotate. angle (float): Rotation angle in degrees. centroid (tuple): Pivot point for rotation. Returns: np.ndarray: Rotated contour points.

## `workpiece_update.py`

Source: [src/engine/vision/implementation/VisionSystem/features/contour_matching/alignment/workpiece_update.py](../../../../../../../../src/engine/vision/implementation/VisionSystem/features/contour_matching/alignment/workpiece_update.py).

Imports (including optional/function-local imports; not a startup dependency list): `logging`.

### `update_workpiece_data`

```python
def update_workpiece_data(workpiece, contourObj, sprayContourObjs, sprayFillObjs, pickup_point)
```
