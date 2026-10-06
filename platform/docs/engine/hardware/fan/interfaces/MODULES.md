# Module reference: `src/engine/hardware/fan/interfaces`

[Package guide](README.md) · [Complete source index](../../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [i_fan_control.py](#i_fan_controlpy)

## `__init__.py`

Source: [src/engine/hardware/fan/interfaces/__init__.py](../../../../../src/engine/hardware/fan/interfaces/__init__.py).

Imports (including optional/function-local imports; not a startup dependency list): `src.engine.hardware.fan.interfaces.i_fan_control`.

Package-level import/export surface:

```python
from src.engine.hardware.fan.interfaces.i_fan_control import IFanControl
```

Module declarations (expressions are shown without evaluating them):

```python
__all__ = ['IFanControl']
```

## `i_fan_control.py`

Source: [src/engine/hardware/fan/interfaces/i_fan_control.py](../../../../../src/engine/hardware/fan/interfaces/i_fan_control.py).

Imports (including optional/function-local imports; not a startup dependency list): `abc`.

### `IFanControl`

```python
class IFanControl(ABC):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
@abstractmethod
def turn_on(self) -> None
```

```python
@abstractmethod
def turn_off(self) -> None
```

```python
def read_state(self) -> bool
```

Read the configured hardware output without changing it.
