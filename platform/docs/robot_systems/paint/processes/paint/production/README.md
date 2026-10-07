# Shared paint cycle execution

`run_paint_cycle(context, initial_state=STARTING)` builds and synchronously executes the paint business state machine. Production supplies a context prepared for capture and magazine operations; the editor supplies a prepared execution plan and starts at `PICKUP`.

The frozen `PaintCycleExecution` contains `result: PaintOperationResult` and `machine_error: str | None`. A recorded framework error preserves an existing domain failure, including its category and secondary cleanup failures. Without a domain failure, it produces an `INTERNAL` failure at `paint_cycle`. A normal execution returns the context's result, including cancellation. Framework error text remains separately available for entry-point recovery and the editor's existing tuple response.

The runner has no persistent state. It does not load settings, manage the production service's active context, select dropoff strategies, or launch/stop the backend. Construction and execution exceptions propagate to caller-owned `finally` blocks. Terminal handlers still own motion-session, reservation, brightness and live-view restoration; production retains its additional framework-error recovery.

Tests in `tests/robot_systems/paint/test_paint_cycle_runner.py` cover completion/cancellation, the prepared-workpiece initial state, preservation of actionable failures, uncategorized framework errors, and exception propagation. Production, execution-machine and editor suites cover integration behavior.

<!-- source-navigation:start -->
## Source navigation

[Module reference](MODULES.md) — signatures, fields, imports and source links for every Python file in this directory.

[Complete source index](../../../../../SOURCE_INDEX.md).
<!-- source-navigation:end -->
