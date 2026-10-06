# Module reference: `tests/engine`

[Package guide](README.md) · [Complete source index](../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [test_base_json_settings_repository.py](#test_base_json_settings_repositorypy)
- [test_device_control_adapters.py](#test_device_control_adapterspy)
- [test_dryer_controller.py](#test_dryer_controllerpy)
- [test_dryer_peripheral_settings.py](#test_dryer_peripheral_settingspy)
- [test_dryer_service.py](#test_dryer_servicepy)
- [test_intrinsic_capture_runner.py](#test_intrinsic_capture_runnerpy)
- [test_modbus_fc16_register_transport.py](#test_modbus_fc16_register_transportpy)
- [test_physical_control_buttons.py](#test_physical_control_buttonspy)
- [test_work_area_service.py](#test_work_area_servicepy)
- [test_xinje_ma_8x8yr_transport.py](#test_xinje_ma_8x8yr_transportpy)

## `__init__.py`

Source: [tests/engine/__init__.py](../../../tests/engine/__init__.py).

No top-level functions, classes or public value declarations; inspect the source for imports or entry-point statements.

## `test_base_json_settings_repository.py`

Source: [tests/engine/test_base_json_settings_repository.py](../../../tests/engine/test_base_json_settings_repository.py).

Imports (including optional/function-local imports; not a startup dependency list): `dataclasses`, `json`, `src.engine.repositories.interfaces`, `src.engine.repositories.json`, `typing`, `unittest`, `unittest.mock`.

### `_FakeSettings`

```python
@dataclass
class _FakeSettings:
```

Declared fields/defaults:

```python
value: int = 42
```

### `_FakeSerializer`

```python
class _FakeSerializer(ISettingsSerializer[_FakeSettings]):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
@property
def settings_type(self) -> str
```

```python
def get_default(self) -> _FakeSettings
```

```python
def to_dict(self, settings: _FakeSettings) -> Dict[str, Any]
```

```python
def from_dict(self, data: Dict[str, Any]) -> _FakeSettings
```

### `TestBaseJsonSettingsRepository`

```python
class TestBaseJsonSettingsRepository(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_load_returns_default_when_no_file_path(self)
```

```python
@patch('src.engine.repositories.json.base_json_settings_repository.os.path.exists', return_value=False)
@patch('src.engine.repositories.json.base_json_settings_repository.os.makedirs')
@patch('builtins.open', mock_open())
def test_load_creates_default_file_when_missing(self, mock_makedirs, mock_exists)
```

```python
@patch('src.engine.repositories.json.base_json_settings_repository.os.path.exists', return_value=True)
def test_load_reads_existing_file(self, _mock_exists)
```

```python
@patch('src.engine.repositories.json.base_json_settings_repository.os.path.exists', return_value=True)
def test_load_returns_default_on_json_decode_error(self, _mock_exists)
```

```python
@patch('src.engine.repositories.json.base_json_settings_repository.os.path.exists', return_value=True)
def test_load_raises_settings_load_error_on_unexpected_exception(self, _mock_exists)
```

```python
def test_save_raises_when_no_file_path(self)
```

```python
@patch('src.engine.repositories.json.base_json_settings_repository.os.makedirs')
@patch('builtins.open', mock_open())
def test_save_writes_file(self, mock_makedirs)
```

```python
@patch('src.engine.repositories.json.base_json_settings_repository.os.makedirs', side_effect=OSError('no perm'))
def test_save_raises_settings_save_error_on_write_failure(self, _mock_makedirs)
```

```python
def test_exists_false_when_no_path(self)
```

```python
@patch('src.engine.repositories.json.base_json_settings_repository.os.path.exists', return_value=True)
def test_exists_true_when_file_present(self, _)
```

```python
@patch('src.engine.repositories.json.base_json_settings_repository.os.path.exists', return_value=False)
def test_exists_false_when_file_absent(self, _)
```

## `test_device_control_adapters.py`

Source: [tests/engine/test_device_control_adapters.py](../../../tests/engine/test_device_control_adapters.py).

Imports (including optional/function-local imports; not a startup dependency list): `src.engine.hardware.peripherals`, `src.engine.hardware.peripherals.device_control_adapters`, `types`, `unittest`, `unittest.mock`.

### `_Binary`

```python
class _Binary:
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self)
```

```python
def turn_on(self)
```

```python
def turn_off(self)
```

```python
def read_state(self)
```

### `_Sensor`

```python
class _Sensor:
```

Declared fields/defaults:

```python
last_raw_value = 0
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self)
```

```python
def is_vacuum_detected(self)
```

```python
def is_healthy(self)
```

### `_Buttons`

```python
class _Buttons:
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self)
```

```python
def read_output_states(self)
```

```python
def read_states(self)
```

```python
def set_button(self, name, pressed)
```

### `DeviceControlAdaptersTest`

```python
class DeviceControlAdaptersTest(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def setUp(self)
```

```python
def test_builds_only_configured_devices_and_exposes_actions(self)
```

```python
def test_missing_service_is_skipped(self)
```

```python
def test_device_lifecycle_persists_and_gates_actions(self)
```

```python
def test_dryer_named_action_uses_named_controller_method(self)
```

```python
def test_dryer_next_position_fails_when_no_fresh_status_cycle_is_seen(self)
```

```python
def test_failed_register_read_keeps_binary_device_disabled(self)
```

```python
def test_sensor_and_buttons_read_hardware_before_enabling(self)
```

```python
def test_empty_commands_expose_no_ui_actions(self)
```

## `test_dryer_controller.py`

Source: [tests/engine/test_dryer_controller.py](../../../tests/engine/test_dryer_controller.py).

Imports (including optional/function-local imports; not a startup dependency list): `src.engine.hardware.dryer.dryer_controller`, `src.engine.hardware.dryer.models.dryer_config`, `src.engine.hardware.dryer.models.dryer_modbus_registers`, `src.engine.hardware.dryer.models.dryer_status`, `src.engine.hardware.dryer.models.dryer_write_data`, `unittest`, `unittest.mock`.

### `TestDryerController`

```python
class TestDryerController(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_robot_system_can_override_commands_and_statuses(self) -> None
```

```python
def test_decodes_current_firmware_status_flags(self) -> None
```

```python
def test_status_read_logs_raw_register_and_decoded_flags(self) -> None
```

```python
def test_status_read_retries_using_configured_max_retries(self) -> None
```

```python
def test_status_read_reports_unhealthy_after_retries_are_exhausted(self) -> None
```

```python
def test_command_replaces_stale_payload_command(self) -> None
```

```python
def test_execute_command_uses_configured_numeric_value(self) -> None
```

```python
def test_next_position_logs_command_register_target_and_result(self) -> None
```

```python
def test_next_position_reports_single_register_write_failure(self) -> None
```

```python
def test_next_position_retries_using_configured_max_retries(self) -> None
```

```python
def test_next_position_stops_after_configured_retries_are_exhausted(self) -> None
```

```python
def test_next_position_does_not_retry_when_movement_confirms_lost_ack(self) -> None
```

```python
def test_initialize_writes_config_then_sends_next_position(self) -> None
```

```python
def test_initialize_does_not_send_next_position_when_config_write_fails(self) -> None
```

```python
def test_initialize_fails_when_next_position_done_is_not_confirmed(self) -> None
```

```python
def test_decodes_every_firmware_status_flag(self) -> None
```

```python
def test_writes_current_seventeen_register_block(self) -> None
```

```python
def test_write_data_retries_using_configured_max_retries(self) -> None
```

```python
def test_write_data_stops_after_configured_retries_are_exhausted(self) -> None
```

```python
def test_rev_minute_is_transmitted_without_scaling(self) -> None
```

```python
def test_successful_commands_wait_before_status_can_be_checked(self) -> None
```

```python
def test_eject_retries_using_configured_max_retries(self) -> None
```

```python
def test_eject_does_not_retry_when_status_confirms_lost_ack(self) -> None
```

```python
def test_acceleration_is_transmitted_in_integer_tenths(self) -> None
```

```python
def test_updated_config_is_used_by_subsequent_default_commands(self) -> None
```

```python
def test_robot_system_can_override_register_addresses(self) -> None
```

## `test_dryer_peripheral_settings.py`

Source: [tests/engine/test_dryer_peripheral_settings.py](../../../tests/engine/test_dryer_peripheral_settings.py).

Imports (including optional/function-local imports; not a startup dependency list): `src.applications.device_control.dryer.application_service`, `src.engine.hardware.dryer.models.dryer_config`, `src.engine.hardware.peripherals`, `unittest`, `unittest.mock`.

### `TestDeviceControlDryerPersistence`

```python
class TestDeviceControlDryerPersistence(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_dryer_status_masks_survive_settings_round_trip(self) -> None
```

```python
def test_device_control_loads_and_saves_dedicated_dryer_config(self) -> None
```

## `test_dryer_service.py`

Source: [tests/engine/test_dryer_service.py](../../../tests/engine/test_dryer_service.py).

Imports (including optional/function-local imports; not a startup dependency list): `src.engine.hardware.dryer.dryer_service`, `src.engine.hardware.dryer.models.dryer_config`, `threading`, `time`, `unittest`, `unittest.mock`.

### `TestDryerService`

```python
class TestDryerService(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_async_enable_returns_before_initialization_completes(self) -> None
```

```python
def test_disable_cancels_async_initialization_controller(self) -> None
```

```python
def test_failed_next_position_verification_keeps_service_disabled(self) -> None
```

```python
def test_failed_enable_keeps_stable_service_disabled_and_reports_error(self) -> None
```

```python
def test_disable_releases_controller_and_commands_fail_safely(self) -> None
```

## `test_intrinsic_capture_runner.py`

Source: [tests/engine/test_intrinsic_capture_runner.py](../../../tests/engine/test_intrinsic_capture_runner.py).

Imports (including optional/function-local imports; not a startup dependency list): `numpy`, `src.engine.robot.calibration.intrinsic_capture.runner`, `src.engine.robot.calibration.intrinsic_capture.types`, `threading`, `types`, `unittest`, `unittest.mock`.

### `_PoseDrivenCharucoDetector`

```python
class _PoseDrivenCharucoDetector:
```

Declared fields/defaults:

```python
pose = None
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, **_kwargs)
```

```python
def detect(self, _frame)
```

### `IntrinsicCaptureRunnerTests`

```python
class IntrinsicCaptureRunnerTests(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_charuco_maps_image_grid_before_capture_and_respects_sweep_bounds(self)
```

## `test_modbus_fc16_register_transport.py`

Source: [tests/engine/test_modbus_fc16_register_transport.py](../../../tests/engine/test_modbus_fc16_register_transport.py).

Imports (including optional/function-local imports; not a startup dependency list): `src.engine.hardware.communication.modbus.modbus_fc16_register_transport`, `src.engine.hardware.communication.transport_registry`, `unittest`, `unittest.mock`.

### `TestModbusFc16RegisterTransport`

```python
class TestModbusFc16RegisterTransport(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_single_register_write_uses_fc16_batch_operation(self) -> None
```

```python
def test_transport_is_registered(self) -> None
```

## `test_physical_control_buttons.py`

Source: [tests/engine/test_physical_control_buttons.py](../../../tests/engine/test_physical_control_buttons.py).

Imports (including optional/function-local imports; not a startup dependency list): `src.engine.hardware.physical_control_buttons.modbus.modbus_physical_control_buttons`, `unittest`, `unittest.mock`.

### `TestModbusPhysicalControlButtons`

```python
class TestModbusPhysicalControlButtons(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_set_button_writes_configured_output(self) -> None
```

```python
def test_read_output_states_reads_configured_outputs(self) -> None
```

```python
def test_failed_operation_updates_cached_health(self) -> None
```

## `test_work_area_service.py`

Source: [tests/engine/test_work_area_service.py](../../../tests/engine/test_work_area_service.py).

Imports (including optional/function-local imports; not a startup dependency list): `src.engine.common_settings_ids`, `src.engine.work_areas.work_area_service`, `src.engine.work_areas.work_area_settings`, `src.shared_contracts.declarations`, `unittest`, `unittest.mock`.

### `TestWorkAreaService`

```python
class TestWorkAreaService(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_defaults_active_area_from_robot_system_default(self)
```

```python
def test_empty_default_leaves_active_area_unknown(self)
```

```python
def test_active_area_requires_explicit_verification_after_set(self)
```

```python
def test_set_invalid_active_area_raises(self)
```

```python
def test_save_and_get_detection_roi(self)
```

```python
def test_get_brightness_roi_falls_back_to_detection(self)
```

```python
def test_get_area_definition_returns_declared_definition(self)
```

## `test_xinje_ma_8x8yr_transport.py`

Source: [tests/engine/test_xinje_ma_8x8yr_transport.py](../../../tests/engine/test_xinje_ma_8x8yr_transport.py).

Imports (including optional/function-local imports; not a startup dependency list): `os`, `serial`, `src.engine.hardware.communication.modbus.xinje_ma_8x8yr_transport`, `unittest`, `unittest.mock`.

### `TestXinjeMA8X8YRTransport`

```python
class TestXinjeMA8X8YRTransport(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_bounded_fd_write_completes_without_blocking(self) -> None
```

```python
def test_bounded_fd_write_times_out_when_fd_is_not_writable(self) -> None
```

```python
def test_read_input_uses_fc1_for_x_points(self) -> None
```

```python
def test_separate_transports_share_output_image(self) -> None
```
