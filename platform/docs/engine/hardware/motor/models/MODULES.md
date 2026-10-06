# Module reference: `src/engine/hardware/motor/models`

[Package guide](README.md) · [Complete source index](../../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [motor_config.py](#motor_configpy)
- [motor_state.py](#motor_statepy)

## `__init__.py`

Source: [src/engine/hardware/motor/models/__init__.py](../../../../../src/engine/hardware/motor/models/__init__.py).

No top-level functions, classes or public value declarations; inspect the source for imports or entry-point statements.

## `motor_config.py`

Source: [src/engine/hardware/motor/models/motor_config.py](../../../../../src/engine/hardware/motor/models/motor_config.py).

Imports (including optional/function-local imports; not a startup dependency list): `dataclasses`, `typing`.

### `MotorConfig`

```python
@dataclass
class MotorConfig:
```

Register map, motor topology, and timing constants for a motor controller board. All register addresses are board firmware specific — no defaults are provided. Instantiate with explicit values in the robot vision_service that owns the hardware. motor_addresses — ordered list of Modbus register addresses for each motor. Length determines the motor count (1, 4, 44, …). address_to_error_prefix — optional mapping: motor_address → error-code prefix digit, used to filter board-level error codes per motor. Leave empty ({}) if the board does not use prefixed error codes.

Declared fields/defaults:

```python
health_check_trigger_register: int
motor_error_count_register: int
motor_error_registers_start: int
motor_addresses: List[int]
health_check_delay_s: float = 0.1
ramp_step_delay_s: float = 0.001
address_to_error_prefix: Dict[int, int] = field(default_factory=dict)
```

## `motor_state.py`

Source: [src/engine/hardware/motor/models/motor_state.py](../../../../../src/engine/hardware/motor/models/motor_state.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `dataclasses`, `typing`.

### `MotorState`

```python
@dataclass
class MotorState:
```

Declared fields/defaults:

```python
motor_address: int
is_healthy: bool = False
error_codes: List[int] = field(default_factory=list)
communication_errors: List[str] = field(default_factory=list)
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
@property
def has_errors(self) -> bool
```

```python
def describe_errors(self) -> List[str]
```

Returns raw error codes as strings — decoder is in the transport layer.

### `MotorsSnapshot`

```python
@dataclass
class MotorsSnapshot:
```

Declared fields/defaults:

```python
success: bool
motors: Dict[int, MotorState] = field(default_factory=dict)
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def get_motor(self, address: int) -> Optional[MotorState]
```

```python
def add(self, state: MotorState) -> None
```

```python
def all_healthy(self) -> bool
```

```python
def get_all_errors_sorted(self) -> List[Tuple[int, int]]
```
