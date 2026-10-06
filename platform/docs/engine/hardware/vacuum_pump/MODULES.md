# Module reference: `src/engine/hardware/vacuum_pump`

[Package guide](README.md) · [Complete source index](../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [mock_runner.py](#mock_runnerpy)
- [vacuum_pump_controller.py](#vacuum_pump_controllerpy)

## `__init__.py`

Source: [src/engine/hardware/vacuum_pump/__init__.py](../../../../src/engine/hardware/vacuum_pump/__init__.py).

Imports (including optional/function-local imports; not a startup dependency list): `src.engine.hardware.vacuum_pump.interfaces.i_vacuum_pump_controller`, `src.engine.hardware.vacuum_pump.interfaces.i_vacuum_pump_transport`, `src.engine.hardware.vacuum_pump.models.vacuum_pump_config`, `src.engine.hardware.vacuum_pump.vacuum_pump_controller`.

Package-level import/export surface:

```python
from src.engine.hardware.vacuum_pump.interfaces.i_vacuum_pump_controller import IVacuumPumpController
from src.engine.hardware.vacuum_pump.interfaces.i_vacuum_pump_transport import IVacuumPumpTransport
from src.engine.hardware.vacuum_pump.models.vacuum_pump_config import VacuumPumpConfig
from src.engine.hardware.vacuum_pump.vacuum_pump_controller import VacuumPumpController
```

Module declarations (expressions are shown without evaluating them):

```python
__all__ = ['IVacuumPumpController', 'IVacuumPumpTransport', 'VacuumPumpConfig', 'VacuumPumpController']
```

## `mock_runner.py`

Source: [src/engine/hardware/vacuum_pump/mock_runner.py](../../../../src/engine/hardware/vacuum_pump/mock_runner.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `logging`, `src.engine.hardware.vacuum_pump.interfaces.i_vacuum_pump_transport`, `src.engine.hardware.vacuum_pump.models.vacuum_pump_config`, `src.engine.hardware.vacuum_pump.vacuum_pump_controller`.

### `MockVacuumPumpTransport`

```python
class MockVacuumPumpTransport(IVacuumPumpTransport):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self) -> None
```

```python
def read_register(self, address: int) -> int
```

```python
def write_register(self, address: int, value: int) -> None
```

### `scenario_turn_on_off`

```python
def scenario_turn_on_off()
```

### `scenario_blow_off_pulse`

```python
def scenario_blow_off_pulse()
```

### `scenario_transport_failure`

```python
def scenario_transport_failure()
```

## `vacuum_pump_controller.py`

Source: [src/engine/hardware/vacuum_pump/vacuum_pump_controller.py](../../../../src/engine/hardware/vacuum_pump/vacuum_pump_controller.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `logging`, `src.engine.core.i_health_checkable`, `src.engine.hardware.vacuum_pump.interfaces.i_vacuum_pump_controller`, `src.engine.hardware.vacuum_pump.interfaces.i_vacuum_pump_transport`, `src.engine.hardware.vacuum_pump.models.vacuum_pump_config`, `src.engine.hardware.xinje`, `threading`, `time`.

### `VacuumPumpController`

```python
class VacuumPumpController(IVacuumPumpController, IHealthCheckable):
```

High-level vacuum-pump controller. Implements turn-on/turn-off commands with optional blow-off pulse. Writes to a single coil/register via the injected transport.

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, transport: IVacuumPumpTransport, config: VacuumPumpConfig | None=None) -> None
```

Initialize controller. Args: transport: Hardware transport for register writes. config: Pump configuration (register addresses, values, blow-off). Defaults to VacuumPumpConfig() if not provided.

```python
def turn_on(self) -> bool
```

Turn the vacuum pump ON. Closes the blow-off register first if configured, then writes the configured on_value to the pump register. Returns: True if the write succeeded, False otherwise.

```python
def turn_off(self) -> bool
```

Turn the vacuum pump OFF and optionally pulse the blow-off. Writes the configured off_value to the pump register, then pulses the blow-off register if configured. Returns: True if both the OFF write and blow-off pulse (if any) succeeded. False if the OFF write failed or the blow-off pulse failed.

```python
def turn_off_nonblocking(self) -> bool
```

Turn off vacuum and finish the blow-off pulse in the background.

```python
def close(self) -> None
```

Release the underlying Modbus transport if it owns a session.

```python
def read_state(self) -> bool
```

Return whether the pump output register currently contains ON.

```python
def is_healthy(self) -> bool
```
