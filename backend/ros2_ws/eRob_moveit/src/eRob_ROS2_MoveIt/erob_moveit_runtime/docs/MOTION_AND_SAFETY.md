# Motion And Safety

## Motion Lifecycle

### 1. Request acceptance

A request enters through:
- REST
- or direct strategy execution on `RobotController`

`MotionCoordinator.execute()` decides whether the request:
- executes immediately
- is queued
- is rejected because a non-queueable command was sent while busy

### 2. Planning

Single targets and paths both use MoveIt Cartesian planning modules under `motion/planning/`.

Important planning helpers:
- `_build_cartesian_request()` in `trajectory_planner.py`
- `_cartesian_path_response()` in `trajectory_planner.py`
- staged path approach flow in `trajectory.py`
- Jacobian fallback in `jacobian_move.py`

### 3. Trajectory optimization

After raw MoveIt joint trajectories are produced, they are time-parameterized through:
- TOTG helper
- or Ruckig helper

Selection is controlled by:
- `config.TRAJECTORY_OPTIMIZER`

### 4. Controller execution

Timed trajectories are sent through the FollowJointTrajectory action client.

`TrajectoryExecutor` owns:
- goal submission
- result handling
- handoff to queued motion when one goal completes

## Safety Layers

### Local workspace safety

`SafetyWallManager.check_position_safety()` validates raw target XYZ against configured workspace bounds before planning.

Inputs come from:
- workspace extracted from URDF
- XY expansion configured by `WALL_XY_OFFSET_M`
- soft warning margin configured by `SAFETY_MARGIN_M`

### MoveIt planning-scene safety walls

`SafetyWallManager` also publishes wall collision objects into the MoveIt planning scene and matching RViz markers.

Capabilities:
- enable / disable walls
- republish on demand
- clear from planning scene
- expose status through REST

Allowed-collision support:
- `WALL_BYPASS_LINKS` can suppress selected link-wall contacts inside the ACM

### Collision diagnostics

Planner diagnostics distinguish:
- start-state collision
- FK mismatch / bad start-state assumptions
- IK/reachability failures

### Dynamics-based collision detector

The production ZeroErr observer is the C++ `zeroerr/RealtimeCollisionController`
running inside the synchronous controller-manager update loop. It reads loaned
joint/drive interfaces after hardware read. `scripts/safety/collision_detection/`
contains Python models/estimators for offline/legacy use;
`zeroerr_collision_monitor.py` is deprecated and is not launched in production.

The production estimator is a generalized-momentum observer with calibrated
friction, pose-residual and signed velocity/acceleration compensation. Both its
residual correction and motion-conditioned thresholds distinguish positive and
negative motion because collision-free torque behavior was found to be
direction dependent.

The monitor fails closed on incomplete, stale, unsynchronized or non-finite
joint/drive samples. Such an input invalidates observer readiness and restarts
stationary warm-up. Readiness requires both elapsed warm-up time and a minimum
count of valid stationary samples. Telemetry exposes the observer auxiliary
term separately from the full inverse-dynamics `expected_torque` used for
calibration.

The detector supports passive reporting and active stopping. In active mode a
confirmed detection stops current motion, clears queued motion, latches the
runtime motion interlock and blocks later motion/drive-enable requests until
operator acknowledgement. Recovery Jog can temporarily suppress detection, but
the backend must confirm suppression and detection is restored on exit.

See the [sensorless collision runbook](../../zeroerr/collision_detection/docs/SENSORLESS_COLLISION_DETECTION.md) for the equations, clean
data requirements, fitting procedure, validation, latch workflow and Recovery
Jog behavior.

## Reachability Precheck Versus Real Execution

### `POST /reachability/pose`

Intended for:
- UI prechecks
- simulation of planned measurement order
- quick “can I use this point?” validation

It now uses:
- IK for start
- IK for target with start seed
- `check_state_validity` on the target joint state

