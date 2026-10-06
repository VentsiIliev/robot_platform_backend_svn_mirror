# Module reference: `src/robot_systems/glue/processes/glue_dispensing/state_handlers/terminal`

[Package guide](README.md) · [Complete source index](../../../../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [terminal_handlers.py](#terminal_handlerspy)

## `__init__.py`

Source: [src/robot_systems/glue/processes/glue_dispensing/state_handlers/terminal/__init__.py](../../../../../../../src/robot_systems/glue/processes/glue_dispensing/state_handlers/terminal/__init__.py).

No top-level functions, classes or public value declarations; inspect the source for imports or entry-point statements.

## `terminal_handlers.py`

Source: [src/robot_systems/glue/processes/glue_dispensing/state_handlers/terminal/terminal_handlers.py](../../../../../../../src/robot_systems/glue/processes/glue_dispensing/state_handlers/terminal/terminal_handlers.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `logging`, `src.robot_systems.glue.processes.glue_dispensing.dispensing_state`.

### `handle_idle`

```python
def handle_idle(context) -> GlueDispensingState
```

### `handle_paused`

```python
def handle_paused(context) -> GlueDispensingState
```

### `handle_stopped`

```python
def handle_stopped(context) -> GlueDispensingState
```

### `handle_completed`

```python
def handle_completed(context) -> GlueDispensingState
```

### `handle_error`

```python
def handle_error(context) -> GlueDispensingState
```
