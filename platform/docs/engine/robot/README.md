# `src/engine/robot/` — Robot Module Overview

The `robot` package is the heart of the motion control system. It implements the full robot service stack from the physical driver layer up to high-level navigation and tool management, all behind well-defined interfaces.

---

## Package Structure

```
robot/
├── interfaces/            ← Abstract contracts for all robot subsystems
├── configuration/         ← Settings dataclasses (RobotSettings, RobotCalibrationSettings)
├── targeting/             ← Generic target-point registry, resolver math, and robot-system targeting provider
├── plane_pose_mapper.py   ← Generic rigid XY frame mapping between robot pose frames
├── enums/                 ← RobotAxis, Direction, ImageToRobotMapping
├── safety/                ← SafetyChecker (workspace bounds) + MotionCorridor / MotionCorridorRegistry
├── features/              ← NavigationService (named positions), RobotToolService
├── calibration/           ← calibration services, builders, provider contract, TCP/Z-shift/intrinsic capture
├── height_measuring/      ← Generic height-measuring builders + provider contract
├── services/              ← MotionService, RobotStateManager, RobotService, factory
├── path_interpolation/    ← active ContourPathPipeline + debug plotting (legacy under deprecated/)
├── path_preparation/      ← workpiece pixel contours → WorkpieceExecutionPlan
├── procedures/            ← ServoUntilConditionProcedure + pickup conditions
├── drivers/
│   ├── ros2_robot.py      ← Ros2Robot: IRobot over the ROS2 bridge
│   ├── client_adapters/   ← RobotClientAdapter + HTTP/WebSocket and fake transports
│   └── fairino/           ← FairinoRobot, TestRobotWrapper
├── base_robot.py          ← empty placeholder (0 bytes)
├── base_robot_service.py  ← deprecated shim re-exporting services.robot_service.RobotService
├── motion_sequence.py     ← OrderedMotionType / ordered-motion configuration types
├── tool_changer.py        ← ToolChanger (slot ↔ gripper mapping)
├── tool_manager.py        ← ToolManager (pick-and-place logic)
├── tool_transform.py      ← rotation_matrix / rotate / inverse_rotate / compose_translation
├── tool_activation_service.py        ← ToolActivationService
└── relative_tool_calibration_service.py ← relative tool calibration
```

---

## Architecture

### Service Composition Hierarchy

```
IRobotService (public contract — what applications see)
└── RobotService
      ├── IMotionService → MotionService
      │     ├── IRobot → Ros2Robot (production; ROS2 bridge via client adapters)
      │     │            / FairinoRobot (direct SDK) / TestRobotWrapper (dev)
      │     ├── ISafetyChecker → SafetyChecker
      │     └── MotionCorridorRegistry (registered corridors for move_linear_in_corridor)
      └── IRobotStateProvider → RobotStateManager
            ├── IRobot (same instance as above)
            └── IStatePublisher → RobotStatePublisher → IMessagingService
```

All inter-layer communication goes through interfaces. `RobotService` never knows about `FairinoRobot`; `MotionService` never knows about `RobotStateManager`. This allows each layer to be tested and replaced independently.

### Optional Tool Service

```
RobotService.tools: Optional[IToolService]
└── RobotToolService
      └── ToolManager
            ├── IMotionService (shared with motion layer)
            └── IToolChanger → ToolChanger (slot ↔ tool ID registry)
```

That diagram describes the legacy `create_robot_service()` path, where a
`tool_changer` must be supplied. Systems built with `SystemBuilder`, including
paint and glue, instead register `CommonServiceID.TOOLS: IToolService`. The default
builder creates one `ToolManager`, separate from `RobotService.tools`, and injects
it into the Tool Settings application.

`ToolManager` executes both saved pickup/drop-off operations and editor drafts
through one validated executor. Before each operation the default builder supplies
current tool, slot, robot-frame, and movement-group settings. Slot occupancy is
runtime state and is preserved independently of saved configuration.

