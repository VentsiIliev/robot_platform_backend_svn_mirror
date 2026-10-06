# Module reference: `src/robot_systems/ROBOT_SYSTEM_BLUEPRINT/calibration`

[Package guide](README.md) · [Complete source index](../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [provider.py](#providerpy)

## `__init__.py`

Source: [src/robot_systems/ROBOT_SYSTEM_BLUEPRINT/calibration/__init__.py](../../../../src/robot_systems/ROBOT_SYSTEM_BLUEPRINT/calibration/__init__.py).

Imports (including optional/function-local imports; not a startup dependency list): `src.robot_systems.ROBOT_SYSTEM_BLUEPRINT.calibration.provider`.

Package-level import/export surface:

```python
from src.robot_systems.ROBOT_SYSTEM_BLUEPRINT.calibration.provider import MyRobotSystemCalibrationProvider
```

Module declarations (expressions are shown without evaluating them):

```python
__all__ = ['MyRobotSystemCalibrationProvider']
```

## `provider.py`

Source: [src/robot_systems/ROBOT_SYSTEM_BLUEPRINT/calibration/provider.py](../../../../src/robot_systems/ROBOT_SYSTEM_BLUEPRINT/calibration/provider.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `src.engine.common_service_ids`, `src.engine.robot.calibration`.

### `MyRobotSystemCalibrationProvider`

```python
class MyRobotSystemCalibrationProvider(RobotSystemCalibrationProvider):
```

Build the calibration-navigation adapter for this robot system.

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, robot_system) -> None
```

```python
def build_calibration_navigation(self, calibration_target_area_id_getter=None)
```
