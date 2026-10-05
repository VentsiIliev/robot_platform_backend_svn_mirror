# Sensorless collision calibration runner

The runner generates single-joint sweeps at several velocity/acceleration
profiles followed by deterministic broad-workspace joint samples. It starts
idle. Every candidate path is sampled at no
more than `COLLISION_CALIBRATION_MAX_INTERPOLATION_STEP_RAD`, checked against
the current MoveIt planning scene, timed by Ruckig, densely sampled again, and
checked a second time before controller dispatch.

Keep people and loose equipment outside the robot workspace. MoveIt checks the
modeled robot and collision world; it cannot detect an unmodeled person or
object. Use the hardware emergency stop and supervise the complete real run.

## First dry run

Keep this setting in `config/runtime.yaml`:

```yaml
COLLISION_CALIBRATION_DRY_RUN: true
```

Restart the stack, then start and inspect the validation-only run:

```bash
ros2 service call /zeroerr_collision_calibration_runner/start std_srvs/srv/Trigger {}
ros2 topic echo /zeroerr_collision_calibration_runner/status
```

Rejected targets are skipped and reported by the node. A dry run sends no
controller goals and therefore has no measured Cartesian coverage.

## Supervised data collection

Stop the stack, set `COLLISION_CALIBRATION_DRY_RUN: false` and
`SENSORLESS_COLLISION_LOG_ENABLED: true`, then restart it. With the robot
stationary and the workspace clear, call the same `start` service. Stop at any
time with:

```bash
ros2 service call /zeroerr_collision_calibration_runner/stop std_srvs/srv/Trigger {}
```

Each run creates a timestamped directory under
`zeroerr_data/collision_detection/calibration_runs/` containing
`coverage_points.csv` and `coverage_summary.json`. The CSV records X/Y/Z and
all six joint positions during actual motion. Render XY, XZ, YZ, and 3-D views:

```bash
ros2 run zeroerr zeroerr_calibration_coverage_plot.py \
  /home/ilv/ros2_ws/eRob_moveit/zeroerr_data/collision_detection/calibration_runs/RUN_TIMESTAMP
```

This measured coverage describes the accepted and executed calibration paths,
not the entire theoretical reachable workspace. The configured joint sampling
box and coupled sample count control its extent and density; invalid targets or
transitions remain excluded by MoveIt.
