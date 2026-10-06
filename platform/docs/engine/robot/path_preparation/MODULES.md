# Module reference: `src/engine/robot/path_preparation`

[Package guide](README.md) · [Complete source index](../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [config.py](#configpy)
- [debug.py](#debugpy)
- [default_workpiece_path_preparation_service.py](#default_workpiece_path_preparation_servicepy)
- [geometry.py](#geometrypy)
- [i_workpiece_path_preparation_service.py](#i_workpiece_path_preparation_servicepy)

## `__init__.py`

Source: [src/engine/robot/path_preparation/__init__.py](../../../../src/engine/robot/path_preparation/__init__.py).

Imports (including optional/function-local imports; not a startup dependency list): `src.engine.robot.path_preparation.config`, `src.engine.robot.path_preparation.default_workpiece_path_preparation_service`, `src.engine.robot.path_preparation.i_workpiece_path_preparation_service`.

Package-level import/export surface:

```python
from src.engine.robot.path_preparation.config import PIXEL_TO_MM_MODE_GEOMETRY_PPM_ANCHOR, PIXEL_TO_MM_MODE_HOMOGRAPHY_RESIDUAL
from src.engine.robot.path_preparation.default_workpiece_path_preparation_service import DefaultWorkpiecePathPreparationService, WorkpieceExecutionPlan
from src.engine.robot.path_preparation.i_workpiece_path_preparation_service import IWorkpiecePathPreparationService
```

No top-level functions, classes or public value declarations; inspect the source for imports or entry-point statements.

## `config.py`

Source: [src/engine/robot/path_preparation/config.py](../../../../src/engine/robot/path_preparation/config.py).

Module declarations (expressions are shown without evaluating them):

```python
PIXEL_TO_MM_MODE_GEOMETRY_PPM_ANCHOR = 'geometry_ppm_anchor'
PIXEL_TO_MM_MODE_HOMOGRAPHY_RESIDUAL = 'homography_residual'
```

## `debug.py`

Source: [src/engine/robot/path_preparation/debug.py](../../../../src/engine/robot/path_preparation/debug.py).

Imports (including optional/function-local imports; not a startup dependency list): `cv2`, `datetime`, `logging`, `numpy`, `os`, `src.engine.robot.path_preparation.geometry`.

### `_save_contour_canonicalization_steps_debug_plot`

```python
def _save_contour_canonicalization_steps_debug_plot(original_points: np.ndarray, pickup_point: tuple[float, float] | None=None, *, debug_dir: str='/home/ilv/Desktop/robot_app_platform/src/bootstrap/debug_plots') -> None
```

Save each contour canonicalization step used before pixel-to-mm conversion.

### `_save_contour_reordering_debug_plot`

```python
def _save_contour_reordering_debug_plot(original_points: np.ndarray, reordered_points: np.ndarray, pickup_point: tuple[float, float] | None=None, *, debug_dir: str='/home/ilv/Desktop/robot_app_platform/src/bootstrap/debug_plots') -> None
```

Save an overlay image showing original vs canonicalized contour ordering.

## `default_workpiece_path_preparation_service.py`

Source: [src/engine/robot/path_preparation/default_workpiece_path_preparation_service.py](../../../../src/engine/robot/path_preparation/default_workpiece_path_preparation_service.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `cv2`, `dataclasses`, `datetime`, `matplotlib`, `numpy`, `os`, `pathlib`, `queue`, `src.engine.geometry.planar`, `src.engine.robot.path_interpolation.new_interpolation.debug_plotting`, `src.engine.robot.path_preparation`, `src.engine.robot.path_preparation.debug`, `src.engine.robot.path_preparation.geometry`, `src.engine.robot.path_preparation.i_workpiece_path_preparation_service`, `src.engine.robot.path_preparation.pixel_to_mm`, `src.engine.robot.targeting`, `threading`, `typing`.

Module declarations (expressions are shown without evaluating them):

```python
PIXEL_TO_MM_MODE_GEOMETRY_PPM_ANCHOR = config.PIXEL_TO_MM_MODE_GEOMETRY_PPM_ANCHOR
PIXEL_TO_MM_MODE_HOMOGRAPHY_RESIDUAL = config.PIXEL_TO_MM_MODE_HOMOGRAPHY_RESIDUAL
```

### `_ensure_debug_plot_worker`

```python
def _ensure_debug_plot_worker() -> None
```

### `_debug_plot_worker_loop`

```python
def _debug_plot_worker_loop() -> None
```

### `_submit_debug_plot`

```python
def _submit_debug_plot(logger, plot_label: str, fn: Callable, *args, **kwargs) -> None
```

### `_unwrap_contour_payload`

```python
def _unwrap_contour_payload(contour)
```

### `_contour_points_array`

```python
def _contour_points_array(contour) -> np.ndarray
```

### `_has_valid_contour_payload`

```python
def _has_valid_contour_payload(contour) -> bool
```

### `_copy_path_collection`

```python
def _copy_path_collection(paths: list[list[list[float]]]) -> list[list[list[float]]]
```

### `_pose_path_from_xy`

```python
def _pose_path_from_xy(xy_points: np.ndarray, reference_path: list[list[float]]) -> list[list[float]]
```

### `_cut_closed_contour_at_saved_selection_start`

```python
def _cut_closed_contour_at_saved_selection_start(contour: np.ndarray, selection_payloads: list[dict]) -> tuple[np.ndarray, int | None]
```

Start a closed contour at the first explicit paint-segment point. Only the starting index changes; winding is never reversed. Doing this before interpolation and robot-frame conversion keeps pickup and RTCP orientation consistent and preserves the configured motion direction.

### `WorkpieceExecutionPlan`

```python
@dataclass(frozen=True)
class WorkpieceExecutionPlan:
```

Complete execution plan for a workpiece, holding all path representations and per-segment job specs. Stores the transformation chain: raw pixel paths → prepared/curve/sampled poses → final execution paths, plus per-job metadata (velocity, acceleration, pickup point, target offsets).

Declared fields/defaults:

```python
workpiece: dict
raw_paths: list[list[list[float]]]
prepared_paths: list[list[list[float]]]
curve_paths: list[list[list[float]]]
sampled_paths: list[list[list[float]]]
execution_jobs: list[dict]
total_spline_pts: int
raw_pixel_paths: list[list[list[float]]] = field(default_factory=list)
raw_homography_paths: list[list[list[float]]] = field(default_factory=list)
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def execution_paths(self) -> list[list[list[float]]]
```

Extract the final execution path from each job, falling back to the legacy path key.

### `_safe_float`

```python
def _safe_float(value, default: float) -> float
```

Convert *value* to float, returning *default* on None/empty/conversion failure.

### `_plot_xy_debug_axis`

```python
def _plot_xy_debug_axis(axis, points: np.ndarray, title: str, x_label: str, y_label: str) -> None
```

### `_resolve_segment_tangent_settings`

```python
def _resolve_segment_tangent_settings(settings: dict) -> tuple[float, float]
```

Extract the tangent heading lookahead distance and deadband from per-segment *settings*. Each segment can override the global defaults (PATH_TANGENT_LOOKAHEAD_DISTANCE_MM, PATH_TANGENT_HEADING_DEADBAND_DEG) via its own settings dict.

### `DefaultWorkpiecePathPreparationService`

```python
class DefaultWorkpiecePathPreparationService(IWorkpiecePathPreparationService):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, *, logger, segment_config, transformer=None, resolver=None, transformer_getter: Optional[Callable[[], object]]=None, resolver_getter: Optional[Callable[[], object]]=None, z_min: float=0.0, rz_mode: str='constant', execute_from_workpiece_layer: bool=False, target_point_name: str='', pickup_target_point_name: str='', calibration_frame_name: str='', calibration_frame_name_getter: Optional[Callable[[], str]]=None, pixel_height_compensation_fn: Optional[Callable[[float], tuple[float, float]]]=None, base_position_provider: Optional[Callable[[], Optional[list[float]]]]=None, pickup_axis_alignment_sign: float=1.0, pixel_to_mm_mode: str=config.PIXEL_TO_MM_MODE_GEOMETRY_PPM_ANCHOR, debug_plot_dir: Optional[str]=None, source_contour_processor: Optional[Callable[[np.ndarray, dict], np.ndarray | None]]=None, contour_processor: Optional[Callable[[list[list[float]], dict], dict | None]]=None) -> None
```

Configure the service with transformer/resolver references and per-application settings. Calibration objects can be injected directly (*transformer*, *resolver*) or resolved lazily via callables (*transformer_getter*, *resolver_getter*). The *rz_mode* controls whether heading is constant (segment-level rz_angle) or computed per-point from the path tangent. When *execute_from_workpiece_layer* is True the workpiece contour is used instead of sprayPattern data.

```python
def build_execution_plan(self, workpiece: dict, skip_debug_plot: bool=False) -> WorkpieceExecutionPlan
```

Main entry point: convert a workpiece dict into a fully-prepared execution plan. The pipeline is: 1. Select source — workpiece layer contour or sprayPattern paths. 2. Pixel→robot transform — via calibration resolver or fallback transformer. 3. Optional contour processor — injected by the robot system for smoothing/resampling. 4. Heading reconstruction — constant RZ or path-tangent-aligned. 5. Pickup resolution — compute the first-segment pickup XY and RZ.

### `_base_orientation_xy`

```python
def _base_orientation_xy(base_position: Optional[list[float]]) -> tuple[float, float]
```

Extract RX and RY from a base-position 6-DOF vector, defaulting to (180, 0) when unavailable.

## `geometry.py`

Source: [src/engine/robot/path_preparation/geometry.py](../../../../src/engine/robot/path_preparation/geometry.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `cv2`, `logging`, `numpy`, `src.engine.geometry.planar`.

Module declarations (expressions are shown without evaluating them):

```python
PATH_TANGENT_HEADING_SMOOTHING_WINDOW = 5
PATH_TANGENT_LOOKAHEAD_DISTANCE_MM = 15.0
PATH_TANGENT_HEADING_DEADBAND_DEG = 5.0
```

### `has_valid_contour`

```python
def has_valid_contour(contour) -> bool
```

### `canonicalize_closed_contour_points`

```python
def canonicalize_closed_contour_points(points: np.ndarray) -> np.ndarray
```

Normalize a closed contour to a stable winding and start point. This matters for processes that derive orientation or projected motion from the first contour segment. Raw captured contours often have arbitrary winding and arbitrary start index. Important: canonicalization must not invent new boundary adjacency. If the raw contour order is already a valid closed walk, only cyclic shift and optional reversal are allowed. Rebuilding the loop with nearest-neighbor logic can create broken shapes for otherwise valid captures.

### `_orient_contour_like_original`

```python
def _orient_contour_like_original(points: np.ndarray, original_points: np.ndarray) -> np.ndarray
```

Preserve the original traversal direction when possible. After continuity repair and start-point normalization, the remaining ambiguity is the loop direction. Resolve that by comparing the candidate second point to the original predecessor/successor around the same start.

### `fast_inverse_preview_points`

```python
def fast_inverse_preview_points(transformer, robot_xy_points: np.ndarray) -> np.ndarray | None
```

### `compute_path_aligned_rz_degrees`

```python
def compute_path_aligned_rz_degrees(robot_xy_points: list[tuple[float, float]], base_rz_offset_degrees: float=0.0, lookahead_distance_mm: float=PATH_TANGENT_LOOKAHEAD_DISTANCE_MM, heading_deadband_deg: float=PATH_TANGENT_HEADING_DEADBAND_DEG, boundary_xy_points: np.ndarray | None=None) -> list[float]
```

### `compute_pickup_rz_from_robot_path`

```python
def compute_pickup_rz_from_robot_path(path: list[list[float]], pickup_xy: tuple[float, float]) -> float
```

### `compute_pickup_rz_from_stable_paint_segment`

```python
def compute_pickup_rz_from_stable_paint_segment(path: list[list[float]] | np.ndarray, reference_rz: float=0.0) -> float
```

Select a pickup orientation from a stable segment of the prepared paint path. Closed workpiece contours do not always have a useful whole-shape axis: asymmetry can pull moment/PCA orientation away from the edge frame that will be painted. This selector instead scans the final execution contour and favors segments that are locally straight and require the smallest axis-equivalent rotation from the pickup reference orientation.

### `compute_pickup_rz_from_initial_paint_segment`

```python
def compute_pickup_rz_from_initial_paint_segment(path: list[list[float]] | np.ndarray, reference_rz: float=0.0, *, max_run_mm: float=25.0, heading_tolerance_deg: float=5.0) -> float
```

Return pickup RZ from the first stable run of the prepared paint path. The workpiece is picked before the paint handoff. To align the selected start of the contour with the paint axis, pickup RZ must follow the initial directed segment instead of whichever later segment happens to be closest to zero rotation.

### `compute_pickup_rz_from_min_rect_long_axis`

```python
def compute_pickup_rz_from_min_rect_long_axis(points: list[list[float]] | np.ndarray, reference_rz: float=0.0) -> float
```

Return pickup RZ from the long axis of the contour minimum-area rectangle.

### `_first_directed_heading_from_x`

```python
def _first_directed_heading_from_x(path: list[list[float]]) -> float | None
```

### `compute_pickup_rz_from_robot_contour`

```python
def compute_pickup_rz_from_robot_contour(points: list[list[float]] | np.ndarray) -> float
```

Estimate pickup orientation from contour central moments instead of a local tangent. This is better for centroid pickup on closed workpiece contours, because the centroid is inside the shape and does not have a meaningful boundary tangent.

### `compute_pickup_rz_from_robot_contour_with_direction`

```python
def compute_pickup_rz_from_robot_contour_with_direction(contour_points: list[list[float]] | np.ndarray, path_points: list[list[float]] | np.ndarray) -> float
```

Estimate pickup orientation from the whole contour, then resolve the 180-degree ambiguity using the directed execution path ordering.

### `rebuild_pose_path_from_xy`

```python
def rebuild_pose_path_from_xy(xy_points: np.ndarray, prototype_path: list[list[float]], rz_mode: str, tangent_lookahead_distance_mm: float=PATH_TANGENT_LOOKAHEAD_DISTANCE_MM, tangent_heading_deadband_deg: float=PATH_TANGENT_HEADING_DEADBAND_DEG, tangent_boundary_xy: np.ndarray | None=None) -> list[list[float]]
```

## `i_workpiece_path_preparation_service.py`

Source: [src/engine/robot/path_preparation/i_workpiece_path_preparation_service.py](../../../../src/engine/robot/path_preparation/i_workpiece_path_preparation_service.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `abc`.

### `IWorkpiecePathPreparationService`

```python
class IWorkpiecePathPreparationService(ABC):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
@abstractmethod
def build_execution_plan(self, workpiece: dict, skip_debug_plot: bool=False)
```
