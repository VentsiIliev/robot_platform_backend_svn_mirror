# Module reference: `src/engine/hardware/vacuum_pump/modbus`

[Package guide](README.md) · [Complete source index](../../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [modbus_vacuum_pump_factory.py](#modbus_vacuum_pump_factorypy)
- [modbus_vacuum_pump_transport.py](#modbus_vacuum_pump_transportpy)

## `__init__.py`

Source: [src/engine/hardware/vacuum_pump/modbus/__init__.py](../../../../../src/engine/hardware/vacuum_pump/modbus/__init__.py).

Imports (including optional/function-local imports; not a startup dependency list): `src.engine.hardware.vacuum_pump.modbus.modbus_vacuum_pump_factory`, `src.engine.hardware.vacuum_pump.modbus.modbus_vacuum_pump_transport`.

Package-level import/export surface:

```python
from src.engine.hardware.vacuum_pump.modbus.modbus_vacuum_pump_factory import build_modbus_vacuum_pump_controller
from src.engine.hardware.vacuum_pump.modbus.modbus_vacuum_pump_transport import ModbusVacuumPumpTransport
```

Module declarations (expressions are shown without evaluating them):

```python
__all__ = ['ModbusVacuumPumpTransport', 'build_modbus_vacuum_pump_controller']
```

## `modbus_vacuum_pump_factory.py`

Source: [src/engine/hardware/vacuum_pump/modbus/modbus_vacuum_pump_factory.py](../../../../../src/engine/hardware/vacuum_pump/modbus/modbus_vacuum_pump_factory.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `src.engine.hardware.communication.modbus.modbus`, `src.engine.hardware.communication.transport_registry`, `src.engine.hardware.vacuum_pump.interfaces.i_vacuum_pump_controller`, `src.engine.hardware.vacuum_pump.modbus.modbus_vacuum_pump_transport`, `src.engine.hardware.vacuum_pump.models.vacuum_pump_config`, `src.engine.hardware.vacuum_pump.vacuum_pump_controller`.

### `build_modbus_vacuum_pump_controller`

```python
def build_modbus_vacuum_pump_controller(modbus_config: ModbusConfig, vacuum_config: VacuumPumpConfig | None=None, profile_name: str='default') -> IVacuumPumpController
```

## `modbus_vacuum_pump_transport.py`

Source: [src/engine/hardware/vacuum_pump/modbus/modbus_vacuum_pump_transport.py](../../../../../src/engine/hardware/vacuum_pump/modbus/modbus_vacuum_pump_transport.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `src.engine.hardware.communication.modbus.xinje_ma_8x8yr_transport`, `src.engine.hardware.vacuum_pump.interfaces.i_vacuum_pump_transport`.

Module declarations (expressions are shown without evaluating them):

```python
__all__ = ['ModbusExceptionResponse', 'ModbusVacuumPumpTransport', '_crc16']
```

### `ModbusVacuumPumpTransport`

```python
class ModbusVacuumPumpTransport(XinjeMA8X8YRTransport, IVacuumPumpTransport):
```

Backward-compatible vacuum-pump view of the Xinje MA transport. The protocol implementation belongs to the shared communication layer; this name remains for existing vacuum-pump callers and integrations.
