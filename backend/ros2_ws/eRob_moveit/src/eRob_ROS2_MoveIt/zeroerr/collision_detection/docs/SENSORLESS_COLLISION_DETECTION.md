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
6. Require continuous threshold exceedance for `confirm_duration_ms`, measured
   from the synchronous controller periods.
7. In passive mode, report and latch the collision. In active mode, also stop
   motion and activate the backend motion interlock.
8. Keep new motion and drive-enable requests blocked until the platform
   operator acknowledges the collision.

The production implementation is the C++ ros2_control plugin
`zeroerr/RealtimeCollisionController` in
`zeroerr/collision_detection/runtime/src/realtime_collision_controller.cpp`.
The former Python node
`zeroerr_collision_monitor.py` is deprecated, is not launched, and is retained
only for offline comparison and legacy tests. It is not a runtime fallback.

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

`zeroerr_motion_model_fit.py` reproducibly fits friction, pose, and
`motion_residual_correction_coefficients` together and validates them by holding
out each complete session. The older `zeroerr_residual_model_fit.py` is retained
for comparison with historical symmetric-friction fits and should not be used
for new deployments.

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
active until all observer inputs are valid and warm-up has completed. Warm-up
requires both the configured elapsed time and `warmup_min_samples` complete,
finite stationary samples; continuous motion cannot make the observer ready.

The controller reads position, velocity, torque sensor, statusword, and error
code directly from the loaned ros2_control state interfaces during the same
synchronous update. No DDS subscription or Python callback lies in the
detection path, and values from independently delivered topics are never mixed.
Observer integration, acceleration estimation, threshold evolution, and
confirmation all use the ros2_control period. Invalid/non-finite state or drives
that are not operation-enabled reset readiness and stationary warm-up.

Changing the update rate changes the discrete observer filter and the sampled
velocity/acceleration distribution. Refit and validate models using clean data
captured under the deployed controller rate before raising sensitivity or
enabling production stopping.

Torque telemetry deliberately distinguishes two model quantities:

- `observer_auxiliary_torque`: the Eq. (7) auxiliary term used internally by
  the generalized-momentum observer;
- `expected_torque`: full inverse-dynamics torque
  `M(q)ddq + C(q,dq)dq + g(q)`, plus deployed bias/correction terms, used for
  diagnostics and residual-model calibration.

The auxiliary term must not be substituted with full inverse dynamics inside
the observer equation. Conversely, calibration must not treat the auxiliary
term as the full expected actuator torque.

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
The fitter uses non-negative least squares with ridge regularization. All motion
coefficients are therefore non-negative: increasing any directional velocity or
acceleration feature cannot reduce the fitted threshold. The static floor and
maximum-ratio clamp remain independent runtime safeguards.

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
- `confirm_duration_ms` requires continuous threshold exceedance for a fixed
  controller-period duration. Its behavior is independent of ROS diagnostics;
  increasing it rejects longer spikes at the cost of detection delay.

Sensitivity and confirmation duration are operational adjustments, not substitutes
for representative clean data. Validate every change through the full production
motion range and with supervised contact tests.

## Runtime timing diagnostics

`/zeroerr/collision_rt/timing` reports cumulative controller updates, update
overruns, latest/max observer execution time, readiness, and the implementation
identifier `cpp_realtime`. The controller update count—not the PlotJuggler topic
rate—is the authoritative observer-rate measurement.

Verified on 2026-10-16 at a 2 kHz ros2_control/EtherCAT rate:

- controller active and Python observer absent;
- 153,984 synchronous updates observed;
- zero overruns;
- latest measured update 55.629 us;
- maximum measured update 81.801 us, below the 500 us cycle budget;
- observer ready after stationary warm-up.

## In-process 2 kHz controller

`zeroerr/RealtimeCollisionController` runs inside the synchronous
`controller_manager` update loop. It reads each joint's `position`, `velocity`,
and `torque_sensor` loaned state interfaces directly after the EtherCAT hardware
read, then runs the KDL momentum observer and time-based threshold decision.
This controller is the sole production collision observer. The former
`zeroerr_collision_monitor.py` implementation is deprecated, is not started by
the launch files, and is retained only for offline comparison and legacy tests.
ROS is used for the existing runtime control contracts and diagnostics:

