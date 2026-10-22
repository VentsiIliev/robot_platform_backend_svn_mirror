# Runtime architecture

`erob_moveit_runtime` is shared by the `zeroerr` and
`fairino5_v6_moveit2_config` robot packages. Robot packages supply descriptions,
MoveIt/controller configuration, launch files and profile values; they do not
contain private copies of this runtime.

## Composition and process model

`scripts/main.py` starts `rest.server.start_rest_server()` with an asynchronous
initializer. `runtime_initializer.initialize_robot_runtime()` constructs the ROS
node, executor and configured backend. HTTP can report initialization progress
before the motion stack is ready. The main entry point currently explicitly binds
HTTP to `0.0.0.0:5000`; callers of `start_rest_server()` otherwise use its configured
host/port defaults or explicit arguments.

HTTP and the state/execution/sensor WebSocket servers share the runtime process.
Using a gateway separates responsibilities but does not yet isolate failures into
separate processes. A ROS-backed gateway is an extension point, not a deployed
transport. `scripts/rest/main.py` supports standalone REST startup; embedded mode
reuses supplied robot/node instances.

## Request boundary

```text
rest/server.py                      startup and composition
  -> rest/routes/<group>.py         HTTP parsing/serialization only
  -> runtime_api/<group>/api.py     validation, typed results, error mapping
  -> runtime_gateway/base.py        transport-independent operations
  -> runtime_gateway/local.py       local services and adapters
     -> configuration/              profile persistence and application
     -> backend/                    robot-style facade and frame transforms
     -> RobotController             planning, execution, state and interlocks
     -> runtime_gateway/adapters/   ROS confirmations and diagnostic processes
```

The four groups are `ConfigurationApi`, `MotionApi`, `StateApi` and `ControlApi`.
Each has `api.py`, `requests.py`, `responses.py` and `__init__.py`.
`runtime_api/contracts.py` supplies `ApiResponse[T]`, correlation and the shared
exception boundary. `RuntimeApi` in `handlers.py` is the flat compatibility facade.
`rest/api_support.py`, `rest/rviz_process.py` and `configuration/http.py` retain
compatibility imports rather than owning the implementation.

See [API architecture](runtime_api_architecture.md) for type/error contracts and
[configuration ownership](backend_configuration.md) for persistent state.

## Robot and motion ownership

`RobotController` owns ROS clients, `MotionCoordinator`, `MotionQueue`,
`TrajectoryExecutor`, planning support/context, workspace safety and state caches.
`MoveItRobotBackend` applies user/work-object and tool context before delegating
robot-style operations to that controller. API code accesses it through the gateway.

A linear target normally uses Cartesian planning; PTP and forced Pilz LIN use their
respective planning paths. Paths/sequences and ordered chains have their own
planning/execution orchestration. Time parameterization uses the selected
trajectory optimizer before FollowJointTrajectory dispatch. Micro-move fallback
and direct-contour behavior are controlled by their planning configuration.

`MotionCoordinator` arbitrates immediate execution, queueing and rejection.
`MotionQueue` tracks requests, IDs and completion; acceptance of a queued task is
not controller completion. `TrajectoryExecutor` owns action submission/results,
stop trajectory dispatch and execution handoff.

## Stop, collision and recovery

Operator/process Stop and collision Stop have distinct profiles. Implementations
live in `motion/execution/stop_strategies/`; collision strategy selection comes
from the active profile's sensorless runtime settings. Action handling and fallback
remain in the executor. UI/process Stop retains its existing Joint_6 hold policy;
collision stop uses its own configured held joints.

The production ZeroErr observer is the C++ `zeroerr/RealtimeCollisionController`
in the controller-manager update loop. Python estimator modules and the deprecated
Python monitor are retained for offline/legacy use. Runtime ROS adapters consume
collision stop/readiness/acknowledgement messages. A confirmed active collision
latches motion, clears queued work and invokes the collision stop path.

Recovery uses a fresh acknowledgement generation. Ordinary release can retain a
valid stationary torque baseline; explicit recalibration and invalid baseline
require full warm-up. Reset releases the hold only after current readiness and
settling checks. It does not resume the previous task or suppress detection.
See [motion and safety](MOTION_AND_SAFETY.md) and the
[sensorless runbook](../../zeroerr/collision_detection/docs/SENSORLESS_COLLISION_DETECTION.md).

## State and diagnostics

`status/` maintains measured state and publishes status. `StateApi` exposes
snapshots and queries; partial state explicitly lists unavailable fields.
`runtime_websockets/` provides streaming state, execution and generic sensor data.
Those servers still have separate stream payload/lifecycle code; the four API
request/response contracts do not imply all streams have been migrated to it.

The gateway owns diagnostic resources. `adapters/rviz_process.py` manages only its
own RViz launch session; diagnostics adapters open the configured collision plots.
The backend shutdown path closes owned resources.
