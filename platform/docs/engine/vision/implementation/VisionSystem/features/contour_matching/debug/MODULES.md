# Module reference: `src/engine/vision/implementation/VisionSystem/features/contour_matching/debug`

[Package guide](README.md) · [Complete source index](../../../../../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [plot_generator.py](#plot_generatorpy)

## `__init__.py`

Source: [src/engine/vision/implementation/VisionSystem/features/contour_matching/debug/__init__.py](../../../../../../../../src/engine/vision/implementation/VisionSystem/features/contour_matching/debug/__init__.py).

No top-level functions, classes or public value declarations; inspect the source for imports or entry-point statements.

## `plot_generator.py`

Source: [src/engine/vision/implementation/VisionSystem/features/contour_matching/debug/plot_generator.py](../../../../../../../../src/engine/vision/implementation/VisionSystem/features/contour_matching/debug/plot_generator.py).

Imports (including optional/function-local imports; not a startup dependency list): `datetime`, `matplotlib.pyplot`, `numpy`, `pathlib`, `typing`.

### `_ensure_debug_dir`

```python
def _ensure_debug_dir() -> Path
```

### `_to_2d`

```python
def _to_2d(contour) -> np.ndarray
```

### `_create_debug_plot`

```python
def _create_debug_plot(contour1, contour2, metrics: dict) -> None
```

### `get_similarity_debug_plot`

```python
def get_similarity_debug_plot(workpiece_contour, contour, workpiece_centroid: Tuple, contour_centroid: Tuple, wp_angle: float, contour_angle: float, centroid_diff: np.ndarray, rotation_diff: float) -> None
```

### `plot_contour_alignment`

```python
def plot_contour_alignment(original_target: np.ndarray, reference: np.ndarray, centroid: Tuple, original_sprays: List[np.ndarray], workpiece: Any, rotated: np.ndarray, final: np.ndarray, rotation_diff: float, translation_diff, contour_orientation: Optional[float], spray_contour_objs: Optional[list], spray_fill_objs: Optional[list], index: int) -> None
```
