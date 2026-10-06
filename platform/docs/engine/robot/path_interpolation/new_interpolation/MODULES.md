# Module reference: `src/engine/robot/path_interpolation/new_interpolation`

[Package guide](README.md) · [Complete source index](../../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [debug_plotting.py](#debug_plottingpy)
- [interpolation_pipeline.py](#interpolation_pipelinepy)
- [simple_interpolation_pyqt6.py](#simple_interpolation_pyqt6py)

## `__init__.py`

Source: [src/engine/robot/path_interpolation/new_interpolation/__init__.py](../../../../../src/engine/robot/path_interpolation/new_interpolation/__init__.py).

No top-level functions, classes or public value declarations; inspect the source for imports or entry-point statements.

## `debug_plotting.py`

Source: [src/engine/robot/path_interpolation/new_interpolation/debug_plotting.py](../../../../../src/engine/robot/path_interpolation/new_interpolation/debug_plotting.py).

Imports (including optional/function-local imports; not a startup dependency list): `cv2`, `datetime`, `json`, `matplotlib`, `numpy`, `os`, `traceback`.

### `plot_pixel_to_mm_debug`

```python
def plot_pixel_to_mm_debug(raw_paths, raw_pixel_paths=None, homography_paths=None, min_rects_mm=None, measurement_text=None, save_dir='debug_plots')
```

Plot robot-mm paths immediately after pixel-to-mm conversion.

### `plot_pixel_to_mm_strategy_comparison`

```python
def plot_pixel_to_mm_strategy_comparison(raw_pixel_path, strategy_paths, *, min_rects_mm=None, save_dir='debug_plots')
```

Plot side-by-side pixel-to-mm strategy results with min-rect dimensions.

### `_draw_min_rect_overlay`

```python
def _draw_min_rect_overlay(ax, rect_info, index: int) -> None
```

### `_execution_rotation_change_mask`

```python
def _execution_rotation_change_mask(execution_arr: np.ndarray, threshold_deg: float=_EXECUTION_HEADING_MARKER_THRESHOLD_DEG) -> np.ndarray
```

### `write_path_shape_comparison_debug`

```python
def write_path_shape_comparison_debug(*, raw_paths, sampled_paths, execution_paths, save_dir='debug_plots')
```

Persist metrics and an overlay comparing pixel-to-mm output to move-prep paths.

### `_path_xy`

```python
def _path_xy(path) -> np.ndarray
```

### `_shape_metrics`

```python
def _shape_metrics(xy: np.ndarray) -> dict
```

### `_shape_delta`

```python
def _shape_delta(reference_xy: np.ndarray, candidate_xy: np.ndarray) -> dict
```

### `_nearest_distance_stats`

```python
def _nearest_distance_stats(reference_xy: np.ndarray, candidate_xy: np.ndarray) -> dict
```

### `_nearest_distances`

```python
def _nearest_distances(source_xy: np.ndarray, target_xy: np.ndarray) -> np.ndarray
```

### `_xy_path_length`

```python
def _xy_path_length(xy: np.ndarray) -> float
```

### `_signed_area_abs`

```python
def _signed_area_abs(xy: np.ndarray) -> float
```

### `_plot_path_shape_comparison_overlay`

```python
def _plot_path_shape_comparison_overlay(*, raw_paths, sampled_paths, execution_paths, reports, save_dir: str, timestamp: str)
```

### `plot_trajectory_debug`

```python
def plot_trajectory_debug(raw_paths, curve_paths, sampled_paths, execution_paths=None, prepared_paths=None, camera_preview_paths=None, save_dir='debug_plots', heading_marker_threshold_deg: float=_EXECUTION_HEADING_MARKER_THRESHOLD_DEG)
```

### `plot_pivot_path_debug`

```python
def plot_pivot_path_debug(source_paths, pivot_paths, pivot_pose, motion_snapshots=None, save_dir='debug_plots')
```

### `plot_workpiece_alignment_debug`

```python
def plot_workpiece_alignment_debug(original_contour, aligned_contour, save_dir='debug_plots')
```

## `interpolation_pipeline.py`

Source: [src/engine/robot/path_interpolation/new_interpolation/interpolation_pipeline.py](../../../../../src/engine/robot/path_interpolation/new_interpolation/interpolation_pipeline.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `cv2`, `dataclasses`, `numpy`, `scipy.interpolate`, `scipy.signal`, `typing`.

Module declarations (expressions are shown without evaluating them):

```python
CurveMethod = Literal['linear', 'pchip']
NoiseMethod = Literal['none', 'moving_average', 'savgol']
ContourSelectionMode = Literal['largest_area', 'index']
```

### `PreprocessConfig`

```python
@dataclass(slots=True)
class PreprocessConfig:
```

Declared fields/defaults:

```python
close_tol: float = 5.0
min_spacing: float = 1.0
max_segment_length: float = 0.0
use_approx_poly_dp: bool = False
approx_epsilon_factor: float = 0.01
noise_method: NoiseMethod = 'none'
noise_strength: float = 5.0
```

### `InterpolationConfig`

```python
@dataclass(slots=True)
class InterpolationConfig:
```

Declared fields/defaults:

```python
method: CurveMethod = 'pchip'
output_spacing: float = 10.0
dense_sampling_factor: float = 0.25
```

### `PipelineResult`

```python
@dataclass(slots=True)
class PipelineResult:
```

Declared fields/defaults:

```python
raw: np.ndarray
prepared: np.ndarray
curve: np.ndarray
sampled: np.ndarray
```

### `contour_to_xy`

```python
def contour_to_xy(contour: np.ndarray) -> np.ndarray
```

Convert a contour from OpenCV-style or Nx2 format to float Nx2.

### `normalize_contours`

```python
def normalize_contours(contours: list[np.ndarray] | None) -> list[np.ndarray]
```

Normalize a list of contours into float Nx2 arrays.

### `contour_area_xy`

```python
def contour_area_xy(contour: np.ndarray) -> float
```

Compute absolute contour area in XY space.

### `select_contour`

```python
def select_contour(contours: list[np.ndarray], mode: ContourSelectionMode='largest_area', index: int=0) -> np.ndarray
```

Select one contour from a list.

### `remove_duplicate_consecutive`

```python
def remove_duplicate_consecutive(points: np.ndarray, eps: float=1e-09) -> np.ndarray
```

Drop consecutive duplicates or near-duplicates.

### `close_if_needed`

```python
def close_if_needed(points: np.ndarray, close_tol: float) -> np.ndarray
```

Append the first point if the contour is almost closed.

### `simplify_min_spacing`

```python
def simplify_min_spacing(points: np.ndarray, min_spacing: float) -> np.ndarray
```

Keep points separated by at least min_spacing.

### `densify_max_spacing`

```python
def densify_max_spacing(points: np.ndarray, max_segment_length: float) -> np.ndarray
```

Insert linear support points so no segment exceeds max_segment_length.

### `approx_polyline`

```python
def approx_polyline(points: np.ndarray, epsilon_factor: float, closed: bool) -> np.ndarray
```

Simplify using OpenCV approxPolyDP with perimeter-scaled epsilon.

### `smooth_points`

```python
def smooth_points(points: np.ndarray, method: NoiseMethod, strength: float) -> np.ndarray
```

Apply optional light denoising in XY space.

### `path_lengths`

```python
def path_lengths(points: np.ndarray) -> np.ndarray
```

Cumulative arc length along a polyline.

### `pchip_curve`

```python
def pchip_curve(points: np.ndarray, sample_count: int) -> np.ndarray
```

Fit and sample a PCHIP curve using arc length as parameter.

### `fit_curve`

```python
def fit_curve(points: np.ndarray, config: InterpolationConfig) -> np.ndarray
```

Create a dense geometric curve from prepared contour points.

### `arc_length_resample`

```python
def arc_length_resample(points: np.ndarray, spacing: float) -> np.ndarray
```

Resample a polyline at nearly uniform arc-length spacing.

### `ContourPathPipeline`

```python
class ContourPathPipeline:
```

Clean contour-to-path pipeline for vision contours.

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, preprocess: PreprocessConfig | None=None, interpolation: InterpolationConfig | None=None) -> None
```

```python
def prepare(self, points: np.ndarray) -> tuple[np.ndarray, np.ndarray]
```

Normalize and preprocess raw contour points.

```python
def run(self, points: np.ndarray) -> PipelineResult
```

Run the full contour pipeline.

## `simple_interpolation_pyqt6.py`

Source: [src/engine/robot/path_interpolation/new_interpolation/simple_interpolation_pyqt6.py](../../../../../src/engine/robot/path_interpolation/new_interpolation/simple_interpolation_pyqt6.py).

Imports (including optional/function-local imports; not a startup dependency list): `PyQt6.QtCore`, `PyQt6.QtGui`, `PyQt6.QtWidgets`, `__future__`, `cv2`, `matplotlib.backends.backend_qtagg`, `matplotlib.figure`, `numpy`, `os`, `src.engine.common_settings_ids`, `src.engine.core.message_broker`, `src.engine.repositories.settings_service_factory`, `src.engine.robot.path_interpolation.new_interpolation.interpolation_pipeline`, `src.engine.vision.implementation.VisionSystem.VisionSystem`, `src.engine.vision.implementation.VisionSystem.core.service.internal_service`, `src.engine.vision.vision_service`, `src.engine.work_areas.work_area_service`, `src.robot_systems.glue.glue_robot_system`, `sys`, `time`, `traceback`.

Module declarations (expressions are shown without evaluating them):

```python
DEFAULT_FIGURE8 = '100, 100\n140, 110\n170, 140\n180, 180\n170, 220\n140, 250\n100, 260\n60, 250\n30, 220\n20, 180\n30, 140\n60, 110\n100, 100\n140, 90\n170, 60\n180, 20\n170, -20\n140, -50\n100, -60\n60, -50\n30, -20\n20, 20\n30, 60\n60, 90\n100, 100'
```

### `try_build_vision_service`

```python
def try_build_vision_service(project_root: str | None=None, active_area: str | None=None)
```

### `parse_points`

```python
def parse_points(text: str) -> np.ndarray
```

### `make_shape`

```python
def make_shape(name: str) -> np.ndarray
```

### `draw_contours_on_frame`

```python
def draw_contours_on_frame(frame: np.ndarray, contours: list[np.ndarray], selected_index: int | None) -> np.ndarray
```

### `frame_to_pixmap`

```python
def frame_to_pixmap(frame: np.ndarray, target_width: int=520) -> QPixmap
```

### `MplCanvas`

```python
class MplCanvas(FigureCanvas):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, figsize=(11, 8))
```

### `MainWindow`

```python
class MainWindow(QMainWindow):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self)
```

```python
def build_pipeline(self) -> ContourPathPipeline
```

```python
def on_shape_changed(self, shape: str)
```

```python
def get_selected_contour_index(self) -> int | None
```

```python
def start_vision(self)
```

```python
def stop_vision(self)
```

```python
def poll_vision(self)
```

```python
def refresh_camera_preview(self)
```

```python
def capture_selected_contour(self)
```

```python
def get_raw_points(self) -> np.ndarray
```

```python
def recompute(self)
```

```python
def draw_path(self, result: PipelineResult)
```

```python
def draw_axis_group(self, axes, profiles, axis_name: str, title_prefix: str, limits=None)
```

```python
def draw_profiles(self, result: PipelineResult)
```

```python
def save_current_tab(self)
```

```python
def closeEvent(self, event)
```

### `main`

```python
def main()
```
