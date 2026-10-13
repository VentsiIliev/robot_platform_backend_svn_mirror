# Module reference: `src/robot_systems/paint/processes/paint/motion`

[Package guide](README.md). Generated from source ASTs; no runtime imports.

## `__init__.py`

[Source](../../../../../../src/robot_systems/paint/processes/paint/motion/__init__.py).


## `executor.py`

[Source](../../../../../../src/robot_systems/paint/processes/paint/motion/executor.py).

- `PaintMotionExecutor`: Submit individual robot moves and ordered sequences.

## `failure.py`

[Source](../../../../../../src/robot_systems/paint/processes/paint/motion/failure.py).

- `motion_failure_message`: Return the latest backend command error without hiding it behind a result code.

## `path_geometry.py`

[Source](../../../../../../src/robot_systems/paint/processes/paint/motion/path_geometry.py).

- `shift_path_rotation`: Return a copied path with a constant shift applied to one rotation component.

## `pose_comparison.py`

[Source](../../../../../../src/robot_systems/paint/processes/paint/motion/pose_comparison.py).

- `poses_close`: Return whether two six-axis poses match, accounting for wrapped RZ angles.

## `pose_sampling.py`

[Source](../../../../../../src/robot_systems/paint/processes/paint/motion/pose_sampling.py).

- `FreshPoseReadError`: Raised when a required fresh six-axis robot pose cannot be acquired.
- `read_fresh_pose`: Read one valid six-axis pose through the required fresh-read API.
- `wait_for_stable_pose`: Return a pose after consecutive samples show that robot motion has settled.

## `recovery.py`

[Source](../../../../../../src/robot_systems/paint/processes/paint/motion/recovery.py).

- `PaintMotionRecovery`: Track and resume interrupted non-contact robot movements.

## `waypoint.py`

[Source](../../../../../../src/robot_systems/paint/processes/paint/motion/waypoint.py).

- `ConfiguredMotionWaypoint`: Validated six-axis waypoint and its complete motion profile.
