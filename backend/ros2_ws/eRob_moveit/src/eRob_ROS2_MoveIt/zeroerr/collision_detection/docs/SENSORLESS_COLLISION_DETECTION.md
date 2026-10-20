# Sensorless collision detection

## Profile-owned configuration

Each robot profile owns `config/<profile>/sensorless_collision.yaml`. Profile
selection follows `ACTIVE_PROFILE` in `config/runtime.yaml` or the existing
`ZEROERR_ACTIVE_PROFILE` environment override. Missing profile files fail startup;
there is no silent switch to another profile. Standalone ROS startup uses these
same files and does not depend on the platform.

The initial profile files explicitly include `../shared/sensorless_collision.yaml`
with `RUNTIME_INCLUDES`. Nested mappings merge recursively; arrays replace whole
arrays. Add only differing values to the profile file, for example:

```yaml
RUNTIME_INCLUDES:
- ../shared/sensorless_collision.yaml
controller:
  warmup_sec: 6.0
monitor:
  collision_sensitivity_percent: 110.0
runtime:
  EXECUTOR_COLLISION_STOP_STRATEGY: planned_path
```

The three sections are `controller` (startup observer/recovery/telemetry ROS
parameters), `monitor` (existing flat GUI/API detection fields and fitted model),
and `runtime` (recovery policy, stop strategies, collection and legacy settings).
All effective values were preserved during extraction. Shared robot motion limits
remain in `joint_limits.yaml`; the brake reads them instead of duplicating them.

The existing platform Robot Settings → Sensorless Collision tab and ROS
configuration messages retain their field names. Its live changes are atomically
saved as differences in the selected profile's `monitor` section, never into the
shared defaults or other profiles. Only live-supported detector fields apply
immediately. Editing startup observer parameters, runtime policy/strategy values
or model coefficients requires restarting/reconfiguring the backend. Calibration
fit tools accept the profile YAML and update only its model/threshold overrides;
historical explicit JSON inputs remain readable. The old global monitor JSON is
no longer a configuration source.

The Python runtime, launch helpers and C++ observer resolve the same profile file.
Collision settings left behind in runtime YAML overrides are rejected instead of
silently competing with the new source. The platform remains an API client in
this first extraction step; platform-owned full configuration is future work.


This document describes the deployed ZeroErr joint-torque collision detector,
its direction-dependent calibration models, the data needed to fit them, and
the runtime stop and recovery workflow.

The detector is an additional safety layer. It does not replace the emergency
stop, drive safety functions, guarding, supervision, or MoveIt geometric
collision checking. It estimates contact from actuator torque and a robot
model; contacts that produce little observable joint torque can remain below
threshold.

## Current validation status and known limitation

The current implementation is still under commissioning and is **not yet
validated as a production safety function**. Active stopping works, but normal
collision-free motion can still produce occasional false-positive detections.
On 2026-10-19, for example, the C++ real-time detector latched Joint 3 during
the collision-free transition from plate release into the blended plate-exit
trajectory. The configured 25 ms confirmation interval was exceeded, so this
was a sustained model/envelope miss rather than a single noisy sample.

An important suspected cause is selection bias in the current fitted residual
correction: peak-preserving samples were used during model fitting. Those
samples are useful for calibrating and validating a worst-case threshold
envelope, but they over-represent extreme residuals and are not an appropriate
substitute for uniformly sampled data when estimating the centre of normal
collision-free torque. Passing held-out peak sessions therefore does not prove
that all normal start, stop, reversal, blend, plate-entry, and plate-exit
regimes are covered.

Until the residual model is retrained on representative uniformly sampled
collision-free sessions and validated by holding out complete sessions and
motion regimes:

- treat active collision stopping as commissioning functionality;
- use supervised contact tests and collision-free process validation before
  enabling it on a deployment;
- do not respond to new false positives solely by repeatedly increasing joint
  thresholds, because that reduces sensitivity without correcting the model;
- use peak-preserving recordings for envelope validation, not as the primary
  residual-model training dataset.

