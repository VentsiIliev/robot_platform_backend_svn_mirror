# Paint execution runtime and cycles

Production/cycle diagnostics now create an outer request boundary before settings
or readiness checks. Operation identity is inherited from the caller or allocated
with an explicit unknown actor. Each cycle request allocates its ID before an
execution context exists. Prepared contexts retain these identities and engine
snapshot references; a failed new preparation cannot reuse the preceding part's
failure-register/bundle ownership. See [Paint diagnostics](../../../diagnostics/README.md)
for the snapshot format, event meanings, limits and export guarantees.

`execution_dependencies.py` declares composition inputs. `PaintExecutionRuntime` in `execution_runtime.py` owns per-execution state, runtime configuration, and operation composition. It no longer implements the editor interface; the editor adapter owns that contract.

`prepared_cycle.py` adapts an already prepared workpiece to the shared cycle runner. Both editor-triggered execution and production use the same workflow, preserving typed outcomes, cleanup, and motion behavior.

`run_paint_cycle(context, initial_state=STARTING)` builds and synchronously executes the paint business state machine. Production supplies a context prepared for capture and magazine operations; the editor supplies a prepared execution plan and starts at `PICKUP`.

The frozen `PaintCycleExecution` contains `result: PaintOperationResult` and `machine_error: str | None`. A recorded framework error preserves an existing domain failure, including its category and secondary cleanup failures. Without a domain failure, it produces an `INTERNAL` failure at `paint_cycle`. A normal execution returns the context's result, including cancellation. Framework error text remains separately available for entry-point recovery and the editor's existing tuple response.

The runner has no persistent state. It does not load settings, manage the production service's active context, select dropoff strategies, or launch/stop the backend. Construction and execution exceptions propagate to caller-owned `finally` blocks. Terminal handlers still own motion-session, reservation, brightness and live-view restoration; production retains its additional framework-error recovery.

Tests in `tests/robot_systems/paint/test_paint_cycle_runner.py` cover completion/cancellation, the prepared-workpiece initial state, preservation of actionable failures, uncategorized framework errors, and exception propagation. Production, execution-machine and editor suites cover integration behavior.

<!-- source-navigation:start -->
## Source navigation

[Module reference](MODULES.md) — signatures, fields, imports and source links for every Python file in this directory.

[Complete source index](../../../../../SOURCE_INDEX.md).
<!-- source-navigation:end -->

`prepare_projection_context()` exposes planning inputs and shared coordinate-transform hooks. Preview generation belongs to the system-level visualization provider, not to the execution runtime.

## Production services

`service.py` owns manual, magazine, and batch repetition, active-context ownership, and capture-view cleanup. `execution_control.py` coordinates pause/resume/stop. `src/robot_systems/paint/contracts/next_cycle_target.py` defines validated prepositioning data. Magazine transfer support lives in `magazine/`. The package also holds the runtime and complete-cycle runners used by both production and editor actions.

## Dropoff lifecycle injection

The runtime delegates preparation and release through `IDropoffStrategy`; workflow/operation consumers also use its cycle reservation, approach, handoff, and finalization hooks. `dropoff_strategy_factory` is a required composition input. The factory runs once after initialization; the process runtime never chooses a concrete lifecycle implementation. The default paint wiring supplies `ConfiguredDropoffStrategy`, which preserves cycle strategy overrides and alternating drying.
