# Module reference: `src/robot_systems/glue/processes/glue_dispensing/state_handlers/startup`

[Package guide](README.md) · [Complete source index](../../../../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [handle_issuing_move_to_first_point.py](#handle_issuing_move_to_first_pointpy)
- [handle_loading_current_path.py](#handle_loading_current_pathpy)
- [handle_loading_path.py](#handle_loading_pathpy)
- [handle_resuming.py](#handle_resumingpy)
- [handle_starting.py](#handle_startingpy)

## `__init__.py`

Source: [src/robot_systems/glue/processes/glue_dispensing/state_handlers/startup/__init__.py](../../../../../../../src/robot_systems/glue/processes/glue_dispensing/state_handlers/startup/__init__.py).

No top-level functions, classes or public value declarations; inspect the source for imports or entry-point statements.

## `handle_issuing_move_to_first_point.py`

Source: [src/robot_systems/glue/processes/glue_dispensing/state_handlers/startup/handle_issuing_move_to_first_point.py](../../../../../../../src/robot_systems/glue/processes/glue_dispensing/state_handlers/startup/handle_issuing_move_to_first_point.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `src.robot_systems.glue.processes.glue_dispensing.dispensing_error`, `src.robot_systems.glue.processes.glue_dispensing.dispensing_state`.

### `handle_issuing_move_to_first_point`

```python
def handle_issuing_move_to_first_point(context) -> GlueDispensingState
```

## `handle_loading_current_path.py`

Source: [src/robot_systems/glue/processes/glue_dispensing/state_handlers/startup/handle_loading_current_path.py](../../../../../../../src/robot_systems/glue/processes/glue_dispensing/state_handlers/startup/handle_loading_current_path.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `src.robot_systems.glue.processes.glue_dispensing.dispensing_state`.

### `handle_loading_current_path`

```python
def handle_loading_current_path(context) -> GlueDispensingState
```

## `handle_loading_path.py`

Source: [src/robot_systems/glue/processes/glue_dispensing/state_handlers/startup/handle_loading_path.py](../../../../../../../src/robot_systems/glue/processes/glue_dispensing/state_handlers/startup/handle_loading_path.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `logging`, `src.robot_systems.glue.processes.glue_dispensing.dispensing_state`.

### `handle_loading_path`

```python
def handle_loading_path(context) -> GlueDispensingState
```

## `handle_resuming.py`

Source: [src/robot_systems/glue/processes/glue_dispensing/state_handlers/startup/handle_resuming.py](../../../../../../../src/robot_systems/glue/processes/glue_dispensing/state_handlers/startup/handle_resuming.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `src.robot_systems.glue.processes.glue_dispensing.dispensing_state`.

### `handle_resuming`

```python
def handle_resuming(context) -> GlueDispensingState
```

## `handle_starting.py`

Source: [src/robot_systems/glue/processes/glue_dispensing/state_handlers/startup/handle_starting.py](../../../../../../../src/robot_systems/glue/processes/glue_dispensing/state_handlers/startup/handle_starting.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `src.robot_systems.glue.processes.glue_dispensing.dispensing_state`.

### `handle_starting`

```python
def handle_starting(context) -> GlueDispensingState
```
