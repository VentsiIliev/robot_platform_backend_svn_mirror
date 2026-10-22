# REST API reference

The configured backend HTTP listener serves `/docs` (alias `/api/docs`) and
`/openapi.json`. OpenAPI is the detailed request/response schema reference;
Python API request/response types are used to build shared schemas. The main
runtime entry point currently supplies `0.0.0.0:5000` explicitly, while the server
factory accepts host/port arguments and configuration defaults.

All business routes follow **HTTP → API group → RuntimeGateway → backend services**.
See [API architecture](runtime_api_architecture.md) for types, errors and extension
rules, [request flows](API_ENDPOINT_FLOWS.md) for behavior, and
[profile configuration](backend_configuration.md) for persistent settings.

## Common contract

Send JSON objects for routes requiring a body. Invalid values/malformed JSON
return 400; routes requiring JSON media type can return 415. `X-Request-ID` is
validated or generated and returned in the header and API response body.

Failures include `success: false`, a legacy readable `error`, and typed
`error_info` with `code`, `message`, `source`, `operation`, `retryable`,
`outcome_unknown` and `details`. Inspect the specific cause instead of parsing
message text. Never automatically resend motion/control after an unknown outcome.

Nonblocking or queued motion returns **202**, `accepted: true`, `final: false`;
a completed blocking request returns **200**, `final: true`. Configuration
`success: true` confirms persistence; inspect `pending_application`,
`application_error_info`, `applied` and `restart_required` separately. Accepted
but unverified drive commands return 202 with `success: false` and
`drive_verification_pending`; query drive status before retrying.

Configuration routes remain available before robot/node initialization; applied
state may be unknown. Most other business routes return 503 until robot and node
exist. Health, startup and documentation remain available. This initialization
gate does not imply the motion stack is ready: inspect startup/status and let
backend motion/interlock checks enforce operational readiness.

## Route inventory

This inventory includes every explicit business route in `scripts/rest/routes/`.
`<id>` forms below are Flask path parameters. HEAD/OPTIONS are framework supplied.
The API group describes ownership; a GET control-status route need not belong to
StateApi. Documentation routes are `GET /docs`, `GET /api/docs`, `GET /openapi.json`.

### ConfigurationApi

| Method | Route | HTTP adapter |
| --- | --- | --- |
| GET | `/collision/monitor/config` | `get_collision_monitor_config` |
| POST | `/collision/monitor/config` | `update_collision_monitor_config` |
| GET | `/tool/registry` | `get_tool_registry` |
| POST | `/tool/registry/<int:tool_id>` | `update_tool_registry` |
| GET | `/workobject/registry` | `get_workobject_registry` |
| POST | `/workobject/registry/<int:user_id>` | `update_workobject_registry` |
| GET | `/configuration` | `configuration_catalog` |
| GET / PATCH | `/configuration/<section>` | `configuration_section` |
| POST | `/configuration/<section>/apply` | `configuration_apply` |
| PATCH | `/configuration/calibration/tools/<int:tool_id>` | `configuration_tool` |
| PATCH | `/configuration/calibration/workobjects/<int:user_id>` | `configuration_workobject` |

### MotionApi

| Method | Route | HTTP adapter |
| --- | --- | --- |
| POST | `/move/linear` | `move_linear` |
| POST | `/move/fast_lin` | `move_fast_lin` |
| POST | `/move/ptp` | `move_ptp` |
| POST | `/execute/path` | `execute_path` |
| POST | `/execute/sequence` | `execute_sequence` |
| POST | `/execute/ordered_motion_chain` | `execute_ordered_motion_chain` |
| POST | `/execute/ordered_motion_chain/prepare` | `prepare_ordered_motion_chain` |
| POST | `/execute/ordered_motion_chain/prepared/<plan_id>/execute` | `execute_prepared_ordered_motion_chain` |
| POST | `/unwind/joint6` | `unwind_joint6` |
| GET | `/tool/active` | `get_active_tool` |
| POST | `/tool/active` | `set_active_tool` |
| POST | `/reachability/pose` | `validate_pose` |
| POST | `/stop` | `stop_motion` |
| POST | `/motion/controlled-stop` | `controlled_stop` |
| POST | `/workobject/set` | `set_workobject` |
| GET | `/workobject/active` | `get_active_workobject` |
| POST | `/workobject/active` | `set_active_workobject` |
| POST | `/servo/cartesian/start` | `cartesian_servo_start` |
| POST | `/servo/cartesian/update` | `cartesian_servo_update` |
| POST | `/servo/cartesian/stop` | `cartesian_servo_stop` |
| POST | `/jog` | `jog` |
| POST | `/jog/joint` | `joint_jog` |
| POST | `/servojog/start` | `servo_jog_start` |
| POST | `/servojog/stop` | `servo_jog_stop` |
| POST | `/servojog/until-condition/start` | `conditional_servo_start` |
| POST | `/servojog/until-condition/cancel` | `conditional_servo_cancel` |
| POST | `/servojog/to-z` | `servo_jog_to_z` |
| DELETE | `/execute/ordered_motion_chain/prepared/<plan_id>` | `discard_prepared_ordered_motion_chain` |

### StateApi

