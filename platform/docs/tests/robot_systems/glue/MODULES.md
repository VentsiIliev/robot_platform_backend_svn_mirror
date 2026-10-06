# Module reference: `tests/robot_systems/glue`

[Package guide](README.md) · [Complete source index](../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [test_authentication_service.py](#test_authentication_servicepy)
- [test_broker_debug_plugin_integration.py](#test_broker_debug_plugin_integrationpy)
- [test_calibration_plugin_integration.py](#test_calibration_plugin_integrationpy)
- [test_calibration_settings_plugin_integration.py](#test_calibration_settings_plugin_integrationpy)
- [test_camera_settings_plugin_integration.py](#test_camera_settings_plugin_integrationpy)
- [test_contour_matching_tester_plugin_integration.py](#test_contour_matching_tester_plugin_integrationpy)
- [test_dashboard_localization.py](#test_dashboard_localizationpy)
- [test_dashboard_plugin_integration.py](#test_dashboard_plugin_integrationpy)
- [test_dashboard_preview_widget.py](#test_dashboard_preview_widgetpy)
- [test_dispensing_manual_debug_runner.py](#test_dispensing_manual_debug_runnerpy)
- [test_glue_cell_settings_integration.py](#test_glue_cell_settings_integrationpy)
- [test_glue_cell_type_resolver.py](#test_glue_cell_type_resolverpy)
- [test_glue_dashboard_controller.py](#test_glue_dashboard_controllerpy)
- [test_glue_dispensing_state_machine.py](#test_glue_dispensing_state_machinepy)
- [test_glue_job_builder_service.py](#test_glue_job_builder_servicepy)
- [test_glue_job_execution_service.py](#test_glue_job_execution_servicepy)
- [test_glue_process_driver_controller.py](#test_glue_process_driver_controllerpy)
- [test_glue_process_driver_factory.py](#test_glue_process_driver_factorypy)
- [test_glue_process_driver_model.py](#test_glue_process_driver_modelpy)
- [test_glue_process_driver_plugin_integration.py](#test_glue_process_driver_plugin_integrationpy)
- [test_glue_process_driver_service.py](#test_glue_process_driver_servicepy)
- [test_glue_process_driver_view.py](#test_glue_process_driver_viewpy)
- [test_glue_processes.py](#test_glue_processespy)
- [test_glue_robot_system.py](#test_glue_robot_systempy)
- [test_glue_settings_controller.py](#test_glue_settings_controllerpy)
- [test_glue_settings_mapper.py](#test_glue_settings_mapperpy)
- [test_glue_settings_model.py](#test_glue_settings_modelpy)
- [test_glue_workpiece.py](#test_glue_workpiecepy)
- [test_modbus_settings_plugin_integration.py](#test_modbus_settings_plugin_integrationpy)
- [test_navigation.py](#test_navigationpy)
- [test_permissions_migrator.py](#test_permissions_migratorpy)
- [test_permissions_repository.py](#test_permissions_repositorypy)
- [test_pick_and_place_workflow.py](#test_pick_and_place_workflowpy)
- [test_pickup_plane_mapper.py](#test_pickup_plane_mapperpy)
- [test_robot_settings_plugin_integration.py](#test_robot_settings_plugin_integrationpy)
- [test_targeting_refresh_wiring.py](#test_targeting_refresh_wiringpy)
- [test_tool_settings_plugin_integration.py](#test_tool_settings_plugin_integrationpy)
- [test_user_management_plugin_integration.py](#test_user_management_plugin_integrationpy)
- [test_workpiece_editor_plugin_integration.py](#test_workpiece_editor_plugin_integrationpy)
- [test_workpiece_library_plugin_integration.py](#test_workpiece_library_plugin_integrationpy)

## `__init__.py`

Source: [tests/robot_systems/glue/__init__.py](../../../../tests/robot_systems/glue/__init__.py).

No top-level functions, classes or public value declarations; inspect the source for imports or entry-point statements.

## `test_authentication_service.py`

Source: [tests/robot_systems/glue/test_authentication_service.py](../../../../tests/robot_systems/glue/test_authentication_service.py).

Tests for: src/engine/auth/authenticated_user.py src/engine/auth/authentication_service.py AuthenticatedUser wraps an AuthUserRecord and satisfies IAuthenticatedUser. AuthenticationService verifies credentials against IAuthUserRepository.

Imports (including optional/function-local imports; not a startup dependency list): `src.applications.user_management.domain.user`, `src.engine.auth.auth_user_record`, `src.engine.auth.authenticated_user`, `src.engine.auth.authentication_service`, `src.engine.auth.i_auth_user_repository`, `src.engine.auth.i_authenticated_user`, `src.engine.auth.i_authentication_service`, `unittest`, `unittest.mock`.

### `_make_record`

```python
def _make_record(user_id: str='1', password: str='pass123', role: Role=Role.OPERATOR) -> AuthUserRecord
```

### `_repo_with`

```python
def _repo_with(record: AuthUserRecord | None) -> IAuthUserRepository
```

### `TestAuthenticatedUser`

```python
class TestAuthenticatedUser(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def setUp(self)
```

```python
def test_satisfies_i_authenticated_user(self)
```

```python
def test_user_id_returns_string_of_int_id(self)
```

```python
def test_role_returns_the_users_role_enum(self)
```

```python
def test_role_value_matches(self)
```

```python
def test_record_is_accessible(self)
```

### `TestAuthenticationServiceInterface`

```python
class TestAuthenticationServiceInterface(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_satisfies_i_authentication_service(self)
```

### `TestAuthenticate`

```python
class TestAuthenticate(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_returns_authenticated_user_on_correct_credentials(self)
```

```python
def test_returns_none_on_wrong_password(self)
```

```python
def test_returns_none_when_user_not_found(self)
```

```python
def test_role_on_returned_user_matches_stored_role(self)
```

```python
def test_looks_up_user_by_provided_user_id(self)
```

### `TestAuthenticateQr`

```python
class TestAuthenticateQr(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_valid_payload_returns_authenticated_user(self)
```

```python
def test_wrong_password_in_payload_returns_none(self)
```

```python
def test_malformed_payload_returns_none(self)
```

```python
def test_empty_payload_returns_none(self)
```

## `test_broker_debug_plugin_integration.py`

Source: [tests/robot_systems/glue/test_broker_debug_plugin_integration.py](../../../../tests/robot_systems/glue/test_broker_debug_plugin_integration.py).

Plugin integration tests for BrokerDebug application. Verifies: - ApplicationSpec is declared in GlueRobotSystem.shell.applications - factory produces a WidgetApplication

Imports (including optional/function-local imports; not a startup dependency list): `src.applications.base.widget_application`, `src.robot_systems.glue.glue_robot_system`, `unittest`, `unittest.mock`.

### `_make_robot_system`

```python
def _make_robot_system()
```

### `_spec`

```python
def _spec()
```

### `TestBrokerDebugApplicationSpec`

```python
class TestBrokerDebugApplicationSpec(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_spec_declared(self)
```

```python
def test_spec_folder_id(self)
```

```python
def test_spec_has_factory(self)
```

```python
def test_spec_icon_set(self)
```

### `TestBrokerDebugApplicationFactory`

```python
class TestBrokerDebugApplicationFactory(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_factory_returns_widget_application(self)
```

```python
def test_register_stores_messaging_service(self)
```

## `test_calibration_plugin_integration.py`

Source: [tests/robot_systems/glue/test_calibration_plugin_integration.py](../../../../tests/robot_systems/glue/test_calibration_plugin_integration.py).

Imports (including optional/function-local imports; not a startup dependency list): `src.applications.base.widget_application`, `src.engine.common_service_ids`, `src.robot_systems.glue.component_ids`, `src.robot_systems.glue.glue_robot_system`, `unittest`, `unittest.mock`.

### `_make_robot_system`

```python
def _make_robot_system()
```

### `TestCalibrationApplicationSpec`

```python
class TestCalibrationApplicationSpec(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_spec_declared(self)
```

```python
def test_spec_folder_id(self)
```

```python
def test_spec_has_factory(self)
```

```python
def test_spec_icon_set(self)
```

### `TestCalibrationApplicationFactory`

```python
class TestCalibrationApplicationFactory(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_factory_returns_widget_application(self)
```

```python
def test_factory_fetches_vision_service_as_optional(self)
```

```python
def test_register_stores_messaging_service(self)
```

```python
def test_widget_factory_forwards_messaging_service(self)
```

## `test_calibration_settings_plugin_integration.py`

Source: [tests/robot_systems/glue/test_calibration_settings_plugin_integration.py](../../../../tests/robot_systems/glue/test_calibration_settings_plugin_integration.py).

Imports (including optional/function-local imports; not a startup dependency list): `src.applications.base.widget_application`, `src.engine.common_service_ids`, `src.robot_systems.glue.glue_robot_system`, `unittest`, `unittest.mock`.

### `_make_robot_system`

```python
def _make_robot_system()
```

### `_spec`

```python
def _spec()
```

### `TestCalibrationSettingsApplicationSpec`

```python
class TestCalibrationSettingsApplicationSpec(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_spec_declared(self)
```

```python
def test_spec_folder_id(self)
```

```python
def test_spec_has_factory(self)
```

### `TestCalibrationSettingsApplicationFactory`

```python
class TestCalibrationSettingsApplicationFactory(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_factory_returns_widget_application(self)
```

```python
def test_register_stores_messaging_service(self)
```

## `test_camera_settings_plugin_integration.py`

Source: [tests/robot_systems/glue/test_camera_settings_plugin_integration.py](../../../../tests/robot_systems/glue/test_camera_settings_plugin_integration.py).

Plugin integration tests for CameraSettings application. Verifies: - ApplicationSpec is declared in GlueRobotSystem.shell.applications - factory produces a WidgetApplication - vision service is fetched as optional

Imports (including optional/function-local imports; not a startup dependency list): `src.applications.base.widget_application`, `src.engine.common_service_ids`, `src.robot_systems.glue.component_ids`, `src.robot_systems.glue.glue_robot_system`, `unittest`, `unittest.mock`.

### `_make_robot_system`

```python
def _make_robot_system()
```

### `_spec`

```python
def _spec()
```

### `TestCameraSettingsApplicationSpec`

```python
class TestCameraSettingsApplicationSpec(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_spec_declared(self)
```

```python
def test_spec_folder_id(self)
```

```python
def test_spec_has_factory(self)
```

```python
def test_spec_icon_set(self)
```

### `TestCameraSettingsApplicationFactory`

```python
class TestCameraSettingsApplicationFactory(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_factory_returns_widget_application(self)
```

```python
def test_factory_fetches_vision_service_as_optional(self)
```

```python
def test_register_stores_messaging_service(self)
```

## `test_contour_matching_tester_plugin_integration.py`

Source: [tests/robot_systems/glue/test_contour_matching_tester_plugin_integration.py](../../../../tests/robot_systems/glue/test_contour_matching_tester_plugin_integration.py).

Plugin integration tests for ContourMatchingTester application. Verifies: - ApplicationSpec is declared in GlueRobotSystem.shell.applications - factory produces a WidgetApplication - vision service is fetched as optional

Imports (including optional/function-local imports; not a startup dependency list): `src.applications.base.widget_application`, `src.engine.common_service_ids`, `src.robot_systems.glue.component_ids`, `src.robot_systems.glue.glue_robot_system`, `unittest`, `unittest.mock`.

### `_make_robot_system`

```python
def _make_robot_system()
```

### `_spec`

```python
def _spec()
```

### `TestContourMatchingTesterApplicationSpec`

```python
class TestContourMatchingTesterApplicationSpec(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_spec_declared(self)
```

```python
def test_spec_folder_id(self)
```

```python
def test_spec_has_factory(self)
```

```python
def test_spec_icon_set(self)
```

### `TestContourMatchingTesterApplicationFactory`

```python
class TestContourMatchingTesterApplicationFactory(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_factory_returns_widget_application(self)
```

```python
def test_factory_fetches_vision_service_as_optional(self)
```

```python
def test_register_stores_messaging_service(self)
```

## `test_dashboard_localization.py`

Source: [tests/robot_systems/glue/test_dashboard_localization.py](../../../../tests/robot_systems/glue/test_dashboard_localization.py).

Imports (including optional/function-local imports; not a startup dependency list): `PyQt6.QtCore`, `PyQt6.QtWidgets`, `pathlib`, `src.engine.localization.localization_service`, `src.robot_systems.glue.applications.dashboard`, `src.robot_systems.glue.applications.dashboard.config`, `src.robot_systems.glue.applications.dashboard.controller.glue_dashboard_controller`, `src.robot_systems.glue.applications.dashboard.ui.system_status_widget`, `src.robot_systems.glue.applications.dashboard.ui.widgets.GlueMeterCard`, `src.robot_systems.glue.applications.dashboard.view.glue_dashboard_view`, `tempfile`, `unittest`, `unittest.mock`.

### `TestDashboardLocalization`

```python
class TestDashboardLocalization(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
@classmethod
def setUpClass(cls)
```

```python
def setUp(self)
```

```python
def test_glue_meter_card_retranslates_title_and_state_tooltip(self)
```

```python
def test_system_status_widget_retranslates_labels_and_badges(self)
```

```python
def test_dashboard_buttons_start_translated_on_initial_load(self)
```

## `test_dashboard_plugin_integration.py`

Source: [tests/robot_systems/glue/test_dashboard_plugin_integration.py](../../../../tests/robot_systems/glue/test_dashboard_plugin_integration.py).

Imports (including optional/function-local imports; not a startup dependency list): `src.applications.base.widget_application`, `src.engine.process.process_requirements`, `src.engine.system.i_system_manager`, `src.robot_systems.glue.applications.dashboard.service.glue_dashboard_service`, `src.robot_systems.glue.component_ids`, `src.robot_systems.glue.domain.glue_job_execution_service`, `src.robot_systems.glue.glue_robot_system`, `src.robot_systems.glue.processes.glue_dispensing.dispensing_config`, `src.robot_systems.glue.processes.glue_operation_coordinator`, `src.robot_systems.glue.processes.glue_operation_mode`, `src.robot_systems.glue.processes.glue_process`, `src.robot_systems.glue.settings.cells`, `src.robot_systems.glue.settings.glue_types`, `src.shared_contracts.events.process_events`, `unittest`, `unittest.mock`.

### `_make_cell`

```python
def _make_cell(cell_id: int, glue_type: str='Type A', capacity: float=5000.0) -> CellConfig
```

### `_make_cells`

```python
def _make_cells(*cell_ids: int) -> GlueCellsConfig
```

### `_make_catalog`

```python
def _make_catalog(*names: str) -> GlueCatalog
```

### `_make_messaging`

```python
def _make_messaging()
```

### `_make_robot_service`

```python
def _make_robot_service()
```

### `_make_navigation_service`

```python
def _make_navigation_service()
```

### `_make_motor_service`

```python
def _make_motor_service()
```

### `_make_glue_process`

```python
def _make_glue_process(robot_service=None, messaging=None, navigation_service=None, **kwargs)
```

### `_make_settings_service`

```python
def _make_settings_service(cells=None, catalog=None)
```

### `_make_runner`

```python
def _make_runner()
```

### `_make_dashboard_service`

```python
def _make_dashboard_service(cells=None, catalog=None, runner=None, weight_service=None, execution_service=None)
```

### `_make_robot_system`

```python
def _make_robot_system(cells=None, catalog=None)
```

### `TestDashboardApplicationSpec`

```python
class TestDashboardApplicationSpec(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_spec_declared(self)
```

```python
def test_spec_folder_id(self)
```

```python
def test_spec_has_factory(self)
```

```python
def test_spec_icon_set(self)
```

### `TestDashboardApplicationFactory`

```python
class TestDashboardApplicationFactory(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_factory_returns_widget_application(self)
```

```python
def test_factory_accesses_coordinator(self)
```

```python
def test_register_stores_messaging_service(self)
```

```python
def test_widget_factory_forwards_messaging_service(self)
```

```python
def test_widget_factory_passes_execution_service(self)
```

```python
def test_widget_factory_without_vision_passes_no_execution_service(self)
```

### `TestGlueDashboardServiceCommands`

```python
class TestGlueDashboardServiceCommands(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_start_delegates_to_runner(self)
```

```python
def test_start_in_spray_only_mode_still_delegates_to_runner(self)
```

```python
def test_start_in_pick_and_spray_mode_keeps_runner_sequence(self)
```

```python
def test_stop_delegates_to_runner(self)
```

```python
def test_pause_delegates_to_runner(self)
```

```python
def test_resume_delegates_to_runner(self)
```

```python
def test_reset_errors_delegates_to_runner(self)
```

```python
def test_clean_delegates_to_runner(self)
```

### `TestGlueDashboardServiceSetMode`

```python
class TestGlueDashboardServiceSetMode(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_set_mode_spray_only_passes_enum_to_runner(self)
```

```python
def test_set_mode_pick_and_spray_passes_enum_to_runner(self)
```

### `TestGlueDashboardServiceQueries`

```python
class TestGlueDashboardServiceQueries(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_get_cells_count_correct(self)
```

```python
def test_get_cells_count_single(self)
```

```python
def test_get_cells_count_returns_zero_on_error(self)
```

```python
def test_get_cell_capacity_returns_correct_value(self)
```

```python
def test_get_cell_capacity_fallback_on_missing_cell(self)
```

```python
def test_get_cell_capacity_fallback_on_error(self)
```

```python
def test_get_cell_glue_type_correct(self)
```

```python
def test_get_cell_glue_type_none_on_missing(self)
```

```python
def test_get_all_glue_types_returns_names(self)
```

```python
def test_get_all_glue_types_empty_on_error(self)
```

```python
def test_get_initial_cell_state_returns_none(self)
```

```python
def test_get_current_robot_image_position_uses_inverse_transformer(self)
```

### `TestGlueDashboardServiceConnectionState`

```python
class TestGlueDashboardServiceConnectionState(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_disconnected_when_no_weight_service(self)
```

```python
def test_delegates_to_weight_service_get_cell_state(self)
```

```python
def test_disconnected_on_weight_service_exception(self)
```

### `TestGlueDashboardServiceChangeGlue`

```python
class TestGlueDashboardServiceChangeGlue(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_change_glue_saves_updated_cells(self)
```

```python
def test_change_glue_only_updates_target_cell(self)
```

```python
def test_change_glue_saves_with_correct_key(self)
```

```python
def test_change_glue_missing_cell_does_not_save(self)
```

```python
def test_change_glue_exception_does_not_propagate(self)
```

### `TestGlueProcess`

```python
class TestGlueProcess(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_initial_state_idle(self)
```

```python
def test_process_id_is_glue(self)
```

```python
def test_start_transitions_to_running(self)
```

```python
def test_stop_from_running_transitions_to_stopped(self)
```

```python
def test_pause_transitions_to_paused(self)
```

```python
def test_resume_from_paused_transitions_to_running(self)
```

```python
def test_restart_from_stopped(self)
```

```python
def test_set_error_forces_error_state(self)
```

```python
def test_reset_errors_returns_to_idle(self)
```

```python
def test_stop_from_idle_is_blocked(self)
```

```python
def test_pause_from_idle_is_blocked(self)
```

```python
def test_start_does_not_call_enable_robot(self)
```

Robot enabling is the system's responsibility at startup, not per-process.

```python
def test_stop_calls_stop_motion(self)
```

```python
def test_pause_calls_stop_motion(self)
```

```python
def test_resume_transitions_state_to_running(self)
```

```python
def test_start_from_paused_calls_on_resume_not_on_start(self)
```

start() from PAUSED must route to _on_resume — stop_motion not called again.

```python
def test_hook_error_forces_error_state(self)
```

```python
def test_hook_error_does_not_propagate_to_caller(self)
```

```python
def test_hook_error_publishes_error_event_with_message(self)
```

```python
def test_publishes_active_topic_on_start(self)
```

```python
def test_publishes_process_specific_topic_on_start(self)
```

```python
def test_active_topic_published_before_specific_topic(self)
```

```python
def test_system_manager_acquire_blocks_start_when_false(self)
```

```python
def test_system_manager_acquire_called_with_process_id(self)
```

```python
def test_system_manager_release_called_on_stop(self)
```

```python
def test_system_manager_release_called_on_reset_errors_idle(self)
```

```python
def test_requirements_blocks_start_when_service_missing(self)
```

```python
def test_requirements_allows_start_when_services_available(self)
```

## `test_dashboard_preview_widget.py`

Source: [tests/robot_systems/glue/test_dashboard_preview_widget.py](../../../../tests/robot_systems/glue/test_dashboard_preview_widget.py).

Imports (including optional/function-local imports; not a startup dependency list): `PyQt6.QtCore`, `PyQt6.QtWidgets`, `numpy`, `pathlib`, `src.engine.localization.localization_service`, `src.robot_systems.glue.applications.dashboard.ui.dashboard_preview_widget`, `tempfile`, `unittest`.

### `TestDashboardPreviewWidget`

```python
class TestDashboardPreviewWidget(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
@classmethod
def setUpClass(cls)
```

```python
def test_live_primary_with_inset_renders_progress_thumbnail(self)
```

```python
def test_progress_primary_with_inset_disabled_renders_only_progress(self)
```

```python
def test_progress_overlay_draws_completed_and_pending_segments_with_different_colors(self)
```

```python
def test_progress_overlay_uses_robot_point_for_continuous_progress(self)
```

```python
def test_preview_controls_retranslate(self)
```

## `test_dispensing_manual_debug_runner.py`

Source: [tests/robot_systems/glue/test_dispensing_manual_debug_runner.py](../../../../tests/robot_systems/glue/test_dispensing_manual_debug_runner.py).

Imports (including optional/function-local imports; not a startup dependency list): `src.robot_systems.glue.processes.glue_dispensing.manual_debug_runner`, `unittest`.

### `TestDispensingManualDriver`

```python
class TestDispensingManualDriver(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_snapshot_includes_machine_and_context_details(self)
```

```python
def test_step_advances_machine_one_state(self)
```

```python
def test_move_robot_to_current_start_uses_loaded_path(self)
```

## `test_glue_cell_settings_integration.py`

Source: [tests/robot_systems/glue/test_glue_cell_settings_integration.py](../../../../tests/robot_systems/glue/test_glue_cell_settings_integration.py).

Imports (including optional/function-local imports; not a startup dependency list): `src.applications.base.widget_application`, `src.applications.glue_cell_settings.model.glue_cell_settings_model`, `src.applications.glue_cell_settings.model.mapper`, `src.applications.glue_cell_settings.service.glue_cell_settings_service`, `src.engine.hardware.weight.config`, `src.robot_systems.glue.component_ids`, `src.robot_systems.glue.glue_robot_system`, `src.robot_systems.glue.settings.cells`, `src.robot_systems.glue.settings.dispense_channels`, `unittest`, `unittest.mock`.

### `_calib`

```python
def _calib()
```

### `_meas`

```python
def _meas()
```

### `_cell`

```python
def _cell(cid)
```

### `_cells`

```python
def _cells(*ids)
```

### `_make_robot_system`

```python
def _make_robot_system(cells=None)
```

### `_spec`

```python
def _spec()
```

### `TestDispenseChannelSettingsApplicationSpec`

```python
class TestDispenseChannelSettingsApplicationSpec(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_spec_declared(self)
```

```python
def test_spec_folder_id(self)
```

```python
def test_spec_has_factory(self)
```

```python
def test_spec_icon_set(self)
```

```python
def test_spec_name(self)
```

### `TestDispenseChannelSettingsApplicationFactory`

```python
class TestDispenseChannelSettingsApplicationFactory(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_factory_returns_widget_application(self)
```

```python
def test_factory_passes_weight_service(self)
```

```python
def test_factory_works_without_weight_service(self)
```

```python
def test_widget_factory_callable(self)
```

### `TestGlueCellsSettingsSpec`

```python
class TestGlueCellsSettingsSpec(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_spec_declared(self)
```

```python
def test_spec_serializer_type(self)
```

```python
def test_spec_path(self)
```

```python
def test_serializer_default_has_cells(self)
```

```python
def test_serializer_roundtrip(self)
```

```python
def test_serializer_settings_type(self)
```

### `TestDispenseChannelsSettingsSpec`

```python
class TestDispenseChannelsSettingsSpec(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_spec_declared(self)
```

```python
def test_spec_serializer_type(self)
```

```python
def test_spec_path(self)
```

```python
def test_serializer_default_has_channels(self)
```

### `TestWeightServiceSpec`

```python
class TestWeightServiceSpec(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_weight_service_spec_declared(self)
```

```python
def test_weight_service_optional(self)
```

```python
def test_weight_service_has_builder(self)
```

### `TestGlueCellSettingsServiceSaveAndPush`

```python
class TestGlueCellSettingsServiceSaveAndPush(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_save_persists_and_pushes(self)
```

```python
def test_save_without_weight_service_still_persists(self)
```

## `test_glue_cell_type_resolver.py`

Source: [tests/robot_systems/glue/test_glue_cell_type_resolver.py](../../../../tests/robot_systems/glue/test_glue_cell_type_resolver.py).

Imports (including optional/function-local imports; not a startup dependency list): `src.engine.hardware.weight.config`, `src.robot_systems.glue.service_builders`, `unittest`.

### `_cell`

```python
def _cell(cell_id: int, glue_type: str, motor_address: int)
```

### `TestGlueCellTypeResolver`

```python
class TestGlueCellTypeResolver(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_resolve_accepts_motor_address_zero(self)
```

```python
def test_resolve_returns_matching_nonzero_motor_address(self)
```

```python
def test_resolve_returns_minus_one_when_type_missing(self)
```

## `test_glue_dashboard_controller.py`

Source: [tests/robot_systems/glue/test_glue_dashboard_controller.py](../../../../tests/robot_systems/glue/test_glue_dashboard_controller.py).

Imports (including optional/function-local imports; not a startup dependency list): `src.robot_systems.glue.applications.dashboard.controller.glue_dashboard_controller`, `src.shared_contracts.events.notification_events`, `src.shared_contracts.events.process_events`, `unittest`, `unittest.mock`.

### `TestGlueDashboardController`

```python
class TestGlueDashboardController(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_on_start_runs_model_start_in_background_helper(self)
```

```python
def test_on_start_does_nothing_when_inactive(self)
```

```python
def test_process_error_publishes_shared_notification_event(self)
```

```python
@patch('src.robot_systems.glue.applications.dashboard.controller.glue_dashboard_controller.QCoreApplication.translate')
def test_translation_helper_falls_back_to_source_text_when_qt_returns_empty(self, mock_translate)
```

## `test_glue_dispensing_state_machine.py`

Source: [tests/robot_systems/glue/test_glue_dispensing_state_machine.py](../../../../tests/robot_systems/glue/test_glue_dispensing_state_machine.py).

Imports (including optional/function-local imports; not a startup dependency list): `src.robot_systems.glue.processes.glue_dispensing.context_ops.pump_thread_ops`, `src.robot_systems.glue.processes.glue_dispensing.dispensing_config`, `src.robot_systems.glue.processes.glue_dispensing.dispensing_context`, `src.robot_systems.glue.processes.glue_dispensing.dispensing_error`, `src.robot_systems.glue.processes.glue_dispensing.dispensing_machine_factory`, `src.robot_systems.glue.processes.glue_dispensing.dispensing_state`, `src.robot_systems.glue.processes.glue_dispensing.state_handlers.hardware.generator_handlers`, `src.robot_systems.glue.processes.glue_dispensing.state_handlers.hardware.handle_starting_pump_adjustment_thread`, `src.robot_systems.glue.processes.glue_dispensing.state_handlers.hardware.handle_waiting_for_pump_thread_ready`, `src.robot_systems.glue.processes.glue_dispensing.state_handlers.hardware.pump_handlers`, `src.robot_systems.glue.processes.glue_dispensing.state_handlers.motion.handle_advancing_path`, `src.robot_systems.glue.processes.glue_dispensing.state_handlers.motion.handle_moving_to_first_point`, `src.robot_systems.glue.processes.glue_dispensing.state_handlers.motion.handle_sending_path_points`, `src.robot_systems.glue.processes.glue_dispensing.state_handlers.startup.handle_issuing_move_to_first_point`, `src.robot_systems.glue.processes.glue_dispensing.state_handlers.startup.handle_loading_current_path`, `src.robot_systems.glue.processes.glue_dispensing.state_handlers.startup.handle_loading_path`, `src.robot_systems.glue.processes.glue_dispensing.state_handlers.startup.handle_resuming`, `src.robot_systems.glue.processes.glue_dispensing.state_handlers.startup.handle_starting`, `src.robot_systems.glue.processes.glue_dispensing.state_handlers.terminal.terminal_handlers`, `src.robot_systems.glue.processes.glue_dispensing.state_handlers.waiting.handle_routing_path_completion_wait`, `src.robot_systems.glue.processes.glue_dispensing.state_handlers.waiting.handle_waiting_for_final_position`, `src.robot_systems.glue.processes.glue_dispensing.state_handlers.waiting.handle_waiting_for_pump_thread`, `src.robot_systems.glue.settings.glue`, `unittest`, `unittest.mock`.

### `_settings`

```python
def _settings(**overrides)
```

### `_point`

```python
def _point(x)
```

### `_make_context`

```python
def _make_context()
```

### `_make_machine_context`

```python
def _make_machine_context()
```

### `_FakePumpThread`

```python
class _FakePumpThread:
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, alive_values, result=None)
```

```python
def is_alive(self)
```

```python
def join(self, timeout=None)
```

### `TestHandleStarting`

```python
class TestHandleStarting(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_routes_fresh_start_to_loading_path(self)
```

```python
def test_routes_resume_to_resuming_state(self)
```

### `TestHandleLoadingPath`

```python
class TestHandleLoadingPath(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_routes_non_empty_path_to_loading_current_path(self)
```

```python
def test_skips_empty_paths_and_stays_in_loading_path(self)
```

### `TestHandleLoadingCurrentPath`

```python
class TestHandleLoadingCurrentPath(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_loads_current_path_and_prepares_first_move(self)
```

### `TestHandleIssuingMoveToFirstPoint`

```python
class TestHandleIssuingMoveToFirstPoint(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_commands_move_to_first_point_using_segment_motion_settings(self)
```

```python
def test_commands_move_to_first_point_using_global_motion_settings_when_segment_disabled(self)
```

```python
def test_records_error_when_move_to_first_point_raises(self)
```

```python
def test_returns_paused_when_move_to_first_point_is_interrupted_by_pause(self)
```

```python
def test_returns_stopped_when_move_to_first_point_is_interrupted_by_stop(self)
```

### `TestHandleResuming`

```python
class TestHandleResuming(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_resume_from_execution_state_slices_path_from_saved_progress(self)
```

```python
def test_resume_after_path_completion_advances_to_next_path(self)
```

```python
def test_resume_before_execution_restarts_from_path_beginning(self)
```

```python
def test_resume_waiting_for_final_position_restarts_segment_from_submission_point(self)
```

```python
def test_resume_waiting_for_final_position_after_completion_routes_to_pump_shutdown(self)
```

### `TestHandleSendingPathPoints`

```python
class TestHandleSendingPathPoints(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_pause_before_trajectory_submission_saves_progress_and_origin_state(self)
```

```python
def test_submits_remaining_segment_as_single_trajectory(self)
```

```python
def test_records_error_when_trajectory_submission_fails(self)
```

### `TestHandleMovingToFirstPoint`

```python
class TestHandleMovingToFirstPoint(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_reaching_first_point_advances_send_cursor_to_second_point(self)
```

```python
def test_records_error_when_current_path_is_missing(self)
```

### `TestHandlePathCompletionWait`

```python
class TestHandlePathCompletionWait(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_routes_to_pump_thread_wait_when_thread_exists(self)
```

```python
def test_routes_to_final_position_wait_when_no_thread_exists(self)
```

```python
def test_pause_while_waiting_for_pump_thread_captures_progress(self)
```

```python
def test_waiting_for_pump_thread_records_error_details(self)
```

```python
def test_waiting_for_pump_thread_records_worker_exception(self)
```

```python
def test_position_poll_path_completes_when_robot_reaches_final_point(self)
```

```python
def test_waiting_for_final_position_uses_execution_status_before_completing(self)
```

```python
def test_pause_waiting_for_final_position_preserves_segment_start_for_resume(self)
```

```python
def test_resume_waiting_for_final_position_uses_saved_mid_segment_progress(self)
```

```python
def test_waiting_for_final_position_fails_when_reported_task_finishes_with_error(self)
```

### `TestHandlePumpAdjustmentStartup`

```python
class TestHandlePumpAdjustmentStartup(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
@patch.object(DispensingPumpThreadOps, 'start_for_current_path', autospec=True)
def test_starts_thread_with_saved_progress_and_waits_for_ready(self, start_thread)
```

```python
def test_waiting_for_ready_transitions_to_sending_points(self)
```

```python
def test_waiting_for_ready_without_thread_skips_to_sending_points(self)
```

```python
def test_waiting_for_ready_records_error_without_ready_event(self)
```

```python
@patch.object(DispensingPumpThreadOps, 'start_for_current_path', autospec=True)
def test_starting_thread_records_startup_exception(self, start_thread)
```

### `TestHandlePumpStates`

```python
class TestHandlePumpStates(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_turning_on_pump_starts_motor_once(self)
```

```python
def test_turning_on_pump_records_error_for_invalid_motor_address(self)
```

```python
def test_turns_pump_off_before_advancing_path(self)
```

```python
def test_turning_on_pump_records_controller_exception_details(self)
```

```python
def test_advancing_path_moves_to_next_path(self)
```

```python
def test_advancing_last_path_routes_to_completed(self)
```

```python
def test_turning_off_pump_records_controller_exception_details(self)
```

### `TestHandleGeneratorStates`

```python
class TestHandleGeneratorStates(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_turning_on_generator_starts_generator_once(self)
```

```python
def test_turning_on_generator_waits_before_starting_pump_when_configured(self)
```

```python
def test_completed_keeps_pump_cleanup_and_routes_to_generator_shutdown(self)
```

```python
def test_turning_off_generator_finishes_completion(self)
```

```python
def test_turning_off_generator_records_error_details(self)
```

### `TestTerminalErrorHandling`

```python
class TestTerminalErrorHandling(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_error_state_cleans_up_and_returns_idle(self)
```

### `TestDispensingMachineIntegration`

```python
class TestDispensingMachineIntegration(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_machine_submits_multi_point_path_as_single_trajectory(self)
```

```python
def test_machine_completes_single_point_path(self)
```

```python
def test_machine_stops_and_cleans_up_when_stop_requested_before_start(self)
```

```python
def test_machine_skips_empty_path_and_completes_next_path(self)
```

## `test_glue_job_builder_service.py`

Source: [tests/robot_systems/glue/test_glue_job_builder_service.py](../../../../tests/robot_systems/glue/test_glue_job_builder_service.py).

Imports (including optional/function-local imports; not a startup dependency list): `numpy`, `src.engine.robot.targeting.vision_target_resolver`, `src.robot_systems.glue.domain.glue_job_builder_service`, `src.robot_systems.glue.domain.workpieces.model.glue_workpiece`, `unittest`, `unittest.mock`.

### `_make_resolver`

```python
def _make_resolver(offset_x=100.0, offset_y=200.0, z=0.0)
```

Create a mock VisionTargetResolver that offsets coordinates.

### `_segment_settings`

```python
def _segment_settings(**overrides)
```

### `_raw_segment`

```python
def _raw_segment(points, settings=None)
```

### `_workpiece`

```python
def _workpiece(workpiece_id='111')
```

### `_glue_workpiece`

```python
def _glue_workpiece(workpiece_id='111')
```

### `TestGlueJobBuilderService`

```python
class TestGlueJobBuilderService(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_build_job_extracts_segments_in_contour_then_fill_order(self)
```

```python
def test_build_job_flattens_nested_contour_points(self)
```

```python
def test_build_job_preserves_segment_settings_and_metadata(self)
```

```python
def test_build_job_accepts_glue_workpiece_objects(self)
```

```python
def test_to_process_paths_returns_glue_process_ready_tuples(self)
```

```python
def test_build_job_raises_when_segment_settings_are_missing(self)
```

```python
def test_build_job_raises_when_segment_has_no_points(self)
```

```python
def test_build_job_accepts_numpy_array_contours(self)
```

```python
def test_build_job_raises_when_resolver_is_unavailable(self)
```

```python
def test_build_job_uses_live_resolver_getter(self)
```

```python
def test_build_job_uses_rz_from_segment_settings(self)
```

## `test_glue_job_execution_service.py`

Source: [tests/robot_systems/glue/test_glue_job_execution_service.py](../../../../tests/robot_systems/glue/test_glue_job_execution_service.py).

Imports (including optional/function-local imports; not a startup dependency list): `numpy`, `src.robot_systems.glue.domain.glue_job_builder_service`, `src.robot_systems.glue.domain.glue_job_execution_service`, `src.shared_contracts.events.glue_overlay_events`, `threading`, `unittest`, `unittest.mock`.

### `_matched_workpiece`

```python
def _matched_workpiece(workpiece_id='wp-1')
```

### `_job`

```python
def _job() -> GlueJob
```

### `TestGlueJobExecutionService`

```python
class TestGlueJobExecutionService(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_cancel_pending_stops_robot_when_prepare_running(self)
```

```python
def test_prepare_and_load_fails_when_robot_cannot_reach_capture_position(self)
```

```python
def test_prepare_and_load_moves_to_capture_position_and_waits_before_matching(self)
```

```python
def test_prepare_and_load_publishes_overlay_snapshot_when_job_loads(self)
```

```python
def test_prepare_and_load_returns_cancelled_when_cancelled_during_stabilization(self)
```

```python
def test_prepare_and_load_returns_cancelled_when_navigation_wait_is_cancelled(self)
```

```python
def test_prepare_and_load_fails_when_no_workpieces_match(self)
```

```python
def test_prepare_and_load_fails_when_job_build_raises(self)
```

```python
def test_prepare_and_load_fails_when_built_job_has_no_segments(self)
```

```python
def test_prepare_and_load_sets_paths_and_returns_loaded_result(self)
```

```python
def test_prepare_load_and_start_starts_process(self)
```

```python
def test_prepare_load_and_start_returns_start_failure(self)
```

## `test_glue_process_driver_controller.py`

Source: [tests/robot_systems/glue/test_glue_process_driver_controller.py](../../../../tests/robot_systems/glue/test_glue_process_driver_controller.py).

Imports (including optional/function-local imports; not a startup dependency list): `src.robot_systems.glue.applications.glue_process_driver.controller.glue_process_driver_controller`, `src.robot_systems.glue.component_ids`, `src.shared_contracts.events.glue_process_events`, `src.shared_contracts.events.process_events`, `unittest`, `unittest.mock`.

### `_make_view`

```python
def _make_view()
```

### `TestGlueProcessDriverController`

```python
class TestGlueProcessDriverController(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_init_wires_view_signals(self)
```

```python
def test_load_pushes_initial_snapshot_to_view(self)
```

```python
def test_capture_and_match_updates_view(self)
```

```python
def test_build_job_updates_view(self)
```

```python
def test_load_job_delegates_to_model(self)
```

```python
def test_process_commands_delegate_to_model(self)
```

```python
def test_refresh_updates_process_snapshot(self)
```

```python
def test_stop_is_idempotent_and_clears_subscriptions(self)
```

```python
def test_view_destroyed_stops_controller(self)
```

```python
def test_process_state_event_refreshes_snapshot_through_broker_path(self)
```

```python
def test_diagnostics_event_pushes_snapshot_directly(self)
```

## `test_glue_process_driver_factory.py`

Source: [tests/robot_systems/glue/test_glue_process_driver_factory.py](../../../../tests/robot_systems/glue/test_glue_process_driver_factory.py).

Imports (including optional/function-local imports; not a startup dependency list): `PyQt6.QtWidgets`, `os`, `src.engine.core.i_messaging_service`, `src.robot_systems.glue.applications.glue_process_driver.controller.glue_process_driver_controller`, `src.robot_systems.glue.applications.glue_process_driver.glue_process_driver_factory`, `src.robot_systems.glue.applications.glue_process_driver.model.glue_process_driver_model`, `src.robot_systems.glue.applications.glue_process_driver.service.i_glue_process_driver_service`, `src.robot_systems.glue.applications.glue_process_driver.view.glue_process_driver_view`, `sys`, `unittest`, `unittest.mock`.

### `TestGlueProcessDriverFactory`

```python
class TestGlueProcessDriverFactory(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
@classmethod
def setUpClass(cls)
```

```python
def test_build_returns_view(self)
```

```python
def test_build_attaches_controller(self)
```

```python
def test_build_creates_model(self)
```

## `test_glue_process_driver_model.py`

Source: [tests/robot_systems/glue/test_glue_process_driver_model.py](../../../../tests/robot_systems/glue/test_glue_process_driver_model.py).

Imports (including optional/function-local imports; not a startup dependency list): `src.robot_systems.glue.applications.glue_process_driver.model.glue_process_driver_model`, `unittest`, `unittest.mock`.

### `TestGlueProcessDriverModel`

```python
class TestGlueProcessDriverModel(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_load_caches_initial_process_snapshot(self)
```

```python
def test_capture_and_match_updates_match_cache(self)
```

```python
def test_select_and_build_job_updates_cached_job(self)
```

```python
def test_process_commands_delegate_to_service(self)
```

## `test_glue_process_driver_plugin_integration.py`

Source: [tests/robot_systems/glue/test_glue_process_driver_plugin_integration.py](../../../../tests/robot_systems/glue/test_glue_process_driver_plugin_integration.py).

Imports (including optional/function-local imports; not a startup dependency list): `PyQt6.QtWidgets`, `os`, `src.applications.base.widget_application`, `src.engine.common_service_ids`, `src.robot_systems.glue.component_ids`, `src.robot_systems.glue.glue_robot_system`, `sys`, `unittest`, `unittest.mock`.

### `_spec`

```python
def _spec()
```

### `_make_robot_system`

```python
def _make_robot_system()
```

### `TestGlueProcessDriverApplicationSpec`

```python
class TestGlueProcessDriverApplicationSpec(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_spec_declared(self)
```

```python
def test_spec_folder_id(self)
```

```python
def test_spec_has_factory(self)
```

```python
def test_spec_icon_set(self)
```

### `TestGlueProcessDriverApplicationFactory`

```python
class TestGlueProcessDriverApplicationFactory(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
@classmethod
def setUpClass(cls)
```

```python
def test_factory_returns_widget_application(self)
```

```python
def test_factory_fetches_vision_service_as_optional(self)
```

```python
def test_register_stores_messaging_service(self)
```

```python
def test_widget_factory_passes_registered_broker(self)
```

```python
def test_widget_factory_configures_execution_service(self)
```

## `test_glue_process_driver_service.py`

Source: [tests/robot_systems/glue/test_glue_process_driver_service.py](../../../../tests/robot_systems/glue/test_glue_process_driver_service.py).

Imports (including optional/function-local imports; not a startup dependency list): `src.robot_systems.glue.applications.glue_process_driver.service.glue_process_driver_service`, `unittest`, `unittest.mock`.

### `_matched_workpiece`

```python
def _matched_workpiece(workpiece_id='wp-1')
```

### `TestGlueProcessDriverService`

```python
class TestGlueProcessDriverService(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_capture_and_match_exposes_match_summary(self)
```

```python
def test_capture_and_match_stores_latest_match_result(self)
```

```python
def test_build_job_from_latest_match_uses_job_builder(self)
```

```python
def test_load_latest_job_passes_process_ready_paths_to_glue_process(self)
```

```python
def test_get_latest_job_summary_exposes_segment_metadata(self)
```

```python
def test_build_job_from_latest_match_requires_prior_match_result(self)
```

```python
def test_select_matched_workpieces_limits_job_build_input(self)
```

```python
def test_select_matched_workpieces_rejects_invalid_index(self)
```

```python
def test_process_control_methods_delegate_to_glue_process(self)
```

```python
def test_prepare_and_load_delegates_to_execution_service(self)
```

```python
def test_prepare_load_and_start_delegates_to_execution_service(self)
```

```python
def test_getters_expose_latest_job_and_process_snapshot(self)
```

## `test_glue_process_driver_view.py`

Source: [tests/robot_systems/glue/test_glue_process_driver_view.py](../../../../tests/robot_systems/glue/test_glue_process_driver_view.py).

Imports (including optional/function-local imports; not a startup dependency list): `PyQt6.QtWidgets`, `os`, `src.robot_systems.glue.applications.glue_process_driver.view.glue_process_driver_view`, `sys`, `unittest`, `unittest.mock`.

### `TestGlueProcessDriverView`

```python
class TestGlueProcessDriverView(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
@classmethod
def setUpClass(cls)
```

```python
def test_get_selected_match_indexes_defaults_to_all_items(self)
```

```python
def test_set_process_snapshot_updates_machine_state_summary(self)
```

```python
def test_clean_up_stops_controller_if_present(self)
```

## `test_glue_processes.py`

Source: [tests/robot_systems/glue/test_glue_processes.py](../../../../tests/robot_systems/glue/test_glue_processes.py).

Comprehensive tests for src/robot_systems/glue/processes/. Critical business logic — robot lifecycle hooks and the GlueOperationCoordinator coordination layer. Covered: - CleanProcess: state transitions, requirements - PickAndPlaceProcess: identical pattern with process_id "pick_and_place" - GlueProcess: state transitions (mirrors CleanProcess) - GlueOperationCoordinator: mode switching, correct sequence selection and delegation for SPRAY_ONLY and PICK_AND_SPRAY modes, calibration path Note: Timers in CleanProcess and PickAndPlaceProcess are simulation-only and are not tested here. Only state flow and correct execution order are verified. Note: The auto-advance chain between processes (pick_and_place → glue in PICK_AND_SPRAY mode) is implemented inside ProcessSequence and is tested separately in tests/engine/process/test_process_sequence.y_pixels.

Imports (including optional/function-local imports; not a startup dependency list): `src.engine.process.process_requirements`, `src.engine.process.process_sequence`, `src.robot_systems.glue.component_ids`, `src.robot_systems.glue.domain.glue_job_execution_service`, `src.robot_systems.glue.processes.clean_process`, `src.robot_systems.glue.processes.glue_dispensing.dispensing_config`, `src.robot_systems.glue.processes.glue_dispensing.dispensing_context`, `src.robot_systems.glue.processes.glue_dispensing.dispensing_error`, `src.robot_systems.glue.processes.glue_dispensing.dispensing_state`, `src.robot_systems.glue.processes.glue_operation_coordinator`, `src.robot_systems.glue.processes.glue_operation_mode`, `src.robot_systems.glue.processes.glue_process`, `src.robot_systems.glue.processes.pick_and_place_process`, `src.robot_systems.glue.processes.robot_calibration_process`, `src.robot_systems.glue.settings.glue`, `src.shared_contracts.events.glue_process_events`, `src.shared_contracts.events.pick_and_place_events`, `src.shared_contracts.events.process_events`, `types`, `unittest`, `unittest.mock`.

### `_ms`

```python
def _ms()
```

### `_robot`

```python
def _robot()
```

### `_navigation_service`

```python
def _navigation_service()
```

### `_motor`

```python
def _motor()
```

### `_resolver`

```python
def _resolver()
```

### `_glue_process`

```python
def _glue_process()
```

### `TestCleanProcessIdentity`

```python
class TestCleanProcessIdentity(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_process_id_is_clean(self)
```

```python
def test_initial_state_is_idle(self)
```

### `TestCleanProcessStateTransitions`

```python
class TestCleanProcessStateTransitions(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_start_transitions_to_running(self)
```

```python
def test_stop_from_running_transitions_to_stopped(self)
```

```python
def test_pause_from_running_transitions_to_paused(self)
```

```python
def test_resume_from_paused_transitions_to_running(self)
```

```python
def test_stop_from_idle_is_blocked(self)
```

```python
def test_pause_from_idle_is_blocked(self)
```

```python
def test_set_error_forces_error_state(self)
```

```python
def test_reset_errors_returns_to_idle(self)
```

```python
def test_restart_from_stopped(self)
```

### `TestCleanProcessRequirements`

```python
class TestCleanProcessRequirements(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_requirements_block_start_when_service_unavailable(self)
```

```python
def test_requirements_allow_start_when_service_available(self)
```

### `TestPickAndPlaceProcessIdentity`

```python
class TestPickAndPlaceProcessIdentity(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_process_id_is_pick_and_place(self)
```

```python
def test_initial_state_is_idle(self)
```

### `TestPickAndPlaceProcessStateTransitions`

```python
class TestPickAndPlaceProcessStateTransitions(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_start_transitions_to_running(self)
```

```python
def test_stop_from_running_transitions_to_stopped(self)
```

```python
def test_pause_from_running_transitions_to_paused(self)
```

```python
def test_resume_from_paused_transitions_to_running(self)
```

```python
def test_stop_from_idle_is_blocked(self)
```

```python
def test_set_error_forces_error_state(self)
```

```python
def test_reset_errors_returns_to_idle(self)
```

```python
def test_start_publishes_pick_and_place_diagnostics(self)
```

```python
def test_step_mode_can_be_toggled(self)
```

```python
def test_step_once_requires_running_process(self)
```

```python
def test_run_workflow_uses_live_resolver_getter(self)
```

### `_make_runner_mocks`

```python
def _make_runner_mocks(execution_service=None, spray_on=True)
```

Build a GlueOperationCoordinator with real processes (needed for construction), then replace the internal ProcessSequence objects with mocks so tests can verify delegation without executing real sequence logic. Returns (runner, spray_seq, pick_seq, clean_seq).

### `TestGlueOperationCoordinatorMode`

```python
class TestGlueOperationCoordinatorMode(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_default_mode_is_spray_only(self)
```

```python
def test_set_mode_changes_to_pick_and_spray(self)
```

```python
def test_set_mode_can_revert_to_spray_only(self)
```

```python
def test_glue_process_property_returns_spray_only_process(self)
```

### `TestGlueOperationCoordinatorSprayOnly`

```python
class TestGlueOperationCoordinatorSprayOnly(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_start_calls_spray_sequence_start(self)
```

```python
def test_start_sets_active_to_spray_sequence(self)
```

```python
def test_start_in_spray_only_prepares_glue_before_sequence_start(self)
```

```python
def test_start_in_spray_only_blocks_sequence_when_preparation_fails(self)
```

```python
def test_stop_cancels_pending_spray_only_preparation(self)
```

```python
def test_resume_in_spray_only_does_not_reprepare_glue(self)
```

```python
def test_start_again_after_stopped_spray_run_reprepares_glue(self)
```

### `TestGlueOperationCoordinatorPickAndSpray`

```python
class TestGlueOperationCoordinatorPickAndSpray(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_start_calls_pick_sequence_start(self)
```

```python
def test_start_sets_active_to_pick_sequence(self)
```

```python
def test_pick_and_spray_sequence_prepares_glue_before_starting_it(self)
```

```python
def test_pick_and_spray_sequence_sets_glue_error_when_preparation_fails(self)
```

### `TestGlueOperationCoordinatorStop`

```python
class TestGlueOperationCoordinatorStop(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_stop_calls_active_sequence_stop(self)
```

```python
def test_stop_when_no_active_preserves_idle_coordinator(self)
```

### `TestGlueOperationCoordinatorPauseResume`

```python
class TestGlueOperationCoordinatorPauseResume(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_pause_calls_active_sequence_pause(self)
```

```python
def test_pause_when_no_active_preserves_idle_coordinator(self)
```

```python
def test_pause_cancels_pending_spray_only_preparation(self)
```

```python
def test_resume_calls_start_on_active_sequence(self)
```

```python
def test_resume_when_no_active_preserves_idle_coordinator(self)
```

### `TestGlueOperationCoordinatorClean`

```python
class TestGlueOperationCoordinatorClean(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_clean_starts_clean_sequence(self)
```

```python
def test_clean_sets_active_to_clean_sequence(self)
```

```python
def test_clean_stops_previously_active_sequence(self)
```

```python
def test_clean_does_not_stop_itself_when_already_active(self)
```

### `TestGlueOperationCoordinatorResetErrors`

```python
class TestGlueOperationCoordinatorResetErrors(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_reset_errors_calls_active_sequence_reset_errors(self)
```

```python
def test_reset_errors_when_no_active_preserves_idle_coordinator(self)
```

### `TestGlueOperationMode`

```python
class TestGlueOperationMode(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_from_label_spray_only(self)
```

```python
def test_from_label_pick_and_spray(self)
```

```python
def test_from_label_unknown_returns_none(self)
```

```python
def test_enum_values(self)
```

### `TestGlueProcessIdentity`

```python
class TestGlueProcessIdentity(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_process_id_is_glue(self)
```

```python
def test_initial_state_is_idle(self)
```

### `TestGlueProcessStateTransitions`

```python
class TestGlueProcessStateTransitions(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_start_transitions_to_running(self)
```

```python
def test_stop_from_running_transitions_to_stopped(self)
```

```python
def test_pause_from_running_transitions_to_paused(self)
```

```python
def test_resume_from_paused_transitions_to_running(self)
```

```python
def test_set_error_forces_error_state(self)
```

```python
def test_reset_errors_returns_to_idle(self)
```

```python
def test_reset_errors_clears_dispensing_last_error(self)
```

```python
def test_get_dispensing_snapshot_returns_idle_summary_without_context(self)
```

```python
def test_get_dispensing_snapshot_includes_context_debug_snapshot(self)
```

```python
def test_start_in_manual_mode_builds_machine_without_worker_thread(self)
```

```python
def test_start_publishes_diagnostics_snapshot(self)
```

```python
def test_completed_worker_run_transitions_outer_process_to_stopped(self)
```

```python
def test_step_once_delegates_to_machine_in_manual_mode(self)
```

### `TestGlueOperationCoordinatorCalibration`

```python
class TestGlueOperationCoordinatorCalibration(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_calibrate_calls_process_start(self)
```

```python
def test_stop_calibration_calls_process_stop_when_active(self)
```

```python
def test_stop_calibration_clears_active_process(self)
```

```python
def test_stop_calibration_when_not_active_preserves_no_active_process(self)
```

## `test_glue_robot_system.py`

Source: [tests/robot_systems/glue/test_glue_robot_system.py](../../../../tests/robot_systems/glue/test_glue_robot_system.py).

Imports (including optional/function-local imports; not a startup dependency list): `json`, `os`, `src.engine.common_settings_ids`, `src.engine.repositories.settings_service_factory`, `src.engine.robot.configuration`, `src.robot_systems.glue.glue_robot_system`, `src.shared_contracts.declarations`, `tempfile`, `unittest`.

Module declarations (expressions are shown without evaluating them):

```python
APP_NAME = GlueRobotSystem.__name__.lower()
```

### `_make_service`

```python
def _make_service(tmp: str, robot_ip: str='10.0.0.1', robot_tool: int=1)
```

Helper: write config to tmp dir and build a SettingsService.

### `TestGlueRobotAppSettings`

```python
class TestGlueRobotAppSettings(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_loads_existing_file(self)
```

```python
def test_default_robot_tool(self)
```

```python
def test_reload_returns_fresh_instance(self)
```

```python
def test_get_returns_same_instance_without_reload(self)
```

## `test_glue_settings_controller.py`

Source: [tests/robot_systems/glue/test_glue_settings_controller.py](../../../../tests/robot_systems/glue/test_glue_settings_controller.py).

Imports (including optional/function-local imports; not a startup dependency list): `src.applications.base.widget_application`, `src.robot_systems.glue.applications.glue_settings.controller.glue_settings_controller`, `src.robot_systems.glue.applications.glue_settings.model.glue_settings_model`, `src.robot_systems.glue.applications.glue_settings.model.mapper`, `src.robot_systems.glue.glue_robot_system`, `src.robot_systems.glue.settings.glue`, `src.robot_systems.glue.settings.glue_types`, `unittest`, `unittest.mock`.

### `_make_view`

```python
def _make_view()
```

### `_make_model`

```python
def _make_model(settings=None, types=None)
```

### `_make_controller`

```python
def _make_controller(settings=None, types=None)
```

### `TestGlueSettingsControllerInit`

```python
class TestGlueSettingsControllerInit(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_wires_save_requested(self)
```

```python
def test_wires_spray_on_changed(self)
```

```python
def test_wires_add_type_requested(self)
```

```python
def test_wires_update_type_requested(self)
```

```python
def test_wires_remove_type_requested(self)
```

```python
def test_wires_destroyed(self)
```

### `TestGlueSettingsControllerLoad`

```python
class TestGlueSettingsControllerLoad(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_load_calls_model_load(self)
```

```python
def test_load_pushes_settings_to_view(self)
```

```python
def test_load_pushes_glue_types_to_view(self)
```

### `TestGlueSettingsControllerSave`

```python
class TestGlueSettingsControllerSave(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_on_save_calls_model_save(self)
```

```python
def test_on_save_passes_view_values(self)
```

```python
def test_on_save_exception_does_not_propagate(self)
```

### `TestGlueSettingsControllerSprayOn`

```python
class TestGlueSettingsControllerSprayOn(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_spray_on_true_saves(self)
```

```python
def test_spray_on_value_overridden_in_flat(self)
```

```python
def test_spray_on_false_saves_false(self)
```

```python
def test_spray_on_exception_does_not_propagate(self)
```

### `TestGlueSettingsControllerGlueTypes`

```python
class TestGlueSettingsControllerGlueTypes(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_add_type_calls_model(self)
```

```python
def test_add_type_reloads_view(self)
```

```python
def test_add_type_exception_does_not_propagate(self)
```

```python
def test_update_type_calls_model(self)
```

```python
def test_update_type_reloads_view(self)
```

```python
def test_update_type_exception_does_not_propagate(self)
```

```python
def test_remove_type_calls_model(self)
```

```python
def test_remove_type_reloads_view(self)
```

```python
def test_remove_type_exception_does_not_propagate(self)
```

```python
def test_stop_returns_none(self)
```

### `TestGlueSettingsApplicationSpec`

```python
class TestGlueSettingsApplicationSpec(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_spec_declared(self)
```

```python
def test_spec_folder_id(self)
```

```python
def test_spec_has_factory(self)
```

```python
def test_spec_icon_set(self)
```

```python
def test_factory_returns_widget_application(self)
```

```python
def test_factory_registers_messaging_service(self)
```

## `test_glue_settings_mapper.py`

Source: [tests/robot_systems/glue/test_glue_settings_mapper.py](../../../../tests/robot_systems/glue/test_glue_settings_mapper.py).

Imports (including optional/function-local imports; not a startup dependency list): `copy`, `src.robot_systems.glue.applications.glue_settings.model.mapper`, `src.robot_systems.glue.settings.glue`, `unittest`.

### `TestGlueSettingsMapperToFlatDict`

```python
class TestGlueSettingsMapperToFlatDict(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def setUp(self)
```

```python
def test_all_expected_keys_present(self)
```

```python
def test_spray_width_value(self)
```

```python
def test_spray_on_value(self)
```

```python
def test_glue_type_value(self)
```

```python
def test_motor_speed_value(self)
```

```python
def test_forward_ramp_steps_value(self)
```

### `TestGlueSettingsMapperFromFlatDict`

```python
class TestGlueSettingsMapperFromFlatDict(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def setUp(self)
```

```python
def test_spray_width_updated(self)
```

```python
def test_spray_on_updated_true(self)
```

```python
def test_spray_on_updated_false(self)
```

```python
def test_glue_type_updated(self)
```

```python
def test_motor_speed_updated(self)
```

```python
def test_forward_ramp_steps_cast_to_int(self)
```

```python
def test_missing_keys_fall_back_to_base(self)
```

```python
def test_does_not_mutate_base(self)
```

```python
def test_full_roundtrip(self)
```

## `test_glue_settings_model.py`

Source: [tests/robot_systems/glue/test_glue_settings_model.py](../../../../tests/robot_systems/glue/test_glue_settings_model.py).

Imports (including optional/function-local imports; not a startup dependency list): `src.robot_systems.glue.applications.glue_settings`, `src.robot_systems.glue.applications.glue_settings.model.glue_settings_model`, `src.robot_systems.glue.applications.glue_settings.model.mapper`, `src.robot_systems.glue.settings.glue`, `src.robot_systems.glue.settings.glue_types`, `unittest`, `unittest.mock`.

### `_make_service`

```python
def _make_service(settings=None, glue_types=None)
```

### `TestGlueSettingsModelLoad`

```python
class TestGlueSettingsModelLoad(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_load_calls_service(self)
```

```python
def test_load_returns_settings(self)
```

```python
def test_settings_cached_after_load(self)
```

### `TestGlueSettingsModelSave`

```python
class TestGlueSettingsModelSave(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_save_calls_save_settings(self)
```

```python
def test_save_updates_spray_width(self)
```

```python
def test_save_updates_spray_on(self)
```

```python
def test_save_updates_internal_cache(self)
```

```python
def test_save_without_load_uses_default_base(self)
```

```python
def test_save_does_not_mutate_previous_settings(self)
```

### `TestGlueSettingsModelGlueTypes`

```python
class TestGlueSettingsModelGlueTypes(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_load_glue_types_delegates(self)
```

```python
def test_load_glue_types_returns_list(self)
```

```python
def test_add_glue_type_delegates(self)
```

```python
def test_update_glue_type_delegates(self)
```

```python
def test_remove_glue_type_delegates(self)
```

### `TestGlueSettingsApplicationService`

```python
class TestGlueSettingsApplicationService(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_load_settings_reads_correct_key(self)
```

```python
def test_save_settings_writes_correct_key(self)
```

```python
def test_load_glue_types_returns_list(self)
```

```python
def test_add_glue_type_saves_catalog(self)
```

```python
def test_update_glue_type_saves_catalog(self)
```

```python
def test_update_glue_type_missing_id_raises(self)
```

```python
def test_remove_glue_type_saves_catalog(self)
```

```python
def test_remove_glue_type_missing_id_raises(self)
```

## `test_glue_workpiece.py`

Source: [tests/robot_systems/glue/test_glue_workpiece.py](../../../../tests/robot_systems/glue/test_glue_workpiece.py).

No top-level functions, classes or public value declarations; inspect the source for imports or entry-point statements.

## `test_modbus_settings_plugin_integration.py`

Source: [tests/robot_systems/glue/test_modbus_settings_plugin_integration.py](../../../../tests/robot_systems/glue/test_modbus_settings_plugin_integration.py).

Imports (including optional/function-local imports; not a startup dependency list): `src.applications.base.widget_application`, `src.applications.modbus_settings.service.i_modbus_settings_service`, `src.applications.modbus_settings.service.modbus_settings_application_service`, `src.engine.common_settings_ids`, `src.engine.hardware.communication.modbus.i_modbus_action_service`, `src.engine.hardware.communication.modbus.modbus`, `src.engine.hardware.communication.modbus.modbus_action_service`, `src.robot_systems.glue.glue_robot_system`, `unittest`, `unittest.mock`.

### `_make_robot_system`

```python
def _make_robot_system(config=None)
```

### `_spec`

```python
def _spec()
```

### `TestModbusSettingsApplicationSpec`

```python
class TestModbusSettingsApplicationSpec(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_spec_declared(self)
```

```python
def test_spec_folder_id(self)
```

```python
def test_spec_has_factory(self)
```

```python
def test_spec_icon_set(self)
```

```python
def test_spec_name(self)
```

### `TestModbusSettingsApplicationFactory`

```python
class TestModbusSettingsApplicationFactory(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_factory_returns_widget_application(self)
```

```python
def test_factory_does_not_require_messaging_service(self)
```

```python
def test_register_stores_messaging_service(self)
```

```python
def test_widget_factory_callable_ignores_messaging_service(self)
```

```python
def test_factory_called_twice_returns_independent_applications(self)
```

### `TestModbusSettingsApplicationServiceIntegration`

```python
class TestModbusSettingsApplicationServiceIntegration(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_load_config_returns_correct_instance(self)
```

```python
def test_load_config_reads_modbus_config_key(self)
```

```python
def test_save_config_delegates_to_settings_service(self)
```

```python
def test_load_config_port(self)
```

```python
def test_load_config_baudrate(self)
```

```python
def test_load_config_slave_address(self)
```

```python
def test_load_config_parity(self)
```

```python
def test_load_config_timeout(self)
```

```python
def test_save_config_correct_object_passed(self)
```

```python
def test_service_has_no_detect_ports(self)
```

```python
def test_service_has_no_test_connection(self)
```

### `TestModbusActionServiceIntegration`

```python
class TestModbusActionServiceIntegration(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_implements_i_modbus_action_service(self)
```

```python
def test_detect_ports_returns_list(self)
```

```python
def test_test_connection_returns_bool(self)
```

```python
def test_factory_uses_modbus_action_service(self)
```

_build_modbus_settings_application must wire ModbusActionService — not a mock.

```python
def test_factory_keeps_settings_and_action_services_separate(self)
```

### `TestModbusSettingsSpecInGlueApp`

```python
class TestModbusSettingsSpecInGlueApp(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_modbus_settings_spec_declared(self)
```

```python
def test_modbus_settings_spec_path(self)
```

```python
def test_modbus_settings_spec_has_serializer(self)
```

```python
def test_serializer_get_default_returns_modbus_config(self)
```

```python
def test_serializer_roundtrip(self)
```

```python
def test_serializer_settings_type(self)
```

### `TestModbusSettingsApplicationOrdering`

```python
class TestModbusSettingsApplicationOrdering(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_modbus_settings_in_service_folder(self)
```

```python
def test_service_folder_declared(self)
```

```python
def test_all_service_applications_have_icons(self)
```

```python
def test_all_service_applications_have_factories(self)
```

## `test_navigation.py`

Source: [tests/robot_systems/glue/test_navigation.py](../../../../tests/robot_systems/glue/test_navigation.py).

Imports (including optional/function-local imports; not a startup dependency list): `src.robot_systems.glue.navigation`, `unittest`, `unittest.mock`.

### `TestGlueNavigationService`

```python
class TestGlueNavigationService(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_move_home_goes_directly_to_home(self)
```

```python
def test_move_home_uses_capture_z_offset_when_vision_is_present(self)
```

```python
def test_move_home_updates_active_area_via_work_area_service(self)
```

```python
def test_get_group_position_returns_parsed_position(self)
```

```python
def test_move_to_group_updates_observed_area(self)
```

## `test_permissions_migrator.py`

Source: [tests/robot_systems/glue/test_permissions_migrator.py](../../../../tests/robot_systems/glue/test_permissions_migrator.py).

Tests for src/robot_systems/glue/domain/permissions/permissions_migrator.y_pixels Verifies that ensure_permissions_current adds missing app_ids, removes stale keys, saves back only when changes were made, and preserves existing values untouched.

Imports (including optional/function-local imports; not a startup dependency list): `src.engine.auth.i_permissions_repository`, `src.engine.auth.permissions_migrator`, `unittest`, `unittest.mock`.

### `_repo`

```python
def _repo(data: dict) -> IPermissionsRepository
```

### `TestEnsurePermissionsCurrent`

```python
class TestEnsurePermissionsCurrent(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_adds_missing_app_id_with_admin_default(self)
```

```python
def test_does_not_overwrite_existing_entry(self)
```

```python
def test_removes_stale_key_no_longer_in_known_ids(self)
```

```python
def test_no_writes_when_already_in_sync(self)
```

```python
def test_adds_multiple_missing_apps(self)
```

```python
def test_mixed_add_and_remove(self)
```

```python
def test_empty_known_ids_removes_all_stale_keys(self)
```

## `test_permissions_repository.py`

Source: [tests/robot_systems/glue/test_permissions_repository.py](../../../../tests/robot_systems/glue/test_permissions_repository.py).

Tests for src/robot_systems/glue/domain/permissions/permissions_repository.y_pixels Covers JSON persistence, default fallback, copy semantics, and round-trip fidelity. Uses a temp file so tests are fully isolated and leave no side effects.

Imports (including optional/function-local imports; not a startup dependency list): `json`, `os`, `src.engine.auth.json_permissions_repository`, `tempfile`, `unittest`.

### `TestJsonPermissionsRepository`

```python
class TestJsonPermissionsRepository(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def setUp(self)
```

```python
def tearDown(self)
```

```python
def test_loads_existing_file(self)
```

```python
def test_creates_empty_file_when_missing(self)
```

```python
def test_handles_empty_json_file(self)
```

```python
def test_returns_stored_roles(self)
```

```python
def test_defaults_to_empty_for_unknown_app(self)
```

```python
def test_returns_copy_not_internal_reference(self)
```

```python
def test_set_persists_to_disk(self)
```

```python
def test_set_overwrites_existing_entry(self)
```

```python
def test_set_does_not_store_input_reference(self)
```

```python
def test_get_all_returns_full_map(self)
```

```python
def test_get_all_returns_copy(self)
```

```python
def test_round_trip_multiple_apps(self)
```

## `test_pick_and_place_workflow.py`

Source: [tests/robot_systems/glue/test_pick_and_place_workflow.py](../../../../tests/robot_systems/glue/test_pick_and_place_workflow.py).

Imports (including optional/function-local imports; not a startup dependency list): `logging`, `src.engine.robot.targeting.vision_target_resolver`, `src.engine.vision.implementation.VisionSystem.core.models.contour`, `src.robot_systems.glue.domain.workpieces.model.glue_workpiece`, `src.robot_systems.glue.processes.pick_and_place.config`, `src.robot_systems.glue.processes.pick_and_place.errors`, `src.robot_systems.glue.processes.pick_and_place.execution`, `src.robot_systems.glue.processes.pick_and_place.plane`, `src.robot_systems.glue.processes.pick_and_place.planning`, `src.robot_systems.glue.processes.pick_and_place.workflow`, `src.shared_contracts.events.process_events`, `threading`, `unittest`, `unittest.mock`.

### `_make_resolver`

```python
def _make_resolver(x=10.0, y=20.0)
```

### `TestPickupCalculator`

```python
class TestPickupCalculator(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_calculate_preserves_current_rotation_and_offset_behavior(self)
```

### `TestPlacementCalculator`

```python
class TestPlacementCalculator(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_calculate_does_not_mutate_input_contour(self)
```

```python
def test_plane_management_uses_configured_row_gap(self)
```

### `TestPickAndPlaceWorkflow`

```python
class TestPickAndPlaceWorkflow(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_workflow_reports_place_motion_failure(self)
```

```python
def test_workflow_zero_height_mode_preserves_current_effective_pick_height(self)
```

```python
def test_workflow_reports_step_checkpoints_in_order(self)
```

```python
def test_workflow_can_stop_from_step_gate(self)
```

### `TestPickAndPlacePolicies`

```python
class TestPickAndPlacePolicies(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_height_resolution_zero_mode_preserves_current_behavior(self)
```

```python
def test_selection_policy_preserves_match_order(self)
```

## `test_pickup_plane_mapper.py`

Source: [tests/robot_systems/glue/test_pickup_plane_mapper.py](../../../../tests/robot_systems/glue/test_pickup_plane_mapper.py).

Imports (including optional/function-local imports; not a startup dependency list): `src.engine.robot.plane_pose_mapper`, `unittest`.

### `TestCalibrationToPickupPlaneMapper`

```python
class TestCalibrationToPickupPlaneMapper(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_maps_calibration_origin_to_pickup_origin(self)
```

```python
def test_rotates_and_translates_calibration_plane_point_into_pickup_plane(self)
```

## `test_robot_settings_plugin_integration.py`

Source: [tests/robot_systems/glue/test_robot_settings_plugin_integration.py](../../../../tests/robot_systems/glue/test_robot_settings_plugin_integration.py).

Imports (including optional/function-local imports; not a startup dependency list): `src.applications.base.widget_application`, `src.applications.robot_settings.service.robot_settings_application_service`, `src.engine.common_settings_ids`, `src.engine.robot.configuration`, `src.robot_systems.glue.glue_robot_system`, `unittest`, `unittest.mock`.

### `_make_robot_system`

```python
def _make_robot_system(config=None, calibration=None)
```

### `TestRobotSettingsApplicationSpec`

```python
class TestRobotSettingsApplicationSpec(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_spec_declared(self)
```

```python
def test_spec_folder_id(self)
```

```python
def test_spec_has_factory(self)
```

```python
def test_spec_icon_set(self)
```

### `TestRobotSettingsApplicationFactory`

```python
class TestRobotSettingsApplicationFactory(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_factory_returns_widget_application(self)
```

```python
def test_factory_does_not_require_messaging_service(self)
```

```python
def test_register_stores_messaging_service(self)
```

```python
def test_widget_factory_callable_ignores_messaging_service(self)
```

RobotSettings does not use the broker — lambda must accept and ignore it.

### `TestRobotSettingsApplicationServiceIntegration`

```python
class TestRobotSettingsApplicationServiceIntegration(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_load_config_returns_correct_instance(self)
```

```python
def test_load_config_reads_robot_config_key(self)
```

```python
def test_load_calibration_returns_correct_instance(self)
```

```python
def test_load_calibration_reads_robot_calibration_key(self)
```

```python
def test_save_config_delegates_to_settings_service(self)
```

```python
def test_save_calibration_delegates_to_settings_service(self)
```

```python
def test_load_config_robot_ip(self)
```

```python
def test_load_config_robot_tool(self)
```

```python
def test_load_calibration_z_target(self)
```

## `test_targeting_refresh_wiring.py`

Source: [tests/robot_systems/glue/test_targeting_refresh_wiring.py](../../../../tests/robot_systems/glue/test_targeting_refresh_wiring.py).

Imports (including optional/function-local imports; not a startup dependency list): `src.robot_systems.glue`, `types`, `unittest`, `unittest.mock`.

### `TestGlueTargetingRefreshWiring`

```python
class TestGlueTargetingRefreshWiring(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_glue_process_driver_uses_live_resolver_getter_for_job_builder(self)
```

```python
def test_workpiece_editor_uses_live_resolver_getter_for_path_preparation(self)
```

## `test_tool_settings_plugin_integration.py`

Source: [tests/robot_systems/glue/test_tool_settings_plugin_integration.py](../../../../tests/robot_systems/glue/test_tool_settings_plugin_integration.py).

Plugin integration tests for ToolSettings application. Verifies: - ApplicationSpec is declared in GlueRobotSystem.shell.applications - factory produces a WidgetApplication - settings_service is accessed

Imports (including optional/function-local imports; not a startup dependency list): `src.applications.base.widget_application`, `src.robot_systems.glue.glue_robot_system`, `unittest`, `unittest.mock`.

### `_make_robot_system`

```python
def _make_robot_system()
```

### `_spec`

```python
def _spec()
```

### `TestToolSettingsApplicationSpec`

```python
class TestToolSettingsApplicationSpec(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_spec_declared(self)
```

```python
def test_spec_folder_id(self)
```

```python
def test_spec_has_factory(self)
```

```python
def test_spec_icon_set(self)
```

### `TestToolSettingsApplicationFactory`

```python
class TestToolSettingsApplicationFactory(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_factory_returns_widget_application(self)
```

```python
def test_factory_uses_settings_service(self)
```

```python
def test_register_stores_messaging_service(self)
```

## `test_user_management_plugin_integration.py`

Source: [tests/robot_systems/glue/test_user_management_plugin_integration.py](../../../../tests/robot_systems/glue/test_user_management_plugin_integration.py).

Plugin integration tests for UserManagement application. Verifies: - ApplicationSpec is declared in GlueRobotSystem.shell.applications - factory produces a WidgetApplication - factory creates the service with a CSV repository

Imports (including optional/function-local imports; not a startup dependency list): `os`, `src.applications.base.widget_application`, `src.robot_systems.glue.glue_robot_system`, `tempfile`, `unittest`, `unittest.mock`.

### `_make_robot_system`

```python
def _make_robot_system()
```

### `_spec`

```python
def _spec()
```

### `TestUserManagementApplicationSpec`

```python
class TestUserManagementApplicationSpec(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_spec_declared(self)
```

```python
def test_spec_folder_id(self)
```

```python
def test_spec_has_factory(self)
```

```python
def test_spec_icon_set(self)
```

### `TestUserManagementApplicationFactory`

```python
class TestUserManagementApplicationFactory(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_factory_returns_widget_application(self)
```

```python
def test_register_stores_messaging_service(self)
```

```python
def test_factory_creates_service_without_robot_service(self)
```

UserManagement does not depend on robot or vision service.

## `test_workpiece_editor_plugin_integration.py`

Source: [tests/robot_systems/glue/test_workpiece_editor_plugin_integration.py](../../../../tests/robot_systems/glue/test_workpiece_editor_plugin_integration.py).

Plugin integration tests for WorkpieceEditor application. Verifies: - ApplicationSpec is declared in GlueRobotSystem.shell.applications - factory produces a WidgetApplication

Imports (including optional/function-local imports; not a startup dependency list): `src.applications.base.widget_application`, `src.engine.common_service_ids`, `src.engine.common_settings_ids`, `src.robot_systems.glue.component_ids`, `src.robot_systems.glue.glue_robot_system`, `unittest`, `unittest.mock`.

### `_make_robot_system`

```python
def _make_robot_system()
```

### `_spec`

```python
def _spec()
```

### `TestWorkpieceEditorApplicationSpec`

```python
class TestWorkpieceEditorApplicationSpec(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_spec_declared(self)
```

```python
def test_spec_folder_id(self)
```

```python
def test_spec_has_factory(self)
```

```python
def test_spec_icon_set(self)
```

### `TestWorkpieceEditorApplicationFactory`

```python
class TestWorkpieceEditorApplicationFactory(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_factory_returns_widget_application(self)
```

```python
def test_factory_fetches_vision_service_as_optional(self)
```

```python
def test_register_stores_messaging_service(self)
```

## `test_workpiece_library_plugin_integration.py`

Source: [tests/robot_systems/glue/test_workpiece_library_plugin_integration.py](../../../../tests/robot_systems/glue/test_workpiece_library_plugin_integration.py).

Plugin integration tests for WorkpieceLibrary application. Verifies: - ApplicationSpec is declared in GlueRobotSystem.shell.applications - factory produces a WidgetApplication - settings_service is used to fetch catalog settings

Imports (including optional/function-local imports; not a startup dependency list): `src.applications.base.widget_application`, `src.engine.common_settings_ids`, `src.robot_systems.glue.component_ids`, `src.robot_systems.glue.glue_robot_system`, `unittest`, `unittest.mock`.

### `_make_robot_system`

```python
def _make_robot_system()
```

### `_spec`

```python
def _spec()
```

### `TestWorkpieceLibraryApplicationSpec`

```python
class TestWorkpieceLibraryApplicationSpec(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_spec_declared(self)
```

```python
def test_spec_folder_id(self)
```

```python
def test_spec_has_factory(self)
```

```python
def test_spec_icon_set(self)
```

### `TestWorkpieceLibraryApplicationFactory`

```python
class TestWorkpieceLibraryApplicationFactory(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_factory_returns_widget_application(self)
```

```python
def test_factory_fetches_catalog_settings(self)
```

```python
def test_register_stores_messaging_service(self)
```
