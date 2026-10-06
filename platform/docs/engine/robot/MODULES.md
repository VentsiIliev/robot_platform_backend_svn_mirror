# Module reference: `src/engine/robot`

[Package guide](README.md) · [Complete source index](../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [base_robot.py](#base_robotpy)
- [base_robot_service.py](#base_robot_servicepy)
- [motion_sequence.py](#motion_sequencepy)
- [plane_pose_mapper.py](#plane_pose_mapperpy)
- [relative_tool_calibration_service.py](#relative_tool_calibration_servicepy)
- [tool_activation_service.py](#tool_activation_servicepy)
- [tool_changer.py](#tool_changerpy)
- [tool_manager.py](#tool_managerpy)
- [tool_transform.py](#tool_transformpy)

## `__init__.py`

Source: [src/engine/robot/__init__.py](../../../src/engine/robot/__init__.py).

No top-level functions, classes or public value declarations; inspect the source for imports or entry-point statements.

## `base_robot.py`

Source: [src/engine/robot/base_robot.py](../../../src/engine/robot/base_robot.py).

No top-level functions, classes or public value declarations; inspect the source for imports or entry-point statements.

## `base_robot_service.py`

Source: [src/engine/robot/base_robot_service.py](../../../src/engine/robot/base_robot_service.py).

Imports (including optional/function-local imports; not a startup dependency list): `.services.robot_service`.

Module declarations (expressions are shown without evaluating them):

```python
__all__ = ['RobotService']
```

## `motion_sequence.py`

Source: [src/engine/robot/motion_sequence.py](../../../src/engine/robot/motion_sequence.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `dataclasses`, `enum`, `math`, `typing`.

Module declarations (expressions are shown without evaluating them):

```python
MotionType = Literal['linear', 'ptp']
OrderedMotionCommand: TypeAlias = OrderedPositionCommand | OrderedPathCommand | OrderedUnwindJoint6Command
OrderedMotionInput: TypeAlias = OrderedMotionCommand
```

### `OrderedMotionType`

```python
class OrderedMotionType(StrEnum):
```

Supported motion algorithms for a single-position ordered command.

Declared fields/defaults:

```python
PTP = 'ptp'
LINEAR = 'linear'
FAST_LINEAR = 'fast_lin'
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
@classmethod
def parse(cls, value: object, *, field_name: str='motion_type') -> 'OrderedMotionType'
```

Validate an external motion-type value at a configuration boundary.

### `OrderedExecutionPolicy`

```python
class OrderedExecutionPolicy(StrEnum):
```

How adjacent ordered commands are combined by the motion backend.

Declared fields/defaults:

```python
CONCATENATE = 'concatenate'
```

### `OrderedMotionLimitProfile`

```python
class OrderedMotionLimitProfile(StrEnum):
```

Named backend limit profiles supported by ordered motion.

Declared fields/defaults:

```python
PAINT_CONTACT = 'paint_contact'
```

### `OrderedMotionProfile`

```python
@dataclass(frozen=True)
class OrderedMotionProfile:
```

Velocity, acceleration, and blending for an ordered motion command.

Declared fields/defaults:

```python
velocity_percent: float
acceleration_percent: float
blend_radius: float | None = None
```

### `OrderedMotionMetadata`

```python
@dataclass(frozen=True)
class OrderedMotionMetadata:
```

Optional scheduling and interruption metadata for an ordered command.

Declared fields/defaults:

```python
protected: bool = False
readiness_group: str | None = None
execution_group: str | None = None
execution_policy: OrderedExecutionPolicy | None = None
```

### `OrderedPositionCommand`

```python
@dataclass(frozen=True)
class OrderedPositionCommand:
```

One typed ordered move to a six-axis robot pose.

Declared fields/defaults:

```python
label: str
motion_type: OrderedMotionType
position: tuple[float, ...]
profile: OrderedMotionProfile
metadata: OrderedMotionMetadata = OrderedMotionMetadata()
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def to_payload(self) -> dict[str, object]
```

### `OrderedPathCommand`

```python
@dataclass(frozen=True)
class OrderedPathCommand:
```

One typed ordered Cartesian path containing one or more six-axis poses.

Declared fields/defaults:

```python
label: str
path: tuple[tuple[float, ...], ...]
profile: OrderedMotionProfile
metadata: OrderedMotionMetadata = OrderedMotionMetadata()
limit_profile: OrderedMotionLimitProfile | None = None
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def to_payload(self) -> dict[str, object]
```

### `OrderedUnwindJoint6Command`

```python
@dataclass(frozen=True)
class OrderedUnwindJoint6Command:
```

One typed request to unwind robot Joint 6 inside an ordered chain.

Declared fields/defaults:

```python
label: str
velocity_percent: float
acceleration_percent: float
protected: bool = False
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def to_payload(self) -> dict[str, object]
```

### `serialize_ordered_motion_commands`

```python
def serialize_ordered_motion_commands(commands: list[OrderedMotionCommand] | tuple[OrderedMotionCommand, ...]) -> list[dict[str, object]]
```

Serialize typed commands at the ordered-motion transport boundary.

### `serialize_ordered_motion_inputs`

```python
def serialize_ordered_motion_inputs(commands: list[OrderedMotionInput] | tuple[OrderedMotionInput, ...]) -> list[dict[str, object]]
```

Serialize typed commands at the robot-client boundary.

### `_base_payload`

```python
def _base_payload(label: str, profile: OrderedMotionProfile, metadata: OrderedMotionMetadata) -> dict[str, object]
```

### `_require_pose`

```python
def _require_pose(name: str, pose: tuple[float, ...]) -> None
```

### `_require_finite`

```python
def _require_finite(name: str, value: float) -> None
```

### `MotionSequenceSegment`

```python
@dataclass(frozen=True)
class MotionSequenceSegment:
```

One explicitly parameterized robot motion segment.

Declared fields/defaults:

```python
position: list[float]
velocity: float
acceleration: float
motion_type: MotionType = 'linear'
blend_radius: float = 0.0
```

## `plane_pose_mapper.py`

Source: [src/engine/robot/plane_pose_mapper.py](../../../src/engine/robot/plane_pose_mapper.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `dataclasses`, `logging`, `math`, `typing`.

Module declarations (expressions are shown without evaluating them):

```python
TRACE_LOG_LEVEL = logging.DEBUG - 5
```

### `PlanePose`

```python
@dataclass(frozen=True)
class PlanePose:
```

Declared fields/defaults:

```python
x: float
y: float
rz: float
```

### `PlanePoseMapper`

```python
class PlanePoseMapper:
```

Map robot XY points from one pose frame into another pose frame.

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, source_pose: PlanePose, target_pose: PlanePose)
```

```python
@property
def source_pose(self) -> PlanePose
```

```python
@property
def target_pose(self) -> PlanePose
```

```python
@classmethod
def from_positions(cls, source_position: Sequence[float], target_position: Sequence[float]) -> 'PlanePoseMapper'
```

```python
def map_point(self, x: float, y: float) -> tuple[float, float]
```

## `relative_tool_calibration_service.py`

Source: [src/engine/robot/relative_tool_calibration_service.py](../../../src/engine/robot/relative_tool_calibration_service.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `collections.abc`, `logging`, `math`, `src.engine.robot.tool_transform`.

### `RelativeToolCalibrationService`

```python
class RelativeToolCalibrationService:
```

Calibrate a tool TCP by touching a point previously captured with a reference tool.

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, *, minimum_samples: int=3)
```

```python
def capture_reference(self, flange_pose: Sequence[float], tool_transform: Sequence[float]) -> None
```

```python
def capture_candidate(self, flange_pose: Sequence[float]) -> list[float]
```

```python
def solve(self) -> dict
```

```python
def clear(self) -> None
```

### `_rounded`

```python
def _rounded(values: Sequence[float]) -> list[float]
```

## `tool_activation_service.py`

Source: [src/engine/robot/tool_activation_service.py](../../../src/engine/robot/tool_activation_service.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `collections.abc`, `src.engine.robot.tool_transform`, `typing`.

### `ToolRegistryClient`

```python
class ToolRegistryClient(Protocol):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def update_tool(self, tool_id: int, name: str | None, transform: Sequence[float], *, persist: bool, collision_profile: str | None=None) -> tuple[bool, str]
```

### `ToolActivator`

```python
class ToolActivator(Protocol):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def set_active_tool(self, tool: int) -> bool
```

### `ToolActivationService`

```python
class ToolActivationService:
```

Synchronize a resolved tool transform before selecting it on the robot.

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, registry: ToolRegistryClient, activator: ToolActivator)
```

```python
def activate(self, *, tool_id: int, name: str, reference_transform: Sequence[float], relative_transform: Sequence[float], persist_registry: bool=True, collision_profile: str='') -> tuple[bool, str, list[float]]
```

## `tool_changer.py`

Source: [src/engine/robot/tool_changer.py](../../../src/engine/robot/tool_changer.py).

Imports (including optional/function-local imports; not a startup dependency list): `dataclasses`, `src.engine.robot.interfaces.i_tool_changer`, `src.engine.robot.interfaces.tool_definition`, `typing`.

### `ToolChangeStep`

```python
@dataclass
class ToolChangeStep:
```

Declared fields/defaults:

```python
kind: str = 'motion'
label: str = ''
pose: list[float] = field(default_factory=list)
motion_type: str = 'linear'
velocity: float = 10.0
acceleration: float = 10.0
blend_radius: float = 0.0
wait_seconds: float = 0.0
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
@classmethod
def from_dict(cls, data: dict) -> 'ToolChangeStep'
```

```python
def to_dict(self) -> dict
```

### `SlotConfig`

```python
@dataclass
class SlotConfig:
```

Declared fields/defaults:

```python
id: int
tool_id: Optional[int]
occupied: bool = False
label: str = ''
pickup_sequence: List[ToolChangeStep] = field(default_factory=list)
dropoff_sequence: List[ToolChangeStep] = field(default_factory=list)
```

### `ToolChanger`

```python
class ToolChanger(IToolChanger):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, slots: List[SlotConfig], tools: List[ToolDefinition])
```

```python
def get_slot_id_by_tool_id(self, tool_id: int) -> Optional[int]
```

```python
def is_slot_occupied(self, slot_id: int) -> bool
```

```python
def set_slot_available(self, slot_id: int) -> None
```

```python
def set_slot_not_available(self, slot_id: int) -> None
```

```python
def get_occupied_slots(self) -> List[int]
```

```python
def get_empty_slots(self) -> List[int]
```

```python
def list_tools(self) -> List[ToolDefinition]
```

```python
def get_slot(self, slot_id: int) -> SlotConfig | None
```

## `tool_manager.py`

Source: [src/engine/robot/tool_manager.py](../../../src/engine/robot/tool_manager.py).

Imports (including optional/function-local imports; not a startup dependency list): `.interfaces`, `.interfaces.i_motion_service`, `.interfaces.i_tool_changer`, `.interfaces.tool_definition`, `logging`, `src.shared_contracts.declarations`, `threading`, `time`, `typing`.

### `ToolManager`

```python
class ToolManager(IToolService):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, motion_service: IMotionService, tool_changer: IToolChanger, robot_config, movement_groups, slot_definitions: List[ToolSlotDefinition] | None=None, tool_activator=None, operator_confirmation=None)
```

```python
@property
def current_gripper(self) -> Optional[int]
```

```python
@property
def current_tool(self) -> Optional[int]
```

```python
def pickup_tool(self, tool_id: int, max_retries: int=3) -> Tuple[bool, Optional[str]]
```

```python
def drop_off_tool(self, tool_id: int, max_retries: int=3) -> Tuple[bool, Optional[str]]
```

```python
def add_tool(self, name: str, tool) -> None
```

```python
def get_tool(self, name: str)
```

```python
def verify_gripper_change(self, target_gripper_id: int) -> bool
```

```python
def pickup_gripper(self, gripper_id: int, max_retries: int=3) -> Tuple[bool, Optional[str]]
```

```python
def drop_off_gripper(self, gripper_id: int, max_retries: int=3) -> Tuple[bool, Optional[str]]
```

```python
def get_tools(self) -> List[ToolDefinition]
```

## `tool_transform.py`

Source: [src/engine/robot/tool_transform.py](../../../src/engine/robot/tool_transform.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `collections.abc`, `math`.

### `rotation_matrix`

```python
def rotation_matrix(rx_deg: float, ry_deg: float, rz_deg: float) -> list[list[float]]
```

Return the XYZ Euler rotation used by robot tool transforms.

### `rotate`

```python
def rotate(matrix: Sequence[Sequence[float]], vector: Sequence[float]) -> list[float]
```

### `inverse_rotate`

```python
def inverse_rotate(matrix: Sequence[Sequence[float]], vector: Sequence[float]) -> list[float]
```

### `compose_translation`

```python
def compose_translation(reference: Sequence[float], relative: Sequence[float]) -> list[float]
```

Compose a translation-only relative tool transform with an absolute reference TCP.
