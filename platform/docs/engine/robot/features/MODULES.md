# Module reference: `src/engine/robot/features`

[Package guide](README.md) · [Complete source index](../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [navigation_service.py](#navigation_servicepy)
- [tool_service.py](#tool_servicepy)

## `__init__.py`

Source: [src/engine/robot/features/__init__.py](../../../../src/engine/robot/features/__init__.py).

Imports (including optional/function-local imports; not a startup dependency list): `.navigation_service`, `.tool_service`.

Package-level import/export surface:

```python
from .navigation_service import NavigationService
from .tool_service import RobotToolService
```

Module declarations (expressions are shown without evaluating them):

```python
__all__ = ['NavigationService', 'RobotToolService']
```

## `navigation_service.py`

Source: [src/engine/robot/features/navigation_service.py](../../../../src/engine/robot/features/navigation_service.py).

Imports (including optional/function-local imports; not a startup dependency list): `..interfaces.i_motion_service`, `enum`, `logging`, `traceback`, `typing`.

### `NavigationService`

```python
class NavigationService:
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, motion: IMotionService, robot_config_key, movement_groups_key, settings_service=None)
```

```python
def move_to_group(self, group_name: str, wait_cancelled: Callable[[], bool] | None=None, velocity: float | None=None, acceleration: float | None=None, motion_type: str | None=None, blendR: float | None=None, tool: int | None=None, user: int | None=None) -> bool
```

```python
def move_linear_group(self, group_name: str) -> bool
```

```python
def get_group_names(self) -> list[str]
```

```python
def move_to_position(self, position: list, group_name: str, wait_cancelled: Callable[[], bool] | None=None, velocity: float | None=None, acceleration: float | None=None, motion_type: str | None=None, blendR: float | None=None, tool: int | None=None, user: int | None=None) -> bool
```

Move to an explicit position using the velocity/acceleration of the named group.

## `tool_service.py`

Source: [src/engine/robot/features/tool_service.py](../../../../src/engine/robot/features/tool_service.py).

Imports (including optional/function-local imports; not a startup dependency list): `..interfaces.i_motion_service`, `..interfaces.i_tool_service`, `..interfaces.tool_definition`, `..tool_manager`, `typing`.

### `RobotToolService`

```python
class RobotToolService(IToolService):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, motion_service: IMotionService, robot_config, movement_groups, tool_changer)
```

```python
@property
def current_gripper(self) -> Optional[int]
```

```python
@property
def current_tool(self) -> Optional[int]
```

```python
def pickup_gripper(self, gripper_id: int) -> Tuple[bool, Optional[str]]
```

```python
def drop_off_gripper(self, gripper_id: int) -> Tuple[bool, Optional[str]]
```

```python
def pickup_tool(self, tool_id: int) -> Tuple[bool, Optional[str]]
```

```python
def drop_off_tool(self, tool_id: int) -> Tuple[bool, Optional[str]]
```

```python
def get_tools(self) -> List[ToolDefinition]
```