The manager validates every step before motion, rejects concurrent tool operations,
and checks robot health and stationarity when the injected robot exposes those
checks. Failed commands are not replayed automatically (`max_retries` remains a
compatibility argument). Cancellation is checked between blocking calls and during
waits; an in-flight move also needs a robot stop request.

Saved operations update attachment at attach/detach boundaries, preserving a
completed boundary if retreat fails. An interrupted saved operation sets
`recovery_required` and blocks further execution until the caller manually inspects
the physical setup and calls `confirm_attached_tool(tool_id)` (`None` for an empty
flange). Confirmation selects the corresponding TCP. These are software records,
not hardware sensor verification; state is not restored as physical truth after
a restart. The editor draft path deliberately does not commit occupancy.

---

## Full Interface Hierarchy

```
IRobotLifecycle
  enable_robot() / disable_robot()
      │
      ┤ (also inherits)
      │
IMotionService
  move_ptp() / move_linear() / start_jog() / stop_motion() / get_current_position()
      │
      └── IRobotService   ← the single interface applications import
              + get_current_velocity()
              + get_current_acceleration()
              + get_state() / get_state_topic()
              + validate_pose(start_position, target_position, tool=0, user=0)
              + enable_safety_walls() / disable_safety_walls()
              + are_safety_walls_enabled() / get_safety_walls_status()
```

---

## Wiring

All components are assembled by `create_robot_service()` in `services/robot_service_factory.py`:

```python
from src.engine.robot.services.robot_service_factory import create_robot_service

robot_service = create_robot_service(
    robot=FairinoRobot(ip="192.168.58.2"),
    messaging_service=messaging,
    settings_service=settings,  # optional — enables safety checks
    tool_changer=None,           # optional — enables tool service
)
```

In a running system the driver is normally `Ros2Robot(server_url=...)` chosen by the bootstrap provider — see [drivers/](drivers/README.md).

The factory:
1. Creates `SafetyChecker(settings_service)`
2. Creates `MotionService(robot, safety_checker)`
3. Creates `RobotStatePublisher(messaging_service)`
4. Creates `RobotStateManager(robot, publisher)` and starts its monitoring thread
5. Optionally creates `RobotToolService`
6. Returns `RobotService(motion, robot, state_manager, tool_service)`

---

## Robot Availability States

`RobotStateManager` publishes `RobotStateSnapshot` on `RobotTopics.STATE`.

The important `snapshot.state` values are:

| State | Meaning |
|---|---|
| `idle` | Robot transport is reachable and no higher-level fault is being reported |
| `disconnected` | The underlying robot transport/bridge is unavailable |
| `error` | State polling itself failed unexpectedly |

For the ROS bridge driver:
- `HttpWebSocketRobotClient` (the ROS-bridge transport behind `Ros2Robot`) no longer raises during startup when `http://localhost:5000` is unavailable
- instead it reports `disconnected`
- `RobotStateManager` publishes that state through the normal broker topic

For motion stop requests against the ROS bridge:
- the bridge now returns an explicit `stop_state`
- `STOPPED` and `NO_ACTIVE_MOTION` are treated as benign stop outcomes by the platform client
- `STOP_REQUESTED_BUT_UNCONFIRMED` and `ERROR` are treated as failed stop outcomes and can trigger retries or operator warnings

For queued motion requests against the ROS bridge:
- queueable motion types are:
  - single-target linear/PTP moves
  - multi-waypoint trajectory execution
- both share one server-side motion queue, so mixed ordering is preserved:
  - single move -> trajectory
  - trajectory -> single move
- `jog` is explicitly not queueable
- the platform motion layer treats `ret >= 0` as an accepted motion command:
  - `0` = started immediately
  - `>0` = accepted and queued by the bridge

This means application startup can continue even when the bridge is down, and subscribers should treat `disconnected` as a first-class availability state, not as an exception path.

`RobotStateSnapshot.extra` may include transport diagnostics such as:
- `server_url`
- `last_error`

## Remote Safety Walls

`IRobotService` now also exposes optional control of the remote ROS/MoveIt safety-wall system:

