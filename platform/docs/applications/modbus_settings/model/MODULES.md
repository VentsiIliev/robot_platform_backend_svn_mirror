# Module reference: `src/applications/modbus_settings/model`

[Package guide](README.md) · [Complete source index](../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [mapper.py](#mapperpy)
- [modbus_settings_model.py](#modbus_settings_modelpy)

## `__init__.py`

Source: [src/applications/modbus_settings/model/__init__.py](../../../../src/applications/modbus_settings/model/__init__.py).

No top-level functions, classes or public value declarations; inspect the source for imports or entry-point statements.

## `mapper.py`

Source: [src/applications/modbus_settings/model/mapper.py](../../../../src/applications/modbus_settings/model/mapper.py).

Imports (including optional/function-local imports; not a startup dependency list): `copy`, `src.engine.hardware.communication.modbus.modbus`.

### `ModbusSettingsMapper`

```python
class ModbusSettingsMapper:
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
@staticmethod
def to_flat_dict(config: ModbusConfig) -> dict
```

```python
@staticmethod
def from_flat_dict(flat: dict, base: ModbusConfig) -> ModbusConfig
```

```python
@staticmethod
def device_to_flat_dict(config: ModbusDeviceConfig) -> dict
```

```python
@staticmethod
def device_from_flat_dict(flat: dict, base: ModbusDeviceConfig) -> ModbusDeviceConfig
```

## `modbus_settings_model.py`

Source: [src/applications/modbus_settings/model/modbus_settings_model.py](../../../../src/applications/modbus_settings/model/modbus_settings_model.py).

Imports (including optional/function-local imports; not a startup dependency list): `logging`, `src.applications.base.i_application_model`, `src.applications.modbus_settings.model.mapper`, `src.applications.modbus_settings.service.i_modbus_settings_service`, `src.engine.hardware.communication.modbus.i_modbus_action_service`, `src.engine.hardware.communication.modbus.modbus`, `typing`.

### `ModbusSettingsModel`

```python
class ModbusSettingsModel(IApplicationModel):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, settings_service: IModbusSettingsService, action_service: IModbusActionService)
```

```python
def load(self) -> ModbusConfig
```

```python
def save(self, flat: dict, **kwargs) -> None
```

```python
def save_profiles(self, profiles: dict[str, dict]) -> None
```

```python
def save_all(self, profiles: dict[str, dict], slaves: dict[str, dict]) -> None
```

Persist profiles and slave assignments as one configuration snapshot.

```python
def save_slaves(self, slaves: dict[str, dict]) -> None
```

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

```python
def config_from_flat(self, flat: dict) -> ModbusConfig
```
