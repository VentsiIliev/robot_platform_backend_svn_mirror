# `src/engine/robot/drivers/` — Driver System Overview

The `drivers` package contains concrete implementations of `IRobot` — the lowest-level interface that talks directly to physical or simulated robot hardware. Each driver translates `IRobot` method calls into vendor-specific transport calls.

There are **two transport families**:

| Family | Driver | Talks to |
|---|---|---|
| ROS2 bridge | `Ros2Robot` | HTTP commands + WebSocket state streams against the ROS2 bridge server, via a pluggable `RobotClientAdapter` |
| Fairino SDK | `FairinoRobot` | FairinoRobot SDK directly over TCP/IP |

---

## Structure

```
drivers/
├── ros2_robot.py           ← Ros2Robot: IRobot over the ROS2 bridge (delegates to a client adapter)
├── client_adapters/
│   ├── base.py             ← RobotClientAdapter: marker base (transport_name = "unknown")
│   ├── factory.py          ← build_robot_client() / should_use_fake_robot_client()
│   ├── http_websocket.py   ← HttpWebSocketRobotClient: HTTP commands + 3 WebSocket streams
│   └── fake.py             ← FakeRobotClient: in-process simulation (no network)
├── fairino/
│   ├── fairino_robot.py    ← FairinoRobot: production driver (FairinoRobot SDK)
│   └── test_robot.py       ← TestRobotWrapper: full mock for development
└── zeroerr_robot.py        ← (empty placeholder)
```

`src/engine/robot/drivers/__init__.py` exports only `Ros2Robot`.

---

## Interface Contract

All drivers implement `IRobot`:

```
IRobot (ABC)
  move_ptp(position, tool, user, vel, acc) → int
  move_linear(position, tool, user, vel, acc, blend_radius) → int
  start_jog(axis, direction, step, vel, acc) → int
  stop_motion() → int
  get_current_position() → List[float]   # [x, y, z, rx, ry, rz]
  get_current_velocity() → float
  get_current_acceleration() → float
  enable() → None
  disable() → None
```

Return convention: `0` = success, non-zero = vendor error code.

---

## `Ros2Robot` — IRobot over the ROS2 Bridge

**File:** `ros2_robot.py` (471 lines)

```python
class Ros2Robot(IRobot):
    def __init__(self, server_url: str):
        self._client = build_robot_client(server_url=server_url)
```

`Ros2Robot` is a **thin, logging normalisation layer** over a client adapter:

- Every call delegates to `self._client.<method>(...)`.
- Every integer return is normalised: a non-int (or `bool`) result becomes `-1`.
- Every entry/exit is logged (debug level; init and errors at info/error).

### Capability groups exposed on top of `IRobot`

| Group | Methods |
|---|---|
| Motion | `move_ptp`, `move_linear` (extra `blocking`, `allow_collision_recovery`), `move_fast_linear`, `execute_trajectory`, `execute_motion_sequence`, `execute_custom_motion_sequence` |
| Ordered chains | `execute_ordered_motion_chain`, `prepare_ordered_motion_chain`, `execute_prepared_ordered_motion_chain`, `discard_prepared_ordered_motion_chain`, `get_prepared_ordered_motion_chain`, `get_ordered_motion_chain_status` |
| Jog / servo | `start_jog`, `start_joint_jog`, `start_servo_jog`, `stop_servo_jog`, `servo_jog_to_z`, `unwind_joint6` |
| Conditional servo | `start_conditional_servo`, `publish_conditional_servo_sensor`, `get_conditional_servo_status`, `cancel_conditional_servo` |
| Stop / recovery | `stop_motion`, `controlled_stop(expected_task_id, *, stop_duration_s)`, `get_last_motion_error`, `reset_all_errors` |
| Pose / frame | `get_current_position_fresh` (bypasses caches), `get_current_flange_position`, `get_current_base_tcp_position`, `validate_pose`, `set_active_tool`, `get_tool_registry`, `set_active_workobject`, `get_workobject_registry`, `update_workobject_registry` |
| State / status | `get_state_snapshot`, `get_execution_status`, `get_connection_state`, `get_connection_details`, `get_drive_status`, `get_status` (via client) |
| Safety walls | `enable_safety_walls`, `disable_safety_walls`, `are_safety_walls_enabled`, `get_safety_walls_status` |
| Passage lid / IO | `set_motion_passage_closed(passage_id, closed)`, `set_digital_output` |
| Misc | `enable`, `disable`, `clone()`, `prefers_incremental_jog()` |

