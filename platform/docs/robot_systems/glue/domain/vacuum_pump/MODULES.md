# Module reference: `src/robot_systems/glue/domain/vacuum_pump`

[Package guide](README.md) · [Complete source index](../../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [vacuum_pump_controller.py](#vacuum_pump_controllerpy)

## `__init__.py`

Source: [src/robot_systems/glue/domain/vacuum_pump/__init__.py](../../../../../src/robot_systems/glue/domain/vacuum_pump/__init__.py).

Imports (including optional/function-local imports; not a startup dependency list): `.vacuum_pump_controller`.

Package-level import/export surface:

```python
from .vacuum_pump_controller import VacuumPumpController
```

Module declarations (expressions are shown without evaluating them):

```python
__all__ = ['VacuumPumpController']
```

## `vacuum_pump_controller.py`

Source: [src/robot_systems/glue/domain/vacuum_pump/vacuum_pump_controller.py](../../../../../src/robot_systems/glue/domain/vacuum_pump/vacuum_pump_controller.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `logging`, `src.engine.core.i_health_checkable`, `src.engine.hardware.vacuum_pump.interfaces.i_vacuum_pump_controller`, `src.engine.robot.interfaces.i_robot_service`, `time`.

### `VacuumPumpController`

```python
class VacuumPumpController(IVacuumPumpController, IHealthCheckable):
```

Declared fields/defaults:

```python
ON_VALUE = True
OFF_VALUE = False
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, robot_service: IRobotService, digital_output: int=1, reset_output: int=2, reset_pulse_s: float=0.3) -> None
```

```python
def turn_on(self) -> bool
```

```python
def turn_off(self) -> bool
```

```python
def is_healthy(self) -> bool
```
