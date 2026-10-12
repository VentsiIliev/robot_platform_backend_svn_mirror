# Paint diagnostics

See [platform diagnostics](../../engine/diagnostics/README.md) for deployment,
retention, persistence guarantees and support export.

Instrumentation follows the existing production and hardware boundaries:

| Area | Observations |
|---|---|
| Machine | Profile/version, startup, composed device presence, shutdown request |
| Production run | Attempts and typed final outcome, with expected stop reason |
| Execution cycle | Unique ID, effective process configuration and content fingerprint, requested operation, final outcome, failure code/stage/backend code and secondary failures |
| Execution substeps | Existing paint-contact, pickup, planning and cleanup timing blocks become persistent observations |
| Execution stage | Entry, next state, duration and exceptions, even when legacy timing reports are disabled |
| Vision | Paint capture attempts, contour count, capture duration; matched/unmatched/failed results, candidate count, selected stored workpiece and confidence when provided |
| Robot motion | Service call counts, duration, requested target and unsuccessful results; motion semantics are preserved |
| Paint head | Actual register target and verified readback, adjustment counts, duration and failures |
| Vacuum pump | Successful ON/OFF writes, commanded ON intervals/runtime, unknown states on failed writes |
| Fans | Separate main-fan and tray-fan writes, intervals/runtime and failures |
| Mechanical dryer | Command write acceptance, sequence attempts/result/duration and later eject-completion checks |

Magazine-only transfers, operator adjustment cycles and pickup-only operations use distinct metric names
from paint cycles. A completed operation is not a measurement of coating quality,
paint consumption or physical equipment wear. No heating or temperature metrics
exist.

The dryer release worker confirms next-position completion and eject START.
Its successful sequence result does not mean eject finished. Eject completion is
verified separately before a later dropoff. Disabled dryer bypass is not a
hardware fault. The originating cycle ID is retained in asynchronous events.

Terminal state and domain outcome are separate:

- `COMPLETED`: the requested operation succeeded.
- `FINISHED`: expected stop; `NO_WORKPIECE`, `UNMATCHED`, `TRAY_FULL` or
  `WORK_AREA_FULL` explains the reason.
- `STOPPED`: cancellation.
- `ERROR`: genuine failure, including a failed cleanup after an expected stop.

Continuous production can return `COMPLETED` with a stop reason when a batch
ends normally. Cycle counters come from individual cycle outcomes, not that
aggregate run outcome. Expected stops do not increment failure-code counters.
Existing operator popups continue to present clear guidance and unmatched
recapture; diagnostics collection does not perform additional hardware reads.

Logs outside an execution cycle, such as live camera-stream warnings and manual
commands, still carry the machine/session identity. Existing vision debug
artifacts remain separate; the support export currently includes logs and
statistics, not those image directories. There is no new statistics GUI in this
change; the report command is the service/support entry point.

Robot `unsuccessful_calls` includes safety rejection and cooperative cancellation;
it is not a hardware-fault count. Nested stage/substep durations overlap and
must not be summed as elapsed cycle time. Command acceptance is not physical
completion unless that operation explicitly waits and verifies it.