- `enable_safety_walls() -> bool`
- `disable_safety_walls() -> bool`
- `are_safety_walls_enabled() -> Optional[bool]`
- `get_safety_walls_status() -> dict`

Important distinction:

- `ISafetyChecker`
  - platform-side Cartesian limit checking before commands are sent
- remote safety walls
  - ROS/MoveIt planning-scene walls enforced by the ROS bridge

These are related but separate safety layers. The platform contract keeps both:
- local safety checks remain in `MotionService` through `ISafetyChecker`
- remote wall control is exposed through `IRobotService`

Current driver support:

- `Ros2Robot` (via `HttpWebSocketRobotClient`)
  - backed by the REST endpoints:
    - `GET /safety/walls/enabled`
    - `GET /safety/walls/status`
    - `POST /safety/walls/enable`
    - `POST /safety/walls/disable`
- non-ROS drivers inherit safe default no-op implementations from `IRobot`

## Pose Reachability Validation

`IRobotService` now also exposes a reusable planning-only reachability primitive:

- `validate_pose(start_position, target_position, tool=0, user=0) -> dict`

Purpose:

- simulate whether a target pose is reachable from an explicit start pose
- reuse the same ROS/MoveIt planning path without physically moving the robot
- support higher-level workflows such as Calibration area-grid prechecks

Current driver support:

- `Ros2Robot` (via `HttpWebSocketRobotClient`)
  - backed by the REST endpoint:
    - `POST /reachability/pose`

Expected response fields include:

- `reachable`
- `fraction`
- `reason`
- `start_position`
- `target_position`

Important distinction:

- `validate_pose(...)`
  - planning-only simulation from a supplied start state
- `move_ptp(...)` / `move_linear(...)`
  - live execution from the robot's actual current state

The Calibration application uses `validate_pose(...)` only for precheck simulation. Real motion still plans from the live robot state at execution time.

---

## Subpackage Documentation

| Subpackage | Key Classes | Docs |
|-----------|------------|------|
| `interfaces/` | `IRobot`, `IMotionService`, `IRobotService`, `ISafetyChecker`, `IRobotStateProvider`, `IStatePublisher`, `IToolChanger`, `IToolService`, `ToolDefinition` | [interfaces/](interfaces/README.md) |
| `configuration/` | `RobotSettings`, `SafetyLimits`, `MovementGroup`, `MovementGroupSettings`, `RobotCalibrationSettings`, `ToolChangerSettings` | [configuration/](configuration/README.md) |
| `targeting/` | `PointRegistry`, `VisionTargetResolver`, `JogFramePoseResolver`, `RobotSystemTargetingProvider` | [targeting/](targeting/README.md) |
| `calibration/` | `build_robot_system_calibration_service`, `RobotSystemCalibrationProvider`, `CameraTcpOffsetCalibrationService`, `CameraZShiftCalibrationService`, `ToolTcpCalibrationService`, `RobotCalibrationProcess` | [calibration/](calibration/README.md) |
| `height_measuring/` | `IHeightMeasuringService`, `IHeightCorrectionService`, `HeightCorrectionService`, `build_robot_system_height_measuring_services` | [height_measuring/](height_measuring/README.md) |
| `path_interpolation/` | `ContourPathPipeline`, `smooth_points`, `arc_length_resample` (legacy: `interpolate_path_two_stage`) | [path_interpolation/](path_interpolation/README.md) |
| `path_preparation/` | `IWorkpiecePathPreparationService`, `DefaultWorkpiecePathPreparationService`, `WorkpieceExecutionPlan` | [path_preparation/](path_preparation/README.md) |
| `procedures/` | `ServoUntilConditionProcedure`, `ServoUntilConditionConfig`, `ServoRetractConfig`, `VacuumPickupCondition`, `TimedDummyPickupCondition` | [procedures/](procedures/README.md) |
| `../../robot_systems/default_service_builders.py` | `build_tool_service`, `build_vision_service` | centralized shared default builders used by `SystemBuilder` |
| `plane_pose_mapper.py` | `PlanePose`, `PlanePoseMapper` | reusable 2D rigid frame transform between robot pose frames |
| `enums/` | `RobotAxis`, `Direction`, `ImageToRobotMapping` | [enums/](enums/README.md) |
| `safety/` | `SafetyChecker`, `MotionCorridor`, `MotionCorridorRegistry` | [safety/](safety/README.md) |
| `features/` | `NavigationService`, `RobotToolService` | [features/](features/README.md) |
| `services/` | `MotionService`, `RobotStateManager`, `RobotService`, `create_robot_service` | [services/](services/README.md) |
| `drivers/` | `Ros2Robot`, `HttpWebSocketRobotClient`, `FakeRobotClient`, `build_robot_client` | [drivers/](drivers/README.md) |
| `drivers/fairino/` | `FairinoRobot`, `TestRobotWrapper` | [drivers/fairino/](drivers/fairino/README.md) |

