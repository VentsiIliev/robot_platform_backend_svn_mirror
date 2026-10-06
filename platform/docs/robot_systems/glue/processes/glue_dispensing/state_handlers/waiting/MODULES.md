# Module reference: `src/robot_systems/glue/processes/glue_dispensing/state_handlers/waiting`

[Package guide](README.md) · [Complete source index](../../../../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [handle_routing_path_completion_wait.py](#handle_routing_path_completion_waitpy)
- [handle_waiting_for_final_position.py](#handle_waiting_for_final_positionpy)
- [handle_waiting_for_pump_thread.py](#handle_waiting_for_pump_threadpy)

## `__init__.py`

Source: [src/robot_systems/glue/processes/glue_dispensing/state_handlers/waiting/__init__.py](../../../../../../../src/robot_systems/glue/processes/glue_dispensing/state_handlers/waiting/__init__.py).

No top-level functions, classes or public value declarations; inspect the source for imports or entry-point statements.

## `handle_routing_path_completion_wait.py`

Source: [src/robot_systems/glue/processes/glue_dispensing/state_handlers/waiting/handle_routing_path_completion_wait.py](../../../../../../../src/robot_systems/glue/processes/glue_dispensing/state_handlers/waiting/handle_routing_path_completion_wait.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `src.robot_systems.glue.processes.glue_dispensing.dispensing_state`.

### `handle_routing_path_completion_wait`

```python
def handle_routing_path_completion_wait(context) -> GlueDispensingState
```

## `handle_waiting_for_final_position.py`

Source: [src/robot_systems/glue/processes/glue_dispensing/state_handlers/waiting/handle_waiting_for_final_position.py](../../../../../../../src/robot_systems/glue/processes/glue_dispensing/state_handlers/waiting/handle_waiting_for_final_position.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `math`, `src.robot_systems.glue.processes.glue_dispensing.dispensing_error`, `src.robot_systems.glue.processes.glue_dispensing.dispensing_state`, `time`.

### `_dist`

```python
def _dist(a, b) -> float
```

### `handle_waiting_for_final_position`

```python
def handle_waiting_for_final_position(context) -> GlueDispensingState
```

## `handle_waiting_for_pump_thread.py`

Source: [src/robot_systems/glue/processes/glue_dispensing/state_handlers/waiting/handle_waiting_for_pump_thread.py](../../../../../../../src/robot_systems/glue/processes/glue_dispensing/state_handlers/waiting/handle_waiting_for_pump_thread.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `logging`, `src.robot_systems.glue.processes.glue_dispensing.dispensing_error`, `src.robot_systems.glue.processes.glue_dispensing.dispensing_state`, `time`.

### `handle_waiting_for_pump_thread`

```python
def handle_waiting_for_pump_thread(context) -> GlueDispensingState
```