### Two notable behaviours

- **`clone()` returns `self`** — deliberately. Unlike the Fairino driver, the ROS2 transport is safe to share, so `RobotStateManager` does not open a second pair of state/execution WebSocket connections. See the comment at `ros2_robot.py:463`.
- **`prefers_incremental_jog() → True`** — callers use this to choose incremental jog semantics for this transport.

`MotionService` and `RobotService` reach the optional capabilities through `getattr(self._robot, "method", None)` guards, so a driver that lacks them (e.g. `TestRobotWrapper`) degrades gracefully.

---

## `client_adapters/` — Transport Layer

### `RobotClientAdapter` (`base.py`)

Marker base class with a single class attribute `transport_name = "unknown"`. Subclasses declare their transport id (`"http_websocket"`, `"fake"`).

### `build_robot_client()` (`factory.py`)

```python
should_use_fake_robot_client(server_url) -> bool
build_robot_client(server_url="http://localhost:5000", ip=None, transport=None) -> RobotClientAdapter
```

Selection rules, in order:

| Step | Rule |
|---|---|
| 1 | `server_url` in `{"fake", "mock", "test", "sim"}` (case-insensitive, stripped) **or** starting with `fake://`, `mock://`, `test://`, `sim://` → `FakeRobotClient` |
| 2 | `transport` arg, else `$ROBOT_CLIENT_TRANSPORT`, else `"http_websocket"` |
| 3 | value in `{"http_websocket", "http+websocket", "hybrid", "default"}` → `HttpWebSocketRobotClient` |
| 4 | anything else → `ValueError` listing the available transports |

### `HttpWebSocketRobotClient` (`http_websocket.py`, 1961 lines)

> Docstring: *"Current robot transport: HTTP commands with WebSocket state/status streams."*
> `transport_name = "http_websocket"`

**Channels** — one HTTP command plane plus three WebSocket streams, each in its own thread:

| Channel | Shared configuration field | Staleness threshold |
|---|---|---|
| State | `state_ws_port`, path `/ws/state` | `_STATE_WS_STALE_AFTER_S = 1.0` |
| Execution status | `execution_ws_port`, path `/ws/execution` | `_EXECUTION_WS_STALE_AFTER_S = 1.0` |
| Sensors (publish) | `sensor_ws_port`, path `/ws/sensors` | — |
| Commands | `client_host` and `http_port` | — |

Addresses and ports come from [backend network configuration](../backend_network.md).
The former per-channel URL environment overrides are rejected.

If the state WebSocket goes stale, an HTTP snapshot fallback runs every `_STATE_HTTP_FALLBACK_INTERVAL_S = 0.5`.

**Lifecycle:** `__init__` runs `health_check()` against the bridge; a non-`ok` status marks the client unavailable (logged), then the three WebSocket threads start regardless. Reconnection is probed every `_RECONNECT_CHECK_INTERVAL_S = 1.0` s.

**Motion error convention:** `_MOTION_ERROR_DRIVE_NOT_ENABLED = -13`. Stop outcomes are normalised into `_STOP_STATE_STOPPED` / `_STOP_STATE_NO_ACTIVE_MOTION` / `_STOP_STATE_STOP_REQUESTED_BUT_UNCONFIRMED` / `_STOP_STATE_ERROR`.