---

## Design Notes

- **Production robot services avoid Qt widgets**: GUI consumers subscribe to state topics. The interpolation demo `path_interpolation/new_interpolation/simple_interpolation_pyqt6.py` is an explicit Qt exception and imports glue composition for demonstration.
- **State monitoring runs in a daemon thread**: `RobotStateManager` uses a nominal 0.02-second poll interval, with actual rate dependent on driver work. The thread is daemonized and doesn't block process exit.
- **Position format**: All positions are `List[float]` with 6 elements: `[x, y, z, rx, ry, rz]` in mm and degrees.
- **Return codes vs booleans**: `IRobot` methods return `int` (`0` = started immediately, `>0` = accepted and queued, negative = error). `IMotionService` wraps these and returns `bool` (`True` = accepted motion command). This distinction is maintained at the interface boundary.
- **Blocking waits are pose-aware**: when `wait_to_reach=True`, the default `MotionService` waits for Cartesian convergence and, for 6D targets, orientation convergence with wrapped-angle handling. This prevents orientation-only moves from being acknowledged early.
- **Bridge-down is not bootstrap-fatal**: for the ROS bridge transport, unavailable hardware should surface as `robot/state = disconnected`, allowing the rest of the platform to boot and show degraded availability.

<!-- source-navigation:start -->
## Source navigation

[Module reference](MODULES.md) — signatures, fields, imports and source links for every Python file in this directory.

| Source subdirectory | Guide |
|---|---|
| `calibration/` | [calibration](calibration/README.md) |
| `configuration/` | [configuration](configuration/README.md) |
| `drivers/` | [drivers](drivers/README.md) |
| `enums/` | [enums](enums/README.md) |
| `features/` | [features](features/README.md) |
| `height_measuring/` | [height_measuring](height_measuring/README.md) |
| `interfaces/` | [interfaces](interfaces/README.md) |
| `path_interpolation/` | [path_interpolation](path_interpolation/README.md) |
| `path_preparation/` | [path_preparation](path_preparation/README.md) |
| `procedures/` | [procedures](procedures/README.md) |
| `safety/` | [safety](safety/README.md) |
| `services/` | [services](services/README.md) |
| `targeting/` | [targeting](targeting/README.md) |

[Complete source index](../../SOURCE_INDEX.md).
<!-- source-navigation:end -->

## Trajectory and sequence return contract

`IRobot`, `IRobotService`, and their trajectory/sequence implementations return integer motion codes, excluding booleans and `None`. Blocking calls return `0` only for successful completion and negative values for failures. Nonblocking calls return `0` for immediate acceptance or a positive queue position; callers must observe execution status to establish completion. Higher-level `IMotionService` methods retain their boolean contracts.

`Ros2Robot` validates trajectory and sequence transport results. The HTTP client normalizes legacy wire booleans to integer codes, rejects malformed codes and contradictory HTTP/error responses, and rejects positive or non-final blocking outcomes. The direct Fairino SDK adapter does not support trajectory execution and returns `-1` without issuing motion; its test wrapper returns `0` for simulated success.

## Optional backend RViz control

