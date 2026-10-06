# Paint processes

The paint system composes `PaintProcess` for production and the shared engine `RobotCalibrationProcess` for calibration. The calibration implementation is [src/engine/robot/calibration/robot_calibration_process.py](../../../../src/engine/robot/calibration/robot_calibration_process.py); `PaintCalibrationCoordinator` adapts launch/context to paint navigation and observers.

`PaintProcess` starts a daemon production worker and reports `RUNNING`, `PAUSED`, `STOPPED` or `ERROR` through `BaseProcess`. It supports cooperative pause/resume via `PaintProductionService`, manual single-cycle requests, incremental adjustment and unmatched-workpiece retry. Stop requests signal the phase and start a separate hardware-stop worker for robot/vacuum operations. A successful background run calls `stop()`; a failure calls `set_error()` unless stopping has already been requested.

`PaintProductionService.run_once()` orchestrates a business execution machine, optional magazine loading, capture/preparation/planning, pickup/painting, dropoff and post-return behavior. Configuration influences whether multiple workpieces/cycles are processed; describing all production as an unconditionally one-shot, five-step capture/paint path is inaccurate.

Source-controlled defaults/types are in `paint/config.py`. `PaintProcessConfigService` and its serializer own persisted/live process configuration, and production uses snapshots. See [production package](paint/README.md), [execution machine](paint/execution_machine/README.md), and the module references for exact method contracts.

Earlier package layout and no-pause descriptions are preserved only in [archive](../../../archive/robot_systems/paint/processes/README.md).

<!-- source-navigation:start -->
## Source navigation

[Module reference](MODULES.md) — signatures, fields, imports and source links for every Python file in this directory.

| Source subdirectory | Guide |
|---|---|
| `paint/` | [paint](paint/README.md) |

[Complete source index](../../../SOURCE_INDEX.md).
<!-- source-navigation:end -->
