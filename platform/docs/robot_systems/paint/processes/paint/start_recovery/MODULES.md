# Start recovery module reference

[Package guide](README.md). Source package: `src/robot_systems/paint/processes/paint/start_recovery/`.

## `__init__.py`

[Source](../../../../../../src/robot_systems/paint/processes/paint/start_recovery/__init__.py).

Paint-specific start recovery motion routing.


## `contracts.py`

[Source](../../../../../../src/robot_systems/paint/processes/paint/start_recovery/contracts.py).

Contracts for paint-specific routing before production navigation.

- `StartRecoveryRequest`: Typed failure case; see the failure mapping below.
- `IStartRecoveryStrategy`: Select and build motion only; never release a workpiece or change tray state.

## `errors.py`

[Source](../../../../../../src/robot_systems/paint/processes/paint/start_recovery/errors.py).

Stable recovery failures and the exceptions raised by their producers.

- `StartRecoveryFailureCode`: Typed failure case; see the failure mapping below.
- `StartRecoveryFailure`: Paint-compatible failure retaining the specific recovery reason in diagnostics.
- `StartRecoveryError`: Base for expected recovery failures; consumers inspect failure codes.
- `InvalidTrayGeometryError`: Typed failure case; see the failure mapping below.
- `TrayFrameMismatchError`: Typed failure case; see the failure mapping below.
- `RecoveryPoseUnavailableError`: Typed failure case; see the failure mapping below.
- `NoRecoveryStrategyError`: Typed failure case; see the failure mapping below.
- `RecoveryTargetUnavailableError`: Typed failure case; see the failure mapping below.
- `InvalidRecoveryExitGateError`: Typed failure case; see the failure mapping below.
- `MissingRecoveryWaypointsError`: Typed failure case; see the failure mapping below.
- `InvalidRecoveryWaypointError`: Typed failure case; see the failure mapping below.
- `InvalidRecoveryMotionProfileError`: Typed failure case; see the failure mapping below.
- `InvalidRecoveryClearanceError`: Typed failure case; see the failure mapping below.
- `BelowTraySurfaceError`: Typed failure case; see the failure mapping below.
- `RecoveryMotionFailedError`: Typed failure case; see the failure mapping below.
- `RecoveryInternalError`: Unexpected implementation/runtime error; also blocks production.

## `results.py`

[Source](../../../../../../src/robot_systems/paint/processes/paint/start_recovery/results.py).

Typed outcomes for start/restart recovery.

- `StartRecoveryOutcome`: Typed failure case; see the failure mapping below.
- `StartRecoveryResult`: Typed failure case; see the failure mapping below.

## `service.py`

[Source](../../../../../../src/robot_systems/paint/processes/paint/start_recovery/service.py).

Select one recovery strategy and execute it without direct-motion fallback.

- `StartRecoveryService`: Run a required regional return before allowing production to start.

## `strategies.py`

[Source](../../../../../../src/robot_systems/paint/processes/paint/start_recovery/strategies.py).

Tray return and unchanged startup outside the tray footprint.

- `TrayReturnRecoveryStrategy`: Route every TCP inside the taught XY polygon through the tray return path.

Height does not exclude a pose from detection. Initial vertical clearance
preserves orientation; configured gate/return poses then define the route.
- `ContinueStartStrategy`: Preserve normal startup when no preceding regional strategy matches.

## Failure mapping

| Exception | Recovery code | Paint category |
|---|---|---|
| `InvalidTrayGeometryError` | `INVALID_TRAY_GEOMETRY` | `INVALID_CONFIGURATION` |
| `TrayFrameMismatchError` | `FRAME_MISMATCH` | `INVALID_CONFIGURATION` |
| `RecoveryPoseUnavailableError` | `POSE_UNAVAILABLE` | `UNAVAILABLE` |
| `NoRecoveryStrategyError` | `NO_STRATEGY` | `PLANNING` |
| `RecoveryTargetUnavailableError` | `TARGET_UNAVAILABLE` | `UNAVAILABLE` |
| `InvalidRecoveryExitGateError` | `INVALID_EXIT_GATE` | `INVALID_CONFIGURATION` |
| `MissingRecoveryWaypointsError` | `MISSING_RETURN_WAYPOINTS` | `INVALID_CONFIGURATION` |
| `InvalidRecoveryWaypointError` | `INVALID_RETURN_WAYPOINT` | `INVALID_CONFIGURATION` |
| `InvalidRecoveryMotionProfileError` | `INVALID_MOTION_PROFILE` | `INVALID_CONFIGURATION` |
| `InvalidRecoveryClearanceError` | `INVALID_CLEARANCE` | `INVALID_CONFIGURATION` |
| `BelowTraySurfaceError` | `BELOW_TRAY_SURFACE` | `PLANNING` |
| `RecoveryMotionFailedError` | `MOTION_FAILED` | `MOTION` |
| `RecoveryInternalError` | `INTERNAL` | `INTERNAL` |
