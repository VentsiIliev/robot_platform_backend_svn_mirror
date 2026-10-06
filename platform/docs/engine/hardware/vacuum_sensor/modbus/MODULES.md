# Module reference: `src/engine/hardware/vacuum_sensor/modbus`

[Package guide](README.md) · [Complete source index](../../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [modbus_vacuum_sensor_factory.py](#modbus_vacuum_sensor_factorypy)
- [modbus_vacuum_sensor_transport.py](#modbus_vacuum_sensor_transportpy)

## `__init__.py`

Source: [src/engine/hardware/vacuum_sensor/modbus/__init__.py](../../../../../src/engine/hardware/vacuum_sensor/modbus/__init__.py).

Imports (including optional/function-local imports; not a startup dependency list): `src.engine.hardware.vacuum_sensor.modbus.modbus_vacuum_sensor_factory`, `src.engine.hardware.vacuum_sensor.modbus.modbus_vacuum_sensor_transport`.

Package-level import/export surface:

```python
from src.engine.hardware.vacuum_sensor.modbus.modbus_vacuum_sensor_factory import build_modbus_vacuum_sensor_service
from src.engine.hardware.vacuum_sensor.modbus.modbus_vacuum_sensor_transport import ModbusVacuumSensorTransport
```

Module declarations (expressions are shown without evaluating them):

```python
__all__ = ['ModbusVacuumSensorTransport', 'build_modbus_vacuum_sensor_service']
```

## `modbus_vacuum_sensor_factory.py`

Source: [src/engine/hardware/vacuum_sensor/modbus/modbus_vacuum_sensor_factory.py](../../../../../src/engine/hardware/vacuum_sensor/modbus/modbus_vacuum_sensor_factory.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `src.engine.hardware.communication.modbus.modbus`, `src.engine.hardware.vacuum_sensor.interfaces.i_vacuum_sensor_service`, `src.engine.hardware.vacuum_sensor.interfaces.i_vacuum_sensor_transport`, `src.engine.hardware.vacuum_sensor.modbus.modbus_vacuum_sensor_transport`, `src.engine.hardware.vacuum_sensor.models.vacuum_sensor_config`, `src.engine.hardware.vacuum_sensor.vacuum_sensor_service`.

### `build_modbus_vacuum_sensor_service`

```python
def build_modbus_vacuum_sensor_service(modbus_config: ModbusConfig, sensor_config: VacuumSensorConfig) -> IVacuumSensorService
```

Build a VacuumSensorService wired to Modbus RTU.

## `modbus_vacuum_sensor_transport.py`

Source: [src/engine/hardware/vacuum_sensor/modbus/modbus_vacuum_sensor_transport.py](../../../../../src/engine/hardware/vacuum_sensor/modbus/modbus_vacuum_sensor_transport.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `src.engine.hardware.communication.modbus.modbus_register_transport`, `src.engine.hardware.vacuum_sensor.interfaces.i_vacuum_sensor_transport`.

### `ModbusVacuumSensorTransport`

```python
class ModbusVacuumSensorTransport(ModbusRegisterTransport, IVacuumSensorTransport):
```

Modbus RTU transport for vacuum-sensor relay/coil boards. Reads the sensor output as a coil (function code 1), mirroring the vacuum-pump transport used on the same relay-board family. Override read_register if the sensor is exposed on a discrete input (FC2) or a holding register (default FC3) instead.

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def read_register(self, address: int) -> int
```
