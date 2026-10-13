# Module reference: `src/robot_systems/paint/processes/paint/operations/dropoff`

[Package guide](README.md). Generated from source ASTs; no runtime imports.

## `__init__.py`

[Source](../../../../../../../src/robot_systems/paint/processes/paint/operations/dropoff/__init__.py).


## `executor.py`

[Source](../../../../../../../src/robot_systems/paint/processes/paint/operations/dropoff/executor.py).

- `DropoffWaypointExecutor`: Execute a waypoint plan; lifecycle strategies own preparation and release.

## `motion.py`

[Source](../../../../../../../src/robot_systems/paint/processes/paint/operations/dropoff/motion.py).

- `_ordered_position_command`: See source for contract.
- `_parse_motion_type`: Validate an external/configured motion type at its input boundary.
- `_DropoffRouteItem`: See source for contract.
- `open_dropoff_passage_for_preparation`: Open the configured passage before planning any route that crosses its lid.
- `_on_workpiece_release_verified`: Dispatch older release callers to the strategy's destination bookkeeping.
- `_verify_workpiece_released`: Verify that vacuum cleared after pump-off at the dropoff waypoint.
- `build_ordered_dropoff_preparation_segments`: Build the post-paint ordered dropoff preparation chain.
- `_resolve_dropoff_safe_travel_waypoints`: See source for contract.
- `_apply_distributed_dropoff_unwind`: Progressively shift the active rotation component by whole-turn equivalents
- `_should_prepare_dropoff_align_before_unwind`: See source for contract.
- `_dropoff_strategy_name`: See source for contract.
- `_resolve_dropoff_release_pose`: See source for contract.
- `_resolve_dropoff_align_pose`: See source for contract.
- `_resolve_dropoff_preparation_pose`: Resolve the safe above-floor endpoint used before a corridor dropoff.
- `_dropoff_align_pose_near_reference`: See source for contract.
- `execute_dropoff_preparation_for_executor`: Dispatch existing callers to strategy-owned preparation code.
- `execute_dropoff_release_for_executor`: Dispatch existing callers to strategy-owned verified release code.
- `_cleanup_position_command`: Build one strictly typed cleanup/drop-off position command.
- `build_cleanup_dropoff_approach`: Preserve the shared cleanup-to-destination safe-travel/unwind sequence.

## `plan.py`

[Source](../../../../../../../src/robot_systems/paint/processes/paint/operations/dropoff/plan.py).

- `DropoffWaypoint`: One dropoff move or release action.
- `DropoffPlan`: Resolved dropoff sequence for the current held workpiece.
- `IDropoffWaypointPlanner`: Build a waypoint plan consumed by the low-level dropoff executor.
