# Module reference: `src/robot_systems/paint/processes/paint/execution_machine/handlers/dropoff`

[Package guide](README.md) · [Complete source index](../../../../../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [dropoff_handler.py](#dropoff_handlerpy)
- [dropoff_handlers.py](#dropoff_handlerspy)
- [post_return_handler.py](#post_return_handlerpy)
- [prepare_dropoff_handler.py](#prepare_dropoff_handlerpy)

## `__init__.py`

Source: [src/robot_systems/paint/processes/paint/execution_machine/handlers/dropoff/__init__.py](../../../../../../../../src/robot_systems/paint/processes/paint/execution_machine/handlers/dropoff/__init__.py).

Dropoff-phase execution-machine handlers.

No top-level functions, classes or public value declarations; inspect the source for imports or entry-point statements.

## `dropoff_handler.py`

Source: [src/robot_systems/paint/processes/paint/execution_machine/handlers/dropoff/dropoff_handler.py](../../../../../../../../src/robot_systems/paint/processes/paint/execution_machine/handlers/dropoff/dropoff_handler.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `logging`, `src.robot_systems.paint.processes.paint.config`, `src.robot_systems.paint.processes.paint.execute.diagnostics`, `src.robot_systems.paint.processes.paint.execution_machine.context`, `src.robot_systems.paint.processes.paint.execution_machine.handlers.common.motion_handlers`, `src.robot_systems.paint.processes.paint.execution_machine.handlers.dropoff.dropoff_handlers`, `src.robot_systems.paint.processes.paint.execution_machine.state`.

### `handle_dropoff`

```python
def handle_dropoff(ctx: PaintExecutionContext) -> PaintExecutionState
```

### `log_timing`

```python
def log_timing(ctx: PaintExecutionContext, stage: str) -> None
```

### `log_completion`

```python
def log_completion(ctx: PaintExecutionContext) -> None
```

## `dropoff_handlers.py`

Source: [src/robot_systems/paint/processes/paint/execution_machine/handlers/dropoff/dropoff_handlers.py](../../../../../../../../src/robot_systems/paint/processes/paint/execution_machine/handlers/dropoff/dropoff_handlers.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `dataclasses`, `logging`, `math`, `numpy`, `src.engine.geometry.planar`, `src.engine.robot.motion_sequence`, `src.robot_systems.paint.processes.paint.config`, `src.robot_systems.paint.processes.paint.execute.diagnostics`, `src.robot_systems.paint.processes.paint.execution_machine.handlers.common.motion_handlers`, `src.robot_systems.paint.processes.paint.motion.pose_comparison`, `src.robot_systems.paint.processes.paint.motion.pose_sampling`, `src.robot_systems.paint.processes.paint.next_cycle_target`, `src.robot_systems.paint.processes.paint.tray_dry.plate_layout`, `src.robot_systems.paint.timing`, `time`.

### `_completed_rotation_turns`

```python
def _completed_rotation_turns(rotation_delta_deg: float) -> int
```

Count only fully executed 360-degree turns, preserving direction.

### `DropoffReleaseWaypoint`

```python
@dataclass(frozen=True)
class DropoffReleaseWaypoint:
```

One release-strategy move or release action.

Declared fields/defaults:

```python
label: str
pose: list[float] | None
vel_percent: float
acc_percent: float
motion_type: OrderedMotionType = OrderedMotionType.PTP
blendR: float = 0.0
release_here: bool = False
corridor_id: str | None = None
```

### `_ordered_position_command`

```python
def _ordered_position_command(label: str, pose: object, velocity_percent: object, acceleration_percent: object, motion_type: OrderedMotionType, blend_radius: object=0.0, *, protected: bool=False) -> OrderedPositionCommand
```

### `_parse_motion_type`

```python
def _parse_motion_type(value: object, *, field_name: str) -> OrderedMotionType
```

Validate an external/configured motion type at its input boundary.

### `_DropoffRouteItem`

```python
@dataclass(frozen=True)
class _DropoffRouteItem:
```

Declared fields/defaults:

```python
label: str
position: list[float]
velocity_percent: float
acceleration_percent: float
motion_type: OrderedMotionType
blend_radius: float
```

### `_PlateMotionProfile`

```python
@dataclass(frozen=True)
class _PlateMotionProfile:
```

Declared fields/defaults:

```python
velocity_percent: float
acceleration_percent: float
blend_radius: float
motion_type: OrderedMotionType
```

### `_PlateNextWaypoint`

```python
@dataclass
class _PlateNextWaypoint:
```

Declared fields/defaults:

```python
position: list[float]
profile: _PlateMotionProfile
```

### `DropoffReleasePlan`

```python
@dataclass(frozen=True)
class DropoffReleasePlan:
```

Resolved release sequence for the currently held painted workpiece.

Declared fields/defaults:

```python
strategy_name: DropoffStrategy
waypoints: tuple[DropoffReleaseWaypoint, ...]
```

### `open_dropoff_passage_for_preparation`

```python
def open_dropoff_passage_for_preparation(executor: object) -> tuple[bool, str]
```

Open the configured passage before planning any route that crosses its lid.

### `execute_dropoff_preparation_for_executor`

```python
def execute_dropoff_preparation_for_executor(executor: object) -> tuple[bool, str]
```

Build and execute paint-to-dropoff safe travel, align, and Joint 6 unwind.

### `execute_dropoff_release_for_executor`

```python
def execute_dropoff_release_for_executor(executor: object, *, next_cycle_start: NextCycleTarget | None=None) -> tuple[bool, str]
```

Build and execute the configured dropoff release strategy.

### `_execute_movement_group_ordered_exit`

```python
def _execute_movement_group_ordered_exit(executor: object, retract_waypoint: DropoffReleaseWaypoint, next_cycle_start: NextCycleTarget) -> tuple[bool, str]
```

Blend a sub-zero corridor retract into the next-cycle start move.

### `_move_to_next_cycle_start`

```python
def _move_to_next_cycle_start(executor: object, next_cycle_start: NextCycleTarget) -> bool
```

### `_next_cycle_start_pose_reached`

```python
def _next_cycle_start_pose_reached(executor: object, next_cycle_start: NextCycleTarget, position_tolerance_mm: float=2.0, orientation_tolerance_deg: float=2.0, *, log_result: bool=True) -> bool
```

### `_wait_for_next_cycle_start_pose`

```python
def _wait_for_next_cycle_start_pose(executor: object, next_cycle_start: NextCycleTarget, *, timeout_s: float=2.0, poll_interval_s: float=0.05, stable_samples: int=2) -> bool
```

Wait through ordered-chain response/telemetry skew for stable arrival.

### `_on_workpiece_release_verified`

```python
def _on_workpiece_release_verified(executor: object) -> tuple[bool, str]
```

Notify the composed system after release verification succeeds.

### `_verify_workpiece_released`

```python
def _verify_workpiece_released(executor: object) -> tuple[bool, str]
```

Verify that vacuum cleared after pump-off at the dropoff waypoint.

### `_build_dropoff_release_plan`

```python
def _build_dropoff_release_plan(executor: object) -> DropoffReleasePlan
```

### `build_ordered_dropoff_preparation_segments`

```python
def build_ordered_dropoff_preparation_segments(executor: object) -> tuple[list[OrderedPositionCommand | OrderedUnwindJoint6Command], list[float] | None]
```

Build the post-paint ordered dropoff preparation chain. This is the place to adjust ordered dropoff preparation move shape: - safe-travel segment labels - safe-travel/dropoff align velocity and acceleration - route `blendR` - final Joint 6 unwind segment settings

### `_resolve_dropoff_safe_travel_waypoints`

```python
def _resolve_dropoff_safe_travel_waypoints(executor: object) -> list[dict]
```

### `_apply_distributed_dropoff_unwind`

```python
def _apply_distributed_dropoff_unwind(executor: object, poses: list[list[float]], start_pose: list[float] | None) -> list[list[float]]
```

Progressively shift the active rotation component by whole-turn equivalents so Joint 6 can unwind while travelling toward dropoff.

### `_should_prepare_dropoff_align_before_unwind`

```python
def _should_prepare_dropoff_align_before_unwind(executor: object) -> bool
```

### `_dropoff_strategy_name`

```python
def _dropoff_strategy_name(executor: object) -> DropoffStrategy
```

### `_resolve_dropoff_release_pose`

```python
def _resolve_dropoff_release_pose(executor: object) -> list[float] | None
```

### `_resolve_dropoff_align_pose`

```python
def _resolve_dropoff_align_pose(executor: object, reference_pose: list[float] | None=None) -> list[float] | None
```

### `_resolve_dropoff_preparation_pose`

```python
def _resolve_dropoff_preparation_pose(executor: object, reference_pose: list[float] | None=None) -> list[float] | None
```

Resolve the safe above-floor endpoint used before a corridor dropoff.

### `_plate_motion_profile`

```python
def _plate_motion_profile(dropoff: object, key: str) -> _PlateMotionProfile
```

### `_plate_ordered_segment`

```python
def _plate_ordered_segment(label: str, pose: list[float], profile: _PlateMotionProfile, *, stop: bool=False) -> OrderedPositionCommand
```

### `_wait_for_motion_slot_idle`

```python
def _wait_for_motion_slot_idle(executor: object, *, timeout_s: float=2.0, poll_interval_s: float=0.025, stable_samples: int=2) -> bool
```

Wait through the controller-success/backend-slot release handoff.

### `_plate_route_poses_with_distributed_unwind`

```python
def _plate_route_poses_with_distributed_unwind(executor: object, *, entry_gate_pose: list[float], exit_gate_pose: list[float], center_pose: list[float], dropoff_pose: list[float], next_start_pose: list[float] | None, use_center_waypoint: bool, entry_completed: bool=False) -> dict[str, list[float]]
```

### `build_plate_entry_segments_for_paint_chain`

```python
def build_plate_entry_segments_for_paint_chain(executor: object) -> tuple[list[OrderedPositionCommand], list[float] | None, str]
```

Build plate entry through release for the combined paint chain.

### `_interpolate_route_rotations`

```python
def _interpolate_route_rotations(start_pose: list[float], route_poses: list[list[float]], *, end_rotation: float, rotation_index: int) -> None
```

Interpolate one rotation axis at a constant rate over route distance.

### `_plate_route_uses_center`

```python
def _plate_route_uses_center(dropoff: object, reservation: object) -> bool
```

Select the safer center route for placements near the bottom-left corner.

### `_execute_plate_layout_ordered_release`

```python
def _execute_plate_layout_ordered_release(executor: object, *, next_cycle_start: NextCycleTarget | None) -> tuple[bool, str]
```

### `_execute_plate_layout_preparation`

```python
def _execute_plate_layout_preparation(executor: object) -> tuple[bool, str]
```

Unwind at the paint-detach pose before the plate entry chain.

### `_dropoff_align_pose_near_reference`

```python
def _dropoff_align_pose_near_reference(executor: object, align_pose: list[float], reference_pose: list[float] | None=None) -> list[float]
```

## `post_return_handler.py`

Source: [src/robot_systems/paint/processes/paint/execution_machine/handlers/dropoff/post_return_handler.py](../../../../../../../../src/robot_systems/paint/processes/paint/execution_machine/handlers/dropoff/post_return_handler.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `logging`, `src.robot_systems.paint.processes.paint.execute.diagnostics`, `src.robot_systems.paint.processes.paint.execution_machine.context`, `src.robot_systems.paint.processes.paint.execution_machine.handlers.common.motion_handlers`, `src.robot_systems.paint.processes.paint.execution_machine.state`, `src.robot_systems.paint.timing`, `time`.

### `handle_post_return`

```python
def handle_post_return(ctx: PaintExecutionContext) -> PaintExecutionState
```

### `log_timing`

```python
def log_timing(ctx: PaintExecutionContext, stage: str) -> None
```

### `log_on_not_moved`

```python
def log_on_not_moved(ctx: PaintExecutionContext) -> None
```

### `log_on_exception`

```python
def log_on_exception(ctx: PaintExecutionContext, exception: Exception) -> None
```

## `prepare_dropoff_handler.py`

Source: [src/robot_systems/paint/processes/paint/execution_machine/handlers/dropoff/prepare_dropoff_handler.py](../../../../../../../../src/robot_systems/paint/processes/paint/execution_machine/handlers/dropoff/prepare_dropoff_handler.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `logging`, `src.robot_systems.paint.processes.paint.execute.diagnostics`, `src.robot_systems.paint.processes.paint.execution_machine.context`, `src.robot_systems.paint.processes.paint.execution_machine.handlers.common.motion_handlers`, `src.robot_systems.paint.processes.paint.execution_machine.handlers.dropoff.dropoff_handlers`, `src.robot_systems.paint.processes.paint.execution_machine.state`.

### `handle_prepare_dropoff`

```python
def handle_prepare_dropoff(ctx: PaintExecutionContext) -> PaintExecutionState
```

### `log_timing`

```python
def log_timing(ctx: PaintExecutionContext, stage: str) -> None
```
