# Module reference: `src/robot_systems/welding/calibration`

[Package guide](README.md) · [Complete source index](../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [coordinator.py](#coordinatorpy)
- [provider.py](#providerpy)

## `__init__.py`

Source: [src/robot_systems/welding/calibration/__init__.py](../../../../src/robot_systems/welding/calibration/__init__.py).

Imports (including optional/function-local imports; not a startup dependency list): `src.robot_systems.welding.calibration.provider`.

Package-level import/export surface:

```python
from src.robot_systems.welding.calibration.provider import WeldingRobotSystemCalibrationProvider
```

Module declarations (expressions are shown without evaluating them):

```python
__all__ = ['WeldingRobotSystemCalibrationProvider']
```

## `coordinator.py`

Source: [src/robot_systems/welding/calibration/coordinator.py](../../../../src/robot_systems/welding/calibration/coordinator.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `logging`, `src.engine.core.i_messaging_service`, `src.engine.process.i_process`, `src.engine.robot.calibration.robot_calibration_process`, `src.robot_systems.welding.component_ids`, `src.shared_contracts.events.process_events`, `threading`, `typing`.

### `WeldingCalibrationCoordinator`

```python
class WeldingCalibrationCoordinator:
```

Manages the robot calibration process for the welding system.

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, calibration_process: RobotCalibrationProcess, messaging: IMessagingService) -> None
```

```python
def calibrate(self) -> None
```

```python
def stop_calibration(self) -> None
```

## `provider.py`

Source: [src/robot_systems/welding/calibration/provider.py](../../../../src/robot_systems/welding/calibration/provider.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `src.engine.common_service_ids`, `src.engine.robot.calibration.calibration_navigation_service`, `src.engine.robot.calibration.robot_system_calibration_provider`.

### `WeldingRobotSystemCalibrationProvider`

```python
class WeldingRobotSystemCalibrationProvider(RobotSystemCalibrationProvider):
```

Welding adapter that supplies the welding-specific calibration move.

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, robot_system) -> None
```

```python
def build_calibration_navigation(self, calibration_target_area_id_getter=None)
```
