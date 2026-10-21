# Runtime API architecture

The backend exposes four API groups. All use the same route → API → gateway →
backend-service flow. The backend remains independently startable without the platform.

| Group | Responsibilities |
| --- | --- |
| `ConfigurationApi` | Profile settings, tool/work-object definitions, revision checks, persistence and application status |
| `MotionApi` | Moves, paths, sequences, jogging/Servo, controlled stops, reachability, active tool/work-object selection |
| `StateApi` | Positions, velocities, snapshots, execution status, health and startup |
| `ControlApi` | Drives, interlocks, safety walls/passages, transient collision suppression, I/O and diagnostics |

Saving tool geometry is configuration. Selecting an existing tool is motion context.
A persistent collision threshold is configuration. Releasing a collision interlock
or temporarily suppressing detection is runtime control. State queries never change
settings or issue commands.

## Consistent layout

```text
scripts/
  runtime_api/
    contracts.py                 ApiResponse[T], ErrorInfo, correlation/error boundary
    common.py                    Immutable API settings and shared result helpers
    handlers.py                  RuntimeApi compatibility facade and composition
    configuration/
      api.py                     ConfigurationApi
      requests.py                Typed DTO and validation
      responses.py               Typed wire payloads
      __init__.py
    motion/                      Same four-file layout
    state/                       Same four-file layout
    control/                     Same four-file layout
  runtime_gateway/
    base.py                      RuntimeGateway contract (no HTTP or local backend imports)
    errors.py                    Transport-independent GatewayError
    local.py                     LocalRuntimeGateway implementation and service composition
    adapters/
      collision_monitor.py       ROS channel, request confirmation, freshness and bounded waits
      diagnostics.py             Backend diagnostic process ownership
      rviz_process.py            RViz process lifecycle
  rest/
    server.py                    HTTP/runtime startup and composition
    routes/
      configuration.py           HTTP adapter for ConfigurationApi
      motion.py                  HTTP adapter for MotionApi
      state.py                   HTTP adapter for StateApi
      control.py                 HTTP adapter for ControlApi
      common.py                  HTTP serialization, request IDs and transport errors
    openapi.py                   Routes/examples
    openapi_contracts.py         Schemas generated from Python DTO/response definitions
  configuration/                 Domain validation, persistence and runtime application services
```

Each API takes a `RuntimeGateway` and immutable `ApiSettings`. It can be imported and
used with a fake or remote gateway without importing Flask, ROS, `config`, or the
local backend. The `RuntimeApi` facade preserves the existing flat method interface
and composes the four groups. New code should use `api.configuration`, `api.motion`,
`api.state` and `api.control` explicitly.

The facade's default construction is a compatibility composition root. It resolves
local profile defaults and constructs `LocalRuntimeGateway` only when no gateway
or explicit settings were supplied. Alternate transports inject their own gateway
and settings; they must not import local runtime implementation modules.

The local gateway owns access to the configuration service, conditional Servo
supervisor, ROS channels and diagnostic process manager. API handlers do not access
`.node`, `.robot` or configuration service objects. HTTP routes do not publish ROS
messages, persist YAML or launch processes.

## Typed responses and failures

Every API method returns `ApiResponse[GroupResponse]`, with a JSON-compatible typed
payload and a status. Existing top-level fields and URLs remain available. Shared
fields are additive:

```json
{
  "success": false,
  "request_id": "client-request-123",
  "error": "Collision configuration was sent, but the controller did not confirm the matching request",
  "error_info": {
    "code": "collision_config_confirmation_timeout",
    "message": "Collision configuration was sent, but the controller did not confirm the matching request",
    "source": "gateway",
    "operation": "control.set_collision_suppression",
    "retryable": false,
    "outcome_unknown": true,
    "details": {"command_id": "example", "timeout_s": 2.0}
  }
}
```

`ErrorInfo` contains:

| Field | Contract |
| --- | --- |
| `code` | Stable machine-readable cause; clients must not parse the human message |
| `message` | Specific cause, including the backend/controller reason when supplied |
| `source` | Validation, gateway, runtime, storage, controller or transport |
| `operation` | API operation, or HTTP operation if parsing failed before API dispatch |
| `retryable` | Whether retrying is appropriate; false is conservative and never triggers an automatic retry |
| `outcome_unknown` | A command may have been applied despite the missing confirmation |
| `details` | Structured evidence: numeric result, command/task ID, fault, timeout, storage errno/cause as available |

