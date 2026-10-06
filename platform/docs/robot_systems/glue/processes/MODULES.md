# Module reference: `src/robot_systems/glue/processes`

[Package guide](README.md) · [Complete source index](../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [clean_process.py](#clean_processpy)
- [glue_operation_coordinator.py](#glue_operation_coordinatorpy)
- [glue_operation_mode.py](#glue_operation_modepy)
- [glue_process.py](#glue_processpy)
- [pick_and_place_process.py](#pick_and_place_processpy)
- [robot_calibration_process.py](#robot_calibration_processpy)

## `__init__.py`

Source: [src/robot_systems/glue/processes/__init__.py](../../../../src/robot_systems/glue/processes/__init__.py).

No top-level functions, classes or public value declarations; inspect the source for imports or entry-point statements.

## `clean_process.py`

Source: [src/robot_systems/glue/processes/clean_process.py](../../../../src/robot_systems/glue/processes/clean_process.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `src.engine.core.i_messaging_service`, `src.engine.process.base_process`, `src.engine.process.process_requirements`, `src.engine.robot.interfaces.i_robot_service`, `src.engine.system.i_system_manager`, `src.robot_systems.glue.component_ids`, `threading`, `typing`.

### `CleanProcess`

```python
class CleanProcess(BaseProcess):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, robot_service: IRobotService, messaging: IMessagingService, system_manager: Optional[ISystemManager]=None, requirements: Optional[ProcessRequirements]=None, service_checker: Optional[Callable[[str], bool]]=None, simulation_duration_s: float=_SIMULATION_DURATION_S)
```

## `glue_operation_coordinator.py`

Source: [src/robot_systems/glue/processes/glue_operation_coordinator.py](../../../../src/robot_systems/glue/processes/glue_operation_coordinator.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `logging`, `src.engine.core.i_messaging_service`, `src.engine.process.i_process`, `src.engine.process.process_sequence`, `src.engine.repositories.interfaces.i_settings_service`, `src.robot_systems.glue.component_ids`, `src.robot_systems.glue.processes.clean_process`, `src.robot_systems.glue.processes.glue_operation_mode`, `src.robot_systems.glue.processes.glue_process`, `src.robot_systems.glue.processes.pick_and_place_process`, `src.robot_systems.glue.processes.robot_calibration_process`, `src.shared_contracts.events.process_events`, `threading`, `typing`.

### `GlueOperationCoordinator`

```python
class GlueOperationCoordinator:
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, glue_process: GlueProcess, pick_and_place_process: PickAndPlaceProcess, clean_process: CleanProcess, calibration_process: RobotCalibrationProcess, messaging: IMessagingService, execution_service=None, settings_service: ISettingsService | None=None) -> None
```

```python
@property
def pick_and_place_process(self) -> PickAndPlaceProcess
```

```python
@property
def glue_process(self) -> GlueProcess
```

```python
def start(self) -> None
```

```python
def stop(self) -> None
```

```python
def pause(self) -> None
```

```python
def resume(self) -> None
```

```python
def reset_errors(self) -> None
```

```python
def get_active_state(self) -> str
```

Return the state of the currently active process, or IDLE if none.

```python
def set_mode(self, mode: GlueOperationMode) -> None
```

```python
def get_mode(self) -> GlueOperationMode
```

```python
def clean(self) -> None
```

```python
def calibrate(self) -> None
```

```python
def stop_calibration(self) -> None
```

## `glue_operation_mode.py`

Source: [src/robot_systems/glue/processes/glue_operation_mode.py](../../../../src/robot_systems/glue/processes/glue_operation_mode.py).

Imports (including optional/function-local imports; not a startup dependency list): `enum`.

### `GlueOperationMode`

```python
class GlueOperationMode(Enum):
```

Declared fields/defaults:

```python
SPRAY_ONLY = 'spray_only'
PICK_AND_SPRAY = 'pick_and_spray'
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
@staticmethod
def from_label(label: str) -> 'GlueOperationMode'
```

## `glue_process.py`

Source: [src/robot_systems/glue/processes/glue_process.py](../../../../src/robot_systems/glue/processes/glue_process.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `src.engine.core.i_messaging_service`, `src.engine.hardware.generator.interfaces.i_generator_controller`, `src.engine.hardware.motor.interfaces.i_motor_service`, `src.engine.process.base_process`, `src.engine.process.executable_state_machine`, `src.engine.process.process_requirements`, `src.engine.robot.interfaces.i_robot_service`, `src.engine.system`, `src.robot_systems.glue.component_ids`, `src.robot_systems.glue.domain.dispense_channels.i_dispense_channel_service`, `src.robot_systems.glue.navigation`, `src.robot_systems.glue.processes.glue_dispensing.dispensing_config`, `src.robot_systems.glue.processes.glue_dispensing.dispensing_context`, `src.robot_systems.glue.processes.glue_dispensing.dispensing_machine_factory`, `src.robot_systems.glue.processes.glue_dispensing.dispensing_path`, `src.robot_systems.glue.processes.glue_dispensing.i_glue_type_resolver`, `src.shared_contracts.events.glue_process_events`, `src.shared_contracts.events.process_events`, `threading`, `typing`.

### `GlueProcess`

```python
class GlueProcess(BaseProcess):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, robot_service: IRobotService, motor_service: IMotorService, dispense_channels: IDispenseChannelService, config: GlueDispensingConfig, navigation_service: GlueNavigationService, messaging: IMessagingService, generator: Optional[IGeneratorController]=None, system_manager: Optional[ISystemManager]=None, requirements: Optional[ProcessRequirements]=None, service_checker: Optional[Callable[[str], bool]]=None)
```

```python
def set_paths(self, paths: List[Tuple], spray_on: bool) -> None
```

```python
def set_manual_mode(self, enabled: bool) -> None
```

```python
def is_manual_mode_enabled(self) -> bool
```

```python
def step_once(self) -> dict
```

```python
def get_dispensing_snapshot(self) -> dict
```

## `pick_and_place_process.py`

Source: [src/robot_systems/glue/processes/pick_and_place_process.py](../../../../src/robot_systems/glue/processes/pick_and_place_process.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `src.engine.core.i_messaging_service`, `src.engine.hardware.vacuum_pump.interfaces.i_vacuum_pump_controller`, `src.engine.process.base_process`, `src.engine.process.process_requirements`, `src.engine.robot.height_measuring.i_height_measuring_service`, `src.engine.robot.interfaces.i_robot_service`, `src.engine.robot.interfaces.i_tool_service`, `src.engine.robot.plane_pose_mapper`, `src.engine.robot.targeting`, `src.engine.system.i_system_manager`, `src.robot_systems.glue.component_ids`, `src.robot_systems.glue.domain.matching.i_matching_service`, `src.robot_systems.glue.navigation`, `src.robot_systems.glue.processes.pick_and_place.config`, `src.robot_systems.glue.processes.pick_and_place.workflow`, `src.shared_contracts.events.pick_and_place_events`, `src.shared_contracts.events.process_events`, `threading`, `typing`.

### `PickAndPlaceProcess`

```python
class PickAndPlaceProcess(BaseProcess):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, robot_service: IRobotService, navigation_service: GlueNavigationService, messaging: IMessagingService, matching_service: Optional[IMatchingService]=None, tool_service: Optional[IToolService]=None, height_service: Optional[IHeightMeasuringService]=None, resolver: Optional[VisionTargetResolver]=None, resolver_getter: Optional[Callable[[], Optional[VisionTargetResolver]]]=None, vacuum_pump: Optional[IVacuumPumpController]=None, config: Optional[PickAndPlaceConfig]=None, system_manager: Optional[ISystemManager]=None, requirements: Optional[ProcessRequirements]=None, service_checker: Optional[Callable[[str], bool]]=None)
```

```python
def set_simulation(self, value: bool) -> None
```

```python
def set_step_mode(self, value: bool) -> None
```

```python
def is_step_mode_enabled(self) -> bool
```

```python
def step_once(self) -> None
```

## `robot_calibration_process.py`

Source: [src/robot_systems/glue/processes/robot_calibration_process.py](../../../../src/robot_systems/glue/processes/robot_calibration_process.py).

Imports (including optional/function-local imports; not a startup dependency list): `src.engine.core.i_messaging_service`, `src.engine.process.process_requirements`, `src.engine.robot.calibration.i_robot_calibration_service`, `src.engine.robot.calibration.robot_calibration_process`, `src.engine.system.i_system_manager`, `src.robot_systems.glue.component_ids`, `typing`.

### `RobotCalibrationProcess`

```python
class RobotCalibrationProcess(_Base):
```

Thin subclass that pins the process_id to glue's ProcessID.ROBOT_CALIBRATION.

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, calibration_service: IRobotCalibrationService, messaging: IMessagingService, system_manager: Optional[ISystemManager]=None, requirements: Optional[ProcessRequirements]=None, service_checker: Optional[Callable[[str], bool]]=None)
```
