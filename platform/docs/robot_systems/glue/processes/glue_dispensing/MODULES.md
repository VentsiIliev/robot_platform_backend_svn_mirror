# Module reference: `src/robot_systems/glue/processes/glue_dispensing`

[Package guide](README.md) · [Complete source index](../../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [cancellation_token.py](#cancellation_tokenpy)
- [dispensing_config.py](#dispensing_configpy)
- [dispensing_context.py](#dispensing_contextpy)
- [dispensing_error.py](#dispensing_errorpy)
- [dispensing_machine_factory.py](#dispensing_machine_factorypy)
- [dispensing_path.py](#dispensing_pathpy)
- [dispensing_settings.py](#dispensing_settingspy)
- [dispensing_state.py](#dispensing_statepy)
- [glue_pump_controller.py](#glue_pump_controllerpy)
- [handler_guards.py](#handler_guardspy)
- [i_glue_type_resolver.py](#i_glue_type_resolverpy)
- [manual_debug_runner.py](#manual_debug_runnerpy)
- [pump_speed_adjuster.py](#pump_speed_adjusterpy)

## `__init__.py`

Source: [src/robot_systems/glue/processes/glue_dispensing/__init__.py](../../../../../src/robot_systems/glue/processes/glue_dispensing/__init__.py).

No top-level functions, classes or public value declarations; inspect the source for imports or entry-point statements.

## `cancellation_token.py`

Source: [src/robot_systems/glue/processes/glue_dispensing/cancellation_token.py](../../../../../src/robot_systems/glue/processes/glue_dispensing/cancellation_token.py).

### `CancellationToken`

```python
class CancellationToken:
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self) -> None
```

```python
def cancel(self, reason: str='') -> None
```

```python
def is_cancelled(self) -> bool
```

```python
def get_cancellation_reason(self) -> str
```

## `dispensing_config.py`

Source: [src/robot_systems/glue/processes/glue_dispensing/dispensing_config.py](../../../../../src/robot_systems/glue/processes/glue_dispensing/dispensing_config.py).

Imports (including optional/function-local imports; not a startup dependency list): `dataclasses`.

### `GlueDispensingConfig`

```python
@dataclass
class GlueDispensingConfig:
```

Declared fields/defaults:

```python
use_segment_settings: bool = True
use_segment_motion_settings: bool = True
turn_off_pump_between_paths: bool = True
adjust_pump_speed_while_spray: bool = True
robot_tool: int = 0
robot_user: int = 0
global_velocity: float = 10.0
global_acceleration: float = 30.0
move_to_first_point_poll_s: float = 0.02
move_to_first_point_timeout_s: float = 30.0
pump_thread_wait_poll_s: float = 0.1
final_position_poll_s: float = 0.1
pump_ready_timeout_s: float = 5.0
pump_thread_join_timeout_s: float = 2.0
pump_adjuster_poll_s: float = 0.01
```

## `dispensing_context.py`

Source: [src/robot_systems/glue/processes/glue_dispensing/dispensing_context.py](../../../../../src/robot_systems/glue/processes/glue_dispensing/dispensing_context.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `dataclasses`, `logging`, `math`, `src.robot_systems.glue.processes.glue_dispensing.context_ops.cleanup_ops`, `src.robot_systems.glue.processes.glue_dispensing.context_ops.motion_ops`, `src.robot_systems.glue.processes.glue_dispensing.context_ops.path_ops`, `src.robot_systems.glue.processes.glue_dispensing.context_ops.pump_thread_ops`, `src.robot_systems.glue.processes.glue_dispensing.dispensing_error`, `src.robot_systems.glue.processes.glue_dispensing.dispensing_path`, `src.robot_systems.glue.processes.glue_dispensing.dispensing_settings`, `src.robot_systems.glue.processes.glue_dispensing.dispensing_state`, `threading`, `typing`.

### `_dist`

```python
def _dist(a, b) -> float
```

### `DispensingContext`

```python
class DispensingContext:
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self) -> None
```

```python
def reset(self) -> None
```

```python
def save_progress(self, path_index: int, point_index: int) -> None
```

```python
def pause_from(self, state) -> None
```

```python
def stop_with_progress(self, path_index: int, point_index: int) -> None
```

```python
def pause_with_progress(self, state, path_index: int, point_index: int) -> None
```

```python
def mark_segment_trajectory_submitted(self, start_index: int, task_id: int | None=None) -> None
```

```python
def mark_segment_trajectory_completed(self) -> None
```

```python
def reset_segment_trajectory_state(self) -> None
```

```python
def pause_current_segment_execution(self, state) -> None
```

```python
def stop_current_segment_execution(self) -> None
```

```python
def estimate_resume_point_index_for_current_segment(self) -> int
```

```python
def mark_generator_stopped(self) -> None
```

```python
def mark_motor_stopped(self) -> None
```

```python
def mark_completed(self) -> None
```

```python
def clear_error(self) -> None
```

```python
def fail(self, kind: DispensingErrorKind, code: DispensingErrorCode, state, operation: str, message: str, exc: Exception | None=None, recoverable: bool=False)
```

```python
def has_valid_context(self) -> bool
```

```python
def build_debug_snapshot(self) -> dict[str, Any]
```

```python
def get_segment_settings(self) -> DispensingSegmentSettings | None
```

```python
def get_motor_address_for_current_path(self) -> int
```

```python
def get_valid_motor_address_for_current_path(self) -> int | None
```

```python
def get_motion_velocity(self) -> float
```

```python
def get_motion_acceleration(self) -> float
```

## `dispensing_error.py`

Source: [src/robot_systems/glue/processes/glue_dispensing/dispensing_error.py](../../../../../src/robot_systems/glue/processes/glue_dispensing/dispensing_error.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `dataclasses`, `enum`.

### `DispensingErrorKind`

```python
class DispensingErrorKind(Enum):
```

Declared fields/defaults:

```python
CONFIG = auto()
MOTION = auto()
PUMP = auto()
GENERATOR = auto()
THREAD = auto()
STATE = auto()
TIMEOUT = auto()
```

### `DispensingErrorCode`

```python
class DispensingErrorCode(Enum):
```

Declared fields/defaults:

```python
MISSING_CURRENT_PATH = auto()
MOVE_TO_FIRST_POINT_FAILED = auto()
MOVE_TO_FIRST_POINT_TIMEOUT = auto()
MOVE_LINEAR_FAILED = auto()
EXECUTE_TRAJECTORY_FAILED = auto()
INVALID_MOTOR_ADDRESS = auto()
PUMP_ON_FAILED = auto()
PUMP_OFF_FAILED = auto()
GENERATOR_START_FAILED = auto()
GENERATOR_STOP_FAILED = auto()
PUMP_THREAD_START_FAILED = auto()
PUMP_THREAD_READY_MISSING = auto()
PUMP_THREAD_READY_TIMEOUT = auto()
PUMP_THREAD_WAIT_FAILED = auto()
PUMP_THREAD_EXECUTION_FAILED = auto()
```

### `DispensingErrorInfo`

```python
@dataclass(slots=True)
class DispensingErrorInfo:
```

Declared fields/defaults:

```python
kind: DispensingErrorKind
code: DispensingErrorCode
state: object
operation: str
message: str
exception_type: str | None
path_index: int
point_index: int
recoverable: bool = False
```

## `dispensing_machine_factory.py`

Source: [src/robot_systems/glue/processes/glue_dispensing/dispensing_machine_factory.py](../../../../../src/robot_systems/glue/processes/glue_dispensing/dispensing_machine_factory.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `logging`, `src.engine.process.executable_state_machine`, `src.robot_systems.glue.processes.glue_dispensing.dispensing_config`, `src.robot_systems.glue.processes.glue_dispensing.dispensing_context`, `src.robot_systems.glue.processes.glue_dispensing.dispensing_state`, `src.robot_systems.glue.processes.glue_dispensing.handler_guards`, `src.robot_systems.glue.processes.glue_dispensing.state_handlers.hardware.generator_handlers`, `src.robot_systems.glue.processes.glue_dispensing.state_handlers.hardware.handle_starting_pump_adjustment_thread`, `src.robot_systems.glue.processes.glue_dispensing.state_handlers.hardware.handle_waiting_for_pump_thread_ready`, `src.robot_systems.glue.processes.glue_dispensing.state_handlers.hardware.pump_handlers`, `src.robot_systems.glue.processes.glue_dispensing.state_handlers.motion.handle_advancing_path`, `src.robot_systems.glue.processes.glue_dispensing.state_handlers.motion.handle_moving_to_first_point`, `src.robot_systems.glue.processes.glue_dispensing.state_handlers.motion.handle_sending_path_points`, `src.robot_systems.glue.processes.glue_dispensing.state_handlers.startup.handle_issuing_move_to_first_point`, `src.robot_systems.glue.processes.glue_dispensing.state_handlers.startup.handle_loading_current_path`, `src.robot_systems.glue.processes.glue_dispensing.state_handlers.startup.handle_loading_path`, `src.robot_systems.glue.processes.glue_dispensing.state_handlers.startup.handle_resuming`, `src.robot_systems.glue.processes.glue_dispensing.state_handlers.startup.handle_starting`, `src.robot_systems.glue.processes.glue_dispensing.state_handlers.terminal.terminal_handlers`, `src.robot_systems.glue.processes.glue_dispensing.state_handlers.waiting.handle_routing_path_completion_wait`, `src.robot_systems.glue.processes.glue_dispensing.state_handlers.waiting.handle_waiting_for_final_position`, `src.robot_systems.glue.processes.glue_dispensing.state_handlers.waiting.handle_waiting_for_pump_thread`.

### `DispensingMachineFactory`

```python
class DispensingMachineFactory:
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def build(self, context: DispensingContext, config: GlueDispensingConfig) -> ExecutableStateMachine
```

## `dispensing_path.py`

Source: [src/robot_systems/glue/processes/glue_dispensing/dispensing_path.py](../../../../../src/robot_systems/glue/processes/glue_dispensing/dispensing_path.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `dataclasses`, `src.robot_systems.glue.processes.glue_dispensing.dispensing_settings`, `typing`.

Module declarations (expressions are shown without evaluating them):

```python
DispensingPoint: TypeAlias = list[float]
DispensingPathPoints: TypeAlias = list[DispensingPoint]
DispensingSettings: TypeAlias = DispensingSegmentSettings
```

### `DispensingPathEntry`

```python
@dataclass(slots=True)
class DispensingPathEntry:
```

Declared fields/defaults:

```python
points: DispensingPathPoints
settings: DispensingSettings
metadata: dict[str, Any] = field(default_factory=dict)
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
@classmethod
def from_raw(cls, raw_entry) -> 'DispensingPathEntry'
```

```python
def is_empty(self) -> bool
```

```python
def sliced_from(self, point_index: int) -> DispensingPathPoints
```

### `normalize_dispensing_paths`

```python
def normalize_dispensing_paths(raw_paths: list[Any]) -> list[DispensingPathEntry]
```

## `dispensing_settings.py`

Source: [src/robot_systems/glue/processes/glue_dispensing/dispensing_settings.py](../../../../../src/robot_systems/glue/processes/glue_dispensing/dispensing_settings.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `dataclasses`, `src.robot_systems.glue.settings.glue`, `typing`.

### `DispensingSegmentSettings`

```python
@dataclass(slots=True)
class DispensingSegmentSettings:
```

Declared fields/defaults:

```python
glue_type: str | None = None
velocity: float | None = None
acceleration: float | None = None
time_between_generator_and_glue: float = 0.0
reach_start_threshold: float = 1.0
reach_end_threshold: float = 1.0
motor_speed: int = 0
forward_ramp_steps: int = 1
initial_ramp_speed: int = 0
initial_ramp_speed_duration: float = 1.0
speed_reverse: int = 0
reverse_duration: float = 0.0
reverse_ramp_steps: int = 1
glue_speed_coefficient: float = 5.0
glue_acceleration_coefficient: float = 0.0
extra: dict[str, Any] = field(default_factory=dict)
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
@classmethod
def from_raw(cls, raw_settings: Any) -> 'DispensingSegmentSettings'
```

```python
def to_dict(self) -> dict[str, Any]
```

```python
def get(self, key: str, default: Any=None) -> Any
```

### `_optional_float`

```python
def _optional_float(value: Any) -> float | None
```

## `dispensing_state.py`

Source: [src/robot_systems/glue/processes/glue_dispensing/dispensing_state.py](../../../../../src/robot_systems/glue/processes/glue_dispensing/dispensing_state.py).

Imports (including optional/function-local imports; not a startup dependency list): `enum`, `typing`.

### `GlueDispensingState`

```python
class GlueDispensingState(Enum):
```

Declared fields/defaults:

```python
IDLE = auto()
STARTING = auto()
LOADING_PATH = auto()
LOADING_CURRENT_PATH = auto()
ISSUING_MOVE_TO_FIRST_POINT = auto()
MOVING_TO_FIRST_POINT = auto()
TURNING_ON_GENERATOR = auto()
TURNING_ON_PUMP = auto()
STARTING_PUMP_ADJUSTMENT_THREAD = auto()
WAITING_FOR_PUMP_THREAD_READY = auto()
SENDING_PATH_POINTS = auto()
ROUTING_PATH_COMPLETION_WAIT = auto()
WAITING_FOR_PUMP_THREAD = auto()
WAITING_FOR_FINAL_POSITION = auto()
TURNING_OFF_PUMP = auto()
ADVANCING_PATH = auto()
TURNING_OFF_GENERATOR = auto()
RESUMING = auto()
PAUSED = auto()
STOPPED = auto()
COMPLETED = auto()
ERROR = auto()
```

### `GlueDispensingTransitions`

```python
class GlueDispensingTransitions:
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
@staticmethod
def get_rules() -> Dict[GlueDispensingState, Set[GlueDispensingState]]
```

## `glue_pump_controller.py`

Source: [src/robot_systems/glue/processes/glue_dispensing/glue_pump_controller.py](../../../../../src/robot_systems/glue/processes/glue_dispensing/glue_pump_controller.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `logging`, `src.engine.hardware.motor.interfaces.i_motor_service`, `src.robot_systems.glue.processes.glue_dispensing.dispensing_settings`, `typing`.

### `GluePumpController`

```python
class GluePumpController:
```

Adapter between the dispensing process and IMotorService. Reads motor parameters from per-segment settings dict or falls back to a GlueSettings dataclass when use_segment_settings=False.

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, motor_service: IMotorService, use_segment_settings: bool=True, fallback_settings=None) -> None
```

```python
def get_last_exception(self) -> Exception | None
```

```python
def pump_on(self, motor_address: int, settings: Optional[DispensingSegmentSettings]=None) -> bool
```

```python
def pump_off(self, motor_address: int, settings: Optional[DispensingSegmentSettings]=None) -> bool
```

## `handler_guards.py`

Source: [src/robot_systems/glue/processes/glue_dispensing/handler_guards.py](../../../../../src/robot_systems/glue/processes/glue_dispensing/handler_guards.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `src.robot_systems.glue.processes.glue_dispensing.dispensing_state`.

### `guard_stop`

```python
def guard_stop(context) -> GlueDispensingState | None
```

### `guard_pause`

```python
def guard_pause(context, current_state: GlueDispensingState) -> GlueDispensingState | None
```

## `i_glue_type_resolver.py`

Source: [src/robot_systems/glue/processes/glue_dispensing/i_glue_type_resolver.py](../../../../../src/robot_systems/glue/processes/glue_dispensing/i_glue_type_resolver.py).

Imports (including optional/function-local imports; not a startup dependency list): `abc`.

### `IGlueTypeResolver`

```python
class IGlueTypeResolver(ABC):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
@abstractmethod
def resolve(self, glue_type: str) -> int
```

Return motor_address for glue_type, or -1 if not found.

## `manual_debug_runner.py`

Source: [src/robot_systems/glue/processes/glue_dispensing/manual_debug_runner.py](../../../../../src/robot_systems/glue/processes/glue_dispensing/manual_debug_runner.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `argparse`, `dataclasses`, `json`, `logging`, `pathlib`, `src.engine.process.executable_state_machine`, `src.robot_systems.glue.domain.dispense_channels.dispense_channel_service`, `src.robot_systems.glue.processes.glue_dispensing.dispensing_config`, `src.robot_systems.glue.processes.glue_dispensing.dispensing_context`, `src.robot_systems.glue.processes.glue_dispensing.dispensing_machine_factory`, `src.robot_systems.glue.processes.glue_dispensing.dispensing_path`, `src.robot_systems.glue.processes.glue_dispensing.glue_pump_controller`, `sys`, `typing`.

### `_point`

```python
def _point(x: float, y: float=0.0, z: float=0.0) -> list[float]
```

### `_default_paths`

```python
def _default_paths() -> list[tuple[list[list[float]], dict[str, Any]]]
```

### `DebugRobotService`

```python
@dataclass
class DebugRobotService:
```

Declared fields/defaults:

```python
current_position: list[float] = field(default_factory=lambda: _point(0.0))
current_velocity: float = 10.0
current_acceleration: float = 30.0
ptp_commands: list[dict[str, Any]] = field(default_factory=list)
linear_commands: list[dict[str, Any]] = field(default_factory=list)
stop_count: int = 0
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def move_ptp(self, **kwargs) -> bool
```

```python
def move_linear(self, **kwargs) -> bool
```

```python
def get_current_position(self)
```

```python
def get_current_velocity(self) -> float
```

```python
def get_current_acceleration(self) -> float
```

```python
def stop_motion(self) -> None
```

```python
def set_current_position(self, position: list[float]) -> None
```

### `DebugMotorService`

```python
@dataclass
class DebugMotorService:
```

Declared fields/defaults:

```python
commands: list[dict[str, Any]] = field(default_factory=list)
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def turn_on(self, **kwargs) -> bool
```

```python
def turn_off(self, **kwargs) -> bool
```

```python
def set_speed(self, **kwargs) -> bool
```

### `DebugGeneratorController`

```python
@dataclass
class DebugGeneratorController:
```

Declared fields/defaults:

```python
commands: list[str] = field(default_factory=list)
is_on: bool = False
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def turn_on(self) -> None
```

```python
def turn_off(self) -> None
```

### `DebugGlueTypeResolver`

```python
class DebugGlueTypeResolver:
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, mapping: dict[str, int] | None=None) -> None
```

```python
def resolve(self, glue_type: str) -> int
```

### `DispensingManualDriver`

```python
class DispensingManualDriver:
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, paths: list[Any] | None=None, spray_on: bool=False, config: GlueDispensingConfig | None=None) -> None
```

```python
def reset(self) -> None
```

```python
def step(self, count: int=1) -> bool
```

```python
def request_pause(self) -> None
```

```python
def resume(self) -> None
```

```python
def request_stop(self) -> None
```

```python
def clear_stop(self) -> None
```

```python
def set_robot_position(self, position: list[float]) -> None
```

```python
def move_robot_to_current_start(self) -> None
```

```python
def move_robot_to_current_end(self) -> None
```

```python
def get_snapshot(self) -> dict[str, Any]
```

```python
def format_snapshot(self) -> str
```

### `_build_arg_parser`

```python
def _build_arg_parser() -> argparse.ArgumentParser
```

### `_print_help`

```python
def _print_help() -> None
```

### `_run_cli`

```python
def _run_cli(args: argparse.Namespace) -> int
```

### `main`

```python
def main() -> int
```

## `pump_speed_adjuster.py`

Source: [src/robot_systems/glue/processes/glue_dispensing/pump_speed_adjuster.py](../../../../../src/robot_systems/glue/processes/glue_dispensing/pump_speed_adjuster.py).

Dynamic pump speed adjustment — clean port of the old dynamicPumpSpeedAdjustment.y_pixels. Key changes from original: - IMotorService.set_speed() replaces adjustMotorSpeed() - IRobotService.get_current_position/velocity/acceleration() used directly - context.stop_event / context.run_allowed replace state-machine enum checks - stdlib logging replaces files.write_to_debug_file - inline math replaces robot_utils.calculate_distance_between_points

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `logging`, `math`, `src.engine.hardware.motor.interfaces.i_motor_service`, `src.engine.robot.interfaces.i_robot_service`, `src.robot_systems.glue.processes.glue_dispensing.dispensing_settings`, `threading`, `time`, `typing`.

### `_dist`

```python
def _dist(a, b) -> float
```

### `_should_exit`

```python
def _should_exit(context) -> Tuple[bool, int]
```

Return (exit, progress). progress=-1 means caller should fill in.

### `_update_checkpoints`

```python
def _update_checkpoints(pos, remaining, furthest, start_idx) -> int
```

### `_final_reached`

```python
def _final_reached(pos, final, remaining, furthest, threshold) -> bool
```

### `_calc_speed`

```python
def _calc_speed(velocity, acceleration, speed_coeff, accel_coeff) -> float
```

### `adjust_pump_speed_dynamically`

```python
def adjust_pump_speed_dynamically(motor_service: IMotorService, robot_service: IRobotService, speed_coeff, accel_coeff, motor_address: int, path: list, threshold: float, start_point_index: int=0, ready_event=None, context=None) -> Tuple[bool, int]
```

### `PumpThreadWithResult`

```python
class PumpThreadWithResult(threading.Thread):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, *args, **kwargs)
```

```python
def run(self) -> None
```

### `start_pump_speed_adjustment_thread`

```python
def start_pump_speed_adjustment_thread(motor_service: IMotorService, robot_service: IRobotService, settings: DispensingSegmentSettings | None, motor_address: int, path: list, reach_end_threshold: float, pump_ready_event, start_point_index: int=0, context=None) -> PumpThreadWithResult
```
