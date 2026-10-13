# Module reference: `src/robot_systems/paint/processes/paint/workflow`

[Package guide](README.md) · [Complete source index](../../../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [context.py](#contextpy)
- [machine_factory.py](#machine_factorypy)
- [state.py](#statepy)

## `__init__.py`

Source: [src/robot_systems/paint/processes/paint/workflow/__init__.py](../../../../../../src/robot_systems/paint/processes/paint/workflow/__init__.py).

Imports (including optional/function-local imports; not a startup dependency list): `src.robot_systems.paint.processes.paint.workflow.context`, `src.robot_systems.paint.processes.paint.workflow.machine_factory`, `src.robot_systems.paint.processes.paint.workflow.state`.

Package-level import/export surface:

```python
from src.robot_systems.paint.processes.paint.workflow.context import PaintExecutionContext
from src.robot_systems.paint.processes.paint.workflow.machine_factory import PaintExecutionMachineFactory
from src.robot_systems.paint.processes.paint.workflow.state import PaintExecutionState, PaintExecutionTransitions
```

Module declarations (expressions are shown without evaluating them):

```python
__all__ = ['PaintExecutionContext', 'PaintExecutionMachineFactory', 'PaintExecutionState', 'PaintExecutionTransitions']
```

## `context.py`

Source: [src/robot_systems/paint/processes/paint/workflow/context.py](../../../../../../src/robot_systems/paint/processes/paint/workflow/context.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `dataclasses`, `src.robot_systems.paint.processes.paint.configuration.models`, `src.robot_systems.paint.processes.paint.production.execution_control`, `src.robot_systems.paint.processes.paint.workflow.state`, `src.robot_systems.paint.processes.paint.results`, `src.robot_systems.paint.processes.paint.tray_dry.errors`, `threading`, `time`, `typing`.

### `PaintExecutionContext`

```python
@dataclass
class PaintExecutionContext:
```

Per-cycle state shared by paint execution-machine handlers.

Declared fields/defaults:

```python
production_service: object
stop_requested: Callable[[], bool]
control: PaintExecutionControl
process_config: PaintProcessConfig | None = None
raw_process_config: PaintProcessConfig | None = None
magazine_config: PaintMagazineLoadConfig | None = None
magazine_group: str = ''
magazine_index: int = 0
cycle_index: int = 1
repeats_after_success: bool = False
stop_event: threading.Event = field(default_factory=threading.Event)
run_allowed: threading.Event = field(default_factory=threading.Event)
state_machine: object | None = None
current_state: PaintExecutionState | None = None
paused_from_state: PaintExecutionState | None = None
resume_state: PaintExecutionState | None = None
is_resuming: bool = False
tray_failure: TrayFailure | None = None
result: PaintOperationResult = field(default_factory=lambda: PaintOperationResult(PaintOutcome.CANCELLED, 'Paint process stopped'))
total_started_at: float = field(default_factory=perf_counter)
snapshot: object | None = None
contour: object | None = None
raw_workpiece: object | None = None
workpiece_description: str = ''
execution_plan: object | None = None
paint_started_at: float | None = None
paint_previous_control: object | None = None
paint_timing_session: object | None = None
paint_timing_recorder: object | None = None
state_timing_recorder: object | None = None
paint_total_waypoints: int = 0
paint_ordered_result: PaintOperationResult | None = None
paint_contact_executed_in_ordered_chain: bool = False
paint_motion_active: bool = False
cycle_start_unwind_completed: bool = False
resume_retry_available: bool = False
calibration_group: str = ''
magazine_snapshot: object | None = None
magazine_contour: object | None = None
magazine_discovery_contours: list = field(default_factory=list)
magazine_discovery_active_contour: object | None = None
magazine_discovery_empty_capture: bool = False
magazine_pose: list[float] | None = None
magazine_release_pose: list[float] | None = None
magazine_target: dict | None = None
magazine_fixed_pickup_pose: list[float] | None = None
magazine_stage_only: bool = False
retry_capture_until_workpiece: bool = False
adjustment_session: object | None = None
magazine_nesting_has_more: bool = True
cached_workpiece_contour: object | None = None
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def should_stop(self) -> bool
```

```python
def motion_cancel_requested(self) -> bool
```

```python
def pause_from(self, state: PaintExecutionState) -> None
```

```python
def mark_resuming(self) -> None
```

```python
def consume_resume_retry(self) -> bool
```

```python
@property
def result_ok(self) -> bool
```

```python
@property
def result_message(self) -> str
```

```python
@property
def operation_failure(self) -> PaintFailure | None
```

```python
@operation_failure.setter
def operation_failure(self, failure: PaintFailure) -> None
```

```python
def set_outcome(self, result: PaintOperationResult) -> None
```

```python
def set_result(self, ok: bool, message: str) -> None
```

Adapter for handlers with simple completion/failure contracts.

```python
def snapshot_dict(self) -> dict
```

## `machine_factory.py`

Source: [src/robot_systems/paint/processes/paint/workflow/machine_factory.py](../../../../../../src/robot_systems/paint/processes/paint/workflow/machine_factory.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `logging`, `src.engine.process.executable_state_machine`, `src.robot_systems.paint.processes.paint.workflow.context`, `src.robot_systems.paint.processes.paint.workflow.handlers.dropoff.dropoff_handler`, `src.robot_systems.paint.processes.paint.workflow.handlers.dropoff.post_return_handler`, `src.robot_systems.paint.processes.paint.workflow.handlers.dropoff.prepare_dropoff_handler`, `src.robot_systems.paint.processes.paint.workflow.handlers.lifecycle.completed_handler`, `src.robot_systems.paint.processes.paint.workflow.handlers.lifecycle.error_handler`, `src.robot_systems.paint.processes.paint.workflow.handlers.lifecycle.idle_handler`, `src.robot_systems.paint.processes.paint.workflow.handlers.lifecycle.pause_handler`, `src.robot_systems.paint.processes.paint.workflow.handlers.lifecycle.startup_handler`, `src.robot_systems.paint.processes.paint.workflow.handlers.lifecycle.stopped_handler`, `src.robot_systems.paint.processes.paint.workflow.handlers.magazine_load.calibration_wait_camera_settle_handler`, `src.robot_systems.paint.processes.paint.workflow.handlers.magazine_load.magazine_capture_handler`, `src.robot_systems.paint.processes.paint.workflow.handlers.magazine_load.magazine_execute_pickup_release_handler`, `src.robot_systems.paint.processes.paint.workflow.handlers.magazine_load.magazine_move_to_calibration_handler`, `src.robot_systems.paint.processes.paint.workflow.handlers.magazine_load.magazine_move_to_magazine_handler`, `src.robot_systems.paint.processes.paint.workflow.handlers.magazine_load.magazine_prepare_pickup_release_handler`, `src.robot_systems.paint.processes.paint.workflow.handlers.magazine_load.magazine_wait_camera_settle_handler`, `src.robot_systems.paint.processes.paint.workflow.handlers.workflow.capture_handler`, `src.robot_systems.paint.processes.paint.workflow.handlers.workflow.edge_cleanup_handler`, `src.robot_systems.paint.processes.paint.workflow.handlers.workflow.execution_handler`, `src.robot_systems.paint.processes.paint.workflow.handlers.workflow.paint_contact_handler`, `src.robot_systems.paint.processes.paint.workflow.handlers.workflow.pickup_handler`, `src.robot_systems.paint.processes.paint.workflow.handlers.workflow.plan_handler`, `src.robot_systems.paint.processes.paint.workflow.handlers.workflow.preparation_handler`, `src.robot_systems.paint.processes.paint.workflow.state`, `src.robot_systems.paint.processes.paint.results`, `src.robot_systems.paint.processes.paint.tray_dry.errors`, `src.robot_systems.paint.timing`, `time`, `typing`.

### `PaintExecutionMachineFactory`

```python
class PaintExecutionMachineFactory:
```

Build the internal state machine for one paint production cycle.

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def build(self, context: PaintExecutionContext, *, initial_state: PaintExecutionState=PaintExecutionState.STARTING) -> ExecutableStateMachine
```

### `_record_current_state`

```python
def _record_current_state(context: PaintExecutionContext, state: PaintExecutionState) -> None
```

### `_register`

```python
def _register(registry: StateRegistry, context: PaintExecutionContext, state: PaintExecutionState, handler: Callable[[PaintExecutionContext], PaintExecutionState]) -> None
```

### `_failure_aware_handler`

```python
def _failure_aware_handler(handler: Callable[[PaintExecutionContext], PaintExecutionState], state: PaintExecutionState) -> Callable[[PaintExecutionContext], PaintExecutionState]
```

### `_timed_handler`

```python
def _timed_handler(context: PaintExecutionContext, state: PaintExecutionState, handler: Callable[[PaintExecutionContext], PaintExecutionState]) -> Callable[[PaintExecutionContext], PaintExecutionState]
```

### `_record_state_timing`

```python
def _record_state_timing(context: PaintExecutionContext, *, state: PaintExecutionState, next_state: PaintExecutionState | None, success: bool, exception: bool, started: float, ended: float, message: str) -> None
```

### `_state_success`

```python
def _state_success(context: PaintExecutionContext, next_state: PaintExecutionState) -> bool
```

### `_state_message`

```python
def _state_message(context: PaintExecutionContext, next_state: PaintExecutionState) -> str
```

### `_state_timing_enabled`

```python
def _state_timing_enabled(context: PaintExecutionContext) -> bool
```

## `state.py`

Source: [src/robot_systems/paint/processes/paint/workflow/state.py](../../../../../../src/robot_systems/paint/processes/paint/workflow/state.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `enum`.

### `PaintExecutionState`

```python
class PaintExecutionState(Enum):
```

Business-level states for one paint production cycle.

Declared fields/defaults:

```python
STARTING = auto()
MAGAZINE_MOVE_TO_MAGAZINE = auto()
MAGAZINE_WAIT_CAMERA_SETTLE = auto()
MAGAZINE_CAPTURE = auto()
MAGAZINE_PREPARE_PICKUP_RELEASE = auto()
MAGAZINE_EXECUTE_PICKUP_RELEASE = auto()
MAGAZINE_MOVE_TO_CALIBRATION = auto()
CALIBRATION_WAIT_CAMERA_SETTLE = auto()
CAPTURE_WORKPIECE = auto()
PREPARE_WORKPIECE = auto()
BUILD_EXECUTION_PLAN = auto()
EXECUTE_PAINT = auto()
PICKUP = auto()
PAINT_CONTACT = auto()
EDGE_CLEANUP = auto()
PREPARE_DROPOFF = auto()
DROPOFF = auto()
POST_RETURN = auto()
COMPLETED = auto()
PAUSED = auto()
STOPPED = auto()
ERROR = auto()
IDLE = auto()
```

### `PaintExecutionTransitions`

```python
class PaintExecutionTransitions:
```

Allowed transitions for the paint production execution machine.

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
@staticmethod
def get_rules() -> dict[PaintExecutionState, set[PaintExecutionState]]
```
