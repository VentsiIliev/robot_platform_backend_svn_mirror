# `src/engine/robot/procedures/` — Reusable Motion Primitives

Robot-system-agnostic motion procedures. Everything here works against a plain
`robot` object plus small duck-typed collaborators — no `IRobotService`, no
broker, no Qt.

---

## Files

| File | Contents |
|------|----------|
| `__init__.py` | Public surface (see below) |
| `servo_until_condition.py` | `ServoUntilConditionProcedure` + config/result types (2076 lines) |
| `vacuum_pickup_condition.py` | `VacuumPickupCondition` |
| `dummy_pickup_condition.py` | `TimedDummyPickupCondition` |

```python
__all__ = [
    "ServoUntilConditionConfig", "ServoUntilConditionResult",
    "ServoUntilConditionProcedure", "ServoRetractConfig",
    "ServoRetractMotionType",
    "TimedDummyPickupCondition", "VacuumPickupCondition",
]
```

---

## The condition protocol

```python
class PickupCondition(Protocol):
    def is_active(self) -> bool: ...
```

The procedure docstring states the intent:

> Generic servo-until-condition primitive. This is intentionally robot-system
> agnostic. The condition can be a vacuum sensor, force threshold, distance
> sensor, dummy test trigger, or any object exposing `is_active()`.

A bare `Callable[[], bool]` is accepted anywhere a `PickupCondition` is.

### Built-in conditions

| Class | Contract |
|-------|----------|
| `VacuumPickupCondition(vacuum_sensor: IVacuumSensorService)` | Adapter from `IVacuumSensorService`. Reads `is_vacuum_detected()`; **raises `RuntimeError("Vacuum sensor read failed")` when `is_healthy()` is `False`**. Also exposes `get_read_diagnostics()` via `getattr` fallback — returns `None` if the concrete sensor does not implement it |
| `TimedDummyPickupCondition(detect_after_s=1.0)` | **Test only.** `on_servo_start()` arms a `time.monotonic()` timestamp and logs a `WARNING` `[DUMMY_PICKUP_CONDITION] TEST ONLY …`; `is_active()` returns `False` until the delay elapses. Returns `False` before `on_servo_start()` |

`VacuumPickupCondition` and `TimedDummyPickupCondition` are wired from
`src/robot_systems/paint/paint_robot_system.py`.

---

## `ServoUntilConditionProcedure`

```python
procedure = ServoUntilConditionProcedure(robot, condition)
result = procedure.run(
    approach_pose=...,
    config=ServoUntilConditionConfig(...),
    retract=ServoRetractConfig(...),
    cancel_requested=...,
    stop_guard=...,
    on_retract_start=...,
)
```

### `run()` signature

| Parameter | Type | Role |
|-----------|------|------|
| `approach_pose` | `Sequence[float] \| None` | Optional pose moved to before the descent; failure → `approach_failed` |
| `config` | `ServoUntilConditionConfig \| None` | Descent behaviour (defaults when `None`) |
| `retract` | `ServoRetractConfig \| None` | Optional post-contact retract; `None` means stop at contact |
| `cancel_requested` | `Callable[[], bool] \| None` | Checked every poll → `cancelled` |
| `stop_guard` | `Callable[[], bool] \| None` | Emergency/stop input; unreadable → `stop_guard_unreadable`, active → `stop_guard_triggered` |
| `on_retract_start` | `Callable[[tuple, float], None] \| None` | Called with `(current_pose, target_z)`; an exception here fails the retract with `retract_start_callback_failed` |

Returns `ServoUntilConditionResult`.

### `ServoUntilConditionConfig` (frozen)

