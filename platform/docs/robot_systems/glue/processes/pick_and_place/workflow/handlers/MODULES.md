# Module reference: `src/robot_systems/glue/processes/pick_and_place/workflow/handlers`

[Package guide](README.md) · [Complete source index](../../../../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [completion_handler.py](#completion_handlerpy)
- [height_handler.py](#height_handlerpy)
- [matching_handler.py](#matching_handlerpy)
- [pick_handler.py](#pick_handlerpy)
- [place_handler.py](#place_handlerpy)
- [placement_handler.py](#placement_handlerpy)
- [planning_handler.py](#planning_handlerpy)
- [preparation_handler.py](#preparation_handlerpy)
- [shutdown_handler.py](#shutdown_handlerpy)
- [startup_handler.py](#startup_handlerpy)
- [tooling_handler.py](#tooling_handlerpy)
- [transform_handler.py](#transform_handlerpy)

## `__init__.py`

Source: [src/robot_systems/glue/processes/pick_and_place/workflow/handlers/__init__.py](../../../../../../../src/robot_systems/glue/processes/pick_and_place/workflow/handlers/__init__.py).

Imports (including optional/function-local imports; not a startup dependency list): `.completion_handler`, `.height_handler`, `.matching_handler`, `.pick_handler`, `.place_handler`, `.placement_handler`, `.planning_handler`, `.preparation_handler`, `.shutdown_handler`, `.startup_handler`, `.tooling_handler`, `.transform_handler`.

Package-level import/export surface:

```python
from .completion_handler import finalize_placement
from .height_handler import resolve_workpiece_height
from .matching_handler import run_matching_cycle
from .pick_handler import execute_pick_contact_stage, execute_pick_descent_stage, execute_pick_lift_stage
from .place_handler import execute_place_approach_stage, execute_place_drop_stage
from .placement_handler import plan_and_execute_placement
from .planning_handler import plan_placement
from .preparation_handler import PreparedWorkpiece, prepare_workpiece
from .shutdown_handler import shutdown_workflow
from .startup_handler import run_startup
from .tooling_handler import ensure_gripper_ready
from .transform_handler import transform_pickup_point
```

Module declarations (expressions are shown without evaluating them):

```python
__all__ = ['PreparedWorkpiece', 'ensure_gripper_ready', 'execute_pick_contact_stage', 'execute_pick_descent_stage', 'execute_pick_lift_stage', 'execute_place_approach_stage', 'execute_place_drop_stage', 'finalize_placement', 'plan_and_execute_placement', 'plan_placement', 'prepare_workpiece', 'resolve_workpiece_height', 'run_matching_cycle', 'run_startup', 'shutdown_workflow', 'transform_pickup_point']
```

## `completion_handler.py`

Source: [src/robot_systems/glue/processes/pick_and_place/workflow/handlers/completion_handler.py](../../../../../../../src/robot_systems/glue/processes/pick_and_place/workflow/handlers/completion_handler.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `src.robot_systems.glue.processes.pick_and_place.errors`.

### `finalize_placement`

```python
def finalize_placement(workflow, workpiece, prepared, placement)
```

## `height_handler.py`

Source: [src/robot_systems/glue/processes/pick_and_place/workflow/handlers/height_handler.py](../../../../../../../src/robot_systems/glue/processes/pick_and_place/workflow/handlers/height_handler.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `src.robot_systems.glue.processes.pick_and_place.errors`.

### `resolve_workpiece_height`

```python
def resolve_workpiece_height(workflow, fallback_height_mm: float, robot_x: float, robot_y: float)
```

## `matching_handler.py`

Source: [src/robot_systems/glue/processes/pick_and_place/workflow/handlers/matching_handler.py](../../../../../../../src/robot_systems/glue/processes/pick_and_place/workflow/handlers/matching_handler.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `src.robot_systems.glue.processes.pick_and_place.errors`.

### `run_matching_cycle`

```python
def run_matching_cycle(workflow)
```

## `pick_handler.py`

Source: [src/robot_systems/glue/processes/pick_and_place/workflow/handlers/pick_handler.py](../../../../../../../src/robot_systems/glue/processes/pick_and_place/workflow/handlers/pick_handler.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `src.robot_systems.glue.processes.pick_and_place.errors`.

### `_cancelled_result`

```python
def _cancelled_result(workflow)
```

### `_execute_pick_move`

```python
def _execute_pick_move(workflow, checkpoint: str, message: str, move_fn, pickup_positions)
```

### `execute_pick_descent_stage`

```python
def execute_pick_descent_stage(workflow, pickup_positions)
```

### `execute_pick_contact_stage`

```python
def execute_pick_contact_stage(workflow, pickup_positions)
```

### `execute_pick_lift_stage`

```python
def execute_pick_lift_stage(workflow, pickup_positions)
```

## `place_handler.py`

Source: [src/robot_systems/glue/processes/pick_and_place/workflow/handlers/place_handler.py](../../../../../../../src/robot_systems/glue/processes/pick_and_place/workflow/handlers/place_handler.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `src.robot_systems.glue.processes.pick_and_place.errors`.

### `_cancelled_result`

```python
def _cancelled_result(workflow)
```

### `_execute_place_move`

```python
def _execute_place_move(workflow, checkpoint: str, message: str, move_fn, drop_off_positions)
```

### `execute_place_approach_stage`

```python
def execute_place_approach_stage(workflow, drop_off_positions)
```

### `execute_place_drop_stage`

```python
def execute_place_drop_stage(workflow, drop_off_positions)
```

## `placement_handler.py`

Source: [src/robot_systems/glue/processes/pick_and_place/workflow/handlers/placement_handler.py](../../../../../../../src/robot_systems/glue/processes/pick_and_place/workflow/handlers/placement_handler.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `src.robot_systems.glue.processes.pick_and_place.errors`, `src.robot_systems.glue.processes.pick_and_place.workflow.handlers.completion_handler`, `src.robot_systems.glue.processes.pick_and_place.workflow.handlers.pick_handler`, `src.robot_systems.glue.processes.pick_and_place.workflow.handlers.place_handler`, `src.robot_systems.glue.processes.pick_and_place.workflow.handlers.planning_handler`.

### `plan_and_execute_placement`

```python
def plan_and_execute_placement(workflow, workpiece, prepared)
```

## `planning_handler.py`

Source: [src/robot_systems/glue/processes/pick_and_place/workflow/handlers/planning_handler.py](../../../../../../../src/robot_systems/glue/processes/pick_and_place/workflow/handlers/planning_handler.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `src.robot_systems.glue.processes.pick_and_place.errors`.

### `plan_placement`

```python
def plan_placement(workflow, prepared)
```

## `preparation_handler.py`

Source: [src/robot_systems/glue/processes/pick_and_place/workflow/handlers/preparation_handler.py](../../../../../../../src/robot_systems/glue/processes/pick_and_place/workflow/handlers/preparation_handler.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `dataclasses`, `src.engine.vision.implementation.VisionSystem.core.models.contour`, `src.robot_systems.glue.processes.pick_and_place.errors`, `src.robot_systems.glue.processes.pick_and_place.workflow.handlers.height_handler`, `src.robot_systems.glue.processes.pick_and_place.workflow.handlers.tooling_handler`, `src.robot_systems.glue.processes.pick_and_place.workflow.handlers.transform_handler`.

### `_parse_pickup_point`

```python
def _parse_pickup_point(pickup_point)
```

### `PreparedWorkpiece`

```python
@dataclass(frozen=True)
class PreparedWorkpiece:
```

Declared fields/defaults:

```python
contour: Contour
gripper_id: int
robot_x: float
robot_y: float
workpiece_height: float
pickup_positions: object
```

### `prepare_workpiece`

```python
def prepare_workpiece(workflow, workpiece, orientation: float)
```

## `shutdown_handler.py`

Source: [src/robot_systems/glue/processes/pick_and_place/workflow/handlers/shutdown_handler.py](../../../../../../../src/robot_systems/glue/processes/pick_and_place/workflow/handlers/shutdown_handler.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`.

### `shutdown_workflow`

```python
def shutdown_workflow(workflow) -> None
```

## `startup_handler.py`

Source: [src/robot_systems/glue/processes/pick_and_place/workflow/handlers/startup_handler.py](../../../../../../../src/robot_systems/glue/processes/pick_and_place/workflow/handlers/startup_handler.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `src.robot_systems.glue.processes.pick_and_place.errors`.

### `run_startup`

```python
def run_startup(workflow) -> PickAndPlaceWorkflowResult | None
```

## `tooling_handler.py`

Source: [src/robot_systems/glue/processes/pick_and_place/workflow/handlers/tooling_handler.py](../../../../../../../src/robot_systems/glue/processes/pick_and_place/workflow/handlers/tooling_handler.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `src.robot_systems.glue.processes.pick_and_place.errors`.

### `ensure_gripper_ready`

```python
def ensure_gripper_ready(workflow, gripper_id: int)
```

## `transform_handler.py`

Source: [src/robot_systems/glue/processes/pick_and_place/workflow/handlers/transform_handler.py](../../../../../../../src/robot_systems/glue/processes/pick_and_place/workflow/handlers/transform_handler.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `src.engine.robot.plane_pose_mapper`, `src.engine.robot.targeting`, `src.robot_systems.glue.processes.pick_and_place.errors`.

### `transform_pickup_point`

```python
def transform_pickup_point(workflow, pickup_px)
```

### `resolve_target_point`

```python
def resolve_target_point(workflow, pickup_px, rz_final, active_mapper)
```

### `_pickup_target_point`

```python
def _pickup_target_point(workflow)
```
