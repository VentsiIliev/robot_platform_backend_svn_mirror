# Shared paint movement and recovery

`PaintMotionExecutor` submits individual moves and ordered chains through `IRobotService`. Tool and user providers are evaluated at execution time. It receives a `PaintMotionRecovery` collaborator; it does not receive the entire paint runtime or own vacuum control.

`PaintMotionRecovery` owns interruption state, protected-segment checks, the backend resume index, and geometric fallback when no usable index is available. The existing execution control still owns pause/stop requests. Protected contact segments defer robot stopping. Motion retries retain the existing ordered-command and fresh-pose semantics.

Pose comparison, sampling, and path geometry remain shared utilities in this package. Vacuum commands belong to the robot-system hardware package.

[Module reference](MODULES.md).

`waypoint.py` defines a validated six-axis position with its complete motion profile. Planning and execution share this data contract.
