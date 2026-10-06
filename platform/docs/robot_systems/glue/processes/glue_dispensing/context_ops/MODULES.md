# Module reference: `src/robot_systems/glue/processes/glue_dispensing/context_ops`

[Package guide](README.md) · [Complete source index](../../../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [cleanup_ops.py](#cleanup_opspy)
- [motion_ops.py](#motion_opspy)
- [path_ops.py](#path_opspy)
- [pump_thread_ops.py](#pump_thread_opspy)

## `__init__.py`

Source: [src/robot_systems/glue/processes/glue_dispensing/context_ops/__init__.py](../../../../../../src/robot_systems/glue/processes/glue_dispensing/context_ops/__init__.py).

No top-level functions, classes or public value declarations; inspect the source for imports or entry-point statements.

## `cleanup_ops.py`

Source: [src/robot_systems/glue/processes/glue_dispensing/context_ops/cleanup_ops.py](../../../../../../src/robot_systems/glue/processes/glue_dispensing/context_ops/cleanup_ops.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `logging`.

### `DispensingCleanupOps`

```python
class DispensingCleanupOps:
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, context) -> None
```

```python
def stop_robot_motion_safely(self) -> None
```

```python
def stop_generator_if_running(self) -> None
```

```python
def stop_pump_if_running(self) -> None
```

```python
def shutdown_best_effort(self, include_motion: bool=True) -> None
```

## `motion_ops.py`

Source: [src/robot_systems/glue/processes/glue_dispensing/context_ops/motion_ops.py](../../../../../../src/robot_systems/glue/processes/glue_dispensing/context_ops/motion_ops.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `math`.

### `DispensingMotionOps`

```python
class DispensingMotionOps:
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, context) -> None
```

```python
def get_reach_start_threshold(self) -> float
```

```python
def is_at_current_path_start(self, threshold: float) -> bool
```

## `path_ops.py`

Source: [src/robot_systems/glue/processes/glue_dispensing/context_ops/path_ops.py](../../../../../../src/robot_systems/glue/processes/glue_dispensing/context_ops/path_ops.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `src.robot_systems.glue.processes.glue_dispensing.dispensing_path`.

### `DispensingPathOps`

```python
class DispensingPathOps:
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, context) -> None
```

```python
def has_remaining_paths(self) -> bool
```

```python
def get_current_path_entry(self)
```

```python
def load_current_path(self) -> None
```

```python
def restart_current_path(self) -> None
```

```python
def load_current_path_from_progress(self) -> None
```

```python
def resume_current_path_from_progress(self) -> None
```

```python
def has_current_path_loaded(self) -> bool
```

```python
def get_current_path_start_point(self)
```

```python
def get_current_path_end_point(self)
```

```python
def advance_to_next_path(self) -> None
```

```python
def skip_current_path(self) -> None
```

```python
def mark_first_point_reached(self) -> None
```

## `pump_thread_ops.py`

Source: [src/robot_systems/glue/processes/glue_dispensing/context_ops/pump_thread_ops.py](../../../../../../src/robot_systems/glue/processes/glue_dispensing/context_ops/pump_thread_ops.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `logging`, `src.robot_systems.glue.processes.glue_dispensing.dispensing_state`, `src.robot_systems.glue.processes.glue_dispensing.pump_speed_adjuster`, `threading`.

### `DispensingPumpThreadOps`

```python
class DispensingPumpThreadOps:
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, context) -> None
```

```python
def clear(self) -> None
```

```python
def create_ready_event(self) -> None
```

```python
def start_for_current_path(self, motor_address: int, reach_end_threshold: float) -> None
```

```python
def capture_progress(self, pump_thread) -> None
```

```python
def get_failure_exception(self, pump_thread)
```

```python
def handle_interruption(self, pump_thread, paused_state)
```