Pros:
- much faster than full Cartesian planning
- keeps endpoint collision detection
- keeps joint-limit and reachability filtering

Cons:
- does not validate the full path between the two poses

### Real execution

Actual motion commands still use the normal planner/executor path.
That remains the authority for:
- full path feasibility
- partial-cartesian-path rejection rules
- real controller execution success/failure

## Important Config Knobs

These names are exposed by `scripts/config.py`, which loads the selected robot
package/profile YAML composition. Change their owning configuration file rather
than editing the loader. Sensorless stop/recovery settings have their own
profile file, described below.

- `CARTESIAN_MIN_FRACTION`
- `WALL_XY_OFFSET_M`
- `SAFETY_MARGIN_M`
- `MOTION_QUEUE_MAX_SIZE`
- `BLOCKING_MOVE_TIMEOUT_S`
- `DEFAULT_VEL_PERCENT`
- `DEFAULT_ACC_PERCENT`
- `TRAJECTORY_OPTIMIZER`

## Operational Notes

- Safety walls and local workspace checks are separate layers.
- Queueing preserves mixed ordering between immediate point moves and path moves.
- Stopping motion can also clear queued tasks.
- Workobjects are applied before planning, so REST/user-frame targets are not always base-frame targets.

## Known Issue And Current Policy

### Issue found in single-target Cartesian planning

We reproduced a failure mode on short single-target linear moves where:
- the requested TCP line was geometrically valid
- the start state was collision-free
- the endpoint was reachable
- but `compute_cartesian_path` still returned a partial fraction for the move

The failing cases were traced to the structural pre-interpolation layer in `motion/planning/single_target.py`.

Before the Cartesian request was sent to MoveIt, the planner inserted exact intermediate poses on the requested line. Although those points were on the same geometric line, they were still treated by MoveIt as hard waypoint constraints.

That changed the planning problem from:
- one continuous `A -> B` Cartesian interpolation

into:
- a sequence of anchored subproblems such as `A -> mid -> B`

For short moves, that over-constrained the nonlinear IK continuation and could make a move fail even when the equivalent `A -> B` request succeeded.

### Current policy

Single-target planning currently uses:
- micro moves: Jacobian direct path
- normal single-target linear moves: start/end Cartesian poses only
- multi-waypoint paths: explicit path waypoints as requested

For normal single-target linear moves, MoveIt now performs the Cartesian interpolation internally from the start pose to the end pose without additional structural waypoint anchors from our side.

This is a deliberate temporary policy because it avoids the short-move failure mode above.

## Dedicated collision stop and recovery

Collision Stop uses the selected implementation under
`motion/execution/stop_strategies/`: `measured_ruckig` or `planned_path`.
`EXECUTOR_COLLISION_STOP_ENABLED: false` disables the dedicated brake trajectory
and leaves cancellation fallback; it does not select another brake strategy.
The named strategy and limits live under `runtime` in the active profile's
`sensorless_collision.yaml`. Regular operator/process Stop retains its own
Joint_6 hold behavior. Changing the collision strategy does not change that path.

Ordinary collision release retains a valid baseline when
`COLLISION_RESET_RECALIBRATE_ON_RELEASE` is false. It resets integration/filter
state and waits for drive stability, stationary settling and fresh matching
acknowledgement-generation readiness. An invalid baseline or explicit
recalibration still requires full warm-up. Recovery uses normal trip thresholds,
with no extra lower release threshold. Continuing above-threshold torque leaves
motion interlocked. Reset neither resumes the old trajectory nor learns away
contact on each release.

Read the active profile/effective API values for timing and stop limits; shared
values are inheritance defaults, not guaranteed live controller state. The
[sensorless runbook](../../zeroerr/collision_detection/docs/SENSORLESS_COLLISION_DETECTION.md)
documents the timeout, suppression/recovery-only gate, braking limits and fallback.
