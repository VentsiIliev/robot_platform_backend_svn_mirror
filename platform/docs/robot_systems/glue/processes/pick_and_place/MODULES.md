# Module reference: `src/robot_systems/glue/processes/pick_and_place`

[Package guide](README.md) · [Complete source index](../../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)

## `__init__.py`

Source: [src/robot_systems/glue/processes/pick_and_place/__init__.py](../../../../../src/robot_systems/glue/processes/pick_and_place/__init__.py).

Imports (including optional/function-local imports; not a startup dependency list): `.config`, `.context`, `.errors`, `.execution`, `.plane`, `.planning`, `.workflow`.

Package-level import/export surface:

```python
from .config import MotionProfile, PickAndPlaceConfig, PlaneConfig
from .context import PickAndPlaceContext
from .errors import PickAndPlaceErrorCode, PickAndPlaceErrorInfo, PickAndPlaceStage, PickAndPlaceWorkflowResult, WorkpieceProcessResult
from .execution import HeightResolutionResult, HeightResolutionService, MotionExecutionResult, PickAndPlaceMotionExecutor
from .plane import Plane, PlaneManagementService
from .planning import DropOffPositions, PickupCalculator, PickupPositions, PlacementCalculator, PlacementResult, PlacementStrategy, PlacementTarget, Position, SelectedWorkpiece, WorkpieceDimensions, WorkpiecePlacement, WorkpieceSelectionPolicy
from .workflow import PickAndPlaceWorkflow
```

Module declarations (expressions are shown without evaluating them):

```python
__all__ = ['DropOffPositions', 'HeightResolutionResult', 'HeightResolutionService', 'MotionExecutionResult', 'MotionProfile', 'PickAndPlaceConfig', 'PickAndPlaceContext', 'PickAndPlaceErrorCode', 'PickAndPlaceErrorInfo', 'PickAndPlaceMotionExecutor', 'PickAndPlaceStage', 'PickAndPlaceWorkflow', 'PickAndPlaceWorkflowResult', 'PickupCalculator', 'PickupPositions', 'PlacementCalculator', 'PlacementResult', 'PlacementStrategy', 'PlacementTarget', 'Plane', 'PlaneConfig', 'PlaneManagementService', 'Position', 'SelectedWorkpiece', 'WorkpieceDimensions', 'WorkpiecePlacement', 'WorkpieceProcessResult', 'WorkpieceSelectionPolicy']
```