| Field | Default | Notes |
|-------|---------|-------|
| `execution_mode` | `"legacy"` | `"legacy"` \| `"ros_managed"` \| `"sensor_controlled_fast_lin"` |
| `axis` / `direction` | `RobotAxis.Z` / `Direction.MINUS` | |
| `linear_mm_s` | `25.0` | Contact speed; must be > 0 for axes 1–3 |
| `angular_deg_s` | `None` | Required (> 0) for rotary axes 4–6 |
| `frame`, `tool`, `user` | `"user"`, `0`, `0` | |
| `poll_interval_s` | `0.02` | Clamped to ≥ `0.005` when used |
| `timeout_s` | `10.0` | Absolute deadline from start |
| `approach_velocity` / `approach_acceleration` | `10.0` / `10.0` | Approach move + ROS fast-lin |
| `preflight_condition_read_attempts` | `2` | Reads before motion |
| `condition_read_failure_limit` | `3` | Consecutive read failures before `condition_unreadable_during_servo` |
| `allow_subzero_descent` | `False` | Passed through to `start_servo_jog` |
| `disable_collision_checking` | `False` | Passed through; see the override rules below |
| `maximum_travel_mm` | `None` | Travel guard from the start pose |
| `minimum_z_mm` | `None` | Z floor guard |
| `initial_linear_mm_s` | `None` | Two-speed descent stage 1 |
| `slowdown_z_mm` | `None` | Two-speed descent switch point |
| `controlled_stop_duration_s` | `0.20` | ROS-managed stop window |
| `stop_confirmation_timeout_s` | `3.0` | Must be finite and > 0 |

**Two-speed validation** (`_validate_config`): `initial_linear_mm_s` and
`slowdown_z_mm` must be set **together** (`incomplete_slowdown_config`), and if
set they require `axis == Z`, `direction == MINUS`, and positive finite values
(`invalid_slowdown_config`).

### `ServoRetractConfig` (frozen)

| Field | Default | Notes |
|-------|---------|-------|
| `target_pose` | `None` | Absolute retract target (alternative to `distance_mm`) |
| `distance_mm` | `None` | Relative Z lift; **exactly one** of `target_pose` / `distance_mm` must be usable |
| `motion_type` | `SERVO` | `ServoRetractMotionType.parse()` accepts the enum or the strings `"servo"` / `"ptp"` / `"fast_lin"`; anything else → `ValueError("Unsupported Servo retract motion type …")`. Coerced in `__post_init__` |
| `linear_mm_s` | `25.0` | |
| `ptp_velocity_percent` / `ptp_acceleration_percent` | `30.0` / `30.0` | PTP retract |
| `fast_lin_velocity_percent` / `fast_lin_acceleration_percent` | `80.0` / `60.0` | Fast-LIN retract |
| `poll_interval_s` / `timeout_s` | `0.02` / `10.0` | |
| `position_tolerance_mm` | `2.0` | Completion tolerance |
| `maximum_distance_mm` | `500.0` | Default bound when `safety_margin_mm is None` |
| `safety_margin_mm` | `None` | If set, bound becomes `requested_distance + safety_margin` |
| `final_linear_mm_s` / `slowdown_distance_mm` | `None` / `None` | Two-speed retract; both or neither (`invalid_retract_speed_transition`) |
| `progress_timeout_s` | `1.5` | Independent progress watchdog |

### `ServoUntilConditionResult` (frozen)

```python
success, detected, timed_out, start_failed
condition_failed, guard_triggered
retracted, retract_failed, stop_failed
contact_pose: tuple[float, ...] | None   # first 6 elements only
elapsed_s: float                         # max(0, monotonic - started)
message: str
```

`_result()` is the single construction point: it clamps `elapsed_s`, truncates
`contact_pose` to 6 values, and `None`s it when shorter.

---

## Execution modes

Selected by `cfg.execution_mode` after validation, preflight, approach, and
travel-guard setup:

### `legacy` (default)

1. `_move_to_approach()` if `approach_pose` given
2. `start_servo_jog(axis, direction, linear_mm_s/angular_deg_s, frame, tool, user)`
   — `allow_subzero_descent` / `disable_collision_checking` forwarded when set
3. Poll loop (`>= 0.005 s`): cancel → condition read → travel guards → two-speed
   slowdown → stop guard → timeout → sleep
4. On detection: `_stop_servo()`, capture `contact_pose`, then optional
   `_retract()`

**Two-speed descent:** when `initial_linear_mm_s` is set, the jog starts at the
fast speed and `_slowdown_reached()` (`Z` axis, `MINUS` direction,
`current_z <= slowdown_z_mm`) stops it and restarts at `linear_mm_s`. A failed
stop/start in that transition returns `slowdown_servo_stop_failed:*` /
`slowdown_servo_start_failed:*`.

**Collision-checking override:** if `disable_collision_checking` is set **and**
the retract is `motion_type == "servo"`, the override is *held* across the
contact stop into the retract (`collision_override_held`). The `finally` block
always restores it — the comment notes *"The contact stop may intentionally keep
collision checking disabled for retract. Always restore it on every final exit,
including retract-start and exception failures."*

