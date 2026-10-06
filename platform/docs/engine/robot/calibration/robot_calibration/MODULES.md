# Module reference: `src/engine/robot/calibration/robot_calibration`

[Package guide](README.md) · [Complete source index](../../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [CalibrationVision.py](#calibrationvisionpy)
- [RobotCalibrationContext.py](#robotcalibrationcontextpy)
- [__init__.py](#__init__py)
- [calibration_report.py](#calibration_reportpy)
- [config_helpers.py](#config_helperspy)
- [live_feed.py](#live_feedpy)
- [logging.py](#loggingpy)
- [metrics.py](#metricspy)
- [model_fitting.py](#model_fittingpy)
- [online_navigation.py](#online_navigationpy)
- [overlay.py](#overlaypy)
- [overlay_renderer.py](#overlay_rendererpy)
- [ppm_utils.py](#ppm_utilspy)
- [robot_calibration_pipeline.py](#robot_calibration_pipelinepy)
- [robot_controller.py](#robot_controllerpy)
- [target_planning.py](#target_planningpy)
- [tcp_offset_capture.py](#tcp_offset_capturepy)

## `CalibrationVision.py`

Source: [src/engine/robot/calibration/robot_calibration/CalibrationVision.py](../../../../../src/engine/robot/calibration/robot_calibration/CalibrationVision.py).

Imports (including optional/function-local imports; not a startup dependency list): `cv2`, `dataclasses`, `logging`, `numpy`, `src.engine.vision.implementation.VisionSystem.features.calibration.charuco.charuco_detector`.

### `ChessboardDetectionResult`

```python
@dataclass
class ChessboardDetectionResult:
```

Declared fields/defaults:

```python
found: bool
ppm: float
bottom_left_px: tuple
message: str
board_kind: str = 'unknown'
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def to_dict(self)
```

### `SpecificMarkerDetectionResult`

```python
@dataclass()
class SpecificMarkerDetectionResult:
```

Declared fields/defaults:

```python
found: bool
aruco_corners: np.ndarray
aruco_ids: np.ndarray
frame: np.ndarray
```

### `FindRequiredMarkersResult`

```python
@dataclass
class FindRequiredMarkersResult:
```

Declared fields/defaults:

```python
found: bool
frame: np.ndarray
```

### `CalibrationVision`

```python
class CalibrationVision:
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, vision_service, chessboard_size, square_size_mm, required_ids, debug, use_marker_centre: bool=False, perspective_matrix=None, reference_board_mode: str='auto', charuco_board_size=None, charuco_marker_size_mm: float | None=None)
```

```python
def find_chessboard_and_compute_ppm(self, frame) -> ChessboardDetectionResult
```

```python
def find_required_aruco_markers(self, frame) -> FindRequiredMarkersResult
```

```python
def update_marker_top_left_corners(self, marker_id, corners, ids)
```

```python
def collect_reference_sample(self, frame, allowed_ids=None) -> dict
```

Detect required markers in a single frame and return their corner positions. Does NOT update internal state — used exclusively for multi-frame averaging. Returns {marker_id: np.ndarray([x, y], float32)} for each detected marker.

```python
def detect_specific_marker(self, frame, marker_id) -> SpecificMarkerDetectionResult
```

## `RobotCalibrationContext.py`

Source: [src/engine/robot/calibration/robot_calibration/RobotCalibrationContext.py](../../../../../src/engine/robot/calibration/robot_calibration/RobotCalibrationContext.py).

Robot Calibration Context This module provides the execution context for robot calibration operations, similar to the ExecutionContext used in the glue dispensing application. It holds all the state and data needed during the calibration process.

Imports (including optional/function-local imports; not a startup dependency list): `dataclasses`, `threading`, `time`.

### `Context`

```python
@dataclass
class Context:
```

Base context class for compatibility with ExecutableStateMachine

### `CalibrationServicesView`

```python
@dataclass
class CalibrationServicesView:
```

Declared fields/defaults:

```python
vision_service: object = None
height_measuring_service: object = None
calibration_robot_controller: object = None
calibration_vision: object = None
settings_service: object = None
broker: object = None
state_machine: object = None
```

### `CalibrationTargetPlanView`

```python
@dataclass
class CalibrationTargetPlanView:
```

Declared fields/defaults:

```python
required_ids: list[int] = None
candidate_ids: list[int] = None
target_marker_ids: list[int] = None
homography_marker_ids: list[int] = None
residual_marker_ids: list[int] = None
validation_marker_ids: list[int] = None
execution_marker_ids: list[int] = None
recovery_marker_id: int | None = None
marker_neighbor_ids: dict | None = None
target_selection_report: dict | None = None
```

### `CalibrationArtifactsView`

```python
@dataclass
class CalibrationArtifactsView:
```

Declared fields/defaults:

```python
bottom_left_chessboard_corner_px: object = None
chessboard_center_px: object = None
markers_offsets_mm: dict | None = None
camera_points_for_homography: dict | None = None
robot_positions_for_calibration: dict | None = None
image_to_robot_mapping: object = None
available_marker_points_px: dict | None = None
failed_target_ids: set[int] | None = None
skipped_target_ids: set[int] | None = None
camera_tcp_offset_samples: list | None = None
camera_tcp_offset_captured_markers: set[int] | None = None
height_map_samples: list | None = None
```

### `CalibrationProgressView`

```python
@dataclass
class CalibrationProgressView:
```

Declared fields/defaults:

```python
current_marker_id: int = 0
iteration_count: int = 0
max_iterations: int = 50
alignment_threshold_mm: float = 1.0
z_current: float | None = None
z_target: float | None = None
ppm_scale: float | None = None
calibration_error_message: str | None = None
total_calibration_start_time: float | None = None
```

### `CalibrationTimingView`

```python
@dataclass
class CalibrationTimingView:
```

Declared fields/defaults:

```python
state_timings: dict | None = None
current_state_start_time: float | None = None
```

### `RobotCalibrationContext`

```python
class RobotCalibrationContext(Context):
```

Holds execution state for robot calibration operations

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self)
```

```python
def reset(self)
```

Reset calibration context to initial state

```python
def get_current_state_name(self) -> str
```

Get current state name for logging

```python
def start_state_timer(self, state_name: str)
```

Start timing for a state

```python
def end_state_timer(self)
```

End timing for current state

```python
def wait_for_frame(self)
```

Return next camera frame, or None if stop was requested before a frame arrived.

```python
def interruptible_sleep(self, seconds: float) -> bool
```

Sleep up to `seconds`. Returns True if interrupted (stop requested), False otherwise.

```python
def flush_camera_buffer(self)
```

```python
def to_debug_dict(self) -> dict
```

Serialize context to dictionary for debug output. Returns a human-readable representation of current calibration state.

```python
def refresh_group_views(self) -> None
```

```python
@property
def target_marker_ids(self)
```

```python
@target_marker_ids.setter
def target_marker_ids(self, value)
```

```python
@property
def homography_marker_ids(self)
```

```python
@homography_marker_ids.setter
def homography_marker_ids(self, value)
```

```python
@property
def residual_marker_ids(self)
```

```python
@residual_marker_ids.setter
def residual_marker_ids(self, value)
```

```python
@property
def validation_marker_ids(self)
```

```python
@validation_marker_ids.setter
def validation_marker_ids(self, value)
```

```python
@property
def execution_marker_ids(self)
```

```python
@execution_marker_ids.setter
def execution_marker_ids(self, value)
```

```python
@property
def recovery_marker_id(self)
```

```python
@recovery_marker_id.setter
def recovery_marker_id(self, value)
```

```python
@property
def marker_neighbor_ids(self)
```

```python
@marker_neighbor_ids.setter
def marker_neighbor_ids(self, value)
```

```python
@property
def target_selection_report(self)
```

```python
@target_selection_report.setter
def target_selection_report(self, value)
```

```python
@property
def bottom_left_chessboard_corner_px(self)
```

```python
@bottom_left_chessboard_corner_px.setter
def bottom_left_chessboard_corner_px(self, value)
```

```python
@property
def chessboard_center_px(self)
```

```python
@chessboard_center_px.setter
def chessboard_center_px(self, value)
```

```python
@property
def markers_offsets_mm(self)
```

```python
@markers_offsets_mm.setter
def markers_offsets_mm(self, value)
```

```python
@property
def camera_points_for_homography(self)
```

```python
@camera_points_for_homography.setter
def camera_points_for_homography(self, value)
```

```python
@property
def robot_positions_for_calibration(self)
```

```python
@robot_positions_for_calibration.setter
def robot_positions_for_calibration(self, value)
```

```python
@property
def image_to_robot_mapping(self)
```

```python
@image_to_robot_mapping.setter
def image_to_robot_mapping(self, value)
```

```python
@property
def available_marker_points_px(self)
```

```python
@available_marker_points_px.setter
def available_marker_points_px(self, value)
```

```python
@property
def failed_target_ids(self)
```

```python
@failed_target_ids.setter
def failed_target_ids(self, value)
```

```python
@property
def skipped_target_ids(self)
```

```python
@skipped_target_ids.setter
def skipped_target_ids(self, value)
```

```python
@property
def camera_tcp_offset_samples(self)
```

```python
@camera_tcp_offset_samples.setter
def camera_tcp_offset_samples(self, value)
```

```python
@property
def camera_tcp_offset_captured_markers(self)
```

```python
@camera_tcp_offset_captured_markers.setter
def camera_tcp_offset_captured_markers(self, value)
```

```python
@property
def height_map_samples(self)
```

```python
@height_map_samples.setter
def height_map_samples(self, value)
```

```python
@property
def current_marker_id(self)
```

```python
@current_marker_id.setter
def current_marker_id(self, value)
```

```python
@property
def iteration_count(self)
```

```python
@iteration_count.setter
def iteration_count(self, value)
```

```python
@property
def max_iterations(self)
```

```python
@max_iterations.setter
def max_iterations(self, value)
```

```python
@property
def alignment_threshold_mm(self)
```

```python
@alignment_threshold_mm.setter
def alignment_threshold_mm(self, value)
```

```python
@property
def Z_current(self)
```

```python
@Z_current.setter
def Z_current(self, value)
```

```python
@property
def Z_target(self)
```

```python
@Z_target.setter
def Z_target(self, value)
```

```python
@property
def ppm_scale(self)
```

```python
@ppm_scale.setter
def ppm_scale(self, value)
```

```python
@property
def calibration_error_message(self)
```

```python
@calibration_error_message.setter
def calibration_error_message(self, value)
```

```python
@property
def total_calibration_start_time(self)
```

```python
@total_calibration_start_time.setter
def total_calibration_start_time(self, value)
```

```python
@property
def state_timings(self)
```

```python
@state_timings.setter
def state_timings(self, value)
```

```python
@property
def current_state_start_time(self)
```

```python
@current_state_start_time.setter
def current_state_start_time(self, value)
```

## `__init__.py`

Source: [src/engine/robot/calibration/robot_calibration/__init__.py](../../../../../src/engine/robot/calibration/robot_calibration/__init__.py).

No top-level functions, classes or public value declarations; inspect the source for imports or entry-point statements.

## `calibration_report.py`

Source: [src/engine/robot/calibration/robot_calibration/calibration_report.py](../../../../../src/engine/robot/calibration/robot_calibration/calibration_report.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `dataclasses`, `datetime`, `json`, `logging`, `numpy`, `pathlib`, `src.engine.robot.calibration.robot_calibration.logging`.

### `CalibrationReportBundle`

```python
@dataclass(frozen=True)
class CalibrationReportBundle:
```

Declared fields/defaults:

```python
completion_log: str
model_comparison_report: str
calibration_analysis_report: str
artifact_paths: dict
```

### `build_calibration_reports`

```python
def build_calibration_reports(*, context, model_result, candidate_ids: list[int], selected_ids: list[int], used_ids: list[int], skipped_ids: list[int], failed_ids: list[int], recovery_marker_id: int | None, total_calibration_time: float) -> CalibrationReportBundle
```

### `save_calibration_model_report`

```python
def save_calibration_model_report(report: dict, report_path: str) -> None
```

### `save_homography_residual_artifact`

```python
def save_homography_residual_artifact(homography_residual_artifact: dict, path: str) -> None
```

### `save_geometry_scale_artifact`

```python
def save_geometry_scale_artifact(payload: dict, path: str) -> None
```

### `derive_calibration_artifact_paths`

```python
def derive_calibration_artifact_paths(matrix_path: str) -> dict
```

### `format_model_comparison_report`

```python
def format_model_comparison_report(report: dict) -> str
```

### `format_calibration_analysis_report`

```python
def format_calibration_analysis_report(report: dict) -> str
```

### `_format_summary_line`

```python
def _format_summary_line(model_name: str, summary: dict) -> str
```

### `_format_analysis_line`

```python
def _format_analysis_line(model_name: str, summary: dict) -> str
```

### `_fmt_error`

```python
def _fmt_error(value) -> str
```

### `_fmt_delta`

```python
def _fmt_delta(before, after) -> str
```

### `_to_json_ready`

```python
def _to_json_ready(value)
```

## `config_helpers.py`

Source: [src/engine/robot/calibration/robot_calibration/config_helpers.py](../../../../../src/engine/robot/calibration/robot_calibration/config_helpers.py).

Imports (including optional/function-local imports; not a startup dependency list): `src.engine.robot.interfaces`, `src.engine.vision`.

### `AdaptiveMovementConfig`

```python
class AdaptiveMovementConfig:
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, min_step_mm, max_step_mm, target_error_mm, max_error_ref, k, derivative_scaling, initial_align_y_scale: float=1.0, initial_align_approach_z: float | None=None)
```

```python
def to_dict(self)
```

### `RobotCalibrationEventsConfig`

```python
class RobotCalibrationEventsConfig:
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, broker, calibration_start_topic, calibration_stop_topic, calibration_image_topic, calibration_log_topic)
```

```python
def to_dict(self)
```

### `RobotCalibrationConfig`

```python
class RobotCalibrationConfig:
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, vision_service, robot_service, navigation_service, height_measuring_service, required_ids, z_target, robot_tool, robot_user, candidate_ids=None, min_target_separation_px: float=120.0, homography_target_count: int | None=None, residual_target_count: int | None=None, validation_target_count: int | None=None, test_target_count: int | None=None, auto_skip_known_unreachable_markers: bool=True, unreachable_marker_failure_threshold: int=1, known_unreachable_marker_ids=None, unreachable_marker_failure_counts=None, velocity: int=30, acceleration: int=10, travel_velocity: int | None=None, travel_acceleration: int | None=None, iterative_velocity: int | None=None, iterative_acceleration: int | None=None, run_height_measurement: bool=True, settings_service=None, calibration_settings_key: str | None=None, vision_calibration_settings_key: str | None=None, robot_config=None, robot_config_key: str | None=None, camera_tcp_offset_config=None, axis_mapping_config=None, chessboard_width: int | None=None, chessboard_height: int | None=None, chessboard_square_size_mm: float | None=None, reference_board_mode: str='auto', charuco_board_width: int | None=None, charuco_board_height: int | None=None, charuco_square_size_mm: float | None=None, charuco_marker_size_mm: float | None=None, debug=False, step_by_step=False, live_visualization=False, use_marker_centre: bool=False, use_ransac: bool=False, perspective_matrix=None)
```

## `live_feed.py`

Source: [src/engine/robot/calibration/robot_calibration/live_feed.py](../../../../../src/engine/robot/calibration/robot_calibration/live_feed.py).

Imports (including optional/function-local imports; not a startup dependency list): `cv2`, `logging`, `queue`, `src.engine.robot.calibration.robot_calibration.overlay`, `threading`, `time`.

### `show_live_feed`

```python
def show_live_feed(context, frame, current_error_mm=None, window_name='Calibration Live Feed', draw_overlay=True, broadcast_image=False)
```

Show live camera feed with overlays in a background display thread.

### `stop_live_feed_thread`

```python
def stop_live_feed_thread()
```

Stop the live feed display thread gracefully.

### `_live_feed_display_worker`

```python
def _live_feed_display_worker()
```

## `logging.py`

Source: [src/engine/robot/calibration/robot_calibration/logging.py](../../../../../src/engine/robot/calibration/robot_calibration/logging.py).

Imports (including optional/function-local imports; not a startup dependency list): `numpy`, `typing`.

### `get_log_timing_summary`

```python
def get_log_timing_summary(state_timings)
```

Construct and return a detailed timing summary for calibration state durations. Args: state_timings (dict[str, list[float]]): Mapping of state names to lists of duration values. Returns: str: A formatted multi-line string containing total times, averages, and bottleneck analysis.

### `construct_chessboard_state_log_message`

```python
def construct_chessboard_state_log_message(found: bool, ppm: Optional[float]=None, bottom_left_corner: Optional[np.ndarray]=None, debug_enabled: bool=False, detection_message: Optional[str]=None) -> str
```

Construct a structured log message describing the LOOKING_FOR_CHESSBOARD state results. Args: found (bool): Whether the reference board was successfully detected. ppm (Optional[float]): Pixels-per-millimeter value computed from the detected reference board. bottom_left_corner (Optional[np.ndarray]): Pixel coordinates of the bottom-left board reference corner. debug_enabled (bool): Whether debug drawing is active. detection_message (Optional[str]): Message from the board detection result. Returns: str: Formatted multi-line message summarizing the board detection step.

### `construct_aruco_state_log_message`

```python
def construct_aruco_state_log_message(detected_ids: Set[Any], marker_top_left_corners_px: Dict[int, Tuple[float, float]], marker_top_left_corners_mm: Optional[Dict[int, Tuple[float, float]]]=None, ppm: Optional[float]=None, bottom_left_corner_px: Optional[np.ndarray]=None, selected_ids: Optional[list[int]]=None) -> str
```

Construct a structured log message summarizing the ALL_ARUCO_FOUND state. Args: detected_ids (List[int]): List of detected ArUco marker IDs. marker_top_left_corners_px (Dict[int, Tuple[float, float]]): Top-left corner pixel positions for each marker. marker_top_left_corners_mm (Optional[Dict[int, Tuple[float, float]]]): Converted millimeter positions. ppm (Optional[float]): Pixels per millimeter value (used for conversion). bottom_left_corner_px (Optional[np.ndarray]): Bottom-left chessboard corner in pixels. Returns: str: Multi-line formatted message summarizing ArUco marker detection results.

### `construct_compute_offsets_log_message`

```python
def construct_compute_offsets_log_message(ppm: Optional[float], bottom_left_corner_px: Optional[np.ndarray], image_center_px: Optional[Tuple[int, int]], marker_top_left_corners_mm: Dict[int, Tuple[float, float]], markers_offsets_mm: Optional[Dict[int, Tuple[float, float]]]=None) -> str
```

Construct a detailed log message summarizing the COMPUTE_OFFSETS stage of calibration. Args: ppm (Optional[float]): Pixels per millimeter calibration constant. bottom_left_corner_px (Optional[np.ndarray]): Bottom-left chessboard corner in pixels. image_center_px (Optional[Tuple[int, int]]): Camera image center in pixels. marker_top_left_corners_mm (Dict[int, Tuple[float, float]]): Marker positions in mm relative to bottom-left. markers_offsets_mm (Optional[Dict[int, Tuple[float, float]]]): Computed offsets from image center. Returns: str: Multi-line human-readable calibration summary.

### `construct_align_robot_log_message`

```python
def construct_align_robot_log_message(marker_id: int, calib_to_marker: Tuple[float, float], current_pose: Tuple[float, float, float, float, float, float], calib_pose: Tuple[float, float, float, float, float, float], z_target: float, result: Optional[int]=None, retry_attempted: bool=False, actual_target_pose=None, settle_s: float=1.0) -> str
```

Construct a detailed log message summarizing the ALIGN_ROBOT stage. Args: marker_id (int): Current marker being aligned to. calib_to_marker (Tuple[float, float]): Offset from calibration pose to marker (mm). current_pose (Tuple[float, float, float, float, float, float]): Current robot pose (x, y, z, rx_degrees, ry_degrees, rz_degrees). calib_pose (Tuple[float, float, float, float, float, float]): Calibration reference pose. z_target (float): Z target height for movement. result (Optional[int]): Result of movement command (0 = success, nonzero = failure). retry_attempted (bool): Whether a retry was performed. Returns: str: Formatted multi-line log summary for this robot alignment step.

### `construct_iterative_alignment_log_message`

```python
def construct_iterative_alignment_log_message(marker_id: int, iteration: int, max_iterations: int, capture_time: float, detection_time: float, processing_time: float, movement_time: Optional[float]=None, stability_time: Optional[float]=None, current_error_mm: Optional[float]=None, current_error_px: Optional[float]=None, offset_mm: Optional[Tuple[float, float]]=None, threshold_mm: Optional[float]=None, alignment_success: bool=False, result: Optional[int]=None) -> str
```

Construct a structured log summary for the ITERATE_ALIGNMENT state. Args: marker_id (int): Marker being processed. iteration (int): Current iteration number. max_iterations (int): Maximum allowed iterations. capture_time (float): Time to capture frame. detection_time (float): Time to detect ArUco marker. processing_time (float): Time for error computation and data updates. movement_time (float, optional): Time for robot movement. stability_time (float, optional): Time waited for stabilization. current_error_mm (float, optional): Current alignment error in mm. current_error_px (float, optional): Current alignment error in x_pixels. offset_mm (tuple, optional): (X, Y) offset in mm. threshold_mm (float, optional): Error threshold for success. alignment_success (bool): True if alignment succeeded this iteration. result (int, optional): Movement command result (0=success, nonzero=failure). Returns: str: A formatted multi-line log summary.

### `construct_calibration_completion_log_message`

```python
def construct_calibration_completion_log_message(sorted_robot_items, sorted_camera_items, H_camera_center, status, average_error_camera_center, matrix_path, total_calibration_time, *, candidate_ids=None, selected_ids=None, used_ids=None, skipped_ids=None, failed_ids=None, recovery_marker_id=None) -> str
```

Construct a structured log message summarizing the calibration completion phase. Args: sorted_robot_items (list): List of (marker_id, robot_position) pairs. sorted_camera_items (list): List of (marker_id, camera_point) pairs. H_camera_center (np.ndarray): Computed homography matrix. status (np.ndarray): Homography computation status array. average_error_camera_center (float): Mean reprojection error in mm. matrix_path (str): File path where matrix is saved. total_calibration_time (float): Total duration of calibration in seconds. Returns: str: Multi-line structured summary log.

## `metrics.py`

Source: [src/engine/robot/calibration/robot_calibration/metrics.py](../../../../../src/engine/robot/calibration/robot_calibration/metrics.py).

Imports (including optional/function-local imports; not a startup dependency list): `cv2`, `dataclasses`, `itertools`, `json`, `logging`, `numpy`, `scipy.interpolate`, `src.engine.robot.calibration.robot_calibration.calibration_report`.

### `compute_avg_ppm`

```python
def compute_avg_ppm(camera_points, robot_points)
```

### `test_calibration`

```python
def test_calibration(homography_matrix, camera_points, robot_points, save_json_path=None)
```

### `compute_homography`

```python
def compute_homography(camera_points_for_homography, robot_positions_for_calibration, use_ransac: bool=False)
```

### `prepare_correspondence_points`

```python
def prepare_correspondence_points(camera_points_for_homography, robot_positions_for_calibration)
```

### `compute_homography_from_arrays`

```python
def compute_homography_from_arrays(src_pts, dst_pts, use_ransac: bool=False)
```

### `HomographyResidualModel`

```python
@dataclass(frozen=True)
class HomographyResidualModel:
```

Declared fields/defaults:

```python
homography_matrix: np.ndarray
dx_coeffs: np.ndarray
dy_coeffs: np.ndarray
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def predict(self, point) -> np.ndarray
```

```python
def to_dict(self) -> dict
```

### `HomographyTPSResidualModel`

```python
class HomographyTPSResidualModel:
```

Homography + Thin Plate Spline residual correction model.

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, homography_matrix, support_points, dx_residuals, dy_residuals)
```

```python
def predict(self, point) -> np.ndarray
```

```python
def to_dict(self) -> dict
```

### `evaluate_homography_fit`

```python
def evaluate_homography_fit(labels, src_pts, dst_pts, use_ransac: bool=False) -> dict
```

### `build_homography_residual_model`

```python
def build_homography_residual_model(src_pts, dst_pts, use_ransac: bool=False) -> HomographyResidualModel
```

### `evaluate_homography_residual_fit`

```python
def evaluate_homography_residual_fit(labels, src_pts, dst_pts, use_ransac: bool=False) -> dict
```

### `build_homography_tps_residual_model`

```python
def build_homography_tps_residual_model(src_pts, dst_pts, use_ransac: bool=False) -> HomographyTPSResidualModel
```

### `build_homography_residual_model_from_base`

```python
def build_homography_residual_model_from_base(homography_matrix, src_pts, dst_pts) -> HomographyResidualModel
```

### `build_homography_tps_residual_model_from_base`

```python
def build_homography_tps_residual_model_from_base(homography_matrix, src_pts, dst_pts) -> HomographyTPSResidualModel
```

### `evaluate_homography_tps_residual_fit`

```python
def evaluate_homography_tps_residual_fit(labels, src_pts, dst_pts, use_ransac: bool=False) -> dict
```

### `evaluate_homography_residual_fit_from_model`

```python
def evaluate_homography_residual_fit_from_model(labels, src_pts, dst_pts, model: HomographyResidualModel) -> dict
```

### `evaluate_homography_tps_residual_fit_from_model`

```python
def evaluate_homography_tps_residual_fit_from_model(labels, src_pts, dst_pts, model: HomographyTPSResidualModel) -> dict
```

### `evaluate_model_on_holdout`

```python
def evaluate_model_on_holdout(labels, src_pts, dst_pts, *, homography_matrix=None, homography_residual_model: HomographyResidualModel | None=None, homography_tps_residual_model: HomographyTPSResidualModel | None=None) -> dict
```

### `evaluate_leave_one_out`

```python
def evaluate_leave_one_out(labels, src_pts, dst_pts, use_ransac: bool=False) -> dict
```

### `build_calibration_model_report`

```python
def build_calibration_model_report(camera_points_for_homography, robot_positions_for_calibration, use_ransac: bool=False, metadata: dict | None=None, validation_camera_points=None, validation_robot_positions=None) -> dict
```

### `build_split_calibration_model_report`

```python
def build_split_calibration_model_report(homography_camera_points, homography_robot_points, residual_camera_points, residual_robot_points, *, use_ransac: bool=False, metadata: dict | None=None, validation_camera_points=None, validation_robot_positions=None) -> dict
```

### `save_calibration_model_report`

```python
def save_calibration_model_report(report: dict, report_path: str) -> None
```

### `save_homography_residual_artifact`

```python
def save_homography_residual_artifact(homography_residual_artifact: dict, path: str) -> None
```

### `derive_calibration_artifact_paths`

```python
def derive_calibration_artifact_paths(matrix_path: str) -> dict
```

### `format_model_comparison_report`

```python
def format_model_comparison_report(report: dict) -> str
```

### `format_calibration_analysis_report`

```python
def format_calibration_analysis_report(report: dict) -> str
```

### `_build_error_records`

```python
def _build_error_records(labels, src_pts, dst_pts, predictions, model_name: str) -> list[dict]
```

### `_build_single_record`

```python
def _build_single_record(label, camera_point, robot_point, prediction, model_name: str, note: str | None=None, error_override: float | None=None) -> dict
```

### `_summarize_records`

```python
def _summarize_records(records: list[dict]) -> dict
```

### `_quadratic_uv_features`

```python
def _quadratic_uv_features(point) -> np.ndarray
```

### `_format_summary_line`

```python
def _format_summary_line(model_name: str, summary: dict) -> str
```

### `_format_analysis_line`

```python
def _format_analysis_line(model_name: str, summary: dict) -> str
```

### `_fmt_error`

```python
def _fmt_error(value) -> str
```

### `_fmt_delta`

```python
def _fmt_delta(before, after) -> str
```

### `_fmt_note`

```python
def _fmt_note(note: str | None) -> str
```

### `_to_json_ready`

```python
def _to_json_ready(value)
```

## `model_fitting.py`

Source: [src/engine/robot/calibration/robot_calibration/model_fitting.py](../../../../../src/engine/robot/calibration/robot_calibration/model_fitting.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `dataclasses`, `src.engine.robot.calibration.robot_calibration`.

### `CalibrationDataset`

```python
@dataclass(frozen=True)
class CalibrationDataset:
```

Declared fields/defaults:

```python
used_marker_ids: list[int]
dropped_camera_ids: list[int]
homography_training_ids: list[int]
residual_training_ids: list[int]
validation_ids: list[int]
homography_camera_points: dict[int, tuple[float, float]]
homography_robot_positions: dict[int, tuple[float, ...]]
residual_camera_points: dict[int, tuple[float, float]]
residual_robot_positions: dict[int, tuple[float, ...]]
validation_camera_points: dict[int, tuple[float, float]]
validation_robot_positions: dict[int, tuple[float, ...]]
```

### `CalibrationModelResult`

```python
@dataclass(frozen=True)
class CalibrationModelResult:
```

Declared fields/defaults:

```python
labels: list[int]
src_pts: object
dst_pts: object
homography_matrix: object
homography_status: list[int] | None
average_error_mm: float
model_report: dict
sorted_robot_items: list[tuple[int, tuple[float, ...]]]
sorted_camera_items: list[tuple[int, tuple[float, float]]]
```

### `build_calibration_dataset`

```python
def build_calibration_dataset(context) -> CalibrationDataset
```

### `build_calibration_model`

```python
def build_calibration_model(dataset: CalibrationDataset, *, use_ransac: bool, metadata: dict) -> CalibrationModelResult
```

## `online_navigation.py`

Source: [src/engine/robot/calibration/robot_calibration/online_navigation.py](../../../../../src/engine/robot/calibration/robot_calibration/online_navigation.py).

Guarded in-memory navigation model used while collecting calibration points.

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `cv2`, `dataclasses`, `logging`, `numpy`.

### `OnlineNavigationPrediction`

```python
@dataclass(frozen=True)
class OnlineNavigationPrediction:
```

Declared fields/defaults:

```python
robot_xy: tuple[float, float]
sample_count: int
median_training_error_mm: float
```

### `predict_robot_xy`

```python
def predict_robot_xy(context, marker_id: int) -> OnlineNavigationPrediction | None
```

Predict marker robot XY from accepted training correspondences. The model is deliberately ephemeral and never replaces the final calibration artifact. Validation markers are excluded from fitting.

## `overlay.py`

Source: [src/engine/robot/calibration/robot_calibration/overlay.py](../../../../../src/engine/robot/calibration/robot_calibration/overlay.py).

Imports (including optional/function-local imports; not a startup dependency list): `src.engine.robot.calibration.robot_calibration.overlay_renderer`.

### `draw_image_center`

```python
def draw_image_center(frame) -> None
```

### `build_overlay_status`

```python
def build_overlay_status(context, current_error_mm=None) -> dict
```

### `draw_live_overlay`

```python
def draw_live_overlay(context, frame, current_error_mm=None)
```

## `overlay_renderer.py`

Source: [src/engine/robot/calibration/robot_calibration/overlay_renderer.py](../../../../../src/engine/robot/calibration/robot_calibration/overlay_renderer.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `cv2`, `dataclasses`, `typing`.

### `OverlayStatus`

```python
@dataclass(frozen=True)
class OverlayStatus:
```

Declared fields/defaults:

```python
state_name: str
target_ids: list[int]
current_marker_index: int
iteration_count: int
max_iterations: int
alignment_threshold_mm: float
current_error_mm: float | None = None
```

### `CalibrationRenderer`

```python
class CalibrationRenderer(Protocol):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def draw_image_center(self, frame) -> None
```

```python
def render_live_overlay(self, frame, status: OverlayStatus)
```

### `NoOpCalibrationRenderer`

```python
class NoOpCalibrationRenderer:
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def draw_image_center(self, frame) -> None
```

```python
def render_live_overlay(self, frame, status: OverlayStatus)
```

### `OpenCvCalibrationRenderer`

```python
class OpenCvCalibrationRenderer:
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def draw_image_center(self, frame) -> None
```

```python
def render_live_overlay(self, frame, status: OverlayStatus)
```

### `get_calibration_renderer`

```python
def get_calibration_renderer(context) -> CalibrationRenderer
```

### `_draw_progress_bar`

```python
def _draw_progress_bar(frame, progress: float) -> None
```

### `_draw_status_text`

```python
def _draw_status_text(frame, status_text: str) -> None
```

### `_draw_marker_info`

```python
def _draw_marker_info(frame, marker_id: int, marker_index: int, total_markers: int) -> None
```

### `_draw_iteration_info`

```python
def _draw_iteration_info(frame, iteration_count: int, max_iterations: int) -> None
```

### `_draw_error_info`

```python
def _draw_error_info(frame, current_error_mm: float, threshold_mm: float) -> None
```

### `_draw_progress_text`

```python
def _draw_progress_text(frame, progress: float) -> None
```

## `ppm_utils.py`

Source: [src/engine/robot/calibration/robot_calibration/ppm_utils.py](../../../../../src/engine/robot/calibration/robot_calibration/ppm_utils.py).

Shared PPM (pixels-per-mm) online-refinement helpers. Used by both ``handle_iterate_alignment_state`` (iterate_alignment.py) and ``_align_marker_to_center`` (tcp_offset_capture.py) so the logic lives in exactly one place. Algorithm summary ----------------- At every iteration we know: * How far the robot actually moved (query position before+after) * How much the pixel error changed (measured in the next frame) Because ImageToRobotMapping is a pure axis-permutation + sign-flip (orthogonal, unit-scale), \|robot_delta_mm\| == \|image_delta_mm\|, so: ppm_observed = pixel_reduction / robot_delta_mm We maintain a running EMA on ``context.ppm_working``. The learning rate (α) scales with the robot-move magnitude: large moves produce high-SNR observations and are trusted more. Noise guards ------------ * robot_delta > 0.5 mm — reject jitter / micro-settling * pixel_reduction > 3 px — sub-pixel ArUco noise floor * probe_err > 8 px — previous error must be significant (≥ ~1.8 mm) to prevent near-convergence noise from dirtying the estimate * outlier band [0.55×, 2.5×] current estimate * observed reduction must be at least 40% of the reduction predicted by the current PPM estimate; otherwise a sideways/poorly-correlated move can look like a much lower PPM and destabilize the next correction.

Imports (including optional/function-local imports; not a startup dependency list): `logging`, `math`.

### `get_working_ppm`

```python
def get_working_ppm(context) -> float
```

Return (and lazily initialise) ``context.ppm_working``.

### `clear_ppm_probe`

```python
def clear_ppm_probe(context) -> None
```

Invalidate the probe — call when the robot teleports or rotates significantly.

### `store_ppm_probe`

```python
def store_ppm_probe(context, robot_pos_now: list, current_error_px: float) -> None
```

Record position + error *before* a move so the next iteration can compute Δ.

### `try_refine_ppm`

```python
def try_refine_ppm(context, robot_pos_now: list, current_error_px: float, label: str) -> float
```

Attempt one PPM-refinement step and return the (possibly updated) ppm_working. Parameters ---------- context: calibration context (holds ppm_working + probe attributes) robot_pos_now: current robot position as [x, y, z, ...] list current_error_px: pixel error measured in this iteration (AFTER the previous move) label: short string for the log line (e.g. "marker 0 iter 3")

### `adaptive_stability_wait`

```python
def adaptive_stability_wait(context, current_error_mm: float) -> float
```

Return a stability-wait duration scaled to the current error magnitude. Small corrections near the threshold settle in milliseconds. The full ``context.fast_iteration_wait`` is only used for errors at or above ``_MAX_ERR_REF_MM`` (10 mm).

## `robot_calibration_pipeline.py`

Source: [src/engine/robot/calibration/robot_calibration/robot_calibration_pipeline.py](../../../../../src/engine/robot/calibration/robot_calibration/robot_calibration_pipeline.py).

Refactored Robot Calibration using ExecutableStateMachine This module provides a refactored version of the robot calibration vision_service that uses the ExecutableStateMachine for better separation of concerns, maintainability, and consistency with other vision_service components.

Imports (including optional/function-local imports; not a startup dependency list): `cv2`, `logging`, `numpy`, `src.engine.process.executable_state_machine`, `src.engine.robot.calibration.robot_calibration`, `src.engine.robot.calibration.robot_calibration.CalibrationVision`, `src.engine.robot.calibration.robot_calibration.RobotCalibrationContext`, `src.engine.robot.calibration.robot_calibration.calibration_report`, `src.engine.robot.calibration.robot_calibration.config_helpers`, `src.engine.robot.calibration.robot_calibration.live_feed`, `src.engine.robot.calibration.robot_calibration.logging`, `src.engine.robot.calibration.robot_calibration.model_fitting`, `src.engine.robot.calibration.robot_calibration.robot_controller`, `src.engine.robot.calibration.robot_calibration.states.align_robot`, `src.engine.robot.calibration.robot_calibration.states.all_aruco_found_handler`, `src.engine.robot.calibration.robot_calibration.states.axis_mapping`, `src.engine.robot.calibration.robot_calibration.states.chessboard_found_handler`, `src.engine.robot.calibration.robot_calibration.states.compute_offsets_handler`, `src.engine.robot.calibration.robot_calibration.states.error_handling`, `src.engine.robot.calibration.robot_calibration.states.handle_height_sample_state`, `src.engine.robot.calibration.robot_calibration.states.initializing`, `src.engine.robot.calibration.robot_calibration.states.iterate_alignment`, `src.engine.robot.calibration.robot_calibration.states.looking_for_aruco_markers_handler`, `src.engine.robot.calibration.robot_calibration.states.looking_for_chessboard_handler`, `src.engine.robot.calibration.robot_calibration.states.robot_calibration_states`, `src.engine.robot.calibration.robot_calibration.states.tcp_offset_state`, `src.engine.robot.calibration.robot_calibration.states.terminal_states`, `time`, `traceback`.

### `RefactoredRobotCalibrationPipeline`

```python
class RefactoredRobotCalibrationPipeline:
```

Refactored robot calibration pipeline using ExecutableStateMachine. This class provides the same functionality as the original pipeline but with better separation of concerns and maintainability.

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, config: RobotCalibrationConfig, adaptive_movement_config: AdaptiveMovementConfig=None, events_config: RobotCalibrationEventsConfig=None)
```

Initialize the refactored calibration pipeline. Args: config: Main calibration configuration adaptive_movement_config: Movement adaptation settings events_config: Event broadcasting configuration

```python
def run(self)
```

Run the calibration process using the state machine. Returns: bool: True if calibration completed successfully, False if error occurred

```python
def get_context(self) -> RobotCalibrationContext
```

Get the calibration context for external access

```python
def get_state_machine(self) -> ExecutableStateMachine
```

Get the state machine for external monitoring

## `robot_controller.py`

Source: [src/engine/robot/calibration/robot_calibration/robot_controller.py](../../../../../src/engine/robot/calibration/robot_calibration/robot_controller.py).

Imports (including optional/function-local imports; not a startup dependency list): `logging`, `numpy`.

### `CalibrationRobotController`

```python
class CalibrationRobotController:
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, robot_service, navigation_service, tool: int, user: int, adaptive_movement_config, velocity: int=30, acceleration: int=10, iterative_velocity: int | None=None, iterative_acceleration: int | None=None)
```

```python
def move_to_position(self, position, blocking=False, velocity=None, acceleration=None)
```

```python
def move_to_iterative_position(self, position, blocking=False, velocity=None, acceleration=None)
```

```python
def get_iterative_align_position(self, current_error_mm, offset_x_mm, offset_y_mm, alignment_threshold_mm, preserve_current_orientation=False)
```

```python
def move_to_calibration_position(self)
```

```python
def get_current_z_value(self)
```

```python
def get_current_position(self)
```

```python
def get_calibration_position(self)
```

```python
def move_y_relative(self, dy_mm, blocking=False)
```

```python
def move_x_relative(self, dx_mm, blocking=False)
```

```python
def reset_derivative_state(self)
```

Clear the derivative term so the first iteration of a new marker is not wrongly damped.

## `target_planning.py`

Source: [src/engine/robot/calibration/robot_calibration/target_planning.py](../../../../../src/engine/robot/calibration/robot_calibration/target_planning.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `cv2`, `dataclasses`, `logging`, `numpy`.

### `TargetSelectionPlan`

```python
@dataclass(frozen=True)
class TargetSelectionPlan:
```

Declared fields/defaults:

```python
selected_ids: list[int]
neighbor_ids: dict[int, list[int]]
report: dict
homography_ids: list[int] | None = None
residual_ids: list[int] | None = None
validation_ids: list[int] | None = None
execution_ids: list[int] | None = None
```

### `build_target_selection_plan`

```python
def build_target_selection_plan(marker_points_px: dict[int, np.ndarray | tuple[float, float]], *, image_width: int, image_height: int, min_targets: int, max_targets: int, min_target_separation_px: float, preferred_ids: list[int] | set[int] | None=None) -> TargetSelectionPlan
```

### `build_partitioned_target_selection_plan`

```python
def build_partitioned_target_selection_plan(marker_points_px: dict[int, np.ndarray | tuple[float, float]], *, image_width: int, image_height: int, homography_targets: int, residual_targets: int, validation_targets: int, min_target_separation_px: float, preferred_ids: list[int] | set[int] | None=None) -> TargetSelectionPlan
```

### `_nearest_neighbor_order`

```python
def _nearest_neighbor_order(points_by_id: dict[int, np.ndarray], marker_ids: list[int], start_point: np.ndarray) -> list[int]
```

### `_select_spread_ids`

```python
def _select_spread_ids(points_by_id: dict[int, np.ndarray], *, image_width: int, image_height: int, min_targets: int, max_targets: int, min_target_separation_px: float, preferred_ids: list[int] | None=None, seed_ids: list[int] | None=None) -> list[int]
```

### `_select_partition_ids`

```python
def _select_partition_ids(points_by_id: dict[int, np.ndarray], *, candidate_ids: list[int], image_width: int, image_height: int, target_count: int, min_target_separation_px: float, preferred_ids: list[int] | None=None, seed_ids: list[int] | None=None) -> list[int]
```

### `_select_grid_coverage_ids`

```python
def _select_grid_coverage_ids(points_by_id: dict[int, np.ndarray], *, image_width: int, image_height: int, target_count: int) -> list[int]
```

### `_sort_ids_for_execution`

```python
def _sort_ids_for_execution(points_by_id: dict[int, np.ndarray], marker_ids: list[int]) -> list[int]
```

### `_build_neighbor_ids`

```python
def _build_neighbor_ids(points_by_id: dict[int, np.ndarray]) -> dict[int, list[int]]
```

### `_convex_hull_area`

```python
def _convex_hull_area(points: list[np.ndarray]) -> float
```

### `_minimum_pair_distance`

```python
def _minimum_pair_distance(points: list[np.ndarray]) -> float | None
```

## `tcp_offset_capture.py`

Source: [src/engine/robot/calibration/robot_calibration/tcp_offset_capture.py](../../../../../src/engine/robot/calibration/robot_calibration/tcp_offset_capture.py).

Imports (including optional/function-local imports; not a startup dependency list): `dataclasses`, `logging`, `math`, `numpy`, `src.engine.robot.calibration.robot_calibration.ppm_utils`, `src.engine.robot.calibration.robot_calibration.states.error_handling`.

### `CameraTcpOffsetSample`

```python
@dataclass(frozen=True)
class CameraTcpOffsetSample:
```

Declared fields/defaults:

```python
marker_id: int
sample_index: int
reference_rz: float
sample_rz: float
world_dx: float
world_dy: float
local_dx: float
local_dy: float
```

### `capture_tcp_offset_for_current_marker`

```python
def capture_tcp_offset_for_current_marker(context) -> bool
```

### `finalize_tcp_offset_calibration`

```python
def finalize_tcp_offset_calibration(context) -> tuple[bool, str]
```

### `_build_tcp_offset_summary`

```python
def _build_tcp_offset_summary(samples: list[CameraTcpOffsetSample], *, offset_x: float, offset_y: float, std_x: float, std_y: float) -> str
```

### `should_capture_tcp_offset_for_current_marker`

```python
def should_capture_tcp_offset_for_current_marker(context) -> bool
```

### `_move_and_realign_marker`

```python
def _move_and_realign_marker(context, marker_id: int, target_rz: float)
```

### `_align_marker_to_center`

```python
def _align_marker_to_center(context, marker_id: int, max_iterations: int, camera_rotation_deg: float=0.0)
```

### `_tcp_recenter_position`

```python
def _tcp_recenter_position(context, offset_x_mm: float, offset_y_mm: float, *, max_step_mm: float, correction_gain: float)
```

### `_move_to_pose`

```python
def _move_to_pose(context, pose, label: str, velocity=None, acceleration=None)
```

### `_restore_reference_pose`

```python
def _restore_reference_pose(context, reference_pose, reason: str) -> None
```

### `_solve_local_offset`

```python
def _solve_local_offset(world_dx: float, world_dy: float, *, reference_rz_deg: float, sample_rz_deg: float) -> tuple[float, float]
```
