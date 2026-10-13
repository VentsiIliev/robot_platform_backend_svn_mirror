# Module reference: `src/robot_systems/paint/processes/paint/operations/pickup`

[Package guide](README.md). Generated from source ASTs; no runtime imports.

## `__init__.py`

[Source](../../../../../../../src/robot_systems/paint/processes/paint/operations/pickup/__init__.py).

Workpiece pickup operations.


## `executor.py`

[Source](../../../../../../../src/robot_systems/paint/processes/paint/operations/pickup/executor.py).

- `pickup_pose_is_close`: Return True when a recovery move would be an effective no-op.
- `pickup_condition_is_active_after_retract`: Require the carried-workpiece signal to remain active after retract.
- `PickupWaypoint`: One carried-part pickup or staging move.
- `MagazineTransferWaypoint`: One fully typed move in a magazine pickup-to-release chain.
- `PickupPlan`: Resolved pickup sequence for moving the workpiece to the paint start.
- `normalize_pickup_contact_mode`: See source for contract.
- `PaintPickupStrategy`: Build paint pickup/staging plans without exposing strategy details to the main executor.
- `DefaultPickupStrategy`: Default strategy for calibration-table pickup, align, and pivot staging.
- `PaintPickupExecutor`: Execute the configured pickup strategy.
- `build_ordered_pickup_segments`: Build ordered paint pickup/staging motion segments from a pickup plan.
- `build_paint_pickup_segments`: Build paint pickup/staging motion segments.
- `_equivalent_pickup_poses`: See source for contract.
- `build_ordered_paint_contact_segments`: Build ordered paint-contact path segments.
- `build_magazine_pickup_release_segments`: Build ordered magazine pickup-to-release segments.