The `finally` block also stops a still-running servo (and force-stops if the stop
fails), so no path leaves motion running.

### `ros_managed`

Delegates the descent to ROS 2 via four required capabilities on `robot`:

```python
start_conditional_servo(request)
publish_conditional_servo_sensor(sensor, state, stream_id, sequence, detected_monotonic_ns)
get_conditional_servo_status()
cancel_conditional_servo()
```

Missing capabilities → `ros_managed_unavailable:missing_capabilities:<names>`.

The request carries a `fast_lin` block (position = start with `z = minimum_z_mm`,
`trajectory_optimizer: "TOTG"`, `controlled_stop_duration_s`), a `servo` block,
a `condition` block (`required_state: True`, `require_fresh_transition: True`),
an optional `boundary` for `minimum_z_mm`, plus
`sensor_stale_timeout_s = max(0.25, poll_interval_s × 10)` and
`restore_collision_checking: True`.

While running, the loop publishes sensor state (on change or every ≥ 100 ms),
honours cancel/stop-guard/read-failure limits, and polls status. An
`operation_id` mismatch means another operation took over →
`ros_managed_operation_replaced`. Terminal `state` maps to a result message,
including `boundary_reached → minimum_z_reached`, `sensor_fault →
condition_stream_failed`. Timing is logged as `[CONDITIONAL_SERVO_TIMING]` and
`[CONDITIONAL_SERVO_PHASE_TIMING]`.

Two-speed descent is rejected up front:
`ros_managed_unsupported:two_speed_descent`.

### `sensor_controlled_fast_lin`

> "Diagnostic replacement for conditional Servo using one bounded Fast LIN."

Requires `start_pose` **and** `minimum_z_mm` (it bounds itself by geometry rather
than a travel counter); missing either → `sensor_controlled_fast_lin_missing_start_or_minimum_z`.
Needs `robot.move_fast_linear` → otherwise `sensor_controlled_fast_lin_unsupported`.

It issues one bounded move to `z = minimum_z_mm` while polling the condition
itself, then performs a controlled stop and waits for execution to become
inactive (`sensor_controlled_fast_lin_execution_still_active`) and for the pose to
be stationary (`sensor_controlled_fast_lin_stationary_unconfirmed`).

`_SensorPollMetrics` accumulates every poll: achieved Hz, cycle/condition/Modbus
read latencies (avg/p50/p95/max), attempts, retries, failed attempts/calls, and
missing diagnostics — flushed as one `WARNING`
`[SENSOR_CONTROLLED_FAST_LIN_SENSOR_METRICS]` line on exit.

---

## Retract

`_retract()` validates before moving and returns `(ok, message)`:

| Check | Message |
|-------|---------|
| Current pose unreadable | `retract_position_unreadable` |
| Non-finite/≤ 0 `distance_mm` | `invalid_retract_distance` |
| No valid `target_pose` | `invalid_retract_pose` |
| Non-positive `linear_mm_s` | `invalid_retract_linear_speed` |
| Half-configured or invalid speed transition | `invalid_retract_speed_transition` |
| Target not above contact (`requested_distance <= tolerance`) | `retract_target_not_above_contact` |
| `requested_distance > maximum_distance` | `retract_maximum_distance_exceeded` |
| `on_retract_start` raised | `retract_start_callback_failed` |
| Unknown motion type | `invalid_retract_motion_type` |

Dispatch by `motion_type`:

| Type | Implementation |
|------|----------------|
| `"servo"` | Prefers `robot.servo_jog_to_z(...)` when available — a target-bounded ROS primitive that takes both speeds, slowdown distance, tolerance, max distance, an auto-derived timeout, and `disable_collision_checking`. A `dict` response with `success` → done; otherwise `target_bounded_retract_<error>`. Falls back to a polled servo jog |
| `"ptp"` | `_retract_ptp()` — `ptp_velocity_percent` / `ptp_acceleration_percent` |
| `"fast_lin"` | `_retract_fast_linear()` — `fast_lin_velocity_percent` / `fast_lin_acceleration_percent` |

Timeouts are deliberately floored, with an in-code rationale:

> The configured jog speed is an upper command value; acceleration, controller
> scaling, and transport sampling can make a long retract take materially longer
> than distance / commanded speed. Keep the explicit timeout as a floor and
> derive a conservative distance-aware deadline. The independent progress
> watchdog still stops stalled motion.