- `/zeroerr/collision_monitor/config` and `config_state` for live platform settings;
- `/zeroerr/collision_monitor/acknowledged` for explicit latch reset and warm-up;
- `/zeroerr/collision_monitor/stop_request` for active collision response;
- `/zeroerr/collision_monitor/state` for observer readiness;
- `/zeroerr/collision_monitor/plot/external_torque` and
  `/zeroerr/collision_monitor/plot/external_torque_threshold`, attempted at the
  configured plot period (0.5 ms / 2 kHz by default);
- `/zeroerr/collision_rt/timing`

`active_stop_enabled` is controlled live by the platform. When enabled, a
confirmed threshold crossing remains latched until the operator acknowledgement
is received; acknowledgement restarts observer warm-up before recovery motion is
released. Confirm that `last_update_us` stays below the 500 us cycle budget and
`overruns` remains zero. Plot publication is independent of the 100 Hz timing
telemetry and may be disabled with `diagnostics_enabled` without disabling
collision decisions.

Plot topics are explicitly best-effort diagnostics. Their
`RealtimePublisher::trylock()` calls never block the controller; a busy ROS
transport may therefore skip diagnostic publications. In the 2026-10-16 test,
`ros2 topic hz` received roughly 1.11-1.14 kHz even though the authoritative
controller counter ran at 2 kHz with zero overruns. This is expected separation:
the observer and decision execute at 2 kHz, while ROS/PlotJuggler delivery is
not guaranteed at 2 kHz. Do not replace the non-blocking publisher with a
blocking publish operation merely to improve graph density.

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

### Peak-preserving C++ recorder

The real-time controller examines every 2 kHz update and retains, independently
for every joint, the sample with the largest absolute observer residual in each
10 ms timing window. It publishes those compact snapshots on
`/zeroerr/collision_rt/peak_samples`. This preserves short start/stop/reversal
transients without performing disk I/O or blocking ROS publication in the
control loop.

Record one collision-free production session with:

```bash
ros2 run zeroerr zeroerr_peak_recorder.py
```

Stop with Ctrl-C. Each run creates a new directory under
`~/zeroerr_data/collision_detection/peak_sessions/` containing
`peak_samples.csv` and `metadata.json`. Use separate runs for training and
held-out validation. Never include supervised contact tests in model-fitting
inputs.

The peak stream is intended for false-positive/tail modeling. Keep ordinary
collision-free trajectory coverage as well, because peak-only samples do not
represent the centre of the residual distribution.

### Torque, timestamp, payload, and URDF audit

Run the audit against every candidate session and the exact expanded URDF used
at runtime:

```bash
ros2 run zeroerr zeroerr_collision_model_audit.py \
  --input SESSION_1/peak_samples.csv \
  --input SESSION_2/peak_samples.csv \
  --urdf /path/to/runtime-expanded.urdf \
  --output collision_model_audit.json
```

The report checks timestamp intervals, software torque-channel scale/sign
agreement, observed joint ranges, URDF limits, and declared link mass. Matching
`torque_sensor` and `measured_torque` proves only software consistency. Absolute
Nm scaling still requires a traceable known-load test, and declared URDF mass
must be checked against the physically installed tool/payload.

An audit of the historical combined CSV on 2026-10-16 found exact internal
torque-channel agreement, but also found an observed J5 range beyond the chosen
URDF upper limit and implausible 1000 rad/s velocity limits in that URDF. These
must be resolved against the actual runtime URDF before treating its limits as
physical validation.

### Reproducible motion-model fit

The deployed model can be regenerated with session-held-out validation:

```bash
ros2 run zeroerr zeroerr_motion_model_fit.py \
  --input SESSION_1/peak_samples.csv \
  --input SESSION_2/peak_samples.csv \
  --input SESSION_3/peak_samples.csv \
  --config /path/to/collision_monitor_config.json
```

Preview mode writes `motion_model_fit_report.json`. Add `--apply` only after
every joint improves both held-out RMSE and held-out p99 absolute residual in
every session. Partial deployment is refused. The fitted model contains:

- positive/negative Coulomb friction;
- positive/negative static friction;
- a smooth zero-velocity transition and Stribeck decay;
- viscous friction;
- pose-dependent trigonometric correction;
- signed velocity and acceleration motion-residual correction.

Acceleration is now derived at 2 kHz and passed through a deterministic
first-order low-pass filter (`acceleration_filter_cutoff_hz`, default 40 Hz)
before inverse dynamics, correction, and threshold features. Any change to this
cutoff requires new sessions and a refit.

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
  --config /path/to/zeroerr/collision_detection/config/collision_monitor_config.json
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
  --config /path/to/zeroerr/collision_detection/config/collision_monitor_config.json \
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
  --config /path/to/zeroerr/collision_detection/config/collision_monitor_config.json
