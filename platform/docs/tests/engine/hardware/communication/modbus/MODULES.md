# Module reference: `tests/engine/hardware/communication/modbus`

[Package guide](README.md) · [Complete source index](../../../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [test_modbus_action_service.py](#test_modbus_action_servicepy)
- [test_modbus_config.py](#test_modbus_configpy)

## `__init__.py`

Source: [tests/engine/hardware/communication/modbus/__init__.py](../../../../../../tests/engine/hardware/communication/modbus/__init__.py).

No top-level functions, classes or public value declarations; inspect the source for imports or entry-point statements.

## `test_modbus_action_service.py`

Source: [tests/engine/hardware/communication/modbus/test_modbus_action_service.py](../../../../../../tests/engine/hardware/communication/modbus/test_modbus_action_service.py).

Imports (including optional/function-local imports; not a startup dependency list): `pathlib`, `src.engine.hardware.communication.modbus.i_modbus_action_service`, `src.engine.hardware.communication.modbus.modbus`, `src.engine.hardware.communication.modbus.modbus_action_service`, `subprocess`, `sys`, `tempfile`, `unittest`, `unittest.mock`.

### `TestModbusActionServiceInterface`

```python
class TestModbusActionServiceInterface(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_implements_i_modbus_action_service(self)
```

```python
def test_has_detect_ports_method(self)
```

```python
def test_has_test_connection_method(self)
```

```python
def test_has_grant_serial_port_permissions_method(self)
```

```python
def test_has_set_serial_port_low_latency_method(self)
```

```python
def test_instantiation_requires_no_settings_dependency(self)
```

### `TestModbusActionServiceDetectPortsSuccess`

```python
class TestModbusActionServiceDetectPortsSuccess(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_returns_list(self)
```

```python
def test_returns_correct_port_names(self)
```

```python
def test_returns_single_port(self)
```

```python
def test_returns_empty_when_no_ports(self)
```

```python
def test_skips_ports_without_usb_vid(self)
```

```python
def test_calls_comports(self)
```

```python
def test_logs_open_failure_reason_and_continues(self)
```

### `TestModbusActionServiceDetectPortsFailure`

```python
class TestModbusActionServiceDetectPortsFailure(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_returns_empty_list_when_serial_not_installed(self)
```

```python
def test_returns_list_type_on_import_error(self)
```

```python
def test_returns_empty_list_when_comports_raises(self)
```

```python
def test_runtime_exception_returns_empty_list(self)
```

### `TestModbusActionServiceGrantPermissions`

```python
class TestModbusActionServiceGrantPermissions(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_grants_permissions_for_usb_serial_ports_with_vid(self)
```

```python
def test_uses_pkexec_when_not_root(self)
```

```python
def test_returns_empty_when_no_permission_targets(self)
```

### `TestModbusActionServiceLowLatency`

```python
class TestModbusActionServiceLowLatency(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_sets_and_verifies_latency_timer(self)
```

```python
def test_raises_when_no_latency_timer_is_available(self)
```

```python
def test_dismissed_authorization_has_clear_error(self)
```

```python
def test_returns_empty_when_permission_command_fails(self)
```

### `TestModbusActionServiceTestConnectionSuccess`

```python
class TestModbusActionServiceTestConnectionSuccess(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_returns_true_on_successful_open(self)
```

```python
def test_returns_bool(self)
```

```python
def test_passes_port_to_serial(self)
```

```python
def test_passes_baudrate_to_serial(self)
```

```python
def test_passes_parity_to_serial(self)
```

```python
def test_passes_timeout_to_serial(self)
```

```python
def test_passes_bytesize_to_serial(self)
```

```python
def test_passes_stopbits_to_serial(self)
```

### `TestModbusActionServiceTestConnectionFailure`

```python
class TestModbusActionServiceTestConnectionFailure(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_returns_false_when_serial_not_installed(self)
```

```python
def test_returns_false_on_serial_exception(self)
```

```python
def test_returns_false_on_permission_error(self)
```

```python
def test_returns_false_on_runtime_error(self)
```

```python
def test_catastrophic_exception_returns_false(self)
```

```python
def test_returns_bool_on_failure(self)
```

### `TestModbusActionServiceIsolation`

```python
class TestModbusActionServiceIsolation(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_detect_ports_failure_does_not_affect_test_connection(self)
```

```python
def test_multiple_calls_are_independent(self)
```

## `test_modbus_config.py`

Source: [tests/engine/hardware/communication/modbus/test_modbus_config.py](../../../../../../tests/engine/hardware/communication/modbus/test_modbus_config.py).

Imports (including optional/function-local imports; not a startup dependency list): `src.engine.hardware.communication.modbus.modbus`, `unittest`.

### `TestModbusConfigDefaults`

```python
class TestModbusConfigDefaults(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def setUp(self)
```

```python
def test_default_port(self)
```

```python
def test_default_baudrate(self)
```

```python
def test_default_bytesize(self)
```

```python
def test_default_stopbits(self)
```

```python
def test_default_parity(self)
```

```python
def test_default_timeout(self)
```

```python
def test_default_slave_address(self)
```

```python
def test_default_max_retries(self)
```

### `TestModbusConfigConstruction`

```python
class TestModbusConfigConstruction(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_custom_port(self)
```

```python
def test_custom_baudrate(self)
```

```python
def test_custom_bytesize(self)
```

```python
def test_custom_stopbits(self)
```

```python
def test_custom_parity(self)
```

```python
def test_custom_timeout(self)
```

```python
def test_custom_slave_address(self)
```

```python
def test_custom_max_retries(self)
```

```python
def test_two_configs_with_same_values_are_equal(self)
```

```python
def test_two_configs_with_different_values_are_not_equal(self)
```

### `TestModbusConfigToDict`

```python
class TestModbusConfigToDict(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def setUp(self)
```

```python
def test_all_keys_present(self)
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

```python
def test_returns_new_dict_each_call(self)
```

### `TestModbusConfigFromDict`

```python
class TestModbusConfigFromDict(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_port_parsed(self)
```

```python
def test_baudrate_parsed(self)
```

```python
def test_bytesize_parsed(self)
```

```python
def test_stopbits_parsed(self)
```

```python
def test_parity_parsed(self)
```

```python
def test_timeout_parsed(self)
```

```python
def test_slave_address_parsed(self)
```

```python
def test_max_retries_parsed(self)
```

```python
def test_missing_keys_use_defaults(self)
```

```python
def test_partial_dict_keeps_unspecified_defaults(self)
```

```python
def test_full_roundtrip(self)
```

### `TestModbusConfigUpdateField`

```python
class TestModbusConfigUpdateField(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_update_port(self)
```

```python
def test_update_baudrate(self)
```

```python
def test_update_slave_address(self)
```

```python
def test_update_timeout(self)
```

```python
def test_update_invalid_field_raises_value_error(self)
```

```python
def test_update_does_not_affect_other_fields(self)
```

### `TestModbusConfigSerializer`

```python
class TestModbusConfigSerializer(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def setUp(self)
```

```python
def test_settings_type(self)
```

```python
def test_get_default_returns_modbus_config(self)
```

```python
def test_get_default_has_correct_port(self)
```

```python
def test_get_default_returns_new_instance_each_call(self)
```

```python
def test_to_dict_returns_dict(self)
```

```python
def test_to_dict_contains_all_keys(self)
```

```python
def test_from_dict_returns_modbus_config(self)
```

```python
def test_from_dict_parses_port(self)
```

```python
def test_serializer_roundtrip(self)
```

```python
def test_serializer_roundtrip_all_fields(self)
```