The production design should also retain a bounded automatic trigger snapshot
containing residual, threshold, position, velocity, acceleration, and
exceedance duration. An external recorder may assist commissioning, but daily
manual recording must not be required for reliable operation or diagnosis.

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
finite stationary samples in one continuous stationary window; motion restarts
that window. Continuous motion cannot make the observer ready.

The controller reads position, velocity, torque sensor, statusword, and error
code directly from the loaned ros2_control state interfaces during the same
synchronous update. No DDS subscription or Python callback lies in the
detection path, and values from independently delivered topics are never mixed.
Observer integration, acceleration estimation, threshold evolution, and
confirmation all use the ros2_control period. Invalid/non-finite state or drives
that are not operation-enabled reset readiness and partial stationary warm-up,
but retain an already valid baseline.

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
  --config /path/to/config/development_short_links/sensorless_collision.yaml
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
  --config /path/to/zeroerr/config/<ACTIVE_PROFILE>/sensorless_collision.yaml
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
  --config /path/to/zeroerr/config/<ACTIVE_PROFILE>/sensorless_collision.yaml \
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
  --config /path/to/zeroerr/config/<ACTIVE_PROFILE>/sensorless_collision.yaml
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

### Recovery with a retained baseline (trial)

With `COLLISION_RESET_RECALIBRATE_ON_RELEASE: false` in the active profile `sensorless_collision.yaml` under `runtime`,
ordinary collision release retains a valid torque baseline. It reinitializes
momentum integration, filters, threshold envelopes and confirmation counters,
then requires the existing 2-second drive-stability interval and 0.5 seconds of
stationary, clear settling. Expected reset time is about 2.5 seconds when those
checks pass. Startup and explicit recalibration still require the full 8-second
stationary calibration. An invalid baseline also requires full calibration.
The runtime sends a distinct `recalibrate` boolean and logs `baseline_retained`;
coalesced observer requests give explicit recalibration precedence.

Recovery uses the normal collision thresholds, with no lower recovery margin.
Persistent torque above threshold keeps motion held and eventually times out;
it never automatically triggers recalibration of an already valid baseline.
Repeated releases do not change the baseline or learn away continuing contact.
If earlier pose/model offset problems return, inspect the residual diagnostics.
To restore full calibration on every ordinary release, set
`COLLISION_RESET_RECALIBRATE_ON_RELEASE: true` and restart ZeroErr.
For full calibration the robot must be stationary and free of external contact:
a sustained load present during calibration becomes part of the new baseline.
Movement restarts calibration.

The runtime holds motion throughout recovery. Duplicate reset requests return
`in_progress` without clearing the hold or sending another acknowledgement.
Release requires fresh ready telemetry carrying the acknowledgement generation
for this reset; an old ready sample cannot release motion. A new collision,
drive-enable failure or the 12-second recovery timeout leaves motion interlocked.
Timeout diagnostics include each joint's filtered residual, actual release limit,
velocity, observer initialization, drive-stable time and accumulated settling time,
plus telemetry age and acknowledgement generation in the runtime context.
The reset response names joints whose residual exceeds their release limit when
fresh telemetry for the current acknowledgement is available. Stale telemetry
or an unconfirmed acknowledgement is reported separately. A drive-disable
request during recovery ends the wait immediately and leaves motion interlocked;
recovery never automatically reverses an external disable request.
Real-hardware motion also requires fresh ready telemetry outside reset. Startup drive enable
uses the separate drive-enable readiness gate, which checks the motion interlock
and EtherCAT fault state without requiring observer readiness. Enabled drives
are needed for stationary observer calibration; automatic motion remains blocked
until calibration and the clear settling window complete.

When the physical load or model changes and a new stationary baseline is needed,
explicitly request full recalibration with the robot stationary and free of
external contact:

```bash
ros2 service call /zeroerr/collision_monitor/recalibrate std_srvs/srv/Trigger '{}'
```

