# Module reference: `src/engine/hardware/fan`

[Package guide](README.md) · [Complete source index](../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)

## `__init__.py`

Source: [src/engine/hardware/fan/__init__.py](../../../../src/engine/hardware/fan/__init__.py).

Imports (including optional/function-local imports; not a startup dependency list): `src.engine.hardware.fan.interfaces.i_fan_control`, `src.engine.hardware.fan.modbus.modbus_fan_control`.

Package-level import/export surface:

```python
from src.engine.hardware.fan.interfaces.i_fan_control import IFanControl
from src.engine.hardware.fan.modbus.modbus_fan_control import ModbusFanControl
```

Module declarations (expressions are shown without evaluating them):

```python
__all__ = ['IFanControl', 'ModbusFanControl']
```
