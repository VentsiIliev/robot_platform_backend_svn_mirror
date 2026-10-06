# Module reference: `src/robot_systems/paint/processes/paint/align/alignment`

[Package guide](README.md) · [Complete source index](../../../../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [io.py](#iopy)
- [sampling.py](#samplingpy)

## `__init__.py`

Source: [src/robot_systems/paint/processes/paint/align/alignment/__init__.py](../../../../../../../src/robot_systems/paint/processes/paint/align/alignment/__init__.py).

Imports (including optional/function-local imports; not a startup dependency list): `.io`, `.sampling`.

Package-level import/export surface:

```python
from .io import _extract_raw_contour_points, _main_contour_payload, _normalize_contour_points, _raw_contour_payload_points, _replace_raw_contour_payload, _resample_raw_contour_payload
from .sampling import _describe_contour, _laplacian_smooth_closed_path, _path_length, _polygon_area, _resample_closed_path
```

No top-level functions, classes or public value declarations; inspect the source for imports or entry-point statements.

## `io.py`

Source: [src/robot_systems/paint/processes/paint/align/alignment/io.py](../../../../../../../src/robot_systems/paint/processes/paint/align/alignment/io.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `numpy`, `src.robot_systems.paint.processes.paint.align.alignment.sampling`.

### `_main_contour_payload`

```python
def _main_contour_payload(raw: dict)
```

Return the raw main contour list, unwrapping compatibility wrapper payloads.

### `_extract_raw_contour_points`

```python
def _extract_raw_contour_points(raw: dict) -> np.ndarray
```

Extract the main raw workpiece contour as an Nx2 numpy array.

### `_normalize_contour_points`

```python
def _normalize_contour_points(contour) -> np.ndarray
```

Normalize OpenCV-style contour arrays into a simple Nx2 float array.

### `_resample_raw_contour_payload`

```python
def _resample_raw_contour_payload(contour_array, count: int) -> np.ndarray
```

Convert a raw contour payload into a resampled Nx2 contour for smoothing.

### `_raw_contour_payload_points`

```python
def _raw_contour_payload_points(contour_array) -> np.ndarray
```

Convert a raw contour payload into an Nx2 contour without changing ordering.

### `_replace_raw_contour_payload`

```python
def _replace_raw_contour_payload(contour_array, points: np.ndarray) -> None
```

Rewrite a raw contour payload from an Nx2 point array.

## `sampling.py`

Source: [src/robot_systems/paint/processes/paint/align/alignment/sampling.py](../../../../../../../src/robot_systems/paint/processes/paint/align/alignment/sampling.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `numpy`.

### `_resample_closed_path`

```python
def _resample_closed_path(points: np.ndarray, count: int) -> np.ndarray
```

Resample a closed contour to a fixed number of evenly spaced points.

### `_polygon_area`

```python
def _polygon_area(points: np.ndarray) -> float
```

Return absolute polygon area for a closed contour sample.

### `_path_length`

```python
def _path_length(points: np.ndarray) -> float
```

Return perimeter/closed path length for a contour sample.

### `_describe_contour`

```python
def _describe_contour(points: np.ndarray) -> str
```

Return a compact contour summary for diagnostics.

### `_laplacian_smooth_closed_path`

```python
def _laplacian_smooth_closed_path(points: np.ndarray, iterations: int=2, alpha: float=0.2) -> np.ndarray
```

Apply light closed-path Laplacian smoothing without collapsing the contour.
