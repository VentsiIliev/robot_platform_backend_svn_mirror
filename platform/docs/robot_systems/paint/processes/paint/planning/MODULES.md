# Module reference: `src/robot_systems/paint/processes/paint/planning`

[Package guide](README.md). Generated from source ASTs; no runtime imports.

## `__init__.py`

[Source](../../../../../../src/robot_systems/paint/processes/paint/planning/__init__.py).


## `pose_helpers.py`

[Source](../../../../../../src/robot_systems/paint/processes/paint/planning/pose_helpers.py).

- `_camera_to_tcp_delta`: Return the tool-frame TCP sweep delta between the reference and current pickup angles.
- `_paint_axis_staging_offset_pose`: Return the pre-paint staging pose below and behind the first pivot contact.
- `_finite_pose`: See source for contract.
- `calculate_workpiece_dropoff_pose`: Return a plate pose preserving workpiece orientation across plane rotation.

## `workpiece_preparation_service.py`

[Source](../../../../../../src/robot_systems/paint/processes/paint/planning/workpiece_preparation_service.py).

- `PaintWorkpiecePreparationService`: Prepare the raw workpiece payload that paint production should execute.
