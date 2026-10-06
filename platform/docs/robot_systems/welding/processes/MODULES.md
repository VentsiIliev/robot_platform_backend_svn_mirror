# Module reference: `src/robot_systems/welding/processes`

[Package guide](README.md) · [Complete source index](../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [robot_calibration_process.py](#robot_calibration_processpy)
- [welding_process.py](#welding_processpy)

## `__init__.py`

Source: [src/robot_systems/welding/processes/__init__.py](../../../../src/robot_systems/welding/processes/__init__.py).

Imports (including optional/function-local imports; not a startup dependency list): `src.robot_systems.welding.processes.welding_process`.

Package-level import/export surface:

```python
from src.robot_systems.welding.processes.welding_process import WeldingProcess
```

Module declarations (expressions are shown without evaluating them):

```python
__all__ = ['WeldingProcess']
```

## `robot_calibration_process.py`

Source: [src/robot_systems/welding/processes/robot_calibration_process.py](../../../../src/robot_systems/welding/processes/robot_calibration_process.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `src.engine.core.i_messaging_service`, `src.engine.process.base_process`, `src.engine.process.process_requirements`, `src.engine.robot.calibration.i_robot_calibration_service`, `src.engine.system.i_system_manager`, `src.robot_systems.glue.component_ids`, `threading`, `typing`.

### `RobotCalibrationProcess`

```python
class RobotCalibrationProcess(BaseProcess):
```

Runs IRobotCalibrationService.run_calibration() in a background thread. Transitions to STOPPED on success, ERROR on failure. _on_stop() signals stop_calibration() but does NOT join — called while the lock is held.

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, calibration_service: IRobotCalibrationService, messaging: IMessagingService, system_manager: Optional[ISystemManager]=None, requirements: Optional[ProcessRequirements]=None, service_checker: Optional[Callable[[str], bool]]=None)
```

## `welding_process.py`

Source: [src/robot_systems/welding/processes/welding_process.py](../../../../src/robot_systems/welding/processes/welding_process.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `src.engine.core.i_messaging_service`, `src.engine.process.base_process`, `src.engine.process.process_requirements`, `src.engine.system.i_system_manager`, `src.robot_systems.welding.component_ids`, `threading`, `typing`.

### `WeldingProcess`

```python
class WeldingProcess(BaseProcess):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, messaging: IMessagingService, system_manager: Optional[ISystemManager]=None, requirements: Optional[ProcessRequirements]=None, service_checker: Optional[Callable[[str], bool]]=None, simulation_duration_s: float=_SIMULATION_DURATION_S) -> None
```
