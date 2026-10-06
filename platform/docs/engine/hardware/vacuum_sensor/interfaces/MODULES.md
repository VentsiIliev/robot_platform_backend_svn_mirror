# Module reference: `src/engine/hardware/vacuum_sensor/interfaces`

[Package guide](README.md) · [Complete source index](../../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [i_vacuum_sensor_service.py](#i_vacuum_sensor_servicepy)
- [i_vacuum_sensor_transport.py](#i_vacuum_sensor_transportpy)

## `__init__.py`

Source: [src/engine/hardware/vacuum_sensor/interfaces/__init__.py](../../../../../src/engine/hardware/vacuum_sensor/interfaces/__init__.py).

No top-level functions, classes or public value declarations; inspect the source for imports or entry-point statements.

## `i_vacuum_sensor_service.py`

Source: [src/engine/hardware/vacuum_sensor/interfaces/i_vacuum_sensor_service.py](../../../../../src/engine/hardware/vacuum_sensor/interfaces/i_vacuum_sensor_service.py).

Imports (including optional/function-local imports; not a startup dependency list): `abc`, `src.engine.core.i_health_checkable`.

### `IVacuumSensorService`

```python
class IVacuumSensorService(IHealthCheckable):
```

High-level vacuum-sensor interface — answers a single question: is vacuum currently detected? Communication-agnostic. Can be implemented over Modbus RTU, discrete I/O, simulated drivers, etc.

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
@abstractmethod
def is_vacuum_detected(self) -> bool
```

Return True when the sensor reports vacuum present. A read failure is treated as "no vacuum" (fail-safe). Implementations should update the health flag reported by is_healthy() on every read.

## `i_vacuum_sensor_transport.py`

Source: [src/engine/hardware/vacuum_sensor/interfaces/i_vacuum_sensor_transport.py](../../../../../src/engine/hardware/vacuum_sensor/interfaces/i_vacuum_sensor_transport.py).

Imports (including optional/function-local imports; not a startup dependency list): `src.engine.hardware.communication.i_register_transport`.

### `IVacuumSensorTransport`

```python
class IVacuumSensorTransport(IRegisterTransport):
```

Semantic type alias — constrains injection sites to vacuum-sensor transports. All register I/O contract is inherited from IRegisterTransport.
