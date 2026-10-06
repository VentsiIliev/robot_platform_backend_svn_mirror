# Module reference: `src/engine/robot/procedures`

[Package guide](README.md) · [Complete source index](../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [dummy_pickup_condition.py](#dummy_pickup_conditionpy)
- [servo_until_condition.py](#servo_until_conditionpy)
- [vacuum_pickup_condition.py](#vacuum_pickup_conditionpy)

## `__init__.py`

Source: [src/engine/robot/procedures/__init__.py](../../../../src/engine/robot/procedures/__init__.py).

Imports (including optional/function-local imports; not a startup dependency list): `.dummy_pickup_condition`, `.servo_until_condition`, `.vacuum_pickup_condition`.

Package-level import/export surface:

```python
from .servo_until_condition import ServoUntilConditionConfig, ServoUntilConditionResult, ServoUntilConditionProcedure, ServoRetractConfig, ServoRetractMotionType
from .dummy_pickup_condition import TimedDummyPickupCondition
from .vacuum_pickup_condition import VacuumPickupCondition
```

Module declarations (expressions are shown without evaluating them):

```python
__all__ = ['ServoUntilConditionConfig', 'ServoUntilConditionResult', 'ServoUntilConditionProcedure', 'ServoRetractConfig', 'ServoRetractMotionType', 'TimedDummyPickupCondition', 'VacuumPickupCondition']
```

## `dummy_pickup_condition.py`

Source: [src/engine/robot/procedures/dummy_pickup_condition.py](../../../../src/engine/robot/procedures/dummy_pickup_condition.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `logging`, `time`.

### `TimedDummyPickupCondition`

```python
class TimedDummyPickupCondition:
```

Test-only pickup condition that becomes active after a delay.

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, detect_after_s: float=1.0) -> None
```

```python
def on_servo_start(self) -> None
```

```python
def is_active(self) -> bool
```

## `servo_until_condition.py`

Source: [src/engine/robot/procedures/servo_until_condition.py](../../../../src/engine/robot/procedures/servo_until_condition.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `dataclasses`, `enum`, `logging`, `math`, `src.engine.robot.enums.axis`, `time`, `typing`, `uuid`.

### `ServoRetractMotionType`

```python
class ServoRetractMotionType(StrEnum):
```

Declared fields/defaults:

```python
SERVO = 'servo'
PTP = 'ptp'
FAST_LINEAR = 'fast_lin'
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
@classmethod
def parse(cls, value: object) -> 'ServoRetractMotionType'
```

### `PickupCondition`

```python
class PickupCondition(Protocol):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def is_active(self) -> bool
```

### `ServoUntilConditionConfig`

```python
@dataclass(frozen=True)
class ServoUntilConditionConfig:
```

Declared fields/defaults:

```python
execution_mode: str = 'legacy'
axis: RobotAxis = RobotAxis.Z
direction: Direction = Direction.MINUS
linear_mm_s: float = 25.0
angular_deg_s: float | None = None
frame: str | int = 'user'
tool: int = 0
user: int = 0
poll_interval_s: float = 0.02
timeout_s: float = 10.0
approach_velocity: float = 10.0
approach_acceleration: float = 10.0
preflight_condition_read_attempts: int = 2
condition_read_failure_limit: int = 3
allow_subzero_descent: bool = False
disable_collision_checking: bool = False
maximum_travel_mm: float | None = None
minimum_z_mm: float | None = None
initial_linear_mm_s: float | None = None
slowdown_z_mm: float | None = None
controlled_stop_duration_s: float | None = 0.2
stop_confirmation_timeout_s: float = 3.0
```

### `ServoRetractConfig`

```python
@dataclass(frozen=True)
class ServoRetractConfig:
```

Declared fields/defaults:

```python
target_pose: Sequence[float] | None = None
distance_mm: float | None = None
motion_type: ServoRetractMotionType = ServoRetractMotionType.SERVO
linear_mm_s: float = 25.0
ptp_velocity_percent: float = 30.0
ptp_acceleration_percent: float = 30.0
poll_interval_s: float = 0.02
timeout_s: float = 10.0
position_tolerance_mm: float = 2.0
maximum_distance_mm: float = 500.0
safety_margin_mm: float | None = None
final_linear_mm_s: float | None = None
slowdown_distance_mm: float | None = None
progress_timeout_s: float = 1.5
fast_lin_velocity_percent: float = 80.0
fast_lin_acceleration_percent: float = 60.0
```

### `ServoUntilConditionResult`

```python
@dataclass(frozen=True)
class ServoUntilConditionResult:
```

Declared fields/defaults:

```python
success: bool
detected: bool
timed_out: bool
start_failed: bool
elapsed_s: float
message: str
condition_failed: bool = False
guard_triggered: bool = False
retracted: bool = False
retract_failed: bool = False
stop_failed: bool = False
contact_pose: tuple[float, ...] | None = None
```

### `_SensorPollMetrics`

```python
class _SensorPollMetrics:
```

In-memory measurements for one sensor-controlled motion.

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, configured_sleep_s: float) -> None
```

```python
def record(self, started_ns: int, finished_ns: int, diagnostics: dict[str, object] | None) -> None
```

```python
def log(self, *, reason: str, task_id: object) -> None
```

### `ServoUntilConditionProcedure`

```python
class ServoUntilConditionProcedure:
```

Generic servo-until-condition primitive. This is intentionally robot-system agnostic. The condition can be a vacuum sensor, force threshold, distance sensor, dummy test trigger, or any object exposing is_active().

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, robot, condition: PickupCondition | Callable[[], bool]) -> None
```

```python
def run(self, *, approach_pose: Sequence[float] | None=None, config: ServoUntilConditionConfig | None=None, retract: ServoRetractConfig | None=None, cancel_requested: Callable[[], bool] | None=None, stop_guard: Callable[[], bool] | None=None, on_retract_start: Callable[[tuple[float, ...], float], None] | None=None) -> ServoUntilConditionResult
```

## `vacuum_pickup_condition.py`

Source: [src/engine/robot/procedures/vacuum_pickup_condition.py](../../../../src/engine/robot/procedures/vacuum_pickup_condition.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `src.engine.hardware.vacuum_sensor.interfaces.i_vacuum_sensor_service`.

### `VacuumPickupCondition`

```python
class VacuumPickupCondition:
```

Adapter from IVacuumSensorService to the generic pickup condition shape.

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, vacuum_sensor: IVacuumSensorService) -> None
```

```python
def is_active(self) -> bool
```

```python
def get_read_diagnostics(self) -> dict[str, object] | None
```

Expose cached transport timing when the concrete sensor supports it.
