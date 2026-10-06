# Hand-eye Calibration

This MVC application collects robot/chessboard poses and computes a camera-to-flange transform. `IHandEyeCalibrationService` separates the screen from robot, vision and capture-snapshot services. `core/hand_eye_core.py` supplies board detection, pose conversion/generation and the calibration calculation.

The runtime `HandEyeCalibrationService` starts a daemon capture thread; repeated starts while the thread is alive are ignored. `stop_capture()` sets a cooperative stop event and does not join the worker or itself guarantee immediate hardware stop. `is_running()` reflects thread liveness. The latest frame can be annotated with board detection when idle; during capture it avoids concurrent chessboard detection on the Qt thread.

`HandEyeConfig` controls board dimensions/square size, pose counts/ranges, probe distances/rotations, stabilization delays, velocities and visual-servo/search bounds. Defaults are listed in [service reference](service/MODULES.md). Physical board dimensions and camera intrinsics must match the configured setup. UI configuration delegates to the service; the current runtime `save_config()` stores configuration in memory, despite the interface docstring describing persistence. This limitation is included in [issues](../../CODE_ISSUES.md).

The controller connects progress, completion and sample-count topics through the application's messaging path and owns teardown. Check the runtime service's output paths/calibration-storage integration before using the result; this screen is an active robot workflow, not a hardware-free solver preview. System factories choose the real dependencies.

<!-- source-navigation:start -->
## Source navigation

[Module reference](MODULES.md) — signatures, fields, imports and source links for every Python file in this directory.

| Source subdirectory | Guide |
|---|---|
| `controller/` | [controller](controller/README.md) |
| `core/` | [core](core/README.md) |
| `model/` | [model](model/README.md) |
| `service/` | [service](service/README.md) |
| `view/` | [view](view/README.md) |

[Complete source index](../../SOURCE_INDEX.md).
<!-- source-navigation:end -->