This holds motion and relearns the baseline using the configured `warmup_sec`
(default 8 seconds). The baseline is not persisted across controller restarts.
Both `zeroerr` and `erob_moveit_runtime` must be rebuilt and restarted together;
a controller missing acknowledgement-generation telemetry cannot complete the
new reset workflow. Software regression tests cover recovery state transitions;
physical collision response still requires validation on the deployed robot.

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

`zeroerr/config/<ACTIVE_PROFILE>/sensorless_collision.yaml` contains the fitted model and
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


## Collision event logging

The controller emits one `[CollisionDiagnostics]` JSON snapshot for each latched
collision and each observer-ready transition. Collision snapshots have an
`event_id` matching `diagnostic_event_id` in the backend's `[CollisionMonitor]`
stop-request log. The snapshot's ROS timestamp is captured in the control loop;
the console timestamp is later because formatting/logging runs on a non-RT timer.
`event=observer_ready` describes initial calibration or acknowledgement-triggered
rearm completion, rather than a contact detection.

Each snapshot records all six joints' positions, measured velocities and filtered
accelerations, measured/compensated/expected torques, friction/pose/motion
corrections, calibration offsets, raw/filtered residuals, effective thresholds,
base floors, threshold envelopes, and continuous exceedance durations. Flags and
settings include detection/suppression/active-stop state, dynamic-threshold
settings, sensitivity, confirmation duration and observer/filter parameters.
Readiness age, warmup elapsed/sample count, acknowledgement/reset counts, update
period and overrun count describe recovery and observer timing.
`baseline_valid`, `observer_initialized`, and `rearm_settled_ms` distinguish
retained calibration from observer initialization and the stationary clear gate.

A rolling history contains up to 25 residual/threshold samples at approximately
10 ms intervals before the event. Array order is specified by `joint_order`;
`age_ms` is relative to the captured event timestamp. The history is cleared on
observer reset and may therefore be shorter than 250 ms immediately after
calibration. It is event evidence, not a continuous recording of missed contacts.

The stop request is published before diagnostic capture. Capture uses fixed-size
copies into a bounded single-producer/single-consumer queue, without waiting or
formatting JSON in the control loop. A full queue drops diagnostics only; later
snapshots expose the cumulative `dropped_diagnostic_events` count. The
`stop_publish_attempted` and `stop_published` fields distinguish detector trips
from publication to the stop-request topic; they do not certify a physical stop.

Backend logs add cached motion/interlock/readiness/suppression context and time
since reset completion to the collision event. `[CollisionStopDiagnostics]`
records the matching event ID, stop-call latency and returned stop result.
`[CollisionRecoveryDiagnostics]` records reset requests, successful reset
completion and observed readiness transitions. `[CollisionObserverReset]`
marks receipt of the observer acknowledgement and its recovery mode. Thresholds,
confirmation and suppression settings remain independently configured.
The detailed C++ snapshot appears in ROS console/launch logs; the backend context
also travels with `collision_event` into the platform failure register when that
failure is captured.

After updating these sources, rebuild `zeroerr` and `erob_moveit_runtime`, then
restart the robot backend/controller to load the new C++ plugin and Python files.
Do not infer that compiling the sources updates an already-running controller.

When the observer is uninitialized (including the drive-stability wait after a
reset), the torque plot publishes NaN samples at the readiness telemetry cadence.
These denote unavailable estimates and prevent interpolation from an old torque
residual to the reset value. Once initialized, live residuals remain visible even
while readiness is false; plotting does not change the collision or recovery gates.

### Separate collision and operator stopping profiles

The detector calls `RobotController.collision_stop()` and the coordinator selects
`send_collision_stop_trajectory()`. UI/process Stop continues to call
`stop_motion()` and uses the existing operator path-stop profile, including its
Joint_6 hold. Collision-specific settings use `EXECUTOR_COLLISION_STOP_*`; the
planned-path collision duration is 0.3 seconds with no held joints. Logs identify
`stop_kind=collision` or `stop_kind=operator`. A later process Stop does not
overwrite an active collision-stop trajectory.

