# Runtime endpoint flows

The [REST route inventory](REST_API.md) lists the current methods/paths.
Every HTTP business operation enters one of four API groups, then the
`RuntimeGateway`; the installed local implementation owns backend/service access.
The [historical flow snapshot](API_ENDPOINT_FLOWS_LEGACY.md) retains older detailed
examples, which must not be used as current response/status contracts.

## Startup and state

`main.py` starts HTTP with an asynchronous runtime initializer. HTTP and all three
WebSocket servers run in the same runtime process. `/health`, `/startup/status`,
`/docs`, `/api/docs`, `/openapi.json` and configuration routes are available while
robot/node initialization is pending. Configuration reads show saved values even
when runtime observation/application is unavailable. Other business routes return
503 until both robot and node exist. Motion readiness is checked separately.

State routes call `StateApi` → gateway → cached/measured backend state. Partial
snapshot/kinematics responses can return 206 with `unavailable_fields`; they do not
prove the hardware is ready. State, execution and sensor WebSockets have separate
stream implementations under `runtime_websockets/`, on configured listeners.
They do not acquire the HTTP response envelope automatically.

## Motion submission

1. `rest/routes/motion.py` reads JSON and calls `MotionApi`.
2. `motion/requests.py` validates and normalizes fields using injected defaults.
3. The API invokes the gateway. The local gateway delegates to the backend,
   which applies frame/tool context and calls the controller/coordinator.
4. The coordinator rejects, starts or queues the request. Planning/optimization
   precede FollowJointTrajectory execution; planner/controller faults retain
   their specific cause alongside the legacy integer result.
5. The API maps acceptance to 202 (`accepted: true`, `final: false`) or a blocking
   completion to 200 (`final: true`). Execution state supplies the final outcome
   for asynchronous work. A task ID or an accepted response is not physical success.

Sequence and ordered-chain requests preserve ordered segments through their
respective backend operations. Preparing an ordered chain creates a plan; it does
not execute it. StateApi queries a prepared plan; MotionApi executes or discards
it. See [ordered motion chains](ORDERED_MOTION_CHAIN_BG.md) and live OpenAPI for
segment schemas, IDs and preparation constraints.

`/reachability/pose` validates endpoint feasibility using start/target IK and
target state validity. It does not prove path feasibility. `/tool/active` and
`/workobject/active` select execution context; persistent geometry belongs to
ConfigurationApi.

## Stop and collision release

Regular `/stop` calls MotionApi → gateway → operator/process stop and clears
queued work. Inspect `stop_state` and `success`: successful/no-active outcomes
return 200, unsuccessful outcomes 409. `/motion/controlled-stop` uses the task-aware
controlled-stop operation and its request schema.

A confirmed sensorless collision enters the dedicated collision stop path and
latches the motion interlock. Strategy construction and fallback are owned by the
executor, independently of operator Stop's Joint_6 hold policy.

`/motion/interlock/reset` calls ControlApi → gateway → controller recovery. Motion
stays held during acknowledgement, drive/readiness checks and settling. Ordinary
release can retain a valid baseline; explicit recalibration or an invalid baseline
requires full warm-up. A duplicate reset reports `in_progress`; stale telemetry
cannot release the hold. Known failure returns 409 and keeps the interlock. Reset
neither resumes the old task nor implicitly suppresses detection. See the
[sensorless recovery runbook](../../zeroerr/collision_detection/docs/SENSORLESS_COLLISION_DETECTION.md).

Suppression is a separate ControlApi command. The collision ROS adapter waits for
a fresh correlated acknowledgement, distinguishes not-sent from unknown outcome,
and applies bounded discovery/confirmation timeouts. Recovery-only authorization
does not bypass drive faults.

## Persistent configuration

1. Read `/configuration/<section>` for the active profile, saved/applied values
   and revision.
2. Submit explicit changes with `expected_revision` to ConfigurationApi.
3. The gateway's configuration service validates domain constraints and revision,
   then the repository writes atomically within the selected profile.
4. Runtime application follows persistence. Idle/fresh-state checks or unsupported
   live fields may leave the save pending. The durable save is retained.
5. Check `pending_application`, `application_error_info`, `applied` and
   `restart_required`. Retry `/apply` with the saved revision, or restart when
   required. Saving does not restart/recalibrate the observer or move the robot.

Legacy registry/configuration routes use the same service. New editors use the
revision-checked routes. Shared defaults and other profiles are not written by
these saves. [Configuration ownership](backend_configuration.md) specifies storage
and compatibility semantics.

## Control and diagnostics

ControlApi owns drive commands/verification, interlocks, safety walls/passages,
digital output, collision suppression/recording and diagnostic process controls.
An accepted drive command that is not yet verified returns 202 with
`success: false` and `drive_verification_pending`; query state before retrying.

The local gateway owns RViz and collision-diagnostic adapters. RViz start/stop acts
only on its managed session. Calibration recording endpoints start/stop passive
collection, not a motion program.

## Error boundary and correlation

The shared API decorator emits typed `error_info` and a request ID, preserving
actual gateway/controller/storage causes. HTTP parsing failures use the same
error envelope. `outcome_unknown: true` means the command may have taken effect:
observe state before deciding whether to retry. Do not implement automatic motion
retries based solely on timeout or HTTP transport loss. See
[API architecture](runtime_api_architecture.md) for complete fields/status mapping
and [motion codes](../../../../../docs/error_codes.md) for legacy numeric results.