| Method | Route | HTTP adapter |
| --- | --- | --- |
| GET | `/health` | `health` |
| GET | `/startup/status` | `startup_status` |
| GET | `/execute/ordered_motion_chain/prepared/<plan_id>` | `prepared_ordered_motion_chain` |
| GET | `/position/current` | `get_position` |
| GET | `/position/base_tcp` | `get_base_tcp_position` |
| GET | `/position/flange` | `get_flange_position` |
| GET | `/velocity/current` | `get_velocity` |
| GET | `/status` | `get_status` |
| GET | `/execute/ordered_motion_chain/status` | `get_ordered_motion_chain_status` |
| GET | `/state/snapshot` | `get_state_snapshot` |
| GET | `/state/kinematics` | `get_state_kinematics` |
| GET | `/servojog/until-condition/status` | `conditional_servo_status` |

### ControlApi

| Method | Route | HTTP adapter |
| --- | --- | --- |
| POST | `/collision/calibration/recording/start` | `start_collision_calibration_recording` |
| POST | `/collision/calibration/recording/stop` | `stop_collision_calibration_recording` |
| POST | `/collision/monitor/suppression` | `set_collision_monitor_suppression` |
| GET / POST | `/visualization/rviz` | `control_rviz` |
| POST | `/collision/monitor/diagnostics/open` | `open_collision_monitor_diagnostics` |
| GET | `/safety/walls/enabled` | `safety_walls_enabled` |
| GET | `/safety/walls/status` | `safety_walls_status` |
| POST | `/safety/walls/enable` | `enable_safety_walls` |
| POST | `/safety/walls/disable` | `disable_safety_walls` |
| GET | `/safety/passages` | `motion_passages_status` |
| GET / POST | `/safety/passages/<passage_id>` | `motion_passage` |
| POST | `/io/digital_output` | `set_digital_output` |
| POST | `/drive/enable` | `enable_drive_operation` |
| POST | `/drive/disable` | `disable_drive_operation` |
| GET | `/drive/status` | `drive_operation_status` |
| GET | `/motion/interlock/status` | `motion_interlock_status` |
| POST | `/motion/interlock/reset` | `reset_motion_interlock` |

## Motion units and examples

Cartesian poses are `[x, y, z, rx, ry, rz]` in millimetres/degrees. Velocity and
acceleration percentages are request/profile dependent; Servo requests can use
explicit linear/angular speeds. Follow the operation's schema rather than mixing
units between Cartesian HTTP poses and ROS joint trajectories (radians).

A blocking linear request:

```json
{"position": [300, 0, 250, 180, 0, 0], "tool": 0, "user": 0,
 "vel": 30, "acc": 10, "blocking": true}
```

This is an illustrative payload, not a safe target for any particular cell.
`/move/fast_lin` selects forced Pilz LIN; `/move/linear` retains its normal planning
path. `/reachability/pose` performs start/target IK plus target state validity;
it does not validate an entire intervening Cartesian path.

`POST /stop` returns `stop_state`, `stopped`, `queue_cleared`, `result` and
`success`. Confirmed/no-active-motion outcomes return 200; unsuccessful stop
outcomes return 409. Collision stop is invoked by the collision path, not by
reusing the regular UI/process Stop profile.

## Collision recovery and configuration

`POST /motion/interlock/reset` acknowledges the collision hold. It can wait while
recovery completes; duplicate requests report `in_progress`. A known failure
returns 409 and leaves motion interlocked. It never resumes the interrupted task.
See the [sensorless runbook](../../zeroerr/collision_detection/docs/SENSORLESS_COLLISION_DETECTION.md)
for baseline retention, readiness, timeout and stop strategies.

`POST /collision/monitor/suppression` with `{"suppressed": true}` requests transient
Recovery Jog suppression and waits for a fresh matching confirmation. It preserves
the collision latch and restricts normal motion. Only explicitly authorized
`/move/linear` recovery requests (`allow_collision_recovery: true`) may pass the
recovery gate; drive/EtherCAT faults remain enforced. Restore detection on exit.

Use revision-checked `/configuration/sensorless_collision` for durable settings.
Legacy `/collision/monitor/config`, `/tool/registry` and `/workobject/registry`
writes delegate to the same configuration application. Legacy registry writes
require `persist: true`; see the configuration guide for compatibility differences.
There is no arbitrary-file or profile-switch endpoint.

Recording start/stop controls passive calibration collection; it does not command
robot motion. RViz control accepts `{"enabled": true}` or `false`, owns its own
launch session and leaves robot control/MoveIt running. Collision diagnostics
open on the backend host and require its graphical environment.

## WebSocket listeners

Streams use separate TCP listeners in the same process, not Flask HTTP routes:

| Stream | Path | Configuration | Default port relative to HTTP |
| --- | --- | --- | --- |
| State | `/ws/state` | `REST_WS_STATE_*` | +1 |
| Execution | `/ws/execution` | `REST_WS_EXECUTION_*` | +2 |
| Generic sensor input | `/ws/sensors` | `REST_WS_SENSOR_*` | +3 |

Each has its own enable/host/port configuration. State and execution rates are
configurable. Actual ports may override these fallbacks. The implementation and
stream message shapes are in `scripts/runtime_websockets/`; do not assume HTTP
`ApiResponse` fields appear in every stream message. Sensor input feeds the
conditional Servo supervisor; it does not persist profile configuration.
