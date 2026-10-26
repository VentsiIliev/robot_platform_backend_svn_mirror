# Paint start-position recovery

Production attempts entering `STARTING` check the current robot position before cycle-start
J6 unwind or magazine navigation. This includes Start after a process failure,
not just the first Start after launching the platform. The manual/calibration
entry path performs the same check before its preliminary calibration move.
Pause/resume retains the existing interrupted-phase behavior.

`processes/paint/start_recovery/` owns the policy:

- `IStartRecoveryStrategy`: match a position and build a required motion route.
- `TrayReturnRecoveryStrategy`: return from the tray through its configured exit
  gate and every enabled next-cycle waypoint to the production start target.
- `ContinueStartStrategy`: no extra movement outside the tray; other regions are
  deliberately not implemented yet.
- `StartRecoveryService`: select one strategy, build the entire route before
  submitting it, and reject the attempt if reading, planning, or execution fails.
  There is no direct-motion fallback after a failed tray return.

The production service supplies fresh pose reads, the current destination, and
ordered motion execution. Strategies perform no hardware calls, release actions,
vacuum changes, reservations, or tray clearing. Normal dropoff and start recovery
share the pure return-segment builder in `tray_dry/return_route.py`.

## Tray boundary and route

The initial region is the convex XY polygon of `dropoff.plate_corners`, including
its edges, at any height. It is not an axis-aligned bounding rectangle. The taught
tool/user metadata must match the configured motion tool/user. Invalid geometry,
missing pose feedback, or a frame mismatch rejects the attempt rather than
assuming that the robot is outside the tray. Systems without tray configuration
retain their existing behavior.

From inside the polygon, recovery:

1. Raises vertically, retaining orientation, if below the configured tray approach
   clearance. A pose below the taught surface is rejected for manual positioning.
2. Joins the tray center at that clearance or the current height, whichever is
   higher. Recovery uses the center even when normal dropoff can omit it, because
   there is no active placement reservation defining the starting position.
3. Visits `plate_exit_gate_pose`, all `plate_next_cycle_waypoints` in order, and
   the current production start target. Enabled, nonempty return waypoints are
   mandatory for this recovery. The final target is an exact stop.

When `plate_distribute_unwind` is enabled, recovery distributes the change from
fresh TCP RZ to the taught production-start RZ over the entire center/gate/return
route, proportional to XYZ travel distance. Normal dropoff and recovery share
this interpolation helper. An initial vertical clearance move keeps its starting
orientation. When disabled, recovery retains the equivalent-angle continuity
behavior.

Recovery does not infer completed paint turns or J6 winding from TCP RZ; fresh
Start may follow a platform restart or an interrupted cycle without trustworthy
paint-turn history. The existing cycle-start J6 unwind remains after successful
recovery at the production-start position. No stationary unwind is added before
the tray return. Distributed waypoint rotation remains subject to backend
planning and orientation limits; it does not guarantee that every initial joint
configuration has a valid route. Fixed-magazine targets and single-cycle runs
use the same destination resolution as normal next-cycle prepositioning. Manual
cycles target calibration instead of magazine.

## Scope and verification

This is route selection using the existing configured motion profiles. It does
not add a geometric tool-changer exclusion volume to the planner, validate all
possible arm configurations, or recover from every possible failure position.
The taught footprint may be smaller than the surrounding tray work area. A pose
outside that footprint, including a partial return stopped outside it, follows
existing startup behavior. Extending the region or adding other recovery
strategies is a separate configuration/design change.

Before running on hardware, validate the clearance join and the configured return
segments with the actual arm, tool, fixtures, and any held workpiece. PTP segments
and blending retain their existing backend semantics; visiting configured
waypoints alone is not proof that the swept arm avoids the tool-changer area.

Unit tests cover polygon boundaries, rotated regions, fresh reads on restart,
route ordering, frame/geometry failures, disabled/missing return paths,
cancellation, no fallback, execution before unwind, manual-entry guarding, and
unchanged pause/resume. No hardware motion is performed by these tests.

## Typed outcomes and failures

`StartRecoveryResult` distinguishes `NOT_REQUIRED`, `RECOVERED`, `CANCELLED`, and
`FAILED`. Cancellation is not a motion failure. Failed results carry a
`StartRecoveryFailure`, which extends the existing paint failure contract with a
stable `recovery_code`. The workflow and manual-cycle boundary retain this object
when converting to `PaintOperationResult`, so diagnostic serialization preserves
the specific reason instead of flattening it into a message.

Each expected case has a dedicated `StartRecoveryError` subclass: invalid tray
geometry, frame mismatch, unavailable fresh pose, no matching strategy,
unavailable target, invalid exit gate, missing return waypoints, invalid waypoint,
invalid motion profile, invalid clearance, below-surface position, and motion
failure. Unexpected exceptions become `RecoveryInternalError`. Human-readable
messages provide detail; branching and tests use the enum codes.

The shared return builder also raises specific configuration exceptions for
missing waypoints, invalid waypoints, and invalid motion profiles. Only the
existing legacy dropoff adapter converts these back to its existing tuple API.

## Package reference

See [module reference](MODULES.md) for source links and public contracts.
The production service composes `StartRecoveryService` with fresh-pose and ordered
execution callbacks. `prepare_start_recovery()` temporarily binds the execution
control and restores it in `finally`. The `STARTING` handler checks the typed
result before invoking cycle-start J6 unwind. Manual calibration entry points
check recovery before their preliminary navigation.

A resume with a saved phase bypasses start recovery. Prepared-workpiece editor
execution beginning at `PICKUP` and unmatched-workpiece recapture beginning at
`CAPTURE_WORKPIECE` also bypass `STARTING`; this module is not a global interceptor
for every robot command.

## Extending regional recovery

Implement `IStartRecoveryStrategy.matches(request)` and `build_route(request)`.
Keep matching and route construction free of hardware side effects. Register the
strategy in the ordered strategy sequence before `ContinueStartStrategy`, which
always matches. Explicitly decide precedence for overlapping regions. The first
matching strategy owns the attempt; a construction or motion failure never falls
through to a later strategy.

The current request contains taught tray corners, not a generic region registry.
Adding paint-area recovery therefore also requires defining and supplying that
region's geometry and route configuration. Add typed failure codes/exceptions
for new failure cases and tests for overlap, cancellation, and failed-route
blocking. Do not infer joint winding from Cartesian orientation.

## Related documentation

- [Paint production](../README.md)
- [Tray lifecycle and fault handling](../../../../paint_tray_dry/RECOVERY.md)
- [Regression tests](../../../../../../tests/robot_systems/paint/test_start_recovery.py)
