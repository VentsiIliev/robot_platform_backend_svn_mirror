# Module reference: `src/engine/hardware/vacuum_pump/models`

[Package guide](README.md) · [Complete source index](../../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [vacuum_pump_config.py](#vacuum_pump_configpy)

## `__init__.py`

Source: [src/engine/hardware/vacuum_pump/models/__init__.py](../../../../../src/engine/hardware/vacuum_pump/models/__init__.py).

Imports (including optional/function-local imports; not a startup dependency list): `src.engine.hardware.vacuum_pump.models.vacuum_pump_config`.

Package-level import/export surface:

```python
from src.engine.hardware.vacuum_pump.models.vacuum_pump_config import VacuumPumpConfig
```

Module declarations (expressions are shown without evaluating them):

```python
__all__ = ['VacuumPumpConfig']
```

## `vacuum_pump_config.py`

Source: [src/engine/hardware/vacuum_pump/models/vacuum_pump_config.py](../../../../../src/engine/hardware/vacuum_pump/models/vacuum_pump_config.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `dataclasses`.

### `VacuumPumpConfig`

```python
@dataclass(frozen=True)
class VacuumPumpConfig:
```

Declared fields/defaults:

```python
pump_register: int | str = 'Y0'
on_value: int = 1
off_value: int = 0
blow_off_register: int | str | None = None
blow_off_on_value: int = 1
blow_off_off_value: int = 0
blow_off_pulse_seconds: float = 0.0
```
