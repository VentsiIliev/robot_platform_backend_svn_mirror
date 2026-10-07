# Module reference: `src/robot_systems/paint/processes/paint/execution_machine/handlers/common`

[Package guide](README.md) · [Complete source index](../../../../../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [guards.py](#guardspy)
- [motion_handlers.py](#motion_handlerspy)

## `__init__.py`

Source: [src/robot_systems/paint/processes/paint/execution_machine/handlers/common/__init__.py](../../../../../../../../src/robot_systems/paint/processes/paint/execution_machine/handlers/common/__init__.py).

Shared execution-machine handler helpers.

No top-level functions, classes or public value declarations; inspect the source for imports or entry-point statements.

## `guards.py`

Source: [src/robot_systems/paint/processes/paint/execution_machine/handlers/common/guards.py](../../../../../../../../src/robot_systems/paint/processes/paint/execution_machine/handlers/common/guards.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `src.robot_systems.paint.processes.paint.execution_machine.context`, `src.robot_systems.paint.processes.paint.execution_machine.state`, `src.robot_systems.paint.processes.paint.results`.

### `guard_control`

```python
def guard_control(ctx: PaintExecutionContext, state: PaintExecutionState) -> PaintExecutionState | None
```

Return a terminal/paused state when cooperative process control requires it.

## `motion_handlers.py`

Source: [src/robot_systems/paint/processes/paint/execution_machine/handlers/common/motion_handlers.py](../../../../../../../../src/robot_systems/paint/processes/paint/execution_machine/handlers/common/motion_handlers.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `contextlib`, `logging`, `math`, `src.robot_systems.paint.processes.paint.execute.diagnostics`, `src.robot_systems.paint.processes.paint.execution_machine.context`, `src.robot_systems.paint.processes.paint.execution_machine.handlers.common.guards`, `src.robot_systems.paint.processes.paint.execution_machine.state`, `src.robot_systems.paint.processes.paint.results`, `src.robot_systems.paint.timing`, `time`.

### `unwind_joint6_at_cycle_start`

```python
def unwind_joint6_at_cycle_start(ctx: PaintExecutionContext) -> bool
```

Recover J6 once per cycle before any production navigation starts.

### `_wait_for_unwind_motion_idle`

```python
def _wait_for_unwind_motion_idle(robot_service, *, timeout_s: float=2.0) -> bool
```

Wait through the blocking-response/websocket-inactive handoff.

### `start_paint_motion_if_needed`

```python
def start_paint_motion_if_needed(ctx: PaintExecutionContext) -> None
```

### `wait_or_guard`

```python
def wait_or_guard(ctx: PaintExecutionContext, state: PaintExecutionState) -> PaintExecutionState | None
```

### `fail_paint_motion`

```python
def fail_paint_motion(ctx: PaintExecutionContext, message: str) -> None
```

### `motion_failure_message`

```python
def motion_failure_message(robot_service, fallback: str) -> str
```

Return the latest backend command error without hiding it behind a result code.

### `set_paint_result`

```python
def set_paint_result(ctx: PaintExecutionContext, ok: bool, message: str, *, already_prefixed: bool=False) -> None
```

### `_post_return_failure_result`

```python
def _post_return_failure_result(result_ok: bool, result_message: str) -> tuple[bool, str]
```

### `post_return_failure_result`

```python
def post_return_failure_result(result_ok: bool, result_message: str) -> tuple[bool, str]
```

### `finish_paint_motion`

```python
def finish_paint_motion(ctx: PaintExecutionContext, *, success: bool) -> None
```
