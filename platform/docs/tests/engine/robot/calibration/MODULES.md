# Module reference: `tests/engine/robot/calibration`

[Package guide](README.md) · [Complete source index](../../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [test_calibration_artifact_routing.py](#test_calibration_artifact_routingpy)
- [test_calibration_navigation_service.py](#test_calibration_navigation_servicepy)
- [test_calibration_refactor_modules.py](#test_calibration_refactor_modulespy)
- [test_calibration_state_handlers.py](#test_calibration_state_handlerspy)
- [test_calibration_vision.py](#test_calibration_visionpy)
- [test_camera_tcp_offset_calibration_service.py](#test_camera_tcp_offset_calibration_servicepy)
- [test_compute_offsets_handler.py](#test_compute_offsets_handlerpy)
- [test_online_navigation.py](#test_online_navigationpy)
- [test_robot_calibration_context.py](#test_robot_calibration_contextpy)
- [test_robot_calibration_controller.py](#test_robot_calibration_controllerpy)
- [test_tcp_offset_capture.py](#test_tcp_offset_capturepy)

## `__init__.py`

Source: [tests/engine/robot/calibration/__init__.py](../../../../../tests/engine/robot/calibration/__init__.py).

No top-level functions, classes or public value declarations; inspect the source for imports or entry-point statements.

## `test_calibration_artifact_routing.py`

Source: [tests/engine/robot/calibration/test_calibration_artifact_routing.py](../../../../../tests/engine/robot/calibration/test_calibration_artifact_routing.py).

Imports (including optional/function-local imports; not a startup dependency list): `pathlib`, `src.engine.common_settings_ids`, `src.engine.robot.calibration.service_builders`, `src.engine.vision.calibration_vision_settings`, `tempfile`, `types`, `unittest`, `unittest.mock`.

### `TestCalibrationArtifactRouting`

```python
class TestCalibrationArtifactRouting(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_intrinsic_calibration_remains_in_the_shared_camera_directory(self)
```

```python
def test_destination_is_frozen_for_the_calibration_session(self)
```

```python
def test_shared_global_profile_cannot_be_overwritten_as_an_area_target(self)
```

## `test_calibration_navigation_service.py`

Source: [tests/engine/robot/calibration/test_calibration_navigation_service.py](../../../../../tests/engine/robot/calibration/test_calibration_navigation_service.py).

Imports (including optional/function-local imports; not a startup dependency list): `src.engine.robot.calibration.calibration_navigation_service`, `unittest`, `unittest.mock`.

### `TestCalibrationNavigationService`

```python
class TestCalibrationNavigationService(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_move_to_calibration_position_runs_before_move_then_navigation(self)
```

```python
def test_move_to_calibration_position_propagates_before_move_errors(self)
```

```python
def test_dynamic_group_is_resolved_once_before_move_side_effects(self)
```

## `test_calibration_refactor_modules.py`

Source: [tests/engine/robot/calibration/test_calibration_refactor_modules.py](../../../../../tests/engine/robot/calibration/test_calibration_refactor_modules.py).

Imports (including optional/function-local imports; not a startup dependency list): `src.engine.robot.calibration.robot_calibration.RobotCalibrationContext`, `src.engine.robot.calibration.robot_calibration.live_feed`, `src.engine.robot.calibration.robot_calibration.model_fitting`, `src.engine.robot.calibration.robot_calibration.overlay`, `src.engine.robot.calibration.robot_calibration.overlay_renderer`, `src.engine.robot.calibration.robot_calibration.states.error_handling`, `src.engine.robot.calibration.robot_calibration.states.robot_calibration_states`, `threading`, `unittest`, `unittest.mock`.

### `TestCalibrationModelFitting`

```python
class TestCalibrationModelFitting(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_build_calibration_dataset_uses_partitioned_groups(self)
```

### `TestCalibrationErrorHandling`

```python
class TestCalibrationErrorHandling(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_fail_calibration_sets_error_and_returns_error_state(self)
```

```python
def test_build_error_notification_uses_grouped_state(self)
```

### `TestCalibrationVisualizationSeams`

```python
class TestCalibrationVisualizationSeams(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_draw_live_overlay_uses_injected_renderer(self)
```

```python
def test_show_live_feed_can_publish_without_visualization(self)
```

```python
def test_show_live_feed_returns_without_queueing_when_visualization_disabled(self)
```

## `test_calibration_state_handlers.py`

Source: [tests/engine/robot/calibration/test_calibration_state_handlers.py](../../../../../tests/engine/robot/calibration/test_calibration_state_handlers.py).

Tests for calibration state handlers in src/engine/robot/calibration/robot_calibration/states/ Each handler receives a context and returns a RobotCalibrationStates value. Tests verify: - stop_event is respected (returns CANCELLED, not ERROR) - normal happy/sad paths return correct next states

Imports (including optional/function-local imports; not a startup dependency list): `numpy`, `src.engine.robot.calibration.robot_calibration.RobotCalibrationContext`, `src.engine.robot.calibration.robot_calibration.overlay_renderer`, `src.engine.robot.calibration.robot_calibration.states.align_robot`, `src.engine.robot.calibration.robot_calibration.states.handle_height_sample_state`, `src.engine.robot.calibration.robot_calibration.states.iterate_alignment`, `src.engine.robot.calibration.robot_calibration.states.looking_for_aruco_markers_handler`, `src.engine.robot.calibration.robot_calibration.states.looking_for_chessboard_handler`, `src.engine.robot.calibration.robot_calibration.states.robot_calibration_states`, `src.engine.robot.calibration.robot_calibration.states.tcp_offset_state`, `src.engine.robot.calibration.robot_calibration.states.terminal_states`, `threading`, `unittest`, `unittest.mock`.

### `_make_context`

```python
def _make_context(**overrides)
```

### `TestLookingForChessboardHandler`

```python
class TestLookingForChessboardHandler(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_returns_cancelled_when_stop_event_set_before_call(self)
```

```python
def test_returns_cancelled_when_stop_event_set_while_waiting_for_frame(self)
```

```python
def test_chessboard_found_returns_chessboard_found(self)
```

```python
def test_chessboard_not_found_stays_in_looking(self)
```

### `TestLookingForArucoMarkersHandler`

```python
class TestLookingForArucoMarkersHandler(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_returns_cancelled_when_stop_event_set_before_call(self)
```

```python
def test_returns_cancelled_when_stop_event_set_while_waiting_for_frame(self)
```

```python
def test_all_markers_found_returns_all_aruco_found(self)
```

```python
def test_markers_not_found_stays_in_looking(self)
```

### `TestAlignRobotHandler`

```python
class TestAlignRobotHandler(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_returns_cancelled_when_stop_event_set_at_entry(self)
```

```python
def test_move_success_returns_iterate_alignment(self)
```

```python
def test_move_failure_returns_error(self)
```

```python
def test_skips_duplicate_stages_when_approach_and_target_z_match(self)
```

```python
def test_target_uses_calibration_orientation_not_live_readback(self)
```

```python
def test_returns_cancelled_when_stop_event_fires_in_post_move_wait(self)
```

### `TestIterateAlignmentHandler`

```python
class TestIterateAlignmentHandler(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_stable_near_target_errors_trigger_verification_candidate(self)
```

```python
def test_verification_rejection_forces_one_correction(self)
```

```python
def test_unstable_near_target_errors_do_not_trigger_verification(self)
```

```python
def test_returns_cancelled_when_stop_event_set_before_frame(self)
```

```python
def test_returns_cancelled_when_stop_event_set_while_waiting_for_frame(self)
```

```python
def test_returns_error_on_max_iterations_exceeded(self)
```

```python
def test_max_iterations_triggers_local_recovery_nudge(self)
```

```python
def test_marker_not_found_stays_in_iterate(self)
```

```python
def test_stop_event_in_stability_wait_returns_cancelled(self)
```

Stop event fires during the post-move stability wait (non-aligned path).

```python
def test_alignment_success_returns_sample_height(self)
```

```python
def test_acceptable_alignment_gets_two_bounded_improvement_attempts(self)
```

```python
def test_alignment_success_returns_capture_tcp_offset_when_enabled(self)
```

```python
def test_alignment_success_skips_capture_when_max_markers_already_reached(self)
```

```python
def test_alignment_not_reached_stays_in_iterate(self)
```

```python
def test_iterative_move_pins_calibration_orientation_and_target_z(self)
```

### `TestDoneHandler`

```python
class TestDoneHandler(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_advances_to_next_marker(self)
```

```python
def test_stays_done_when_all_markers_processed(self)
```

### `TestCaptureTcpOffsetHandler`

```python
class TestCaptureTcpOffsetHandler(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
@patch('src.engine.robot.calibration.robot_calibration.states.tcp_offset_state.capture_tcp_offset_for_current_marker')
def test_returns_sample_height_when_capture_succeeds(self, capture_mock)
```

```python
@patch('src.engine.robot.calibration.robot_calibration.states.tcp_offset_state.capture_tcp_offset_for_current_marker')
def test_returns_error_when_capture_fails(self, capture_mock)
```

```python
@patch('src.engine.robot.calibration.robot_calibration.states.tcp_offset_state.capture_tcp_offset_for_current_marker')
def test_skips_capture_when_max_markers_already_captured(self, capture_mock)
```

### `TestHeightSampleHandler`

```python
class TestHeightSampleHandler(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_skips_height_measurement_when_disabled(self)
```

```python
def test_samples_height_when_enabled(self)
```

## `test_calibration_vision.py`

Source: [tests/engine/robot/calibration/test_calibration_vision.py](../../../../../tests/engine/robot/calibration/test_calibration_vision.py).

Imports (including optional/function-local imports; not a startup dependency list): `cv2`, `numpy`, `src.engine.robot.calibration.robot_calibration.CalibrationVision`, `unittest`, `unittest.mock`.

### `TestCalibrationVision`

```python
class TestCalibrationVision(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_uses_4x4_250_as_calibration_fallback_dictionary(self)
```

```python
def test_detect_specific_marker_returns_detected_marker(self)
```

## `test_camera_tcp_offset_calibration_service.py`

Source: [tests/engine/robot/calibration/test_camera_tcp_offset_calibration_service.py](../../../../../tests/engine/robot/calibration/test_camera_tcp_offset_calibration_service.py).

Imports (including optional/function-local imports; not a startup dependency list): `src.engine.robot.calibration.camera_tcp_offset_calibration_service`, `unittest`, `unittest.mock`.

### `TestCameraTcpOffsetCalibrationMotion`

```python
class TestCameraTcpOffsetCalibrationMotion(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_linear_move_uses_unblended_linear_motion_and_waits(self)
```

## `test_compute_offsets_handler.py`

Source: [tests/engine/robot/calibration/test_compute_offsets_handler.py](../../../../../tests/engine/robot/calibration/test_compute_offsets_handler.py).

Imports (including optional/function-local imports; not a startup dependency list): `numpy`, `src.engine.robot.calibration.robot_calibration.RobotCalibrationContext`, `src.engine.robot.calibration.robot_calibration.states.compute_offsets_handler`, `src.engine.robot.calibration.robot_calibration.states.robot_calibration_states`, `unittest`, `unittest.mock`.

### `TestComputeOffsetsHandler`

```python
class TestComputeOffsetsHandler(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_offsets_are_scaled_for_target_height(self)
```

## `test_online_navigation.py`

Source: [tests/engine/robot/calibration/test_online_navigation.py](../../../../../tests/engine/robot/calibration/test_online_navigation.py).

Imports (including optional/function-local imports; not a startup dependency list): `src.engine.robot.calibration.robot_calibration.online_navigation`, `types`, `unittest`, `unittest.mock`.

### `OnlineNavigationTests`

```python
class OnlineNavigationTests(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_predicts_from_four_spread_training_samples(self)
```

```python
def test_requires_four_training_samples(self)
```

## `test_robot_calibration_context.py`

Source: [tests/engine/robot/calibration/test_robot_calibration_context.py](../../../../../tests/engine/robot/calibration/test_robot_calibration_context.py).

Tests for src/engine/robot/calibration/robot_calibration/RobotCalibrationContext.y_pixels Covers stop_event lifecycle, reset behaviour, and flush_camera_buffer.

Imports (including optional/function-local imports; not a startup dependency list): `src.engine.robot.calibration.robot_calibration.RobotCalibrationContext`, `threading`, `unittest`, `unittest.mock`.

### `TestRobotCalibrationContextStopEvent`

```python
class TestRobotCalibrationContextStopEvent(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_stop_event_initially_clear(self)
```

```python
def test_stop_event_is_threading_event(self)
```

```python
def test_reset_creates_fresh_stop_event(self)
```

```python
def test_reset_clears_stop_event(self)
```

### `TestRobotCalibrationContextFlushCamera`

```python
class TestRobotCalibrationContextFlushCamera(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_flush_camera_buffer_calls_get_frame_min_flush_times(self)
```

```python
def test_flush_camera_buffer_without_vision_service_preserves_none(self)
```

```python
def test_flush_uses_min_camera_flush_value(self)
```

### `TestRobotCalibrationContextReset`

```python
class TestRobotCalibrationContextReset(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_reset_clears_robot_positions(self)
```

```python
def test_reset_clears_iteration_count(self)
```

```python
def test_reset_clears_error_message(self)
```

```python
def test_legacy_properties_proxy_to_grouped_views(self)
```

```python
def test_grouped_views_are_initialized_with_mutable_containers(self)
```

## `test_robot_calibration_controller.py`

Source: [tests/engine/robot/calibration/test_robot_calibration_controller.py](../../../../../tests/engine/robot/calibration/test_robot_calibration_controller.py).

Imports (including optional/function-local imports; not a startup dependency list): `src.engine.robot.calibration.robot_calibration.robot_controller`, `unittest`, `unittest.mock`.

### `_AdaptiveConfig`

```python
class _AdaptiveConfig:
```

Declared fields/defaults:

```python
min_step_mm = 0.1
max_step_mm = 25.0
max_error_ref = 30.0
k = 2.0
derivative_scaling = 0.5
iterative_gain = 0.7
near_target_gain = 0.35
axis_deadband_mm = 0.2
axis_flip_scale_min = 0.2
```

### `TestCalibrationRobotController`

```python
class TestCalibrationRobotController(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_damps_axis_when_offset_sign_flips_near_target(self)
```

```python
def test_reset_derivative_state_clears_axis_history(self)
```

```python
def test_zeroes_axis_inside_deadband(self)
```

## `test_tcp_offset_capture.py`

Source: [tests/engine/robot/calibration/test_tcp_offset_capture.py](../../../../../tests/engine/robot/calibration/test_tcp_offset_capture.py).

Imports (including optional/function-local imports; not a startup dependency list): `dataclasses`, `src.engine.robot.calibration.robot_calibration.tcp_offset_capture`, `src.engine.robot.configuration.robot_settings`, `unittest`, `unittest.mock`.

### `TestFinalizeTcpOffsetCalibration`

```python
class TestFinalizeTcpOffsetCalibration(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_saves_mean_offset_when_sample_spread_is_acceptable(self)
```

```python
def test_saves_offset_to_selected_area_without_replacing_global(self)
```

```python
def test_rejects_result_when_sample_spread_is_too_high(self)
```

```python
def test_rejects_result_when_not_enough_samples_exist(self)
```

```python
def test_ignores_reference_samples_when_checking_sample_count(self)
```

### `TestCaptureTcpOffsetForCurrentMarker`

```python
class TestCaptureTcpOffsetForCurrentMarker(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_solves_consistent_local_offset_from_multiple_rotation_angles(self)
```

```python
def test_iterations_count_rotated_samples_after_reference_pose(self)
```

```python
def test_restores_reference_pose_when_sampling_fails_after_reference_alignment(self)
```
