# Sensorless collision detection

This document describes the deployed ZeroErr joint-torque collision detector,
its direction-dependent calibration models, the data needed to fit them, and
the runtime stop and recovery workflow.

The detector is an additional safety layer. It does not replace the emergency
stop, drive safety functions, guarding, supervision, or MoveIt geometric
collision checking. It estimates contact from actuator torque and a robot
model; contacts that produce little observable joint torque can remain below
threshold.

## System overview

The runtime pipeline is:

1. Read synchronized joint position, velocity, torque sensor and drive state.
2. Reject invalid data and wait for stable, operation-enabled drives.
3. Compensate measured torque for identified friction, pose-dependent model
   error, and repeatable direction-dependent motion residual.
4. Run the generalized-momentum observer to estimate external joint torque.
5. Compute a direction- and motion-conditioned threshold for every joint.
6. Require the configured number of consecutive threshold exceedances.
7. In passive mode, report and latch the collision. In active mode, also stop
   motion and activate the backend motion interlock.
8. Keep new motion and drive-enable requests blocked until the platform
   operator acknowledges the collision.

The primary implementation is
`zeroerr/scripts/zeroerr_collision_monitor.py`. The reusable dynamics classes
are under
`erob_moveit_runtime/scripts/safety/collision_detection/`.

## Why the model is direction dependent

Collision-free commissioning data showed that the normal torque residual is
not symmetric when a joint reverses direction. At the same absolute speed and
acceleration, positive and negative motion can have different residual centre,
spread, and transient peak. Causes include Coulomb friction, reducer and seal
asymmetry, drive/torque-estimator behavior, cable loading, gravity-model error,
and controller tracking transients.

A model based only on `abs(velocity)` or one threshold per joint therefore
forces a poor compromise:

- a high threshold avoids false positives in the noisier direction but misses
  lighter contacts in the quieter direction;
- a low threshold detects lighter contacts but trips during legitimate motion
  in the noisier direction.

ZeroErr handles this in two separate layers:

- **direction-aware residual correction** removes repeatable signed model error
  before the observer;
- **direction-aware dynamic thresholding** models the remaining collision-free
  residual envelope without hiding the residual itself.

These layers must not be confused. The correction predicts the expected
collision-free torque. The threshold predicts how large the remaining error may
legitimately become.

## Torque and observer model

### Measured-torque compensation

For joint `j`, the monitor supplies the observer with approximately:

```text
tau_compensated = tau_measured
                - tau_friction
                - tau_pose_correction
                - tau_motion_correction
```

The friction model is:

```text
tau_friction = coulomb_j * sign(dq_j) + viscous_j * dq_j
```

`sign(dq_j)` is zero inside `friction_velocity_deadband_rad_s`.

The pose correction is a small physics-shaped trigonometric model using the
principal serial-chain gravity angles:

```text
[1,
 sin(q2), cos(q2),
 sin(q2+q3), cos(q2+q3),
 sin(q2+q3+q4), cos(q2+q3+q4),
 sin(q3), cos(q3)]
```

Each joint has its own coefficients. This structure interpolates across poses
and avoids a workspace lookup table.

The direction-aware motion correction uses:

```text
[dq+, dq-, dq+^2, dq-^2, ddq+, ddq-]
```

where `x+ = max(x, 0)` and `x- = max(-x, 0)`. Velocity and acceleration are
clipped to the range covered by training data. Extrapolation beyond measured
motion is deliberately not allowed.

Current tooling note: `zeroerr_residual_model_fit.py` fits Coulomb/viscous
friction and pose correction. It does **not** generate
`motion_residual_correction_coefficients`. Those coefficients are runtime-
supported deployed calibration data, but this repository currently has no
standalone reproducible fitter for them. Do not hand-tune or regenerate them
without adding an equivalent session-held-out fitting and validation tool. The
fully reproducible direction-aware fitter currently provided by the repository
is the dynamic-threshold fitter described below.

### Generalized-momentum observer