```
distance_aware_timeout = requested_distance / minimum_speed * 4.0 + 1.0
effective_timeout      = max(configured timeout_s, distance_aware_timeout)
```

---

## Result message catalogue

Grouped by phase — useful for grepping logs and asserting in tests.

| Phase | Messages |
|-------|----------|
| Validation | `invalid_execution_mode`, `invalid_axis`, `invalid_linear_speed`, `invalid_angular_speed`, `invalid_maximum_travel`, `invalid_minimum_z`, `invalid_stop_confirmation_timeout`, `incomplete_slowdown_config`, `invalid_slowdown_config` |
| Preflight / approach | `condition_unreadable_before_motion`, `condition_already_active_before_motion`, `condition_already_active`, `approach_failed`, `condition_unreadable_after_approach`, `condition_already_active_before_servo` |
| Pre-servo guards | `travel_guard_position_unreadable_before_servo`, `minimum_z_reached_before_servo` |
| Descent | `cancelled`, `condition_unreadable_during_servo`, `servo_start_failed:<ret>`, `servo_stop_failed:<ret>`, `slowdown_servo_stop_failed:<ret>`, `slowdown_servo_start_failed:<ret>` |
| Travel guards | `travel_guard_position_unreadable`, `minimum_z_reached`, `maximum_travel_reached` |
| Stop guard | `stop_guard_unreadable`, `stop_guard_triggered` |
| Outcome | `timeout`, `condition_detected`, `condition_detected_and_retracted` |
| ROS-managed | `ros_managed_unavailable:missing_capabilities:*`, `ros_managed_unavailable:no_response`, `ros_managed_unavailable:<error>`, `ros_managed_fast_lin_missing_start_or_minimum_z`, `ros_managed_fast_lin_start_failed:*`, `ros_managed_unsupported:two_speed_descent`, `ros_managed_operation_replaced`, `ros_managed_unknown_state` |
| Fast-LIN diagnostic | `sensor_controlled_fast_lin_missing_start_or_minimum_z`, `sensor_controlled_fast_lin_unsupported`, `cancelled_before/during_sensor_controlled_fast_lin`, `stop_guard_triggered_during_sensor_controlled_fast_lin`, `sensor_controlled_fast_lin_condition_unreadable`, `sensor_controlled_fast_lin_stop_failed`, `sensor_controlled_fast_lin_execution_still_active`, `sensor_controlled_fast_lin_stationary_unconfirmed`, `sensor_controlled_fast_lin_timeout` |
| Retract | see the retract table above, plus `retract_timeout`, `stop_guard_*`, `retract_servo_start_failed:*`, `retract_servo_stop_failed:*` |

`message.startswith("stop_guard")` is what sets `guard_triggered=True` on a
failed retract; `message == "retract_timeout"` sets `timed_out=True`.

---

## Consumers

| Consumer | Usage |
|----------|-------|
| `src/robot_systems/paint/paint_robot_system.py` | Builds `VacuumPickupCondition` and `TimedDummyPickupCondition` |
| `src/robot_systems/paint/processes/paint/execute/pickup_executor.py` | Imports the procedure + configs |
| `src/robot_systems/paint/processes/paint/execution_machine/handlers/magazine_load/magazine_execute_pickup_release_handler.py` | Imports the condition/procedure types |

---

## Design Notes

- **Duck-typed robot.** `getattr(self._robot, "servo_jog_to_z", None)` and
  `getattr(self._robot, "move_fast_linear", None)` mean every optional primitive
  degrades to a fallback or a specific error message instead of `AttributeError`.
- **Return codes are normalised** by `_return_code_ok(ret)`: `bool` → itself,
  anything `int(ret) == 0` → ok, everything else → failure. So `True`, `0`, and
  `"0"`-like values all work.
- **One result constructor.** Every exit goes through `_result()`, which keeps the
  11 boolean fields and `elapsed_s`/`contact_pose` handling consistent across
  three execution modes.
- **`finally` is load-bearing.** It stops leftover servo motion and restores
  collision checking regardless of which return path was taken.
- **No platform imports beyond `src.engine.robot.enums`.** The package takes
  `robot` and `condition` as opaque collaborators, which is why it can be reused
  by any robot system.
