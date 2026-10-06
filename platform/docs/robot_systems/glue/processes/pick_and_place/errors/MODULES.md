# Module reference: `src/robot_systems/glue/processes/pick_and_place/errors`

[Package guide](README.md) · [Complete source index](../../../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [pick_and_place_error.py](#pick_and_place_errorpy)

## `__init__.py`

Source: [src/robot_systems/glue/processes/pick_and_place/errors/__init__.py](../../../../../../src/robot_systems/glue/processes/pick_and_place/errors/__init__.py).

Imports (including optional/function-local imports; not a startup dependency list): `.pick_and_place_error`.

Package-level import/export surface:

```python
from .pick_and_place_error import PickAndPlaceErrorCode, PickAndPlaceErrorInfo, PickAndPlaceStage, PickAndPlaceWorkflowResult, WorkpieceProcessResult
```

Module declarations (expressions are shown without evaluating them):

```python
__all__ = ['PickAndPlaceErrorCode', 'PickAndPlaceErrorInfo', 'PickAndPlaceStage', 'PickAndPlaceWorkflowResult', 'WorkpieceProcessResult']
```

## `pick_and_place_error.py`

Source: [src/robot_systems/glue/processes/pick_and_place/errors/pick_and_place_error.py](../../../../../../src/robot_systems/glue/processes/pick_and_place/errors/pick_and_place_error.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `dataclasses`, `enum`, `src.shared_contracts.events.process_events`, `typing`.

### `PickAndPlaceStage`

```python
class PickAndPlaceStage(str, Enum):
```

Declared fields/defaults:

```python
STARTUP = 'startup'
MATCHING = 'matching'
TRANSFORM = 'transform'
HEIGHT = 'height'
TOOLING = 'tooling'
PICK = 'pick'
PLACE = 'place'
PLANE = 'plane'
SHUTDOWN = 'shutdown'
CANCELLED = 'cancelled'
```

### `PickAndPlaceErrorCode`

```python
class PickAndPlaceErrorCode(str, Enum):
```

Declared fields/defaults:

```python
NOT_CONFIGURED = 'NOT_CONFIGURED'
MOVE_HOME_FAILED = 'MOVE_HOME_FAILED'
MATCHING_FAILED = 'MATCHING_FAILED'
TRANSFORM_FAILED = 'TRANSFORM_FAILED'
HEIGHT_MEASUREMENT_FAILED = 'HEIGHT_MEASUREMENT_FAILED'
TOOL_CHANGE_FAILED = 'TOOL_CHANGE_FAILED'
PICK_MOTION_FAILED = 'PICK_MOTION_FAILED'
PLACE_MOTION_FAILED = 'PLACE_MOTION_FAILED'
VACUUM_ON_FAILED = 'VACUUM_ON_FAILED'
VACUUM_OFF_FAILED = 'VACUUM_OFF_FAILED'
DROP_GRIPPER_FAILED = 'DROP_GRIPPER_FAILED'
PLANE_FULL = 'PLANE_FULL'
UNEXPECTED_ERROR = 'UNEXPECTED_ERROR'
CANCELLED = 'CANCELLED'
```

### `PickAndPlaceErrorInfo`

```python
@dataclass(frozen=True)
class PickAndPlaceErrorInfo:
```

Declared fields/defaults:

```python
code: PickAndPlaceErrorCode
stage: PickAndPlaceStage
message: str
detail: Optional[str] = None
recoverable: bool = False
```

### `PickAndPlaceWorkflowResult`

```python
@dataclass(frozen=True)
class PickAndPlaceWorkflowResult:
```

Declared fields/defaults:

```python
state: ProcessState
message: str = ''
error: Optional[PickAndPlaceErrorInfo] = None
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
@property
def success(self) -> bool
```

```python
@classmethod
def stopped(cls, message: str='') -> 'PickAndPlaceWorkflowResult'
```

```python
@classmethod
def error_result(cls, code: PickAndPlaceErrorCode, stage: PickAndPlaceStage, message: str, detail: Optional[str]=None, recoverable: bool=False) -> 'PickAndPlaceWorkflowResult'
```

### `WorkpieceProcessResult`

```python
@dataclass(frozen=True)
class WorkpieceProcessResult:
```

Declared fields/defaults:

```python
placed: bool
plane_full: bool = False
error: Optional[PickAndPlaceErrorInfo] = None
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
@classmethod
def success(cls) -> 'WorkpieceProcessResult'
```

```python
@classmethod
def skipped_plane_full(cls) -> 'WorkpieceProcessResult'
```

```python
@classmethod
def fail(cls, error: PickAndPlaceErrorInfo) -> 'WorkpieceProcessResult'
```
