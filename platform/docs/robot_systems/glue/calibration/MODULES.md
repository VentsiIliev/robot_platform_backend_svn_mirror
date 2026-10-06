# Module reference: `src/robot_systems/glue/calibration`

[Package guide](README.md) · [Complete source index](../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [provider.py](#providerpy)

## `provider.py`

Source: [src/robot_systems/glue/calibration/provider.py](../../../../src/robot_systems/glue/calibration/provider.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `src.engine.common_service_ids`, `src.engine.robot.calibration.calibration_navigation_service`, `src.engine.robot.calibration.robot_system_calibration_provider`.

### `GlueRobotSystemCalibrationProvider`

```python
class GlueRobotSystemCalibrationProvider(RobotSystemCalibrationProvider):
```

Glue adapter that supplies the glue-specific calibration move.

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, robot_system) -> None
```

```python
def build_calibration_navigation(self, calibration_target_area_id_getter=None)
```
