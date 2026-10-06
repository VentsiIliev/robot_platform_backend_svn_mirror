# Module reference: `src/applications/robot_settings/service`

[Package guide](README.md) · [Complete source index](../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [i_robot_settings_navigation.py](#i_robot_settings_navigationpy)
- [i_robot_settings_service.py](#i_robot_settings_servicepy)
- [robot_settings_application_service.py](#robot_settings_application_servicepy)

## `__init__.py`

Source: [src/applications/robot_settings/service/__init__.py](../../../../src/applications/robot_settings/service/__init__.py).

No top-level functions, classes or public value declarations; inspect the source for imports or entry-point statements.

## `i_robot_settings_navigation.py`

Source: [src/applications/robot_settings/service/i_robot_settings_navigation.py](../../../../src/applications/robot_settings/service/i_robot_settings_navigation.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `typing`.

### `IRobotSettingsNavigation`

```python
class IRobotSettingsNavigation(Protocol):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def move_to_group(self, group_name: str, wait_cancelled: Callable[[], bool] | None=None) -> bool
```

```python
def move_linear_group(self, group_name: str) -> bool
```

```python
def move_to_position(self, position: list, group_name: str, wait_cancelled: Callable[[], bool] | None=None) -> bool
```

## `i_robot_settings_service.py`

Source: [src/applications/robot_settings/service/i_robot_settings_service.py](../../../../src/applications/robot_settings/service/i_robot_settings_service.py).

Imports (including optional/function-local imports; not a startup dependency list): `abc`, `src.engine.robot.configuration`, `src.shared_contracts.declarations`, `typing`.

### `IRobotSettingsService`

```python
class IRobotSettingsService(ABC):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
@abstractmethod
def load_config(self) -> RobotSettings
```

```python
@abstractmethod
def save_config(self, config: RobotSettings) -> None
```

```python
@abstractmethod
def load_calibration(self) -> RobotCalibrationSettings
```

```python
@abstractmethod
def save_calibration(self, calibration: RobotCalibrationSettings) -> None
```

```python
@abstractmethod
def load_targeting_definitions(self) -> Any
```

```python
@abstractmethod
def save_targeting_definitions(self, targeting: Any) -> None
```

```python
@abstractmethod
def load_movement_groups(self) -> MovementGroupSettings
```

```python
@abstractmethod
def save_movement_groups(self, movement_groups: dict[str, MovementGroup]) -> None
```

```python
@abstractmethod
def get_current_position(self) -> Optional[List[float]]
```

```python
@abstractmethod
def get_slot_info(self) -> List[Tuple[int, Optional[str]]]
```

Returns (slot_id, tool_name) per slot. tool_name is None if the slot is unassigned.

```python
@abstractmethod
def get_movement_group_definitions(self) -> List[MovementGroupDefinition]
```

```python
@abstractmethod
def move_to_group(self, group_name: str) -> tuple[bool, str]
```

Move robot to the named single-position group (PTP). Blocking.

```python
@abstractmethod
def execute_group(self, group_name: str) -> tuple[bool, str]
```

Execute the trajectory of the named multi-position group (linear). Blocking.

```python
@abstractmethod
def move_to_point(self, group_name: str, point_str: str) -> tuple[bool, str]
```

Move to an explicit point string using the group's vel/acc. Blocking.

```python
@abstractmethod
def jog(self, axis: str, direction: str, step: float) -> None
```

```python
@abstractmethod
def stop_jog(self) -> None
```

## `robot_settings_application_service.py`

Source: [src/applications/robot_settings/service/robot_settings_application_service.py](../../../../src/applications/robot_settings/service/robot_settings_application_service.py).

Imports (including optional/function-local imports; not a startup dependency list): `enum`, `src.applications.robot_settings.service.i_robot_settings_navigation`, `src.applications.robot_settings.service.i_robot_settings_service`, `src.engine.repositories.interfaces.i_settings_service`, `src.engine.robot.configuration`, `src.engine.robot.enums.axis`, `src.engine.robot.interfaces.i_robot_service`, `src.shared_contracts.declarations`, `typing`.

### `RobotSettingsApplicationService`

```python
class RobotSettingsApplicationService(IRobotSettingsService):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, settings_service: ISettingsService, config_key: Enum, movement_groups_key: Enum, calibration_key: Enum, robot_service: Optional[IRobotService]=None, tool_settings_key: Optional[Enum]=None, navigation_service: Optional[IRobotSettingsNavigation]=None, load_targeting_definitions_fn: Optional[Callable[[], object]]=None, save_targeting_definitions_fn: Optional[Callable[[object], None]]=None, movement_group_definitions: Optional[List[MovementGroupDefinition]]=None)
```

```python
def load_config(self) -> RobotSettings
```

```python
def save_config(self, config: RobotSettings) -> None
```

```python
def load_movement_groups(self) -> MovementGroupSettings
```

```python
def save_movement_groups(self, movement_groups: dict[str, MovementGroup]) -> None
```

```python
def load_calibration(self) -> RobotCalibrationSettings
```

```python
def save_calibration(self, calibration: RobotCalibrationSettings) -> None
```

```python
def load_targeting_definitions(self)
```

```python
def save_targeting_definitions(self, targeting) -> None
```

```python
def get_current_position(self) -> Optional[List[float]]
```

```python
def get_slot_info(self) -> List[Tuple[int, Optional[str]]]
```

Returns (slot_id, tool_name) per slot. tool_name is None if slot is unassigned.

```python
def get_movement_group_definitions(self) -> List[MovementGroupDefinition]
```

```python
def move_to_group(self, group_name: str) -> tuple[bool, str]
```

```python
def execute_group(self, group_name: str) -> tuple[bool, str]
```

```python
def move_to_point(self, group_name: str, point_str: str) -> tuple[bool, str]
```

```python
def jog(self, axis: str, direction: str, step: float) -> None
```

```python
def stop_jog(self) -> None
```
