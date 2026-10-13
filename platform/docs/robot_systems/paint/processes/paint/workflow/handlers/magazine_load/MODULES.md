# Module reference: `src/robot_systems/paint/processes/paint/workflow/handlers/magazine_load`

[Package guide](README.md) · [Complete source index](../../../../../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [calibration_wait_camera_settle_handler.py](#calibration_wait_camera_settle_handlerpy)
- [magazine_capture_handler.py](#magazine_capture_handlerpy)
- [magazine_control.py](#magazine_controlpy)
- [magazine_execute_pickup_release_handler.py](#magazine_execute_pickup_release_handlerpy)
- [magazine_move_to_calibration_handler.py](#magazine_move_to_calibration_handlerpy)
- [magazine_move_to_magazine_handler.py](#magazine_move_to_magazine_handlerpy)
- [magazine_prepare_pickup_release_handler.py](#magazine_prepare_pickup_release_handlerpy)
- [magazine_wait_camera_settle_handler.py](#magazine_wait_camera_settle_handlerpy)

## `__init__.py`

Source: [src/robot_systems/paint/processes/paint/workflow/handlers/magazine_load/__init__.py](../../../../../../../../src/robot_systems/paint/processes/paint/workflow/handlers/magazine_load/__init__.py).

Magazine-load execution-machine handlers.

No top-level functions, classes or public value declarations; inspect the source for imports or entry-point statements.

## `calibration_wait_camera_settle_handler.py`

Source: [src/robot_systems/paint/processes/paint/workflow/handlers/magazine_load/calibration_wait_camera_settle_handler.py](../../../../../../../../src/robot_systems/paint/processes/paint/workflow/handlers/magazine_load/calibration_wait_camera_settle_handler.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `src.robot_systems.paint.processes.paint.workflow.context`, `src.robot_systems.paint.processes.paint.workflow.handlers.common.guards`, `src.robot_systems.paint.processes.paint.workflow.handlers.magazine_load.magazine_control`, `src.robot_systems.paint.processes.paint.workflow.state`.

### `handle_calibration_wait_camera_settle`

```python
def handle_calibration_wait_camera_settle(ctx: PaintExecutionContext) -> PaintExecutionState
```

## `magazine_capture_handler.py`

Source: [src/robot_systems/paint/processes/paint/workflow/handlers/magazine_load/magazine_capture_handler.py](../../../../../../../../src/robot_systems/paint/processes/paint/workflow/handlers/magazine_load/magazine_capture_handler.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `cv2`, `logging`, `numpy`, `src.robot_systems.paint.processes.paint.configuration.models`, `src.robot_systems.paint.processes.paint.workflow.context`, `src.robot_systems.paint.processes.paint.workflow.handlers.common.guards`, `src.robot_systems.paint.processes.paint.workflow.state`, `src.robot_systems.paint.processes.paint.production.magazine.outcomes`, `src.robot_systems.paint.processes.paint.planning`, `src.robot_systems.paint.processes.paint.results`, `time`.

### `handle_magazine_capture`

```python
def handle_magazine_capture(ctx: PaintExecutionContext) -> PaintExecutionState
```

### `_ordered_contours`

```python
def _ordered_contours(contours) -> list
```

Return valid discovery contours in deterministic top-to-bottom order.

### `_ordered_contours_nearest_to_calibration`

```python
def _ordered_contours_nearest_to_calibration(ctx: PaintExecutionContext, contours) -> list
```

Order piles from the calibration-side exit inward in robot XY space.

## `magazine_control.py`

Source: [src/robot_systems/paint/processes/paint/workflow/handlers/magazine_load/magazine_control.py](../../../../../../../../src/robot_systems/paint/processes/paint/workflow/handlers/magazine_load/magazine_control.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `src.robot_systems.paint.processes.paint.workflow.context`, `src.robot_systems.paint.processes.paint.workflow.handlers.common.guards`, `src.robot_systems.paint.processes.paint.workflow.state`.

### `interrupted_or_error`

```python
def interrupted_or_error(ctx: PaintExecutionContext, state: PaintExecutionState, message: str) -> PaintExecutionState
```

## `magazine_execute_pickup_release_handler.py`

Source: [src/robot_systems/paint/processes/paint/workflow/handlers/magazine_load/magazine_execute_pickup_release_handler.py](../../../../../../../../src/robot_systems/paint/processes/paint/workflow/handlers/magazine_load/magazine_execute_pickup_release_handler.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `concurrent.futures`, `logging`, `math`, `src.engine.geometry.planar`, `src.engine.robot.enums.axis`, `src.engine.robot.motion_sequence`, `src.engine.robot.procedures`, `src.robot_systems.paint.processes.paint.configuration.models`, `src.robot_systems.paint.processes.paint.operations.pickup.executor`, `src.robot_systems.paint.processes.paint.workflow.context`, `src.robot_systems.paint.processes.paint.workflow.handlers.common.guards`, `src.robot_systems.paint.processes.paint.workflow.handlers.magazine_load.magazine_control`, `src.robot_systems.paint.processes.paint.workflow.state`, `src.robot_systems.paint.processes.paint.production.magazine.outcomes`, `src.robot_systems.paint.processes.paint.motion.pose_sampling`, `src.robot_systems.paint.processes.paint.results`, `src.robot_systems.paint.timing`, `time`.

### `_configured_motion_type`

```python
def _configured_motion_type(value: object, *, field_name: str) -> OrderedMotionType
```

### `calculate_workpiece_dropoff_pose`

```python
def calculate_workpiece_dropoff_pose(calibration_pose: list[float] | tuple[float, ...], plate_dropoff_pose: list[float] | tuple[float, ...], workpiece_rz_at_calibration_deg: float) -> list[float]
```

Return a plate pose preserving workpiece orientation across plane rotation. ``workpiece_rz_at_calibration_deg`` is the resolved robot/tool RZ holding the workpiece at the calibration pose, not the raw contour angle. XYZ, RX, and RY come from the plate pose; RZ also includes the taught rotation from the calibration pose to the plate pose.

### `execute_magazine_pickup_release`

```python
def execute_magazine_pickup_release(load_service: object, *, pickup_xy: tuple[float, float] | list[float], pickup_rz: float, pickup_base_pose: list[float], release_pose: list[float], workpiece_height_mm: float=0.0, release_label: str='release', resume_from_current_pose: bool=False, fixed_approach_pose: list[float] | None=None, fixed_position_tolerance_mm: float=2.0, fixed_orientation_tolerance_deg: float=1.0, magazine_pickup_mode: str=MAGAZINE_PICKUP_MODE_VISION_PLANNED) -> tuple[bool, str]
```

Pick up a resolved magazine target and release it at an explicit pose.

### `_execute_magazine_servo_contact_pickup_release`

```python
def _execute_magazine_servo_contact_pickup_release(executor, transfer_waypoints: tuple[tuple, ...], *, retract_reference_pose: list[float], release_label: str, expected_start_pose: list[float] | None=None, position_tolerance_mm: float=2.0, orientation_tolerance_deg: float=1.0) -> tuple[bool, str]
```

### `_prepare_magazine_release`

```python
def _prepare_magazine_release(executor, segments: list[dict], *, start_pose: list[float]) -> str | None
```

### `_discard_prepared_magazine_release`

```python
def _discard_prepared_magazine_release(executor, plan_id: str) -> None
```

### `_prepared_execution_succeeded`

```python
def _prepared_execution_succeeded(result: object) -> bool
```

### `_read_fresh_pose`

```python
def _read_fresh_pose(robot_service) -> list[float]
```

### `_verify_fixed_pickup_start_pose`

```python
def _verify_fixed_pickup_start_pose(robot_service, expected_pose: list[float], *, position_tolerance_mm: float, orientation_tolerance_deg: float, settle_timeout_s: float=0.5, poll_interval_s: float=0.025) -> tuple[bool, str]
```

### `_finite_pose`

```python
def _finite_pose(pose) -> list[float] | None
```

### `_wait_for_stable_pose`

```python
def _wait_for_stable_pose(robot_service, *, timeout_s: float=1.0, sample_interval_s: float=0.05, required_stable_samples: int=3, xyz_tolerance_mm: float=0.5, angular_tolerance_deg: float=0.2) -> list[float] | None
```

Confirm the Servo stop has physically settled before planning from it.

### `_wait_for_execution_inactive`

```python
def _wait_for_execution_inactive(robot_service, *, timeout_s: float=2.0, poll_interval_s: float=0.025, required_inactive_samples: int=2) -> bool
```

Wait for the backend to finish a nominally blocking approach request.

### `handle_magazine_execute_pickup_release`

```python
def handle_magazine_execute_pickup_release(ctx: PaintExecutionContext) -> PaintExecutionState
```

## `magazine_move_to_calibration_handler.py`

Source: [src/robot_systems/paint/processes/paint/workflow/handlers/magazine_load/magazine_move_to_calibration_handler.py](../../../../../../../../src/robot_systems/paint/processes/paint/workflow/handlers/magazine_load/magazine_move_to_calibration_handler.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `src.robot_systems.paint.processes.paint.workflow.context`, `src.robot_systems.paint.processes.paint.workflow.handlers.common.guards`, `src.robot_systems.paint.processes.paint.workflow.handlers.magazine_load.magazine_control`, `src.robot_systems.paint.processes.paint.workflow.state`.

### `handle_magazine_move_to_calibration`

```python
def handle_magazine_move_to_calibration(ctx: PaintExecutionContext) -> PaintExecutionState
```

## `magazine_move_to_magazine_handler.py`

Source: [src/robot_systems/paint/processes/paint/workflow/handlers/magazine_load/magazine_move_to_magazine_handler.py](../../../../../../../../src/robot_systems/paint/processes/paint/workflow/handlers/magazine_load/magazine_move_to_magazine_handler.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `logging`, `src.robot_systems.paint.processes.paint.configuration.models`, `src.robot_systems.paint.processes.paint.workflow.context`, `src.robot_systems.paint.processes.paint.workflow.handlers.common.guards`, `src.robot_systems.paint.processes.paint.workflow.handlers.magazine_load.magazine_control`, `src.robot_systems.paint.processes.paint.workflow.state`.

### `handle_magazine_move_to_magazine`

```python
def handle_magazine_move_to_magazine(ctx: PaintExecutionContext) -> PaintExecutionState
```

## `magazine_prepare_pickup_release_handler.py`

Source: [src/robot_systems/paint/processes/paint/workflow/handlers/magazine_load/magazine_prepare_pickup_release_handler.py](../../../../../../../../src/robot_systems/paint/processes/paint/workflow/handlers/magazine_load/magazine_prepare_pickup_release_handler.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `logging`, `src.robot_systems.paint.processes.paint.configuration.models`, `src.robot_systems.paint.processes.paint.workflow.context`, `src.robot_systems.paint.processes.paint.workflow.handlers.common.guards`, `src.robot_systems.paint.processes.paint.workflow.state`, `src.robot_systems.paint.processes.paint.results`, `time`.

### `handle_magazine_prepare_pickup_release`

```python
def handle_magazine_prepare_pickup_release(ctx: PaintExecutionContext) -> PaintExecutionState
```

## `magazine_wait_camera_settle_handler.py`

Source: [src/robot_systems/paint/processes/paint/workflow/handlers/magazine_load/magazine_wait_camera_settle_handler.py](../../../../../../../../src/robot_systems/paint/processes/paint/workflow/handlers/magazine_load/magazine_wait_camera_settle_handler.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `logging`, `src.robot_systems.paint.processes.paint.workflow.context`, `src.robot_systems.paint.processes.paint.workflow.handlers.common.guards`, `src.robot_systems.paint.processes.paint.workflow.handlers.magazine_load.magazine_control`, `src.robot_systems.paint.processes.paint.workflow.state`, `time`.

### `handle_magazine_wait_camera_settle`

```python
def handle_magazine_wait_camera_settle(ctx: PaintExecutionContext) -> PaintExecutionState
```