The operator profile uses the existing planned-path algorithm. The collision
profile defaults to the measured-state brake described below. Selecting `planned_path`
restores the previous planned-path collision algorithm and cancellation
fallback. Neither path is a safety-rated drive stop function.

### Measured-state collision-brake trial

`EXECUTOR_COLLISION_STOP_STRATEGY: measured_ruckig` selects a local native Ruckig
velocity-control trajectory. It starts from measured joint positions, velocities
and a 10 Hz low-pass acceleration estimate from successive joint-state samples.
All six axes target zero velocity and acceleration with time synchronization;
there is no Joint_6 hold and no initial correction toward the planned path.
Acceleration/deceleration, velocity and jerk limits are read from the active
profile's `joint_limits.yaml` or its package default, and position bounds from
the expanded active URDF. Missing limits or a missing native library refuse this
brake; no invented joint-limit defaults are used.

The initial trial rejects feedback older than 50 ms (receipt and source stamp),
trajectories longer than 0.6 seconds, or per-axis excursions exceeding 0.35 rad.
These configurable rejection budgets are not validated stopping-distance claims.
Samples include each jerk-phase boundary, positions, velocities and accelerations,
so the controller can interpolate each constant-jerk segment. A zero trajectory
header starts execution on receipt. The collision goal also requires velocity
within 0.02 rad/s at completion. No waits for server discovery are allowed after
generating a measured-state brake.

Logs contain `generator=measured_ruckig`, state age, generated duration, initial
joint state and predicted per-axis travel. Result logs include measured endpoint
positions/velocities and feedback age. If generation fails, the controller is
unavailable or feedback expires before dispatch, the coordinator uses its existing
cancellation fallback and records the reason. A rejected brake requests cancellation
of the previous goal when its handle exists; an unavailable handle is explicitly
reported as unconfirmed. Execution-active collisions can submit a replacement brake
even when the previous goal handle is missing. Stale goal responses cannot erase a
new pending collision-stop request.

For a quick trial revert, set `EXECUTOR_COLLISION_STOP_STRATEGY: planned_path`
and restore `EXECUTOR_COLLISION_STOP_SAMPLE_PERIOD_S: 0.04`, then restart ZeroErr.
UI/process Stop retains its original Joint_6 hold in either mode. Native-library
and trajectory tests plus offline snapshots do not establish physical stopping
performance; verify measured deceleration, travel and drive faults at reduced
speed before drawing conclusions about the earlier abrupt stops.

### Stop strategy organization

`erob_moveit_runtime/scripts/motion/execution/stop_strategies/` contains separate
`planned_path.py` and `measured_ruckig.py` implementations. `base.py` defines the
`StopStrategy` interface and `StopPlan` result, including trajectory, held-joint
exemptions, final velocity tolerance, server timeout and optional dispatch deadline.
`TrajectoryExecutor` handles shared action submission and results without selecting
strategy-specific braking behavior. `braking_state.py` supplies shared measured
feedback; the Ruckig wrapper is `stop_strategies/ruckig_generator.py` and its native
implementation is `src_cpp/stop_strategies/measured_ruckig.cpp`.

Select `EXECUTOR_COLLISION_STOP_STRATEGY: measured_ruckig` or `planned_path` and
restart ZeroErr. To add a strategy, implement `build(executor, stop_duration_s=None)`
and register its name in `stop_strategies.STRATEGIES`. A refusal returns `(None,
reason)` and uses the existing cancellation fallback. A missing native dependency
or unknown strategy is logged and also leaves cancellation fallback active; it
never silently selects a different braking algorithm.

For older external configurations only, the deprecated
`EXECUTOR_COLLISION_STOP_USE_MEASURED_STATE` boolean maps to the corresponding
strategy if the named setting is absent. The named setting takes precedence.
Other robot packages without either setting retain `planned_path`. Strategy
selection does not alter the regular operator/process Stop profile.
