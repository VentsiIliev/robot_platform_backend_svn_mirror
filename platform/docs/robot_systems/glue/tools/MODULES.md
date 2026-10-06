# Module reference: `src/robot_systems/glue/tools`

[Package guide](README.md) · [Complete source index](../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [glue_laser_control.py](#glue_laser_controlpy)

## `__init__.py`

Source: [src/robot_systems/glue/tools/__init__.py](../../../../src/robot_systems/glue/tools/__init__.py).

No top-level functions, classes or public value declarations; inspect the source for imports or entry-point statements.

## `glue_laser_control.py`

Source: [src/robot_systems/glue/tools/glue_laser_control.py](../../../../src/robot_systems/glue/tools/glue_laser_control.py).

Imports (including optional/function-local imports; not a startup dependency list): `logging`, `src.engine.hardware.communication.i_register_transport`, `src.engine.hardware.laser.i_laser_control`.

### `GlueLaserControl`

```python
class GlueLaserControl(ILaserControl):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, transport: IRegisterTransport)
```

```python
def turn_on(self) -> None
```

```python
def turn_off(self) -> None
```
