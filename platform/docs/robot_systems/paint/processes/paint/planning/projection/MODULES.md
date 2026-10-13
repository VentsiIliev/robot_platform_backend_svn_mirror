# Module reference: `src/robot_systems/paint/processes/paint/planning/projection`

[Package guide](README.md). Generated from source ASTs; no runtime imports.

## `__init__.py`

[Source](../../../../../../../src/robot_systems/paint/processes/paint/planning/projection/__init__.py).


## `command_job.py`

[Source](../../../../../../../src/robot_systems/paint/processes/paint/planning/projection/command_job.py).

- `PaintContactCommandJob`: Motion settings for one generated paint-contact path.

## `config.py`

[Source](../../../../../../../src/robot_systems/paint/processes/paint/planning/projection/config.py).

- `_normalize_contact_motion_config`: Normalize user-facing pivot settings into a validated simulation config.
- `_xz_ry_projection_rotation_sign`: Return the planar rotation sign used during projection, before command generation.

## `core.py`

[Source](../../../../../../../src/robot_systems/paint/processes/paint/planning/projection/core.py).

- `rebase_contact_motion_path_to_zero_start_rotation`: Shift a paint contact-motion path so its active rotation starts at zero.
- `_rotate_points_about`: Vectorized 2D rotation around ``pivot``.
- `_save_projection_snapshots`: Return whether expensive full-shape debug snapshots should be stored.
- `project_paint_contact_motion_continuous`: Project a dense contour into paint-axis contact motion.
- `_extend_closed_path_by_overlap`: Append an exact arc-length prefix after a closed contour's seam.
- `_compose_pose`: Build a full 6D pose from a projected 2D point and the active motion plane.
- `_segment_heading_deg`: Return the heading of the segment from ``point_a`` to ``point_b``.
- `_angle_error_deg`: Return the smallest angular error between two angles in degrees.
- `_canonicalize_closed_source_path`: Give closed contours a pivot-aware start point and traversal direction.
- `_orient_open_source_path_for_contact_side`: Choose the open-path direction that places the workpiece on the configured side.

## `inputs.py`

[Source](../../../../../../../src/robot_systems/paint/processes/paint/planning/projection/inputs.py).

- `pivot_source_path`: Return the path used as geometric source for pivot projection.
- `projection_tool_anchor_xy`: Return the selected tool/workpiece anchor used by pivot projection.
- `PaintProjectionContext`: Prepared projection inputs and shared command-space transformations.

## `planes.py`

[Source](../../../../../../../src/robot_systems/paint/processes/paint/planning/projection/planes.py).

- `ExecutionPlaneStrategy`: Behavioral strategy for one pivot execution plane.
- `XyZRzExecutionPlaneStrategy`: See source for contract.
- `XzYRyExecutionPlaneStrategy`: See source for contract.
- `get_execution_plane_strategy`: Return the strategy object for a configured execution plane.

## `source_plan.py`

[Source](../../../../../../../src/robot_systems/paint/processes/paint/planning/projection/source_plan.py).

- `build_paint_contact_source_plan`: Attach the final paint contact source contour to each execution job.
- `_planar_spacing_stats`: Return min/mean/max spacing in the active source plane.
- `_trim_and_profile_selected_interval`: Trim after the last selected span and add clearance through internal gaps.
- `_points_near_polyline`: See source for contract.
- `_cumulative_distances`: See source for contract.
