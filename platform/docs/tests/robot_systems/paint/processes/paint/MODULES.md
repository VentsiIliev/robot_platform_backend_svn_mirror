# Module reference: `tests/robot_systems/paint/processes/paint`

[Package guide](README.md) · [Complete source index](../../../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [test_motion_primitives.py](#test_motion_primitivespy)

## `test_motion_primitives.py`

Source: [tests/robot_systems/paint/processes/paint/test_motion_primitives.py](../../../../../../tests/robot_systems/paint/processes/paint/test_motion_primitives.py).

Imports (including optional/function-local imports; not a startup dependency list): `src.engine.robot.motion_sequence`, `src.robot_systems.paint.processes.paint.motion.executor`, `src.robot_systems.paint.processes.paint.operations.pickup.executor`, `src.robot_systems.paint.processes.paint.motion`, `src.robot_systems.paint.processes.paint.planning.projection.command_job`, `types`, `unittest`, `unittest.mock`.

### `_FakeClock`

```python
class _FakeClock:
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self) -> None
```

```python
def monotonic(self) -> float
```

```python
def sleep(self, duration: float) -> None
```

### `TestShiftPathRotation`

```python
class TestShiftPathRotation(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_returns_a_copy_when_shift_is_zero(self)
```

```python
def test_shifts_only_existing_rotation_components(self)
```

### `TestPosesClose`

```python
class TestPosesClose(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_rejects_missing_or_incomplete_poses(self)
```

```python
def test_uses_tolerance_for_linear_axes(self)
```

```python
def test_treats_wrapped_rz_as_equivalent(self)
```

### `TestPoseSampling`

```python
class TestPoseSampling(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_fresh_read_is_preferred_and_normalized(self)
```

```python
def test_missing_fresh_api_fails_loudly_without_legacy_fallback(self)
```

```python
def test_fresh_read_exception_is_propagated_as_explicit_pose_error(self)
```

```python
def test_invalid_fresh_pose_fails_loudly(self)
```

```python
def test_stability_requires_consecutive_samples_with_wrapped_angles(self)
```

```python
def test_unstable_samples_time_out(self)
```

### `TestOrderedMotionResume`

```python
class TestOrderedMotionResume(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_backend_resume_index_is_applied_to_original_command_list(self)
```

```python
def test_geometric_fallback_near_final_target_is_bounds_safe(self)
```

### `TestOrderedPaintContactCommands`

```python
class TestOrderedPaintContactCommands(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_builder_returns_typed_position_and_path_commands(self)
```
