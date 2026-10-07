# Module reference: `src/robot_systems/paint/processes/paint/production`

[Package guide](README.md) · [Complete source index](../../../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [cycle_runner.py](#cycle_runnerpy)

## `__init__.py`

Source: [src/robot_systems/paint/processes/paint/production/__init__.py](../../../../../../src/robot_systems/paint/processes/paint/production/__init__.py).

Production orchestration shared by process and prepared-workpiece entry points.

No top-level functions, classes or public value declarations; inspect the source for imports or entry-point statements.

## `cycle_runner.py`

Source: [src/robot_systems/paint/processes/paint/production/cycle_runner.py](../../../../../../src/robot_systems/paint/processes/paint/production/cycle_runner.py).

Run an already prepared paint cycle without owning caller-specific resources.

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `dataclasses`, `src.robot_systems.paint.processes.paint.execution_machine.context`, `src.robot_systems.paint.processes.paint.execution_machine.machine_factory`, `src.robot_systems.paint.processes.paint.execution_machine.state`, `src.robot_systems.paint.processes.paint.results`.

### `PaintCycleExecution`

```python
@dataclass(frozen=True)
class PaintCycleExecution:
```

Domain outcome and any framework error requiring caller-specific recovery. A framework error can accompany an existing domain failure; preserve that failure rather than replacing its actionable category with INTERNAL.

Declared fields/defaults:

```python
result: PaintOperationResult
machine_error: str | None = None
```

### `run_paint_cycle`

```python
def run_paint_cycle(context: PaintExecutionContext, *, initial_state: PaintExecutionState=PaintExecutionState.STARTING) -> PaintCycleExecution
```

Execute synchronously; configuration, active-context ownership and recovery stay with callers. Exceptions from construction or execution propagate so caller finally blocks still release their resources. Handler errors recorded by the state machine are returned alongside the typed domain result.
