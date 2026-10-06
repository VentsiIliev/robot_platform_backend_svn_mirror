# Module reference: `src/engine/hardware/dryer/models`

[Package guide](README.md) · [Complete source index](../../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [dryer_commands.py](#dryer_commandspy)
- [dryer_config.py](#dryer_configpy)
- [dryer_modbus_registers.py](#dryer_modbus_registerspy)
- [dryer_state.py](#dryer_statepy)
- [dryer_status.py](#dryer_statuspy)
- [dryer_write_data.py](#dryer_write_datapy)

## `__init__.py`

Source: [src/engine/hardware/dryer/models/__init__.py](../../../../../src/engine/hardware/dryer/models/__init__.py).

Imports (including optional/function-local imports; not a startup dependency list): `src.engine.hardware.dryer.models.dryer_commands`, `src.engine.hardware.dryer.models.dryer_config`, `src.engine.hardware.dryer.models.dryer_modbus_registers`, `src.engine.hardware.dryer.models.dryer_state`, `src.engine.hardware.dryer.models.dryer_status`, `src.engine.hardware.dryer.models.dryer_write_data`.

Package-level import/export surface:

```python
from src.engine.hardware.dryer.models.dryer_commands import DEFAULT_DRYER_COMMANDS, DryerCommand, dryer_commands
from src.engine.hardware.dryer.models.dryer_status import DEFAULT_DRYER_STATUSES, DryerStatus, dryer_statuses
from src.engine.hardware.dryer.models.dryer_config import DryerConfig, DryerConfigSerializer
from src.engine.hardware.dryer.models.dryer_state import DryerState
from src.engine.hardware.dryer.models.dryer_write_data import DryerWriteData
from src.engine.hardware.dryer.models.dryer_modbus_registers import DryerDefaults, DryerModbusRegister, DryerRegisterMap
```

Module declarations (expressions are shown without evaluating them):

```python
__all__ = ['DryerCommand', 'DryerStatus', 'DEFAULT_DRYER_COMMANDS', 'DEFAULT_DRYER_STATUSES', 'dryer_commands', 'dryer_statuses', 'DryerConfig', 'DryerConfigSerializer', 'DryerState', 'DryerWriteData', 'DryerDefaults', 'DryerModbusRegister', 'DryerRegisterMap']
```

## `dryer_commands.py`

Source: [src/engine/hardware/dryer/models/dryer_commands.py](../../../../../src/engine/hardware/dryer/models/dryer_commands.py).

Imports (including optional/function-local imports; not a startup dependency list): `enum`, `typing`.

Module declarations (expressions are shown without evaluating them):

```python
DEFAULT_DRYER_COMMANDS: dict[str, int] = {'next_position': int(DryerCommand.NEXT_POSITION), 'eject': int(DryerCommand.EJECT), 'close_plate': int(DryerCommand.CLOSE_PLATE)}
```

### `DryerCommand`

```python
class DryerCommand(IntFlag):
```

Declared fields/defaults:

```python
NEXT_POSITION = 1
EJECT = 2
CLOSE_PLATE = 4
MOVE_SERVOS = EJECT
OPEN_PLATE = CLOSE_PLATE
```

### `dryer_commands`

```python
def dryer_commands(overrides: Mapping[str, int] | None=None) -> dict[str, int]
```

Return firmware command defaults with robot-system overrides applied.

## `dryer_config.py`

Source: [src/engine/hardware/dryer/models/dryer_config.py](../../../../../src/engine/hardware/dryer/models/dryer_config.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `dataclasses`, `src.engine.hardware.dryer.models.dryer_modbus_registers`, `src.engine.repositories.interfaces.settings_serializer`, `typing`.

### `DryerConfig`

```python
@dataclass(frozen=True)
class DryerConfig:
```

Editable values for the current dryer firmware register block.

Declared fields/defaults:

```python
pwm_open_vrytka: int = DryerDefaults.pwm_open_vrytka
pwm_close_vrytka: int = DryerDefaults.pwm_close_vrytka
pwm_open_izbutvatel: int = DryerDefaults.pwm_open_izbutvatel
pwm_close_izbutvatel: int = DryerDefaults.pwm_close_izbutvatel
time_delay_move_servo_up: int = DryerDefaults.time_delay_move_servo_up
time_delay_move_servo_down: int = DryerDefaults.time_delay_move_servo_down
time_delay_move_servo_in: int = DryerDefaults.time_delay_move_servo_in
time_delay_move_servo_out: int = DryerDefaults.time_delay_move_servo_out
time_delay_move_plate_in: int = DryerDefaults.time_delay_move_plate_in
time_delay_move_plate_out: int = DryerDefaults.time_delay_move_plate_out
time_delay_start_servo_move: int = DryerDefaults.time_delay_start_servo_move
rev_minute: int = DryerDefaults.rev_minute
acceleration: float = DryerDefaults.acceleration
target_position_backword: int = DryerDefaults.target_position_backword
target_position_forword: int = DryerDefaults.target_position_forword
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
@classmethod
def from_dict(cls, data: dict[str, Any]) -> 'DryerConfig'
```

```python
def to_dict(self) -> dict[str, Any]
```

### `DryerConfigSerializer`

```python
class DryerConfigSerializer(ISettingsSerializer[DryerConfig]):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
@property
def settings_type(self) -> str
```

```python
def get_default(self) -> DryerConfig
```

```python
def to_dict(self, settings: DryerConfig) -> dict[str, Any]
```

```python
def from_dict(self, data: dict[str, Any]) -> DryerConfig
```

## `dryer_modbus_registers.py`

Source: [src/engine/hardware/dryer/models/dryer_modbus_registers.py](../../../../../src/engine/hardware/dryer/models/dryer_modbus_registers.py).

Imports (including optional/function-local imports; not a startup dependency list): `dataclasses`, `enum`, `typing`.

### `DryerModbusRegister`

```python
class DryerModbusRegister(IntEnum):
```

Declared fields/defaults:

```python
STATUS = 0
COMMAND = 1
PWM_OPEN_VRYTKA = 2
PWM_CLOSE_VRYTKA = 3
PWM_OPEN_IZBUTVATEL = 4
PWM_CLOSE_IZBUTVATEL = 5
TIME_DELAY_MOVE_SERVO_UP = 6
TIME_DELAY_MOVE_SERVO_DOWN = 7
TIME_DELAY_MOVE_SERVO_IN = 8
TIME_DELAY_MOVE_SERVO_OUT = 9
TIME_DELAY_MOVE_PLATE_IN = 10
TIME_DELAY_MOVE_PLATE_OUT = 11
TIME_DELAY_START_SERVO_MOVE = 12
REV_MINUTE = 13
ACCELERATION = 14
TARGET_POSITION_BACKWORD = 15
TARGET_POSITION_FORWORD = 16
```

### `DryerRegisterMap`

```python
@dataclass(frozen=True)
class DryerRegisterMap:
```

Runtime dryer addresses, defaulting to the firmware register map.

Declared fields/defaults:

```python
status: int = DryerModbusRegister.STATUS
command: int = DryerModbusRegister.COMMAND
pwm_open_vrytka: int = DryerModbusRegister.PWM_OPEN_VRYTKA
pwm_close_vrytka: int = DryerModbusRegister.PWM_CLOSE_VRYTKA
pwm_open_izbutvatel: int = DryerModbusRegister.PWM_OPEN_IZBUTVATEL
pwm_close_izbutvatel: int = DryerModbusRegister.PWM_CLOSE_IZBUTVATEL
time_delay_move_servo_up: int = DryerModbusRegister.TIME_DELAY_MOVE_SERVO_UP
time_delay_move_servo_down: int = DryerModbusRegister.TIME_DELAY_MOVE_SERVO_DOWN
time_delay_move_servo_in: int = DryerModbusRegister.TIME_DELAY_MOVE_SERVO_IN
time_delay_move_servo_out: int = DryerModbusRegister.TIME_DELAY_MOVE_SERVO_OUT
time_delay_move_plate_in: int = DryerModbusRegister.TIME_DELAY_MOVE_PLATE_IN
time_delay_move_plate_out: int = DryerModbusRegister.TIME_DELAY_MOVE_PLATE_OUT
time_delay_start_servo_move: int = DryerModbusRegister.TIME_DELAY_START_SERVO_MOVE
rev_minute: int = DryerModbusRegister.REV_MINUTE
acceleration: int = DryerModbusRegister.ACCELERATION
target_position_backword: int = DryerModbusRegister.TARGET_POSITION_BACKWORD
target_position_forword: int = DryerModbusRegister.TARGET_POSITION_FORWORD
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
@classmethod
def from_mapping(cls, addresses: Mapping[str, str | int]) -> 'DryerRegisterMap'
```

```python
@property
def addresses(self) -> tuple[int, ...]
```

```python
def require_contiguous(self) -> None
```

### `DryerDefaults`

```python
@dataclass(frozen=True)
class DryerDefaults:
```

Declared fields/defaults:

```python
status: int = 0
command: int = 0
pwm_open_vrytka: int = 150
pwm_close_vrytka: int = 600
pwm_open_izbutvatel: int = 600
pwm_close_izbutvatel: int = 180
time_delay_move_servo_up: int = 80
time_delay_move_servo_down: int = 50
time_delay_move_servo_in: int = 30
time_delay_move_servo_out: int = 50
time_delay_move_plate_in: int = 520
time_delay_move_plate_out: int = 550
time_delay_start_servo_move: int = 50
rev_minute: int = 50
acceleration: float = 0.1
target_position_backword: int = 500
target_position_forword: int = 500
```

## `dryer_state.py`

Source: [src/engine/hardware/dryer/models/dryer_state.py](../../../../../src/engine/hardware/dryer/models/dryer_state.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `dataclasses`, `src.engine.hardware.dryer.models.dryer_status`, `typing`.

### `DryerState`

```python
@dataclass(frozen=True)
class DryerState:
```

Declared fields/defaults:

```python
raw_status: int = 0
is_ready: bool = False
ejecting: bool = False
eject_done: bool = False
next_position_moving: bool = False
next_position_done: bool = False
is_healthy: bool = False
communication_errors: List[str] = field(default_factory=list)
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
@classmethod
def from_raw_status(cls, raw_status: int, statuses: Mapping[str, int] | None=None) -> 'DryerState'
```

```python
@property
def servos_moving(self) -> bool
```

Compatibility view of either firmware movement status.

```python
@property
def plate_on_position(self) -> bool
```

Compatibility view of the firmware's completed-position status.

```python
@property
def has_errors(self) -> bool
```

## `dryer_status.py`

Source: [src/engine/hardware/dryer/models/dryer_status.py](../../../../../src/engine/hardware/dryer/models/dryer_status.py).

Imports (including optional/function-local imports; not a startup dependency list): `enum`, `typing`.

Module declarations (expressions are shown without evaluating them):

```python
DEFAULT_DRYER_STATUSES: dict[str, int] = {'ready': int(DryerStatus.READY), 'eject': int(DryerStatus.EJECT), 'eject_done': int(DryerStatus.EJECT_DONE), 'next_pos_moving': int(DryerStatus.NEXT_POS_MOVING), 'next_pos_done': int(DryerStatus.NEXT_POS_DONE)}
```

### `DryerStatus`

```python
class DryerStatus(IntFlag):
```

Declared fields/defaults:

```python
READY = 1
EJECT = 8
EJECT_DONE = 16
NEXT_POS_MOVING = 32
NEXT_POS_DONE = 64
```

### `dryer_statuses`

```python
def dryer_statuses(overrides: Mapping[str, int] | None=None) -> dict[str, int]
```

Return firmware status defaults with robot-system overrides applied.

## `dryer_write_data.py`

Source: [src/engine/hardware/dryer/models/dryer_write_data.py](../../../../../src/engine/hardware/dryer/models/dryer_write_data.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `dataclasses`, `src.engine.hardware.dryer.models.dryer_commands`, `src.engine.hardware.dryer.models.dryer_config`, `src.engine.hardware.dryer.models.dryer_modbus_registers`.

### `DryerWriteData`

```python
@dataclass(frozen=True)
class DryerWriteData:
```

Declared fields/defaults:

```python
status: int = DryerDefaults.status
command: int | DryerCommand = DryerDefaults.command
pwm_open_vrytka: int = DryerDefaults.pwm_open_vrytka
pwm_close_vrytka: int = DryerDefaults.pwm_close_vrytka
pwm_open_izbutvatel: int = DryerDefaults.pwm_open_izbutvatel
pwm_close_izbutvatel: int = DryerDefaults.pwm_close_izbutvatel
time_delay_move_servo_up: int = DryerDefaults.time_delay_move_servo_up
time_delay_move_servo_down: int = DryerDefaults.time_delay_move_servo_down
time_delay_move_servo_in: int = DryerDefaults.time_delay_move_servo_in
time_delay_move_servo_out: int = DryerDefaults.time_delay_move_servo_out
time_delay_move_plate_in: int = DryerDefaults.time_delay_move_plate_in
time_delay_move_plate_out: int = DryerDefaults.time_delay_move_plate_out
time_delay_start_servo_move: int = DryerDefaults.time_delay_start_servo_move
rev_minute: int = DryerDefaults.rev_minute
acceleration: float = DryerDefaults.acceleration
target_position_backword: int = DryerDefaults.target_position_backword
target_position_forword: int = DryerDefaults.target_position_forword
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
@classmethod
def from_config(cls, config: DryerConfig, command: int | DryerCommand=0) -> 'DryerWriteData'
```

```python
def to_register_values(self) -> list[int]
```
