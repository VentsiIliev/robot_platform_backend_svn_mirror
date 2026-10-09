# Module reference: `tests/applications`

[Package guide](README.md) · [Complete source index](../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [test_device_control_controller.py](#test_device_control_controllerpy)
- [test_intrinsic_capture_service.py](#test_intrinsic_capture_servicepy)
- [test_network_settings.py](#test_network_settingspy)
- [test_robot_jog_widget_localization.py](#test_robot_jog_widget_localizationpy)

## `__init__.py`

Source: [tests/applications/__init__.py](../../../tests/applications/__init__.py).

No top-level functions, classes or public value declarations; inspect the source for imports or entry-point statements.

## `test_device_control_controller.py`

Source: [tests/applications/test_device_control_controller.py](../../../tests/applications/test_device_control_controller.py).

Imports (including optional/function-local imports; not a startup dependency list): `PyQt6.QtCore`, `PyQt6.QtWidgets`, `logging`, `pl_gui.settings.settings_view.styles`, `src.applications.base.widgets.keyboard_number_field`, `src.applications.camera_settings.service.i_camera_settings_service`, `src.applications.camera_settings.view.camera_devices_widget`, `src.applications.device_control.controller.device_control_controller`, `src.applications.device_control.dryer.view`, `src.applications.device_control.view.device_control_view`, `src.engine.hardware.dryer.models.dryer_config`, `src.robot_systems.paint.applications.paint_head_settings.paint_head_settings_view`, `unittest`, `unittest.mock`.

### `TestDeviceControlController`

```python
class TestDeviceControlController(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_normal_action_does_not_access_lifecycle_enabled_value(self) -> None
```

```python
def test_lifecycle_request_records_requested_enabled_state(self) -> None
```

```python
def test_failed_enable_rolls_optimistic_toggle_back_to_inactive(self) -> None
```

```python
def test_completed_action_refreshes_only_the_acted_device(self) -> None
```

```python
def test_load_attaches_and_loads_optional_dryer_panel(self) -> None
```

```python
def test_stop_stops_optional_dryer_controller(self) -> None
```

```python
def test_load_and_stop_manage_extension_panels(self) -> None
```

```python
def test_extension_panel_for_device_is_embedded_in_its_tab(self) -> None
```

### `TestDeviceControlView`

```python
class TestDeviceControlView(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
@classmethod
def setUpClass(cls) -> None
```

```python
def test_setup_does_not_emit_enable_request_for_enabled_device(self) -> None
```

```python
def test_device_tab_scrolls_as_one_complete_page(self) -> None
```

```python
def test_dryer_settings_use_editable_parameter_tables(self) -> None
```

```python
def test_custom_panel_is_added_as_a_top_level_tab(self) -> None
```

```python
def test_sidebar_keeps_selected_device_checked_on_repeated_click(self) -> None
```

```python
def test_camera_device_mode_switches_assignment_and_preview_role(self) -> None
```

```python
def test_paint_head_uses_touch_fields_and_preserves_save_values(self) -> None
```

## `test_intrinsic_capture_service.py`

Source: [tests/applications/test_intrinsic_capture_service.py](../../../tests/applications/test_intrinsic_capture_service.py).

Imports (including optional/function-local imports; not a startup dependency list): `src.applications.intrinsic_calibration_capture.service.intrinsic_capture_service`, `types`, `unittest`, `unittest.mock`.

### `TestIntrinsicCaptureRawFrames`

```python
class TestIntrinsicCaptureRawFrames(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_capture_uses_raw_frame_without_processed_frame_fallback(self)
```

```python
def test_capture_rejects_missing_vision_service(self)
```

```python
def test_capture_rejects_service_without_raw_frame_api(self)
```

```python
def test_capture_rejects_missing_raw_frame_without_processed_fallback(self)
```

## `test_network_settings.py`

Source: [tests/applications/test_network_settings.py](../../../tests/applications/test_network_settings.py).

Imports (including optional/function-local imports; not a startup dependency list): `PyQt6.QtWidgets`, `os`, `src.applications.base.widgets.keyboard_number_field`, `src.applications.network_settings.controller.network_settings_controller`, `src.applications.network_settings.service.network_settings_service`, `src.applications.network_settings.view.network_settings_view`, `subprocess`, `sys`, `unittest`, `unittest.mock`.

### `NetworkSettingsServiceTests`

```python
class NetworkSettingsServiceTests(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_linux_wifi_ipv4_uses_active_connection(self) -> None
```

```python
def test_invalid_manual_ipv4_does_not_run_network_command(self) -> None
```

```python
def test_secure_wifi_requires_password_before_backend_call(self) -> None
```

```python
def test_remote_support_uses_only_local_controller_client(self) -> None
```

### `NetworkSettingsViewTests`

```python
class NetworkSettingsViewTests(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
@classmethod
def setUpClass(cls) -> None
```

```python
def test_wifi_actions_follow_selected_connection(self) -> None
```

```python
def test_ipv4_dialog_uses_shared_touch_prefix_field(self) -> None
```

```python
def test_controller_schedules_actions_without_blocking_view(self) -> None
```

```python
def test_remote_switch_waits_for_confirmed_state(self) -> None
```

```python
def test_remote_mismatch_is_visible(self) -> None
```

```python
def test_remote_error_replaces_checking_and_can_recover(self) -> None
```

```python
def test_opening_remote_tab_requests_fresh_service_state(self) -> None
```

```python
def test_real_workers_finish_without_freezing_startup(self) -> None
```

## `test_robot_jog_widget_localization.py`

Source: [tests/applications/test_robot_jog_widget_localization.py](../../../tests/applications/test_robot_jog_widget_localization.py).

Imports (including optional/function-local imports; not a startup dependency list): `PyQt6.QtCore`, `PyQt6.QtWidgets`, `__future__`, `os`, `src.applications.base.robot_jog_widget`, `unittest`, `unittest.mock`.

### `TestRobotJogWidgetLocalization`

```python
class TestRobotJogWidgetLocalization(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
@classmethod
def setUpClass(cls) -> None
```

```python
def test_initial_render_uses_stable_translation_context(self) -> None
```

```python
def test_language_change_retranslates_dynamic_mode_labels(self) -> None
```

```python
def test_maximum_linear_servo_speed_is_labeled_and_requested_as_200_mm_s(self) -> None
```

```python
def test_maximum_linear_step_remains_250_mm(self) -> None
```

```python
def test_j6_full_turn_buttons_emit_single_360_degree_requests(self) -> None
```
