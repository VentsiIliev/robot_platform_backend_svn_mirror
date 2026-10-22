# Motion error codes and HTTP outcomes

The canonical numeric mapping lives in
[`runtime_api/motion/responses.py`](../eRob_moveit/src/eRob_ROS2_MoveIt/erob_moveit_runtime/scripts/runtime_api/motion/responses.py).
Request validation may reject a request before a numeric backend result exists.
See [API contracts](../eRob_moveit/src/eRob_ROS2_MoveIt/erob_moveit_runtime/docs/runtime_api_architecture.md)
for typed `error_info`, request IDs and transport/status mapping, and
[REST routes](../eRob_moveit/src/eRob_ROS2_MoveIt/erob_moveit_runtime/docs/REST_API.md)
for the complete inventory.

## Numeric motion results

| Result | Meaning | HTTP mapping |
| --- | --- | --- |
| `> 0` | Accepted/queued, not completed | 202 |
| `0` | Immediate acceptance or successful blocking completion | 202 for nonblocking; 200 for completed blocking |
| `-1` | Busy / invalid input / generic error | 500 |
| `-2` | MoveIt service unavailable | 503 |
| `-3` | Safety violation: target outside workspace | 400 |
| `-4` | No current robot position available | 500 |
| `-5` | Motion queue full | 503 |
| `-6` | Path planning failed: MoveIt returned no trajectory | 500 |
| `-7` | Time parameterization failed (TOTG/Ruckig) | 500 |
| `-8` | Jacobian fallback path planning failed | 500 |
| `-9` | Near-singularity detected | 500 |
| `-10` | Collision detected during Jacobian check | 500 |
| `-11` | Cartesian path planning failed: target unreachable, collision, or joint-limit constraint | 400 |
| `-12` | Hardware not ready: EtherCAT slave not in OP | 503 |
| `-13` | Drive operation is not enabled; call POST /drive/enable before motion | 409 |
| `-14` | Controller execution failed: trajectory tolerance or controller action error | 409 |

A nonblocking/queued response includes `accepted: true`, `final: false` and a task
ID when available. Observe execution state for completion. A controller-provided
fault/reason is retained; the generic table is a fallback description.
Queue capacity is configured, not fixed by this document.

## Other outcomes

- Invalid request fields/malformed JSON: 400. A route requiring JSON media type can
  return 415. Validation rejects before backend command dispatch.
- Stale configuration revision or known state conflict: 409.
- Runtime/hardware/storage unavailable: 503. Unsupported operation: 501.
- Confirmation timeout: 504 with the gateway's actual cause. Inspect
  `outcome_unknown`; a timeout does not prove the command was never applied.
- Accepted but unverified drive command: 202, `success: false`,
  `error_info.code: drive_verification_pending`. Query `/drive/status`.
- Partial snapshot/kinematics: 206 with `unavailable_fields`.
- Durable configuration save with pending runtime application: 200, `success: true`;
  inspect `pending_application` and `application_error_info` separately.

`POST /stop` returns 200 for successful/no-active outcomes and 409 for unsuccessful
outcomes. Inspect `stop_state`, `stopped`, `queue_cleared`, `result` and `success`.
`POST /motion/interlock/reset` returns 200 on success and 409 on a known failure;
it retains the hold until correlated observer readiness is confirmed. Duplicate
reset responses may report `in_progress`; do not treat that as released motion.

## Optimizer and planning failures

`TRAJECTORY_OPTIMIZER` selects the trajectory optimization implementation
(TOTG or Ruckig) through the profile/runtime configuration.
[`trajectory_optimizer.py`](../eRob_moveit/src/eRob_ROS2_MoveIt/erob_moveit_runtime/scripts/motion/execution/trajectory_optimizer.py)
encapsulates selection; helper integration is in `trajectory_optimization.py`.
Use effective profile values rather than assuming one global optimizer default.
Both optimizer failures map to `-7`.

Micro-move fallback can return no-op success if the requested target is already
satisfied, or `-9` if a meaningful target cannot be resolved near a singularity.
`/reachability/pose` performs endpoint IK/state validation and cannot establish
full intervening path feasibility. Actual execution retains planning/controller
checks. Its validation result/reason must be interpreted independently of motion
submission result codes.

State and WebSocket payloads use their documented contracts; a successful state
read or an HTTP acknowledgement alone never establishes physical motion completion.
