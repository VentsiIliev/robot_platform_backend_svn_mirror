# Module reference: `src/robot_systems/paint/processes/paint/operations/painting`

[Package guide](README.md). Generated from source ASTs; no runtime imports.

## `__init__.py`

[Source](../../../../../../../src/robot_systems/paint/processes/paint/operations/painting/__init__.py).


## `executor.py`

[Source](../../../../../../../src/robot_systems/paint/processes/paint/operations/painting/executor.py).

- `_apply_non_paint_clearance`: Retract projected poses from the pivot according to the source profile.
- `_remove_projected_local_reversals`: Remove short folds introduced when tangent rotation is projected about a pivot.
- `_workpiece_min_rect_size_mm`: Return the prepared geometry's minimum-area-rectangle sides in millimetres.
- `_workpiece_largest_side_mm`: Return the long side of the prepared geometry's minimum-area rectangle.
- `_tcp_to_tool_local_xy`: Return the local vector from configured robot TCP to selected tool point.
- `PaintingExecutor`: Execute prepared paint-contact paths against the fixed paint shaft.
