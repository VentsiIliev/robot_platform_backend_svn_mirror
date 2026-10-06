# Module reference: `src/robot_systems/glue/processes/pick_and_place/workflow`

[Package guide](README.md) · [Complete source index](../../../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [pick_and_place_workflow.py](#pick_and_place_workflowpy)

## `__init__.py`

Source: [src/robot_systems/glue/processes/pick_and_place/workflow/__init__.py](../../../../../../src/robot_systems/glue/processes/pick_and_place/workflow/__init__.py).

Imports (including optional/function-local imports; not a startup dependency list): `.pick_and_place_workflow`.

Package-level import/export surface:

```python
from .pick_and_place_workflow import PickAndPlaceWorkflow
```

Module declarations (expressions are shown without evaluating them):

```python
__all__ = ['PickAndPlaceWorkflow']
```

## `pick_and_place_workflow.py`

Source: [src/robot_systems/glue/processes/pick_and_place/workflow/pick_and_place_workflow.py](../../../../../../src/robot_systems/glue/processes/pick_and_place/workflow/pick_and_place_workflow.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `logging`, `src.engine.hardware.vacuum_pump.interfaces.i_vacuum_pump_controller`, `src.engine.robot.height_measuring.i_height_measuring_service`, `src.engine.robot.interfaces.i_robot_service`, `src.engine.robot.interfaces.i_tool_service`, `src.engine.robot.plane_pose_mapper`, `src.engine.robot.targeting`, `src.robot_systems.glue.domain.matching.i_matching_service`, `src.robot_systems.glue.navigation`, `src.robot_systems.glue.processes.pick_and_place.config`, `src.robot_systems.glue.processes.pick_and_place.context`, `src.robot_systems.glue.processes.pick_and_place.errors`, `src.robot_systems.glue.processes.pick_and_place.execution`, `src.robot_systems.glue.processes.pick_and_place.plane`, `src.robot_systems.glue.processes.pick_and_place.planning`, `src.robot_systems.glue.processes.pick_and_place.workflow.handlers`, `threading`, `typing`.

### `PickAndPlaceWorkflow`

```python
class PickAndPlaceWorkflow:
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, robot: IRobotService, navigation: GlueNavigationService, matching: IMatchingService, tools: IToolService, height: IHeightMeasuringService, resolver: VisionTargetResolver, vacuum_pump: IVacuumPumpController, config: PickAndPlaceConfig, logger: logging.Logger, on_workpiece_placed: Optional[Callable]=None, on_match_result: Optional[Callable]=None, on_diagnostics: Optional[Callable[[dict], None]]=None, step_gate: Optional[Callable[[str, dict], bool]]=None, calibration_to_target_pose_mapper: Optional[PlanePoseMapper]=None, simulation: bool=False)
```

```python
def run(self, stop_event: threading.Event, run_allowed: threading.Event) -> PickAndPlaceWorkflowResult
```
