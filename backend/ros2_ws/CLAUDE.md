# Backend development guide

This checkout contains independent ROS 2 backends for Fairino and ZeroErr. Read the
[backend documentation index](../docs/README.md) and
[build/launch guide](BUILD_SCRIPTS_README.md) before using machine-specific commands.
Commands in this guide run from `backend/ros2_ws`; paths resolve from the checkout.

## Build and verify

- `./build_zeroerr.sh`: dependency-closed ZeroErr/runtime build into root `install`.
- `./quick_build.sh`: base packages followed by the legacy stacked overlay build.
- `./quick_build.sh <package> ...`: selected-package build; dependencies must exist.
- `./build_fairino.sh`: Fairino/runtime overlay build with an existing base underlay.
- `./test_backend.sh`: shared runtime offline Python suite.

Select ROS explicitly with `ROS_SETUP_FILE=/opt/ros/<distro>/setup.bash`.
Scripts otherwise honor installed `ROS_DISTRO`, then prefer Rolling, then Jazzy.
Do not mix distro artifacts or source an older overlay over a new root install.
New Python modules/resources and native changes require rebuild; running processes
must restart to load changed code. Source edits are not automatic hot reload.

## Launch

Use `./launch_zeroerr.sh --fake` for ZeroErr mock hardware;
`./launch_zeroerr.sh` and `./launch_fairino.sh` use configured robot connections.
The generic `./launch_robot.sh` reads a compatibility config defaulting to Fairino.
Per-robot launcher configs select setup paths and hardware/RT policy.
`ZEROERR_PROFILE` selects stack mode (`full`/`ethercat_only`);
`ZEROERR_ACTIVE_PROFILE` selects the robot/cell profile. These are distinct.

## Architecture and configuration

The shared package is `eRob_moveit/src/eRob_ROS2_MoveIt/erob_moveit_runtime`.
The robot config packages supply launch/config/model files; avoid duplicate runtime
implementations in them.

HTTP routes → `ConfigurationApi` / `MotionApi` / `StateApi` / `ControlApi` →
`RuntimeGateway` → `LocalRuntimeGateway` → backend services/controller/adapters.
API groups use consistent `api.py`, `requests.py`, `responses.py` files and typed
`ApiResponse`/`error_info`. Preserve actual error causes, accepted versus completed
outcomes and unknown command outcomes. Do not add direct ROS/file/process work to
HTTP routes or automatically retry motion/control.

Configuration domain/storage/application services live in `scripts/configuration/`.
The backend profile owns TCP/work-object definitions and sensorless settings.
The platform owns UI/process metadata and measurement history; edits to backend
values go through revision-checked `/configuration` operations. Check saved versus
applied/pending/restart state. Keep standalone startup independent of the platform.

ZeroErr `config/runtime.yaml` selects `ACTIVE_PROFILE` unless overridden by the
environment. Profile `runtime.yaml` composes includes, `calibration.yaml` stores
frames/tools, and `sensorless_collision.yaml` includes shared defaults plus local
overrides. Sensorless sections are `controller`, `monitor`, `runtime`; do not
reintroduce collision settings into generic runtime files.

The production ZeroErr sensorless observer is the C++
`zeroerr/RealtimeCollisionController`, not the deprecated Python monitor. Collision
Stop uses its own strategy under `motion/execution/stop_strategies/`; regular
operator/process Stop keeps its separate Joint_6 policy. Reset can retain a valid
baseline but requires fresh correlated readiness and settling before releasing
motion. A software stop trajectory does not establish a certified safety function.

HTTP/WebSocket and local runtime currently share one process. A future ROS gateway
must preserve the same typed results, revision identity, task IDs and cancellation
semantics; that separation is not already deployed.

## References

- [Runtime architecture](eRob_moveit/src/eRob_ROS2_MoveIt/erob_moveit_runtime/docs/ARCHITECTURE.md)
- [API contracts and extension rules](eRob_moveit/src/eRob_ROS2_MoveIt/erob_moveit_runtime/docs/runtime_api_architecture.md)
- [Configuration ownership/API](eRob_moveit/src/eRob_ROS2_MoveIt/erob_moveit_runtime/docs/backend_configuration.md)
- [Error codes](docs/error_codes.md)
- [Sensorless runbook](eRob_moveit/src/eRob_ROS2_MoveIt/zeroerr/collision_detection/docs/SENSORLESS_COLLISION_DETECTION.md)

Update the owning guide/contracts when changing behavior. Plans, investigations,
recorded timings and archived prototypes are historical evidence, not live settings.
