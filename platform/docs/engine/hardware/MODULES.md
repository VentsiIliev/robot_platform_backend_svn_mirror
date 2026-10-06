# Module reference: `src/engine/hardware`

[Package guide](README.md) · [Complete source index](../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)

## `__init__.py`

Source: [src/engine/hardware/__init__.py](../../../src/engine/hardware/__init__.py).

Imports (including optional/function-local imports; not a startup dependency list): `src.engine.hardware.communication.modbus.i_modbus_action_service`, `src.engine.hardware.communication.modbus.modbus`, `src.engine.hardware.communication.modbus.modbus_action_service`.

Package-level import/export surface:

```python
from src.engine.hardware.communication.modbus.modbus import ModbusConfig, ModbusConfigSerializer
from src.engine.hardware.communication.modbus.i_modbus_action_service import IModbusActionService
from src.engine.hardware.communication.modbus.modbus_action_service import ModbusActionService
```

Module declarations (expressions are shown without evaluating them):

```python
__all__ = ['ModbusConfig', 'ModbusConfigSerializer', 'IModbusActionService', 'ModbusActionService']
```
