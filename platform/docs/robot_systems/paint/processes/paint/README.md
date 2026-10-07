# Paint production package

This is the shared production implementation used by the paint family. System classes own storage, profile restrictions and runtime wiring; this package owns paint orchestration and its collaborators.

| Package/module | Responsibility |
|---|---|
| `paint_process.py` | Process state, background run, stop worker, manual/adjustment/retry entry points |
| `paint_production_service.py` | Capture, magazine/production flow and business execution-machine coordination |
| [production](production/README.md) | Shared execution of an already prepared cycle for production and editor entry points |
| `results.py` | Operation outcomes, actionable failure categories and exception boundaries |
| `config.py`, config service/serializer | Typed defaults, validated persisted configuration and runtime snapshots |
| [match](match/README.md) | Saved-workpiece candidate selection, matcher adapter and diagnostics |
| [align](align/README.md) | Raw contour payload IO, normalization and sampling helpers |
| [plan](plan/README.md) | Raw workpiece preparation, pickup transfer and paint-contact planning |
| [motion](motion/README.md) | Pose comparison, fresh-pose sampling and path geometry helpers |
| [execute](execute/README.md) | Path-executor facade, pickup/contact/motion/dropoff/cleanup collaborators and preview |
| [execution_machine](execution_machine/README.md) | Business states, context, transitions and per-phase handlers |
| [destination](destination/README.md) | Workpiece destination abstraction |
| [tray_dry](tray_dry/README.md) | Plate-layout reservations, occupancy and placement |
| [auto_dryer](auto_dryer/README.md) | Dryer release coordination |

`PaintWorkpiecePreparationService.prepare_result()` returns a typed prepared payload, `NoMatch`, or `Failed`. Only an actual absent match produces the established `Unknown workpiece` warning and permits operator recapture. Storage, conversion and unexpected matcher failures retain their category and stage and are displayed as preparation errors. A captured-contour fallback is still used when matching is disabled/unavailable. Reading live defaults can fail explicitly; stale defaults are no longer substituted after a read error. Shared path preparation converts the raw payload into a `WorkpieceExecutionPlan` before pickup/contact planning.

`results.py` defines immutable `PaintFailure` records, actionable `PaintOperationError`/`PaintPlanningError`/`PaintConfigurationError` exceptions, `Ready`/`Failed` planning variants, and `PaintOperationResult` with a validated `PaintOutcome`. Outcomes distinguish completion, absence, unmatched workpieces, cancellation, an inapplicable ordered attempt, full tray/work area and failure. A failed outcome must carry a failure; other outcomes cannot carry one. Backend error codes are preserved where the operation exposes them. Secondary cleanup failures retain the primary failure rather than replacing it. Codes describe failure categories; they do not authorize automatic motion retries.

Production uses `run_once_result()` and `run_cycle_result()`. The context stores one result; its legacy `result_ok` and `result_message` are read-only views. Completed cycles may carry a typed `stop_reason` for normal exhaustion or a full tray, so loop decisions and operator messages do not depend on message wording. A single-cycle absence still retains its prior unsuccessful legacy return; exhaustion in a repeating loop remains successful termination. Existing tuple-returning `run_once()`, editor matching, pickup/contact execution and single-cycle APIs remain compatibility adapters. The paint process exposes the latest operation or tray failure through `last_failure`.

Cooperative execution controls coordinate pause, resume and stop across the active context, magazine navigation and path execution. The business machine includes magazine phases, capture/prepare/plan, pickup, paint contact, edge cleanup, prepare/dropoff/post-return and lifecycle states. See [trajectory/execution](TRAJECTORY_AND_EXECUTION.md) for responsibilities and [alignment](ALIGNMENT.md) for the current geometry path.

`production.cycle_runner.run_paint_cycle()` builds and synchronously executes the business machine for an already prepared context. Production starts at `STARTING`; prepared-workpiece editor execution starts at `PICKUP`. Its immutable `PaintCycleExecution` reports the typed operation result and any framework error separately. Existing domain failures retain their category; a framework error without a domain failure becomes `INTERNAL`. Configuration, active-context tracking and caller-specific recovery stay with the entry points. Construction/execution exceptions propagate to their owners, and terminal handlers retain ownership of cycle resource restoration. This extraction does not add backend shutdown behavior.

`PaintProcess` prevents a new run until both the previous production worker and its hardware-stop worker have exited. Stop retains the existing `STOPPED` state while cleanup continues. Each run owns its cancellation event, so resetting the process cannot revive a cancelled run; late results from that run cannot change the current state. Normal starts, manual cycles, adjustment cycles and unmatched-workpiece retries share this restart restriction. Starting from `PAUSED` resumes the existing worker.

The dashboard disables Start during cleanup and enables it again on a subsequent status refresh after both workers exit. The process exposes `is_stopping` and `stopping_elapsed_seconds` for this feedback. Its Process Status details show a waiting message, or "Stopping is taking longer than expected." after ten seconds. That threshold only changes the message: it does not bypass cleanup or automatically restart. Robot-stop and intentional vacuum-off behavior remain unchanged. Regression coverage lives in `tests/robot_systems/paint/test_paint_process_lifecycle.py`.

Plate layout separates reservations from committed occupied records. Entry and exit command profiles are validated before entry motion or vacuum release; release verification remains intentionally disabled. Outlines support dashboard placement display; conservative footprints support allocation. Automatic-dryer coordination and tray dropoff are selected/configured at composition/runtime rather than duplicated into separate full process packages.

The current tree no longer has `align/alignment/core.py`, `align/dxf_image_placement.py` or `execute/pivot_projection/core.py`. Earlier descriptions are retained in [archive](../../../../archive/robot_systems/paint/processes/paint/README.md), not treated as current APIs.

<!-- source-navigation:start -->
## Source navigation

[Module reference](MODULES.md) — signatures, fields, imports and source links for every Python file in this directory.

[Resource reference](RESOURCES.md) — non-Python files and their formats; values remain in the owning storage/source files.

| Source subdirectory | Guide |
|---|---|
| `align/` | [align](align/README.md) |
| `auto_dryer/` | [auto_dryer](auto_dryer/README.md) |
| `destination/` | [destination](destination/README.md) |
| `execute/` | [execute](execute/README.md) |
| `execution_machine/` | [execution_machine](execution_machine/README.md) |
| `match/` | [match](match/README.md) |
| `motion/` | [motion](motion/README.md) |
| `plan/` | [plan](plan/README.md) |
| `production/` | [production](production/README.md) |
| `tray_dry/` | [tray_dry](tray_dry/README.md) |

[Complete source index](../../../../SOURCE_INDEX.md).
<!-- source-navigation:end -->
