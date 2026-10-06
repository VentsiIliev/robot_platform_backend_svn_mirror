# Module reference: `src/applications/modbus_settings/service`

[Package guide](README.md) · [Complete source index](../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [i_modbus_settings_service.py](#i_modbus_settings_servicepy)
- [modbus_settings_application_service.py](#modbus_settings_application_servicepy)
- [stub_modbus_action_service.py](#stub_modbus_action_servicepy)
- [stub_modbus_settings_service.py](#stub_modbus_settings_servicepy)

## `__init__.py`

Source: [src/applications/modbus_settings/service/__init__.py](../../../../src/applications/modbus_settings/service/__init__.py).

No top-level functions, classes or public value declarations; inspect the source for imports or entry-point statements.

## `i_modbus_settings_service.py`

Source: [src/applications/modbus_settings/service/i_modbus_settings_service.py](../../../../src/applications/modbus_settings/service/i_modbus_settings_service.py).

Imports (including optional/function-local imports; not a startup dependency list): `abc`, `src.engine.hardware.communication.modbus.modbus`.

### `IModbusSettingsService`

```python
class IModbusSettingsService(ABC):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
@abstractmethod
def load_config(self) -> ModbusConfig
```

```python
@abstractmethod
def save_config(self, config: ModbusConfig) -> None
```

## `modbus_settings_application_service.py`

Source: [src/applications/modbus_settings/service/modbus_settings_application_service.py](../../../../src/applications/modbus_settings/service/modbus_settings_application_service.py).

Imports (including optional/function-local imports; not a startup dependency list): `enum`, `logging`, `src.applications.modbus_settings.service.i_modbus_settings_service`, `src.engine.hardware.communication.modbus.modbus`, `src.engine.repositories.interfaces.i_settings_service`.

### `ModbusSettingsApplicationService`

```python
class ModbusSettingsApplicationService(IModbusSettingsService):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, settings_service: ISettingsService, config_key: Enum)
```

```python
def load_config(self) -> ModbusConfig
```

```python
def save_config(self, config: ModbusConfig) -> None
```

## `stub_modbus_action_service.py`

Source: [src/applications/modbus_settings/service/stub_modbus_action_service.py](../../../../src/applications/modbus_settings/service/stub_modbus_action_service.py).

Imports (including optional/function-local imports; not a startup dependency list): `src.engine.hardware.communication.modbus.i_modbus_action_service`, `src.engine.hardware.communication.modbus.modbus`, `typing`.

### `StubModbusActionService`

```python
class StubModbusActionService(IModbusActionService):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def detect_ports(self) -> List[str]
```

```python
def test_connection(self, config: ModbusConfig) -> bool
```

```python
def grant_serial_port_permissions(self) -> List[str]
```

```python
def set_serial_port_low_latency(self) -> List[str]
```

## `stub_modbus_settings_service.py`

Source: [src/applications/modbus_settings/service/stub_modbus_settings_service.py](../../../../src/applications/modbus_settings/service/stub_modbus_settings_service.py).

Imports (including optional/function-local imports; not a startup dependency list): `src.applications.modbus_settings.service.i_modbus_settings_service`, `src.engine.hardware.communication.modbus.modbus`.

### `StubModbusSettingsService`

```python
class StubModbusSettingsService(IModbusSettingsService):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self)
```

```python
def load_config(self) -> ModbusConfig
```

```python
def save_config(self, config: ModbusConfig) -> None
```
