# Module reference: `tests/engine/robot`

[Package guide](README.md) · [Complete source index](../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [test_camera_tcp_offset_calibration_service.py](#test_camera_tcp_offset_calibration_servicepy)
- [test_motion_sequence_commands.py](#test_motion_sequence_commandspy)
- [test_motion_service.py](#test_motion_servicepy)
- [test_navigation_service.py](#test_navigation_servicepy)
- [test_per_area_coordinate_calibration.py](#test_per_area_coordinate_calibrationpy)
- [test_relative_tool_calibration_service.py](#test_relative_tool_calibration_servicepy)
- [test_robot_calibration_service.py](#test_robot_calibration_servicepy)
- [test_robot_client_adapters.py](#test_robot_client_adapterspy)
- [test_robot_service.py](#test_robot_servicepy)
- [test_robot_state_manager.py](#test_robot_state_managerpy)
- [test_robot_state_publisher.py](#test_robot_state_publisherpy)
- [test_robot_state_snapshot.py](#test_robot_state_snapshotpy)
- [test_ros2_bridge_joint_state_guard.py](#test_ros2_bridge_joint_state_guardpy)
- [test_ros2_bridge_motion_coordinator.py](#test_ros2_bridge_motion_coordinatorpy)
- [test_ros2_bridge_motion_harness.py](#test_ros2_bridge_motion_harnesspy)
- [test_ros2_bridge_planner_context.py](#test_ros2_bridge_planner_contextpy)
- [test_ros2_bridge_planner_support_service.py](#test_ros2_bridge_planner_support_servicepy)
- [test_ros2_bridge_robot_state_store.py](#test_ros2_bridge_robot_state_storepy)
- [test_ros2_bridge_trajectory_executor.py](#test_ros2_bridge_trajectory_executorpy)
- [test_ros2_bridge_trajectory_optimizer.py](#test_ros2_bridge_trajectory_optimizerpy)
- [test_ros_tool_registry_client.py](#test_ros_tool_registry_clientpy)
- [test_safety_checker.py](#test_safety_checkerpy)
- [test_target_point_geometry.py](#test_target_point_geometrypy)
- [test_tool_changer.py](#test_tool_changerpy)
- [test_tool_manager_sequences.py](#test_tool_manager_sequencespy)
- [test_tool_tcp_calibration_service.py](#test_tool_tcp_calibration_servicepy)
- [test_tool_tcp_pivot_solver.py](#test_tool_tcp_pivot_solverpy)

## `__init__.py`

Source: [tests/engine/robot/__init__.py](../../../../tests/engine/robot/__init__.py).

No top-level functions, classes or public value declarations; inspect the source for imports or entry-point statements.

## `test_camera_tcp_offset_calibration_service.py`

Source: [tests/engine/robot/test_camera_tcp_offset_calibration_service.py](../../../../tests/engine/robot/test_camera_tcp_offset_calibration_service.py).

Imports (including optional/function-local imports; not a startup dependency list): `numpy`, `pathlib`, `src.engine.robot.calibration.camera_tcp_offset_calibration_service`, `src.engine.robot.configuration`, `src.engine.robot.enums.axis`, `tempfile`, `unittest`, `unittest.mock`.

### `_FakeVisionService`

```python
class _FakeVisionService:
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, matrix_path: str, detections: list[tuple[float, float]])
```

```python
def get_latest_frame(self)
```

```python
def detect_aruco_markers(self, image)
```

```python
def get_camera_width(self) -> int
```

```python
def get_camera_height(self) -> int
```

### `_FakeRobotService`

```python
class _FakeRobotService:
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self)
```

```python
def get_current_position(self) -> list
```

```python
def move_ptp(self, position, tool, user, velocity, acceleration, wait_to_reach=False) -> bool
```

```python
def stop_motion(self) -> bool
```

### `_FakeNavigationService`

```python
class _FakeNavigationService:
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self)
```

```python
def move_to_calibration_position(self, wait_cancelled=None) -> bool
```

### `_FakeSettingsService`

```python
class _FakeSettingsService:
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self)
```

```python
def get(self, name)
```

```python
def save(self, name, settings) -> None
```

### `TestCameraTcpOffsetCalibrationService`

```python
class TestCameraTcpOffsetCalibrationService(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_post_solve_verification_persists_measured_angle_residuals(self)
```

```python
def test_calibrate_solves_and_saves_rotating_local_offset(self)
```

```python
def test_axis_mapping_prefers_tcp_marker_id_before_axis_mapping_marker(self)
```

```python
def test_axis_mapping_falls_back_to_configured_axis_marker(self)
```

```python
def test_calibrate_rejects_high_sample_spread_before_saving(self)
```

```python
def test_recenter_noise_floor_tracks_axis_mapping_pixel_scale(self)
```

```python
def test_near_target_recenter_move_uses_lower_gain(self)
```

## `test_motion_sequence_commands.py`

Source: [tests/engine/robot/test_motion_sequence_commands.py](../../../../tests/engine/robot/test_motion_sequence_commands.py).

Imports (including optional/function-local imports; not a startup dependency list): `math`, `src.engine.robot.motion_sequence`, `unittest`.

### `TestOrderedMotionCommands`

```python
class TestOrderedMotionCommands(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_serializes_position_and_path_commands_to_existing_wire_schema(self)
```

```python
def test_serializes_joint6_unwind_command(self)
```

```python
def test_rejects_raw_motion_type_strings(self)
```

```python
def test_rejects_invalid_position_and_path_shapes(self)
```

```python
def test_rejects_non_finite_motion_values(self)
```

```python
def test_input_serializer_accepts_typed_commands(self)
```

```python
def test_serializer_rejects_raw_dictionary_commands(self)
```

## `test_motion_service.py`

Source: [tests/engine/robot/test_motion_service.py](../../../../tests/engine/robot/test_motion_service.py).

Imports (including optional/function-local imports; not a startup dependency list): `src.engine.robot.enums.axis`, `src.engine.robot.motion_sequence`, `src.engine.robot.safety`, `src.engine.robot.services.motion_service`, `time`, `unittest`, `unittest.mock`.

### `TestMotionService`

```python
class TestMotionService(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def setUp(self)
```

```python
def test_move_ptp_success(self)
```

```python
def test_move_ptp_uses_non_blocking_robot_call_when_not_waiting(self)
```

```python
def test_move_ptp_accepts_queued_result(self)
```

```python
def test_move_ptp_blocked_by_safety(self)
```

```python
def test_move_ptp_robot_error_code_returns_false(self)
```

```python
def test_move_ptp_exception_returns_false(self)
```

```python
def test_move_linear_success(self)
```

```python
def test_move_linear_uses_non_blocking_robot_call_when_not_waiting(self)
```

```python
def test_move_linear_accepts_queued_result(self)
```

```python
def test_move_linear_blocked_by_safety(self)
```

```python
def test_move_linear_recovery_can_explicitly_bypass_platform_safety_limits(self)
```

```python
def test_move_linear_passes_blend_radius(self)
```

```python
def test_move_linear_exception_returns_false(self)
```

```python
def test_planar_corridor_allows_bounded_positive_z_transit_without_passage_lid(self)
```

```python
def test_fast_linear_blocks_target_outside_platform_safety_limits(self)
```

```python
def test_subzero_fast_linear_retract_anchors_non_z_axes_to_fresh_pose(self)
```

```python
def test_authorized_fast_linear_retract_accepts_positive_start_z(self)
```

```python
def test_fast_linear_retract_uses_one_pose_sample_near_zero(self)
```

```python
def test_regular_linear_move_below_zero_is_blocked(self)
```

```python
def test_ptp_move_below_zero_is_blocked(self)
```

```python
def test_regular_move_cannot_escape_from_sub_zero_pose(self)
```

```python
def test_registered_corridor_allows_bounded_sub_zero_linear_move(self)
```

```python
def test_corridor_rejects_ptp_by_not_exposing_a_ptp_corridor_operation(self)
```

```python
def test_corridor_rejects_target_outside_xy_tunnel(self)
```

```python
def test_corridor_allows_linear_retract_back_above_zero(self)
```

```python
def test_servo_jog_is_stopped_when_live_pose_reaches_zero_floor(self)
```

```python
def test_bounded_subzero_servo_descent_bypasses_generic_floor_supervisor(self)
```

```python
def test_pickup_retract_settle_may_cross_floor_from_positive_start(self)
```

```python
def test_pickup_collision_override_does_not_apply_recovery_speed_cap(self)
```

```python
def test_recovery_step_allows_pure_upward_move_while_target_remains_subzero(self)
```

```python
def test_recovery_step_rejects_lateral_subzero_move(self)
```

```python
def test_recovery_step_rejects_downward_subzero_move(self)
```

```python
def test_general_collision_recovery_keeps_workspace_checks_and_reaches_driver(self)
```

```python
def test_move_sequence_success(self)
```

```python
def test_move_sequence_blocks_on_safety_violation(self)
```

```python
def test_start_jog_delegates_to_robot(self)
```

```python
def test_start_jog_exception_returns_minus_one(self)
```

```python
def test_stop_motion_success(self)
```

```python
def test_stop_motion_retries_until_success(self)
```

```python
def test_stop_motion_exception_returns_false(self)
```

```python
def test_get_current_position_delegates_to_robot(self)
```

```python
def test_wait_for_position_returns_true_when_within_threshold(self)
```

```python
def test_wait_for_position_default_accepts_ros2_controller_completion_envelope(self)
```

```python
def test_wait_for_position_returns_false_on_timeout(self)
```

```python
def test_wait_for_position_returns_false_when_cancelled(self)
```

```python
def test_wait_for_position_waits_for_orientation_when_target_contains_rpy(self)
```

```python
def test_wait_for_position_accepts_orientation_when_within_wrapped_threshold(self)
```

```python
def test_wait_for_position_does_not_accept_one_transient_target_sample(self)
```

## `test_navigation_service.py`

Source: [tests/engine/robot/test_navigation_service.py](../../../../tests/engine/robot/test_navigation_service.py).

Imports (including optional/function-local imports; not a startup dependency list): `src.engine.common_settings_ids`, `src.engine.robot.configuration`, `src.engine.robot.features.navigation_service`, `unittest`, `unittest.mock`.

### `_Settings`

```python
class _Settings:
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, group: MovementGroup)
```

```python
def get(self, key)
```

### `TestNavigationService`

```python
class TestNavigationService(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_move_to_group_uses_ptp_by_default(self)
```

```python
def test_move_to_group_uses_configured_linear_type(self)
```

```python
def test_move_to_position_uses_group_motion_type(self)
```

```python
def test_move_to_group_allows_motion_type_and_blend_override(self)
```

```python
def test_move_to_group_allows_fast_lin_override(self)
```

### `TestMovementGroupMotionType`

```python
class TestMovementGroupMotionType(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_from_dict_defaults_to_ptp_and_serializes_motion_type(self)
```

```python
def test_from_dict_preserves_linear_motion_type(self)
```

```python
def test_from_dict_preserves_fast_lin_motion_type(self)
```

## `test_per_area_coordinate_calibration.py`

Source: [tests/engine/robot/test_per_area_coordinate_calibration.py](../../../../tests/engine/robot/test_per_area_coordinate_calibration.py).

Imports (including optional/function-local imports; not a startup dependency list): `src.engine.robot.configuration.robot_settings`, `src.engine.robot.plane_pose_mapper`, `src.engine.robot.targeting.end_effector_point`, `src.engine.robot.targeting.point_registry`, `src.engine.robot.targeting.remote_tcp_settings`, `src.engine.robot.targeting.target_frame`, `src.engine.robot.targeting.targeting_settings`, `src.engine.robot.targeting.vision_pose_request`, `src.engine.robot.targeting.vision_target_resolver`, `src.engine.vision.calibration_vision_settings`, `src.robot_systems.base_robot_system`, `src.shared_contracts.declarations`, `types`, `unittest`, `unittest.mock`.

### `_Transformer`

```python
class _Transformer:
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, x_offset=0.0)
```

```python
def transform(self, x, y)
```

```python
def is_available(self)
```

```python
def reload(self)
```

```python
def transform_to_tcp(self, x, y)
```

```python
def inverse_transform(self, x, y)
```

### `_request`

```python
def _request()
```

### `_RoutingSystem`

```python
class _RoutingSystem(BaseRobotSystem):
```

Declared fields/defaults:

```python
work_areas = [WorkAreaDefinition('paint', 'Paint', '#000000'), WorkAreaDefinition('orphan', 'Orphan', '#000000')]
target_frames = [TargetFrameDefinition('calibration', work_area_id='paint')]
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def on_start(self)
```

```python
def on_stop(self)
```

### `TestPerAreaCoordinateCalibration`

```python
class TestPerAreaCoordinateCalibration(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def setUp(self)
```

```python
def test_manual_camera_to_tcp_offset_comes_from_targeting_tool_point(self)
```

```python
def test_automatic_camera_to_tcp_offset_uses_robot_config_result(self)
```

```python
def test_legacy_target_points_become_global_and_local_override_round_trips(self)
```

```python
def test_camera_tcp_area_calibration_preserves_global_values(self)
```

```python
def test_system_builds_area_registry_and_manual_tcp_from_local_points(self)
```

```python
def test_vision_resolver_selects_points_and_tcp_from_frame_area(self)
```

```python
def test_global_mode_preserves_existing_mapper(self)
```

```python
def test_local_profile_skips_mapper_when_referenced_to_target_frame(self)
```

```python
def test_explicit_global_profile_can_be_shared_by_an_area(self)
```

```python
def test_unassigned_area_fails_in_per_area_mode(self)
```

```python
def test_frame_lookup_is_case_and_whitespace_insensitive(self)
```

```python
def test_custom_global_reference_frame_can_be_reused(self)
```

```python
def test_unused_incomplete_profile_does_not_block_assigned_global_profile(self)
```

```python
def test_legacy_global_profile_definition_is_ignored(self)
```

```python
def test_assignment_requires_a_target_frame(self)
```

## `test_relative_tool_calibration_service.py`

Source: [tests/engine/robot/test_relative_tool_calibration_service.py](../../../../tests/engine/robot/test_relative_tool_calibration_service.py).

Imports (including optional/function-local imports; not a startup dependency list): `src.engine.robot.relative_tool_calibration_service`, `src.engine.robot.tool_activation_service`, `unittest`.

### `_Registry`

```python
class _Registry:
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self)
```

```python
def update_tool(self, tool_id, name, transform, *, persist, collision_profile=None)
```

### `_Activator`

```python
class _Activator:
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self)
```

```python
def set_active_tool(self, tool)
```

### `RelativeToolCalibrationServiceTests`

```python
class RelativeToolCalibrationServiceTests(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_solves_translation_from_same_contact_point(self)
```

```python
def test_requires_configured_sample_count(self)
```

```python
def test_activation_composes_local_offset_and_activates(self)
```

## `test_robot_calibration_service.py`

Source: [tests/engine/robot/test_robot_calibration_service.py](../../../../tests/engine/robot/test_robot_calibration_service.py).

Imports (including optional/function-local imports; not a startup dependency list): `src.engine.robot.calibration.robot_calibration.config_helpers`, `src.engine.robot.calibration.robot_calibration_service`, `types`, `unittest`, `unittest.mock`.

### `TestRobotCalibrationService`

```python
class TestRobotCalibrationService(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_run_calibration_refreshes_live_settings_before_building_pipeline(self)
```

```python
def test_run_calibration_refreshes_live_vision_board_settings_before_building_pipeline(self)
```

## `test_robot_client_adapters.py`

Source: [tests/engine/robot/test_robot_client_adapters.py](../../../../tests/engine/robot/test_robot_client_adapters.py).

Imports (including optional/function-local imports; not a startup dependency list): `asyncio`, `json`, `src.engine.robot.drivers.client_adapters`, `src.engine.robot.drivers.ros2_robot`, `src.engine.robot.motion_sequence`, `threading`, `unittest`, `unittest.mock`.

### `TestSensorWebSocketSession`

```python
class TestSensorWebSocketSession(unittest.IsolatedAsyncioTestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
async def test_incoming_status_frames_do_not_starve_sensor_send(self)
```

### `TestRobotClientAdapters`

```python
class TestRobotClientAdapters(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_conditional_status_ignores_uncorrelated_execution_snapshot(self)
```

```python
@patch('src.engine.robot.drivers.client_adapters.http_websocket.requests.get')
def test_init_sets_disconnected_state_when_bridge_is_unavailable(self, get_mock)
```

```python
@patch('src.engine.robot.drivers.client_adapters.http_websocket.requests.get')
def test_successful_health_check_marks_client_available(self, get_mock)
```

```python
@patch('src.engine.robot.drivers.client_adapters.http_websocket.requests.post')
@patch('src.engine.robot.drivers.client_adapters.http_websocket.requests.get')
def test_rejected_active_tool_is_available_to_state_reporting(self, get_mock, post_mock)
```

```python
@patch('src.engine.robot.drivers.client_adapters.http_websocket.requests.get')
def test_starting_health_check_reports_starting_state(self, get_mock)
```

```python
@patch('src.engine.robot.drivers.client_adapters.http_websocket.requests.post')
@patch('src.engine.robot.drivers.client_adapters.http_websocket.requests.get')
def test_stop_motion_treats_no_active_motion_as_benign(self, get_mock, post_mock)
```

```python
@patch('src.engine.robot.drivers.client_adapters.http_websocket.requests.post')
@patch('src.engine.robot.drivers.client_adapters.http_websocket.requests.get')
def test_stop_motion_returns_unconfirmed_code_when_stop_not_confirmed(self, get_mock, post_mock)
```

```python
@patch('src.engine.robot.drivers.client_adapters.http_websocket.requests.post')
@patch('src.engine.robot.drivers.client_adapters.http_websocket.requests.get')
def test_move_linear_sets_active_tool_before_motion(self, get_mock, post_mock)
```

```python
@patch('src.engine.robot.drivers.client_adapters.http_websocket.requests.get')
def test_current_position_failure_does_not_mark_client_available(self, get_mock)
```

```python
@patch('src.engine.robot.drivers.client_adapters.http_websocket.requests.post')
@patch('src.engine.robot.drivers.client_adapters.http_websocket.requests.get')
def test_blocking_ordered_chain_rejects_non_final_response(self, get_mock, post_mock)
```

```python
@patch('src.engine.robot.drivers.client_adapters.http_websocket.requests.post')
@patch('src.engine.robot.drivers.client_adapters.http_websocket.requests.get')
def test_prepared_start_mismatch_response_is_preserved(self, get_mock, post_mock)
```

```python
@patch('src.engine.robot.drivers.client_adapters.http_websocket.requests.post')
@patch('src.engine.robot.drivers.client_adapters.http_websocket.requests.get')
def test_controlled_stop_sends_optional_duration(self, get_mock, post_mock)
```

```python
@patch('src.engine.robot.drivers.client_adapters.http_websocket.requests.Session.get')
@patch('src.engine.robot.drivers.client_adapters.http_websocket.requests.get')
def test_partial_kinematics_snapshot_is_returned(self, get_mock, session_get_mock)
```

```python
def test_fake_client_factory_selects_fake_backend(self)
```

```python
def test_fake_client_updates_position_and_reports_execution_info(self)
```

```python
def test_fake_robot_exposes_state_snapshot_for_platform_polling(self)
```

```python
def test_ros2_robot_forwards_scoped_servo_collision_override(self)
```

```python
def test_ros2_robot_serializes_typed_ordered_commands_at_client_boundary(self)
```

```python
def test_health_check_error_logging_is_throttled_across_client_instances(self)
```

## `test_robot_service.py`

Source: [tests/engine/robot/test_robot_service.py](../../../../tests/engine/robot/test_robot_service.py).

Imports (including optional/function-local imports; not a startup dependency list): `src.engine.robot.enums.axis`, `src.engine.robot.motion_sequence`, `src.engine.robot.services.robot_service`, `unittest`, `unittest.mock`.

### `TestRobotService`

```python
class TestRobotService(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def setUp(self)
```

```python
def test_move_ptp_delegates_to_motion(self)
```

```python
def test_move_linear_delegates_to_motion(self)
```

```python
def test_move_sequence_delegates_to_motion(self)
```

```python
def test_start_jog_delegates_to_motion(self)
```

```python
def test_stop_motion_delegates_to_motion(self)
```

```python
def test_get_current_position_delegates_to_motion(self)
```

```python
def test_set_active_tool_delegates_and_refreshes_state(self)
```

```python
def test_set_active_tool_does_not_refresh_when_driver_rejects(self)
```

```python
def test_registry_reads_delegate_to_robot_driver(self)
```

```python
def test_enable_robot_delegates_to_robot(self)
```

```python
def test_disable_robot_delegates_to_robot(self)
```

```python
def test_get_current_velocity_from_state(self)
```

```python
def test_get_current_acceleration_from_state(self)
```

```python
def test_get_state_from_state(self)
```

```python
def test_connection_state_prefers_driver_transport_state(self)
```

```python
def test_connection_details_delegate_to_driver(self)
```

```python
def test_drive_status_delegates_to_driver(self)
```

```python
def test_get_state_topic_from_state(self)
```

```python
def test_tools_none_by_default(self)
```

```python
def test_tools_returns_injected_service(self)
```

```python
def test_stop_stops_state_monitoring(self)
```

## `test_robot_state_manager.py`

Source: [tests/engine/robot/test_robot_state_manager.py](../../../../tests/engine/robot/test_robot_state_manager.py).

Imports (including optional/function-local imports; not a startup dependency list): `src.engine.robot.services.robot_state_manager`, `src.engine.robot.services.robot_state_snapshot`, `time`, `unittest`, `unittest.mock`.

### `TestRobotStateManager`

```python
class TestRobotStateManager(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_initial_state(self)
```

```python
def test_state_topic_default(self)
```

```python
def test_state_topic_custom(self)
```

```python
def test_polling_updates_state(self)
```

```python
def test_start_monitoring_starts_thread(self)
```

```python
def test_start_monitoring_idempotent(self)
```

```python
def test_stop_monitoring_stops_thread(self)
```

```python
def test_publisher_called_with_snapshot(self)
```

```python
def test_no_publisher_does_not_crash(self)
```

```python
def test_build_snapshot_returns_current_state(self)
```

```python
def test_disconnected_robot_publishes_disconnected_state(self)
```

```python
def test_connection_lost_during_poll_publishes_disconnected_state(self)
```

```python
def test_starting_robot_publishes_starting_without_robot_reads(self)
```

```python
def test_poll_exception_does_not_stop_thread(self)
```

```python
def test_refresh_syncs_configured_tool_before_reading_position(self)
```

```python
def test_refresh_does_not_publish_position_when_tool_sync_fails(self)
```

```python
def test_tool_sync_failure_exposes_robot_rejection_to_readiness(self)
```

```python
def test_refresh_publishes_drive_not_ready_when_drive_status_blocks_motion(self)
```

```python
def test_refresh_retries_tool_sync_until_success(self)
```

## `test_robot_state_publisher.py`

Source: [tests/engine/robot/test_robot_state_publisher.py](../../../../tests/engine/robot/test_robot_state_publisher.py).

Imports (including optional/function-local imports; not a startup dependency list): `src.engine.robot.services.robot_state_publisher`, `src.engine.robot.services.robot_state_snapshot`, `src.shared_contracts.events.robot_events`, `unittest`, `unittest.mock`.

### `TestRobotStatePublisher`

```python
class TestRobotStatePublisher(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def setUp(self)
```

```python
def test_publishes_to_state_topic(self)
```

```python
def test_publishes_position(self)
```

```python
def test_publishes_velocity(self)
```

```python
def test_publishes_acceleration(self)
```

```python
def test_publishes_exactly_four_topics(self)
```

```python
def test_topic_constants_match(self)
```

## `test_robot_state_snapshot.py`

Source: [tests/engine/robot/test_robot_state_snapshot.py](../../../../tests/engine/robot/test_robot_state_snapshot.py).

Imports (including optional/function-local imports; not a startup dependency list): `src.engine.robot.services.robot_state_snapshot`, `unittest`.

### `TestRobotStateSnapshot`

```python
class TestRobotStateSnapshot(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_fields_set_correctly(self)
```

```python
def test_default_extra_is_empty(self)
```

```python
def test_frozen_raises_on_mutation(self)
```

```python
def test_with_extra_returns_new_snapshot(self)
```

```python
def test_with_extra_merges_existing_extra(self)
```

```python
def test_with_extra_preserves_original(self)
```

```python
def test_with_extra_preserves_other_fields(self)
```

## `test_ros2_bridge_joint_state_guard.py`

Source: [tests/engine/robot/test_ros2_bridge_joint_state_guard.py](../../../../tests/engine/robot/test_ros2_bridge_joint_state_guard.py).

Imports (including optional/function-local imports; not a startup dependency list): `motion.planning.single_target`, `motion.planning.trajectory`, `pathlib`, `sys`, `unittest`.

### `_FakeLogger`

```python
class _FakeLogger:
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self)
```

```python
def info(self, *args, **kwargs)
```

```python
def warning(self, *args, **kwargs)
```

```python
def error(self, message, *args, **kwargs)
```

### `_FakeRobotController`

```python
class _FakeRobotController:
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self)
```

```python
def force_safety_update(self)
```

```python
def get_logger(self)
```

### `TestRos2BridgeJointStateGuard`

```python
class TestRos2BridgeJointStateGuard(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_single_target_rejects_when_joint_state_missing(self)
```

```python
def test_path_rejects_when_joint_state_missing(self)
```

## `test_ros2_bridge_motion_coordinator.py`

Source: [tests/engine/robot/test_ros2_bridge_motion_coordinator.py](../../../../tests/engine/robot/test_ros2_bridge_motion_coordinator.py).

Imports (including optional/function-local imports; not a startup dependency list): `motion.execution.motion_coordinator`, `motion.execution.motion_queue`, `pathlib`, `sys`, `unittest`.

### `_FakeLogger`

```python
class _FakeLogger:
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def info(self, *args, **kwargs)
```

```python
def warning(self, *args, **kwargs)
```

```python
def error(self, *args, **kwargs)
```

### `_FakeNode`

```python
class _FakeNode:
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self)
```

```python
def get_logger(self)
```

### `_QueueableStrategy`

```python
class _QueueableStrategy:
```

Declared fields/defaults:

```python
queueable = True
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self)
```

```python
def execute(self, node)
```

### `_NonQueueableStrategy`

```python
class _NonQueueableStrategy:
```

Declared fields/defaults:

```python
queueable = False
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self)
```

```python
def execute(self, node)
```

### `TestRos2BridgeMotionCoordinator`

```python
class TestRos2BridgeMotionCoordinator(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def setUp(self)
```

```python
def test_execute_runs_immediately_when_idle(self)
```

```python
def test_execute_queues_queueable_strategy_when_busy(self)
```

```python
def test_execute_rejects_non_queueable_strategy_when_busy(self)
```

```python
def test_stop_motion_returns_no_active_motion_when_idle(self)
```

## `test_ros2_bridge_motion_harness.py`

Source: [tests/engine/robot/test_ros2_bridge_motion_harness.py](../../../../tests/engine/robot/test_ros2_bridge_motion_harness.py).

Imports (including optional/function-local imports; not a startup dependency list): `enums`, `motion.execution.motion_queue`, `pathlib`, `sys`, `unittest`, `unittest.mock`.

### `_FakeLogger`

```python
class _FakeLogger:
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def info(self, *args, **kwargs)
```

```python
def warning(self, *args, **kwargs)
```

```python
def error(self, *args, **kwargs)
```

### `_FakeQueue`

```python
class _FakeQueue:
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, wait_result=0)
```

```python
def wait_for_task(self, task_id, timeout_s, poll_interval_s=0.05)
```

```python
def get_status(self)
```

### `_FakeNode`

```python
class _FakeNode:
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self)
```

```python
def get_tool_transform(self, tool_id)
```

```python
def execute(self, strategy)
```

```python
def get_logger(self)
```

```python
def get_latest_data(self)
```

```python
def is_motion_active(self)
```

```python
def has_pending_motion(self)
```

```python
def send_cartesian_goal(self, *args, **kwargs)
```

### `TestRos2BridgeMotionHarness`

```python
class TestRos2BridgeMotionHarness(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_motion_queue_wait_for_task_returns_completed_result(self)
```

```python
def test_move_liner_blocking_waits_for_queued_task_completion(self)
```

```python
def test_execute_path_blocking_waits_for_queued_task_completion(self)
```

```python
def test_start_jog_rejects_when_motion_is_active(self)
```

```python
def test_start_jog_rejects_when_motion_is_queued(self)
```

```python
def test_start_jog_sends_non_queueable_goal_when_idle(self)
```

## `test_ros2_bridge_planner_context.py`

Source: [tests/engine/robot/test_ros2_bridge_planner_context.py](../../../../tests/engine/robot/test_ros2_bridge_planner_context.py).

Imports (including optional/function-local imports; not a startup dependency list): `motion.execution.motion_coordinator`, `motion.execution.motion_queue`, `motion.planning.planner_context`, `pathlib`, `status.robot_state_store`, `sys`, `unittest`.

### `_FakeLogger`

```python
class _FakeLogger:
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def info(self, *args, **kwargs)
```

```python
def warning(self, *args, **kwargs)
```

```python
def error(self, *args, **kwargs)
```

### `_FakeClock`

```python
class _FakeClock:
```

### `_FakeFuture`

```python
class _FakeFuture:
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, payload=None)
```

### `_FakeClient`

```python
class _FakeClient:
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self)
```

```python
def call_async(self, request)
```

```python
def wait_for_service(self, timeout_sec=1.0)
```

### `_FakeSafetyManager`

```python
class _FakeSafetyManager:
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self)
```

```python
def force_update(self)
```

```python
def check_position_safety(self, x, y, z)
```

### `_FakePlannerSupport`

```python
class _FakePlannerSupport:
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self)
```

```python
def get_fk_client(self)
```

```python
def get_ik_client(self)
```

```python
def get_state_validity_client(self)
```

### `_FakeNode`

```python
class _FakeNode:
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self)
```

```python
def get_logger(self)
```

```python
def get_clock(self)
```

```python
def create_client(self, *args, **kwargs)
```

### `TestRos2BridgePlannerContext`

```python
class TestRos2BridgePlannerContext(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def setUp(self)
```

```python
def test_proxies_motion_state(self)
```

```python
def test_proxies_state_store(self)
```

```python
def test_exposes_node_logger_clock_and_client_factory(self)
```

```python
def test_tracks_last_requested_delta_and_waypoints(self)
```

```python
def test_stages_and_consumes_pending_path(self)
```

```python
def test_exposes_queue_and_safety_helpers(self)
```

```python
def test_delegates_cached_clients_to_planner_support(self)
```

## `test_ros2_bridge_planner_support_service.py`

Source: [tests/engine/robot/test_ros2_bridge_planner_support_service.py](../../../../tests/engine/robot/test_ros2_bridge_planner_support_service.py).

Imports (including optional/function-local imports; not a startup dependency list): `motion.planning.planner_support_service`, `pathlib`, `sys`, `types`, `unittest`.

### `_FakeNode`

```python
class _FakeNode:
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self)
```

```python
def create_client(self, service_type, service_name)
```

### `TestRos2BridgePlannerSupportService`

```python
class TestRos2BridgePlannerSupportService(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_caches_fk_and_state_validity_clients(self)
```

## `test_ros2_bridge_robot_state_store.py`

Source: [tests/engine/robot/test_ros2_bridge_robot_state_store.py](../../../../tests/engine/robot/test_ros2_bridge_robot_state_store.py).

Imports (including optional/function-local imports; not a startup dependency list): `pathlib`, `status.robot_state_store`, `sys`, `unittest`.

### `TestRos2BridgeRobotStateStore`

```python
class TestRos2BridgeRobotStateStore(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_round_trips_prev_cartesian(self)
```

```python
def test_round_trips_current_joint_state(self)
```

```python
def test_latest_data_returns_copy(self)
```

## `test_ros2_bridge_trajectory_executor.py`

Source: [tests/engine/robot/test_ros2_bridge_trajectory_executor.py](../../../../tests/engine/robot/test_ros2_bridge_trajectory_executor.py).

Imports (including optional/function-local imports; not a startup dependency list): `motion.execution.motion_coordinator`, `motion.execution.motion_queue`, `motion.execution.trajectory_executor`, `pathlib`, `sys`, `types`, `unittest`.

### `_FakeLogger`

```python
class _FakeLogger:
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def info(self, *args, **kwargs)
```

```python
def warning(self, *args, **kwargs)
```

```python
def error(self, *args, **kwargs)
```

### `_FakeNode`

```python
class _FakeNode:
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self)
```

```python
def get_logger(self)
```

### `_FakeFuture`

```python
class _FakeFuture:
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, result)
```

```python
def result(self)
```

```python
def add_done_callback(self, cb)
```

### `_FakeControllerClient`

```python
class _FakeControllerClient:
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, send_future)
```

```python
def wait_for_server(self, timeout_sec=1.0)
```

```python
def send_goal_async(self, goal)
```

### `_QueueTask`

```python
class _QueueTask:
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self)
```

### `TestRos2BridgeTrajectoryExecutor`

```python
class TestRos2BridgeTrajectoryExecutor(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def setUp(self)
```

```python
def test_process_next_queued_task_executes_task(self)
```

```python
def test_controller_goal_result_marks_completion_and_drains_queue(self)
```

## `test_ros2_bridge_trajectory_optimizer.py`

Source: [tests/engine/robot/test_ros2_bridge_trajectory_optimizer.py](../../../../tests/engine/robot/test_ros2_bridge_trajectory_optimizer.py).

Imports (including optional/function-local imports; not a startup dependency list): `motion.execution.trajectory_optimizer`, `pathlib`, `sys`, `unittest`.

### `_FakeNode`

```python
class _FakeNode:
```

### `_FakeLogger`

```python
class _FakeLogger:
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self)
```

```python
def error(self, message)
```

### `TestRos2BridgeTrajectoryOptimizer`

```python
class TestRos2BridgeTrajectoryOptimizer(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_build_returns_totg_optimizer(self)
```

```python
def test_build_returns_ruckig_optimizer(self)
```

```python
def test_build_rejects_unknown_optimizer(self)
```

```python
def test_totg_optimizer_delegates_to_totg_function(self)
```

```python
def test_ruckig_optimizer_delegates_to_ruckig_function(self)
```

```python
def test_build_logs_and_falls_back_when_requested(self)
```

## `test_ros_tool_registry_client.py`

Source: [tests/engine/robot/test_ros_tool_registry_client.py](../../../../tests/engine/robot/test_ros_tool_registry_client.py).

Imports (including optional/function-local imports; not a startup dependency list): `src.engine.robot.calibration.ros_tool_registry_client`, `unittest`, `unittest.mock`.

### `_Response`

```python
class _Response:
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, payload: dict, status_code: int=200)
```

```python
def json(self)
```

### `TestRosToolRegistryClient`

```python
class TestRosToolRegistryClient(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
@patch('src.engine.robot.calibration.ros_tool_registry_client.requests.get')
def test_get_tool_registry_returns_payload(self, get)
```

```python
@patch('src.engine.robot.calibration.ros_tool_registry_client.requests.get')
def test_get_tool_registry_returns_none_on_http_error(self, get)
```

```python
@patch('src.engine.robot.calibration.ros_tool_registry_client.requests.post')
def test_update_tool_posts_transform_payload(self, post)
```

```python
@patch('src.engine.robot.calibration.ros_tool_registry_client.requests.post')
def test_update_tool_returns_server_error_message(self, post)
```

```python
@patch('src.engine.robot.calibration.ros_tool_registry_client.requests.post')
def test_update_tool_includes_collision_profile_when_supplied(self, post)
```

```python
@patch('src.engine.robot.calibration.ros_tool_registry_client.requests.post')
def test_update_tool_returns_network_error(self, post)
```

```python
@patch('src.engine.robot.calibration.ros_tool_registry_client.requests.get')
def test_get_current_flange_position_returns_pose(self, get)
```

```python
@patch('src.engine.robot.calibration.ros_tool_registry_client.requests.get')
def test_get_current_flange_position_rejects_bad_length(self, get)
```

## `test_safety_checker.py`

Source: [tests/engine/robot/test_safety_checker.py](../../../../tests/engine/robot/test_safety_checker.py).

Imports (including optional/function-local imports; not a startup dependency list): `src.engine.common_settings_ids`, `src.engine.robot.safety.safety_checker`, `unittest`, `unittest.mock`.

Module declarations (expressions are shown without evaluating them):

```python
settings_key = CommonSettingsID.ROBOT_CONFIG
```

### `TestSafetyChecker`

```python
class TestSafetyChecker(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def setUp(self)
```

```python
def test_no_settings_allows_any_position(self)
```

```python
def test_empty_position_blocked(self)
```

```python
def test_none_position_blocked(self)
```

```python
def test_position_too_short_blocked(self)
```

```python
def test_settings_without_limits_allows(self)
```

```python
def test_position_within_limits_allowed(self)
```

```python
def test_x_exceeds_max_blocked(self)
```

```python
def test_z_below_min_blocked(self)
```

```python
def test_settings_exception_fails_open(self)
```

## `test_target_point_geometry.py`

Source: [tests/engine/robot/test_target_point_geometry.py](../../../../tests/engine/robot/test_target_point_geometry.py).

Imports (including optional/function-local imports; not a startup dependency list): `src.engine.robot.targeting.end_effector_point`, `src.engine.robot.targeting.jog_frame_pose_resolver`, `src.engine.robot.targeting.target_point_geometry`, `src.engine.robot.targeting.vision_pose_request`, `src.engine.robot.targeting.vision_target_resolver`, `unittest`.

### `_Registry`

```python
class _Registry:
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def by_name(self, name)
```

```python
def names(self)
```

### `_NamedRegistry`

```python
class _NamedRegistry:
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def by_name(self, name)
```

```python
def names(self)
```

### `_Transformer`

```python
class _Transformer:
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
@staticmethod
def is_available()
```

```python
@staticmethod
def transform(_x, _y)
```

### `TestTargetPointGeometry`

```python
class TestTargetPointGeometry(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_rotation_residual_interpolates_only_inside_verified_range(self)
```

```python
def test_command_pose_adds_verified_rotation_residual(self)
```

```python
def test_resolver_applies_camera_base_residual_before_tool_offset(self)
```

```python
def test_command_xyz_keeps_legacy_flat_rz_result(self)
```

```python
def test_jog_ry_in_tilted_pose_keeps_selected_tool_point_fixed(self)
```

```python
def test_vision_resolver_uses_ry_for_tilted_target_offsets(self)
```

## `test_tool_changer.py`

Source: [tests/engine/robot/test_tool_changer.py](../../../../tests/engine/robot/test_tool_changer.py).

Imports (including optional/function-local imports; not a startup dependency list): `src.engine.robot.interfaces.tool_definition`, `src.engine.robot.tool_changer`, `unittest`.

Module declarations (expressions are shown without evaluating them):

```python
tools = [ToolDefinition(id=1, name='Tool1'), ToolDefinition(id=2, name='Tool2'), ToolDefinition(id=3, name='Tool3')]
```

### `TestToolChanger`

```python
class TestToolChanger(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_get_slot_id_by_tool_id_found(self)
```

```python
def test_get_slot_id_by_tool_id_not_found(self)
```

```python
def test_slot_not_occupied_initially(self)
```

```python
def test_set_slot_not_available_marks_occupied(self)
```

```python
def test_set_slot_available_clears_occupied(self)
```

```python
def test_get_occupied_slots_empty_initially(self)
```

```python
def test_get_occupied_slots_after_marking(self)
```

```python
def test_get_empty_slots_all_initially(self)
```

```python
def test_get_empty_slots_excludes_occupied(self)
```

```python
def test_multiple_slots_independent(self)
```

```python
def test_slot_exposes_taught_sequences(self)
```

## `test_tool_manager_sequences.py`

Source: [tests/engine/robot/test_tool_manager_sequences.py](../../../../tests/engine/robot/test_tool_manager_sequences.py).

Imports (including optional/function-local imports; not a startup dependency list): `src.engine.robot.interfaces.tool_definition`, `src.engine.robot.tool_changer`, `src.engine.robot.tool_manager`, `types`, `unittest`, `unittest.mock`.

### `ToolManagerSequenceTests`

```python
class ToolManagerSequenceTests(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_pickup_executes_taught_motion_and_activation_boundary(self)
```

```python
def test_operator_confirmation_fails_closed_without_callback(self)
```

## `test_tool_tcp_calibration_service.py`

Source: [tests/engine/robot/test_tool_tcp_calibration_service.py](../../../../tests/engine/robot/test_tool_tcp_calibration_service.py).

Imports (including optional/function-local imports; not a startup dependency list): `math`, `numpy`, `src.engine.robot.calibration.tool_tcp_calibration_data`, `src.engine.robot.calibration.tool_tcp_calibration_service`, `unittest`.

### `_rotation_matrix_xyz_degrees`

```python
def _rotation_matrix_xyz_degrees(rx: float, ry: float, rz: float) -> np.ndarray
```

### `_pose_for`

```python
def _pose_for(tool_offset_xyz: np.ndarray, pivot_point: np.ndarray, orientation: tuple[float, float, float]) -> list[float]
```

### `_FakeRobot`

```python
class _FakeRobot:
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, poses: list[list[float]] | None=None)
```

```python
def get_current_position(self)
```

```python
def get_current_flange_position(self)
```

```python
def stop_motion(self) -> bool
```

### `_FakeToolRegistry`

```python
class _FakeToolRegistry:
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, ok: bool=True, message: str='ok')
```

```python
def update_tool(self, tool_id, name, transform, *, persist)
```

### `TestToolTcpCalibrationService`

```python
class TestToolTcpCalibrationService(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_captures_solves_and_saves_tool_offset(self)
```

```python
def test_uses_explicit_flange_pose_provider_before_robot_service(self)
```

```python
def test_capture_requires_start(self)
```

```python
def test_save_requires_registry_client(self)
```

```python
def test_save_reports_registry_failure(self)
```

```python
def test_stop_marks_session_stopped_and_stops_robot(self)
```

## `test_tool_tcp_pivot_solver.py`

Source: [tests/engine/robot/test_tool_tcp_pivot_solver.py](../../../../tests/engine/robot/test_tool_tcp_pivot_solver.py).

Imports (including optional/function-local imports; not a startup dependency list): `math`, `numpy`, `src.engine.robot.calibration.tool_tcp_calibration_data`, `src.engine.robot.calibration.tool_tcp_pivot_solver`, `unittest`.

### `_rotation_matrix_xyz_degrees`

```python
def _rotation_matrix_xyz_degrees(rx: float, ry: float, rz: float) -> np.ndarray
```

### `_sample_for`

```python
def _sample_for(tool_offset_xyz: np.ndarray, pivot_point: np.ndarray, orientation: tuple[float, float, float], translation_noise: tuple[float, float, float]=(0.0, 0.0, 0.0)) -> ToolTcpSample
```

### `TestToolTcpPivotSolver`

```python
class TestToolTcpPivotSolver(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_solves_known_offset_from_noise_free_samples(self)
```

```python
def test_reports_residuals_for_noisy_samples(self)
```

```python
def test_rejects_insufficient_samples(self)
```

```python
def test_rejects_degenerate_orientation_set(self)
```

```python
def test_rejects_non_finite_pose_values(self)
```
