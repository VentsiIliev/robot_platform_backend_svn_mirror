# Module reference: `tests/applications/modbus_settings`

[Package guide](README.md) · [Complete source index](../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [test_modbus_settings_controller.py](#test_modbus_settings_controllerpy)
- [test_modbus_settings_mapper.py](#test_modbus_settings_mapperpy)
- [test_modbus_settings_model.py](#test_modbus_settings_modelpy)
- [test_modbus_settings_view.py](#test_modbus_settings_viewpy)

## `__init__.py`

Source: [tests/applications/modbus_settings/__init__.py](../../../../tests/applications/modbus_settings/__init__.py).

No top-level functions, classes or public value declarations; inspect the source for imports or entry-point statements.

## `test_modbus_settings_controller.py`

Source: [tests/applications/modbus_settings/test_modbus_settings_controller.py](../../../../tests/applications/modbus_settings/test_modbus_settings_controller.py).

Imports (including optional/function-local imports; not a startup dependency list): `src.applications.base.widget_application`, `src.applications.modbus_settings.controller.modbus_settings_controller`, `src.applications.modbus_settings.model.mapper`, `src.applications.modbus_settings.model.modbus_settings_model`, `src.engine.hardware.communication.modbus.modbus`, `src.robot_systems.glue.glue_robot_system`, `unittest`, `unittest.mock`.

### `_make_view`

```python
def _make_view()
```

### `_make_model`

```python
def _make_model(config=None)
```

### `_make_controller`

```python
def _make_controller(config=None)
```

### `TestModbusSettingsControllerInit`

```python
class TestModbusSettingsControllerInit(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_wires_save_requested(self)
```

```python
def test_wires_detect_ports_requested(self)
```

```python
def test_wires_test_connection_requested(self)
```

```python
def test_wires_grant_permission_requested(self)
```

```python
def test_wires_set_low_latency_requested(self)
```

```python
def test_wires_destroyed(self)
```

### `TestModbusSettingsControllerLoad`

```python
class TestModbusSettingsControllerLoad(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_load_calls_model_load(self)
```

```python
def test_load_pushes_config_to_view(self)
```

### `TestModbusSettingsControllerSave`

```python
class TestModbusSettingsControllerSave(unittest.TestCase):
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

### `TestModbusSettingsControllerDetect`

```python
class TestModbusSettingsControllerDetect(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_on_ports_detected_pushes_to_view(self)
```

```python
def test_on_ports_detected_empty_list(self)
```

```python
def test_on_detect_failed_pushes_empty_to_view(self)
```

### `TestModbusSettingsControllerGrantPermission`

```python
class TestModbusSettingsControllerGrantPermission(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_on_permission_granted_pushes_success_to_view(self)
```

```python
def test_on_permission_granted_empty_pushes_failure_to_view(self)
```

### `TestModbusSettingsControllerLowLatency`

```python
class TestModbusSettingsControllerLowLatency(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_low_latency_success_pushes_verified_ports(self)
```

```python
def test_low_latency_failure_preserves_error_message(self)
```

```python
def test_on_permission_failed_pushes_failure_to_view(self)
```

### `TestModbusSettingsControllerTestConnection`

```python
class TestModbusSettingsControllerTestConnection(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_on_test_done_success_pushes_to_view(self)
```

```python
def test_on_test_done_failure_pushes_to_view(self)
```

```python
def test_on_test_failed_pushes_failure_to_view(self)
```

### `TestModbusSettingsControllerStop`

```python
class TestModbusSettingsControllerStop(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_stop_clears_active_list(self)
```

```python
def test_stop_returns_none_when_empty(self)
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
def test_factory_returns_widget_application(self)
```

```python
def test_factory_registers_messaging_service(self)
```

## `test_modbus_settings_mapper.py`

Source: [tests/applications/modbus_settings/test_modbus_settings_mapper.py](../../../../tests/applications/modbus_settings/test_modbus_settings_mapper.py).

Imports (including optional/function-local imports; not a startup dependency list): `src.applications.modbus_settings.model.mapper`, `src.engine.hardware.communication.modbus.modbus`, `unittest`.

### `TestModbusSettingsMapperToFlatDict`

```python
class TestModbusSettingsMapperToFlatDict(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def setUp(self)
```

```python
def test_all_expected_keys_present(self)
```

```python
def test_port_value(self)
```

```python
def test_baudrate_value(self)
```

```python
def test_parity_value(self)
```

```python
def test_timeout_value(self)
```

```python
def test_slave_address_value(self)
```

### `TestModbusSettingsMapperFromFlatDict`

```python
class TestModbusSettingsMapperFromFlatDict(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def setUp(self)
```

```python
def test_port_updated(self)
```

```python
def test_baudrate_cast_to_int(self)
```

```python
def test_bytesize_cast_to_int(self)
```

```python
def test_stopbits_cast_to_int(self)
```

```python
def test_parity_updated(self)
```

```python
def test_timeout_cast_to_float(self)
```

```python
def test_slave_address_cast_to_int(self)
```

```python
def test_max_retries_cast_to_int(self)
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

## `test_modbus_settings_model.py`

Source: [tests/applications/modbus_settings/test_modbus_settings_model.py](../../../../tests/applications/modbus_settings/test_modbus_settings_model.py).

Imports (including optional/function-local imports; not a startup dependency list): `src.applications.modbus_settings.model.mapper`, `src.applications.modbus_settings.model.modbus_settings_model`, `src.applications.modbus_settings.service.modbus_settings_application_service`, `src.engine.common_settings_ids`, `src.engine.hardware.communication.modbus.modbus`, `src.engine.hardware.communication.modbus.modbus_action_service`, `unittest`, `unittest.mock`.

### `_make_settings_service`

```python
def _make_settings_service(config=None)
```

### `_make_action_service`

```python
def _make_action_service()
```

### `_loaded`

```python
def _loaded(config=None)
```

### `TestModbusSettingsModelLoad`

```python
class TestModbusSettingsModelLoad(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_load_calls_settings_service(self)
```

```python
def test_load_returns_config(self)
```

```python
def test_config_cached_after_load(self)
```

### `TestModbusSettingsModelSave`

```python
class TestModbusSettingsModelSave(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_save_calls_save_config(self)
```

```python
def test_save_updates_port(self)
```

```python
def test_save_updates_baudrate(self)
```

```python
def test_save_updates_internal_cache(self)
```

```python
def test_save_without_prior_load_uses_default(self)
```

```python
def test_save_does_not_mutate_previous_config(self)
```

### `TestModbusSettingsModelPersistence`

```python
class TestModbusSettingsModelPersistence(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_save_all_persists_profile_and_slave_assignment_together(self)
```

```python
def test_save_all_persists_default_slave_transport_and_profile(self)
```

```python
def test_save_all_rejects_unknown_slave_profile(self)
```

```python
def test_save_profiles_replaces_deleted_profiles(self)
```

```python
def test_save_slaves_preserves_slave_values_when_rebuilding_map(self)
```

```python
def test_sequential_profile_and_slave_saves_share_updated_in_memory_config(self)
```

### `TestModbusSettingsModelDetectPorts`

```python
class TestModbusSettingsModelDetectPorts(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_detect_ports_delegates_to_action_service(self)
```

```python
def test_detect_ports_does_not_call_settings_service(self)
```

```python
def test_detect_ports_empty_list(self)
```

### `TestModbusSettingsModelGrantPermissions`

```python
class TestModbusSettingsModelGrantPermissions(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_grant_permissions_delegates_to_action_service(self)
```

```python
def test_grant_permissions_does_not_call_settings_service(self)
```

### `TestModbusSettingsModelLowLatency`

```python
class TestModbusSettingsModelLowLatency(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_low_latency_delegates_to_action_service(self)
```

### `TestModbusSettingsModelTestConnection`

```python
class TestModbusSettingsModelTestConnection(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_test_connection_delegates_to_action_service(self)
```

```python
def test_test_connection_passes_config_to_action_service(self)
```

```python
def test_test_connection_does_not_call_settings_service(self)
```

```python
def test_test_connection_failure(self)
```

### `TestModbusSettingsModelConfigFromFlat`

```python
class TestModbusSettingsModelConfigFromFlat(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_config_from_flat_uses_cached_base(self)
```

```python
def test_config_from_flat_no_load_uses_default(self)
```

```python
def test_config_from_flat_does_not_mutate_cache(self)
```

### `TestModbusSettingsApplicationService`

```python
class TestModbusSettingsApplicationService(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_load_config_reads_correct_key(self)
```

```python
def test_save_config_writes_correct_key(self)
```

```python
def test_service_has_no_detect_ports_method(self)
```

detect_ports belongs to IModbusActionService — not to the settings service.

```python
def test_service_has_no_test_connection_method(self)
```

test_connection belongs to IModbusActionService — not to the settings service.

### `TestModbusActionService`

```python
class TestModbusActionService(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_detect_ports_returns_list_on_import_error(self)
```

```python
def test_detect_ports_returns_empty_on_import_error(self)
```

```python
def test_test_connection_returns_false_on_import_error(self)
```

```python
def test_test_connection_returns_false_on_serial_error(self)
```

```python
def test_test_connection_returns_true_on_success(self)
```

```python
def test_test_connection_passes_serial_config_values(self)
```

## `test_modbus_settings_view.py`

Source: [tests/applications/modbus_settings/test_modbus_settings_view.py](../../../../tests/applications/modbus_settings/test_modbus_settings_view.py).

Imports (including optional/function-local imports; not a startup dependency list): `PyQt6.QtWidgets`, `os`, `src.applications.base.widgets.custom_virtual_keyboard`, `src.applications.base.widgets.keyboard_number_field`, `src.applications.modbus_settings.view.modbus_settings_view`, `src.engine.hardware.communication.modbus.modbus`, `unittest`, `unittest.mock`.

### `TestModbusSettingsViewSlaveSelection`

```python
class TestModbusSettingsViewSlaveSelection(unittest.TestCase):
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
def tearDown(self)
```

```python
def test_selecting_slave_loads_its_values_before_save_capture(self)
```

```python
def test_editing_transport_is_not_overwritten_when_selector_is_rebuilt(self)
```

```python
def test_tabs_and_dialog_fields_use_shared_touch_controls(self)
```

```python
def test_port_change_can_be_discarded_or_saved(self)
```

```python
def test_profile_edit_can_be_discarded(self)
```
