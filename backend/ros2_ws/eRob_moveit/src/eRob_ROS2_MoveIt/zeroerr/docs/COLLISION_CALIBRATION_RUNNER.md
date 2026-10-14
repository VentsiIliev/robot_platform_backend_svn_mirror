# Sensorless collision calibration runner

This is the operator runbook for collecting coverage and clean model-training
data. The model, direction dependence, fitting acceptance rules, thresholds and
runtime behavior are documented in
[`SENSORLESS_COLLISION_DETECTION.md`](SENSORLESS_COLLISION_DETECTION.md).

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

## Passive recording of real process motion

For production-representative calibration, let the platform own the motion and
use the runner only as a recorder:

```bash
ros2 service call /zeroerr_collision_calibration_runner/start_external \
  std_srvs/srv/Trigger '{}'
```

Run clean dry-run or production trajectories, including representative
positive/negative directions, poses, velocity and acceleration settings. Then
finalize the session:

```bash
ros2 service call /zeroerr_collision_calibration_runner/stop \
  std_srvs/srv/Trigger '{}'
```

The REST bridge exposes the same workflow through:

```text
POST /collision/calibration/recording/start
POST /collision/calibration/recording/stop
```

External-motion runs additionally contain `collision_training.csv`. Samples are
flushed to disk during capture; stopping closes the file and writes the final
coverage summary.

## Data acceptance rules

Use a run for fitting only when it is collision-free and representative. Exclude
runs containing deliberate pushes, impacts, unexpected workpiece/tool contact,
drive faults, emergency stops, payload changes or abnormal controller behavior.
Do not delete legitimate collision-free peaks simply to lower thresholds.

Collect multiple timestamp-separated sessions. Cover both directions for every
moving joint because normal residual torque and transient magnitude are
direction dependent. Include the complete production speed, acceleration, pose,
tool and payload envelope.

Before fitting, verify:

- six synchronized joint rows per sample time;
- finite position, velocity, acceleration and torque fields;
- session duration and timestamp continuity;
- signed velocity/acceleration coverage per joint;
- residual p95/p99/max and the source of large time-localized spikes;
- Cartesian and joint-space coverage against actual production motion.

## Model build order

Build and validate the observer correction before fitting thresholds:

1. Combine at least two clean sessions into one training CSV with one header.
2. Preview `zeroerr_residual_model_fit.py` and inspect its held-out-session
   report.
3. Apply only accepted correction fits.
4. Preview `zeroerr_dynamic_threshold_fit.py` using the clean run timestamp
   bounds.
5. Review per-joint sample count, exceedance fraction, training limits and
   threshold range; then apply.
6. Restart the backend and validate first in passive mode across the full motion
   envelope.
7. Perform supervised contact tests before enabling active stopping.

Exact commands, feature definitions, formulas and acceptance criteria are in
`SENSORLESS_COLLISION_DETECTION.md`.
