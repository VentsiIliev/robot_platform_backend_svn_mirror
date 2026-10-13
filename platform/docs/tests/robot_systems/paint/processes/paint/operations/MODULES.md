# Module reference: `tests/robot_systems/paint/processes/paint/operations`

[Package guide](README.md) · [Complete source index](../../../../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [test_servo_contact_pickup_executor.py](#test_servo_contact_pickup_executorpy)

## `test_servo_contact_pickup_executor.py`

Source: [tests/robot_systems/paint/processes/paint/operations/test_servo_contact_pickup_executor.py](../../../../../../../tests/robot_systems/paint/processes/paint/operations/test_servo_contact_pickup_executor.py).

Imports (including optional/function-local imports; not a startup dependency list): `src.engine.robot.enums.axis`, `src.engine.robot.motion_sequence`, `src.robot_systems.paint.processes.paint.configuration.models`, `src.robot_systems.paint.processes.paint.operations.pickup.executor`, `src.robot_systems.paint.processes.paint.workflow.handlers.magazine_load.magazine_execute_pickup_release_handler`, `src.robot_systems.paint.processes.paint.production.magazine.outcomes`, `sys`, `types`, `unittest`, `unittest.mock`.

Module declarations (expressions are shown without evaluating them):

```python
paint_package = types.ModuleType('src.robot_systems.paint')
execute_package = types.ModuleType('src.robot_systems.paint.processes.paint.operations')
```

### `_FakeRobot`

```python
class _FakeRobot:
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self)
```

```python
def start_servo_jog(self, *args, **kwargs)
```

```python
def stop_servo_jog(self, *, restore_collision_checking=True)
```

```python
def servo_jog_to_z(self, **kwargs)
```

```python
def move_fast_linear(self, **kwargs)
```

```python
def controlled_stop(self, expected_task_id)
```

```python
def stop_motion(self)
```

```python
def get_current_position(self)
```

```python
def get_current_position_fresh(self)
```

```python
def get_execution_status(self)
```

```python
def move_ptp(self, position, *args, **kwargs)
```

```python
def prepare_ordered_motion_chain(self, segments, start_position, tool, user, **kwargs)
```

```python
def execute_prepared_ordered_motion_chain(self, plan_id)
```

```python
def discard_prepared_ordered_motion_chain(self, _plan_id)
```

### `_FakeMotion`

```python
class _FakeMotion:
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self)
```

```python
def turn_vacuum_on(self, *, required=False)
```

```python
def turn_vacuum_off(self)
```

```python
def move_ordered_pickup_sequence(self, label, segments)
```

### `_magazine_waypoints`

```python
def _magazine_waypoints(*items)
```

### `_ConditionAfterStart`

```python
class _ConditionAfterStart:
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self)
```

### `_ConditionLostAfterDetection`

```python
class _ConditionLostAfterDetection:
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self)
```

### `ServoContactPickupExecutorTest`

```python
class ServoContactPickupExecutorTest(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_magazine_approach_waits_for_two_inactive_status_samples(self)
```

```python
def test_magazine_approach_inactive_wait_times_out_while_still_executing(self)
```

```python
def test_magazine_approach_rejects_missing_execution_status_api(self)
```

```python
def test_magazine_approach_rejects_malformed_execution_status(self)
```

```python
def test_calibration_contact_timeout_turns_vacuum_off(self)
```

```python
def test_magazine_contact_timeout_turns_vacuum_off(self)
```

```python
def test_magazine_minimum_z_without_vacuum_advances_as_no_workpiece(self)
```

```python
def test_magazine_contact_timeout_returns_to_fixed_magazine_pose(self)
```

```python
def test_magazine_servo_handoff_executes_clearance_and_release_as_one_chain(self)
```

```python
def test_magazine_short_retract_plans_release_after_live_retract(self)
```

```python
def test_magazine_prepared_start_mismatch_replans_release_from_live_pose(self)
```

```python
def test_magazine_lost_after_retract_turns_vacuum_off(self)
```

```python
def test_planned_pickup_keeps_full_existing_waypoint_sequence(self)
```

```python
def test_planned_pickup_test_mode_stops_after_lift(self)
```

```python
def test_servo_contact_pickup_splits_approach_and_remaining_segments(self)
```

```python
def test_servo_contact_pickup_stops_when_workpiece_is_lost_after_retract(self)
```

```python
def test_xy_rz_servo_pickup_combines_post_retract_lift_with_alignment(self)
```

```python
def test_xy_rz_servo_pickup_combines_alignment_with_first_safe_waypoint(self)
```

```python
def test_xy_rz_servo_pickup_combines_alignment_with_paint_staging(self)
```

```python
def test_servo_pickup_with_safe_travel_never_revisits_calibration_xy(self)
```

```python
def test_servo_contact_prepared_chain_replaces_separate_ptp_retract(self)
```

```python
def test_servo_contact_discards_rejected_prepared_chain_and_replans_from_live_pose(self)
```

```python
def test_servo_contact_does_not_move_when_vacuum_on_fails(self)
```

```python
def test_single_segment_pickup_chain_forces_terminal_blend_zero(self)
```

```python
def test_pickup_chain_removes_redundant_alignment_pose(self)
```

```python
def test_height_measure_pickup_mode_fails_fast_until_wired(self)
```

```python
def test_single_segment_magazine_chain_forces_terminal_blend_zero(self)
```
