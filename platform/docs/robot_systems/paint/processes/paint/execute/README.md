# Paint execution collaborators

`PaintWorkpiecePathExecutor` is the facade implementing the shared editor path-execution contract. It resolves live config, targeting/poses and preview data, and delegates pickup, contact painting, robot motion, edge cleanup and dropoff to separate executors. This layer can issue robot/peripheral operations; it is not data-only geometry.

Prepared-workpiece execution prepares its context and delegates machine construction/execution to [the shared cycle runner](../production/README.md), starting at `PICKUP`. The editor's `(bool, str)` contract is preserved, including the framework error message when machine execution records an error. Production uses the same runner with its own preparation and recovery rules.

`execution_plane/` supplies plane strategies; `projection_preview.py` produces editor overlays/snapshots. `paint_debug_artifacts.py` and `diagnostics.py` support diagnostics. Planning data arrives from `plan/` and shared engine path preparation; business phase sequencing is owned by the production execution machine.

Pickup `build_plan_result()` returns `Ready[PickupPlan]` or `Failed`; `execute_result()` distinguishes completed pickup, no workpiece, cancellation and failure. Plans reference `PickupTransferPlan` and `PickupContactMode`. Unsupported height measurement is an unavailable capability; invalid modes/indexes are rejected before vacuum or motion. Vacuum failure messages are retained. `PaintContactExecutor.execute_result()` returns a typed outcome and planned waypoint count, preserving numeric backend errors when available. Existing `build_plan()`/`execute()` methods adapt results for legacy consumers.

Incremental adjustment uses `AdjustmentPhase`, named snapshots and separate `NextPaintSection`, `FinishAdjustment` and `CancelAdjustment` commands. A next-section command requires a validated step. Its typed contact entry point reports cancellation separately from planning and motion failures; operator pacing and the explicit Finish requirement are unchanged.

Pause/stop checks, fresh-pose confirmation, ordering of vacuum/contact/retract moves and failure propagation are part of execution semantics. Consult the source-backed signatures and guide before changing these contracts. Preview/diagnostic output does not establish that hardware reached a target.

`write_platform_command_path_csv()` queues optional trajectory diagnostics and always returns a `Future[ExportResult]`. Its result is `ExportWritten` (completed artifact paths), `ExportSkipped` (empty command path), or `ExportFailed` (failure code, execution stage, export phase, message and completed artifact paths). A failed export may leave partial files; only fully completed artifacts are reported. The optional before/after plot is omitted when its input is insufficient.

Snapshot and submission failures are converted to completed failure futures, so optional diagnostics cannot interrupt the motion caller. `INVALID_INPUT`, `FILESYSTEM` and executor `UNAVAILABLE` failures are warnings; unexpected `INTERNAL` failures retain error-level tracebacks. Failures are logged even when the motion caller ignores the future. Consumers that need to act on the result should observe completion without waiting in the motion thread. This policy applies to optional trajectory exports only; required production artifacts such as workpiece thumbnails retain their fail-on-error behavior. Process interrupts are not swallowed.

<!-- source-navigation:start -->
## Source navigation

[Module reference](MODULES.md) — signatures, fields, imports and source links for every Python file in this directory.

| Source subdirectory | Guide |
|---|---|
| `execution_plane/` | [execution_plane](execution_plane/README.md) |

[Complete source index](../../../../../SOURCE_INDEX.md).
<!-- source-navigation:end -->
