# Module reference: `src/engine/hardware/motor/health`

[Package guide](README.md) · [Complete source index](../../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [motor_health_checker.py](#motor_health_checkerpy)

## `__init__.py`

Source: [src/engine/hardware/motor/health/__init__.py](../../../../../src/engine/hardware/motor/health/__init__.py).

No top-level functions, classes or public value declarations; inspect the source for imports or entry-point statements.

## `motor_health_checker.py`

Source: [src/engine/hardware/motor/health/motor_health_checker.py](../../../../../src/engine/hardware/motor/health/motor_health_checker.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `logging`, `src.engine.hardware.motor.interfaces.i_motor_error_decoder`, `src.engine.hardware.motor.interfaces.i_motor_transport`, `src.engine.hardware.motor.models.motor_config`, `src.engine.hardware.motor.models.motor_state`, `time`, `typing`.

### `_NullErrorDecoder`

```python
class _NullErrorDecoder(IMotorErrorDecoder):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def decode(self, error_code: int) -> str
```

### `MotorHealthChecker`

```python
class MotorHealthChecker:
```

Performs health check cycles against a motor controller board. Depends only on IMotorTransport and IMotorErrorDecoder — knows nothing about Modbus, serial ports, or board-specific error codes.

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, transport: IMotorTransport, config: MotorConfig, error_decoder: Optional[IMotorErrorDecoder]=None) -> None
```

```python
def check_motor(self, motor_address: int) -> MotorState
```

```python
def check_all_motors(self, motor_addresses: List[int]) -> MotorsSnapshot
```
