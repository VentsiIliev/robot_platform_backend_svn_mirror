# Module reference: `src/applications/robot_settings/model`

[Package guide](README.md) · [Complete source index](../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [mapper.py](#mapperpy)
- [robot_settings_model.py](#robot_settings_modelpy)

## `__init__.py`

Source: [src/applications/robot_settings/model/__init__.py](../../../../src/applications/robot_settings/model/__init__.py).

No top-level functions, classes or public value declarations; inspect the source for imports or entry-point statements.

## `mapper.py`

Source: [src/applications/robot_settings/model/mapper.py](../../../../src/applications/robot_settings/model/mapper.py).

Imports (including optional/function-local imports; not a startup dependency list): `copy`, `src.engine.robot.configuration`.

### `RobotSettingsMapper`

```python
class RobotSettingsMapper:
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
@staticmethod
def to_flat_dict(settings: RobotSettings) -> dict
```

```python
@staticmethod
def from_flat_dict(flat: dict, base: RobotSettings) -> RobotSettings
```

### `RobotCalibrationMapper`

```python
class RobotCalibrationMapper:
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
@staticmethod
def to_flat_dict(settings: RobotCalibrationSettings) -> dict
```

```python
@staticmethod
def from_flat_dict(flat: dict, base: RobotCalibrationSettings) -> RobotCalibrationSettings
```

## `robot_settings_model.py`

Source: [src/applications/robot_settings/model/robot_settings_model.py](../../../../src/applications/robot_settings/model/robot_settings_model.py).

Imports (including optional/function-local imports; not a startup dependency list): `logging`, `src.applications.base.i_application_model`, `src.applications.robot_settings.model.mapper`, `src.applications.robot_settings.service.i_robot_settings_service`, `src.engine.robot.configuration`, `src.shared_contracts.declarations`, `typing`.

### `RobotSettingsModel`

```python
class RobotSettingsModel(IApplicationModel):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, service: IRobotSettingsService)
```

```python
def load(self) -> tuple[RobotSettings, RobotCalibrationSettings, dict | None]
```

```python
def save(self, flat: dict, movement_groups: Dict[str, MovementGroup]=None, targeting_data: dict | None=None) -> None
```

```python
def get_current_position(self) -> Optional[List[float]]
```

```python
def reload_config(self) -> RobotSettings
```

Reload config changed by another application.

```python
def save_targeting_definitions(self, targeting_data: dict) -> None
```

```python
def reload_targeting_definitions(self) -> dict | None
```

```python
def get_slot_info(self) -> List[Tuple[int, str]]
```

```python
def get_movement_group_definitions(self) -> List[MovementGroupDefinition]
```

```python
def get_expected_movement_groups(self) -> Dict[str, MovementGroup]
```

Saved groups merged with declared movement-group defaults.

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
