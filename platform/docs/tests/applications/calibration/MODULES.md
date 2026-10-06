# Module reference: `tests/applications/calibration`

[Package guide](README.md) · [Complete source index](../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [test_calibration_controller.py](#test_calibration_controllerpy)
- [test_calibration_controls_panel.py](#test_calibration_controls_panelpy)
- [test_calibration_model.py](#test_calibration_modelpy)
- [test_calibration_service.py](#test_calibration_servicepy)

## `__init__.py`

Source: [tests/applications/calibration/__init__.py](../../../../tests/applications/calibration/__init__.py).

No top-level functions, classes or public value declarations; inspect the source for imports or entry-point statements.

## `test_calibration_controller.py`

Source: [tests/applications/calibration/test_calibration_controller.py](../../../../tests/applications/calibration/test_calibration_controller.py).

Imports (including optional/function-local imports; not a startup dependency list): `PyQt6.QtWidgets`, `src.applications.calibration.controller.calibration_controller`, `src.applications.calibration.model.calibration_model`, `src.applications.calibration.service.i_calibration_service`, `src.applications.calibration_settings.calibration_settings_data`, `src.applications.intrinsic_calibration_capture.service.i_intrinsic_capture_service`, `src.engine.robot.configuration`, `src.engine.robot.height_measuring.settings`, `src.engine.vision.calibration_vision_settings`, `src.shared_contracts.events.vision_events`, `sys`, `unittest`, `unittest.mock`.

### `_make_calibration_settings`

```python
def _make_calibration_settings()
```

### `_make_model`

```python
def _make_model(**overrides)
```

### `_make_view`

```python
def _make_view()
```

### `_make_broker`

```python
def _make_broker()
```

### `_make_ctrl`

```python
def _make_ctrl(**model_overrides)
```

### `TestCalibrationControllerInit`

```python
class TestCalibrationControllerInit(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
@classmethod
def setUpClass(cls)
```

```python
def test_not_active_before_load(self)
```

### `TestCalibrationControllerLoad`

```python
class TestCalibrationControllerLoad(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
@classmethod
def setUpClass(cls)
```

```python
def test_load_sets_active(self)
```

```python
def test_load_subscribes_to_latest_image(self)
```

```python
def test_wires_destroyed_signal(self)
```

```python
def test_wires_capture_signal(self)
```

```python
def test_wires_calibrate_camera_signal(self)
```

```python
def test_wires_calibrate_robot_signal(self)
```

```python
def test_wires_calibrate_sequence_signal(self)
```

```python
def test_wires_save_calibration_settings_signal(self)
```

```python
def test_load_pushes_calibration_settings_into_view(self)
```

```python
def test_repeated_load_does_not_connect_calibrate_robot_twice(self)
```

### `TestCalibrationControllerStop`

```python
class TestCalibrationControllerStop(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
@classmethod
def setUpClass(cls)
```

```python
def test_stop_sets_inactive(self)
```

```python
def test_stop_unsubscribes_vision_topic(self)
```

```python
def test_stop_clears_subs_list(self)
```

```python
def test_stop_without_load_clears_runtime_state(self)
```

### `TestCalibrationControllerHandlers`

```python
class TestCalibrationControllerHandlers(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
@classmethod
def setUpClass(cls)
```

```python
def test_on_capture_calls_model(self)
```

```python
def test_on_calibrate_camera_calls_model(self)
```

```python
def test_on_calibrate_robot_calls_model(self)
```

```python
def test_on_calibrate_robot_stops_when_area_selection_is_cancelled(self)
```

```python
def test_on_calibrate_sequence_calls_model(self)
```

```python
def test_success_appends_tick_prefix(self)
```

```python
def test_failure_appends_cross_prefix(self)
```

```python
def test_log_helper_success(self)
```

```python
def test_log_helper_failure(self)
```

```python
def test_on_save_calibration_settings_updates_model_and_logs(self)
```

```python
def test_on_save_intrinsic_capture_config_updates_model(self)
```

### `TestCalibrationControllerCameraFrame`

```python
class TestCalibrationControllerCameraFrame(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
@classmethod
def setUpClass(cls)
```

```python
def test_camera_frame_updates_view_when_active(self)
```

```python
def test_camera_tcp_area_is_selected_and_saved_before_start(self)
```

```python
def test_camera_tcp_area_cancelled_before_motion(self)
```

```python
def test_unconfigured_camera_tcp_area_is_rejected_before_motion(self)
```

```python
def test_camera_frame_ignored_when_inactive(self)
```

```python
def test_camera_frame_ignored_when_none(self)
```

```python
def test_latest_image_raw_forwards_image_from_dict(self)
```

```python
def test_latest_image_raw_ignores_non_dict(self)
```

```python
def test_latest_image_raw_ignores_dict_without_image_key(self)
```

## `test_calibration_controls_panel.py`

Source: [tests/applications/calibration/test_calibration_controls_panel.py](../../../../tests/applications/calibration/test_calibration_controls_panel.py).

Imports (including optional/function-local imports; not a startup dependency list): `PyQt6.QtCore`, `PyQt6.QtWidgets`, `src.applications.base.widgets.keyboard_number_field`, `src.applications.calibration.calibration_factory`, `src.applications.calibration.view.calibration_controls_panel`, `src.applications.calibration.view.calibration_view`, `src.applications.calibration.view.compact_settings_group`, `src.applications.calibration_settings.view.calibration_settings_schema`, `src.applications.intrinsic_calibration_capture.service.i_intrinsic_capture_service`, `src.shared_contracts.declarations`, `sys`, `unittest`.

### `TestCalibrationControlsPanel`

```python
class TestCalibrationControlsPanel(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
@classmethod
def setUpClass(cls)
```

```python
def test_uses_phase_tabs_for_workflow_sections(self)
```

```python
def test_factory_can_hide_optional_phases(self)
```

```python
def test_stop_button_starts_disabled(self)
```

```python
def test_each_phase_tab_exposes_save_settings_button(self)
```

```python
def test_height_mapping_content_can_be_injected_after_init(self)
```

```python
def test_cancel_settings_dialog_restores_values(self)
```

```python
def test_camera_auto_capture_fields_share_settings_dialog(self)
```

```python
def test_camera_settings_save_emits_auto_capture_config(self)
```

```python
def test_compact_settings_keep_schema_value_types(self)
```

```python
def test_workobject_steps_preserve_capture_and_solve_flow(self)
```

```python
def test_area_picker_returns_selected_area_id(self)
```

## `test_calibration_model.py`

Source: [tests/applications/calibration/test_calibration_model.py](../../../../tests/applications/calibration/test_calibration_model.py).

Imports (including optional/function-local imports; not a startup dependency list): `src.applications.base.i_application_model`, `src.applications.calibration.model.calibration_model`, `src.applications.calibration.service.i_calibration_service`, `src.applications.calibration_settings.calibration_settings_data`, `src.engine.robot.configuration`, `src.engine.robot.height_measuring.settings`, `src.engine.vision.calibration_vision_settings`, `unittest`, `unittest.mock`.

### `_make_calibration_settings`

```python
def _make_calibration_settings()
```

### `_make_service`

```python
def _make_service(**overrides)
```

### `TestCalibrationModelInterface`

```python
class TestCalibrationModelInterface(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_implements_i_application_model(self)
```

### `TestCalibrationModelLoad`

```python
class TestCalibrationModelLoad(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_load_is_no_op(self)
```

### `TestCalibrationModelDelegation`

```python
class TestCalibrationModelDelegation(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_capture_delegates_to_service(self)
```

```python
def test_calibrate_camera_delegates_to_service(self)
```

```python
def test_calibrate_robot_delegates_to_service(self)
```

```python
def test_calibrate_camera_and_robot_delegates_to_service(self)
```

```python
def test_capture_passes_through_failure(self)
```

```python
def test_save_is_no_op(self)
```

```python
def test_load_calibration_settings_delegates_to_service(self)
```

```python
def test_save_calibration_settings_delegates_to_service(self)
```

```python
def test_tool_tcp_methods_delegate_to_service(self)
```

## `test_calibration_service.py`

Source: [tests/applications/calibration/test_calibration_service.py](../../../../tests/applications/calibration/test_calibration_service.py).

Imports (including optional/function-local imports; not a startup dependency list): `src.applications.calibration.service.calibration_application_service`, `src.applications.calibration.service.stub_calibration_service`, `src.applications.calibration_settings.calibration_settings_data`, `src.engine.common_settings_ids`, `src.engine.robot.configuration`, `src.engine.robot.height_measuring.settings`, `src.engine.vision.calibration_vision_settings`, `src.shared_contracts.declarations`, `types`, `unittest`, `unittest.mock`.

### `_make_calibration_settings`

```python
def _make_calibration_settings()
```

### `_make_vision`

```python
def _make_vision(capture=None, calibrate=None)
```

### `_make_svc`

```python
def _make_svc(capture=None, calibrate=None, calibrator=None, calibration_settings_service=None, tool_tcp_calibrator=None, robot_service=None, robot_config=None, settings_service=None)
```

### `TestStubCalibrationService`

```python
class TestStubCalibrationService(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def setUp(self)
```

```python
def test_capture_returns_success(self)
```

```python
def test_calibrate_camera_returns_success(self)
```

```python
def test_calibrate_robot_returns_success(self)
```

```python
def test_calibrate_camera_and_robot_returns_success(self)
```

```python
def test_calibrate_camera_tcp_offset_returns_success(self)
```

```python
def test_load_calibration_settings_returns_settings(self)
```

```python
def test_preview_robot_calibration_returns_successful_preview(self)
```

```python
def test_intrinsic_capture_config_returns_default_config(self)
```

```python
def test_intrinsic_auto_capture_is_not_running_by_default(self)
```

### `TestCalibrationApplicationServiceDelegation`

```python
class TestCalibrationApplicationServiceDelegation(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_capture_delegates_to_vision(self)
```

```python
def test_calibrate_camera_delegates_to_vision(self)
```

```python
def test_calibrate_robot_calls_process_controller_and_returns_success(self)
```

```python
def test_select_robot_calibration_target_uses_configured_area_profile(self)
```

```python
def test_select_robot_calibration_target_rejects_shared_global_profile(self)
```

```python
def test_local_test_pose_uses_target_z_and_area_observer_orientation(self)
```

```python
def test_local_test_pose_uses_calibration_target_z_not_observer_z(self)
```

```python
def test_local_test_pose_rejects_robot_away_from_area_observer(self)
```

```python
def test_visual_test_routes_from_active_work_area_in_per_area_mode(self)
```

```python
def test_visual_test_rejects_active_area_without_profile_in_per_area_mode(self)
```

```python
def test_calibrate_camera_and_robot_short_circuits_on_camera_failure(self)
```

```python
def test_calibrate_camera_and_robot_starts_robot_on_camera_success(self)
```

```python
def test_calibrate_camera_and_robot_calls_camera_first(self)
```

```python
def test_calibrate_camera_and_robot_does_not_call_controller_on_camera_failure(self)
```

```python
def test_calibrate_camera_tcp_offset_requires_existing_calibration(self)
```

```python
def test_camera_tcp_area_requires_per_area_mode(self)
```

```python
def test_camera_tcp_area_can_use_shared_global_vision_profile(self)
```

```python
def test_calibrate_camera_tcp_offset_delegates_to_calibrator_when_calibrated(self)
```

```python
def test_stop_calibration_stops_camera_tcp_calibrator(self)
```

```python
def test_tool_tcp_methods_delegate_to_calibrator(self)
```

```python
def test_start_tool_tcp_calibration_refuses_nonzero_tool(self)
```

```python
def test_start_tool_tcp_calibration_refuses_nonzero_workobject(self)
```

```python
def test_start_tool_tcp_calibration_checks_latest_saved_robot_settings(self)
```

```python
def test_tool_tcp_methods_report_not_configured(self)
```

```python
def test_stop_calibration_stops_tool_tcp_calibrator(self)
```

```python
def test_service_with_none_vision_raises_on_call(self)
```

```python
def test_load_calibration_settings_delegates_to_bridge_service(self)
```

```python
def test_save_calibration_settings_delegates_to_bridge_service(self)
```

```python
def test_measure_area_grid_prefers_area_observer_pose(self)
```

```python
def test_verify_height_model_prefers_area_observer_pose(self)
```

```python
def test_verify_area_grid_uses_height_measurement_pose_instead_of_observer_pose(self)
```
