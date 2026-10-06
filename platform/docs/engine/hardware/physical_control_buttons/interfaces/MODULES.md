# Module reference: `src/engine/hardware/physical_control_buttons/interfaces`

[Package guide](README.md) · [Complete source index](../../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [i_physical_control_buttons.py](#i_physical_control_buttonspy)

## `__init__.py`

Source: [src/engine/hardware/physical_control_buttons/interfaces/__init__.py](../../../../../src/engine/hardware/physical_control_buttons/interfaces/__init__.py).

Imports (including optional/function-local imports; not a startup dependency list): `src.engine.hardware.physical_control_buttons.interfaces.i_physical_control_buttons`.

Package-level import/export surface:

```python
from src.engine.hardware.physical_control_buttons.interfaces.i_physical_control_buttons import IPhysicalControlButtons
```

Module declarations (expressions are shown without evaluating them):

```python
__all__ = ['IPhysicalControlButtons']
```

## `i_physical_control_buttons.py`

Source: [src/engine/hardware/physical_control_buttons/interfaces/i_physical_control_buttons.py](../../../../../src/engine/hardware/physical_control_buttons/interfaces/i_physical_control_buttons.py).

Imports (including optional/function-local imports; not a startup dependency list): `abc`, `typing`.

### `IPhysicalControlButtons`

```python
class IPhysicalControlButtons(ABC):
```

Read the state of physical machine control buttons.

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
@abstractmethod
def read_states(self) -> Mapping[str, bool]
```

```python
@abstractmethod
def is_pressed(self, button: str) -> bool
```

```python
@abstractmethod
def set_button(self, button: str, pressed: bool) -> None
```

```python
@abstractmethod
def read_output_states(self) -> Mapping[str, bool]
```
