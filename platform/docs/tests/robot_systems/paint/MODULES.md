# Module reference: `tests/robot_systems/paint`

[Package guide](README.md) · [Complete source index](../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [test_contour_matching_tester_wiring.py](#test_contour_matching_tester_wiringpy)
- [test_dropoff_motion_corridor.py](#test_dropoff_motion_corridorpy)
- [test_dryer_release_coordinator.py](#test_dryer_release_coordinatorpy)
- [test_fixed_magazine_pickup.py](#test_fixed_magazine_pickuppy)
- [test_adjustment/session.py](#test_incremental_adjustmentpy)
- [test_magazine_pickup_release_pose.py](#test_magazine_pickup_release_posepy)
- [test_magazine_release_pose.py](#test_magazine_release_posepy)
- [test_paint_adjustment.py](#test_paint_adjustmentpy)
- [test_paint_adjustment_service.py](#test_paint_adjustment_servicepy)
- [test_paint_contact_selection_execution.py](#test_paint_contact_selection_executionpy)
- [test_paint_contour_interpolation.py](#test_paint_contour_interpolationpy)
- [test_paint_cycle_runner.py](#test_paint_cycle_runnerpy)
- [test_paint_dashboard_mvc.py](#test_paint_dashboard_mvcpy)
- [test_paint_dashboard_view_ui.py](#test_paint_dashboard_view_uipy)
- [test_paint_execution_machine.py](#test_paint_execution_machinepy)
- [test_paint_execution_plane_strategies.py](#test_paint_execution_plane_strategiespy)
- [test_paint_geometry_and_config.py](#test_paint_geometry_and_configpy)
- [test_paint_head_availability_adapter.py](#test_paint_head_availability_adapterpy)
- [test_paint_head_device.py](#test_paint_head_devicepy)
- [test_paint_head_settings.py](#test_paint_head_settingspy)
- [test_paint_matching_service.py](#test_paint_matching_servicepy)
- [test_paint_motion_recipe_app.py](#test_paint_motion_recipe_apppy)
- [test_paint_navigation_and_targeting.py](#test_paint_navigation_and_targetingpy)
- [test_paint_pivot_projection.py](#test_paint_pivot_projectionpy)
- [test_paint_process_integration.py](#test_paint_process_integrationpy)
- [test_paint_process_lifecycle.py](#test_paint_process_lifecyclepy)
- [test_paint_process_settings_controller.py](#test_paint_process_settings_controllerpy)
- [test_paint_profiles.py](#test_paint_profilespy)
- [test_paint_runtime_services.py](#test_paint_runtime_servicespy)
- [test_paint_segment_selection.py](#test_paint_segment_selectionpy)
- [test_paint_support_modules.py](#test_paint_support_modulespy)
- [test_paint_system_integration.py](#test_paint_system_integrationpy)
- [test_paint_system_overrides.py](#test_paint_system_overridespy)
- [test_paint_timing.py](#test_paint_timingpy)
- [test_paint_typed_results.py](#test_paint_typed_resultspy)
- [test_paint_workpiece_editor_adapter.py](#test_paint_workpiece_editor_adapterpy)
- [test_paint_workpiece_path_executor.py](#test_paint_workpiece_path_executorpy)
- [test_paint_workpiece_preparation_service.py](#test_paint_workpiece_preparation_servicepy)
- [test_paint_workpiece_storage.py](#test_paint_workpiece_storagepy)
- [test_pickup_condition_wiring.py](#test_pickup_condition_wiringpy)
- [test_plate_layout_dropoff.py](#test_plate_layout_dropoffpy)
- [test_trajectory_export_result.py](#test_trajectory_export_resultpy)
- [test_tray_readiness.py](#test_tray_readinesspy)
- [test_unmatched_second_pass.py](#test_unmatched_second_passpy)
- [test_work_area_nesting.py](#test_work_area_nestingpy)
- [test_workpiece_destinations.py](#test_workpiece_destinationspy)

## `__init__.py`

Source: [tests/robot_systems/paint/__init__.py](../../../../tests/robot_systems/paint/__init__.py).

No top-level functions, classes or public value declarations; inspect the source for imports or entry-point statements.

## `test_contour_matching_tester_wiring.py`

Source: [tests/robot_systems/paint/test_contour_matching_tester_wiring.py](../../../../tests/robot_systems/paint/test_contour_matching_tester_wiring.py).

Imports (including optional/function-local imports; not a startup dependency list): `src.robot_systems.paint.paint_robot_system`, `unittest`.

### `TestContourMatchingTesterWiring`

```python
class TestContourMatchingTesterWiring(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_paint_exposes_matching_tester_in_tests_folder(self)
```

## `test_dropoff_motion_corridor.py`

Source: [tests/robot_systems/paint/test_dropoff_motion_corridor.py](../../../../tests/robot_systems/paint/test_dropoff_motion_corridor.py).

Imports (including optional/function-local imports; not a startup dependency list): `src.engine.robot.motion_sequence`, `src.robot_systems.paint.paint_robot_system`, `src.robot_systems.paint.processes.paint.configuration.models`, `src.robot_systems.paint.processes.paint.operations.dropoff.executor`, `src.robot_systems.paint.processes.paint.motion.executor`, `src.robot_systems.paint.processes.paint.operations.dropoff.motion`, `src.robot_systems.paint.contracts.next_cycle_target`, `src.robot_systems.paint.processes.paint.configuration.service`, `types`, `unittest`, `unittest.mock`.

### `TestDropoffMotionCorridor`

```python
class TestDropoffMotionCorridor(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_retract_failure_reports_that_release_already_completed(self)
```

```python
def test_sub_zero_release_retracts_then_moves_to_and_validates_next_cycle_start(self)
```

```python
def test_saved_settings_update_snapshot_and_notify_live_corridor_consumer(self)
```

```python
def test_live_refresh_replaces_registered_corridor(self)
```

```python
def test_corridor_minimum_z_follows_dropoff_pose_and_tolerance(self)
```

```python
def test_corridor_is_not_built_for_nonnegative_dropoff_pose(self)
```

```python
def test_negative_dropoff_builds_approach_descent_release_and_retract(self)
```

```python
def test_negative_dropoff_is_rejected_when_setting_is_disabled(self)
```

```python
def test_corridor_waypoint_can_only_call_corridor_linear_operation(self)
```

```python
def test_fast_lin_waypoint_calls_fast_linear_operation(self)
```

```python
def test_mixed_ordered_sequence_executes_fast_lin_outside_ordered_chain(self)
```

```python
def test_failed_retract_fails_dropoff_before_any_next_phase_can_continue(self)
```

## `test_dryer_release_coordinator.py`

Source: [tests/robot_systems/paint/test_dryer_release_coordinator.py](../../../../tests/robot_systems/paint/test_dryer_release_coordinator.py).

Imports (including optional/function-local imports; not a startup dependency list): `src.robot_systems.paint.processes.paint.auto_dryer.dryer_release_coordinator`, `threading`, `types`, `unittest`, `unittest.mock`.

### `TestDryerReleaseCoordinator`

```python
class TestDryerReleaseCoordinator(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_enabled_initializing_dryer_refuses_dropoff(self) -> None
```

```python
def test_disabled_dryer_skips_commands_and_readiness_validation(self) -> None
```

```python
def test_sequence_waits_for_next_position_before_eject_and_eject_done(self) -> None
```

```python
def test_eject_completion_accepts_return_to_ready_after_physical_activity(self) -> None
```

```python
def test_stale_next_position_done_does_not_trigger_eject(self) -> None
```

```python
def test_release_callback_queues_without_waiting_for_dryer(self) -> None
```

```python
def test_failed_next_position_does_not_send_eject(self) -> None
```

## `test_fixed_magazine_pickup.py`

Source: [tests/robot_systems/paint/test_fixed_magazine_pickup.py](../../../../tests/robot_systems/paint/test_fixed_magazine_pickup.py).

Imports (including optional/function-local imports; not a startup dependency list): `src.robot_systems.paint.applications.paint_process_settings.mapper`, `src.robot_systems.paint.processes.paint.configuration.models`, `src.robot_systems.paint.processes.paint.production.execution_control`, `src.robot_systems.paint.processes.paint.workflow.context`, `src.robot_systems.paint.processes.paint.workflow.handlers.magazine_load.magazine_capture_handler`, `src.robot_systems.paint.processes.paint.workflow.handlers.magazine_load.magazine_execute_pickup_release_handler`, `src.robot_systems.paint.processes.paint.workflow.handlers.magazine_load.magazine_move_to_magazine_handler`, `src.robot_systems.paint.processes.paint.workflow.handlers.magazine_load.magazine_prepare_pickup_release_handler`, `src.robot_systems.paint.processes.paint.workflow.state`, `src.robot_systems.paint.processes.paint.configuration.serializer`, `unittest`, `unittest.mock`.

### `TestFixedMagazinePickup`

```python
class TestFixedMagazinePickup(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_verified_prepositioned_auto_discovery_recaptures_without_duplicate_move(self)
```

```python
def test_cached_auto_discovery_moves_to_known_pile_approach_before_skipping_camera_wait(self)
```

```python
def test_auto_discovery_approaches_and_retracts_at_configured_z(self)
```

```python
def test_fixed_pickup_allows_approach_to_correct_initial_tolerance_miss(self)
```

```python
def test_old_settings_default_to_vision_targeting(self)
```

```python
def test_legacy_servo_and_fixed_target_are_rejected(self)
```

```python
def test_legacy_servo_without_target_is_rejected(self)
```

```python
def test_fixed_group_settings_round_trip_through_ui_mapper(self)
```

```python
def test_magazine_post_retract_confirmation_round_trips_through_ui_mapper(self)
```

```python
def test_fixed_mode_moves_to_fixed_group_and_skips_camera_wait(self)
```

```python
def test_fixed_mode_moves_to_process_defined_magazine_pose(self)
```

```python
def test_fixed_mode_retries_one_exact_move_after_endpoint_miss(self)
```

```python
def test_capture_retries_one_exact_move_after_settled_endpoint_miss(self)
```

```python
def test_verified_prepositioned_fixed_group_skips_duplicate_move(self)
```

```python
def test_fixed_prepare_does_not_use_snapshot_or_vision_target_resolver(self)
```

```python
def test_start_pose_verification_accepts_wrapped_angles(self)
```

```python
def test_start_pose_verification_refuses_position_mismatch(self)
```

```python
def test_start_pose_verification_waits_for_two_settled_samples(self)
```

## `test_adjustment/session.py`

Source: [tests/robot_systems/paint/test_adjustment/session.py](../../../../tests/robot_systems/paint/test_adjustment/session.py).

Imports (including optional/function-local imports; not a startup dependency list): `src.robot_systems.paint.processes.paint.adjustment.settings_serializer`, `src.robot_systems.paint.processes.paint.adjustment.incremental_painting`, `src.robot_systems.paint.processes.paint.adjustment.session`, `src.robot_systems.paint.processes.paint.paint_process`, `src.robot_systems.paint.processes.paint.results`, `src.shared_contracts.events.process_events`, `threading`, `time`, `types`, `unittest`, `unittest.mock`.

### `_contact_result`

```python
def _contact_result(ok, message, waypoints)
```

### `IncrementalAdjustmentTests`

```python
class IncrementalAdjustmentTests(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_settings_serializer_defaults_require_explicit_inspection_offset(self)
```

```python
def test_adjustment_process_requires_explicit_finish(self)
```

```python
def test_cursor_splits_exact_cartesian_lengths_without_repainting(self)
```

```python
def test_finish_after_final_section_and_explicit_request(self)
```

```python
def test_finish_after_partial_section_skips_remaining_path(self)
```

```python
def test_executor_waits_for_each_press_then_detaches_and_finishes(self)
```

```python
def test_executor_finishes_from_partial_inspection_pose(self)
```

## `test_magazine_pickup_release_pose.py`

Source: [tests/robot_systems/paint/test_magazine_pickup_release_pose.py](../../../../tests/robot_systems/paint/test_magazine_pickup_release_pose.py).

Imports (including optional/function-local imports; not a startup dependency list): `math`, `src.robot_systems.paint.processes.paint.workflow.handlers.magazine_load.magazine_execute_pickup_release_handler`, `unittest`.

### `TestMagazinePickupReleasePose`

```python
class TestMagazinePickupReleasePose(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_applies_calibration_to_plate_rotation_to_workpiece_rz(self) -> None
```

```python
def test_unwraps_result_near_taught_plate_orientation(self) -> None
```

```python
def test_does_not_modify_input_pose(self) -> None
```

```python
def test_rejects_non_finite_orientation(self) -> None
```

## `test_magazine_release_pose.py`

Source: [tests/robot_systems/paint/test_magazine_release_pose.py](../../../../tests/robot_systems/paint/test_magazine_release_pose.py).

Imports (including optional/function-local imports; not a startup dependency list): `src.robot_systems.paint.processes.paint.production.magazine.service`, `types`, `unittest`, `unittest.mock`.

### `TestMagazineReleasePose`

```python
class TestMagazineReleasePose(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_release_center_uses_configured_image_size_without_capture_frame(self) -> None
```

```python
def test_release_z_overrides_calibration_pose_without_changing_orientation(self) -> None
```

## `test_paint_adjustment.py`

Source: [tests/robot_systems/paint/test_paint_adjustment.py](../../../../tests/robot_systems/paint/test_paint_adjustment.py).

Imports (including optional/function-local imports; not a startup dependency list): `PyQt6.QtCore`, `PyQt6.QtTest`, `PyQt6.QtWidgets`, `__future__`, `logging`, `numpy`, `os`, `src.robot_systems.paint.applications.paint_adjustment`, `src.robot_systems.paint.applications.paint_adjustment.dial_geometry`, `src.robot_systems.paint.applications.paint_adjustment.service.i_paint_adjustment_service`, `src.robot_systems.paint.applications.paint_adjustment.service.stub_paint_adjustment_service`, `src.robot_systems.paint.paint_robot_system`, `src.shared_contracts.events.vision_events`, `threading`, `time`, `unittest`, `unittest.mock`.

### `PaintAdjustmentTests`

```python
class PaintAdjustmentTests(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
@classmethod
def setUpClass(cls) -> None
```

```python
def test_registered_in_production_folder(self) -> None
```

```python
def test_dial_maps_presets_evenly_and_interpolates_register_values(self) -> None
```

```python
def test_finish_enabled_after_partial_section_only_at_inspection(self) -> None
```

```python
def test_waiting_for_workpiece_is_visible_and_clears_when_found(self) -> None
```

```python
def test_quick_step_buttons_follow_paint_head_availability(self) -> None
```

```python
def test_more_paint_repeats_while_held_and_stops_on_release(self) -> None
```

```python
def test_invalid_position_read_shows_connection_guidance(self) -> None
```

```python
def test_dragging_dial_sends_positions_before_release(self) -> None
```

```python
def test_dial_sends_latest_release_target_after_slow_write(self) -> None
```

```python
def test_auxiliary_subscription_preview_buttons_and_cleanup(self) -> None
```

## `test_paint_adjustment_service.py`

Source: [tests/robot_systems/paint/test_paint_adjustment_service.py](../../../../tests/robot_systems/paint/test_paint_adjustment_service.py).

Imports (including optional/function-local imports; not a startup dependency list): `dataclasses`, `json`, `pathlib`, `src.engine.common_settings_ids`, `src.engine.hardware.communication.modbus.modbus`, `src.engine.hardware.peripherals`, `src.robot_systems.paint.applications.paint_adjustment.service.i_paint_adjustment_service`, `src.robot_systems.paint.applications.paint_adjustment.service.paint_adjustment_service`, `src.robot_systems.paint.component_ids`, `src.robot_systems.paint.hardware.paint_head_availability_adapter`, `src.robot_systems.paint.processes.paint.adjustment.session`, `unittest`, `unittest.mock`.

### `PaintAdjustmentServiceTests`

```python
class PaintAdjustmentServiceTests(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_tray_profile_enables_plus_and_minus_direction(self)
```

```python
def test_missing_direction_disables_commands(self)
```

```python
def test_rejects_wrong_transport(self)
```

```python
def test_adjusts_relative_to_current_register(self)
```

```python
def test_register_step_uses_units_without_preset_or_degree_conversion(self)
```

```python
def test_register_step_checks_calibrated_range_before_write(self)
```

```python
def test_disabled_device_logs_calculations_without_hardware_io(self)
```

```python
def test_dial_configuration_and_position_read(self)
```

```python
def test_dial_writes_intermediate_position_and_validates_range(self)
```

```python
def test_single_cycle_delegates_without_changing_settings(self)
```

```python
def test_adjustment_options_are_saved_before_start_and_each_next_section(self)
```

```python
def test_open_adjustment_service_follows_devices_toggle_immediately(self)
```

```python
def test_step_must_be_positive_integer(self)
```

## `test_paint_contact_selection_execution.py`

Source: [tests/robot_systems/paint/test_paint_contact_selection_execution.py](../../../../tests/robot_systems/paint/test_paint_contact_selection_execution.py).

Imports (including optional/function-local imports; not a startup dependency list): `numpy`, `src.robot_systems.paint.processes.paint.configuration.models`, `src.robot_systems.paint.processes.paint.operations.painting.executor`, `src.robot_systems.paint.processes.paint.planning.projection.core`, `src.robot_systems.paint.processes.paint.planning.projection.source_plan`, `unittest`.

### `TestPaintContactSelectionExecution`

```python
class TestPaintContactSelectionExecution(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_open_selection_reverses_when_needed_to_keep_configured_paint_side(self)
```

```python
def test_selection_trims_tail_and_retracts_internal_gap(self)
```

```python
def test_prepared_cut_ignores_duplicate_closing_point(self)
```

```python
def test_clearance_offsets_only_non_contact_pose_along_paint_axis(self)
```

## `test_paint_contour_interpolation.py`

Source: [tests/robot_systems/paint/test_paint_contour_interpolation.py](../../../../tests/robot_systems/paint/test_paint_contour_interpolation.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `numpy`, `src.robot_systems.paint.processes.paint.planning.contours.interpolation`, `unittest`.

### `_pose_path_from_xy`

```python
def _pose_path_from_xy(xy_points: list[tuple[float, float]]) -> list[list[float]]
```

### `_max_xy_spacing`

```python
def _max_xy_spacing(path: list[list[float]]) -> float
```

### `_point_to_polyline_distances`

```python
def _point_to_polyline_distances(points: np.ndarray, polyline: np.ndarray) -> np.ndarray
```

### `TestPaintContourInterpolation`

```python
class TestPaintContourInterpolation(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_removes_logged_near_retrace_hairpin(self) -> None
```

```python
def test_hairpin_cleanup_preserves_legitimate_sharp_corner(self) -> None
```

```python
def test_preserves_float_coordinates(self) -> None
```

```python
def test_preserves_hard_corner_while_sampling_curve(self) -> None
```

```python
def test_preserves_rounded_arc_shape(self) -> None
```

```python
def test_mm_hairpin_cleanup_removes_fold_after_simple_resampling(self) -> None
```

## `test_paint_cycle_runner.py`

Source: [tests/robot_systems/paint/test_paint_cycle_runner.py](../../../../tests/robot_systems/paint/test_paint_cycle_runner.py).

Imports (including optional/function-local imports; not a startup dependency list): `src.robot_systems.paint.processes.paint.production.execution_control`, `src.robot_systems.paint.processes.paint.workflow.context`, `src.robot_systems.paint.processes.paint.workflow.state`, `src.robot_systems.paint.processes.paint.production.cycle_runner`, `src.robot_systems.paint.processes.paint.results`, `unittest`, `unittest.mock`.

### `PaintCycleRunnerTests`

```python
class PaintCycleRunnerTests(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def setUp(self)
```

```python
def run_with_machine(self, outcome, error=None, initial_state=PaintExecutionState.STARTING)
```

```python
def test_preserves_completed_and_cancelled_outcomes(self)
```

```python
def test_prepared_workpiece_can_start_at_pickup(self)
```

```python
def test_framework_error_preserves_actionable_failure(self)
```

```python
def test_framework_error_without_domain_failure_becomes_internal(self)
```

```python
def test_construction_and_execution_exceptions_propagate_to_owner(self)
```

## `test_paint_dashboard_mvc.py`

Source: [tests/robot_systems/paint/test_paint_dashboard_mvc.py](../../../../tests/robot_systems/paint/test_paint_dashboard_mvc.py).

Imports (including optional/function-local imports; not a startup dependency list): `PyQt6.QtWidgets`, `__future__`, `os`, `src.robot_systems.paint.applications.dashboard.controller.paint_dashboard_controller`, `src.robot_systems.paint.applications.dashboard.dashboard_state`, `src.robot_systems.paint.applications.dashboard.model.paint_dashboard_model`, `src.robot_systems.paint.contracts.events.dashboard_events`, `src.shared_contracts.events.robot_events`, `src.shared_contracts.events.shell_events`, `src.shared_contracts.events.vision_events`, `time`, `types`, `unittest`, `unittest.mock`.

### `_signal`

```python
def _signal() -> MagicMock
```

### `TestPaintDashboardModel`

```python
class TestPaintDashboardModel(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_load_and_save_contract(self) -> None
```

```python
def test_start_stop_pause_resume_and_reset_delegate_through_service(self) -> None
```

```python
def test_scan_again_uses_dedicated_service_command(self) -> None
```

```python
def test_manual_controls_delegate_through_service(self) -> None
```

```python
def test_paint_head_adjustment_delegates_through_service(self) -> None
```

```python
def test_model_maps_drying_mode_to_service(self)
```

```python
def test_unmatched_paint_settings_delegate_through_service(self) -> None
```

### `TestPaintDashboardController`

```python
class TestPaintDashboardController(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_select_workpieces_action_opens_library(self) -> None
```

```python
def test_scan_again_uses_recapture_command_without_normal_start(self) -> None
```

```python
def test_scan_again_rejection_does_not_start_a_new_pickup_cycle(self) -> None
```

```python
def test_dashboard_refreshes_selection_indicator_after_gallery_return(self) -> None
```

```python
def test_paint_head_command_is_independent_of_running_settings(self) -> None
```

```python
def test_held_paint_head_command_repeats_without_overlapping_and_stops_on_limit(self) -> None
```

```python
def test_finished_worker_cleanup_does_not_query_deleted_threads(self) -> None
```

```python
def test_background_worker_is_removed_before_qt_deletes_thread(self) -> None
```

```python
def test_camera_selection_subscribes_to_selected_topic_and_stops_on_hide(self) -> None
```

```python
def test_compact_dashboard_starts_without_destination_semantics(self)
```

```python
def test_auto_mode_selection_does_not_require_connected_dryer(self)
```

```python
def test_auto_mode_selection_ignores_initializing_dryer(self)
```

```python
def test_start_in_auto_mode_prompts_for_unprepared_destination(self)
```

```python
def test_successful_destination_prepare_continues_pending_start(self)
```

```python
def test_development_mode_can_bypass_unavailable_destination(self)
```

```python
def test_init_wires_signals_and_mixin_setup(self) -> None
```

```python
def test_load_and_stop_manage_subscriptions_and_view_state(self) -> None
```

```python
def test_action_handlers_apply_updated_state(self) -> None
```

```python
def test_saved_unmatched_settings_are_reloaded_from_runtime_snapshot(self) -> None
```

```python
def test_shortcuts_use_visible_shell_apps_and_normal_navigation_topic(self) -> None
```

```python
def test_view_ok_requires_active_visible_view(self) -> None
```

```python
def test_status_refresh_updates_even_when_view_reports_not_visible(self) -> None
```

```python
def test_robot_state_event_refreshes_dashboard_state(self) -> None
```

```python
def test_robot_state_event_reports_starting_state(self) -> None
```

```python
def test_subscribe_dashboard_robot_state_uses_robot_state_topic(self) -> None
```

```python
def test_subscribe_dashboard_live_view_state_uses_paint_live_view_topic(self) -> None
```

```python
def test_unknown_workpiece_message_is_forwarded_as_dashboard_warning(self) -> None
```

```python
def test_subscribe_dashboard_messages_uses_paint_message_topic(self) -> None
```

```python
def test_dashboard_live_view_state_freezes_capture_frame_and_blocks_live_updates(self) -> None
```

## `test_paint_dashboard_view_ui.py`

Source: [tests/robot_systems/paint/test_paint_dashboard_view_ui.py](../../../../tests/robot_systems/paint/test_paint_dashboard_view_ui.py).

Imports (including optional/function-local imports; not a startup dependency list): `PyQt6.QtCore`, `PyQt6.QtWidgets`, `__future__`, `datetime`, `os`, `pl_gui.dashboard.config`, `pl_gui.utils.utils_widgets.SwitchButton`, `src.robot_systems.paint.applications.dashboard.config`, `src.robot_systems.paint.applications.dashboard.dashboard_state`, `src.robot_systems.paint.applications.dashboard.ui.paint_card_factory`, `src.robot_systems.paint.applications.dashboard.ui.paint_controls_drawer`, `src.robot_systems.paint.applications.dashboard.ui.paint_info_card`, `src.robot_systems.paint.applications.dashboard.ui.paint_plate_layout`, `src.robot_systems.paint.applications.dashboard.ui.paint_quick_access_panel`, `src.robot_systems.paint.applications.dashboard.ui.paint_quick_controls_panel`, `src.robot_systems.paint.applications.dashboard.view.paint_dashboard_view`, `src.robot_systems.paint.applications.paint_process_settings.view.paint_process_settings_view`, `src.shared_contracts.events.shell_events`, `types`, `unittest`, `unittest.mock`.

### `_Signal`

```python
class _Signal:
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self) -> None
```

```python
def connect(self, callback) -> None
```

```python
def emit(self, *args) -> None
```

### `_FakeDashboardWidget`

```python
class _FakeDashboardWidget(QWidget):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, config=None, action_buttons=None, cards=None)
```

```python
def set_trajectory_image(self, image) -> None
```

```python
def set_start_enabled(self, enabled: bool) -> None
```

```python
def set_stop_enabled(self, enabled: bool) -> None
```

```python
def set_pause_enabled(self, enabled: bool) -> None
```

```python
def set_pause_text(self, text: str) -> None
```

```python
def set_action_button_enabled(self, action_id: str, enabled: bool) -> None
```

### `TestPaintDashboardUi`

```python
class TestPaintDashboardUi(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_paint_head_buttons_remain_available_when_settings_are_locked(self) -> None
```

```python
def test_compact_select_workpieces_follows_matching_setting_and_emits_action(self) -> None
```

```python
def test_magazine_order_table_reorders_and_disables_available_groups(self) -> None
```

```python
def test_combined_speed_control_maps_speed_to_velocity_and_acceleration(self) -> None
```

```python
def test_combined_speed_control_optionally_shows_live_resolved_values(self) -> None
```

```python
def test_resolved_speed_values_stay_hidden_without_combined_control(self) -> None
```

```python
def test_combined_speed_can_map_ui_one_to_internal_ten(self) -> None
```

```python
def test_separate_velocity_and_acceleration_controls_remain_configurable(self) -> None
```

```python
def test_camera_quick_controls_use_the_same_combined_speed_mapping(self) -> None
```

```python
def test_camera_quick_controls_show_live_resolved_speed_values(self) -> None
```

```python
def test_quick_access_pump_is_off_only_while_fan_remains_toggleable(self) -> None
```

```python
def test_quick_access_new_tray_is_visible_only_in_tray_dry_mode(self) -> None
```

```python
def test_tray_selection_shows_painted_time_and_live_drying_duration(self) -> None
```

```python
def test_tray_dry_duration_control_is_feature_gated(self) -> None
```

```python
def test_tray_marks_workpiece_dried_after_configured_duration(self) -> None
```

```python
def test_tray_canvas_preserves_physical_aspect_ratio(self) -> None
```

```python
def test_portrait_tray_and_workpieces_are_rotated_together_for_display(self) -> None
```

```python
def test_camera_disabled_uses_expanded_settings_and_tray_tabs(self) -> None
```

```python
def test_camera_disabled_can_keep_settings_in_original_tab(self) -> None
```

```python
def test_tray_layout_can_offer_camera_as_optional_tab(self) -> None
```

```python
def test_camera_selector_offers_configured_roles_and_emits_selection(self) -> None
```

```python
def test_camera_disabled_moves_status_cards_to_exclusive_compact_rail(self) -> None
```

```python
@classmethod
def setUpClass(cls) -> None
```

```python
def test_card_factory_builds_info_cards_with_layout_coordinates(self) -> None
```

```python
def test_unmatched_second_pass_tab_defaults_to_pass_one_inheritance(self) -> None
```

```python
def test_info_card_displays_configured_placeholder_content(self) -> None
```

```python
def test_info_card_content_can_be_updated(self) -> None
```

```python
def test_dashboard_view_wires_inner_dashboard_and_applies_state(self) -> None
```

```python
def test_dashboard_view_updates_status_cards_from_state(self) -> None
```

```python
def test_view_initialization_tolerates_missing_dashboard_layout(self) -> None
```

```python
def test_controls_drawer_emits_cable_and_data_driven_device_actions(self) -> None
```

```python
def test_quick_off_command_remains_available_when_device_is_off(self) -> None
```

```python
def test_press_offset_uses_tenth_millimeter_step(self) -> None
```

```python
def test_quick_off_command_is_disabled_only_while_command_is_busy(self) -> None
```

```python
def test_quick_drying_mode_button_cycles_auto_manual_demo(self) -> None
```

```python
def test_drying_mode_controls_can_be_removed_for_tray_dryer(self) -> None
```

```python
def test_system_ui_config_controls_dashboard_drawer_visibility(self) -> None
```

```python
def test_manual_controls_and_shortcuts_are_independently_visible(self) -> None
```

```python
def test_info_and_warning_are_added_to_dashboard_message_queue(self) -> None
```

```python
def test_unknown_workpiece_dialog_uses_action_warning_and_keeps_queue_entry(self) -> None
```

```python
def test_dashboard_message_queue_keeps_latest_fifo_rows(self) -> None
```

## `test_paint_execution_machine.py`

Source: [tests/robot_systems/paint/test_paint_execution_machine.py](../../../../tests/robot_systems/paint/test_paint_execution_machine.py).

Imports (including optional/function-local imports; not a startup dependency list): `numpy`, `src.engine.vision.i_capture_snapshot_service`, `src.robot_systems.paint.processes.paint.configuration.models`, `src.robot_systems.paint.processes.paint.operations.pickup.executor`, `src.robot_systems.paint.processes.paint.production.execution_control`, `src.robot_systems.paint.processes.paint.workflow`, `src.robot_systems.paint.processes.paint.workflow.handlers.common.motion_handlers`, `src.robot_systems.paint.processes.paint.operations.dropoff.motion`, `src.robot_systems.paint.processes.paint.workflow.handlers.workflow.pickup_handler`, `src.robot_systems.paint.processes.paint.workflow.handlers.workflow.plan_handler`, `src.robot_systems.paint.processes.paint.workflow.handlers.workflow.preparation_handler`, `src.robot_systems.paint.processes.paint.production.magazine.service`, `src.robot_systems.paint.processes.paint.match.results`, `src.robot_systems.paint.processes.paint.planning.projection.command_job`, `src.robot_systems.paint.processes.paint.results`, `types`, `unittest`, `unittest.mock`.

### `_prepared_result`

```python
def _prepared_result(raw, message)
```

### `_pickup_result`

```python
def _pickup_result(ok, message)
```

### `_contact_result`

```python
def _contact_result(ok, message, waypoints)
```

### `TestWorkpiecePreparationHandler`

```python
class TestWorkpiecePreparationHandler(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_unknown_match_publishes_established_dashboard_warning(self)
```

```python
def test_build_plan_uses_paint_executor_so_saved_segment_mask_is_attached(self)
```

### `TestPostRetractPickupVerification`

```python
class TestPostRetractPickupVerification(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
@patch('src.robot_systems.paint.processes.paint.operations.pickup.executor.time.sleep')
def test_rejects_signal_that_drops_during_sustained_verification(self, sleep_mock)
```

```python
@patch('src.robot_systems.paint.processes.paint.operations.pickup.executor.time.sleep')
def test_accepts_only_sustained_signal(self, sleep_mock)
```

### `TestDropoffPassagePreparation`

```python
class TestDropoffPassagePreparation(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_opens_configured_passage_before_route_planning(self)
```

```python
def test_rejects_preparation_when_passage_cannot_open(self)
```

### `TestCycleStartUnwind`

```python
class TestCycleStartUnwind(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_unwinds_once_with_navigation_settings(self)
```

```python
def test_skips_unwind_after_prepositioned_partial_segment_rotation(self)
```

```python
def test_keeps_unwind_after_prepositioned_complete_turn(self)
```

### `TestCalibrationPickupTestMode`

```python
class TestCalibrationPickupTestMode(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_completes_after_pickup_without_building_ordered_paint_chain(self)
```

### `TestPaintExecutionMachineScaffold`

```python
class TestPaintExecutionMachineScaffold(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_starting_routes_to_capture_when_magazine_load_is_disabled(self)
```

```python
def test_starting_fails_when_magazine_service_is_missing(self)
```

```python
def test_starting_routes_to_first_fine_magazine_state_for_real_magazine_service(self)
```

```python
def test_starting_routes_to_stopped_when_stop_requested(self)
```

```python
def test_transition_rules_include_planned_execution_phases(self)
```

```python
def test_machine_records_state_timing_when_enabled(self)
```

```python
def test_machine_skips_state_timing_when_disabled(self)
```

```python
def test_machine_executes_mocked_single_cycle_to_completion(self)
```

```python
def test_direct_capture_waits_for_fresh_frame(self)
```

```python
def test_machine_records_no_contour_as_error_result(self)
```

```python
def test_machine_uses_phased_motion_states_for_real_executor_shape(self)
```

### `TestMotionFailureMessage`

```python
class TestMotionFailureMessage(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_uses_backend_error_from_latest_trajectory_response(self)
```

```python
def test_uses_fallback_when_backend_has_no_detail(self)
```

### `_FakePhasedPathExecutor`

```python
class _FakePhasedPathExecutor:
```

Declared fields/defaults:

```python
supports_paint_motion_states = True
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, events: list[str]) -> None
```

## `test_paint_execution_plane_strategies.py`

Source: [tests/robot_systems/paint/test_paint_execution_plane_strategies.py](../../../../tests/robot_systems/paint/test_paint_execution_plane_strategies.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `src.robot_systems.paint.processes.paint.planning.projection.planes`, `unittest`.

### `TestPaintExecutionPlaneStrategies`

```python
class TestPaintExecutionPlaneStrategies(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_xy_strategy_uses_paint_reference_rz_alignment_and_no_flip(self) -> None
```

```python
def test_xy_strategy_unwraps_paint_reference_rz_alignment_near_pickup(self) -> None
```

```python
def test_xz_strategy_uses_z_offset_ry_alignment_and_optional_flip(self) -> None
```

## `test_paint_geometry_and_config.py`

Source: [tests/robot_systems/paint/test_paint_geometry_and_config.py](../../../../tests/robot_systems/paint/test_paint_geometry_and_config.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `json`, `numpy`, `src.engine.robot.motion_sequence`, `src.engine.robot.path_preparation`, `src.robot_systems.paint`, `src.robot_systems.paint.applications.paint_motion_plane_setup.domain.plane_inference`, `src.robot_systems.paint.applications.paint_process_settings.mapper`, `src.robot_systems.paint.applications.paint_process_settings.view.paint_process_settings_schema`, `src.robot_systems.paint.processes.paint.configuration.models`, `src.robot_systems.paint.processes.paint.operations.edge_cleanup.executor`, `src.robot_systems.paint.processes.paint.operations.painting.executor`, `src.robot_systems.paint.processes.paint.production.execution_runtime`, `src.robot_systems.paint.processes.paint.configuration.serializer`, `src.robot_systems.paint.processes.paint.planning.contours.interpolation`, `types`, `unittest`, `unittest.mock`.

### `TestProjectedPathSanitizer`

```python
class TestProjectedPathSanitizer(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_bounded_contour_smoothing_preserves_closure_corners_and_limit(self) -> None
```

```python
def test_workpiece_largest_side_uses_rotated_minimum_area_rectangle(self) -> None
```

```python
def test_removes_short_fold_and_preserves_retreat(self) -> None
```

### `TestPaintProcessConfig`

```python
class TestPaintProcessConfig(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_plate_entry_gate_can_be_used_as_final_paint_detach_pose(self) -> None
```

```python
def test_plate_entry_gate_detach_defaults_to_disabled(self) -> None
```

```python
def test_plate_entry_gate_detach_carries_first_distributed_unwind_quarter(self) -> None
```

```python
def test_serializer_migrates_obsolete_sensor_pickup_settings(self)
```

```python
def test_sub_zero_dropoff_corridor_settings_roundtrip_and_are_exposed(self) -> None
```

```python
def test_contact_staging_settings_roundtrip_through_ui_and_serializer(self) -> None
```

```python
def test_distance_offsets_tab_exposes_attach_and_detach_staging_offsets(self) -> None
```

```python
def test_cleanup_perpendicular_retreat_offset_roundtrips_and_is_exposed(self) -> None
```

```python
def test_cleanup_retreat_uses_axis_perpendicular_to_translation_axis(self) -> None
```

```python
def test_process_config_derived_properties_follow_motion_plane(self) -> None
```

```python
def test_process_config_exposes_pickup_defaults_used_by_executor(self) -> None
```

```python
def test_process_settings_mapper_ignores_removed_interpolation_settings(self) -> None
```

```python
def test_process_settings_mapper_roundtrips_default_paint_motion(self) -> None
```

```python
def test_press_offset_serializer_preserves_tenth_millimeter_value(self) -> None
```

```python
def test_process_settings_mapper_roundtrips_magazine_load_settings(self) -> None
```

```python
def test_process_settings_mapper_roundtrips_safe_travel_settings(self) -> None
```

```python
def test_process_settings_mapper_roundtrips_dropoff_safe_travel_settings(self) -> None
```

```python
def test_process_settings_mapper_roundtrips_diagnostics_settings(self) -> None
```

```python
def test_process_config_serializer_roundtrips_magazine_load_section(self) -> None
```

```python
def test_process_config_serializer_roundtrips_safe_travel_section(self) -> None
```

```python
def test_process_settings_schema_omits_removed_interpolation_tab(self) -> None
```

```python
def test_default_paint_motion_controls_are_under_motion_speeds(self) -> None
```

```python
def test_process_settings_schema_has_magazine_load_motion_speed_controls(self) -> None
```

```python
def test_process_settings_schema_has_process_tab_controls(self) -> None
```

```python
def test_executor_contact_motion_plane_refreshes_from_config_service(self) -> None
```

```python
def test_edge_cleanup_has_separate_xy_rz_enable_gate(self) -> None
```

```python
def test_xy_rz_cleanup_fails_before_clean_move_when_unwind_fails(self) -> None
```

```python
def test_edge_cleanup_uses_ordered_chain_generic_segments(self) -> None
```

```python
def test_paint_contact_executes_final_projected_command_path(self) -> None
```

```python
def test_simulation_config_exposes_plane_specific_indices_and_signs(self) -> None
```

```python
def test_motion_plane_setup_outputs_complete_paint_plane_config(self) -> None
```

```python
def test_normalize_contact_motion_config_preserves_valid_inputs_and_sanitizes_invalid_ones(self) -> None
```

### `TestPaintPickupPlanner`

```python
class TestPaintPickupPlanner(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_camera_to_tcp_delta_accounts_for_rotation_from_reference(self) -> None
```

## `test_paint_head_availability_adapter.py`

Source: [tests/robot_systems/paint/test_paint_head_availability_adapter.py](../../../../tests/robot_systems/paint/test_paint_head_availability_adapter.py).

Imports (including optional/function-local imports; not a startup dependency list): `src.robot_systems.paint.hardware.paint_head_availability_adapter`, `unittest`.

### `PaintHeadAvailabilityAdapterTests`

```python
class PaintHeadAvailabilityAdapterTests(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_toggle_uses_live_state_and_persists_without_hardware(self) -> None
```

## `test_paint_head_device.py`

Source: [tests/robot_systems/paint/test_paint_head_device.py](../../../../tests/robot_systems/paint/test_paint_head_device.py).

Imports (including optional/function-local imports; not a startup dependency list): `src.robot_systems.paint.hardware.paint_head_device`, `unittest`, `unittest.mock`.

### `PaintHeadDeviceTests`

```python
class PaintHeadDeviceTests(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def setUp(self) -> None
```

```python
def test_all_six_presets_match_script_formula(self) -> None
```

```python
def test_one_degree_moves_one_register_unit_in_each_direction(self) -> None
```

```python
def test_degree_conversion_matches_script_rounding(self) -> None
```

```python
def test_rejects_out_of_range_target_without_write(self) -> None
```

```python
def test_rejects_out_of_range_current_position_without_write(self) -> None
```

```python
def test_allows_in_range_current_position_between_calibrated_steps(self) -> None
```

```python
def test_rejects_non_integer_step_without_read(self) -> None
```

```python
def test_rejects_invalid_setting_without_write(self) -> None
```

```python
def test_reports_readback_mismatch(self) -> None
```

## `test_paint_head_settings.py`

Source: [tests/robot_systems/paint/test_paint_head_settings.py](../../../../tests/robot_systems/paint/test_paint_head_settings.py).

Imports (including optional/function-local imports; not a startup dependency list): `PyQt6.QtWidgets`, `__future__`, `os`, `src.applications.base.i_application_controller`, `src.applications.device_control.controller.device_control_controller`, `src.engine.common_settings_ids`, `src.engine.hardware.communication.modbus.modbus`, `src.engine.hardware.peripherals`, `src.robot_systems.paint.applications.paint_adjustment.service.paint_adjustment_service`, `src.robot_systems.paint.applications.paint_head_settings.paint_head_settings_controller`, `src.robot_systems.paint.applications.paint_head_settings.paint_head_settings_service`, `src.robot_systems.paint.applications.paint_head_settings.paint_head_settings_view`, `src.robot_systems.paint.component_ids`, `unittest`, `unittest.mock`.

### `PaintHeadSettingsTests`

```python
class PaintHeadSettingsTests(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_device_control_guard_includes_paint_head_save_workers(self)
```

```python
def setUp(self) -> None
```

```python
def test_saves_direction_spacing_and_count_without_losing_binding(self)
```

```python
def test_rejects_invalid_calibration_without_saving(self)
```

```python
def test_adjustment_uses_new_calibration_without_rebuild(self)
```

```python
def test_view_exposes_saved_values_and_direction(self)
```

## `test_paint_matching_service.py`

Source: [tests/robot_systems/paint/test_paint_matching_service.py](../../../../tests/robot_systems/paint/test_paint_matching_service.py).

Imports (including optional/function-local imports; not a startup dependency list): `json`, `numpy`, `pathlib`, `src.engine.vision.i_capture_snapshot_service`, `src.robot_systems.paint.domain.workpieces.matching_selection`, `src.robot_systems.paint.processes.paint.match.workpiece_matching_service`, `src.robot_systems.paint.processes.paint.planning`, `tempfile`, `unittest`, `unittest.mock`.

### `_square`

```python
def _square(size: float)
```

### `_raw_workpiece`

```python
def _raw_workpiece(name='Part A')
```

### `TestPickLargestContour`

```python
class TestPickLargestContour(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_returns_none_for_empty_input(self)
```

```python
def test_skips_invalid_contours_and_returns_largest_valid(self)
```

### `TestPaintWorkpieceMatchingService`

```python
class TestPaintWorkpieceMatchingService(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_selection_persists_and_prevents_full_library_scan(self)
```

```python
def test_matcher_prefers_preserved_camera_contour_over_editable_contour(self)
```

```python
def test_can_match_saved_workpieces_requires_all_dependencies(self)
```

```python
def test_match_saved_workpieces_returns_unavailable_when_dependencies_missing(self)
```

```python
def test_match_saved_workpieces_returns_no_saved_workpieces_when_candidates_empty(self)
```

```python
def test_match_saved_workpieces_returns_metadata_for_best_match(self)
```

```python
def test_match_saved_workpieces_returns_no_match_message_when_result_empty(self)
```

```python
def test_no_match_writes_contour_comparison_debug_bundle(self)
```

```python
def test_run_matching_caches_snapshot_and_skips_when_no_contours(self)
```

```python
def test_run_matching_uses_candidates_and_snapshot_contours(self)
```

## `test_paint_motion_recipe_app.py`

Source: [tests/robot_systems/paint/test_paint_motion_recipe_app.py](../../../../tests/robot_systems/paint/test_paint_motion_recipe_app.py).

Imports (including optional/function-local imports; not a startup dependency list): `json`, `pathlib`, `src.robot_systems.paint`, `src.robot_systems.paint.applications.paint_motion_recipe.domain.recipe`, `src.robot_systems.paint.applications.paint_motion_recipe.service.paint_motion_recipe_service`, `src.robot_systems.paint.paint_robot_system`, `tempfile`, `types`, `unittest`, `unittest.mock`.

### `TestPaintMotionRecipeService`

```python
class TestPaintMotionRecipeService(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_missing_recipe_file_creates_default_recipe(self)
```

```python
def test_save_and_load_round_trip(self)
```

```python
def test_mock_move_group_updates_pose_without_real_robot_motion(self)
```

```python
def test_mock_vacuum_steps_do_not_call_hardware(self)
```

```python
def test_default_recipe_has_explicit_vacuum_pick_and_drop_steps(self)
```

### `TestPaintMotionRecipeWiring`

```python
class TestPaintMotionRecipeWiring(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_paint_system_declares_developer_motion_recipe_app(self)
```

```python
def test_build_paint_motion_recipe_application_wires_mock_safe_service(self)
```

## `test_paint_navigation_and_targeting.py`

Source: [tests/robot_systems/paint/test_paint_navigation_and_targeting.py](../../../../tests/robot_systems/paint/test_paint_navigation_and_targeting.py).

Imports (including optional/function-local imports; not a startup dependency list): `src.engine.common_service_ids`, `src.engine.common_settings_ids`, `src.engine.robot.targeting`, `src.robot_systems.paint`, `src.robot_systems.paint.calibration.provider`, `src.robot_systems.paint.navigation`, `src.robot_systems.paint.paint_robot_system`, `src.robot_systems.paint.targeting.frames`, `src.robot_systems.paint.targeting.provider`, `src.robot_systems.paint.targeting.registry`, `src.shared_contracts.declarations`, `types`, `unittest`, `unittest.mock`.

### `TestPaintNavigationService`

```python
class TestPaintNavigationService(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_paint_system_starts_with_unknown_active_work_area(self)
```

```python
def test_paint_system_declares_magazine_group_area_and_observer_binding(self)
```

```python
def test_validate_active_capture_area_accepts_robot_at_declared_group(self)
```

```python
def test_validate_active_capture_area_defaults_paint_area_to_calibration_group(self)
```

```python
def test_validate_active_capture_area_rejects_stale_robot_pose(self)
```

```python
def test_validate_active_capture_area_uses_canonical_observer_pose(self)
```

```python
def test_move_home_uses_capture_offset_and_sets_pickup_area(self)
```

```python
def test_move_to_group_sets_observed_area_only_on_success(self)
```

```python
def test_move_to_calibration_position_unwinds_joint6_before_navigation(self)
```

```python
def test_move_to_calibration_position_blocks_when_joint6_unwind_fails(self)
```

```python
def test_move_to_calibration_position_blocks_without_robot_service(self)
```

```python
def test_move_to_calibration_position_can_skip_pre_move_unwind(self)
```

```python
def test_calibration_move_uses_calibration_tool_then_restores_configured_tool(self)
```

```python
def test_magazine_move_restores_configured_tool_when_move_fails(self)
```

```python
def test_observer_pose_is_read_in_calibration_tool_frame_then_restored(self)
```

```python
def test_get_group_position_returns_none_on_lookup_or_parse_failure(self)
```

```python
def test_move_with_z_offset_returns_false_when_group_has_no_position(self)
```

```python
def test_simple_navigation_methods_delegate_and_set_observed_area_on_success(self)
```

```python
def test_move_to_uses_z_offset_path_and_get_group_names_delegates(self)
```

```python
def test_set_area_falls_back_to_vision_when_work_area_service_missing(self)
```

### `TestPaintCalibrationProvider`

```python
class TestPaintCalibrationProvider(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_build_calibration_navigation_rejects_undefined_paint_area(self)
```

```python
def test_build_calibration_navigation_sets_area_when_declared(self)
```

### `TestPaintTargetFrames`

```python
class TestPaintTargetFrames(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_build_frames_uses_navigation_positions_and_height_correction(self)
```

```python
def test_build_frames_returns_none_mapper_when_navigation_missing_or_invalid(self)
```

### `TestPaintTargetRegistry`

```python
class TestPaintTargetRegistry(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_build_point_registry_offsets_points_relative_to_camera(self)
```

### `TestPaintTargetingProvider`

```python
class TestPaintTargetingProvider(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_frame_definitions_merge_persisted_and_declared_data(self)
```

```python
def test_point_definitions_merge_declared_and_persisted_data(self)
```

```python
def test_build_frames_and_lookup_helpers_delegate_to_shared_builders(self)
```

```python
def test_target_options_and_default_name_follow_definitions(self)
```

## `test_paint_pivot_projection.py`

Source: [tests/robot_systems/paint/test_paint_pivot_projection.py](../../../../tests/robot_systems/paint/test_paint_pivot_projection.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `numpy`, `src.robot_systems.paint.processes.paint.configuration.models`, `src.robot_systems.paint.processes.paint.planning.projection`, `unittest`.

### `TestPaintPivotProjection`

```python
class TestPaintPivotProjection(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_closed_contour_overlap_adds_exact_arc_length(self) -> None
```

```python
def test_closed_contour_overlap_rejects_a_second_full_lap(self) -> None
```

```python
def test_continuous_projection_keeps_each_arc_sample_on_pivot(self) -> None
```

```python
def test_continuous_projection_splits_corner_rotation_to_one_degree_steps(self) -> None
```

```python
def test_continuous_projection_applies_xz_rotation_direction_inside_projection(self) -> None
```

```python
def test_rebase_projected_paint_path_to_zero_start_rotation_uses_active_rotation_index(self) -> None
```

```python
def test_project_paint_motion_geometry_continuous_projects_simple_xy_path_around_pivot(self) -> None
```

```python
def test_project_paint_motion_geometry_continuous_uses_explicit_tcp_anchor_for_pose_xy(self) -> None
```

```python
def test_project_paint_motion_geometry_continuous_prefers_long_initial_translation_run(self) -> None
```

```python
def test_project_paint_motion_geometry_continuous_applies_source_rotation_about_tcp_anchor(self) -> None
```

```python
def test_project_paint_motion_geometry_continuous_xz_plane_uses_opposed_contact_heading(self) -> None
```

```python
def test_project_paint_motion_geometry_continuous_for_single_point_returns_snapshot_without_diagnostics(self) -> None
```

```python
def test_project_paint_motion_geometry_continuous_does_not_schedule_rotation_on_straight_lead_in(self) -> None
```

## `test_paint_process_integration.py`

Source: [tests/robot_systems/paint/test_paint_process_integration.py](../../../../tests/robot_systems/paint/test_paint_process_integration.py).

Imports (including optional/function-local imports; not a startup dependency list): `numpy`, `src.engine.vision.i_capture_snapshot_service`, `src.robot_systems.paint.component_ids`, `src.robot_systems.paint.processes.paint.configuration.models`, `src.robot_systems.paint.contracts.events.dashboard_events`, `src.robot_systems.paint.processes.paint.operations.edge_cleanup.executor`, `src.robot_systems.paint.processes.paint.motion.executor`, `src.robot_systems.paint.processes.paint.production.execution_control`, `src.robot_systems.paint.processes.paint.workflow.context`, `src.robot_systems.paint.processes.paint.workflow.handlers.magazine_load.magazine_capture_handler`, `src.robot_systems.paint.processes.paint.workflow.handlers.workflow.capture_handler`, `src.robot_systems.paint.processes.paint.workflow.state`, `src.robot_systems.paint.processes.paint.adjustment.session`, `src.robot_systems.paint.processes.paint.production.magazine.outcomes`, `src.robot_systems.paint.processes.paint.production.magazine.service`, `src.robot_systems.paint.processes.paint.match.results`, `src.robot_systems.paint.processes.paint.paint_process`, `src.robot_systems.paint.processes.paint.production.service`, `src.robot_systems.paint.processes.paint.planning.workpiece_preparation_service`, `src.robot_systems.paint.processes.paint.results`, `src.shared_contracts.events.process_events`, `threading`, `time`, `types`, `unittest`, `unittest.mock`.

### `_square`

```python
def _square(size: float) -> np.ndarray
```

### `_cycle_result`

```python
def _cycle_result(ok, message)
```

### `_prepared_result`

```python
def _prepared_result(raw, message)
```

### `TestPaintProductionServiceIntegration`

```python
class TestPaintProductionServiceIntegration(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_ordered_pickup_requires_completed_integer_success(self)
```

```python
def test_ordered_cleanup_does_not_record_completion_on_invalid_result(self)
```

```python
def test_retry_unmatched_workpiece_recaptures_without_magazine_navigation(self)
```

```python
def test_retry_unmatched_workpiece_rejects_unrelated_error(self)
```

```python
def test_manual_single_cycle_skips_magazine_and_repeat_even_when_enabled(self)
```

```python
def test_manual_single_cycle_capture_retries_empty_frames_then_continues_once(self)
```

```python
def test_manual_single_cycle_capture_retry_stops_on_request(self)
```

```python
def test_magazine_capture_view_preserves_existing_brightness_lock(self)
```

```python
def test_auto_discovery_orders_all_valid_centroids_top_to_bottom_then_left_to_right(self)
```

```python
def test_auto_discovery_orders_piles_nearest_calibration_first(self)
```

```python
def test_batch_nesting_captures_once_and_processes_each_cached_contour(self)
```

```python
def test_auto_discovery_reuses_frozen_contours_without_recapturing(self)
```

```python
def test_preposition_marker_is_consumed_only_after_live_pose_verification(self)
```

```python
def test_resume_clears_preposition_marker(self)
```

```python
def test_run_once_executes_capture_prepare_plan_and_paint_flow(self)
```

```python
def test_run_once_stops_before_planning_when_matching_returns_no_workpiece(self)
```

```python
def test_run_once_freezes_brightness_after_capture_when_auto_enabled(self)
```

```python
@unittest.skip('Legacy aggregate magazine-service mock removed with compatibility path')
def test_run_once_restores_existing_brightness_lock_before_magazine_and_paint_capture(self)
```

```python
def test_run_once_pauses_dashboard_live_view_after_paint_capture_until_cycle_finishes(self)
```

```python
def test_run_once_keeps_dashboard_live_view_enabled_when_capture_pause_disabled(self)
```

```python
def test_run_once_restores_brightness_when_no_contour_found(self)
```

```python
def test_run_once_restores_brightness_after_execution_failure(self)
```

```python
def test_run_once_skips_brightness_lock_when_vision_missing(self)
```

```python
def test_run_once_skips_brightness_lock_when_auto_disabled(self)
```

```python
def test_pause_current_phase_requests_path_executor_pause(self)
```

```python
def test_run_once_enables_path_debug_plots_from_live_settings(self)
```

```python
def test_run_once_returns_no_contour_before_preparation(self)
```

```python
def test_run_once_returns_plan_generation_failure(self)
```

```python
def test_run_once_honors_stop_requests_and_execution_failure(self)
```

```python
def test_run_once_skips_magazine_load_when_disabled(self)
```

```python
def test_run_once_aborts_when_disabled_magazine_calibration_move_fails(self)
```

```python
@unittest.skip('Legacy aggregate magazine-service mock removed with compatibility path')
def test_run_once_executes_magazine_load_before_normal_paint_capture_when_enabled(self)
```

```python
@unittest.skip('Legacy aggregate magazine-service mock removed with compatibility path')
def test_run_once_executes_single_magazine_cycle_when_looping_disabled(self)
```

```python
def test_run_once_loops_manual_cycles_until_no_workpiece_when_looping_enabled(self)
```

```python
def test_repeating_cycle_restores_brightness_after_reaching_calibration(self)
```

```python
def test_manual_loop_uses_any_captured_contour_when_matching_is_disabled(self)
```

```python
@unittest.skip('Legacy aggregate magazine-service mock removed with compatibility path')
def test_run_once_loops_magazine_cycles_until_empty(self)
```

```python
@unittest.skip('Legacy aggregate magazine-service mock removed with compatibility path')
def test_run_once_exits_cleanly_when_magazine_is_empty_before_first_cycle(self)
```

```python
def test_magazine_loop_exhausts_each_ordered_fixed_group_before_finishing(self)
```

```python
def test_fixed_magazine_groups_fall_back_to_legacy_single_group(self)
```

```python
def test_auto_discovery_uses_magazine_group_and_finishes_with_empty_message(self)
```

```python
def test_auto_discovery_repeats_each_pile_until_sensor_reports_empty(self)
```

```python
def test_auto_discovery_recaptures_after_active_pile_is_empty_when_enabled(self)
```

```python
def test_auto_discovery_recaptures_after_every_successful_cycle_when_enabled(self)
```

```python
def test_auto_discovery_prepositions_to_magazine_group_between_pickups(self)
```

```python
def test_auto_discovery_dropoff_preposition_remains_fixed_magazine_pose(self)
```

```python
@unittest.skip('Legacy aggregate magazine-service mock removed with compatibility path')
def test_run_once_aborts_when_magazine_load_fails(self)
```

### `TestPaintMagazineLoadService`

```python
@unittest.skip('Removed standalone magazine state machine; covered by paint execution-machine tests')
class TestPaintMagazineLoadService(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_magazine_load_allows_resume_to_interrupted_execution_state(self)
```

```python
def test_load_to_calibration_uses_simple_contour_center_without_full_paint_planning(self)
```

```python
def test_load_to_calibration_can_pause_and_resume_during_magazine_move(self)
```

```python
def test_load_to_calibration_retries_interrupted_move_once_after_pause_resume(self)
```

### `TestPaintProcessIntegration`

```python
class TestPaintProcessIntegration(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_retry_unmatched_workpiece_starts_capture_only_run(self)
```

```python
def test_retry_unmatched_workpiece_rejects_other_process_errors(self)
```

```python
def test_manual_single_cycle_starts_through_process_and_rejects_duplicate_start(self)
```

```python
def test_successful_run_transitions_process_to_stopped(self)
```

```python
def test_no_workpiece_successful_stop_publishes_operator_message(self)
```

```python
def test_all_magazines_empty_publishes_operator_message(self)
```

```python
def test_failed_run_transitions_process_to_error(self)
```

```python
def test_exception_and_reset_paths_update_internal_stop_flag(self)
```

```python
def test_pause_resume_and_stop_delegate_to_current_production_phase(self)
```

```python
def test_stop_requests_robot_motion_stop_and_vacuum_off(self)
```

```python
def test_stop_does_not_turn_vacuum_off_when_vacuum_is_disabled(self)
```

## `test_paint_process_lifecycle.py`

Source: [tests/robot_systems/paint/test_paint_process_lifecycle.py](../../../../tests/robot_systems/paint/test_paint_process_lifecycle.py).

Imports (including optional/function-local imports; not a startup dependency list): `PyQt6.QtWidgets`, `src.robot_systems.paint.applications.dashboard.config`, `src.robot_systems.paint.applications.dashboard.service.paint_dashboard_service`, `src.robot_systems.paint.applications.dashboard.ui.paint_card_factory`, `src.robot_systems.paint.applications.dashboard.view.paint_dashboard_view`, `src.robot_systems.paint.processes.paint.paint_process`, `src.robot_systems.paint.processes.paint.results`, `src.shared_contracts.events.process_events`, `threading`, `unittest`, `unittest.mock`.

### `TestPaintProcessLifecycle`

```python
class TestPaintProcessLifecycle(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_all_start_paths_wait_for_both_workers_in_either_completion_order(self)
```

```python
def test_reset_cannot_revive_cancelled_run_or_publish_late_result(self)
```

```python
def test_retry_is_rejected_before_reset_while_old_workers_remain(self)
```

```python
def test_start_while_paused_resumes_existing_worker(self)
```

```python
def test_dashboard_reports_delayed_cleanup_without_changing_process_state(self)
```

```python
def test_dashboard_button_stays_disabled_until_workers_exit(self)
```

## `test_paint_process_settings_controller.py`

Source: [tests/robot_systems/paint/test_paint_process_settings_controller.py](../../../../tests/robot_systems/paint/test_paint_process_settings_controller.py).

Imports (including optional/function-local imports; not a startup dependency list): `src.engine.robot.configuration.robot_settings`, `src.robot_systems.paint.applications.paint_process_settings.controller.paint_process_settings_controller`, `src.robot_systems.paint.applications.paint_process_settings.mapper`, `src.robot_systems.paint.applications.paint_process_settings.service.paint_process_settings_application_service`, `src.robot_systems.paint.processes.paint.configuration.models`, `types`, `unittest`, `unittest.mock`.

### `_FakeModel`

```python
class _FakeModel:
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, dropoff_configured: bool, error: str='', pickup_safety_enabled: tuple[bool, bool]=(True, True))
```

```python
def is_dropoff_movement_group_configured(self) -> bool
```

```python
def dropoff_movement_group_configuration_error(self) -> str
```

```python
def get_pickup_safety_enabled(self) -> tuple[bool, bool]
```

### `_FakeView`

```python
class _FakeView:
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self)
```

```python
def set_values(self, values: dict) -> None
```

```python
def values(self) -> dict
```

```python
def set_status(self, message: str) -> None
```

```python
def set_safe_travel_position(self, position: list[float]) -> None
```

```python
def set_dropoff_safe_travel_position(self, position: list[float]) -> None
```

```python
def clear_plate_corners(self) -> None
```

### `TestPaintProcessSettingsController`

```python
class TestPaintProcessSettingsController(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_selecting_servo_contact_requires_pump_and_sensor(self)
```

```python
def test_selecting_servo_contact_requires_process_vacuum_pump(self)
```

```python
def test_magazine_servo_mode_is_allowed_when_pump_and_sensor_are_enabled(self)
```

```python
def test_save_does_not_proceed_with_unsafe_servo_contact(self)
```

```python
def test_servo_contact_minimum_z_round_trips(self)
```

```python
def test_stop_after_calibration_pickup_round_trips(self)
```

```python
def test_legacy_servo_contact_mode_migrates_to_sensor_controlled_fast_lin(self)
```

```python
def test_sensor_controlled_fast_lin_settings_round_trip(self)
```

```python
def test_pickup_sensor_execution_modes_round_trip_independently(self)
```

```python
def test_magazine_retract_policy_round_trips(self)
```

```python
def test_magazine_recapture_after_pile_done_round_trips(self)
```

```python
def test_magazine_recapture_every_cycle_excludes_pile_empty_mode(self)
```

```python
def test_magazine_batch_nesting_settings_round_trip(self)
```

```python
def test_motion_profile_tables_round_trip_type_and_blendr(self)
```

```python
def test_save_rejects_movement_group_strategy_when_dropoff_group_is_not_configured(self)
```

```python
def test_set_safe_travel_current_captures_current_robot_pose_into_view(self)
```

```python
def test_set_dropoff_safe_travel_current_captures_current_robot_pose_into_view(self)
```

```python
def test_clear_plate_corners_resets_poses_and_robot_frame_metadata(self)
```

```python
def test_save_rejects_enabled_safe_travel_without_captured_pose(self)
```

```python
def test_save_rejects_enabled_dropoff_safe_travel_without_captured_pose(self)
```

### `TestPaintProcessSettingsApplicationService`

```python
class TestPaintProcessSettingsApplicationService(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_pickup_safety_reads_persisted_peripheral_enable_flags(self)
```

```python
def test_dropoff_group_validation_requires_position_velocity_and_acceleration(self)
```

```python
def test_current_robot_position_is_read_from_provider_and_normalized(self)
```

```python
def test_move_to_waypoint_dispatches_motion_type_with_robot_tool_and_user(self)
```

```python
def test_move_to_waypoint_uses_live_robot_settings(self)
```

## `test_paint_profiles.py`

Source: [tests/robot_systems/paint/test_paint_profiles.py](../../../../tests/robot_systems/paint/test_paint_profiles.py).

Imports (including optional/function-local imports; not a startup dependency list): `os`, `src.engine.common_settings_ids`, `src.robot_systems.paint.applications.paint_process_settings.view.paint_process_settings_schema`, `src.robot_systems.paint.component_ids`, `src.robot_systems.paint.paint_robot_system`, `src.robot_systems.paint.processes.paint.configuration.models`, `src.robot_systems.paint.processes.paint.configuration.serializer`, `src.robot_systems.paint.processes.paint.configuration.service`, `src.robot_systems.paint_auto_dry.bootstrap_provider`, `src.robot_systems.paint_auto_dry.paint_robot_system`, `src.robot_systems.paint_tray_dry.bootstrap_provider`, `src.robot_systems.paint_tray_dry.paint_robot_system`, `unittest`, `unittest.mock`.

### `TestPaintProfiles`

```python
class TestPaintProfiles(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_fresh_tray_defaults_are_valid_without_changing_saved_values(self)
```

```python
def test_selects_automatic_dryer_profile(self)
```

```python
def test_selects_tray_dryer_profile(self)
```

```python
def test_automatic_dryer_keeps_mode_selection(self)
```

```python
def test_tray_dryer_only_allows_plate_layout_dropoff(self)
```

```python
def test_all_paint_profiles_exclude_height_measurement(self)
```

```python
def test_tray_dryer_rejects_movement_group_dropoff_at_runtime(self)
```

```python
def test_profile_storage_is_isolated(self)
```

```python
def test_providers_resolve_installed_storage_in_their_own_system(self)
```

## `test_paint_runtime_services.py`

Source: [tests/robot_systems/paint/test_paint_runtime_services.py](../../../../tests/robot_systems/paint/test_paint_runtime_services.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `numpy`, `src.engine.hardware.fan.modbus.modbus_fan_control`, `src.engine.hardware.laser`, `src.engine.hardware.vacuum_pump.modbus.modbus_vacuum_pump_transport`, `src.engine.hardware.vacuum_pump.models.vacuum_pump_config`, `src.engine.hardware.vacuum_pump.vacuum_pump_controller`, `src.engine.hardware.vacuum_sensor.models.vacuum_sensor_config`, `src.engine.hardware.vacuum_sensor.vacuum_sensor_service`, `src.engine.hardware.xinje`, `src.engine.robot.calibration.robot_calibration_process`, `src.robot_systems.paint.applications.dashboard.service.paint_dashboard_service`, `src.robot_systems.paint.calibration.coordinator`, `src.robot_systems.paint.component_ids`, `src.robot_systems.paint.destinations`, `src.robot_systems.paint.hardware.paint_head_device`, `src.robot_systems.paint.processes.paint.configuration.models`, `src.robot_systems.paint.processes.paint.production.service`, `src.shared_contracts.events.process_events`, `time`, `types`, `unittest`, `unittest.mock`.

### `TestPaintDashboardService`

```python
class TestPaintDashboardService(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_paint_head_range_limit_returns_normal_command_failure(self) -> None
```

```python
def test_paint_head_adjustment_runs_while_process_is_running(self) -> None
```

```python
def test_dashboard_settings_report_saved_workpiece_selection_count(self) -> None
```

```python
def test_auxiliary_state_reads_active_manual_tray_fan_output(self) -> None
```

```python
def test_failed_auxiliary_state_read_clears_stale_on_indication(self) -> None
```

```python
def test_fan_control_routes_to_tray_fan_in_manual_drying_mode(self) -> None
```

```python
def test_fan_control_routes_to_standard_fan_in_auto_drying_mode(self) -> None
```

```python
def test_enabling_dryer_then_switching_auto_persists_both_settings(self) -> None
```

```python
def test_failed_dryer_enable_does_not_switch_auto_mode(self) -> None
```

```python
def test_drying_mode_persists_matching_dropoff_strategy(self) -> None
```

```python
def test_demo_drying_mode_persists_alternation_starting_with_auto(self) -> None
```

```python
def test_demo_drying_mode_resolves_odd_auto_and_even_manual_cycles(self) -> None
```

```python
def test_drying_mode_cannot_change_while_running(self) -> None
```

```python
def test_cable_relief_uses_configured_unwind_motion_values(self) -> None
```

```python
def test_unmatched_paint_settings_persist_and_replace_runtime_snapshot(self) -> None
```

```python
def test_unmatched_paint_settings_cannot_change_while_running(self) -> None
```

```python
def test_unmatched_paint_settings_can_change_while_running_when_enabled(self) -> None
```

```python
def test_acceleration_scale_can_change_while_paused_when_enabled(self) -> None
```

```python
def test_load_state_maps_process_state_into_dashboard_contract(self) -> None
```

```python
def test_load_state_reports_unavailable_or_unhealthy_status_cards(self) -> None
```

```python
def test_load_state_prefers_robot_connection_details_over_stale_idle_state(self) -> None
```

```python
def test_load_state_prefers_live_robot_connection_state_over_stale_connection_details(self) -> None
```

```python
def test_load_state_sanitizes_robot_connection_exceptions(self) -> None
```

```python
def test_load_state_reports_robot_runtime_starting(self) -> None
```

```python
def test_load_state_reports_drive_not_ready_when_bridge_is_online(self) -> None
```

```python
def test_load_state_reports_ethercat_drive_status_error(self) -> None
```

```python
def test_load_state_uses_vision_health_details_for_offline_camera(self) -> None
```

```python
def test_load_state_reports_intentionally_paused_vision_as_paused(self) -> None
```

```python
def test_control_methods_delegate_to_process(self) -> None
```

```python
def test_reset_errors_is_ignored_while_process_is_running(self) -> None
```

```python
def test_get_process_id_uses_enum_value(self) -> None
```

```python
def test_dashboard_service_does_not_expose_legacy_transform_debug_helper(self) -> None
```

```python
def test_tray_edits_update_shared_layout_while_stopped(self) -> None
```

```python
def test_new_tray_is_rejected_but_removal_updates_layout_while_active(self) -> None
```

### `TestPaintCalibrationCoordinator`

```python
class TestPaintCalibrationCoordinator(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_calibrate_publishes_busy_event_when_calibration_already_running(self) -> None
```

```python
def test_calibrate_resets_error_and_starts_process(self) -> None
```

```python
def test_stop_calibration_clears_active_process_and_stops_only_when_active(self) -> None
```

### `TestRobotCalibrationProcess`

```python
class TestRobotCalibrationProcess(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_on_start_spawns_named_daemon_thread(self) -> None
```

```python
def test_on_stop_sets_flag_and_requests_service_stop(self) -> None
```

```python
def test_on_reset_errors_clears_stop_flag(self) -> None
```

```python
def test_run_in_background_stops_process_on_success(self) -> None
```

```python
def test_run_in_background_sets_error_on_failure(self) -> None
```

```python
def test_run_in_background_sets_error_on_exception_unless_stopping(self) -> None
```

### `TestVacuumPumpController`

```python
class TestVacuumPumpController(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_nonblocking_turn_off_closes_blow_off_after_pulse(self) -> None
```

```python
def test_turn_on_cancels_pending_nonblocking_blow_off(self) -> None
```

```python
def test_read_state_reads_configured_register_without_writing(self) -> None
```

```python
def test_xinje_ma8x8yr_output_labels_resolve_to_modbus_addresses(self) -> None
```

```python
def test_turn_on_and_off_resolve_configured_xinje_output_labels(self) -> None
```

```python
def test_turn_on_and_off_write_configured_values(self) -> None
```

```python
def test_turn_off_pulses_blow_off_after_pump_off(self) -> None
```

```python
def test_turn_on_closes_blow_off_before_pump_on(self) -> None
```

```python
def test_transport_failures_return_false(self) -> None
```

### `TestModbusFanControl`

```python
class TestModbusFanControl(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_operations_update_cached_health(self) -> None
```

### `TestVacuumSensorService`

```python
class TestVacuumSensorService(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_persistent_connection_failure_is_not_hidden(self) -> None
```

```python
def test_transport_connection_is_reused_and_closed_by_service(self) -> None
```

```python
def test_failed_read_reconnects_before_retry(self) -> None
```

```python
def test_read_diagnostics_include_retry_failures_and_attempt_timing(self) -> None
```

```python
def test_read_diagnostics_report_exhausted_retries(self) -> None
```

```python
def test_standard_register_sensor_uses_configured_detected_value(self) -> None
```

```python
def test_repeated_sensor_state_logs_are_throttled_but_transitions_log_immediately(self) -> None
```

```python
def test_sensor_register_accepts_xinje_output_label(self) -> None
```

```python
def test_sensor_register_accepts_xinje_input_label(self) -> None
```

### `TestModbusLaserControl`

```python
class TestModbusLaserControl(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_laser_register_accepts_xinje_output_label(self) -> None
```

### `TestModbusVacuumPumpTransport`

```python
class TestModbusVacuumPumpTransport(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_ma_output_write_uses_fc15_output_bank_frame(self) -> None
```

```python
def test_ma_output_shadow_preserves_previous_bank_values(self) -> None
```

```python
def test_non_ma_output_write_uses_fc5_single_coil_frame(self) -> None
```

```python
def test_send_failures_are_retried_then_raised(self) -> None
```

```python
def test_no_response_write_returns_after_successful_retry(self) -> None
```

```python
def test_explicit_modbus_exception_response_raises(self) -> None
```

```python
def test_padded_modbus_exception_response_raises_clear_exception(self) -> None
```

## `test_paint_segment_selection.py`

Source: [tests/robot_systems/paint/test_paint_segment_selection.py](../../../../tests/robot_systems/paint/test_paint_segment_selection.py).

Imports (including optional/function-local imports; not a startup dependency list): `PyQt6.QtCore`, `contour_editor.models.segment`, `src.robot_systems.paint.domain.paint_segment_selection`, `unittest`, `unittest.mock`.

### `_LayerConfig`

```python
class _LayerConfig:
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
@staticmethod
def name_for_role(role: str) -> str
```

### `TestPaintSegmentSelection`

```python
class TestPaintSegmentSelection(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_contiguous_runs_split_disconnected_rectangle_hits(self)
```

```python
def test_apply_replaces_paint_outline_and_preserves_matching_contour(self)
```

```python
def test_apply_rejects_isolated_selected_points_without_mutating(self)
```

```python
def test_apply_merges_closed_seam_selection_without_rotating_main_contour(self)
```

## `test_paint_support_modules.py`

Source: [tests/robot_systems/paint/test_paint_support_modules.py](../../../../tests/robot_systems/paint/test_paint_support_modules.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `src.engine.common_service_ids`, `src.engine.common_settings_ids`, `src.engine.hardware.communication.modbus.modbus`, `src.engine.hardware.peripherals`, `src.engine.robot.targeting`, `src.robot_systems.paint`, `src.robot_systems.paint.applications`, `src.robot_systems.paint.applications.dashboard`, `src.robot_systems.paint.applications.dashboard.config`, `src.robot_systems.paint.applications.dashboard.dashboard_state`, `src.robot_systems.paint.applications.dashboard.paint_dashboard_factory`, `src.robot_systems.paint.bootstrap_provider`, `src.robot_systems.paint.calibration`, `src.robot_systems.paint.component_ids`, `src.robot_systems.paint.domain.contour_editor_schema`, `src.robot_systems.paint.domain.users`, `src.robot_systems.paint.domain.workpieces.paint_workpiece_library_service`, `src.robot_systems.paint.service_builders`, `src.robot_systems.paint.targeting`, `src.robot_systems.paint.targeting.settings_adapter`, `types`, `unittest`, `unittest.mock`.

### `TestPaintBootstrapProvider`

```python
class TestPaintBootstrapProvider(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_system_class_and_robot_builder(self) -> None
```

```python
def test_build_login_view_wires_auth_and_login_service(self) -> None
```

```python
def test_build_authorization_service_wires_permissions_repository(self) -> None
```

### `TestPaintIdentifiersAndExports`

```python
class TestPaintIdentifiersAndExports(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_component_ids_expose_expected_values(self) -> None
```

```python
def test_package_exports_are_stable(self) -> None
```

### `TestPaintServiceBuildersAndProviders`

```python
class TestPaintServiceBuildersAndProviders(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
@patch('src.robot_systems.default_service_builders.build_vision_service')
def test_build_paint_vision_service_uses_primary_camera_without_fallback(self, default_builder) -> None
```

```python
def test_build_vacuum_pump_service_uses_modbus_factory(self) -> None
```

```python
def test_build_vacuum_pump_service_uses_configured_blow_off_on_value(self) -> None
```

```python
def test_build_vacuum_pump_service_returns_none_on_build_failure(self) -> None
```

### `TestPaintDashboardSupport`

```python
class TestPaintDashboardSupport(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_dashboard_config_and_state_defaults(self) -> None
```

```python
def test_factory_build_sets_messaging_and_constructs_components(self) -> None
```

### `TestPaintSchemasAndLibraryService`

```python
class TestPaintSchemasAndLibraryService(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_contour_editor_schema_defines_expected_fields(self) -> None
```

```python
def test_user_schema_uses_role_values_in_combo_field(self) -> None
```

```python
def test_workpiece_library_service_maps_records_and_updates(self) -> None
```

```python
def test_workpiece_library_update_reports_missing_workpiece(self) -> None
```

### `TestPaintTargetingSettingsAdapter`

```python
class TestPaintTargetingSettingsAdapter(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_to_editor_dict_merges_declared_and_persisted_items(self) -> None
```

```python
def test_from_editor_dict_restores_declared_items_and_preserves_base_work_area(self) -> None
```

## `test_paint_system_integration.py`

Source: [tests/robot_systems/paint/test_paint_system_integration.py](../../../../tests/robot_systems/paint/test_paint_system_integration.py).

Imports (including optional/function-local imports; not a startup dependency list): `dataclasses`, `numpy`, `src.applications.workpiece_editor`, `src.engine.common_service_ids`, `src.engine.common_settings_ids`, `src.engine.vision.calibration_vision_settings`, `src.robot_systems.paint`, `src.robot_systems.paint.applications.dashboard.config`, `src.robot_systems.paint.component_ids`, `src.robot_systems.paint.destinations`, `src.robot_systems.paint.domain.paint_segment_selection`, `src.robot_systems.paint.paint_robot_system`, `src.robot_systems.paint.processes.paint.configuration.models`, `types`, `unittest`, `unittest.mock`.

### `TestPaintApplicationWiring`

```python
class TestPaintApplicationWiring(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_contour_preparation_bypass_is_explicit_and_disabled_by_default(self)
```

```python
def test_build_dashboard_application_passes_dashboard_service_and_messaging(self)
```

```python
def test_build_paint_path_preparation_service_wires_vision_robot_and_navigation_context(self)
```

```python
def test_build_paint_path_preparation_service_falls_back_when_robot_config_values_are_unusable(self)
```

```python
def test_build_paint_path_executor_wires_runtime_callbacks_and_robot_config(self)
```

```python
def test_build_paint_contour_editor_application_wires_factory(self)
```

```python
def test_build_paint_process_settings_application_wires_current_position_provider(self)
```

```python
def test_build_workpiece_library_application_wires_repository_service_and_factory(self)
```

```python
def test_build_matching_service_receives_saved_selection(self)
```

```python
def test_build_user_management_application_wires_roles_permissions_and_factory(self)
```

```python
def test_build_camera_and_calibration_settings_applications_wire_expected_services(self)
```

```python
def test_build_broker_debug_and_intrinsic_capture_applications_wire_factories(self)
```

```python
def test_build_hand_eye_and_pick_target_applications_wire_runtime_services(self)
```

```python
def test_build_capture_snapshot_and_workpiece_services_wire_dependencies(self)
```

```python
def test_small_application_wiring_helpers_cover_debug_dir_and_target_validation(self)
```

```python
def test_build_matching_and_preparation_services_wire_runtime_functions(self)
```

```python
def test_build_workpiece_editor_service_wires_storage_services_and_options(self)
```

```python
def test_build_calibration_application_wires_optional_calibrators_and_observer_position(self)
```

```python
def test_build_robot_settings_application_wires_targeting_load_and_save(self)
```

### `TestPaintRobotSystemStart`

```python
class TestPaintRobotSystemStart(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_on_start_starts_and_registers_vision_when_present(self)
```

```python
def test_on_start_skips_vision_start_when_optional_service_missing(self)
```

## `test_paint_system_overrides.py`

Source: [tests/robot_systems/paint/test_paint_system_overrides.py](../../../../tests/robot_systems/paint/test_paint_system_overrides.py).

Imports (including optional/function-local imports; not a startup dependency list): `src.robot_systems.paint`, `src.robot_systems.paint.application_wiring`, `src.robot_systems.paint.paint_robot_system`, `src.robot_systems.paint_auto_dry.paint_robot_system`, `src.robot_systems.paint_tray_dry`, `src.robot_systems.paint_tray_dry.paint_robot_system`, `types`, `unittest`, `unittest.mock`.

### `PaintSystemOverrideTests`

```python
class PaintSystemOverrideTests(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_empty_overrides_preserve_profile_behavior(self)
```

```python
def test_ui_apps_and_diagnostics_override_only_selected_system(self)
```

```python
def test_unknown_override_fails(self)
```

```python
def test_profile_providers_apply_their_own_module(self)
```

## `test_paint_timing.py`

Source: [tests/robot_systems/paint/test_paint_timing.py](../../../../tests/robot_systems/paint/test_paint_timing.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `src.robot_systems.paint.processes.paint.workflow.state`, `src.robot_systems.paint.timing`, `unittest`, `unittest.mock`.

### `TestPaintTimingRecorder`

```python
class TestPaintTimingRecorder(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_log_summary_keeps_info_compact_and_writes_details_to_debug(self) -> None
```

```python
def test_log_state_summary_emits_ordered_state_table(self) -> None
```

## `test_paint_typed_results.py`

Source: [tests/robot_systems/paint/test_paint_typed_results.py](../../../../tests/robot_systems/paint/test_paint_typed_results.py).

Error categories survive operation boundaries and cleanup remains reliable.

Imports (including optional/function-local imports; not a startup dependency list): `dataclasses`, `numpy`, `pathlib`, `src.engine.vision.i_capture_snapshot_service`, `src.robot_systems.paint.domain.workpieces.errors`, `src.robot_systems.paint.domain.workpieces.repository.json_paint_workpiece_repository`, `src.robot_systems.paint.domain.workpieces.service.paint_workpiece_service`, `src.robot_systems.paint.processes.paint.configuration.models`, `src.robot_systems.paint.processes.paint.operations.pickup.executor`, `src.robot_systems.paint.processes.paint.production.execution_control`, `src.robot_systems.paint.processes.paint.workflow.context`, `src.robot_systems.paint.processes.paint.workflow.handlers.common.motion_handlers`, `src.robot_systems.paint.processes.paint.operations.dropoff.motion`, `src.robot_systems.paint.processes.paint.workflow.handlers.lifecycle.terminal_common`, `src.robot_systems.paint.processes.paint.workflow.handlers.workflow.preparation_handler`, `src.robot_systems.paint.processes.paint.workflow.machine_factory`, `src.robot_systems.paint.processes.paint.workflow.state`, `src.robot_systems.paint.processes.paint.adjustment.session`, `src.robot_systems.paint.processes.paint.match.results`, `src.robot_systems.paint.processes.paint.match.workpiece_matching_service`, `src.robot_systems.paint.processes.paint.paint_process`, `src.robot_systems.paint.processes.paint.planning.pickup.transfer_planner`, `src.robot_systems.paint.processes.paint.planning.workpiece_preparation_service`, `src.robot_systems.paint.processes.paint.results`, `src.robot_systems.paint.processes.paint.tray_dry.plate_layout`, `src.shared_contracts.events.process_events`, `tempfile`, `tests.robot_systems.paint.test_tray_readiness`, `types`, `unittest`, `unittest.mock`.

### `contour`

```python
def contour()
```

### `context`

```python
def context(service=None)
```

### `TestPaintTypedResults`

```python
class TestPaintTypedResults(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_corrupt_saved_record_is_storage_failure_through_real_service(self)
```

```python
def test_unreadable_library_root_is_not_empty_match_through_service(self)
```

```python
def test_adjustment_cancel_does_not_require_a_second_stop_poll(self)
```

```python
def test_adjustment_commands_distinguish_next_finish_and_cancel(self)
```

```python
def test_process_exposes_actionable_failure_from_typed_production_result(self)
```

```python
def test_failed_result_requires_failure_and_success_cannot_carry_one(self)
```

```python
def test_context_boolean_and_message_are_views_of_one_result(self)
```

```python
def test_planning_empty_jobs_reports_explicit_reason_without_motion(self)
```

```python
def test_pickup_invalid_mode_is_rejected_before_vacuum_or_motion(self)
```

```python
def test_height_measure_is_unavailable_rather_than_invalid_mode(self)
```

```python
def test_pickup_vacuum_failure_preserves_its_message_and_category(self)
```

```python
def test_pickup_cancellation_is_not_a_motion_failure(self)
```

```python
def matcher(self, list_fn)
```

```python
def test_empty_repository_and_storage_failure_are_distinct(self)
```

```python
def test_matcher_bug_is_internal_with_traceback(self)
```

```python
def test_storage_failure_survives_preparation_and_dashboard_boundary(self)
```

```python
def test_live_settings_failure_does_not_fall_back_to_stale_defaults(self)
```

```python
def test_timing_disk_failure_cannot_prevent_motion_cleanup(self)
```

```python
def test_cleanup_attempts_other_resources_and_preserves_primary_failure(self)
```

```python
def test_unexpected_handler_failure_runs_terminal_cleanup(self)
```

```python
def test_missing_exit_profile_is_rejected_before_entry_or_release(self)
```

## `test_paint_workpiece_editor_adapter.py`

Source: [tests/robot_systems/paint/test_paint_workpiece_editor_adapter.py](../../../../tests/robot_systems/paint/test_paint_workpiece_editor_adapter.py).

Imports (including optional/function-local imports; not a startup dependency list): `contour_editor.persistence.data.editor_data_model`, `numpy`, `src.applications.workpiece_editor.editor_core.adapters.adapter_utils`, `src.robot_systems.paint.domain.paint_workpiece_editor_adapter`, `unittest`, `unittest.mock`.

### `TestPaintWorkpieceEditorAdapter`

```python
class TestPaintWorkpieceEditorAdapter(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def setUp(self)
```

```python
def test_from_workpiece_maps_main_contour_and_spray_pattern_layers(self)
```

```python
def test_to_workpiece_data_preserves_main_settings_and_process_defaults(self)
```

```python
def test_to_workpiece_data_uses_legacy_layer_fallbacks_and_empty_main_contour(self)
```

```python
def test_from_raw_extracts_main_settings_and_process_layers(self)
```

```python
def test_from_raw_copies_complete_matching_contour_into_empty_paint_layer(self)
```

```python
def test_from_raw_does_not_replace_saved_paint_sections(self)
```

```python
def test_selected_paint_sections_round_trip_without_initial_copy_marker(self)
```

```python
def test_print_summary_delegates_to_shared_helper(self)
```

## `test_paint_workpiece_path_executor.py`

Source: [tests/robot_systems/paint/test_paint_workpiece_path_executor.py](../../../../tests/robot_systems/paint/test_paint_workpiece_path_executor.py).

Imports (including optional/function-local imports; not a startup dependency list): `numpy`, `src.engine.geometry.planar`, `src.engine.robot.motion_sequence`, `src.engine.robot.path_preparation`, `src.robot_systems.paint.processes.paint.configuration.models`, `src.robot_systems.paint.processes.paint.motion.waypoint`, `src.robot_systems.paint.diagnostics.artifacts`, `src.robot_systems.paint.processes.paint.operations.pickup.executor`, `src.robot_systems.paint.processes.paint.production.execution_runtime`, `src.robot_systems.paint.processes.paint.production.execution_control`, `src.robot_systems.paint.processes.paint.operations.dropoff.motion`, `src.robot_systems.paint.processes.paint.workflow.handlers.magazine_load.magazine_execute_pickup_release_handler`, `src.robot_systems.paint.processes.paint.motion.path_geometry`, `src.robot_systems.paint.processes.paint.motion.pose_comparison`, `src.robot_systems.paint.processes.paint.planning.projection.command_job`, `src.robot_systems.paint.processes.paint.results`, `threading`, `time`, `types`, `unittest`, `unittest.mock`.

### `_make_executor`

```python
def _make_executor(robot_service=None, **options)
```

Build the executor through its explicit production-facing configuration API.

### `_execution_plan`

```python
def _execution_plan(*jobs, workpiece=None)
```

### `_pickup_result`

```python
def _pickup_result(ok, message)
```

### `_contact_result`

```python
def _contact_result(ok, message, waypoints)
```

### `TestPaintStagingOffsetPose`

```python
class TestPaintStagingOffsetPose(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_detach_adds_workpiece_clearance_to_configured_paint_axis_offset(self)
```

```python
def test_offsets_axis_perpendicular_to_xy_paint_axis(self)
```

```python
def test_offsets_axis_perpendicular_to_xz_paint_axis(self)
```

### `TestDropoffReleaseVerification`

```python
class TestDropoffReleaseVerification(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_failed_previous_eject_cancels_before_dropoff_motion_with_reason(self)
```

```python
def test_release_verified_callback_notifies_destination(self)
```

```python
def test_release_verified_callback_failure_is_reported(self)
```

```python
def test_release_verification_succeeds_when_vacuum_clears(self)
```

```python
def test_release_verification_fails_when_vacuum_remains_detected(self)
```

```python
def test_release_verification_fails_when_sensor_read_is_unhealthy(self)
```

### `TestNormalizePivotConfig`

```python
class TestNormalizePivotConfig(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_invalid_plane_axis_and_direction_fall_back_to_defaults(self)
```

```python
def test_paint_pickup_segments_stop_only_after_descend_and_at_staging(self)
```

### `TestPaintPathRotationHelpers`

```python
class TestPaintPathRotationHelpers(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_axis_equivalent_shift_preserves_path_relative_rotation(self)
```

### `TestPaintWorkpiecePathExecutor`

```python
class TestPaintWorkpiecePathExecutor(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_prepared_execution_refreshes_settings_and_scales_acceleration_once(self)
```

```python
def test_prepare_workpiece_execution_plan_builds_and_caches_execution_plan(self)
```

```python
def test_prepare_workpiece_execution_plan_requires_path_preparation_service(self)
```

```python
def test_controlled_paint_preplans_pickup_and_contact_in_one_ordered_chain(self)
```

```python
def test_controlled_paint_retries_ordered_chain_when_pause_resume_happens_before_stop_result(self)
```

```python
def test_pause_current_execution_stops_non_protected_ordered_segment(self)
```

```python
def test_pause_current_execution_defers_stop_for_protected_ordered_segment(self)
```

```python
def test_refresh_process_config_updates_vacuum_pump_flag(self)
```

```python
def test_live_peripheral_disable_blocks_vacuum_pump_commands(self)
```

```python
def test_explicit_magazine_transfer_orders_pickup_lift_then_release_pose(self)
```

```python
def test_execute_magazine_pickup_release_uses_direct_target_without_plan(self)
```

```python
def test_resume_pickup_target_release_continues_from_current_pose_to_next_target(self)
```

```python
def test_ordered_non_contact_motion_resume_retries_remaining_waypoints(self)
```

```python
def test_execute_magazine_pickup_release_fails_without_ordered_chain(self)
```

```python
def test_get_projected_pivot_paths_skips_jobs_without_paths_and_applies_offsets(self)
```

```python
def test_get_pivot_motion_snapshots_returns_projected_snapshots(self)
```

```python
def test_build_paint_contact_path_can_rebase_start_rotation_to_zero(self)
```

```python
def test_resolve_base_position_returns_none_for_provider_errors_or_bad_values(self)
```

```python
def test_apply_pivot_offset_uses_y_for_xy_mode_and_z_for_xz_mode(self)
```

```python
def test_build_pickup_and_stage_poses_uses_configured_pickup_offsets(self)
```

```python
def test_incomplete_pickup_movement_group_pose_blocks_execution_without_orientation_fallback(self)
```

```python
def test_configured_waypoints_reject_nonfinite_pose_and_profile_fields(self)
```

```python
def test_waypoint_container_enforces_finiteness_on_direct_construction(self)
```

```python
def test_safe_travel_rejects_invalid_waypoint_before_robot_submission(self)
```

```python
def test_pickup_plan_inserts_configured_safe_travel_waypoint_before_paint_staging(self)
```

```python
def test_enabled_safe_travel_blocks_pickup_plan_when_group_position_is_missing(self)
```

```python
def test_build_pickup_and_stage_poses_does_not_double_apply_tcp_offset_for_resolved_pickup_target(self)
```

```python
def test_build_pickup_and_stage_poses_trusts_prepared_pickup_rz(self)
```

```python
@unittest.skip('Projection ownership moved to PaintPickupTransferPlanner')
def test_build_pickup_and_stage_poses_reprojects_after_pickup_alignment(self)
```

```python
def test_execute_paint_contact_paths_uses_carried_source_rotation(self)
```

```python
def test_projected_pivot_paths_use_pickup_source_rotation_and_command_mapping(self)
```

```python
def test_xz_ry_pickup_handoff_keeps_fixed_paint_rz_without_initial_pivot_rotation(self)
```

```python
def test_move_pickup_phase_uses_pickup_motion_defaults(self)
```

```python
@unittest.skip('Legacy owner-level pickup orchestration was extracted to PaintPickupExecutor')
def test_execute_pickup_to_pivot_uses_phase_specific_motion_settings(self)
```

```python
@unittest.skip('Legacy owner-level pickup orchestration was extracted to PaintPickupExecutor')
def test_execute_pickup_to_pivot_uses_deterministic_optimized_move_sequence(self)
```

```python
@unittest.skip('Covered by PaintPickupExecutor waypoint-plan tests')
def test_pickup_stage_lifts_with_pickup_rz_before_aligning_to_reference_rz(self)
```

```python
@unittest.skip('Covered by PaintDropoffExecutor strategy tests')
def test_pre_release_dropoff_does_not_restore_pickup_rz_before_release(self)
```

```python
def test_xy_rz_pre_dropoff_unwind_does_not_move_to_align_pose_before_unwind(self)
```

```python
def test_xy_rz_ordered_dropoff_preparation_unwinds_without_align_move(self)
```

```python
def test_xy_rz_current_dropoff_releases_without_align_pose_wrap_move(self)
```

```python
def test_xy_rz_dropoff_rejects_missing_movement_group_without_motion(self)
```

```python
def test_xy_rz_movement_group_dropoff_moves_to_configured_group_before_release(self)
```

```python
def test_xy_rz_movement_group_dropoff_preparation_moves_to_dropoff_before_unwind(self)
```

```python
def test_sub_zero_dropoff_preparation_stops_at_configured_release_pose(self)
```

```python
def test_paint_to_dropoff_safe_travel_precedes_dropoff_align_before_unwind(self)
```

```python
def test_enabled_paint_to_dropoff_safe_travel_without_pose_blocks_dropoff_preparation(self)
```

```python
def test_xz_ry_ordered_dropoff_preparation_uses_configured_dropoff_group(self)
```

```python
def test_dropoff_pose_close_treats_wrapped_xy_rz_as_same_release_pose(self)
```

```python
def test_execute_paint_process_runs_post_execute_return_after_success(self)
```

```python
def test_execute_paint_process_pauses_after_contact_before_dropoff(self)
```

```python
def test_execute_paint_process_logs_timing_summary_after_cycle(self)
```

```python
def test_execute_paint_process_skips_timing_csv_when_diagnostics_are_disabled(self)
```

```python
def test_xy_rz_cleanup_unwinds_without_calibration_before_cleanup(self)
```

```python
def test_execute_paint_process_fails_when_post_execute_return_fails(self)
```

```python
def test_execute_paint_process_stops_without_return_after_paint_contact_failure(self)
```

```python
def test_execute_paint_process_reports_dropoff_failure_without_return_motion(self)
```

```python
def test_build_executed_snapshot_series_rebases_preview_snapshot_to_executed_poses(self)
```

```python
def test_build_executed_snapshot_series_does_not_rotate_snapshots_from_command_axis_shift(self)
```

## `test_paint_workpiece_preparation_service.py`

Source: [tests/robot_systems/paint/test_paint_workpiece_preparation_service.py](../../../../tests/robot_systems/paint/test_paint_workpiece_preparation_service.py).

Imports (including optional/function-local imports; not a startup dependency list): `numpy`, `src.robot_systems.paint.processes.paint.planning.workpiece_preparation_service`, `unittest`.

### `_square`

```python
def _square(size: float) -> np.ndarray
```

### `_matched_payload`

```python
def _matched_payload()
```

### `TestContourToWorkpieceRaw`

```python
class TestContourToWorkpieceRaw(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_wraps_captured_contour_into_workpiece_payload(self)
```

```python
def test_wraps_captured_contour_with_default_segment_settings(self)
```

### `TestPaintWorkpiecePreparationService`

```python
class TestPaintWorkpiecePreparationService(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_prepare_workpiece_skips_matching_when_disabled(self)
```

```python
def test_disabled_matching_uses_live_default_motion_settings(self)
```

```python
def test_matched_workpiece_keeps_its_own_motion_settings(self)
```

```python
def test_prepare_workpiece_falls_back_to_captured_contour_when_matching_unavailable(self)
```

```python
def test_prepare_workpiece_stops_when_match_returns_no_payload(self)
```

```python
def test_prepare_workpiece_uses_matched_contour_branch(self)
```

```python
def test_prepare_workpiece_stops_when_matched_raw_has_no_contour(self)
```

```python
def test_prepare_workpiece_stops_when_matched_raw_is_empty(self)
```

```python
def test_resolve_frame_size_uses_defaults_for_missing_shape(self)
```

## `test_paint_workpiece_storage.py`

Source: [tests/robot_systems/paint/test_paint_workpiece_storage.py](../../../../tests/robot_systems/paint/test_paint_workpiece_storage.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `json`, `numpy`, `os`, `pathlib`, `src.robot_systems.paint.domain.workpieces.repository.json_paint_workpiece_repository`, `src.robot_systems.paint.domain.workpieces.service.paint_workpiece_service`, `tempfile`, `unittest`, `unittest.mock`.

### `TestNumpyToPython`

```python
class TestNumpyToPython(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_converts_arrays_recursively(self) -> None
```

### `TestJsonPaintWorkpieceRepository`

```python
class TestJsonPaintWorkpieceRepository(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_save_list_load_update_thumbnail_delete_and_exists(self) -> None
```

```python
def test_preparation_failures_preserve_existing_pair_and_hide_new_records(self)
```

```python
def test_json_publication_failure_restores_thumbnail(self)
```

```python
def test_failed_rollback_blocks_record_and_preserves_recovery_files(self)
```

```python
def test_update_write_and_thumbnail_publication_failures_preserve_pair(self)
```

```python
def test_real_thumbnail_failure_does_not_publish_invalid_workpiece(self)
```

```python
def test_staging_write_and_new_publication_failures_leave_no_record(self)
```

```python
def test_list_all_skips_invalid_entries_and_missing_json(self) -> None
```

```python
def test_invalid_ids_cannot_read_update_or_delete_outside_storage(self)
```

```python
def test_symlink_record_date_and_json_are_rejected(self)
```

```python
def test_thumbnail_symlink_is_not_read_or_overwritten(self)
```

```python
def test_update_missing_storage_id_raises(self) -> None
```

### `TestPaintWorkpieceService`

```python
class TestPaintWorkpieceService(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_service_delegates_success_paths(self) -> None
```

```python
def test_load_exposes_matchable_saved_workpiece(self) -> None
```

```python
def test_load_skips_workpieces_without_contour(self) -> None
```

```python
def test_service_handles_repository_failures(self) -> None
```

```python
def test_delete_reports_not_found_when_repository_returns_false(self) -> None
```

## `test_pickup_condition_wiring.py`

Source: [tests/robot_systems/paint/test_pickup_condition_wiring.py](../../../../tests/robot_systems/paint/test_pickup_condition_wiring.py).

Imports (including optional/function-local imports; not a startup dependency list): `src.engine.robot.procedures`, `src.robot_systems.paint.component_ids`, `src.robot_systems.paint.paint_robot_system`, `types`, `unittest`, `unittest.mock`.

### `TestPaintPickupConditionWiring`

```python
class TestPaintPickupConditionWiring(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_real_vacuum_sensor_is_used_as_stop_condition(self) -> None
```

```python
def test_dummy_condition_remains_explicit_override(self) -> None
```

```python
def test_missing_sensor_leaves_condition_unconfigured(self) -> None
```

## `test_plate_layout_dropoff.py`

Source: [tests/robot_systems/paint/test_plate_layout_dropoff.py](../../../../tests/robot_systems/paint/test_plate_layout_dropoff.py).

Imports (including optional/function-local imports; not a startup dependency list): `datetime`, `math`, `src.engine.robot.motion_sequence`, `src.robot_systems.paint.applications.paint_process_settings.mapper`, `src.robot_systems.paint.processes.paint.configuration.models`, `src.robot_systems.paint.processes.paint.operations.dropoff.motion`, `src.robot_systems.paint.processes.paint.workflow.handlers.magazine_load.magazine_execute_pickup_release_handler`, `src.robot_systems.paint.processes.paint.workflow.handlers.workflow.pickup_handler`, `src.robot_systems.paint.contracts.next_cycle_target`, `src.robot_systems.paint.processes.paint.tray_dry.plate_layout`, `types`, `unittest`, `unittest.mock`.

### `_corners`

```python
def _corners()
```

### `TestPlateLayoutDropoff`

```python
class TestPlateLayoutDropoff(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_paint_pass_metadata_records_two_distinct_pass_settings(self) -> None
```

```python
def test_committed_placement_keeps_painted_timestamp_metadata(self) -> None
```

```python
def test_workpiece_footprint_always_uses_long_side_as_width(self) -> None
```

```python
def test_workpiece_layout_geometry_preserves_normalized_outline(self) -> None
```

```python
def test_workpiece_outline_orientation_is_independent_of_contour_order(self) -> None
```

```python
def test_automatic_center_route_is_used_inside_half_corner_to_center_radius(self) -> None
```

```python
def test_automatic_center_route_is_skipped_outside_half_corner_to_center_radius(self) -> None
```

```python
def test_automatic_center_route_can_be_disabled_near_corner(self) -> None
```

```python
def test_explicit_center_route_setting_forces_center_for_far_position(self) -> None
```

```python
def test_plate_entry_waits_for_two_inactive_motion_status_samples(self) -> None
```

```python
def test_plate_entry_rejects_missing_execution_status_api(self) -> None
```

```python
def test_plate_entry_rejects_malformed_execution_status(self) -> None
```

```python
def test_plate_dropoff_preparation_is_not_appended_to_pickup_paint_chain(self) -> None
```

```python
def test_existing_dropoff_strategy_keeps_ordered_preparation(self) -> None
```

```python
def test_settings_mapper_roundtrips_plate_strategy_and_corners(self) -> None
```

```python
def test_requires_exactly_four_corners_without_fallback(self) -> None
```

```python
def test_rejects_inconsistent_corner_order(self) -> None
```

```python
def test_reserves_pose_rotated_from_calibration_into_plate_frame(self) -> None
```

```python
def test_ordered_release_uses_configured_entry_and_exit_chains(self) -> None
```

```python
def test_preparation_unwinds_at_detach_without_moving(self) -> None
```

```python
def test_distributed_unwind_progresses_continuously_over_plate_route(self) -> None
```

```python
def test_distributed_unwind_is_positive_when_paint_rz_rotation_is_negative(self) -> None
```

```python
def test_distributed_unwind_does_not_add_a_turn_for_small_paint_rotation(self) -> None
```

```python
def test_distributed_unwind_does_not_unwind_partial_selected_segment_turn(self) -> None
```

```python
def test_combined_paint_chain_builds_plate_entry_through_release(self) -> None
```

```python
def test_combined_paint_chain_carries_first_half_of_distributed_unwind(self) -> None
```

```python
def test_combined_paint_chain_does_not_schedule_unwind_for_partial_turn(self) -> None
```

```python
def test_optimized_entry_continues_remaining_half_on_exit(self) -> None
```

```python
def test_distributed_unwind_preserves_dropoff_rectangle_orientation_modulo_180(self) -> None
```

```python
def test_failed_reservation_does_not_consume_position(self) -> None
```

```python
def test_removed_workpiece_space_is_reused(self) -> None
```

```python
def test_new_tray_clears_committed_workpieces_after_pending_is_cancelled(self) -> None
```

## `test_trajectory_export_result.py`

Source: [tests/robot_systems/paint/test_trajectory_export_result.py](../../../../tests/robot_systems/paint/test_trajectory_export_result.py).

Optional exports report failures without raising into their motion caller.

Imports (including optional/function-local imports; not a startup dependency list): `concurrent.futures`, `pathlib`, `src.robot_systems.paint.processes.paint.operations`, `src.robot_systems.paint.diagnostics.trajectory_export_result`, `tempfile`, `unittest`, `unittest.mock`.

### `TestTrajectoryExportResult`

```python
class TestTrajectoryExportResult(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def request(self, **overrides)
```

```python
def test_empty_path_is_explicitly_skipped_without_submission(self)
```

```python
def test_invalid_snapshot_is_a_typed_failure_before_submission(self)
```

```python
def test_executor_shutdown_does_not_raise_into_motion_caller(self)
```

```python
def test_unexpected_submission_bug_is_error_level_internal_failure(self)
```

```python
def test_directory_permission_failure_is_distinct_from_programming_bug(self)
```

```python
def run_export(self, root, *, plot_failure=None)
```

```python
def test_plot_bug_reports_csv_already_written_and_preserves_traceback(self)
```

```python
def test_success_records_only_artifacts_actually_written(self)
```

```python
def test_filesystem_failure_after_csv_retains_completed_artifact(self)
```

```python
def test_queued_data_is_detached_from_mutable_caller_inputs(self)
```

```python
def test_process_interrupts_are_not_converted_to_optional_failures(self)
```

## `test_tray_readiness.py`

Source: [tests/robot_systems/paint/test_tray_readiness.py](../../../../tests/robot_systems/paint/test_tray_readiness.py).

Tray confirmation protects physical occupancy across UI and production paths.

Imports (including optional/function-local imports; not a startup dependency list): `PyQt6.QtCore`, `PyQt6.QtWidgets`, `dataclasses`, `json`, `pathlib`, `src.engine.localization.dict_translator`, `src.robot_systems.paint.applications.dashboard.controller.paint_dashboard_controller`, `src.robot_systems.paint.applications.dashboard.dashboard_state`, `src.robot_systems.paint.applications.dashboard.model.paint_dashboard_model`, `src.robot_systems.paint.applications.dashboard.service.i_paint_dashboard_service`, `src.robot_systems.paint.applications.dashboard.service.paint_dashboard_service`, `src.robot_systems.paint.applications.dashboard.view.paint_dashboard_view`, `src.robot_systems.paint.processes.paint.configuration.models`, `src.robot_systems.paint.processes.paint.production.execution_control`, `src.robot_systems.paint.processes.paint.workflow.context`, `src.robot_systems.paint.processes.paint.workflow.machine_factory`, `src.robot_systems.paint.processes.paint.workflow.state`, `src.robot_systems.paint.processes.paint.paint_process`, `src.robot_systems.paint.processes.paint.production.service`, `src.robot_systems.paint.processes.paint.tray_dry.errors`, `src.robot_systems.paint.processes.paint.tray_dry.plate_layout`, `src.shared_contracts.events.process_events`, `types`, `unittest`, `unittest.mock`.

### `tray_config`

```python
def tray_config()
```

### `reserve`

```python
def reserve(layout, config)
```

### `TestTrayReadiness`

```python
class TestTrayReadiness(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def setUp(self)
```

```python
def test_restart_requires_confirmation_and_does_not_start(self)
```

```python
def test_confirmation_rejected_while_running_paused_or_stopping(self)
```

```python
def test_unavailable_tray_has_typed_failure(self)
```

```python
def test_active_reservation_cannot_be_cleared(self)
```

```python
def test_settings_change_preserves_occupancy_and_requires_explicit_reset(self)
```

```python
def test_reservation_cannot_implicitly_confirm_an_unknown_tray(self)
```

```python
def test_automatic_destination_does_not_require_tray_confirmation(self)
```

```python
def test_success_cannot_contain_failure(self)
```

```python
def production(self)
```

```python
def test_direct_production_is_blocked_before_capture_or_motion(self)
```

```python
def test_direct_process_start_is_blocked_and_retains_typed_failure(self)
```

```python
def test_demo_checks_tray_before_automatic_first_cycle(self)
```

```python
def test_state_handler_preserves_failure_category_and_runs_terminal_cleanup(self)
```

### `TestTrayStartController`

```python
class TestTrayStartController(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def controller(self, confirmed)
```

```python
def test_confirm_continues_requested_start_once(self)
```

```python
def test_cancel_or_dismiss_does_not_confirm_or_retry_start(self)
```

```python
def test_confirmation_failure_does_not_retry_start(self)
```

```python
def test_other_tray_failure_does_not_prompt_for_unknown_occupancy(self)
```

### `TestTrayConfirmationDialog`

```python
class TestTrayConfirmationDialog(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
@classmethod
def setUpClass(cls)
```

```python
def test_explicit_confirm_cancel_and_window_dismissal(self)
```

```python
def test_dialog_uses_current_language_for_every_profile(self)
```

## `test_unmatched_second_pass.py`

Source: [tests/robot_systems/paint/test_unmatched_second_pass.py](../../../../tests/robot_systems/paint/test_unmatched_second_pass.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `dataclasses`, `src.engine.robot.motion_sequence`, `src.robot_systems.paint.processes.paint.configuration.models`, `src.robot_systems.paint.processes.paint.workflow.handlers.workflow.pickup_handler`, `src.robot_systems.paint.processes.paint.planning.projection.command_job`, `src.robot_systems.paint.processes.paint.configuration.serializer`, `unittest`.

### `TestUnmatchedSecondPass`

```python
class TestUnmatchedSecondPass(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_process_acceleration_scale_changes_cycle_copy_only(self) -> None
```

```python
def test_process_acceleration_scale_applies_to_plate_profile_dictionaries(self) -> None
```

```python
def test_config_roundtrip_preserves_second_pass_overrides(self) -> None
```

```python
def test_second_pass_chain_unwinds_before_attach_and_contact(self) -> None
```

## `test_work_area_nesting.py`

Source: [tests/robot_systems/paint/test_work_area_nesting.py](../../../../tests/robot_systems/paint/test_work_area_nesting.py).

Imports (including optional/function-local imports; not a startup dependency list): `src.robot_systems.paint.processes.paint.production.magazine.nesting`, `unittest`.

### `WorkAreaNestingServiceTest`

```python
class WorkAreaNestingServiceTest(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_margin_and_padding_control_reservations(self)
```

```python
def test_reports_full_without_overwriting_committed_positions(self)
```

## `test_workpiece_destinations.py`

Source: [tests/robot_systems/paint/test_workpiece_destinations.py](../../../../tests/robot_systems/paint/test_workpiece_destinations.py).

Imports (including optional/function-local imports; not a startup dependency list): `src.robot_systems.paint.destinations`, `src.robot_systems.paint.processes.paint.destination`, `unittest`, `unittest.mock`.

### `TestWorkpieceDestinations`

```python
class TestWorkpieceDestinations(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_compact_pass_through_has_no_external_handoff(self)
```

```python
def test_automatic_dryer_adapter_delegates_to_coordinator(self)
```