The deployed estimator is `momentum_observer`. It uses joint momentum
`p = M(q)dq` and the rigid-body model's auxiliary/bias torque. This avoids
directly inserting noisy measured acceleration into the inverse-dynamics
residual. The observer residual is low-pass filtered and exposed as estimated
external joint torque.

At startup, and after drive recovery when initialization was interrupted, the
observer learns stationary model/drive bias for `warmup_sec` while velocity is
below `warmup_vel_threshold_rad_s`. External torque is reported as unavailable,
not zero, during this interval. Collision protection must be treated as not
active until all observer inputs are valid and warm-up has completed.

Changing payload, tooling, mounting, torque scaling, drivetrain behavior, URDF
inertials, controller tuning, or the normal motion envelope invalidates some or
all of the calibration and requires new clean data.

## Direction-aware threshold model

The fitted dynamic threshold uses one coefficient vector per joint and these
features:

```text
[1,
 dq+, dq-, ddq+, ddq-,
 dq+^2, dq-^2, ddq+^2, ddq-^2]
```

Positive and negative velocity and acceleration are independent features. A
decaying peak envelope (`dynamic_threshold_decay_sec`) holds recent motion
briefly so acceleration or reversal transients are not forgotten immediately.

At runtime:

```text
fitted = coefficients_j dot features
base   = clamp(max(static_floor_j, fitted),
               static_floor_j,
               static_floor_j * dynamic_threshold_max_ratio)
threshold = base * (100 / collision_sensitivity_percent)
```

Thus:

- 100% is the calibrated threshold;
- above 100% is more sensitive and lowers thresholds;
- below 100% is less sensitive and raises thresholds;
- `dynamic_threshold_max_ratio` limits how much fast motion can mask contact;
- `confirm_cycles` rejects isolated spikes at the cost of detection delay.

Sensitivity and confirmation count are operational adjustments, not substitutes
for representative clean data. Validate every change through the full production
motion range and with supervised contact tests.

## Collision-free data collection

Only collision-free data is valid for model fitting. Do not include deliberate
pushes, impacts, workpiece contact, emergency stops, drive faults, unexpected
payload changes, or motion executed while something touches the robot.

The best dataset contains multiple timestamp-separated sessions and covers:

- the real tools and payloads that will be protected;
- the actual paint, pickup, transfer, drop-off and return trajectories;
- positive and negative motion for each moving joint;
- slow, medium and maximum production velocity/acceleration combinations;
- starts, stops, reversals, blended motion and stationary dwell;
- the production joint-space and Cartesian workspace;
- repeated cycles so rare but legitimate peaks are represented.

Do not collect only slow calibration sweeps if production runs faster. Do not
fit deliberate collision samples as normal behavior. Keep raw sessions so a
bad session can be removed and the model reproduced.

### External-motion recording

The calibration runner can passively record motion owned by the platform:

```bash
ros2 service call /zeroerr_collision_calibration_runner/start_external \
  std_srvs/srv/Trigger '{}'
```

Run the desired clean production or dry-run cycles, then stop and finalize:

```bash
ros2 service call /zeroerr_collision_calibration_runner/stop \
  std_srvs/srv/Trigger '{}'
```

The platform REST equivalents are:

```text
POST /collision/calibration/recording/start
POST /collision/calibration/recording/stop
```

Each run is stored under
`zeroerr_data/collision_detection/calibration_runs/<timestamp>/` and contains:

- `coverage_points.csv`: timestamped TCP and joint-space coverage;
- `collision_training.csv`: synchronized per-joint position, velocity,
  acceleration, measured/expected/external torque and following error;
- `coverage_summary.json`: run type, coverage, accepted/rejected motion and
  captured event summary.

Training CSV rows are flushed while recording, so data is present on disk
during a long session. A normal stop is still required to close files and write
the final summary.

## Reviewing data before fitting

Before using a session:

1. Confirm it lasted for the expected interval and contains six synchronized
   joint rows per timestamp.
2. Check for NaN/inf, timestamp gaps, missing joints and implausible velocity,
   acceleration or torque values.
