# Robot services

`MotionService` wraps the injected `IRobot` with platform safety checks and completion waits. `RobotStateManager` polls that injected driver, stores state and publishes snapshots through `RobotStatePublisher`. `RobotService` composes motion, driver lifecycle/state and optional tool operations behind `IRobotService`. `create_robot_service()` assembles these services, refreshes state once, then starts monitoring.

## Motion contract

`move_ptp()` intentionally calls the driver's `move_linear(..., blendR=0.0, blocking=wait_to_reach)`. This is the current service contract, despite the method name. `move_linear()` forwards the linear call and supports explicit recovery/safety options. Both interpret nonnegative driver return codes as success; when requested, they then verify the target pose. Sequence methods validate each segment, set the active tool, submit the sequence and optionally wait for its final pose.

`_wait_for_position()` uses a monotonic ten-second deadline, 0.1-second polling, a 5 mm Cartesian threshold and 1.2° wrapped-angle threshold. It requires three consecutive acceptable samples. It checks the cancellation callback before each sample. `_fresh_position()` prefers `get_current_position_fresh()`, falls back to the driver's regular getter, and uses the subscribed cache only when that getter returns an empty value. An exception returns an empty pose. Cancellation of the later polling wait cannot interrupt a driver call that is still blocking.

Step jog computes a projected target for the safety preflight. X/Y/Z steps use the tool rotation matrix; angular steps modify the corresponding angle. Velocity and acceleration can be supplied per call, otherwise constructor defaults apply. Narrow subzero recovery paths, servo-floor supervision, motion-corridor checks and stop retries are implemented in the service; read the exact options in [MODULES.md](MODULES.md) before modifying these behaviors.

Incomplete orientation samples in completion waits are a reproduced limitation recorded in [code issues](../../../CODE_ISSUES.md).

## State and publication

`RobotStateManager` stores the same driver passed to its constructor; it does not construct a dedicated `FairinoRobot` XML-RPC connection. Its nominal poll interval is 0.02 seconds and drive-status interval is one second. Actual update rate depends on driver IO/work and cannot be promised as exactly 50 Hz. State, position, velocity and acceleration queries use the stored snapshot; fresh-position access is a distinct driver path.

`RobotStatePublisher.publish(snapshot)` emits `RobotTopics.STATE`, `POSITION`, `VELOCITY` and `ACCELERATION` together. `STATE` carries `RobotStateSnapshot`, not just a raw string. Snapshot extras include readiness and driver-specific status when available. Consumers must tolerate stale/unavailable transport data according to the driver/state contracts.

`start_monitoring()` owns the daemon poll thread; `stop_monitoring()` clears its running flag and joins with a two-second timeout. This bounds shutdown waiting, not all underlying driver IO.

## Composition and lifecycle

The factory accepts robot, messaging, settings-key/service and optional toolchanger dependencies. It builds safety/motion/publisher/state, supplies configured active-tool/workobject getters when settings exist, and optionally constructs tool services. Robot-system service builders may use equivalent composition. Applications depend on the facade/interface through their application service, not on these concrete classes directly.

See [interfaces](../interfaces/README.md), [safety](../safety/README.md), [drivers](../drivers/README.md), and the source reference for all current methods and constructor signatures.

<!-- source-navigation:start -->
## Source navigation

[Module reference](MODULES.md) — signatures, fields, imports and source links for every Python file in this directory.

[Complete source index](../../../SOURCE_INDEX.md).
<!-- source-navigation:end -->
