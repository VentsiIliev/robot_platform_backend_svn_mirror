# Module reference: `src/engine/hardware/motor/modbus`

[Package guide](README.md) · [Complete source index](../../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [modbus_motor_factory.py](#modbus_motor_factorypy)
- [modbus_motor_transport.py](#modbus_motor_transportpy)

## `__init__.py`

Source: [src/engine/hardware/motor/modbus/__init__.py](../../../../../src/engine/hardware/motor/modbus/__init__.py).

No top-level functions, classes or public value declarations; inspect the source for imports or entry-point statements.

## `modbus_motor_factory.py`

Source: [src/engine/hardware/motor/modbus/modbus_motor_factory.py](../../../../../src/engine/hardware/motor/modbus/modbus_motor_factory.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `src.engine.hardware.communication.modbus.modbus`, `src.engine.hardware.motor.interfaces.i_motor_error_decoder`, `src.engine.hardware.motor.interfaces.i_motor_service`, `src.engine.hardware.motor.modbus.modbus_motor_transport`, `src.engine.hardware.motor.models.motor_config`, `src.engine.hardware.motor.motor_service`, `typing`.

### `build_modbus_motor_service`

```python
def build_modbus_motor_service(modbus_config: ModbusConfig, motor_config: MotorConfig, error_decoder: Optional[IMotorErrorDecoder]=None) -> IMotorService
```

Build a MotorService wired to Modbus RTU. motor_config — required: register map and motor topology for this board. Instantiate MotorConfig explicitly in the robot vision_service that owns the hardware — no generic defaults exist. error_decoder — inject a vision_service-specific IMotorErrorDecoder to translate board firmware error codes into human-readable descriptions. If omitted, raw integer codes are logged with a warning.

## `modbus_motor_transport.py`

Source: [src/engine/hardware/motor/modbus/modbus_motor_transport.py](../../../../../src/engine/hardware/motor/modbus/modbus_motor_transport.py).

Imports (including optional/function-local imports; not a startup dependency list): `src.engine.hardware.communication.modbus.modbus_register_transport`, `src.engine.hardware.motor.interfaces.i_motor_transport`.

### `ModbusMotorTransport`

```python
class ModbusMotorTransport(ModbusRegisterTransport, IMotorTransport):
```

Modbus RTU transport for motor controller boards.
