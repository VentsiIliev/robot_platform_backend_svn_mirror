# Module reference: `src/robot_systems/paint/processes/paint/execution_machine/handlers/lifecycle`

[Package guide](README.md) · [Complete source index](../../../../../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [completed_handler.py](#completed_handlerpy)
- [error_handler.py](#error_handlerpy)
- [idle_handler.py](#idle_handlerpy)
- [pause_handler.py](#pause_handlerpy)
- [startup_handler.py](#startup_handlerpy)
- [stopped_handler.py](#stopped_handlerpy)
- [terminal_common.py](#terminal_commonpy)

## `__init__.py`

Source: [src/robot_systems/paint/processes/paint/execution_machine/handlers/lifecycle/__init__.py](../../../../../../../../src/robot_systems/paint/processes/paint/execution_machine/handlers/lifecycle/__init__.py).

Lifecycle and terminal execution-machine handlers.

No top-level functions, classes or public value declarations; inspect the source for imports or entry-point statements.

## `completed_handler.py`

Source: [src/robot_systems/paint/processes/paint/execution_machine/handlers/lifecycle/completed_handler.py](../../../../../../../../src/robot_systems/paint/processes/paint/execution_machine/handlers/lifecycle/completed_handler.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `src.robot_systems.paint.processes.paint.execution_machine.context`, `src.robot_systems.paint.processes.paint.execution_machine.handlers.lifecycle.terminal_common`, `src.robot_systems.paint.processes.paint.execution_machine.state`.

### `handle_completed`

```python
def handle_completed(ctx: PaintExecutionContext) -> PaintExecutionState
```

## `error_handler.py`

Source: [src/robot_systems/paint/processes/paint/execution_machine/handlers/lifecycle/error_handler.py](../../../../../../../../src/robot_systems/paint/processes/paint/execution_machine/handlers/lifecycle/error_handler.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `src.robot_systems.paint.processes.paint.execution_machine.context`, `src.robot_systems.paint.processes.paint.execution_machine.handlers.lifecycle.terminal_common`, `src.robot_systems.paint.processes.paint.execution_machine.state`.

### `handle_error`

```python
def handle_error(ctx: PaintExecutionContext) -> PaintExecutionState
```

## `idle_handler.py`

Source: [src/robot_systems/paint/processes/paint/execution_machine/handlers/lifecycle/idle_handler.py](../../../../../../../../src/robot_systems/paint/processes/paint/execution_machine/handlers/lifecycle/idle_handler.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `src.robot_systems.paint.processes.paint.execution_machine.context`, `src.robot_systems.paint.processes.paint.execution_machine.state`.

### `handle_idle`

```python
def handle_idle(ctx: PaintExecutionContext) -> PaintExecutionState
```

## `pause_handler.py`

Source: [src/robot_systems/paint/processes/paint/execution_machine/handlers/lifecycle/pause_handler.py](../../../../../../../../src/robot_systems/paint/processes/paint/execution_machine/handlers/lifecycle/pause_handler.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `logging`, `src.robot_systems.paint.processes.paint.execution_machine.context`, `src.robot_systems.paint.processes.paint.execution_machine.state`, `src.robot_systems.paint.processes.paint.results`.

### `handle_paused`

```python
def handle_paused(ctx: PaintExecutionContext) -> PaintExecutionState
```

## `startup_handler.py`

Source: [src/robot_systems/paint/processes/paint/execution_machine/handlers/lifecycle/startup_handler.py](../../../../../../../../src/robot_systems/paint/processes/paint/execution_machine/handlers/lifecycle/startup_handler.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `src.robot_systems.paint.processes.paint.execution_machine.context`, `src.robot_systems.paint.processes.paint.execution_machine.handlers.common.motion_handlers`, `src.robot_systems.paint.processes.paint.execution_machine.state`, `src.robot_systems.paint.processes.paint.results`.

### `handle_starting`

```python
def handle_starting(ctx: PaintExecutionContext) -> PaintExecutionState
```

Choose the first production phase for this cycle.

## `stopped_handler.py`

Source: [src/robot_systems/paint/processes/paint/execution_machine/handlers/lifecycle/stopped_handler.py](../../../../../../../../src/robot_systems/paint/processes/paint/execution_machine/handlers/lifecycle/stopped_handler.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `src.robot_systems.paint.processes.paint.execution_machine.context`, `src.robot_systems.paint.processes.paint.execution_machine.handlers.lifecycle.terminal_common`, `src.robot_systems.paint.processes.paint.execution_machine.state`, `src.robot_systems.paint.processes.paint.results`.

### `handle_stopped`

```python
def handle_stopped(ctx: PaintExecutionContext) -> PaintExecutionState
```

## `terminal_common.py`

Source: [src/robot_systems/paint/processes/paint/execution_machine/handlers/lifecycle/terminal_common.py](../../../../../../../../src/robot_systems/paint/processes/paint/execution_machine/handlers/lifecycle/terminal_common.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `dataclasses`, `src.robot_systems.paint.processes.paint.execution_machine.context`, `src.robot_systems.paint.processes.paint.execution_machine.handlers.common.motion_handlers`, `src.robot_systems.paint.processes.paint.results`.

### `restore_cycle_resources`

```python
def restore_cycle_resources(ctx: PaintExecutionContext, *, defer_for_next_capture: bool=False) -> None
```

### `stop_machine`

```python
def stop_machine(ctx: PaintExecutionContext) -> None
```
