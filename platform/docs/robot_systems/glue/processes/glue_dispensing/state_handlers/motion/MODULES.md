# Module reference: `src/robot_systems/glue/processes/glue_dispensing/state_handlers/motion`

[Package guide](README.md) · [Complete source index](../../../../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [handle_advancing_path.py](#handle_advancing_pathpy)
- [handle_moving_to_first_point.py](#handle_moving_to_first_pointpy)
- [handle_sending_path_points.py](#handle_sending_path_pointspy)

## `__init__.py`

Source: [src/robot_systems/glue/processes/glue_dispensing/state_handlers/motion/__init__.py](../../../../../../../src/robot_systems/glue/processes/glue_dispensing/state_handlers/motion/__init__.py).

No top-level functions, classes or public value declarations; inspect the source for imports or entry-point statements.

## `handle_advancing_path.py`

Source: [src/robot_systems/glue/processes/glue_dispensing/state_handlers/motion/handle_advancing_path.py](../../../../../../../src/robot_systems/glue/processes/glue_dispensing/state_handlers/motion/handle_advancing_path.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `logging`, `src.robot_systems.glue.processes.glue_dispensing.dispensing_state`.

### `handle_advancing_path`

```python
def handle_advancing_path(context) -> GlueDispensingState
```

## `handle_moving_to_first_point.py`

Source: [src/robot_systems/glue/processes/glue_dispensing/state_handlers/motion/handle_moving_to_first_point.py](../../../../../../../src/robot_systems/glue/processes/glue_dispensing/state_handlers/motion/handle_moving_to_first_point.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `src.robot_systems.glue.processes.glue_dispensing.dispensing_error`, `src.robot_systems.glue.processes.glue_dispensing.dispensing_state`, `time`.

### `handle_moving_to_first_point`

```python
def handle_moving_to_first_point(context) -> GlueDispensingState
```

## `handle_sending_path_points.py`

Source: [src/robot_systems/glue/processes/glue_dispensing/state_handlers/motion/handle_sending_path_points.py](../../../../../../../src/robot_systems/glue/processes/glue_dispensing/state_handlers/motion/handle_sending_path_points.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `logging`, `src.robot_systems.glue.processes.glue_dispensing.dispensing_error`, `src.robot_systems.glue.processes.glue_dispensing.dispensing_state`.

### `handle_sending_path_points`

```python
def handle_sending_path_points(context) -> GlueDispensingState
```
