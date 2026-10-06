# Module reference: `src/engine/hardware/vacuum_sensor/models`

[Package guide](README.md) · [Complete source index](../../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [vacuum_sensor_config.py](#vacuum_sensor_configpy)

## `__init__.py`

Source: [src/engine/hardware/vacuum_sensor/models/__init__.py](../../../../../src/engine/hardware/vacuum_sensor/models/__init__.py).

Imports (including optional/function-local imports; not a startup dependency list): `src.engine.hardware.vacuum_sensor.models.vacuum_sensor_config`.

Package-level import/export surface:

```python
from src.engine.hardware.vacuum_sensor.models.vacuum_sensor_config import VacuumSensorConfig
```

Module declarations (expressions are shown without evaluating them):

```python
__all__ = ['VacuumSensorConfig']
```

## `vacuum_sensor_config.py`

Source: [src/engine/hardware/vacuum_sensor/models/vacuum_sensor_config.py](../../../../../src/engine/hardware/vacuum_sensor/models/vacuum_sensor_config.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `dataclasses`.

### `VacuumSensorConfig`

```python
@dataclass(frozen=True)
class VacuumSensorConfig:
```

Register map and interpretation rules for a vacuum sensor. sensor_register — Modbus address or Xinje MA output label the sensor output sits on. detected_value — raw register value that means "vacuum present". Active-high sensor: 1. Active-low sensor: 0. read_retries — how many read attempts before reporting failure.

Declared fields/defaults:

```python
sensor_register: int | str
detected_value: int = 1
read_retries: int = 3
```
