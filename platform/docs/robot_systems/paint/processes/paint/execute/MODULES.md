# Module reference: `src/robot_systems/paint/processes/paint/execute`

[Package guide](README.md) · [Complete source index](../../../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [diagnostics.py](#diagnosticspy)
- [dropoff_executor.py](#dropoff_executorpy)
- [edge_cleanup_executor.py](#edge_cleanup_executorpy)
- [incremental_paint_executor.py](#incremental_paint_executorpy)
- [paint_contact_executor.py](#paint_contact_executorpy)
- [paint_debug_artifacts.py](#paint_debug_artifactspy)
- [paint_motion_executor.py](#paint_motion_executorpy)
- [pickup_executor.py](#pickup_executorpy)
- [projection_preview.py](#projection_previewpy)
- [workpiece_path_executor.py](#workpiece_path_executorpy)

## `__init__.py`

Source: [src/robot_systems/paint/processes/paint/execute/__init__.py](../../../../../../src/robot_systems/paint/processes/paint/execute/__init__.py).

Imports (including optional/function-local imports; not a startup dependency list): `.execution_plane`, `.paint_debug_artifacts`, `.workpiece_path_executor`, `src.robot_systems.paint.processes.paint.plan.paint_contact_motion`.

Package-level import/export surface:

```python
from .execution_plane import ExecutionPlaneStrategy, get_execution_plane_strategy
from .paint_debug_artifacts import build_executed_snapshot_series, write_pivot_debug_dump, write_pivot_debug_plot
from src.robot_systems.paint.processes.paint.plan.paint_contact_motion import project_paint_contact_motion_continuous, project_paint_motion_geometry_continuous, rebase_contact_motion_path_to_zero_start_rotation, rebase_projected_paint_path_to_zero_start_rz
from .workpiece_path_executor import PaintExecutorContactMotionConfig, PaintExecutorDependencies, PaintExecutorMotionConfig, PaintWorkpiecePathExecutor
```

No top-level functions, classes or public value declarations; inspect the source for imports or entry-point statements.

## `diagnostics.py`

Source: [src/robot_systems/paint/processes/paint/execute/diagnostics.py](../../../../../../src/robot_systems/paint/processes/paint/execute/diagnostics.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `concurrent.futures`, `csv`, `datetime`, `logging`, `matplotlib`, `matplotlib.pyplot`, `numpy`, `pathlib`, `re`, `src.engine.robot.path_interpolation.new_interpolation.debug_plotting`, `src.engine.robot.path_preparation`, `src.robot_systems.paint.processes.paint.config`, `src.robot_systems.paint.processes.paint.execute.paint_debug_artifacts`, `src.robot_systems.paint.timing`, `time`.

### `elapsed_s`

```python
def elapsed_s(start: float) -> float
```

### `path_length_mm`

```python
def path_length_mm(path: list[list[float]]) -> float
```

### `write_platform_command_path_csv`

```python
def write_platform_command_path_csv(*, command_path: list[list[float]], vel: float, acc: float, pattern_type: str, stage: str, pipeline_stages: dict[str, list[list[float]]] | None=None)
```

Queue CSV and PNG export of the exact ROS-bound Cartesian path.

### `_write_platform_command_path_artifacts`

```python
def _write_platform_command_path_artifacts(command_path: tuple[tuple[float, ...], ...], vel: float, acc: float, pattern_type: str, stage: str, pipeline_stages) -> None
```

### `_write_contour_pipeline_csv`

```python
def _write_contour_pipeline_csv(output_path: Path, pipeline_stages) -> None
```

### `_write_contour_pipeline_plot`

```python
def _write_contour_pipeline_plot(output_path: Path, pipeline_stages) -> None
```

### `_write_contour_before_after_plot`

```python
def _write_contour_before_after_plot(output_path: Path, pipeline_stages) -> None
```

### `_path_turn_angles_degrees`

```python
def _path_turn_angles_degrees(xy: np.ndarray) -> np.ndarray
```

### `_write_platform_pose_plot`

```python
def _write_platform_pose_plot(output_path: Path, command_path) -> None
```

### `_set_equal_3d_axes`

```python
def _set_equal_3d_axes(axis, xyz: np.ndarray) -> None
```

Give X/Y/Z the same physical scale without collapsing flat paths.

### `_log_cartesian_command_path_diagnostics`

```python
def _log_cartesian_command_path_diagnostics(command_path: list[list[float]]) -> None
```

### `_run_cartesian_command_path_diagnostics`

```python
def _run_cartesian_command_path_diagnostics(command_path: list[list[float]]) -> None
```

### `_log_cartesian_command_path_diagnostics_sync`

```python
def _log_cartesian_command_path_diagnostics_sync(command_path: list[list[float]]) -> None
```

Log final Cartesian command-path geometry without modifying the path. The goal is to distinguish an upstream Cartesian backtrack from an IK-only joint-space reversal. Diagnostics run on the exact command path that will be handed to the robot service (including final orientation/retreat edits).

### `diagnostics_with_command_rotation`

```python
def diagnostics_with_command_rotation(diagnostics: list[dict[str, float | int]] | None, command_path: list[list[float]], rotation_index: int) -> list[dict[str, float | int]] | None
```

Attach final robot-command rotation values to projection diagnostics.

### `write_path_shape_comparison_debug`

```python
def write_path_shape_comparison_debug(*, debug_dump_dir: str | None, plan: WorkpieceExecutionPlan) -> None
```

### `execute_paint_trajectory_with_optional_trace`

```python
def execute_paint_trajectory_with_optional_trace(*, robot_service, debug_dump_dir: str | None, pivot_config: PaintSimulationConfig, command_pivot_path: list[list[float]], vel: float, acc: float, pivot_pose: list[float] | None, pattern_type: str, stage: str, tcp_to_tool_local_xy: tuple[float, float] | None=None, paint_process_config: PaintProcessConfig | None=None) -> int
```

Execute a paint trajectory and optionally write commanded-vs-actual samples.

### `write_pivot_job_debug_artifacts`

```python
def write_pivot_job_debug_artifacts(*, debug_dump_dir: str | None, pivot_config: PaintSimulationConfig, source_path: list[list[float]], command_pivot_path: list[list[float]], snapshots: list[np.ndarray] | None, diagnostics: list[dict[str, float | int]] | None, pivot_pose: list[float] | None, anchor_xy: tuple[float, float] | None, source_rotation_deg: float, pattern_type: str, stage: str, paint_process_config: PaintProcessConfig | None=None) -> None
```

## `dropoff_executor.py`

Source: [src/robot_systems/paint/processes/paint/execute/dropoff_executor.py](../../../../../../src/robot_systems/paint/processes/paint/execute/dropoff_executor.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `dataclasses`, `logging`, `src.engine.robot.motion_sequence`, `src.engine.robot.path_preparation`, `src.robot_systems.paint.processes.paint.config`, `src.robot_systems.paint.processes.paint.execute.diagnostics`, `src.robot_systems.paint.processes.paint.execution_machine.handlers.dropoff.dropoff_handlers`, `src.robot_systems.paint.processes.paint.motion.pose_comparison`, `src.robot_systems.paint.timing`, `time`, `typing`.

### `DropoffWaypoint`

```python
@dataclass(frozen=True)
class DropoffWaypoint:
```

One dropoff move or release action.

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

### `DropoffPlan`

```python
@dataclass(frozen=True)
class DropoffPlan:
```

Resolved dropoff sequence for the current held workpiece.

Declared fields/defaults:

```python
strategy_name: DropoffStrategy
waypoints: tuple[DropoffWaypoint, ...]
```

### `PaintDropoffStrategy`

```python
class PaintDropoffStrategy(Protocol):
```

Build a dropoff plan without exposing strategy specifics to the main executor.

Declared fields/defaults:

```python
name: DropoffStrategy
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def build_plan(self, owner, execution_plan: WorkpieceExecutionPlan) -> DropoffPlan
```

Return the ordered dropoff actions for the active workpiece.

### `MovementGroupDropoffStrategy`

```python
class MovementGroupDropoffStrategy:
```

Release the held workpiece at the configured dropoff movement group.

Declared fields/defaults:

```python
name = DropoffStrategy.MOVEMENT_GROUP
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def build_plan(self, owner, execution_plan: WorkpieceExecutionPlan) -> DropoffPlan
```

### `PaintDropoffExecutor`

```python
class PaintDropoffExecutor:
```

Execute the configured paint dropoff strategy.

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, owner, strategy: PaintDropoffStrategy | None=None) -> None
```

```python
@timed_step(_logger, 'pre_release_dropoff')
def execute(self, execution_plan: WorkpieceExecutionPlan) -> tuple[bool, str]
```

Execute the dropoff plan and release the workpiece at its release waypoint.

## `edge_cleanup_executor.py`

Source: [src/robot_systems/paint/processes/paint/execute/edge_cleanup_executor.py](../../../../../../src/robot_systems/paint/processes/paint/execute/edge_cleanup_executor.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `dataclasses`, `logging`, `numpy`, `src.engine.robot.motion_sequence`, `src.engine.robot.path_preparation`, `src.robot_systems.paint.processes.paint.config`, `src.robot_systems.paint.processes.paint.execute.diagnostics`, `src.robot_systems.paint.processes.paint.execution_machine.handlers.common.motion_handlers`, `src.robot_systems.paint.processes.paint.execution_machine.handlers.dropoff.dropoff_handlers`, `src.robot_systems.paint.timing`, `time`.

### `_CleanupPreplan`

```python
@dataclass(frozen=True)
class _CleanupPreplan:
```

Declared fields/defaults:

```python
ok: bool
message: str
total_waypoints: int
stage_approach_pose: list[float]
command_path: list[list[float]]
```

### `_position_command`

```python
def _position_command(label: str, motion_type: object, position: object, velocity_percent: object, acceleration_percent: object, blend_radius: object) -> OrderedPositionCommand
```

Build one strictly typed cleanup/drop-off position command.

### `PaintEdgeCleanupExecutor`

```python
class PaintEdgeCleanupExecutor:
```

Coordinate the optional XY/RZ edge-cleanup pass after XZ/RY paint.

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, owner) -> None
```

```python
def should_run_after_xz_ry(self) -> bool
```

Return whether the configured XZ/RY process should run XY/RZ edge cleanup.

```python
def should_run_after_xy_rz(self) -> bool
```

Return whether the configured XY/RZ process should run XY/RZ edge cleanup.

```python
def should_run_after_current_paint(self) -> bool
```

Return whether the current paint cycle will run a cleanup pass.

```python
@timed_step(_logger, 'edge_cleanup_pre_unwind_align')
def move_to_original_orientation_before_unwind(self) -> tuple[bool, str]
```

Return the held workpiece to the saved align pose before Joint 6 unwind.

```python
@timed_step(_logger, 'edge_cleanup_unwind')
def unwind_joint6_before_cleanup(self, *, failure_context: str | None=None) -> tuple[bool, str]
```

Unwind Joint 6 before the XY/RZ edge-cleanup pass.

```python
@timed_step(_logger, 'edge_cleanup_stage_xy_rz')
def stage_xy_rz_cleanup(self, execution_plan: WorkpieceExecutionPlan) -> tuple[bool, str]
```

Build the XY/RZ edge-cleanup plan and move to its perpendicular approach pose.

```python
def add_perpendicular_approach_and_retreat_waypoints(self, command_path: list[list[float]]) -> list[list[float]]
```

Add cleanup approach and retreat segments along the perpendicular plane axis.

```python
def append_perpendicular_retreat_waypoint(self, command_path: list[list[float]]) -> list[list[float]]
```

Append a cleanup-only retreat waypoint along the perpendicular plane axis.

```python
@timed_step(_logger, 'edge_cleanup_perpendicular_retreat')
def move_perpendicular_retreat_after_cleanup(self) -> tuple[bool, str]
```

Move off cleanup contact along the configured perpendicular plane axis.

```python
def build_ordered_cleanup_segments(self, align_pose: list[float], stage_approach_pose: list[float], command_path: list[list[float]]) -> tuple[list[OrderedMotionCommand], list[float]]
```

Return ordered-chain segments for cleanup plus pre-dropoff preparation.

```python
def build_ordered_cleanup_chain_extension(self, execution_plan: WorkpieceExecutionPlan, *, started: float, align_pose: list[float] | None=None) -> tuple[bool, str, int, list[OrderedMotionCommand], list[float] | None]
```

Prepare cleanup segments for a larger ordered paint-cycle chain.

```python
@timed_step(_logger, 'edge_cleanup_xy_rz_pass')
def execute_after_unwind(self, execution_plan: WorkpieceExecutionPlan, started: float) -> tuple[bool, str, int]
```

Run the XY/RZ edge-cleanup projection pass without releasing vacuum.

```python
@timed_step(_logger, 'edge_cleanup_xy_rz_direct_pass')
def execute_after_xy_rz_paint(self, execution_plan: WorkpieceExecutionPlan, started: float, *, unwind_before_cleanup: bool=True) -> tuple[bool, str, int]
```

Run an XY/RZ cleanup pass by reprojecting the prepared contour at the Clean pose.

## `incremental_paint_executor.py`

Source: [src/robot_systems/paint/processes/paint/execute/incremental_paint_executor.py](../../../../../../src/robot_systems/paint/processes/paint/execute/incremental_paint_executor.py).

Paint a measured command-path prefix, then move to an inspection pose.

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `math`, `src.engine.robot.motion_sequence`, `src.robot_systems.paint.processes.paint.execute.workpiece_path_executor`, `src.robot_systems.paint.processes.paint.incremental_adjustment`, `time`.

### `run_incremental_paint_contact`

```python
def run_incremental_paint_contact(ctx) -> tuple[bool, str]
```

Hold after every section; only an explicit Finish proceeds to dropoff.

## `paint_contact_executor.py`

Source: [src/robot_systems/paint/processes/paint/execute/paint_contact_executor.py](../../../../../../src/robot_systems/paint/processes/paint/execute/paint_contact_executor.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `cv2`, `logging`, `numpy`, `src.engine.geometry.planar`, `src.engine.robot.path_preparation`, `src.robot_systems.paint.processes.paint.config`, `src.robot_systems.paint.processes.paint.execute.diagnostics`, `src.robot_systems.paint.processes.paint.execute.projection_preview`, `src.robot_systems.paint.processes.paint.motion.path_geometry`, `src.robot_systems.paint.processes.paint.paint_contact_job`, `src.robot_systems.paint.timing`, `time`, `typing`.

### `_apply_non_paint_clearance`

```python
def _apply_non_paint_clearance(path: list[list[float]], diagnostics: list[dict[str, float | int]] | None, clearance_profile_mm: list[float], config: PaintSimulationConfig) -> list[list[float]]
```

Retract projected poses from the pivot according to the source profile.

### `_remove_projected_local_reversals`

```python
def _remove_projected_local_reversals(path: list[list[float]], *, max_leg_mm: float=3.0, minimum_turn_deg: float=170.0) -> list[list[float]]
```

Remove short folds introduced when tangent rotation is projected about a pivot. Source-contour sanitization cannot see these folds because rotating an offset workpiece about the fixed paint pivot changes TCP XY. Only local, near-U-turn triples are removed here; approach/retreat transitions have a long leg and are deliberately left untouched.

### `_workpiece_min_rect_size_mm`

```python
def _workpiece_min_rect_size_mm(execution_plan: WorkpieceExecutionPlan) -> tuple[float, float]
```

Return the prepared geometry's minimum-area-rectangle sides in millimetres.

### `_workpiece_largest_side_mm`

```python
def _workpiece_largest_side_mm(execution_plan: WorkpieceExecutionPlan) -> float
```

Return the long side of the prepared geometry's minimum-area rectangle.

### `_tcp_to_tool_local_xy`

```python
def _tcp_to_tool_local_xy(job: dict, paint_config: PaintSimulationConfig) -> tuple[float, float] | None
```

Return the local vector from configured robot TCP to selected tool point.

### `PaintContactExecutor`

```python
class PaintContactExecutor:
```

Execute prepared paint-contact paths against the fixed paint shaft.

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, owner) -> None
```

```python
@timed_step(_logger, 'execute_paint_contact_paths')
def execute(self, execution_plan: WorkpieceExecutionPlan, *, vel_override: float | None=None, acc_override: float | None=None, append_retreat: bool=True, retreat_fn: Callable[[list[list[float]]], list[list[float]]] | None=None, execute_robot: bool=True, collected_command_paths: list[list[list[float]]] | None=None, collected_command_jobs: list[PaintContactCommandJob] | None=None, control=None, pivot_offset_override_mm: float | None=None) -> tuple[bool, str, int]
```

Execute all projected paint-contact paths in the prepared execution plan.

## `paint_debug_artifacts.py`

Source: [src/robot_systems/paint/processes/paint/execute/paint_debug_artifacts.py](../../../../../../src/robot_systems/paint/processes/paint/execute/paint_debug_artifacts.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `datetime`, `json`, `logging`, `matplotlib`, `matplotlib.pyplot`, `numpy`, `os`, `src.engine.robot.targeting.target_point_geometry`, `src.robot_systems.paint.processes.paint.config`, `src.robot_systems.paint.processes.paint.execute.execution_plane`, `src.robot_systems.paint.processes.paint.plan.paint_contact_motion`, `threading`, `time`, `typing`.

Module declarations (expressions are shown without evaluating them):

```python
project_paint_motion_geometry_continuous = project_paint_contact_motion_continuous
```

### `RobotMotionTrace`

```python
class RobotMotionTrace:
```

Background sampler for actual robot poses during blocking trajectory execution.

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, *, get_pose: Callable[[], Sequence[float] | None], sample_period_s: float) -> None
```

```python
def start(self) -> None
```

```python
def stop(self) -> list[dict[str, object]]
```

### `start_robot_motion_trace`

```python
def start_robot_motion_trace(*, get_pose: Callable[[], Sequence[float] | None], sample_period_s: float) -> RobotMotionTrace
```

### `_path_length_mm`

```python
def _path_length_mm(path: list[list[float]]) -> float
```

### `_axis_label_from_index`

```python
def _axis_label_from_index(index: int) -> str
```

### `_unwrap_degrees`

```python
def _unwrap_degrees(values: np.ndarray) -> np.ndarray
```

### `_angle_delta_deg`

```python
def _angle_delta_deg(value: float, reference: float) -> float
```

### `_motion_trace_comparison`

```python
def _motion_trace_comparison(*, commanded_path: list[list[float]], actual_samples: list[dict[str, object]], pivot_config: PaintSimulationConfig, pivot_pose: list[float] | None, tcp_to_tool_local_xy: tuple[float, float] | None=None) -> tuple[dict[str, object], list[dict[str, object]]]
```

### `write_execution_motion_trace`

```python
def write_execution_motion_trace(*, debug_dump_dir: str | None, pivot_config: PaintSimulationConfig, commanded_path: list[list[float]], actual_samples: list[dict[str, object]], pivot_pose: list[float] | None, pattern_type: str, stage: str, tcp_to_tool_local_xy: tuple[float, float] | None=None) -> None
```

Write commanded-vs-actual robot motion samples for execution diagnostics.

### `build_executed_snapshot_series`

```python
def build_executed_snapshot_series(*, source_path: list[list[float]], executed_path: list[list[float]], pivot_pose: list[float] | None, pivot_config: PaintSimulationConfig, anchor_xy: tuple[float, float] | None=None, source_rotation_deg: float=0.0) -> list[np.ndarray]
```

Rebase projected physical contour snapshots onto the final robot command poses.

### `write_pivot_debug_dump`

```python
def write_pivot_debug_dump(*, debug_dump_dir: str | None, pivot_config: PaintSimulationConfig, source_path: list[list[float]], pivot_path: list[list[float]], diagnostics: list[dict[str, float | int]] | None, pivot_pose: list[float] | None, pattern_type: str, stage: str, anchor_xy: tuple[float, float] | None=None, source_rotation_deg: float=0.0) -> None
```

Write source and robot command paths to disk for offline trajectory inspection.

### `write_pivot_debug_plot`

```python
def write_pivot_debug_plot(*, debug_dump_dir: str | None, pivot_config: PaintSimulationConfig, source_path: list[list[float]], pivot_path: list[list[float]], snapshots: list[np.ndarray] | None, diagnostics: list[dict[str, float | int]] | None, pivot_pose: list[float] | None, anchor_xy: tuple[float, float] | None=None, source_rotation_deg: float=0.0, pattern_type: str, stage: str) -> None
```

Write a compact visual debug plot for the source and robot command trajectories.

## `paint_motion_executor.py`

Source: [src/robot_systems/paint/processes/paint/execute/paint_motion_executor.py](../../../../../../src/robot_systems/paint/processes/paint/execute/paint_motion_executor.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `dataclasses`, `logging`, `numpy`, `src.engine.robot.motion_sequence`, `src.robot_systems.paint.processes.paint.motion.pose_sampling`, `src.robot_systems.paint.timing`.

### `PaintMotionExecutor`

```python
class PaintMotionExecutor:
```

Shared robot motion and vacuum operations for paint execution handlers.

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, owner) -> None
```

```python
@timed_step(_logger, 'pickup_phase', label_arg='label')
def move_pickup_phase(self, label: str, pose: list[float], *, velocity: float, acceleration: float, motion_type: OrderedMotionType=OrderedMotionType.PTP, blendR: float=0.0, corridor_id: str | None=None) -> bool
```

Execute one carried-workpiece robot move with explicit motion limits.

```python
@timed_step(_logger, 'pickup_phase', label_arg='label')
def move_ordered_pickup_sequence(self, label: str, segments: list[OrderedMotionCommand]) -> bool
```

Execute a pickup sequence as ordered robot motion segments.

```python
def pause_current_execution(self) -> None
```

```python
def read_ordered_motion_chain_status(self) -> dict | None
```

```python
@staticmethod
def ordered_motion_chain_segment_is_protected(ordered: dict | None) -> bool
```

```python
@staticmethod
def ordered_motion_chain_resume_index(ordered: dict | None) -> int
```

```python
def resume_after_interrupted_non_contact_motion(self, label: str) -> bool
```

```python
def consume_ordered_chain_resume_start_index(self) -> int | None
```

```python
def mark_ordered_chain_interrupted_by_pause(self, interrupted: bool) -> None
```

```python
def trim_ordered_pickup_segments_from_current_pose(self, segments: list[OrderedMotionCommand]) -> list[OrderedMotionCommand]
```

Skip already-passed pickup waypoints after pause/resume.

```python
@timed_step(_logger, 'vacuum_on')
def turn_vacuum_on(self, *, required: bool=False) -> tuple[bool, str]
```

Enable the vacuum pump before pickup if one is configured.

```python
@timed_step(_logger, 'vacuum_off')
def turn_vacuum_off(self, *, wait_for_blow_off: bool=True) -> tuple[bool, str]
```

Disable the vacuum pump after staging if one is configured.

## `pickup_executor.py`

Source: [src/robot_systems/paint/processes/paint/execute/pickup_executor.py](../../../../../../src/robot_systems/paint/processes/paint/execute/pickup_executor.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `dataclasses`, `logging`, `math`, `src.engine.robot.enums.axis`, `src.engine.robot.motion_sequence`, `src.engine.robot.path_preparation`, `src.engine.robot.procedures`, `src.robot_systems.paint.processes.paint.config`, `src.robot_systems.paint.processes.paint.configured_motion_waypoint`, `src.robot_systems.paint.processes.paint.execute.diagnostics`, `src.robot_systems.paint.processes.paint.magazine_load_result`, `src.robot_systems.paint.processes.paint.motion.pose_sampling`, `src.robot_systems.paint.processes.paint.paint_contact_job`, `src.robot_systems.paint.timing`, `time`, `typing`.

### `pickup_pose_is_close`

```python
def pickup_pose_is_close(actual_pose: object, target_pose: object, *, position_tolerance_mm: float=0.5, orientation_tolerance_deg: float=0.5) -> bool
```

Return True when a recovery move would be an effective no-op.

### `pickup_condition_is_active_after_retract`

```python
def pickup_condition_is_active_after_retract(condition: object, *, required_samples: int=1, sample_interval_s: float=0.0) -> bool
```

Require the carried-workpiece signal to remain active after retract.

### `PickupWaypoint`

```python
@dataclass(frozen=True)
class PickupWaypoint:
```

One carried-part pickup or staging move.

Declared fields/defaults:

```python
label: str
pose: list[float]
vel_percent: float
acc_percent: float
motion_type: OrderedMotionType | None = None
blendR: float | None = None
```

### `MagazineTransferWaypoint`

```python
@dataclass(frozen=True)
class MagazineTransferWaypoint:
```

One fully typed move in a magazine pickup-to-release chain.

Declared fields/defaults:

```python
label: str
pose: list[float]
velocity_percent: float
acceleration_percent: float
motion_type: OrderedMotionType
blend_radius: float = 0.0
```

### `PickupPlan`

```python
@dataclass(frozen=True)
class PickupPlan:
```

Resolved pickup sequence for moving the workpiece to the paint start.

Declared fields/defaults:

```python
strategy_name: str
motion_plan: object
waypoints: tuple[PickupWaypoint, ...]
vacuum_on_before_moves: bool = True
change_plane_combined_with_first_contact: bool = False
contact_mode: str = PICKUP_CONTACT_MODE_PLANNED
contact_waypoint_index: int | None = None
retract_reference_pose: list[float] | None = None
```

### `normalize_pickup_contact_mode`

```python
def normalize_pickup_contact_mode(value: object) -> str
```

### `PaintPickupStrategy`

```python
class PaintPickupStrategy(Protocol):
```

Build paint pickup/staging plans without exposing strategy details to the main executor.

Declared fields/defaults:

```python
name: str
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def build_plan(self, owner, prepared_workpiece: WorkpieceExecutionPlan) -> PickupPlan | None
```

Return the ordered pickup actions for the active workpiece.

### `DefaultPickupStrategy`

```python
class DefaultPickupStrategy:
```

Default strategy for calibration-table pickup, align, and pivot staging.

Declared fields/defaults:

```python
name = 'default'
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def build_plan(self, owner, prepared_workpiece: WorkpieceExecutionPlan) -> PickupPlan | None
```

### `PaintPickupExecutor`

```python
class PaintPickupExecutor:
```

Execute the configured pickup strategy.

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, owner, strategy: PaintPickupStrategy | None=None) -> None
```

```python
def build_plan(self, prepared_workpiece: WorkpieceExecutionPlan) -> PickupPlan | None
```

```python
@timed_step(_logger, 'pickup_to_pivot')
def execute(self, prepared_workpiece: WorkpieceExecutionPlan, *, pickup_plan: PickupPlan | None=None, prepared_continuation_segments: list[OrderedMotionCommand] | None=None, stop_after_retract: bool=False) -> tuple[bool, str]
```

Run pickup, align, and staging according to the configured strategy.

### `build_ordered_pickup_segments`

```python
def build_ordered_pickup_segments(pickup_plan: PickupPlan) -> list[OrderedPositionCommand]
```

Build ordered paint pickup/staging motion segments from a pickup plan. Prefer `build_paint_pickup_segments(...)` when the caller already has the waypoint list.

### `build_paint_pickup_segments`

```python
def build_paint_pickup_segments(waypoints: tuple[PickupWaypoint, ...] | list[PickupWaypoint]) -> list[OrderedPositionCommand]
```

Build paint pickup/staging motion segments. This is the place to adjust pickup ordered-chain move shape: - pickup segment `type` - pickup/staging velocity and acceleration propagation - pickup route `blendR` - which waypoints must stop before continuing

### `_equivalent_pickup_poses`

```python
def _equivalent_pickup_poses(first: list[float], second: list[float]) -> bool
```

### `build_ordered_paint_contact_segments`

```python
def build_ordered_paint_contact_segments(paint_paths: list[list[list[float]]], paint_jobs: list[PaintContactCommandJob], contact_staging, *, label_prefix: str='paint', acceleration_scale: float=1.0) -> list[OrderedMotionCommand]
```

Build ordered paint-contact path segments. This is the place to adjust ordered paint-contact path command shape.

### `build_magazine_pickup_release_segments`

```python
def build_magazine_pickup_release_segments(transfer_waypoints: tuple[MagazineTransferWaypoint, ...]) -> list[OrderedPositionCommand]
```

Build ordered magazine pickup-to-release segments. This is the place to adjust magazine transfer `blendR`.

## `projection_preview.py`

Source: [src/robot_systems/paint/processes/paint/execute/projection_preview.py](../../../../../../src/robot_systems/paint/processes/paint/execute/projection_preview.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `numpy`, `src.engine.robot.path_preparation`, `src.robot_systems.paint.processes.paint.config`, `src.robot_systems.paint.processes.paint.plan.paint_contact_motion`, `typing`.

### `pivot_source_path`

```python
def pivot_source_path(job: dict, pivot_config: PaintSimulationConfig) -> list[list[float]]
```

Return the path used as geometric source for pivot projection.

### `projection_tool_anchor_xy`

```python
def projection_tool_anchor_xy(job: dict, pivot_config: PaintSimulationConfig) -> tuple[float, float] | None
```

Return the selected tool/workpiece anchor used by pivot projection.

### `project_pivot_paths_for_editor`

```python
def project_pivot_paths_for_editor(*, execution_plan: WorkpieceExecutionPlan, pivot_config: PaintSimulationConfig, base_pivot_pose: list[float], pickup_plan, apply_pivot_offset: Callable[[list[float] | None, float], list[float] | None], resolve_pivot_offset_mm: Callable[[dict | None, WorkpieceExecutionPlan | None], float], align_projected_path_to_pickup_plan: Callable[[list[list[float]], object | None], list[list[float]]], pivot_execution_command_path: Callable[..., list[list[float]]], project_motion_geometry: Callable[..., tuple[list[list[float]], list[np.ndarray], list[dict[str, float | int]]]]=project_paint_contact_motion_continuous) -> tuple[list[list[list[float]]], list[float] | None]
```

Project editor-visible pivot center paths for each prepared execution job.

### `project_pivot_motion_snapshots_for_editor`

```python
def project_pivot_motion_snapshots_for_editor(*, execution_plan: WorkpieceExecutionPlan, pivot_config: PaintSimulationConfig, base_pivot_pose: list[float], pickup_plan, apply_pivot_offset: Callable[[list[float] | None, float], list[float] | None], resolve_pivot_offset_mm: Callable[[dict | None, WorkpieceExecutionPlan | None], float], project_motion_geometry: Callable[..., tuple[list[list[float]], list[np.ndarray], list[dict[str, float | int]]]]=project_paint_contact_motion_continuous) -> tuple[list[list[np.ndarray]], list[float] | None]
```

Return per-step projected shape snapshots for pivot motion plotting.

## `workpiece_path_executor.py`

Source: [src/robot_systems/paint/processes/paint/execute/workpiece_path_executor.py](../../../../../../src/robot_systems/paint/processes/paint/execute/workpiece_path_executor.py).

Paint workpiece process executor. This module is intentionally organized as a phase map while the executor is still being split into smaller collaborators: 1. Runtime configuration and editor-facing API. 2. Magazine pickup/release helpers. 3. Shared pose/configuration resolvers. 4. Preview and paint-contact path projection helpers. 5. Pickup, ordered-motion, pause/resume, and vacuum helpers. 6. Dropoff preparation/unwind helpers. 7. Top-level paint process orchestration.

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `dataclasses`, `logging`, `numpy`, `src.applications.workpiece_editor.service.i_workpiece_path_executor`, `src.engine.geometry.planar`, `src.engine.robot.motion_sequence`, `src.engine.robot.path_preparation`, `src.robot_systems.paint.processes.paint.config`, `src.robot_systems.paint.processes.paint.configured_motion_waypoint`, `src.robot_systems.paint.processes.paint.execute.dropoff_executor`, `src.robot_systems.paint.processes.paint.execute.edge_cleanup_executor`, `src.robot_systems.paint.processes.paint.execute.execution_plane`, `src.robot_systems.paint.processes.paint.execute.paint_contact_executor`, `src.robot_systems.paint.processes.paint.execute.paint_motion_executor`, `src.robot_systems.paint.processes.paint.execute.pickup_executor`, `src.robot_systems.paint.processes.paint.execute.projection_preview`, `src.robot_systems.paint.processes.paint.execution_control`, `src.robot_systems.paint.processes.paint.execution_machine.context`, `src.robot_systems.paint.processes.paint.execution_machine.machine_factory`, `src.robot_systems.paint.processes.paint.execution_machine.state`, `src.robot_systems.paint.processes.paint.motion.path_geometry`, `src.robot_systems.paint.processes.paint.plan`, `src.robot_systems.paint.processes.paint.plan.paint_contact_motion`, `src.robot_systems.paint.processes.paint.tray_dry.plate_layout`, `src.robot_systems.paint.timing`, `typing`.

### `_camera_to_tcp_delta`

```python
def _camera_to_tcp_delta(x_offset: float, y_offset: float, current_rz: float, reference_rz: float=0.0) -> tuple[float, float]
```

Return the tool-frame TCP sweep delta between the reference and current pickup angles.

### `_paint_axis_staging_offset_pose`

```python
def _paint_axis_staging_offset_pose(contact_pose: list[float], pivot_config: PaintSimulationConfig, *, z_offset_mm: float=0.0, paint_axis_offset_mm: float=0.0, perpendicular_axis_offset_mm: float=0.0) -> list[float]
```

Return the pre-paint staging pose below and behind the first pivot contact.

### `PaintExecutorDependencies`

```python
@dataclass(frozen=True)
class PaintExecutorDependencies:
```

Runtime services and callbacks needed by the paint process executor.

Declared fields/defaults:

```python
robot_service: object
path_preparation_service: Optional[IWorkpiecePathPreparationService] = None
base_position_provider: Optional[Callable[[], Optional[list[float]]]] = None
pickup_base_position_provider: Optional[Callable[[], Optional[list[float]]]] = None
cleanup_base_position_provider: Optional[Callable[[], Optional[list[float]]]] = None
dropoff_position_provider: Optional[Callable[[], Optional[list[float]]]] = None
calibration_position_provider: Optional[Callable[[], Optional[list[float]]]] = None
post_execute_callback: Optional[Callable[[], bool]] = None
dryer_ready_for_release: Optional[Callable[[], tuple[bool, str]]] = None
on_workpiece_release_verified: Optional[Callable[[], bool]] = None
robot_config_provider: Optional[Callable[[], object]] = None
vacuum_pump: object | None = None
vacuum_pump_enabled_provider: Optional[Callable[[], bool]] = None
vacuum_sensor: object | None = None
pickup_condition: object | None = None
pickup_condition_provider: Optional[Callable[[], object | None]] = None
paint_process_config_service: object | None = None
dropoff_motion_corridor_id: str | None = None
```

### `PaintExecutorMotionConfig`

```python
@dataclass(frozen=True)
class PaintExecutorMotionConfig:
```

Robot tool/user and process-motion switches for paint execution.

Declared fields/defaults:

```python
enable_vacuum_pump: bool = True
pickup_tool: int = 0
pickup_user: int = 0
pickup_z_mm: float | None = None
debug_dump_dir: str | None = None
```

### `PaintExecutorContactMotionConfig`

```python
@dataclass(frozen=True)
class PaintExecutorContactMotionConfig:
```

Configured pivot plane/profile used by paint projection and pickup handoff.

Declared fields/defaults:

```python
motion_plane: str = 'xy_z_rz'
translation_axis: str = 'x'
paint_side: str = 'negative'
translation_direction: str = 'forward'
flip_xz_ry_execution_rotation_direction: bool = False
mirror_xz_ry_pickup_handoff: bool = False
apply_camera_to_tcp_for_pickup: bool = False
camera_to_tcp_x_offset: float = 0.0
camera_to_tcp_y_offset: float = 0.0
```

### `_PreparedPaintProcessAdapter`

```python
class _PreparedPaintProcessAdapter:
```

Minimal production-service shape for editor execution of an already prepared plan.

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, path_executor: 'PaintWorkpiecePathExecutor') -> None
```

### `_normalize_contact_motion_config`

```python
def _normalize_contact_motion_config(*, motion_plane: str='xy_z_rz', translation_axis: str='x', pivot_side: str='negative', translation_direction: str='forward', apply_camera_to_tcp_for_pickup: bool=False, camera_to_tcp_x_offset: float=0.0, camera_to_tcp_y_offset: float=0.0, rotation_direction_sign: float=1.0, closed_contour_overlap_mm: float=0.0) -> PaintSimulationConfig
```

Normalize user-facing pivot settings into a validated simulation config.

### `_xz_ry_projection_rotation_sign`

```python
def _xz_ry_projection_rotation_sign(motion_plane: str, mirror_execution_rotation: bool) -> float
```

Return the planar rotation sign used during projection, before command generation.

### `PaintWorkpiecePathExecutor`

```python
class PaintWorkpiecePathExecutor(IWorkpiecePathExecutor):
```

Execute prepared paint paths from pickup through paint contact and dropoff. The class remains the process facade. Phase-specific collaborators already exist for pickup, paint contact, edge cleanup, and dropoff, while this file still owns shared state, configuration refresh, ordered-chain assembly, and process-level orchestration.

Declared fields/defaults:

```python
supports_paint_motion_states = True
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, *, dependencies: PaintExecutorDependencies, motion_config: PaintExecutorMotionConfig | None=None, contact_motion_config: PaintExecutorContactMotionConfig | None=None) -> None
```

Store robot dependencies and initialize the pivot/pickup execution configuration.

```python
def prepare_workpiece_execution_plan(self, workpiece: dict, skip_debug_plot: bool=False) -> WorkpieceExecutionPlan
```

Build and cache the execution plan for a paint workpiece.

```python
def get_last_execution_plan(self) -> WorkpieceExecutionPlan | None
```

Return the last paint execution plan prepared by this executor.

```python
def set_cycle_dropoff_strategy(self, strategy: str | None) -> None
```

Override the persisted strategy for one production cycle.

```python
def get_supported_execution_modes(self) -> tuple[str, ...]
```

Report the execution modes supported by the paint executor.

```python
def get_process_actions(self) -> tuple[WorkpieceProcessAction, ...]
```

Expose the paint process as one editor-facing action.

```python
def execute_process_action(self, execution_plan: WorkpieceExecutionPlan, action_id: str) -> tuple[bool, str]
```

Execute the requested paint process action.

```python
def get_projected_pivot_paths(self, execution_plan: WorkpieceExecutionPlan) -> tuple[list[list[list[float]]], list[float] | None]
```

Project center paths for each prepared execution job around the pivot pose.

```python
def get_pivot_motion_snapshots(self, execution_plan: WorkpieceExecutionPlan) -> tuple[list[list[np.ndarray]], list[float] | None]
```

Return per-step projected shape snapshots for pivot motion plotting.

```python
def execute_process_paths(self, execution_plan: WorkpieceExecutionPlan, mode: str='continuous') -> tuple[bool, str]
```

Paint no longer supports direct/manual paint-contact path execution.

```python
def pause_current_execution(self) -> None
```

```python
def execute_paint_process(self, prepared_workpiece: WorkpieceExecutionPlan, *, control=None) -> tuple[bool, str]
```

Run a prepared workpiece plan through the paint execution state machine.