3. Review maximum velocity and acceleration per direction and per joint.
4. Compare sessions and inspect residual distributions, p95, p99, maximum and
   the largest time-localized spikes.
5. Match spikes to drive faults, emergency stops, operator contact or abnormal
   process events and exclude contaminated intervals/sessions.
6. Inspect positive and negative motion separately. Combining their statistics
   hides the asymmetry the model is intended to learn.
7. Verify coverage includes the production motions to be protected.

Never remove a legitimate clean-motion peak merely to obtain a lower threshold.
First determine its physical cause. A threshold trained after deleting real
normal behavior will false-trigger in production.

## Building the residual model

Combine clean, complete sessions into one CSV with a single header. Keep gaps
of more than five seconds between sessions; the fitter uses timestamp gaps to
create held-out validation folds. At least two sessions and 200 complete
synchronized samples are required.

Preview the robust ridge/Huber fit:

```bash
ros2 run zeroerr zeroerr_residual_model_fit.py \
  --input /path/to/combined_collision_training.csv \
  --config /path/to/zeroerr/config/collision_monitor_config.json
```

The fitted target is:

```text
measured_torque_nm - expected_torque_nm
```

The design contains signed friction, velocity, and the pose features described
above. Each session is held out in turn. A joint fit is accepted only when every
held-out session improves RMSE and p99 absolute residual, while MAE may degrade
by no more than 15%. Rejected joints retain their existing coefficients.

Review `residual_model_fit_report.json`, then apply only after the validation
results are acceptable:

```bash
ros2 run zeroerr zeroerr_residual_model_fit.py \
  --input /path/to/combined_collision_training.csv \
  --config /path/to/zeroerr/config/collision_monitor_config.json \
  --apply
```

The script backs up the previous configuration beside the input data.

## Fitting direction-aware thresholds

Fit thresholds only after the residual model has been selected. Use the clean
torque log plus the timestamp bounds of one or more recorded run directories:

```bash
ros2 run zeroerr zeroerr_dynamic_threshold_fit.py \
  --input /path/to/collision_training.csv \
  --run /path/to/calibration_runs/run_1 \
  --run /path/to/calibration_runs/run_2 \
  --config /path/to/zeroerr/config/collision_monitor_config.json
```

Defaults fit the 99.9th percentile and apply a 1.10 margin. Each joint requires
at least 100 usable samples. The output reports sample count, calibration
exceedance fraction, maximum covered velocity/acceleration and predicted
threshold range.

After reviewing the preview, repeat with `--apply`. The script writes:

- `dynamic_threshold_coefficients`;
- `dynamic_threshold_training_limits`;
- `dynamic_threshold_decay_sec`;
- fit provenance and summary under `dynamic_threshold_fit`.

It also backs up the previous monitor configuration. Runtime inputs are clipped
to the training limits, and the result remains bounded by the static floor and
`dynamic_threshold_max_ratio`.

## Deployment and validation

After applying a fit:

1. Rebuild/install `zeroerr` if required by the workspace layout.
2. Restart the backend; do not assume a source JSON edit changed a running node.
3. Start in passive/report-only mode.
4. Confirm the GUI shows valid inputs and completed warm-up.
5. Repeat collision-free production trajectories across the full speed,
   acceleration, direction, pose, tool and payload envelope.
6. Investigate every false positive; do not immediately hide it with global
   sensitivity.
7. Perform supervised contact tests at stationary, slow and fast motion. Test
   several contact directions and links because the joint-torque projection is
   configuration dependent.
8. Only then enable active stop and verify motion cancellation, queue clearing,
   platform notification, pump shutdown where applicable, latch persistence and
   operator acknowledgement.

A slowly applied load and an impact are not equivalent tests. An impact creates
a sharper residual. A gradual load can distribute torque across joints, lie
near model/bias uncertainty, or have poor leverage at the measured joints. The
detector acts on joint torque, not object mass or Cartesian force directly.

## Runtime modes, latch and acknowledgement

In **passive** mode the monitor reports and latches detections but does not
request a stop. In **active** mode it publishes a stop request. The runtime then:

- cancels/stops current motion and clears queued motion;
- activates the global motion interlock;
- rejects subsequent motion and drive-enable requests;
- notifies the platform with the joint and detector reason.

The latch is cleared from the platform operator acknowledgement workflow, not
from the diagnostic monitor GUI. A reset is accepted only after the configured
rearm/warm-up conditions permit safe release. If the physical/model condition
still exceeds threshold, the detector can latch again immediately; clearing a
latch does not suppress a continuing collision.

Relevant interfaces include:

```text
GET  /motion/interlock/status
POST /motion/interlock/reset
```

## Recovery Jog suppression

Recovery Jog intentionally suppresses sensorless detection so an operator can
move away from a condition that would otherwise re-latch continuously. This is
a narrowly scoped recovery function, not normal operation.

The platform calls:

```text
POST /collision/monitor/suppression
{"suppressed": true|false}
```

The backend publishes the runtime update and waits for the monitor's
`config_state` confirmation. If confirmation is missing, the request fails and
the platform must not enable Recovery Jog. Detection is restored when Recovery
Jog is switched off and when the jog screen closes. Existing latches are not
silently cleared by suppression; operator acknowledgement remains separate.

While suppressed, the monitor clears active/cycle counters and reports
`suppressed by recovery jog`, but preserves an existing latch. The operator must
use reduced speed, maintain supervision, and restore collision detection before
returning to automatic motion.

## Main configuration fields

`zeroerr/config/collision_monitor_config.json` contains the fitted model and
operational settings:

- `external_torque_thresholds`: per-joint static floors;
- `dynamic_threshold_coefficients`: direction-aware envelope model;
- `dynamic_threshold_training_limits`: maximum trained `|dq|` and `|ddq|`;
- `dynamic_threshold_decay_sec`: transient-envelope decay;
- `dynamic_threshold_max_ratio`: upper cap relative to static floor;
- `collision_sensitivity_percent`: global calibrated-threshold scale;
- `confirm_cycles`: consecutive detections required to latch;
- `active_stop_enabled`: report-only versus stop-motion behavior;
- `friction_coulomb_nm`, `friction_viscous_nm_per_rad_s`: drivetrain model;
- `position_correction_coefficients`: pose-dependent correction;
- `motion_residual_correction_coefficients`: signed velocity/acceleration
  correction;
- `motion_residual_correction_limits`: correction training envelope.

`zeroerr/config/runtime.yaml` controls monitor launch, period, observer gain,
drive-stability gate, warm-up, raw logging, GUI launch and calibration-runner
settings.

## Troubleshooting principles

- **False positives in one direction only:** inspect signed residuals and data
  coverage; do not replace the model with an absolute-speed fit.
- **Insensitive during fast motion:** inspect dynamic threshold and max-ratio,
  but first confirm fast collision-free training coverage and residual-model
  accuracy.
- **Sensitive while stationary but not to a placed mass:** examine joint torque
  leverage and residual values; object mass alone does not define detectability.
- **GUI shows zero after a drive event:** zero during warm-up is not a valid
  estimate. Current state should expose unavailable inputs/protection warming.
- **Immediate re-latch after acknowledgement:** the residual still exceeds the
  threshold. Remove the contact or use controlled Recovery Jog; do not repeatedly
  clear the latch.
- **Model works in one tool/payload only:** collect and validate the deployed
  payload envelope or maintain separately selected calibrations.

## Related documents and tools

- `zeroerr/docs/COLLISION_CALIBRATION_RUNNER.md`: operator runbook.
- `zeroerr/docs/ACTUATOR_MASS_MODELING.md`: robot dynamics assumptions.
- `zeroerr/docs/MOTOR_MASS_ASSUMPTIONS.md`: actuator mass assumptions.
- `zeroerr/scripts/zeroerr_calibration_coverage_plot.py`: coverage plots.
- `zeroerr/scripts/zeroerr_collision_status_gui.py`: diagnostic status GUI.
- `docs/A_universal_algorithm_for_sensorless_collision_det.pdf`: background
  paper; the deployed implementation is the repository code and configuration
  documented here.