Notable API surface: `move_ptp`, `move_liner` (sic — bridge spelling), `move_cartesian`, `execute_path`, `execute_sequence`, `execute_ordered_motion_chain` + prepare/execute/discard/get prepared plan, `start_jog`/`start_joint_jog`/`start_servo_jog`/`stop_servo_jog`, conditional-servo quartet, `move_fast_linear`, `set_motion_passage_closed`, `stop_motion`, `controlled_stop`, pose/frame registry methods, safety-wall methods, `setDigitalOutput`, `resetAllErrors`, `publish_sensor_state`.

Response handling: `_parse_motion_response()` converts a bridge payload to an int result code; `_motion_preflight_error()` blocks motion when the client is unavailable or the drive is not enabled; `_execution_status_*` helpers summarise/preplan-signature execution status for the WebSocket transition logs.

### `FakeRobotClient` (`fake.py`, 388 lines)

`transport_name = "fake"`. In-process simulation with **no network and no threads**:

- `_accept_motion()` updates `_current_position` immediately and marks motion active only when non-blocking; returns `0`.
- `_set_path_result()` synthesises a full bridge-shaped response (`http_status`, `result_code`, `task_id`, `queued`, `queue_position`, `raw`).
- Keeps local state for drive enable, safety walls, digital outputs, active tool/workobject, task counter.
- `health_check()` → `{"status": "ok", "message": "Running fake ROS2 client"}`.
- Mirrors the same error constants as the HTTP client (`-13`, the four stop states) so code paths behave identically under simulation.

---

## `fairino/` — Direct SDK Driver

→ See [fairino/README.md](fairino/README.md) for full documentation (`FairinoRobot`, `TestRobotWrapper`).

---

## Wiring

| Consumer | Use |
|---|---|
| `build_configured_robot()` (`src/bootstrap/startup_config.py:261`) | returns `Ros2Robot(server_url="http://localhost:5000")` for the configured startup |
| `PaintBootstrapProvider` / `WeldingBootstrapProvider` | `Ros2Robot("http://localhost:5000")` |
| `GlueBootstrapProvider` / `TwinBootstrapProvider` | `Ros2Robot("fake://local")` — fake client, no bridge required |
| `SystemBuilder` → `create_robot_service(robot=...)` | wraps whichever driver in `RobotService` |

---

## Swapping Drivers

To use a different physical robot, create a new class that implements `IRobot` and pass it to `create_robot_service()`. No changes are required anywhere else in the stack.

```python
class MyCustomRobot(IRobot):
    def move_ptp(self, position, tool, user, vel, acc) -> int:
        # Call your SDK here
        return 0
    # ... implement remaining methods

robot_service = create_robot_service(
    robot=MyCustomRobot(),
    messaging_service=messaging,
)
```

To add a new **transport for the ROS2 driver** instead, subclass `RobotClientAdapter`, give it a `transport_name`, and register it in `build_robot_client()` (`client_adapters/factory.py`) — `Ros2Robot` itself does not need to change.

---

## Design Notes

- **Two seams, two purposes**: `IRobot` swaps the *driver*; `RobotClientAdapter` swaps the *wire protocol* behind `Ros2Robot`. Most changes only need the latter.
- **Fake is selected by URL, not by flag**: `server_url="fake://local"` is the documented way to run a robot system without a bridge — no settings or env var needed.
- **Normalisation happens at the driver**: bridge payloads may be dicts, bools, or ints; `Ros2Robot` collapses all of them to `int` before `MotionService` sees them, so `ret >= 0` is always a valid success test.
- **`zeroerr_robot.py` is empty** (1 byte placeholder) — do not assume a ZeroErr driver exists.

<!-- source-navigation:start -->
## Source navigation

[Module reference](MODULES.md) — signatures, fields, imports and source links for every Python file in this directory.

| Source subdirectory | Guide |
|---|---|
| `client_adapters/` | [client_adapters](client_adapters/README.md) |
| `fairino/` | [fairino](fairino/README.md) |

[Complete source index](../../../SOURCE_INDEX.md).
<!-- source-navigation:end -->
