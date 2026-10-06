# Module reference: `src/engine/robot/calibration/robot_calibration/states`

[Package guide](README.md) · [Complete source index](../../../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [align_robot.py](#align_robotpy)
- [all_aruco_found_handler.py](#all_aruco_found_handlerpy)
- [axis_mapping.py](#axis_mappingpy)
- [chessboard_found_handler.py](#chessboard_found_handlerpy)
- [compute_offsets_handler.py](#compute_offsets_handlerpy)
- [error_handling.py](#error_handlingpy)
- [fallback_targets.py](#fallback_targetspy)
- [handle_height_sample_state.py](#handle_height_sample_statepy)
- [initializing.py](#initializingpy)
- [iterate_alignment.py](#iterate_alignmentpy)
- [looking_for_aruco_markers_handler.py](#looking_for_aruco_markers_handlerpy)
- [looking_for_chessboard_handler.py](#looking_for_chessboard_handlerpy)
- [robot_calibration_states.py](#robot_calibration_statespy)
- [state_result.py](#state_resultpy)
- [tcp_offset_state.py](#tcp_offset_statepy)
- [terminal_states.py](#terminal_statespy)

## `__init__.py`

Source: [src/engine/robot/calibration/robot_calibration/states/__init__.py](../../../../../../src/engine/robot/calibration/robot_calibration/states/__init__.py).

No top-level functions, classes or public value declarations; inspect the source for imports or entry-point statements.

## `align_robot.py`

Source: [src/engine/robot/calibration/robot_calibration/states/align_robot.py](../../../../../../src/engine/robot/calibration/robot_calibration/states/align_robot.py).

Imports (including optional/function-local imports; not a startup dependency list): `logging`, `src.engine.robot.calibration.robot_calibration.logging`, `src.engine.robot.calibration.robot_calibration.online_navigation`, `src.engine.robot.calibration.robot_calibration.ppm_utils`, `src.engine.robot.calibration.robot_calibration.states.error_handling`, `src.engine.robot.calibration.robot_calibration.states.fallback_targets`, `src.engine.robot.calibration.robot_calibration.states.robot_calibration_states`.

Module declarations (expressions are shown without evaluating them):

```python
wait_to_reach_position = True
```

### `_poses_close`

```python
def _poses_close(first, second) -> bool
```

### `_move_to_initial_align_target`

```python
def _move_to_initial_align_target(context, target_position, marker_id)
```

### `handle_align_robot_state`

```python
def handle_align_robot_state(context) -> RobotCalibrationStates
```

## `all_aruco_found_handler.py`

Source: [src/engine/robot/calibration/robot_calibration/states/all_aruco_found_handler.py](../../../../../../src/engine/robot/calibration/robot_calibration/states/all_aruco_found_handler.py).

All ArUco Found State Handler Handles the state when all required ArUco markers have been detected. This state processes the markers and converts their positions from pixel to millimeter coordinates.

Imports (including optional/function-local imports; not a startup dependency list): `logging`, `numpy`, `src.engine.robot.calibration.robot_calibration.logging`, `src.engine.robot.calibration.robot_calibration.states.robot_calibration_states`.

### `handle_all_aruco_found_state`

```python
def handle_all_aruco_found_state(context) -> RobotCalibrationStates
```

Handle the ALL_ARUCO_FOUND state. This state processes all detected ArUco markers and converts their pixel coordinates to millimeter coordinates relative to the chessboard reference. Args: context: RobotCalibrationContext containing all calibration state Returns: Next state to transition to

### `_log_frozen_camera_geometry`

```python
def _log_frozen_camera_geometry(context) -> None
```

## `axis_mapping.py`

Source: [src/engine/robot/calibration/robot_calibration/states/axis_mapping.py](../../../../../../src/engine/robot/calibration/robot_calibration/states/axis_mapping.py).

Imports (including optional/function-local imports; not a startup dependency list): `logging`, `numpy`, `src.engine.robot.calibration.robot_calibration.states.robot_calibration_states`, `src.engine.robot.calibration.robot_calibration.states.state_result`, `src.engine.robot.configuration`, `src.engine.robot.enums.axis`, `time`.

Module declarations (expressions are shown without evaluating them):

```python
wait_to_reach_position_flag = True
```

### `handle_axis_mapping_state`

```python
def handle_axis_mapping_state(system, calibration_vision, calibration_robot_controller, axis_mapping_config=None, stop_event=None)
```

### `get_marker_position`

```python
def get_marker_position(system, calibration_vision, MARKER_ID, MAX_ATTEMPTS, stop_event=None)
```

### `auto_calibrate_image_to_robot_mapping`

```python
def auto_calibrate_image_to_robot_mapping(system, calibration_vision, calibration_robot_controller, axis_mapping_config=None, stop_event=None)
```

## `chessboard_found_handler.py`

Source: [src/engine/robot/calibration/robot_calibration/states/chessboard_found_handler.py](../../../../../../src/engine/robot/calibration/robot_calibration/states/chessboard_found_handler.py).

Chessboard Found State Handler Handles the state when a chessboard has been successfully detected. This is a transition state that prepares for ArUco marker detection.

Imports (including optional/function-local imports; not a startup dependency list): `logging`, `src.engine.robot.calibration.robot_calibration.states.robot_calibration_states`.

### `handle_chessboard_found_state`

```python
def handle_chessboard_found_state(context) -> RobotCalibrationStates
```

Handle the CHESSBOARD_FOUND state. This is a simple transition state that confirms chessboard detection and prepares the vision_service to look for ArUco markers. Args: context: RobotCalibrationContext containing all calibration state Returns: Next state to transition to

## `compute_offsets_handler.py`

Source: [src/engine/robot/calibration/robot_calibration/states/compute_offsets_handler.py](../../../../../../src/engine/robot/calibration/robot_calibration/states/compute_offsets_handler.py).

Compute Offsets State Handler Handles the state where marker offsets relative to the image center are computed. These offsets are used to calculate robot movement targets for each marker.

Imports (including optional/function-local imports; not a startup dependency list): `logging`, `src.engine.robot.calibration.robot_calibration.logging`, `src.engine.robot.calibration.robot_calibration.states.error_handling`, `src.engine.robot.calibration.robot_calibration.states.robot_calibration_states`.

### `handle_compute_offsets_state`

```python
def handle_compute_offsets_state(context) -> RobotCalibrationStates
```

Handle the COMPUTE_OFFSETS state. This state calculates the offsets of all ArUco markers relative to the image center in millimeter coordinates. These offsets are used later to compute robot movements. Args: context: RobotCalibrationContext containing all calibration state Returns: Next state to transition to

## `error_handling.py`

Source: [src/engine/robot/calibration/robot_calibration/states/error_handling.py](../../../../../../src/engine/robot/calibration/robot_calibration/states/error_handling.py).

Imports (including optional/function-local imports; not a startup dependency list): `logging`, `src.engine.robot.calibration.robot_calibration.states.fallback_targets`, `src.engine.robot.calibration.robot_calibration.states.robot_calibration_states`.

### `set_calibration_error`

```python
def set_calibration_error(context, message: str, *, log_level: str='error') -> str
```

### `fail_calibration`

```python
def fail_calibration(context, message: str, *, log_level: str='error') -> RobotCalibrationStates
```

### `build_error_notification`

```python
def build_error_notification(context) -> dict
```

## `fallback_targets.py`

Source: [src/engine/robot/calibration/robot_calibration/states/fallback_targets.py](../../../../../../src/engine/robot/calibration/robot_calibration/states/fallback_targets.py).

Imports (including optional/function-local imports; not a startup dependency list): `logging`.

### `get_target_marker_ids`

```python
def get_target_marker_ids(context) -> list[int]
```

### `get_recovery_marker_id`

```python
def get_recovery_marker_id(context) -> int | None
```

### `record_known_unreachable_marker`

```python
def record_known_unreachable_marker(context, marker_id: int, reason: str) -> None
```

### `try_activate_fallback_target`

```python
def try_activate_fallback_target(context, failed_marker_id: int, reason: str) -> bool
```

### `get_marker_offset_mm`

```python
def get_marker_offset_mm(context, marker_id: int) -> tuple[float, float]
```

## `handle_height_sample_state.py`

Source: [src/engine/robot/calibration/robot_calibration/states/handle_height_sample_state.py](../../../../../../src/engine/robot/calibration/robot_calibration/states/handle_height_sample_state.py).

Imports (including optional/function-local imports; not a startup dependency list): `logging`, `src.engine.robot.calibration.robot_calibration.RobotCalibrationContext`, `src.engine.robot.calibration.robot_calibration.states.robot_calibration_states`.

### `handle_height_sample_state`

```python
def handle_height_sample_state(context: RobotCalibrationContext)
```

## `initializing.py`

Source: [src/engine/robot/calibration/robot_calibration/states/initializing.py](../../../../../../src/engine/robot/calibration/robot_calibration/states/initializing.py).

Imports (including optional/function-local imports; not a startup dependency list): `logging`, `src.engine.robot.calibration.robot_calibration.states.robot_calibration_states`, `src.engine.robot.calibration.robot_calibration.states.state_result`.

### `handle_initializing_state`

```python
def handle_initializing_state(frame_provider)
```

## `iterate_alignment.py`

Source: [src/engine/robot/calibration/robot_calibration/states/iterate_alignment.py](../../../../../../src/engine/robot/calibration/robot_calibration/states/iterate_alignment.py).

Imports (including optional/function-local imports; not a startup dependency list): `logging`, `numpy`, `src.engine.robot.calibration.robot_calibration.live_feed`, `src.engine.robot.calibration.robot_calibration.logging`, `src.engine.robot.calibration.robot_calibration.ppm_utils`, `src.engine.robot.calibration.robot_calibration.states.error_handling`, `src.engine.robot.calibration.robot_calibration.states.fallback_targets`, `src.engine.robot.calibration.robot_calibration.states.robot_calibration_states`, `src.engine.robot.calibration.robot_calibration.tcp_offset_capture`, `time`.

Module declarations (expressions are shown without evaluating them):

```python
wait_to_reach_position = True
```

### `_get_marker_retry_state`

```python
def _get_marker_retry_state(context, marker_id: int) -> dict
```

### `_reset_marker_retry_state`

```python
def _reset_marker_retry_state(context, marker_id: int) -> dict
```

### `_capture_marker_offsets_px`

```python
def _capture_marker_offsets_px(context, marker_id: int, sample_count: int, image_center_px: tuple[int, int])
```

### `_verify_alignment_after_settle`

```python
def _verify_alignment_after_settle(context, marker_id: int, alignment_threshold_mm: float, image_center_px: tuple[int, int], new_ppm: float)
```

### `_get_radial_iterative_damping`

```python
def _get_radial_iterative_damping(context, marker_id: int, iteration_count: int) -> float
```

### `_should_verify_stable_near_target`

```python
def _should_verify_stable_near_target(retry_state: dict, current_error_mm: float, alignment_threshold_mm: float) -> bool
```

Avoid noisy micro-moves without relaxing the acceptance threshold. A stable cluster just outside the threshold is sent to the existing strict verification path. Strict verification must still satisfy the original threshold before the marker is accepted.

### `_finish_verified_alignment`

```python
def _finish_verified_alignment(context, marker_id: int, verification_frame, verify_error_mm: float, new_ppm: float) -> RobotCalibrationStates
```

### `handle_iterate_alignment_state`

```python
def handle_iterate_alignment_state(context) -> RobotCalibrationStates
```

### `_format_point`

```python
def _format_point(point) -> str
```

## `looking_for_aruco_markers_handler.py`

Source: [src/engine/robot/calibration/robot_calibration/states/looking_for_aruco_markers_handler.py](../../../../../../src/engine/robot/calibration/robot_calibration/states/looking_for_aruco_markers_handler.py).

Looking for ArUco Markers State Handler Handles the state where the vision_service is looking for all required ArUco markers in the camera feed to proceed with calibration.

Imports (including optional/function-local imports; not a startup dependency list): `collections`, `logging`, `numpy`, `src.engine.robot.calibration.robot_calibration.live_feed`, `src.engine.robot.calibration.robot_calibration.states.robot_calibration_states`, `src.engine.robot.calibration.robot_calibration.target_planning`.

### `handle_looking_for_aruco_markers_state`

```python
def handle_looking_for_aruco_markers_state(context) -> RobotCalibrationStates
```

Handle the LOOKING_FOR_ARUCO_MARKERS state. This state captures frames and looks for all required ArUco markers to proceed with the calibration process. Args: context: RobotCalibrationContext containing all calibration state Returns: Next state to transition to

### `_collect_averaged_reference_pixels`

```python
def _collect_averaged_reference_pixels(context, n_frames: int) -> dict[int, np.ndarray]
```

Collect n_frames detections and replace marker_top_left_corners with the per-marker mean position. Only frames where a marker is actually detected contribute to its average, so a momentary miss does not corrupt the result.

## `looking_for_chessboard_handler.py`

Source: [src/engine/robot/calibration/robot_calibration/states/looking_for_chessboard_handler.py](../../../../../../src/engine/robot/calibration/robot_calibration/states/looking_for_chessboard_handler.py).

Looking for Chessboard State Handler Handles the state where the vision_service is looking for a chessboard pattern in the camera feed to establish the reference coordinate vision_service.

Imports (including optional/function-local imports; not a startup dependency list): `cv2`, `logging`, `numpy`, `os`, `src.engine.robot.calibration.robot_calibration.calibration_report`, `src.engine.robot.calibration.robot_calibration.live_feed`, `src.engine.robot.calibration.robot_calibration.logging`, `src.engine.robot.calibration.robot_calibration.overlay`, `src.engine.robot.calibration.robot_calibration.states.robot_calibration_states`.

### `handle_looking_for_chessboard_state`

```python
def handle_looking_for_chessboard_state(context) -> RobotCalibrationStates
```

Handle the LOOKING_FOR_CHESSBOARD state. This state captures frames and looks for a chessboard pattern to establish the reference coordinate vision_service and compute pixels-per-millimeter scale. Args: context: RobotCalibrationContext containing all calibration state Returns: Next state to transition to

### `_persist_initial_ppm`

```python
def _persist_initial_ppm(context, ppm: float) -> None
```

### `_persist_initial_ppm_artifact`

```python
def _persist_initial_ppm_artifact(context, ppm: float) -> None
```

### `_point_to_list`

```python
def _point_to_list(point) -> list[float] | None
```

### `_log_chessboard_pose`

```python
def _log_chessboard_pose(context) -> None
```

Compute and log chessboard pose via solvePnP for diagnostic purposes.

## `robot_calibration_states.py`

Source: [src/engine/robot/calibration/robot_calibration/states/robot_calibration_states.py](../../../../../../src/engine/robot/calibration/robot_calibration/states/robot_calibration_states.py).

Imports (including optional/function-local imports; not a startup dependency list): `enum`, `typing`.

### `RobotCalibrationStates`

```python
class RobotCalibrationStates(Enum):
```

Declared fields/defaults:

```python
INITIALIZING = auto()
AXIS_MAPPING = auto()
LOOKING_FOR_CHESSBOARD = auto()
CHESSBOARD_FOUND = auto()
ALIGN_TO_CHESSBOARD_CENTER = auto()
LOOKING_FOR_ARUCO_MARKERS = auto()
ALL_ARUCO_FOUND = auto()
COMPUTE_OFFSETS = auto()
ALIGN_ROBOT = auto()
ITERATE_ALIGNMENT = auto()
CAPTURE_TCP_OFFSET = auto()
SAMPLE_HEIGHT = auto()
DONE = auto()
ERROR = auto()
CANCELLED = auto()
```

### `RobotCalibrationTransitionRules`

```python
class RobotCalibrationTransitionRules:
```

Transition rules for robot calibration process. These rules define the valid state transitions for robot calibration operations.

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
@staticmethod
def get_calibration_transition_rules() -> Dict[RobotCalibrationStates, Set[RobotCalibrationStates]]
```

Get the complete transition rules for robot calibration operations. Returns: Dict mapping calibration states to their valid transition targets

## `state_result.py`

Source: [src/engine/robot/calibration/robot_calibration/states/state_result.py](../../../../../../src/engine/robot/calibration/robot_calibration/states/state_result.py).

Imports (including optional/function-local imports; not a startup dependency list): `src.engine.robot.calibration.robot_calibration.states.robot_calibration_states`.

### `StateResult`

```python
class StateResult:
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, success: bool, message: str='', data: dict=None, next_state: RobotCalibrationStates=None)
```

## `tcp_offset_state.py`

Source: [src/engine/robot/calibration/robot_calibration/states/tcp_offset_state.py](../../../../../../src/engine/robot/calibration/robot_calibration/states/tcp_offset_state.py).

Imports (including optional/function-local imports; not a startup dependency list): `logging`, `src.engine.robot.calibration.robot_calibration.states.robot_calibration_states`, `src.engine.robot.calibration.robot_calibration.tcp_offset_capture`.

### `handle_capture_tcp_offset_state`

```python
def handle_capture_tcp_offset_state(context) -> RobotCalibrationStates
```

## `terminal_states.py`

Source: [src/engine/robot/calibration/robot_calibration/states/terminal_states.py](../../../../../../src/engine/robot/calibration/robot_calibration/states/terminal_states.py).

Imports (including optional/function-local imports; not a startup dependency list): `logging`, `src.engine.robot.calibration.robot_calibration.states.error_handling`, `src.engine.robot.calibration.robot_calibration.states.fallback_targets`, `src.engine.robot.calibration.robot_calibration.states.robot_calibration_states`, `src.engine.robot.calibration.robot_calibration.tcp_offset_capture`, `traceback`.

### `handle_done_state`

```python
def handle_done_state(context) -> RobotCalibrationStates
```

### `handle_error_state`

```python
def handle_error_state(context) -> RobotCalibrationStates
```
