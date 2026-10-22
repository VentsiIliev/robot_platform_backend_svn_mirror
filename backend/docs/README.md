# Backend documentation index

Current guides were reviewed against the source on 2026-10-21. Numeric settings
are profile dependent; effective configuration and live state take precedence over
example values. Check a saved setting's application status before assuming the
running controller uses it.

## Setup and operation

- [Build, test, launch and troubleshooting](../ros2_ws/BUILD_SCRIPTS_README.md)
- [Requirements and recorded installation versions](../ros2_ws/WORKSPACE_REQUIREMENTS.md)
- [Workspace/package layout](../ros2_ws/eRob_moveit/README.md)
- [Motion error codes and HTTP outcomes](../ros2_ws/docs/error_codes.md)
- [Network mode switching](../ros2_ws/net_mode_switch.md)
- [CPU isolation investigation and machine-specific settings](../ros2_ws/docs/rt_cpu_isolation.md)

## Runtime and interfaces

- [Shared runtime overview](../ros2_ws/eRob_moveit/src/eRob_ROS2_MoveIt/erob_moveit_runtime/README.md)
- [Runtime composition](../ros2_ws/eRob_moveit/src/eRob_ROS2_MoveIt/erob_moveit_runtime/docs/ARCHITECTURE.md)
- [Four APIs, gateway, typed responses and errors](../ros2_ws/eRob_moveit/src/eRob_ROS2_MoveIt/erob_moveit_runtime/docs/runtime_api_architecture.md)
- [REST route reference](../ros2_ws/eRob_moveit/src/eRob_ROS2_MoveIt/erob_moveit_runtime/docs/REST_API.md)
- [Request and endpoint flows](../ros2_ws/eRob_moveit/src/eRob_ROS2_MoveIt/erob_moveit_runtime/docs/API_ENDPOINT_FLOWS.md)
- [Motion, collision stop and recovery](../ros2_ws/eRob_moveit/src/eRob_ROS2_MoveIt/erob_moveit_runtime/docs/MOTION_AND_SAFETY.md)
- [Ordered motion chains (Bulgarian)](../ros2_ws/eRob_moveit/src/eRob_ROS2_MoveIt/erob_moveit_runtime/docs/ORDERED_MOTION_CHAIN_BG.md)

The running backend serves Swagger UI at `/docs` (also `/api/docs`) and its
machine-readable operation/schema reference at `/openapi.json`. These are on the
configured HTTP listener, not a separate configuration server.

## Profiles, calibration and sensorless collision detection

- [Configuration ownership, persistence and API](../ros2_ws/eRob_moveit/src/eRob_ROS2_MoveIt/erob_moveit_runtime/docs/backend_configuration.md)
- [Profile composition and robot descriptions](../ros2_ws/eRob_moveit/src/eRob_ROS2_MoveIt/zeroerr/config/README.md)
- [Collision package layout](../ros2_ws/eRob_moveit/src/eRob_ROS2_MoveIt/zeroerr/collision_detection/README.md)
- [Observer, thresholds, recovery, braking strategies and diagnostics](../ros2_ws/eRob_moveit/src/eRob_ROS2_MoveIt/zeroerr/collision_detection/docs/SENSORLESS_COLLISION_DETECTION.md)
- [Supervised calibration collection](../ros2_ws/eRob_moveit/src/eRob_ROS2_MoveIt/zeroerr/collision_detection/docs/COLLISION_CALIBRATION_RUNNER.md)
- [Actuator mass assumptions](../ros2_ws/eRob_moveit/src/eRob_ROS2_MoveIt/zeroerr/docs/ACTUATOR_MASS_MODELING.md)
- [EtherCAT investigation log](../ros2_ws/eRob_moveit/src/eRob_ROS2_MoveIt/zeroerr/docs/ETHERCAT_ZEROERR_COMMUNICATION.md)
- [Fairino package responsibilities](../ros2_ws/eRob_moveit/src/eRob_ROS2_MoveIt/fairino5_v6_moveit2_config/README.md)

## Historical material

Files named `*PLAN*`, the workspace `docs/refactoring/` journals, the dated Servo
pickup context, and `zeroerr/archive/` retain design decisions and observations.
Their proposed layouts, commands, defaults and recorded timings are historical,
not current operating instructions. The gateway and REST migration plans link to
the implemented architecture. A ROS gateway/process split remains future work;
the current local gateway does not provide process isolation.

Vendored MoveIt Servo documentation describes that upstream component. It does
not define this backend's profile ownership or API contracts.

When changing an API, update its Python request/response contracts and OpenAPI,
then the route/flow guide. When changing settings, update the owning profile/schema
and its configuration runbook. Keep historical observations dated instead of
rewriting them as current guarantees.
