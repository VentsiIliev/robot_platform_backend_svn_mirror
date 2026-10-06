# Module reference: `src/engine/hardware/fan/modbus`

[Package guide](README.md) · [Complete source index](../../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [modbus_fan_control.py](#modbus_fan_controlpy)
- [modbus_fan_factory.py](#modbus_fan_factorypy)

## `__init__.py`

Source: [src/engine/hardware/fan/modbus/__init__.py](../../../../../src/engine/hardware/fan/modbus/__init__.py).

Imports (including optional/function-local imports; not a startup dependency list): `src.engine.hardware.fan.modbus.modbus_fan_control`.

Package-level import/export surface:

```python
from src.engine.hardware.fan.modbus.modbus_fan_control import ModbusFanControl
```

Module declarations (expressions are shown without evaluating them):

```python
__all__ = ['ModbusFanControl']
```

## `modbus_fan_control.py`

Source: [src/engine/hardware/fan/modbus/modbus_fan_control.py](../../../../../src/engine/hardware/fan/modbus/modbus_fan_control.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `src.engine.core.i_health_checkable`, `src.engine.hardware.communication.i_register_transport`, `src.engine.hardware.fan.interfaces.i_fan_control`, `src.engine.hardware.xinje`.

### `ModbusFanControl`

```python
class ModbusFanControl(IFanControl, IHealthCheckable):
```

Binary fan control through a configured register/coil transport.

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, transport: IRegisterTransport, register: int | str='Y0', on_value: int=1, off_value: int=0) -> None
```

```python
def turn_on(self) -> None
```

```python
def turn_off(self) -> None
```

```python
def read_state(self) -> bool
```

```python
def is_healthy(self) -> bool
```

## `modbus_fan_factory.py`

Source: [src/engine/hardware/fan/modbus/modbus_fan_factory.py](../../../../../src/engine/hardware/fan/modbus/modbus_fan_factory.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `src.engine.hardware.communication.modbus.modbus`, `src.engine.hardware.communication.transport_registry`, `src.engine.hardware.fan.interfaces.i_fan_control`, `src.engine.hardware.fan.modbus.modbus_fan_control`, `src.engine.hardware.peripherals`.

### `build_modbus_fan_control`

```python
def build_modbus_fan_control(modbus_config: ModbusConfig, peripheral_config: PeripheralConfig, peripheral_key: str='fan') -> IFanControl | None
```
