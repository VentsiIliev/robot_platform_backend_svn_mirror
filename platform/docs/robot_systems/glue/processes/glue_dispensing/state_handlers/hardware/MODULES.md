# Module reference: `src/robot_systems/glue/processes/glue_dispensing/state_handlers/hardware`

[Package guide](README.md) · [Complete source index](../../../../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [generator_handlers.py](#generator_handlerspy)
- [handle_starting_pump_adjustment_thread.py](#handle_starting_pump_adjustment_threadpy)
- [handle_waiting_for_pump_thread_ready.py](#handle_waiting_for_pump_thread_readypy)
- [pump_handlers.py](#pump_handlerspy)

## `__init__.py`

Source: [src/robot_systems/glue/processes/glue_dispensing/state_handlers/hardware/__init__.py](../../../../../../../src/robot_systems/glue/processes/glue_dispensing/state_handlers/hardware/__init__.py).

No top-level functions, classes or public value declarations; inspect the source for imports or entry-point statements.

## `generator_handlers.py`

Source: [src/robot_systems/glue/processes/glue_dispensing/state_handlers/hardware/generator_handlers.py](../../../../../../../src/robot_systems/glue/processes/glue_dispensing/state_handlers/hardware/generator_handlers.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `logging`, `src.robot_systems.glue.processes.glue_dispensing.dispensing_error`, `src.robot_systems.glue.processes.glue_dispensing.dispensing_state`, `time`.

### `handle_turning_on_generator`

```python
def handle_turning_on_generator(context) -> GlueDispensingState
```

### `handle_turning_off_generator`

```python
def handle_turning_off_generator(context) -> GlueDispensingState
```

## `handle_starting_pump_adjustment_thread.py`

Source: [src/robot_systems/glue/processes/glue_dispensing/state_handlers/hardware/handle_starting_pump_adjustment_thread.py](../../../../../../../src/robot_systems/glue/processes/glue_dispensing/state_handlers/hardware/handle_starting_pump_adjustment_thread.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `logging`, `src.robot_systems.glue.processes.glue_dispensing.dispensing_error`, `src.robot_systems.glue.processes.glue_dispensing.dispensing_state`.

### `handle_starting_pump_adjustment_thread`

```python
def handle_starting_pump_adjustment_thread(context, adjust_pump_speed: bool=True) -> GlueDispensingState
```

## `handle_waiting_for_pump_thread_ready.py`

Source: [src/robot_systems/glue/processes/glue_dispensing/state_handlers/hardware/handle_waiting_for_pump_thread_ready.py](../../../../../../../src/robot_systems/glue/processes/glue_dispensing/state_handlers/hardware/handle_waiting_for_pump_thread_ready.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `src.robot_systems.glue.processes.glue_dispensing.dispensing_error`, `src.robot_systems.glue.processes.glue_dispensing.dispensing_state`.

### `handle_waiting_for_pump_thread_ready`

```python
def handle_waiting_for_pump_thread_ready(context) -> GlueDispensingState
```

## `pump_handlers.py`

Source: [src/robot_systems/glue/processes/glue_dispensing/state_handlers/hardware/pump_handlers.py](../../../../../../../src/robot_systems/glue/processes/glue_dispensing/state_handlers/hardware/pump_handlers.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `logging`, `src.robot_systems.glue.processes.glue_dispensing.dispensing_error`, `src.robot_systems.glue.processes.glue_dispensing.dispensing_state`.

### `_get_pump_controller_exception`

```python
def _get_pump_controller_exception(context)
```

### `handle_turning_on_pump`

```python
def handle_turning_on_pump(context) -> GlueDispensingState
```

### `handle_turning_off_pump`

```python
def handle_turning_off_pump(context, turn_off_pump: bool=True) -> GlueDispensingState
```
