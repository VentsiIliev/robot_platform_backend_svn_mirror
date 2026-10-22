# Backend build, test and launch

Run commands from **`backend/ros2_ws`**, relative to your checkout. Scripts resolve
paths from their own location; `/home/ilv/ros2_ws` is not a required installation
path. See [workspace requirements](WORKSPACE_REQUIREMENTS.md) for ROS/MoveIt,
EtherLab and hardware dependencies. Build scripts do not install system packages.

## ROS environment

Build/launch scripts choose ROS in this order: `ROS_SETUP_FILE`, an installed
`ROS_DISTRO` from the environment, Rolling if installed, then Jazzy. Pin one distro
for a deployment, for example:

```bash
export ROS_SETUP_FILE=/opt/ros/jazzy/setup.bash
```

Use a separate build/install workspace when changing ROS distros, or deliberately
clean generated artifacts first. Build scripts clear inherited ROS/overlay paths
to avoid mixing installations. ZeroErr also supports `MOVEIT_SETUP_FILE` for an
additional MoveIt underlay.

## ZeroErr: fresh checkout or incremental build

```bash
./build_zeroerr.sh
source "$ROS_SETUP_FILE"
source install/local_setup.bash
```

The top-level wrapper calls `eRob_moveit/build_zeroerr.sh`. It builds in
`ros2_ws/build` and `ros2_ws/install` with `--symlink-install`, selecting
`--packages-up-to erob_moveit_runtime zeroerr`. Local dependencies are included on
every run, including retries after failure. An existing base install is not
required. This script does **not** implement positional package selection; use
`quick_build.sh <package>` or an explicit colcon invocation for that purpose.

Dependency integration tests are disabled by default (`BUILD_TESTING=OFF`). To
build them after installing their dependencies:

```bash
BUILD_TESTING=ON ./build_zeroerr.sh
```

Rebuild `zeroerr` and `erob_moveit_runtime` together after changes to shared profile
composition, collision-controller interfaces, native brake code or installed
resources. Existing Python symlinks may reflect source edits, but newly added
modules/resources and running processes still require rebuild/restart as relevant.

## Fairino and the legacy stacked build

```bash
./quick_build.sh
# Or selected packages (dependencies must already be built):
./quick_build.sh fairino_hardware
./quick_build.sh erob_moveit_runtime fairino5_v6_moveit2_config
```

With no arguments, `quick_build.sh` builds `fairino_msgs`, the remaining base
packages, then all three overlay packages under `eRob_moveit/`. With package
arguments it routes each selection to the base or overlay; it uses
`--packages-select`, not dependency closure. The overlay sources
`ros2_ws/install/local_setup.bash` and installs under `eRob_moveit/install`.
`./build_fairino.sh` is the dedicated wrapper for the runtime and Fairino overlay;
it also expects local dependencies to have been built.

For this stacked layout, source the ROS installation, then
`eRob_moveit/install/setup.bash` (which chains its recorded underlay). Do not
accidentally launch against an older overlay after building ZeroErr into the root
install: the configured launch setup path determines which artifacts are used.
The ZeroErr launcher selects the root install; Fairino selects the overlay.

## Offline verification

```bash
./test_backend.sh
```

This runs the shared runtime's Python tests using `/usr/bin/python3 -m pytest`.
It requires `python3-pytest` and the modules used by the selected tests. It does
not start the robot. Profile/collision suites are separate; from the same directory
in a sourced ROS environment:

```bash
python3 -m pytest -q \
  eRob_moveit/src/eRob_ROS2_MoveIt/zeroerr/test/test_profile_composition.py \
  eRob_moveit/src/eRob_ROS2_MoveIt/zeroerr/test/test_sensorless_configuration.py
```

## Launch and profile selection

```bash
./launch_zeroerr.sh --fake
# Real hardware:
./launch_zeroerr.sh
# Fairino:
./launch_fairino.sh
```

`--fake` selects ZeroErr mock hardware and skips EtherCAT preparation/monitoring.
Without it, the ZeroErr launcher uses its configured real-hardware path. The
launcher accepts `--fake`, `--real` and `--`; it does not accept a launch filename
or arbitrary `ros2 launch` arguments as positional options.

`eRob_moveit/zeroerr_launch.conf` and `fairino_launch.conf` select workspace/setup,
launch file, hardware/RT policy and RViz startup. The compatibility
`robot_launch.conf` currently selects **Fairino**, so prefer explicit robot
wrappers. For a custom launcher configuration, use the generic wrapper:

```bash
ROBOT_LAUNCH_CONFIG=/absolute/path/custom.conf ./launch_robot.sh
```

`ZEROERR_PROFILE=full|ethercat_only` chooses the stack mode. It is separate from
`ZEROERR_ACTIVE_PROFILE`, which chooses the robot/cell configuration:

```bash
ZEROERR_ACTIVE_PROFILE=development_short_links ./launch_zeroerr.sh --fake
```

Without that override, `zeroerr/config/runtime.yaml` selects `ACTIVE_PROFILE`.
The platform selects its profile through `platform/config/platform.json` and
starts the same independent backend. Runtime values, calibration and sensorless
settings belong to that backend profile; see
[configuration ownership](eRob_moveit/src/eRob_ROS2_MoveIt/erob_moveit_runtime/docs/backend_configuration.md).

Source changes do not update already-running processes. Restart after rebuilding
to load code/controller/startup settings. Persistent API edits may apply a subset
live; check their saved/applied/restart status rather than restarting blindly.

## Troubleshooting

- Missing ROS generators or MoveIt packages: install dependencies for the selected
  distro; do not mix Rolling package names with a Jazzy build.
- `libfairino.so.2` unavailable: build/install `fairino_hardware` before the Fairino
  overlay and source the setup selected by the launcher.
- A partially failed ZeroErr build: rerun `./build_zeroerr.sh`; it includes local
  dependencies even if a partial `install/local_setup.bash` already exists.
- Wrong runtime/model after rebuilding: inspect launch setup paths and profile
  selection; source only the intended deployment layout.
- Port conflict: the HTTP startup check includes enabled WebSocket listeners and
  fails with the conflicting addresses. Stop the stale instance instead of
  launching a second runtime.
- DDS cross-talk: use the launcher's configured ROS domain/local discovery policy;
  see the [recorded investigation](docs/fix-pl25488-dds-crosstalk.md).

`clean_build.sh` does not exist in this checkout. `clean_zeroerr.sh` is a separate
cleanup helper; inspect its scope before using it. Cleaning build artifacts is
not a routine requirement after every pull. The
[CPU isolation note](docs/rt_cpu_isolation.md) records machine-specific RT findings;
its core numbers and kernel options are not portable defaults.
