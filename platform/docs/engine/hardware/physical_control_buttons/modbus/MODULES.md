# Module reference: `src/engine/hardware/physical_control_buttons/modbus`

[Package guide](README.md) · [Complete source index](../../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [modbus_physical_control_buttons.py](#modbus_physical_control_buttonspy)
- [modbus_physical_control_buttons_factory.py](#modbus_physical_control_buttons_factorypy)

## `__init__.py`

Source: [src/engine/hardware/physical_control_buttons/modbus/__init__.py](../../../../../src/engine/hardware/physical_control_buttons/modbus/__init__.py).

Imports (including optional/function-local imports; not a startup dependency list): `src.engine.hardware.physical_control_buttons.modbus.modbus_physical_control_buttons`.

Package-level import/export surface:

```python
from src.engine.hardware.physical_control_buttons.modbus.modbus_physical_control_buttons import ModbusPhysicalControlButtons
```

Module declarations (expressions are shown without evaluating them):

```python
__all__ = ['ModbusPhysicalControlButtons']
```

## `modbus_physical_control_buttons.py`

Source: [src/engine/hardware/physical_control_buttons/modbus/modbus_physical_control_buttons.py](../../../../../src/engine/hardware/physical_control_buttons/modbus/modbus_physical_control_buttons.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `logging`, `src.engine.core.i_health_checkable`, `src.engine.hardware.communication.i_register_transport`, `src.engine.hardware.physical_control_buttons.interfaces.i_physical_control_buttons`, `src.engine.hardware.xinje`.

### `ModbusPhysicalControlButtons`

```python
class ModbusPhysicalControlButtons(IPhysicalControlButtons, IHealthCheckable):
```

Read Xinje digital inputs configured as physical control buttons.

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, transport: IRegisterTransport, inputs: dict[str, int | str], outputs: dict[str, int | str] | None=None) -> None
```

```python
def read_states(self) -> dict[str, bool]
```

```python
def is_pressed(self, button: str) -> bool
```

```python
def set_button(self, button: str, pressed: bool) -> None
```

```python
def read_output_states(self) -> dict[str, bool]
```

```python
def is_healthy(self) -> bool
```

## `modbus_physical_control_buttons_factory.py`

Source: [src/engine/hardware/physical_control_buttons/modbus/modbus_physical_control_buttons_factory.py](../../../../../src/engine/hardware/physical_control_buttons/modbus/modbus_physical_control_buttons_factory.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `src.engine.hardware.communication.modbus.modbus`, `src.engine.hardware.communication.transport_registry`, `src.engine.hardware.peripherals`, `src.engine.hardware.physical_control_buttons.interfaces.i_physical_control_buttons`, `src.engine.hardware.physical_control_buttons.modbus.modbus_physical_control_buttons`.

### `build_modbus_physical_control_buttons`

```python
def build_modbus_physical_control_buttons(modbus_config: ModbusConfig, peripheral_config: PeripheralConfig) -> IPhysicalControlButtons | None
```
