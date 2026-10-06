# Module reference: `src/engine/robot/path_interpolation/deprecated`

[Package guide](README.md) · [Complete source index](../../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [combined_interpolation.py](#combined_interpolationpy)
- [linear_interpolation.py](#linear_interpolationpy)
- [points_interpolation_example.py](#points_interpolation_examplepy)
- [simple_interpolation_viewer.py](#simple_interpolation_viewerpy)
- [spline_interpolation.py](#spline_interpolationpy)
- [test_trajectory_interpolation.py](#test_trajectory_interpolationpy)
- [ttest_trajectory_interpolation.py](#ttest_trajectory_interpolationpy)

## `__init__.py`

Source: [src/engine/robot/path_interpolation/deprecated/__init__.py](../../../../../src/engine/robot/path_interpolation/deprecated/__init__.py).

Legacy interpolation modules kept only for reference/debugging.

No top-level functions, classes or public value declarations; inspect the source for imports or entry-point statements.

## `combined_interpolation.py`

Source: [src/engine/robot/path_interpolation/deprecated/combined_interpolation.py](../../../../../src/engine/robot/path_interpolation/deprecated/combined_interpolation.py).

Imports (including optional/function-local imports; not a startup dependency list): `numpy`, `src.engine.robot.path_interpolation.deprecated.spline_interpolation`, `warnings`.

### `_cumulative_arc_length_mm`

```python
def _cumulative_arc_length_mm(path: list[list[float]]) -> np.ndarray
```

### `_local_cubic_fit_value`

```python
def _local_cubic_fit_value(samples_s: np.ndarray, samples_v: np.ndarray, eval_s: float) -> float
```

### `_point_line_distance_mm`

```python
def _point_line_distance_mm(point_xyz: np.ndarray, start_xyz: np.ndarray, end_xyz: np.ndarray) -> float
```

### `simplify_path_for_interpolation`

```python
def simplify_path_for_interpolation(path: list[list[float]], min_point_spacing_mm: float=0.5, collinear_angle_deg: float=3.0, max_shortcut_deviation_mm: float=0.5) -> list[list[float]]
```

Remove near-duplicate and nearly collinear jitter points while preserving shape.

### `pre_smooth_path_for_interpolation`

```python
def pre_smooth_path_for_interpolation(path: list[list[float]], window_size: int=5, passes: int=1, preserve_corner_angle_deg: float=35.0, max_deviation_mm: float=1.0) -> list[list[float]]
```

Locally smooth noisy robot-space paths with cubic fitting and deviation clamping. The fitter works over arc length in robot space, preserves endpoints and protected corners, and clamps each adjusted sample to a hard geometric deviation bound in mm so the smoothed path cannot drift off the source geometry.

### `_compute_normalized_arc_length`

```python
def _compute_normalized_arc_length(path: list[list[float]]) -> tuple[np.ndarray, float]
```

### `_compute_turn_angles_deg`

```python
def _compute_turn_angles_deg(path: list[list[float]]) -> np.ndarray
```

### `_build_corner_intervals`

```python
def _build_corner_intervals(path: list[list[float]], target_spacing_mm: float, corner_angle_threshold_deg: float, corner_window_spacing_multiplier: float) -> list[tuple[float, float]]
```

### `_is_in_intervals`

```python
def _is_in_intervals(t_value: float, intervals: list[tuple[float, float]]) -> bool
```

### `_normalize`

```python
def _normalize(vec: np.ndarray) -> np.ndarray
```

### `_rodrigues_rotate`

```python
def _rodrigues_rotate(vec: np.ndarray, axis: np.ndarray, angle_rad: float) -> np.ndarray
```

### `_interp_full_point`

```python
def _interp_full_point(start: np.ndarray, end: np.ndarray, ratio: float) -> list[float]
```

### `_resample_polyline_uniformly`

```python
def _resample_polyline_uniformly(path: list[list[float]], target_spacing_mm: float) -> list[list[float]]
```

Resample a polyline at roughly uniform arc-length spacing.

### `_resample_polyline_with_intervals`

```python
def _resample_polyline_with_intervals(path: list[list[float]], target_spacing_mm: float, dense_intervals: list[tuple[float, float]], dense_spacing_scale: float=0.65) -> list[list[float]]
```

Resample with modestly tighter spacing around corners and normal spacing on straights.

### `_inject_corner_support_points`

```python
def _inject_corner_support_points(path: list[list[float]], target_spacing_mm: float, corner_angle_threshold_deg: float=25.0) -> list[list[float]]
```

Add a few local support points near sharp corners without densifying straights.

### `blend_corners_with_radius`

```python
def blend_corners_with_radius(path: list[list[float]], blend_radius_mm: float, target_spacing_mm: float, corner_angle_threshold_deg: float=35.0) -> list[list[float]]
```

Replace sharp corners with local circular blends in robot space.

### `_blend_corner_only_path`

```python
def _blend_corner_only_path(original_path: list[list[float]], dense_linear: list[list[float]], smoothed: list[list[float]], target_spacing_mm: float, corner_angle_threshold_deg: float=35.0, corner_window_spacing_multiplier: float=3.0) -> list[list[float]]
```

### `_stage_linear_densification`

```python
def _stage_linear_densification(path: list[list[float]], adaptive_spacing_mm: float, debug: bool) -> list[list[float]]
```

Stage 1: Densify the path by inserting linearly interpolated points. Adds a light amount of intermediate support points for debug/preview. The final execution path is produced later and should not depend on this stage being extremely dense. Args: path: Original sparse path (list of [x, y, z, rx_degrees, ry_degrees, rz_degrees] points). adaptive_spacing_mm: Target distance between consecutive points in mm. debug: If True, print progress information. Returns: Densified path with more points at approximately *adaptive_spacing_mm* apart.

### `_stage_spline_smoothing`

```python
def _stage_spline_smoothing(dense_path: list[list[float]], original_path: list[list[float]], adaptive_spacing_mm: float, spline_density_multiplier: float, smoothing_lambda: float, debug: bool, blend_radius_mm: float | None=None, pre_smooth_max_deviation_mm: float=1.0) -> list[list[float]]
```

Stage 2: Apply local corner blending in robot space.

### `interpolate_path_two_stage`

```python
def interpolate_path_two_stage(path: list[list[float]], adaptive_spacing_mm: float, spline_density_multiplier: float=2.0, smoothing_lambda: float=0.0, debug: bool=False, return_pre_smoothed: bool=False, blend_radius_mm: float | None=None, pre_smooth_max_deviation_mm: float=1.0)
```

Two-stage path interpolation: linear densification then spline smoothing. Stage 1 inserts linearly spaced points so that the original coarse path has enough density for a reliable spline fit. Stage 2 fits a cubic spline and re-samples at an even finer spacing to produce a smooth trajectory. Args: path: Input path as a list of N points, each point is a list of floats (e.g. [x, y, z, rx_degrees, ry_degrees, rz_degrees]). adaptive_spacing_mm: Target distance between consecutive points in mm for the linear densification stage. spline_density_multiplier: Controls how much denser the spline output is relative to the linear stage. Output spacing = ``adaptive_spacing_mm / spline_density_multiplier``. smoothing_lambda: Smoothing factor for the spline stage. 0.0 = exact interpolation; larger values produce smoother curves that may deviate from the input points. debug: If True, print progress information for both stages. Returns: A tuple of (dense_linear, smoothed) where: - dense_linear: Path after stage 1 (linear densification only). - smoothed: Path after stage 2 (spline smoothing).

## `linear_interpolation.py`

Source: [src/engine/robot/path_interpolation/deprecated/linear_interpolation.py](../../../../../src/engine/robot/path_interpolation/deprecated/linear_interpolation.py).

Imports (including optional/function-local imports; not a startup dependency list): `numpy`, `numpy.typing`.

### `_lerp_points`

```python
def _lerp_points(start: npt.NDArray, end: npt.NDArray, num_points: int) -> list[list[float]]
```

Generate *num_points* evenly spaced points between start and end (exclusive of both).

### `_interpolate_segment_adaptive`

```python
def _interpolate_segment_adaptive(start: npt.NDArray, end: npt.NDArray, target_spacing_mm: float) -> tuple[list[list[float]], bool]
```

Interpolate a single segment using adaptive spacing. Returns (intermediate_points, was_interpolated). If the segment is too short (< 2x target spacing), no points are added.

### `_log_debug`

```python
def _log_debug(path_len: int, result_len: int, target_spacing_mm: float, segments_interpolated: int, segments_skipped: int) -> None
```

Print interpolation summary when debug is enabled.

### `interpolate_path_linear`

```python
def interpolate_path_linear(path: list[list[float]], target_spacing_mm: float, debug: bool=False) -> list[list[float]]
```

## `points_interpolation_example.py`

Source: [src/engine/robot/path_interpolation/deprecated/points_interpolation_example.py](../../../../../src/engine/robot/path_interpolation/deprecated/points_interpolation_example.py).

Example usage of the deprecated two-stage interpolation pipeline. Demonstrates the deprecated two-stage interpolation pipeline (linear densification -> spline smoothing) on different geometric shapes. Run directly to generate debug plots for each shape. Usage: python src/engine/robot/path_interpolation/deprecated/points_interpolation_example.py [shape] Shapes: rectangle, circle, triangle, l_shape, star, all (default: all)

Imports (including optional/function-local imports; not a startup dependency list): `math`, `numpy`, `os`, `src.engine.robot.path_interpolation.deprecated`, `src.engine.robot.path_interpolation.new_interpolation.debug_plotting`, `sys`.

Module declarations (expressions are shown without evaluating them):

```python
Z_HEIGHT = -150.0
ORIENTATION = [0.0, 0.0, 0.0]
SHAPES = {'rectangle': {'fn': make_rectangle, 'desc': '200x100 mm closed rectangle'}, 'circle': {'fn': make_circle, 'desc': 'R=80 mm circle (12 vertices)'}, 'triangle': {'fn': make_triangle, 'desc': 'Equilateral triangle (side=150 mm)'}, 'l_shape': {'fn': make_l_shape, 'desc': 'L-shaped path with right-angle corner'}, 'star': {'fn': make_star, 'desc': '5-pointed star (outer=100, inner=45 mm)'}}
```

### `_pt`

```python
def _pt(x, y, z=Z_HEIGHT)
```

Helper: build a 6-DOF point.

### `make_rectangle`

```python
def make_rectangle(width=200, height=100, origin=(0, 0))
```

Closed rectangular path – 5 points (4 corners + close).

### `make_circle`

```python
def make_circle(radius=80, n_points=12, center=(0, 0))
```

Closed circular path sampled at *n_points* vertices.

### `make_triangle`

```python
def make_triangle(side=150, origin=(0, 0))
```

Equilateral triangle – 4 points (3 vertices + close).

### `make_l_shape`

```python
def make_l_shape(long=200, short=100, width=40, origin=(0, 0))
```

L-shaped path (open) with a right-angle corner.

### `make_star`

```python
def make_star(outer_r=100, inner_r=45, n_tips=5, center=(0, 0))
```

Star shape with alternating outer/inner vertices.

### `run_example`

```python
def run_example(shape_name, adaptive_spacing_mm=2.0, smoothing_lambda=10.0)
```

Interpolate a shape and save a debug plot.

### `main`

```python
def main()
```

## `simple_interpolation_viewer.py`

Source: [src/engine/robot/path_interpolation/deprecated/simple_interpolation_viewer.py](../../../../../src/engine/robot/path_interpolation/deprecated/simple_interpolation_viewer.py).

Imports (including optional/function-local imports; not a startup dependency list): `argparse`, `math`, `matplotlib`, `matplotlib.pyplot`, `numpy`, `scipy.interpolate`, `typing`.

### `cumulative_arc_length`

```python
def cumulative_arc_length(points: np.ndarray) -> np.ndarray
```

### `resample_linear`

```python
def resample_linear(points: np.ndarray, spacing: float) -> np.ndarray
```

### `resample_spline`

```python
def resample_spline(points: np.ndarray, spacing: float, smoothing: float, degree: int=3) -> np.ndarray
```

### `plot_paths`

```python
def plot_paths(original: np.ndarray, interpolated: np.ndarray, out_path: str, title: str) -> None
```

### `make_rectangle`

```python
def make_rectangle() -> np.ndarray
```

### `make_triangle`

```python
def make_triangle() -> np.ndarray
```

### `make_circle`

```python
def make_circle(n: int=12, r: float=80) -> np.ndarray
```

### `make_custom`

```python
def make_custom() -> np.ndarray
```

### `parse_points`

```python
def parse_points(text: str) -> np.ndarray
```

### `get_points`

```python
def get_points(shape: str, points_text: str | None) -> np.ndarray
```

### `main`

```python
def main() -> None
```

## `spline_interpolation.py`

Source: [src/engine/robot/path_interpolation/deprecated/spline_interpolation.py](../../../../../src/engine/robot/path_interpolation/deprecated/spline_interpolation.py).

Imports (including optional/function-local imports; not a startup dependency list): `numpy`, `numpy.typing`, `scipy.interpolate`.

### `_compute_arc_length_parameterization`

```python
def _compute_arc_length_parameterization(path_array: npt.NDArray) -> tuple[npt.NDArray, float]
```

Compute a normalized arc-length parameter for each point in the path. Arc-length parameterization maps each point to a value in [0, 1] based on its cumulative distance along the path (using only x, y, z coordinates). This avoids distortions that occur when parameterizing by point index, especially when segments have very different lengths. Args: path_array: Array of shape (N, D) where the first 3 columns are x, y, z. Returns: t: Normalized parameter array of shape (N,) with values in [0, 1]. total_length: Total arc length of the path in mm.

### `_compute_sample_count`

```python
def _compute_sample_count(n_original: int, total_length: float, target_spacing_mm: float) -> int
```

Decide how many output points the spline should be sampled at. Uses whichever is larger: - twice the original point count (guarantees the spline is at least as dense as the input), or - the number of evenly spaced samples needed to achieve *target_spacing_mm* along the path. Args: n_original: Number of points in the input path. total_length: Total arc length of the path in mm. target_spacing_mm: Desired spacing between output points in mm. Returns: The number of sample points for the output spline.

### `_compute_vertex_turn_weights`

```python
def _compute_vertex_turn_weights(path_array: npt.NDArray) -> npt.NDArray
```

Return a curvature-like weight in [0, 1] for each path vertex. Weight is derived from the turning angle between consecutive XYZ segments. Straight runs approach 0, sharp bends approach 1.

### `_build_adaptive_t_samples`

```python
def _build_adaptive_t_samples(t: npt.NDArray, path_array: npt.NDArray, target_spacing_mm: float, curvature_gain: float) -> npt.NDArray
```

Sample more densely near turns while preserving base spacing on straights.

### `_fit_spline_dimension`

```python
def _fit_spline_dimension(t: npt.NDArray, values: npt.NDArray, t_new: npt.NDArray, k: int, smoothing_lambda: float, dim_index: int) -> npt.NDArray
```

Fit a univariate spline to one dimension and evaluate at new parameters. If the spline fit fails (e.g., due to numerical issues), falls back to simple linear interpolation so the pipeline never crashes. Args: t: Normalized arc-length parameters for the input points, shape (N,). values: Coordinate values for this dimension, shape (N,). t_new: Parameters at which to evaluate the spline, shape (M,). k: Degree of the spline (1=linear, 2=quadratic, 3=cubic). smoothing_lambda: Smoothing factor passed to ``UnivariateSpline(s=...)``. 0.0 means exact interpolation (passes through every point); larger values allow the spline to deviate for a smoother result. dim_index: Index of the dimension (used only for the warning message). Returns: Interpolated values at *t_new*, shape (M,).

### `interpolate_path_spline_with_lambda`

```python
def interpolate_path_spline_with_lambda(path: list[list[float]], target_spacing_mm: float=5.0, k: int=3, smoothing_lambda: float=0.0, curvature_gain: float=3.0) -> list[list[float]]
```

Smooth a path using univariate splines with arc-length parameterization. Each coordinate dimension (x, y, z, rx_degrees, ry_degrees, rz_degrees, ...) is fitted with an independent ``UnivariateSpline``. The spline is then sampled at evenly spaced arc-length intervals to produce the output path. Args: path: Input path as a list of N points, each point is a list of floats (e.g. [x, y, z, rx_degrees, ry_degrees, rz_degrees]). target_spacing_mm: Desired distance between consecutive output points in mm. Smaller values produce denser output. k: Degree of the spline curve (1=linear, 2=quadratic, 3=cubic). Must satisfy ``len(path) >= k + 1``. smoothing_lambda: Smoothing factor for ``UnivariateSpline(s=...)``. 0.0 = exact interpolation (a curve passes through every input point). Increasing this allows the curve to deviate from the input points for a smoother result. curvature_gain: Extra sampling density multiplier applied near turns. 0.0 disables adaptive density and falls back to uniform arc-length sampling. Returns: Smoothed path as a list of M points with the same dimensionality as the input.

## `test_trajectory_interpolation.py`

Source: [src/engine/robot/path_interpolation/deprecated/test_trajectory_interpolation.py](../../../../../src/engine/robot/path_interpolation/deprecated/test_trajectory_interpolation.py).

Imports (including optional/function-local imports; not a startup dependency list): `json`, `os`, `src.engine.robot.path_interpolation.deprecated.combined_interpolation`, `src.engine.robot.path_interpolation.new_interpolation.debug_plotting`, `sys`.

### `load_trajectory_from_json`

```python
def load_trajectory_from_json(json_path)
```

### `main`

```python
def main()
```

## `ttest_trajectory_interpolation.py`

Source: [src/engine/robot/path_interpolation/deprecated/ttest_trajectory_interpolation.py](../../../../../src/engine/robot/path_interpolation/deprecated/ttest_trajectory_interpolation.py).

Imports (including optional/function-local imports; not a startup dependency list): `json`, `os`, `src.engine.robot.path_interpolation.deprecated.combined_interpolation`, `src.engine.robot.path_interpolation.new_interpolation.debug_plotting`, `sys`.

### `load_trajectory_from_json`

```python
def load_trajectory_from_json(json_path)
```

### `main`

```python
def main()
```
