# Module reference: `src/robot_systems/paint/processes/paint/production`

[Package guide](README.md). Generated from source ASTs; no runtime imports.

## `__init__.py`

[Source](../../../../../../src/robot_systems/paint/processes/paint/production/__init__.py).


## `cycle_runner.py`

[Source](../../../../../../src/robot_systems/paint/processes/paint/production/cycle_runner.py).

- `PaintCycleExecution`: Domain outcome and any framework error requiring caller-specific recovery.
- `run_paint_cycle`: Execute synchronously; configuration, active-context ownership and recovery stay with callers.

## `execution_control.py`

[Source](../../../../../../src/robot_systems/paint/processes/paint/production/execution_control.py).

- `PaintExecutionControl`: Cooperative pause/resume state for a single paint execution run.

## `execution_dependencies.py`

[Source](../../../../../../src/robot_systems/paint/processes/paint/production/execution_dependencies.py).

- `PaintExecutorDependencies`: Runtime services and callbacks needed by the paint process executor.
- `PaintExecutorMotionConfig`: Robot tool/user and process-motion switches for paint execution.
- `PaintExecutorContactMotionConfig`: Configured pivot plane/profile used by paint projection and pickup handoff.

## `execution_runtime.py`

[Source](../../../../../../src/robot_systems/paint/processes/paint/production/execution_runtime.py).

- `PaintExecutionRuntime`: Own execution state and compose operations for a paint cycle.

## `prepared_cycle.py`

[Source](../../../../../../src/robot_systems/paint/processes/paint/production/prepared_cycle.py).

- `_PreparedPaintProcessAdapter`: Minimal production-service shape for editor execution of an already prepared plan.
- `run_prepared_paint_cycle`: Run a prepared workpiece plan through the paint execution state machine.

## `service.py`

[Source](../../../../../../src/robot_systems/paint/processes/paint/production/service.py).

- `PaintProductionService`: Own the end-to-end paint production flow outside the editor UI.
