# Module reference: `src/engine/hardware/laser`

[Package guide](README.md) · [Complete source index](../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [i_laser_control.py](#i_laser_controlpy)
- [modbus_laser_control.py](#modbus_laser_controlpy)

## `__init__.py`

Source: [src/engine/hardware/laser/__init__.py](../../../../src/engine/hardware/laser/__init__.py).

Imports (including optional/function-local imports; not a startup dependency list): `src.engine.hardware.laser.i_laser_control`, `src.engine.hardware.laser.modbus_laser_control`.

Package-level import/export surface:

```python
from src.engine.hardware.laser.i_laser_control import ILaserControl
from src.engine.hardware.laser.modbus_laser_control import ModbusLaserControl
```

Module declarations (expressions are shown without evaluating them):

```python
__all__ = ['ILaserControl', 'ModbusLaserControl']
```

## `i_laser_control.py`

Source: [src/engine/hardware/laser/i_laser_control.py](../../../../src/engine/hardware/laser/i_laser_control.py).

Imports (including optional/function-local imports; not a startup dependency list): `abc`.

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

## `modbus_laser_control.py`

Source: [src/engine/hardware/laser/modbus_laser_control.py](../../../../src/engine/hardware/laser/modbus_laser_control.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `src.engine.core.i_health_checkable`, `src.engine.hardware.communication.i_register_transport`, `src.engine.hardware.laser.i_laser_control`, `src.engine.hardware.xinje`.

### `ModbusLaserControl`

```python
class ModbusLaserControl(ILaserControl, IHealthCheckable):
```

Laser control through a register/coil transport.

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, transport: IRegisterTransport, register: int | str='Y5', on_value: int=1, off_value: int=0) -> None
```

```python
def turn_on(self) -> None
```

```python
def turn_off(self) -> None
```

```python
def read_state(self) -> bool
```

```python
def is_healthy(self) -> bool
```
