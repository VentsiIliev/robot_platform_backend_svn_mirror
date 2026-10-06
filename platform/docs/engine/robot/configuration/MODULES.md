# Module reference: `src/engine/robot/configuration`

[Package guide](README.md) · [Complete source index](../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [movement_group_settings.py](#movement_group_settingspy)
- [robot_calibration_settings.py](#robot_calibration_settingspy)
- [robot_settings.py](#robot_settingspy)
- [tool_changer_settings.py](#tool_changer_settingspy)

## `__init__.py`

Source: [src/engine/robot/configuration/__init__.py](../../../../src/engine/robot/configuration/__init__.py).

Imports (including optional/function-local imports; not a startup dependency list): `.movement_group_settings`, `.robot_calibration_settings`, `.robot_settings`, `.tool_changer_settings`.

Package-level import/export surface:

```python
from .robot_settings import SafetyLimits, OffsetDirectionMap, MovementGroup, GlobalMotionSettings, RobotSettings, RobotSettingsSerializer
from .movement_group_settings import MovementGroupSettings, MovementGroupSettingsSerializer
from .robot_calibration_settings import AdaptiveMovementConfig, AxisMappingConfig, CameraTcpOffsetCalibrationConfig, RobotCalibrationSettings, RobotCalibrationSettingsSerializer
from .tool_changer_settings import ToolChangerSettings, ToolChangerSettingsSerializer
```

Module declarations (expressions are shown without evaluating them):

```python
__all__ = ['SafetyLimits', 'OffsetDirectionMap', 'MovementGroup', 'GlobalMotionSettings', 'RobotSettings', 'RobotSettingsSerializer', 'MovementGroupSettings', 'MovementGroupSettingsSerializer', 'AdaptiveMovementConfig', 'AxisMappingConfig', 'CameraTcpOffsetCalibrationConfig', 'RobotCalibrationSettings', 'RobotCalibrationSettingsSerializer', 'ToolChangerSettings', 'ToolChangerSettingsSerializer']
```

## `movement_group_settings.py`

Source: [src/engine/robot/configuration/movement_group_settings.py](../../../../src/engine/robot/configuration/movement_group_settings.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `dataclasses`, `src.engine.repositories.interfaces.settings_serializer`, `src.engine.robot.configuration.robot_settings`, `typing`.

### `MovementGroupSettings`

```python
@dataclass
class MovementGroupSettings:
```

Declared fields/defaults:

```python
movement_groups: Dict[str, MovementGroup] = field(default_factory=dict)
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
@classmethod
def from_dict(cls, data: Dict[str, Any]) -> 'MovementGroupSettings'
```

```python
def to_dict(self) -> Dict[str, Any]
```

### `MovementGroupSettingsSerializer`

```python
class MovementGroupSettingsSerializer(ISettingsSerializer[MovementGroupSettings]):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
@property
def settings_type(self) -> str
```

```python
def get_default(self) -> MovementGroupSettings
```

```python
def to_dict(self, settings: MovementGroupSettings) -> Dict[str, Any]
```

```python
def from_dict(self, data: Dict[str, Any]) -> MovementGroupSettings
```

## `robot_calibration_settings.py`

Source: [src/engine/robot/configuration/robot_calibration_settings.py](../../../../src/engine/robot/configuration/robot_calibration_settings.py).

Imports (including optional/function-local imports; not a startup dependency list): `dataclasses`, `src.engine.repositories.interfaces.settings_serializer`, `typing`.

### `AdaptiveMovementConfig`

```python
@dataclass
class AdaptiveMovementConfig:
```

Declared fields/defaults:

```python
min_step_mm: float = 0.1
max_step_mm: float = 25.0
target_error_mm: float = 0.25
max_error_ref: float = 100.0
k: float = 2.0
derivative_scaling: float = 0.5
iterative_gain: float = 0.7
near_target_gain: float = 0.35
axis_deadband_mm: float = 0.2
axis_flip_scale_min: float = 0.2
fast_iteration_wait: float = 1.0
initial_align_y_scale: float = 1.0
initial_align_approach_z: float | None = None
post_align_settle_s: float = 0.3
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
@classmethod
def from_dict(cls, data: Dict) -> 'AdaptiveMovementConfig'
```

```python
def to_dict(self) -> Dict
```

### `AxisMappingConfig`

```python
@dataclass
class AxisMappingConfig:
```

Declared fields/defaults:

```python
marker_id: int = 4
move_mm: float = 100.0
max_attempts: int = 100
delay_after_move_s: float = 1.0
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
@classmethod
def from_dict(cls, data: Dict) -> 'AxisMappingConfig'
```

```python
def to_dict(self) -> Dict
```

### `CameraTcpOffsetCalibrationConfig`

```python
@dataclass
class CameraTcpOffsetCalibrationConfig:
```

Declared fields/defaults:

```python
run_during_robot_calibration: bool = False
max_markers_for_tcp_capture: int = 2
marker_id: int = 4
rotation_step_deg: float = 15.0
iterations: int = 4
approach_z: float = 300.0
approach_rx: float = 180.0
approach_ry: float = 0.0
approach_rz: float = 0.0
velocity: int = 20
acceleration: int = 10
settle_time_s: float = 0.5
detection_attempts: int = 20
retry_delay_s: float = 0.1
recenter_max_iterations: int = 20
recenter_max_step_mm: float = 15.0
recenter_correction_gain: float = 0.6
recenter_stability_wait_s: float = 0.4
recenter_alignment_threshold_mm: float = 0.5
min_samples: int = 3
max_acceptance_std_mm: float = 10.0
verification_enabled: bool = True
verification_samples: int = 3
verification_max_error_mm: float = 5.0
verification_confirmation_tolerance_mm: float = 0.75
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
@classmethod
def from_dict(cls, data: Dict) -> 'CameraTcpOffsetCalibrationConfig'
```

```python
def to_dict(self) -> Dict
```

### `RobotCalibrationSettings`

```python
@dataclass
class RobotCalibrationSettings:
```

Declared fields/defaults:

```python
adaptive_movement: AdaptiveMovementConfig = field(default_factory=AdaptiveMovementConfig)
axis_mapping: AxisMappingConfig = field(default_factory=AxisMappingConfig)
camera_tcp_offset: CameraTcpOffsetCalibrationConfig = field(default_factory=CameraTcpOffsetCalibrationConfig)
run_height_measurement: bool = True
z_target: int = 300
required_ids: List[int] = field(default_factory=lambda: [0, 1, 2, 3, 4, 5, 6, 8])
candidate_ids: List[int] = field(default_factory=list)
min_target_separation_px: float = 120.0
homography_target_count: int = 16
residual_target_count: int = 14
validation_target_count: int = 6
test_target_count: int = 10
auto_skip_known_unreachable_markers: bool = True
unreachable_marker_failure_threshold: int = 1
known_unreachable_marker_ids: List[int] = field(default_factory=list)
unreachable_marker_failure_counts: Dict[int, int] = field(default_factory=dict)
velocity: int = 30
acceleration: int = 10
travel_velocity: int = 30
travel_acceleration: int = 10
iterative_velocity: int = 30
iterative_acceleration: int = 10
initial_ppm: float | None = None
workobject_calibrations: Dict[str, Dict[str, Any]] = field(default_factory=dict)
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
@classmethod
def from_dict(cls, data: Dict) -> 'RobotCalibrationSettings'
```

```python
def to_dict(self) -> Dict
```

### `RobotCalibrationSettingsSerializer`

```python
class RobotCalibrationSettingsSerializer(ISettingsSerializer[RobotCalibrationSettings]):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
@property
def settings_type(self) -> str
```

```python
def get_default(self) -> RobotCalibrationSettings
```

```python
def to_dict(self, settings: RobotCalibrationSettings) -> Dict[str, Any]
```

```python
def from_dict(self, data: Dict[str, Any]) -> RobotCalibrationSettings
```

## `robot_settings.py`

Source: [src/engine/robot/configuration/robot_settings.py](../../../../src/engine/robot/configuration/robot_settings.py).

Imports (including optional/function-local imports; not a startup dependency list): `dataclasses`, `json`, `src.engine.repositories.interfaces.settings_serializer`, `typing`.

### `SafetyLimits`

```python
@dataclass
class SafetyLimits:
```

Declared fields/defaults:

```python
x_min: int = -500
x_max: int = 500
y_min: int = -500
y_max: int = 500
z_min: int = 100
z_max: int = 800
rx_min: int = 170
rx_max: int = 190
ry_min: int = -10
ry_max: int = 10
rz_min: int = -180
rz_max: int = 180
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
@classmethod
def from_dict(cls, data: Dict) -> 'SafetyLimits'
```

```python
def to_dict(self) -> Dict
```

### `OffsetDirectionMap`

```python
@dataclass
class OffsetDirectionMap:
```

Declared fields/defaults:

```python
pos_x: bool = True
neg_x: bool = True
pos_y: bool = True
neg_y: bool = True
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
@classmethod
def from_dict(cls, data: dict) -> 'OffsetDirectionMap'
```

```python
def to_dict(self) -> dict
```

### `MovementGroup`

```python
@dataclass
class MovementGroup:
```

Declared fields/defaults:

```python
velocity: int = 0
acceleration: int = 0
motion_type: str = 'ptp'
position: Optional[str] = None
points: List[str] = field(default_factory=list)
iterations: int = 1
has_iterations: bool = False
has_trajectory_execution: bool = False
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
@classmethod
def from_dict(cls, data: Dict) -> 'MovementGroup'
```

```python
def parse_position(self) -> Optional[List[float]]
```

```python
def parse_points(self) -> List[List[float]]
```

```python
def to_dict(self) -> Dict
```

### `GlobalMotionSettings`

```python
@dataclass
class GlobalMotionSettings:
```

Declared fields/defaults:

```python
global_velocity: int = 100
global_acceleration: int = 100
emergency_decel: int = 500
max_jog_step: int = 50
recovery_servo_linear_mm_s: float = 25.0
recovery_servo_angular_deg_s: float = 5.0
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
@classmethod
def from_dict(cls, data: Dict) -> 'GlobalMotionSettings'
```

```python
def to_dict(self) -> Dict
```

### `RobotSettings`

```python
@dataclass
class RobotSettings:
```

Declared fields/defaults:

```python
robot_ip: str = '192.168.58.2'
robot_tool: int = 0
robot_user: int = 0
use_automatic_camera_to_tcp_offset: bool = True
camera_to_tcp_x_offset: float = 0.0
camera_to_tcp_y_offset: float = 0.0
camera_to_tcp_rotation_residuals: List[Dict[str, float]] = field(default_factory=list)
camera_to_tcp_mode: str = 'global'
camera_to_tcp_by_area: Dict[str, Dict] = field(default_factory=dict)
camera_z_shift_x_per_mm_px: float = 0.0
camera_z_shift_y_per_mm_px: float = 0.0
camera_z_shift_x_per_mm: float = 0.0
camera_z_shift_y_per_mm: float = 0.0
tcp_x_step_distance: float = 50.0
tcp_x_step_offset: float = 0.1
tcp_y_step_distance: float = 50.0
tcp_y_step_offset: float = 0.1
offset_direction_map: OffsetDirectionMap = field(default_factory=OffsetDirectionMap)
movement_groups: Dict[str, MovementGroup] = field(default_factory=dict)
safety_limits: SafetyLimits = field(default_factory=SafetyLimits)
global_motion_settings: GlobalMotionSettings = field(default_factory=GlobalMotionSettings)
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def camera_to_tcp_for_area(self, area_id: str='') -> tuple[float, float, list[dict]]
```

```python
def save_camera_to_tcp_for_area(self, area_id: str, x_mm: float, y_mm: float, residuals: list[dict]) -> None
```

```python
@classmethod
def from_dict(cls, data: Dict) -> 'RobotSettings'
```

```python
def to_dict(self) -> Dict
```

### `RobotSettingsSerializer`

```python
class RobotSettingsSerializer(ISettingsSerializer[RobotSettings]):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
@property
def settings_type(self) -> str
```

```python
def get_default(self) -> RobotSettings
```

```python
def to_dict(self, settings: RobotSettings) -> Dict[str, Any]
```

```python
def from_dict(self, data: Dict[str, Any]) -> RobotSettings
```

## `tool_changer_settings.py`

Source: [src/engine/robot/configuration/tool_changer_settings.py](../../../../src/engine/robot/configuration/tool_changer_settings.py).

Imports (including optional/function-local imports; not a startup dependency list): `dataclasses`, `src.engine.repositories.interfaces`, `src.engine.robot.interfaces.tool_definition`, `src.engine.robot.tool_changer`, `src.shared_contracts.declarations.tooling`, `typing`.

### `ToolChangerSettings`

```python
@dataclass
class ToolChangerSettings:
```

Declared fields/defaults:

```python
tools: List[ToolDefinition] = field(default_factory=list)
slots: List[SlotConfig] = field(default_factory=list)
reference_tool_id: int = 1
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def get_tool_names(self) -> List[str]
```

```python
def get_tool_options(self) -> List[ToolDefinition]
```

### `ToolChangerSettingsSerializer`

```python
class ToolChangerSettingsSerializer(ISettingsSerializer):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, default_tools: Sequence[ToolDefinitionDeclaration] | None=None, default_slots: Sequence[ToolSlotDefinition] | None=None) -> None
```

```python
@property
def settings_type(self) -> str
```

```python
def get_default(self) -> ToolChangerSettings
```

```python
def to_dict(self, settings: ToolChangerSettings) -> dict
```

```python
def from_dict(self, data: dict) -> ToolChangerSettings
```
