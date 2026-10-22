# Paint diagnostics

Paint composition injects the bootstrap action recorder into its shared Robot
Settings service. Shell navigation, settings-tab selection and collision
active-response edits/Save outcomes now carry the operator identity and action
correlation. These events use the engine history; the existing failure register
and bundles remain separate evidence. Restart the platform to activate new hooks.
The standalone viewer (`python -m src.applications.diagnostics`) can inspect the
machine history or a selected legacy diagnostics folder without starting paint.

## Operator-to-cycle history

The dashboard allocates an actor/action/operation token before dry-run confirmation,
settings loading and destination/tray checks. It records cancellation, rejection,
exceptions and process acceptance separately. `PaintProcess.start_with_diagnostics`
reports admission under the existing process lock; a returned Start call alone
does not establish admission or completion. Its normal `start()` contract is retained.
Lazy dashboard composition binds the bootstrap recorder after login exists.

The worker captures the initiating context and retains it after session changes.
The same run context reaches collision and hardware-stop workers; existing dryer
workers inherit it through their existing context propagation. Each requested cycle
gets its identity before configuration/readiness preparation. Outer
`paint.production.*` and `paint.cycle.request_*` records cover early exits, and
`paint.cycle.started/ended`, stage and run events cover execution. A process can
reject a request without creating a run. Unexpected exceptions retain their traceback;
observations do not replace the domain result or prevent cleanup.

Every executed cycle submits raw and effective process-settings snapshots before
handlers start. Workpiece preparation publishes its selected identity, description,
top-level motion/default settings and dry-run placement before planning can mutate
them. Planning publishes job count, bounded scalar/job settings and planned waypoint
count. The limits and digest/chunk format belong to the generic engine evidence
module. Job metadata is capped at 64 jobs; geometry and images are explicitly outside
these inline contributions. Existing failure bundles/registers additionally carry
the operation context and snapshot references. Failed new preparations clear the
previous part/bundle owner and retain the new request identity.

Select an event from the new run in the desktop viewer and click **Export incident**.
The archive joins the retained operation and reconstructs complete inline snapshots,
reporting missing/partial evidence. It is best effort over retained files, capped at
500 matching events; it does not establish complete history across retention/loss.
Older uncorrelated events fall back to the current filters. Restart the platform
and viewer to activate these changes.

Acceptance tests run real process/workflow/recorder/export wiring with mocked
hardware, covering successful/failed cycles, settings and tray failures, missing
services, preparation-worker errors, session changes and optional-evidence failure.
These tests do not validate physical machine behavior. Other Start entry points,
all operator controls, backend task correlation, images/geometry, historical sensor
coverage, indexed history and durable publication receipts remain later gates.

`artifacts.py` owns debug plots, dumps, and motion tracing. `trajectory.py` instruments trajectory execution and exports; it is not the workflow coordinator. `trajectory_export_result.py` defines typed export outcomes.

`write_platform_command_path_csv()` queues optional trajectory diagnostics and always returns a `Future[ExportResult]`. Its result is `ExportWritten` (completed artifact paths), `ExportSkipped` (empty command path or exhausted work budget), or `ExportFailed` (failure code, execution stage, export phase, message and completed artifact paths). A failed export may leave partial files; only fully completed artifacts are reported. The optional before/after plot is omitted when its input is insufficient.

Trajectory export and Cartesian-path analysis each admit at most two running/queued
jobs and 100,000 total point rows, before copying caller data. Pipeline exports
allow at most sixteen paths; points use at most six primitive numeric coordinates.
Reservations cover snapshot preparation and release on completion, submission/
snapshot failure or cancellation. Budget refusal records `diagnostics.artifact.skipped`
through the engine recorder; export callers also receive `ExportSkipped`.
These limits bound optional work and do not modify robot commands. Full executor
lifecycle/shutdown ownership remains part of the observability hardening plan.

Snapshot and submission failures are converted to completed failure futures, so optional diagnostics cannot interrupt the motion caller. `INVALID_INPUT`, `FILESYSTEM` and executor `UNAVAILABLE` failures are warnings; unexpected `INTERNAL` failures retain error-level tracebacks. Failures are logged even when the motion caller ignores the future. Consumers that need to act on the result should observe completion without waiting in the motion thread. This policy applies to optional trajectory exports only; required production artifacts such as workpiece thumbnails retain their fail-on-error behavior. Process interrupts are not swallowed.

`PaintCollisionInterlockMonitor` observes the backend's global collision interlock independently of whether the paint process is running. An active collision turns the vacuum pump off and presents the operator acknowledgement dialog. Keeping motion held closes the dialog without clearing the backend latch; releasing the hold calls the backend reset workflow. Recovery Jog is a separate, deliberately constrained operation: while it is enabled, ordinary paint motion stays interlocked and only explicitly marked recovery jog requests may move the robot.


The dashboard's consecutive-cycle counter counts full successful paint cycles for the current application session. Normal stops and dashboard navigation preserve it; a process failure resets it. The state machine's internal terminal stop flag is also set on success, so counting uses the typed completion outcome and production cancellation control instead.

Failed production runs and external process faults append a record to the active system's `storage/diagnostics/failure_register.jsonl`. For the tray-dry variant in this checkout, the file is `src/robot_systems/paint_tray_dry/storage/diagnostics/failure_register.jsonl`. The file is created on the first failure and retained across app restarts. Each line is an independent JSON object containing the UTC timestamp, run/cycle IDs, cycle index, completed-cycle streak before reset, failure message and structured failure, original cycle failure, backend collision event when available, and the detailed `paint_failures/.../failure_bundle.json` path when saved. These are reported errors and backend evidence, not a verified physical root cause. Normal stops, empty magazines and other expected outcomes do not create failure entries. Repeated notifications while the process remains in ERROR do not create another entry.

Register writes happen after requesting the fault stop and outside process/state locks. File-system errors are logged without changing fault handling. Diagnostics are best-effort; an abrupt power loss or inability to write storage may leave an incident unrecorded. Existing failure bundles remain available independently of this register.

New register entries include a `workpiece` object with the part ID, prepared workpiece ID, name and description. Dry-run entries use the dataset's part ID instead of the generic `captured` ID and include compact magazine/paint placement metadata: manifest, zero-based dataset index, shape, dimensions, original size, fit scale, angle, center and work area. Magazine metadata can identify a part even before paint capture. Unknown parts are recorded as `null`; contour arrays remain in the detailed bundle. Historical entries are unchanged.

[Module reference](MODULES.md).
