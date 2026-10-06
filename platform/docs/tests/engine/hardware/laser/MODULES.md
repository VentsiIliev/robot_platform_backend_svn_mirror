# Module reference: `tests/engine/hardware/laser`

[Package guide](README.md) · [Complete source index](../../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [i_laser_control.py](#i_laser_controlpy)

## `__init__.py`

Source: [tests/engine/hardware/laser/__init__.py](../../../../../tests/engine/hardware/laser/__init__.py).

No top-level functions, classes or public value declarations; inspect the source for imports or entry-point statements.

## `i_laser_control.py`

Source: [tests/engine/hardware/laser/i_laser_control.py](../../../../../tests/engine/hardware/laser/i_laser_control.py).

### `ILaserControl`

```python
class ILaserControl(ABC):
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
