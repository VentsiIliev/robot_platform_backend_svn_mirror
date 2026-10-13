# Module reference: `src/robot_systems/paint/diagnostics`

[Package guide](README.md). Generated from source ASTs; no runtime imports.

## `__init__.py`

[Source](../../../../src/robot_systems/paint/diagnostics/__init__.py).


## `artifacts.py`

[Source](../../../../src/robot_systems/paint/diagnostics/artifacts.py).

- `RobotMotionTrace`: Background sampler for actual robot poses during blocking trajectory execution.
- `start_robot_motion_trace`: See source for contract.
- `_path_length_mm`: See source for contract.
- `_axis_label_from_index`: See source for contract.
- `_unwrap_degrees`: See source for contract.
- `_angle_delta_deg`: See source for contract.
- `_motion_trace_comparison`: See source for contract.
- `write_execution_motion_trace`: Write commanded-vs-actual robot motion samples for execution diagnostics.
- `build_executed_snapshot_series`: Rebase projected physical contour snapshots onto the final robot command poses.
- `write_pivot_debug_dump`: Write source and robot command paths to disk for offline trajectory inspection.
- `write_pivot_debug_plot`: Write a compact visual debug plot for the source and robot command trajectories.

## `contour_interpolation.py`

[Source](../../../../src/robot_systems/paint/diagnostics/contour_interpolation.py).

- `save_paint_contour_interpolation_debug_plot`: Save a compact before/after plot for the experimental interpolation.
- `show_paint_contour_interpolation_debug_plot`: Show a compact before/after plot for the experimental interpolation.
- `_build_debug_figure`: See source for contract.
- `_plot_min_rect`: See source for contract.
- `_plot_xy`: See source for contract.

## `trajectory.py`

[Source](../../../../src/robot_systems/paint/diagnostics/trajectory.py).

- `elapsed_s`: See source for contract.
- `path_length_mm`: See source for contract.
- `_completed_export`: See source for contract.
- `_export_failure`: See source for contract.
- `write_platform_command_path_csv`: Queue optional diagnostics; the future reports completion without blocking motion.
- `_write_platform_command_path_artifacts`: See source for contract.
- `_write_contour_pipeline_csv`: See source for contract.
- `_write_contour_pipeline_plot`: See source for contract.
- `_write_contour_before_after_plot`: See source for contract.
- `_path_turn_angles_degrees`: See source for contract.
- `_write_platform_pose_plot`: See source for contract.
- `_set_equal_3d_axes`: Give X/Y/Z the same physical scale without collapsing flat paths.
- `_log_cartesian_command_path_diagnostics`: See source for contract.
- `_run_cartesian_command_path_diagnostics`: See source for contract.
- `_log_cartesian_command_path_diagnostics_sync`: Log final Cartesian command-path geometry without modifying the path.
- `diagnostics_with_command_rotation`: Attach final robot-command rotation values to projection diagnostics.
- `write_path_shape_comparison_debug`: See source for contract.
- `execute_paint_trajectory_with_optional_trace`: Execute a paint trajectory and optionally write commanded-vs-actual samples.
- `write_pivot_job_debug_artifacts`: See source for contract.

## `trajectory_export_result.py`

[Source](../../../../src/robot_systems/paint/diagnostics/trajectory_export_result.py).

- `ExportFailureCode`: See source for contract.
- `ExportWritten`: See source for contract.
- `ExportSkipped`: See source for contract.
- `ExportFailed`: See source for contract.