```

Defaults fit the 99.9th percentile and apply a 1.10 margin. The non-negative
ridge fit guarantees a monotonic motion envelope. Each joint requires at least
100 usable samples. The output reports sample count, calibration exceedance
fraction, maximum covered velocity/acceleration and predicted threshold range.

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

Suppression also places the runtime controller in **recovery-only motion mode**.
Drive enable is permitted so the operator can recover from a stopped state, but
the normal hardware-ready gate remains false. Only a linear request carrying
the explicit `allow_collision_recovery` authorization is admitted. Paint
process motion, ordered chains, PTP, fast-LIN, and all other unflagged requests
remain rejected. This prevents an automatic process start from slipping through
while the detector is suppressed. EtherCAT/drive faults are never bypassed.

## Main configuration fields

`zeroerr/collision_detection/config/collision_monitor_config.json` contains the fitted model and
operational settings:

- `detection_enabled`: global runtime enable/disable switch for new detections;
- `effort_following_error_detection_enabled`: deprecated and forced off because
  the C++ torque observer is the only production detector;
- `external_torque_thresholds`: per-joint static floors;
- `dynamic_threshold_coefficients`: direction-aware envelope model;
- `dynamic_threshold_training_limits`: maximum trained `|dq|` and `|ddq|`;
- `dynamic_threshold_decay_sec`: transient-envelope decay;
- `dynamic_threshold_max_ratio`: upper cap relative to static floor;
- `collision_sensitivity_percent`: global calibrated-threshold scale;
- `confirm_duration_ms`: continuous measurement-time exceedance required to latch;
- `active_stop_enabled`: publish a stop request after a confirmed collision;
- `diagnostics_enabled`: opt-in publication of high-rate, per-joint PlotJuggler
  topics under `/zeroerr/collision_monitor/plot/*`;
- `friction_coulomb_nm`, `friction_viscous_nm_per_rad_s`: drivetrain model;
- `position_correction_coefficients`: pose-dependent correction;
- `motion_residual_correction_coefficients`: signed velocity/acceleration
  correction;
- `motion_residual_correction_limits`: correction training envelope.

`zeroerr/config/ros2_controllers.yaml` controls the C++ observer gain, plot and
timing publication periods, stationary warm-up, drive-stability gate, links,
and joint interfaces. `zeroerr/config/runtime.yaml` retains non-real-time GUI
and calibration-runner settings; it no longer selects a Python production
observer.

## Live observer diagnostics

Robot Settings → Sensorless Collision provides **Live observer diagnostics** and
**Open PlotJuggler** controls. Diagnostics do not alter thresholds, latching, or
the active/passive response. They attempt non-blocking publication at the
configured plot period while enabled. The supplied layout compares all six
joints for:

- filtered external torque;
- the current motion-dependent positive threshold.

The threshold is symmetric, so its negative boundary is the negated published
value. Plot delivery may be lower than 2 kHz and must not be used to infer the
observer execution rate; use `/zeroerr/collision_rt/timing` instead.

The backend endpoint `POST /collision/monitor/diagnostics/open` enables the
streams and launches the installed layout
`zeroerr/collision_detection/diagnostics/collision_observer_plotjuggler.xml`.
The installed compatibility path remains `share/zeroerr/config/`. Install the optional GUI on
the backend workstation with `sudo apt install ros-jazzy-plotjuggler-ros`.
Disable the platform switch after testing to stop the additional plot traffic.

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

- `zeroerr/collision_detection/docs/COLLISION_CALIBRATION_RUNNER.md`: operator runbook.
- `zeroerr/docs/ACTUATOR_MASS_MODELING.md`: robot dynamics assumptions.
- `zeroerr/docs/MOTOR_MASS_ASSUMPTIONS.md`: actuator mass assumptions.
- `zeroerr/collision_detection/calibration/data_collection/zeroerr_calibration_coverage_plot.py`:
  coverage plots.
- `zeroerr/collision_detection/diagnostics/zeroerr_collision_status_gui.py`:
  diagnostic status GUI.
- `docs/A_universal_algorithm_for_sensorless_collision_det.pdf`: background
  paper; the deployed implementation is the repository code and configuration
  documented here.
