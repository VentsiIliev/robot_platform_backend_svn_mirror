# eRob MoveIt packages

This directory contains the shared `erob_moveit_runtime`, Fairino
`fairino5_v6_moveit2_config` and EtherCAT `zeroerr` configuration packages.
Hardware/vendor dependencies are under the sibling `../src` directory.

Build/launch commands should normally be run from `backend/ros2_ws`:

```bash
./build_zeroerr.sh
./launch_zeroerr.sh --fake
```

The current ZeroErr build includes its local dependency closure and installs into
`ros2_ws/install`. The `quick_build.sh`/Fairino path retains the stacked base +
`eRob_moveit/install` layout. These layouts are distinct: launch the setup selected
by the corresponding per-robot `.conf` file. Scripts derive paths from the checkout
and support explicit `ROS_SETUP_FILE`; Rolling is not a required hardcoded distro.

See the [build and launch guide](../BUILD_SCRIPTS_README.md) for exact selection,
source/setup instructions, tests and troubleshooting. Prefer `launch_zeroerr.sh`
or `launch_fairino.sh`; legacy `robot_launch.conf` defaults to Fairino.

## Runtime and profile ownership

- [Shared runtime](src/eRob_ROS2_MoveIt/erob_moveit_runtime/README.md): four typed API
  groups behind RuntimeGateway; local gateway currently runs in the same process.
- [ZeroErr profile composition](src/eRob_ROS2_MoveIt/zeroerr/config/README.md): models,
  cells, tools, calibration and per-profile sensorless collision settings.
- [Backend configuration API](src/eRob_ROS2_MoveIt/erob_moveit_runtime/docs/backend_configuration.md):
  authoritative backend storage, optimistic revisions, save/application status.
- [Backend documentation index](../../docs/README.md).

The platform is a client and the backend remains independently startable. A
symlink install does not update a running Python process or C++ controller; rebuild
new resources/native changes and restart the deployed backend as required.