`IRobotService.get_rviz_status()` and `set_rviz_enabled(bool)` expose optional
visualization process control. RobotService, MotionService, and Ros2Robot forward
to the HTTP client, which uses `GET/POST /visualization/rviz`. Unsupported drivers
return `rviz_control_unsupported`. These methods never issue robot motion or
change safety settings; the backend owns the visualization-only process session.

### Tool-change staging position

A robot system can declare `tool_change_group` as the ID of a single-position
movement group. Paint declares `"Tool Changer"`. The default tool-service builder
passes this requirement to `ToolManager`; systems with an empty declaration keep
their existing behavior.

Without an optional start move, the manager compares a fresh robot pose with the
group's current configured position before a saved operation or editor draft starts. Every X/Y/Z axis
must be within 10 mm and every RX/RY/RZ axis within 5 degrees, matching the capture
position guard. Angular differences wrap across +/-180 degrees. The comparison
uses the configured robot tool/user frame, as does navigation to the group.
Selecting a work-area label alone does not satisfy this check.

Missing/invalid settings, non-finite coordinates, or unavailable fresh feedback
reject execution. Without a start move, an out-of-tolerance pose also rejects
execution before motion or TCP changes. The manager approaches staging only when
the sequence explicitly includes `start_at_tool_changer`, then verifies arrival.
A rejected initial staging check does not set `recovery_required`; move to the
configured position and retry.

### Typed tool-operation outcomes

`IToolService` and `ToolManager` commands return `ToolOperationResult`. The
immutable result exposes `success`, `message`, and optional `ToolErrorInfo` with a
`ToolErrorCode`, `message`, one-based `step_number`, and diagnostic `detail`.
Success is derived from the absence of an error, so a failure always has a typed
reason. The contract lives in
[`interfaces/tool_operation_result.py`](../../../src/engine/robot/interfaces/tool_operation_result.py).

```python
from src.engine.robot.interfaces.tool_operation_result import ToolErrorCode

result = tool_service.pickup_tool(7)
if result.error is not None:
    if result.error.code == ToolErrorCode.NOT_AT_TOOL_CHANGER:
        # The operator must navigate to the staging position before retrying.
        print(result.message)
    else:
        print(result.error.code.value, result.error.step_number, result.error.detail)
```

Position checks distinguish `POSITION_NOT_CONFIGURED`, `POSE_UNAVAILABLE`, and
`NOT_AT_TOOL_CHANGER`. Execution distinguishes `CANCELLED`, `MOTION_FAILED`,
`ACTIVATION_FAILED`, and operator-confirmation failures. `BUSY` and
`RECOVERY_REQUIRED` are separate outcomes. Invalid sequences and configuration
load failures have their own codes. Unexpected exceptions return
`UNEXPECTED_ERROR`; callers must not classify errors by matching message text.

Internal guards raise `ToolOperationFailure` carrying the classified error. Public
commands convert that exception to a result without losing the code or context;
robot command exceptions retain the failing step and exception type. Existing
recovery-state and position guards remain in effect.

Legacy `(ok, message)` unpacking and indexing remain available through the result's
compatibility view (`as_tuple()` is the explicit form). New engine callers should
use the typed fields. The application service converts typed outcomes to its
existing UI tuple contract. Constructor dependencies, cancellation events,
callbacks, configuration providers, and all `ToolManager` methods have annotations.

### Optional tool-change endpoint moves

`ToolChangeStep` supports `start_at_tool_changer` and `finish_at_tool_changer` as
symbolic boundary steps. Their pose and motion settings are resolved from the
current `tool_change_group` before any motion. They must appear at the beginning
and end respectively, and at least one taught step must remain. Complete
validation still runs before moving.

The default builder injects the registered navigation service for endpoint moves,
including configured `fast_lin` navigation and cooperative cancellation. Directly
constructed managers can execute linear/PTP endpoints through their motion service.
The start step permits approaching from outside the staging tolerance, then fresh
feedback must verify arrival before the next step. Finish likewise verifies
arrival. With no start step, the original initial-position requirement is intact.
Saved pickup/drop-off failures during endpoint travel preserve completed attachment
boundaries and use the existing typed error/recovery behavior.
