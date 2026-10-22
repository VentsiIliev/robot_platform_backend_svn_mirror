# `fairino5_v6_moveit2_config`

Fairino 5 v6 robot-specific MoveIt configuration and launch package. Shared Python
control/API code, C++ planning helpers and custom runtime services live in
[`erob_moveit_runtime`](../erob_moveit_runtime/README.md), not in this package.
Hardware messages, URDF/meshes and the vendor interface are supplied by the
`fairino_msgs`, `fairino_description` and `fairino_hardware` packages.

Use the [backend build/launch guide](../../../../BUILD_SCRIPTS_README.md) for the
Fairino stacked workspace and `launch_fairino.sh` entry point. Select this package's
configuration when running the shared backend; ZeroErr-only EtherCAT/collision
controller capabilities do not imply equivalent Fairino hardware support.

## Shared documentation

- [Architecture](../erob_moveit_runtime/docs/ARCHITECTURE.md)
- [API/gateway contracts](../erob_moveit_runtime/docs/runtime_api_architecture.md)
- [REST routes](../erob_moveit_runtime/docs/REST_API.md)
- [Motion and safety](../erob_moveit_runtime/docs/MOTION_AND_SAFETY.md)

The legacy documentation URLs under this package's `docs/` link to those shared
references so they no longer describe duplicate or obsolete implementations.
