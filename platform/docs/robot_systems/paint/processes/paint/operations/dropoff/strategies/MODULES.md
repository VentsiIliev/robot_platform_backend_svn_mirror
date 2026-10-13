# Module reference: `src/robot_systems/paint/processes/paint/operations/dropoff/strategies`

[Package guide](README.md). Generated from source ASTs; no runtime imports.

## `__init__.py`

[Source](../../../../../../../../src/robot_systems/paint/processes/paint/operations/dropoff/strategies/__init__.py).


## `configured.py`

[Source](../../../../../../../../src/robot_systems/paint/processes/paint/operations/dropoff/strategies/configured.py).

- `ConfiguredDropoffStrategy`: Select a built-in strategy from the runtime's cycle configuration.

## `movement_group.py`

[Source](../../../../../../../../src/robot_systems/paint/processes/paint/operations/dropoff/strategies/movement_group.py).

- `MovementGroupDropoff`: Prepare the configured movement-group destination and verify release.
- `DropoffReleaseWaypoint`: One release-strategy move or release action.
- `DropoffReleasePlan`: Resolved release sequence for the currently held painted workpiece.
- `execute_dropoff_preparation_for_executor`: Build and execute paint-to-dropoff safe travel, align, and Joint 6 unwind.
- `execute_dropoff_release_for_executor`: Build and execute the configured dropoff release strategy.
- `_execute_movement_group_ordered_exit`: Blend a sub-zero corridor retract into the next-cycle start move.
- `_move_to_next_cycle_start`: See source for contract.
- `_next_cycle_start_pose_reached`: See source for contract.
- `_wait_for_next_cycle_start_pose`: Wait through ordered-chain response/telemetry skew for stable arrival.
- `_build_dropoff_release_plan`: See source for contract.
- `MovementGroupDropoffPlanner`: Release the held workpiece at the configured dropoff movement group.
- `_on_workpiece_release_verified`: Notify the composed system after release verification succeeds.

## `plate_layout.py`

[Source](../../../../../../../../src/robot_systems/paint/processes/paint/operations/dropoff/strategies/plate_layout.py).

- `PlateLayoutDropoff`: Prepare plate travel and release into the active layout reservation.
- `_completed_rotation_turns`: Count only fully executed 360-degree turns, preserving direction.
- `_PlateMotionProfile`: See source for contract.
- `_PlateNextWaypoint`: See source for contract.
- `_plate_motion_profile`: See source for contract.
- `_plate_ordered_segment`: See source for contract.
- `_wait_for_motion_slot_idle`: Wait through the controller-success/backend-slot release handoff.
- `_plate_route_poses_with_distributed_unwind`: See source for contract.
- `build_plate_entry_segments_for_paint_chain`: Build plate entry through release for the combined paint chain.
- `_interpolate_route_rotations`: Interpolate one rotation axis at a constant rate over route distance.
- `_plate_route_uses_center`: Select the safer center route for placements near the bottom-left corner.
- `_execute_plate_layout_ordered_release`: See source for contract.
- `_execute_plate_layout_preparation`: Unwind at the paint-detach pose before the plate entry chain.
- `_reserve_plate_dropoff`: See source for contract.
- `_workpiece_footprint_mm`: Return canonical min-rectangle sides as long-side width and short-side height.
- `_paint_pass_metadata`: Capture the configured paint controls used by each production pass.
- `_workpiece_layout_geometry`: Return footprint and execution paths projected into its local rectangle.
- `_plate_entry_detach_pose`: See source for contract.
- `_on_workpiece_release_verified`: Commit plate occupancy only after successful release.
