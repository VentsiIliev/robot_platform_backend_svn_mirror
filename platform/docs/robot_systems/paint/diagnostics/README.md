# Paint diagnostics

`artifacts.py` owns debug plots, dumps, and motion tracing. `trajectory.py` instruments trajectory execution and exports; it is not the workflow coordinator. `trajectory_export_result.py` defines typed export outcomes.

`write_platform_command_path_csv()` queues optional trajectory diagnostics and always returns a `Future[ExportResult]`. Its result is `ExportWritten` (completed artifact paths), `ExportSkipped` (empty command path), or `ExportFailed` (failure code, execution stage, export phase, message and completed artifact paths). A failed export may leave partial files; only fully completed artifacts are reported. The optional before/after plot is omitted when its input is insufficient.

Snapshot and submission failures are converted to completed failure futures, so optional diagnostics cannot interrupt the motion caller. `INVALID_INPUT`, `FILESYSTEM` and executor `UNAVAILABLE` failures are warnings; unexpected `INTERNAL` failures retain error-level tracebacks. Failures are logged even when the motion caller ignores the future. Consumers that need to act on the result should observe completion without waiting in the motion thread. This policy applies to optional trajectory exports only; required production artifacts such as workpiece thumbnails retain their fail-on-error behavior. Process interrupts are not swallowed.

`PaintCollisionInterlockMonitor` observes the backend's global collision interlock independently of whether the paint process is running. An active collision turns the vacuum pump off and presents the operator acknowledgement dialog. Keeping motion held closes the dialog without clearing the backend latch; releasing the hold calls the backend reset workflow. Recovery Jog is a separate, deliberately constrained operation: while it is enabled, ordinary paint motion stays interlocked and only explicitly marked recovery jog requests may move the robot.


[Module reference](MODULES.md).
