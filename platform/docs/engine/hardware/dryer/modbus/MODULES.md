# Module reference: `src/engine/hardware/dryer/modbus`

[Package guide](README.md) · [Complete source index](../../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [modbus_dryer_factory.py](#modbus_dryer_factorypy)
- [modbus_dryer_transport.py](#modbus_dryer_transportpy)

## `__init__.py`

Source: [src/engine/hardware/dryer/modbus/__init__.py](../../../../../src/engine/hardware/dryer/modbus/__init__.py).

Imports (including optional/function-local imports; not a startup dependency list): `src.engine.hardware.dryer.modbus.modbus_dryer_factory`, `src.engine.hardware.dryer.modbus.modbus_dryer_transport`.

Package-level import/export surface:

```python
from src.engine.hardware.dryer.modbus.modbus_dryer_factory import build_modbus_dryer_controller
from src.engine.hardware.dryer.modbus.modbus_dryer_transport import ModbusDryerTransport
```

Module declarations (expressions are shown without evaluating them):

```python
__all__ = ['ModbusDryerTransport', 'build_modbus_dryer_controller']
```

## `modbus_dryer_factory.py`

Source: [src/engine/hardware/dryer/modbus/modbus_dryer_factory.py](../../../../../src/engine/hardware/dryer/modbus/modbus_dryer_factory.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `src.engine.hardware.communication.modbus.modbus`, `src.engine.hardware.dryer.dryer_controller`, `src.engine.hardware.dryer.interfaces.i_dryer_controller`, `src.engine.hardware.dryer.modbus.modbus_dryer_transport`, `src.engine.hardware.dryer.models.dryer_config`.

### `build_modbus_dryer_controller`

```python
def build_modbus_dryer_controller(modbus_config: ModbusConfig, dryer_config: DryerConfig | None=None) -> IDryerController
```

## `modbus_dryer_transport.py`

Source: [src/engine/hardware/dryer/modbus/modbus_dryer_transport.py](../../../../../src/engine/hardware/dryer/modbus/modbus_dryer_transport.py).

Imports (including optional/function-local imports; not a startup dependency list): `src.engine.hardware.communication.modbus.modbus_register_transport`, `src.engine.hardware.dryer.interfaces.i_dryer_transport`.

### `ModbusDryerTransport`

```python
class ModbusDryerTransport(ModbusRegisterTransport, IDryerTransport):
```

Modbus RTU transport for dryer boards.
