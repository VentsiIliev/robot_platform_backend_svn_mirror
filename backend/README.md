# Robot backend

The backend runs independently of the platform. It owns ROS 2 control, MoveIt
planning/execution, robot profiles and persistent robot configuration. The platform
uses its HTTP/WebSocket interfaces; it does not own backend profile files.

Start with the [documentation index](docs/README.md),
[build and launch guide](ros2_ws/BUILD_SCRIPTS_README.md), and
[shared runtime](ros2_ws/eRob_moveit/src/eRob_ROS2_MoveIt/erob_moveit_runtime/README.md).

From `backend/ros2_ws`, `./build_zeroerr.sh` builds ZeroErr and its local dependencies.
Use `./launch_zeroerr.sh` or `./launch_fairino.sh` for the selected robot.
Launching without `--fake` can connect to real hardware; build/test commands do not
start the robot. See the launch guide for profile selection and environment setup.
