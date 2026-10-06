# Module reference: `src/robot_systems/glue/motor`

[Package guide](README.md) · [Complete source index](../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [glue_motor_error_codes.py](#glue_motor_error_codespy)
- [glue_motor_error_decoder.py](#glue_motor_error_decoderpy)

## `__init__.py`

Source: [src/robot_systems/glue/motor/__init__.py](../../../../src/robot_systems/glue/motor/__init__.py).

No top-level functions, classes or public value declarations; inspect the source for imports or entry-point statements.

## `glue_motor_error_codes.py`

Source: [src/robot_systems/glue/motor/glue_motor_error_codes.py](../../../../src/robot_systems/glue/motor/glue_motor_error_codes.py).

Imports (including optional/function-local imports; not a startup dependency list): `enum`.

### `GlueMotorErrorCode`

```python
class GlueMotorErrorCode(Enum):
```

Error codes reported by the Modbus motor controller board used in the glue robot vision_service. Specific to this board's firmware — do not use in generic motor logic.

Declared fields/defaults:

```python
MOTOR_1_MISSING = 11
MOTOR_2_MISSING = 21
MOTOR_3_MISSING = 31
MOTOR_4_MISSING = 41
MOTOR_1_SHORT = 12
MOTOR_2_SHORT = 22
MOTOR_3_SHORT = 32
MOTOR_4_SHORT = 42
MOTOR_1_DRIVER_OVERHEAT = 13
MOTOR_2_DRIVER_OVERHEAT = 23
MOTOR_3_DRIVER_OVERHEAT = 33
MOTOR_4_DRIVER_OVERHEAT = 43
MOTOR_1_DRIVER_COMMUNICATION = 14
MOTOR_2_DRIVER_COMMUNICATION = 24
MOTOR_3_DRIVER_COMMUNICATION = 34
MOTOR_4_DRIVER_COMMUNICATION = 44
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def description(self) -> str
```

```python
@classmethod
def from_code(cls, code: int) -> 'GlueMotorErrorCode | None'
```

## `glue_motor_error_decoder.py`

Source: [src/robot_systems/glue/motor/glue_motor_error_decoder.py](../../../../src/robot_systems/glue/motor/glue_motor_error_decoder.py).

Imports (including optional/function-local imports; not a startup dependency list): `src.engine.hardware.motor.interfaces.i_motor_error_decoder`, `src.robot_systems.glue.motor.glue_motor_error_codes`.

### `GlueMotorErrorDecoder`

```python
class GlueMotorErrorDecoder(IMotorErrorDecoder):
```

IMotorErrorDecoder for the Modbus motor controller board used in the glue robot vision_service. Inject into build_modbus_motor_controller() when wiring the glue vision_service's motor controller.

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def decode(self, error_code: int) -> str
```
