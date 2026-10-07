# Module reference: `src/robot_systems/paint/processes/paint/execution_machine/handlers/workflow`

[Package guide](README.md) · [Complete source index](../../../../../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [capture_handler.py](#capture_handlerpy)
- [edge_cleanup_handler.py](#edge_cleanup_handlerpy)
- [execution_handler.py](#execution_handlerpy)
- [paint_contact_handler.py](#paint_contact_handlerpy)
- [pickup_handler.py](#pickup_handlerpy)
- [plan_handler.py](#plan_handlerpy)
- [preparation_handler.py](#preparation_handlerpy)

## `__init__.py`

Source: [src/robot_systems/paint/processes/paint/execution_machine/handlers/workflow/__init__.py](../../../../../../../../src/robot_systems/paint/processes/paint/execution_machine/handlers/workflow/__init__.py).

Main paint workflow execution-machine handlers.

No top-level functions, classes or public value declarations; inspect the source for imports or entry-point statements.

## `capture_handler.py`

Source: [src/robot_systems/paint/processes/paint/execution_machine/handlers/workflow/capture_handler.py](../../../../../../../../src/robot_systems/paint/processes/paint/execution_machine/handlers/workflow/capture_handler.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `logging`, `src.robot_systems.paint.processes.paint.execution_machine.context`, `src.robot_systems.paint.processes.paint.execution_machine.handlers.common.guards`, `src.robot_systems.paint.processes.paint.execution_machine.state`, `src.robot_systems.paint.processes.paint.plan`, `src.robot_systems.paint.processes.paint.results`, `time`.

### `handle_capture_workpiece`

```python
def handle_capture_workpiece(ctx: PaintExecutionContext) -> PaintExecutionState
```

## `edge_cleanup_handler.py`

Source: [src/robot_systems/paint/processes/paint/execution_machine/handlers/workflow/edge_cleanup_handler.py](../../../../../../../../src/robot_systems/paint/processes/paint/execution_machine/handlers/workflow/edge_cleanup_handler.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `logging`, `src.robot_systems.paint.processes.paint.execute.diagnostics`, `src.robot_systems.paint.processes.paint.execution_machine.context`, `src.robot_systems.paint.processes.paint.execution_machine.handlers.common.motion_handlers`, `src.robot_systems.paint.processes.paint.execution_machine.state`.

### `handle_edge_cleanup`

```python
def handle_edge_cleanup(ctx: PaintExecutionContext) -> PaintExecutionState
```

## `execution_handler.py`

Source: [src/robot_systems/paint/processes/paint/execution_machine/handlers/workflow/execution_handler.py](../../../../../../../../src/robot_systems/paint/processes/paint/execution_machine/handlers/workflow/execution_handler.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `src.robot_systems.paint.processes.paint.execution_machine.context`, `src.robot_systems.paint.processes.paint.execution_machine.handlers.common.guards`, `src.robot_systems.paint.processes.paint.execution_machine.state`, `time`.

### `handle_execute_paint`

```python
def handle_execute_paint(ctx: PaintExecutionContext) -> PaintExecutionState
```

## `paint_contact_handler.py`

Source: [src/robot_systems/paint/processes/paint/execution_machine/handlers/workflow/paint_contact_handler.py](../../../../../../../../src/robot_systems/paint/processes/paint/execution_machine/handlers/workflow/paint_contact_handler.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `logging`, `src.robot_systems.paint.processes.paint.execute.diagnostics`, `src.robot_systems.paint.processes.paint.execute.incremental_paint_executor`, `src.robot_systems.paint.processes.paint.execution_machine.context`, `src.robot_systems.paint.processes.paint.execution_machine.handlers.common.motion_handlers`, `src.robot_systems.paint.processes.paint.execution_machine.state`, `src.robot_systems.paint.processes.paint.results`.

### `handle_paint_contact`

```python
def handle_paint_contact(ctx: PaintExecutionContext) -> PaintExecutionState
```

## `pickup_handler.py`

Source: [src/robot_systems/paint/processes/paint/execution_machine/handlers/workflow/pickup_handler.py](../../../../../../../../src/robot_systems/paint/processes/paint/execution_machine/handlers/workflow/pickup_handler.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `cv2`, `logging`, `numpy`, `src.engine.robot.motion_sequence`, `src.robot_systems.paint.processes.paint.config`, `src.robot_systems.paint.processes.paint.execute.pickup_executor`, `src.robot_systems.paint.processes.paint.execution_machine.context`, `src.robot_systems.paint.processes.paint.execution_machine.handlers.common.motion_handlers`, `src.robot_systems.paint.processes.paint.execution_machine.handlers.dropoff.dropoff_handlers`, `src.robot_systems.paint.processes.paint.execution_machine.handlers.magazine_load.magazine_execute_pickup_release_handler`, `src.robot_systems.paint.processes.paint.execution_machine.state`, `src.robot_systems.paint.processes.paint.paint_contact_job`, `src.robot_systems.paint.processes.paint.results`, `src.robot_systems.paint.timing`.

### `handle_pickup`

```python
def handle_pickup(ctx: PaintExecutionContext) -> PaintExecutionState
```

### `_dropoff_strategy`

```python
def _dropoff_strategy(executor: object) -> DropoffStrategy
```

### `_reserve_plate_dropoff`

```python
def _reserve_plate_dropoff(ctx, executor, pickup_plan) -> PaintOperationResult
```

### `_workpiece_footprint_mm`

```python
def _workpiece_footprint_mm(execution_plan) -> tuple[float, float]
```

Return canonical min-rectangle sides as long-side width and short-side height.

### `_paint_pass_metadata`

```python
def _paint_pass_metadata(execution_plan, config, executor) -> tuple[dict, ...]
```

Capture the configured paint controls used by each production pass.

### `_workpiece_layout_geometry`

```python
def _workpiece_layout_geometry(execution_plan) -> tuple[float, float, tuple[tuple[tuple[float, float], ...], ...]]
```

Return footprint and execution paths projected into its local rectangle.

### `try_execute_ordered_pickup_and_paint_contact`

```python
def try_execute_ordered_pickup_and_paint_contact(executor: object, prepared_workpiece, *, pickup_plan=None) -> tuple[bool, str, int] | None
```

Legacy adapter; production uses the typed ordered-attempt result.

### `execute_ordered_pickup_and_paint_contact_result`

```python
def execute_ordered_pickup_and_paint_contact_result(executor: object, prepared_workpiece, *, pickup_plan=None) -> PaintOperationResult
```

Execute pickup/staging and primary paint contact as one preplanned ordered chain.

### `_should_preplan_dropoff_in_ordered_chain`

```python
def _should_preplan_dropoff_in_ordered_chain(executor: object) -> bool
```

Keep plate travel/unwind in PREPARE_DROPOFF after paint completes.

### `build_ordered_second_pass_segments`

```python
def build_ordered_second_pass_segments(paint_paths: list[list[list[float]]], paint_jobs: list[PaintContactCommandJob], config) -> list[OrderedMotionCommand]
```

Build the guarded unwind, re-attach, and contact sequence for pass two.

### `_unmatched_second_pass_requested`

```python
def _unmatched_second_pass_requested(executor: object, execution_plan: object) -> bool
```

## `plan_handler.py`

Source: [src/robot_systems/paint/processes/paint/execution_machine/handlers/workflow/plan_handler.py](../../../../../../../../src/robot_systems/paint/processes/paint/execution_machine/handlers/workflow/plan_handler.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `logging`, `src.robot_systems.paint.processes.paint.execution_machine.context`, `src.robot_systems.paint.processes.paint.execution_machine.state`, `src.robot_systems.paint.processes.paint.results`, `time`.

### `handle_build_execution_plan`

```python
def handle_build_execution_plan(ctx: PaintExecutionContext) -> PaintExecutionState
```

### `_path_executor_supports_motion_states`

```python
def _path_executor_supports_motion_states(path_executor: object) -> bool
```

## `preparation_handler.py`

Source: [src/robot_systems/paint/processes/paint/execution_machine/handlers/workflow/preparation_handler.py](../../../../../../../../src/robot_systems/paint/processes/paint/execution_machine/handlers/workflow/preparation_handler.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `src.robot_systems.paint.processes.paint.execution_machine.context`, `src.robot_systems.paint.processes.paint.execution_machine.state`, `src.robot_systems.paint.processes.paint.match.results`, `src.robot_systems.paint.processes.paint.plan`, `src.robot_systems.paint.processes.paint.results`, `time`.

### `handle_prepare_workpiece`

```python
def handle_prepare_workpiece(ctx: PaintExecutionContext) -> PaintExecutionState
```

### `_cycle_default_paint_settings`

```python
def _cycle_default_paint_settings(ctx: PaintExecutionContext) -> dict | None
```
