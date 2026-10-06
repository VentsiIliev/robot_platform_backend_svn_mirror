# Module reference: `src/robot_systems/glue/settings`

[Package guide](README.md) · [Complete source index](../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [cells.py](#cellspy)
- [device_control.py](#device_controlpy)
- [dispense_channels.py](#dispense_channelspy)
- [glue.py](#gluepy)
- [glue_types.py](#glue_typespy)

## `cells.py`

Source: [src/robot_systems/glue/settings/cells.py](../../../../src/robot_systems/glue/settings/cells.py).

Imports (including optional/function-local imports; not a startup dependency list): `src.engine.hardware.weight.config`, `src.shared_contracts.declarations`.

### `_default_cell`

```python
def _default_cell(cell_id: int, url: str, motor_address: int=0, glue_type: str='') -> CellConfig
```

### `_default_url`

```python
def _default_url(cell_id: int) -> str
```

### `GlueCellsConfigSerializer`

```python
class GlueCellsConfigSerializer(CellsConfigSerializer):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, default_channels: list[DispenseChannelDefinition] | None=None) -> None
```

```python
@property
def settings_type(self) -> str
```

```python
def get_default(self) -> GlueCellsConfig
```

## `device_control.py`

Source: [src/robot_systems/glue/settings/device_control.py](../../../../src/robot_systems/glue/settings/device_control.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `dataclasses`, `src.engine.repositories.interfaces.settings_serializer`, `src.shared_contracts.declarations`, `typing`.

Module declarations (expressions are shown without evaluating them):

```python
DeviceControlConfig = GlueMotorConfig
DeviceControlConfigSerializer = GlueMotorConfigSerializer
```

### `MotorSpec`

```python
@dataclass
class MotorSpec:
```

Declared fields/defaults:

```python
name: str
address: int
error_prefix: int = 0
```

### `GlueMotorConfig`

```python
@dataclass
class GlueMotorConfig:
```

Declared fields/defaults:

```python
motors: List[MotorSpec] = field(default_factory=lambda: [MotorSpec(**m) for m in _DEFAULT_MOTORS])
health_check_trigger_register: int = _DEFAULT_BOARD['health_check_trigger_register']
motor_error_count_register: int = _DEFAULT_BOARD['motor_error_count_register']
motor_error_registers_start: int = _DEFAULT_BOARD['motor_error_registers_start']
health_check_delay_s: float = _DEFAULT_BOARD['health_check_delay_s']
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def get_addresses(self) -> List[int]
```

```python
def get_address_to_error_prefix(self) -> Dict[int, int]
```

### `GlueMotorConfigSerializer`

```python
class GlueMotorConfigSerializer(ISettingsSerializer[GlueMotorConfig]):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, default_channels: list[DispenseChannelDefinition] | None=None) -> None
```

```python
@property
def settings_type(self) -> str
```

```python
def get_default(self) -> GlueMotorConfig
```

```python
def to_dict(self, settings: GlueMotorConfig) -> Dict[str, Any]
```

```python
def from_dict(self, data: Dict[str, Any]) -> GlueMotorConfig
```

## `dispense_channels.py`

Source: [src/robot_systems/glue/settings/dispense_channels.py](../../../../src/robot_systems/glue/settings/dispense_channels.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `dataclasses`, `src.engine.repositories.interfaces.settings_serializer`, `src.shared_contracts.declarations`, `typing`.

### `DispenseChannelConfig`

```python
@dataclass(frozen=True)
class DispenseChannelConfig:
```

Declared fields/defaults:

```python
channel_id: str
glue_type: str = ''
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
@classmethod
def from_dict(cls, data: Dict[str, Any]) -> 'DispenseChannelConfig'
```

```python
def to_dict(self) -> Dict[str, Any]
```

### `DispenseChannelSettings`

```python
@dataclass(frozen=True)
class DispenseChannelSettings:
```

Declared fields/defaults:

```python
channels: List[DispenseChannelConfig] = field(default_factory=list)
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def get_channel(self, channel_id: str) -> DispenseChannelConfig | None
```

### `DispenseChannelSettingsSerializer`

```python
class DispenseChannelSettingsSerializer(ISettingsSerializer[DispenseChannelSettings]):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, default_channels: Sequence[DispenseChannelDefinition] | None=None) -> None
```

```python
@property
def settings_type(self) -> str
```

```python
def get_default(self) -> DispenseChannelSettings
```

```python
def to_dict(self, settings: DispenseChannelSettings) -> Dict[str, Any]
```

```python
def from_dict(self, data: Dict[str, Any]) -> DispenseChannelSettings
```

## `glue.py`

Source: [src/robot_systems/glue/settings/glue.py](../../../../src/robot_systems/glue/settings/glue.py).

Imports (including optional/function-local imports; not a startup dependency list): `dataclasses`, `enum`, `json`, `src.engine.repositories.interfaces.settings_serializer`, `typing`.

### `GlueSettingKey`

```python
class GlueSettingKey(Enum):
```

Declared fields/defaults:

```python
SPRAY_WIDTH = 'spray_width'
SPRAYING_HEIGHT = 'spraying_height'
FAN_SPEED = 'fan_speed'
TIME_BETWEEN_GENERATOR_AND_GLUE = 'time_between_generator_and_glue'
MOTOR_SPEED = 'motor_speed'
REVERSE_DURATION = 'reverse_duration'
SPEED_REVERSE = 'speed_reverse'
RZ_ANGLE = 'rz_angle'
GLUE_TYPE = 'glue_type'
GENERATOR_TIMEOUT = 'generator_timeout'
TIME_BEFORE_MOTION = 'time_before_motion'
TIME_BEFORE_STOP = 'time_before_stop'
REACH_START_THRESHOLD = 'reach_start_threshold'
REACH_END_THRESHOLD = 'reach_end_threshold'
INITIAL_RAMP_SPEED = 'initial_ramp_speed'
FORWARD_RAMP_STEPS = 'forward_ramp_steps'
REVERSE_RAMP_STEPS = 'reverse_ramp_steps'
INITIAL_RAMP_SPEED_DURATION = 'initial_ramp_speed_duration'
SPRAY_ON = 'spray_on'
```

### `GlueSettings`

```python
@dataclass
class GlueSettings:
```

Declared fields/defaults:

```python
spray_width: int = 5
spraying_height: int = 10
fan_speed: int = 50
time_between_generator_and_glue: float = 1.0
motor_speed: int = 10000
reverse_duration: float = 1.0
speed_reverse: int = 1000
rz_angle: float = 0.0
glue_type: str = 'Type A'
generator_timeout: float = 5.0
time_before_motion: float = 1.0
time_before_stop: float = 1.0
reach_start_threshold: float = 1.0
reach_end_threshold: float = 1.0
initial_ramp_speed: int = 5000
forward_ramp_steps: int = 1
reverse_ramp_steps: int = 1
initial_ramp_speed_duration: float = 1.0
spray_on: bool = True
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
@classmethod
def from_dict(cls, data: Dict[str, Any]) -> 'GlueSettings'
```

```python
def to_dict(self) -> Dict[str, Any]
```

### `GlueSettingsSerializer`

```python
class GlueSettingsSerializer(ISettingsSerializer[GlueSettings]):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
@property
def settings_type(self) -> str
```

```python
def get_default(self) -> GlueSettings
```

```python
def to_dict(self, settings: GlueSettings) -> Dict[str, Any]
```

```python
def from_dict(self, data: Dict[str, Any]) -> GlueSettings
```

## `glue_types.py`

Source: [src/robot_systems/glue/settings/glue_types.py](../../../../src/robot_systems/glue/settings/glue_types.py).

Imports (including optional/function-local imports; not a startup dependency list): `dataclasses`, `src.engine.repositories.interfaces.settings_serializer`, `typing`, `uuid`.

### `Glue`

```python
@dataclass
class Glue:
```

Declared fields/defaults:

```python
name: str
description: str = ''
id: str = field(default_factory=lambda: str(uuid.uuid4()))
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
@classmethod
def from_dict(cls, data: Dict[str, Any]) -> 'Glue'
```

```python
def __init__(self, name: str, description: str='', glue_id: str=None)
```

```python
def to_dict(self) -> Dict[str, Any]
```

### `GlueCatalog`

```python
@dataclass
class GlueCatalog:
```

Declared fields/defaults:

```python
glue_types: List[Glue] = field(default_factory=list)
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def get_by_id(self, glue_id: str) -> Optional[Glue]
```

```python
def get_by_name(self, name: str) -> Optional[Glue]
```

```python
def get_all_names(self) -> List[str]
```

```python
def get_all_ids(self) -> List[str]
```

```python
def add(self, glue: Glue) -> None
```

```python
def remove_by_id(self, glue_id: str) -> bool
```

```python
@property
def count(self) -> int
```

```python
@classmethod
def from_dict(cls, data: Dict[str, Any]) -> 'GlueCatalog'
```

```python
def to_dict(self) -> Dict[str, Any]
```

### `GlueCatalogSerializer`

```python
class GlueCatalogSerializer(ISettingsSerializer[GlueCatalog]):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
@property
def settings_type(self) -> str
```

```python
def get_default(self) -> GlueCatalog
```

```python
def to_dict(self, settings: GlueCatalog) -> Dict[str, Any]
```

```python
def from_dict(self, data: Dict[str, Any]) -> GlueCatalog
```
