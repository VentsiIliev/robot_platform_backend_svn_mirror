# Module reference: `tests/engine/robot/procedures`

[Package guide](README.md) · [Complete source index](../../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [test_servo_until_condition.py](#test_servo_until_conditionpy)

## `test_servo_until_condition.py`

Source: [tests/engine/robot/procedures/test_servo_until_condition.py](../../../../../tests/engine/robot/procedures/test_servo_until_condition.py).

Imports (including optional/function-local imports; not a startup dependency list): `src.engine.robot.enums.axis`, `src.engine.robot.procedures`, `threading`, `time`, `unittest`.

### `FakeRobot`

```python
class FakeRobot:
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self)
```

```python
def start_servo_jog(self, axis, direction, linear_mm_s=None, angular_deg_s=None, *, frame='user', tool=0, user=0, allow_subzero_descent=False, allow_subzero_retract_settle=False, disable_collision_checking=False)
```

```python
def stop_servo_jog(self, *, restore_collision_checking=True)
```

```python
def controlled_stop(self, expected_task_id)
```

### `ManualCondition`

```python
class ManualCondition:
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self)
```

```python
def is_active(self)
```

### `_ConditionSequence`

```python
class _ConditionSequence:
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, *values)
```

### `FailingCondition`

```python
class FailingCondition:
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def is_active(self)
```

### `FailsAfterStartCondition`

```python
class FailsAfterStartCondition:
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self)
```

```python
def is_active(self)
```

### `UnhealthyVacuumSensor`

```python
class UnhealthyVacuumSensor:
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def is_vacuum_detected(self)
```

```python
def is_healthy(self)
```

### `TestServoUntilConditionProcedure`

```python
class TestServoUntilConditionProcedure(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_descending_servo_switches_from_fast_to_contact_speed_and_captures_pose(self)
```

```python
def test_successful_detection_retracts_up_to_reference_z(self)
```

```python
def test_scoped_collision_override_applies_to_descent_and_retract(self)
```

```python
def test_distance_retract_accepts_overshoot_within_clearance_window(self)
```

```python
def test_target_pose_retract_computes_limit_from_required_distance_and_margin(self)
```

```python
def test_target_pose_retract_delegates_hard_bound_to_robot_runtime(self)
```

```python
def test_fast_lin_retract_requires_final_success_and_verifies_target_z(self)
```

```python
def test_fast_lin_retract_waits_for_delayed_final_pose_feedback(self)
```

```python
def test_fast_lin_retract_accepts_non_final_response_and_waits_for_pose(self)
```

```python
def test_distance_retract_delegates_computed_target_and_notifies_planning_hook(self)
```

```python
def test_stops_servo_when_condition_becomes_active(self)
```

```python
def test_bounded_contact_search_can_authorize_subzero_descent(self)
```

```python
def test_stops_servo_on_timeout(self)
```

```python
def test_stops_servo_when_stop_guard_triggers(self)
```

```python
def test_stops_servo_at_maximum_travel(self)
```

```python
def test_stops_servo_at_configured_minimum_z(self)
```

```python
def test_stops_servo_when_stop_guard_cannot_be_read(self)
```

```python
def test_does_not_start_servo_when_condition_already_active(self)
```

```python
def test_does_not_start_servo_when_condition_unreadable_in_preflight(self)
```

```python
def test_unhealthy_vacuum_sensor_blocks_servo_start(self)
```

```python
def test_stops_servo_when_condition_becomes_unreadable_during_motion(self)
```

```python
def test_invalid_linear_speed_blocks_servo_start(self)
```

```python
def test_invalid_maximum_travel_blocks_servo_start(self)
```

```python
def test_timed_dummy_condition_arms_only_after_servo_start(self)
```

```python
def test_ros_managed_mode_waits_for_terminal_stationary_state(self)
```

```python
def test_ros_managed_mode_ignores_idle_status_without_operation_id(self)
```

```python
def test_ros_managed_mode_fails_without_capabilities_and_never_starts_legacy_servo(self)
```

```python
def test_sensor_controlled_fast_lin_moves_to_minimum_z_without_starting_servo(self)
```

```python
def test_sensor_controlled_fast_lin_waits_for_stopped_task_to_become_inactive(self)
```

```python
def test_sensor_controlled_fast_lin_accepts_stop_race_after_task_completed(self)
```

```python
def test_fast_lin_retract_verification_isolated_from_driver_pose_mutation(self)
```

```python
def test_fast_lin_retract_verifies_motion_service_effective_target(self)
```