The legacy string `error` remains readable by current platform clients. Full
tracebacks are logged with the request ID, rather than serialized in responses.
Non-finite numbers and unsupported backend response objects are reported as
`invalid_runtime_response`, not emitted as invalid JSON or reported as success.

API clients may send `X-Request-ID` (ASCII letters/digits, dot, underscore and dash,
up to 128 characters). A valid ID is echoed in both the response body and header.
Otherwise the backend generates one. Concurrent requests have independent contexts.

### Acceptance, completion and persistence

These are distinct outcomes:

- A nonblocking or queued move returns HTTP 202 with `accepted: true`, `final: false`
  and its task ID. Acceptance is not successful physical completion. Observe runtime
  execution state for the final result.
- A completed blocking move returns HTTP 200 with `final: true`. A supplied
  controller error is preserved alongside the legacy numeric motion result.
- Configuration `success: true` confirms the durable save. Always check
  `pending_application`, `application_error`, `application_error_info`, `applied`
  and `restart_required` separately. An application timeout does not undo the save.
- An accepted drive command whose requested state is not yet observed returns HTTP
  202 with `success: false`, `code: drive_verification_pending` in `error_info`,
  requested/actual state and an unknown outcome. Query the state before retrying.
- Partial state may return HTTP 206 with `unavailable_fields`. It must not be
  interpreted as a complete hardware snapshot.

Legacy registry write routes retain their historical `saved: boolean` and report
pending application as a conflict. The new configuration routes use `saved: object`.
They have separate typed response schemas to document that compatibility difference.

### Status mapping

| HTTP status | Meaning |
| --- | --- |
| 400 | Invalid fields or malformed JSON; command was not dispatched |
| 404 | Unknown resource/plan or route |
| 409 | State conflict, stale revision, or a known rejected operation |
| 415 | JSON request body required, but another media type was supplied |
| 500 | Unexpected runtime failure or an invalid backend response |
| 501 | Operation unsupported by this backend |
| 503 | Runtime/hardware/storage unavailable |
| 504 | Confirmation deadline exceeded; inspect `outcome_unknown` |

A timeout alone cannot establish that a robot command failed to execute. Neither
API nor gateway automatically retries a motion or control command. Numeric legacy
motion codes retain their established mapping; details identify the specific
reported controller/planner fault instead of replacing it with a generic message.

## A future ROS 2 gateway

`RuntimeGateway` exposes runtime operations and plain values, never Flask responses
or local service instances. A ROS 2 implementation can therefore map the same
operations to services/actions/topics:

- Services for revision-checked configuration reads/writes and short commands.
- Topics for observed state and notifications.
- Actions for longer operations that require progress/cancellation and a final result.

A topic-based write needs a correlated acknowledgement protocol. The local
collision adapter already rejects stale cached confirmations using a command ID.
It bounds discovery/confirmation waits and distinguishes unavailable subscribers
(known not sent) from a command whose outcome is unknown after publication.

Remote implementations should raise `GatewayError(code, message, kind=..., details=...,
retryable=..., outcome_unknown=...)`. The shared API boundary maps it to the same
wire error as the local implementation. The gateway must preserve task IDs,
profile/revision identity, cancellation semantics and actual error causes.

## Extending an API

1. Choose the existing group by responsibility; add a new group only for a concrete need.
2. Define normalized request/response types under that group's `requests.py` and `responses.py`.
3. Add the runtime operation to `RuntimeGateway`, with transport-independent failure semantics.
4. Implement it behind `LocalRuntimeGateway` using backend services/adapters.
5. Implement API validation/result mapping with `@api_operation('group.operation')`.
6. Add a thin HTTP route. Keep existing paths stable when replacing an implementation.
7. Document the route and examples in OpenAPI. Shared schemas are generated from
   the Python contracts; do not maintain a second handwritten error schema.
8. Test using a fake gateway: invalid input must not dispatch, faults must preserve
   their cause, and pending/unknown outcomes must not become completed success.

Configuration domain rules, atomic persistence, profile confinement and optimistic
revisions remain in the configuration application, behind the gateway. See
[Backend profile configuration](backend_configuration.md) for its storage contract.

## Validation

The offline suites cover API/gateway dependency boundaries, all four HTTP groups,
legacy facade delegation, route/OpenAPI coverage, typed errors, request correlation,
nonblocking acknowledgements, invalid JSON/types/numbers, stale revisions, persistence
failures, pending application, actual controller reasons, and ROS acknowledgement
freshness/correlation. Fakes replace ROS channels, processes and hardware; tests do
not move the robot. Build both packages before restarting the backend for manual
runtime acceptance testing.
