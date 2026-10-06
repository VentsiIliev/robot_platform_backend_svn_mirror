# Module reference: `src/robot_systems/glue/height_measuring`

[Package guide](README.md) · [Complete source index](../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [provider.py](#providerpy)

## `provider.py`

Source: [src/robot_systems/glue/height_measuring/provider.py](../../../../src/robot_systems/glue/height_measuring/provider.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `src.engine.common_settings_ids`, `src.engine.hardware.communication`, `src.engine.hardware.communication.modbus.modbus_register_transport`, `src.engine.robot.height_measuring.robot_system_height_measuring_provider`, `src.robot_systems.glue.tools.glue_laser_control`.

### `GlueRobotSystemHeightMeasuringProvider`

```python
class GlueRobotSystemHeightMeasuringProvider(RobotSystemHeightMeasuringProvider):
```

Glue adapter that supplies the laser-control implementation.

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, robot_system) -> None
```

```python
def build_laser_control(self)
```
