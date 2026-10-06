# Module reference: `src/shared_contracts/declarations`

[Package guide](README.md) · [Complete source index](../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [dispensing.py](#dispensingpy)
- [movement.py](#movementpy)
- [system_specs.py](#system_specspy)
- [targeting.py](#targetingpy)
- [tooling.py](#toolingpy)
- [work_areas.py](#work_areaspy)

## `__init__.py`

Source: [src/shared_contracts/declarations/__init__.py](../../../src/shared_contracts/declarations/__init__.py).

Imports (including optional/function-local imports; not a startup dependency list): `src.shared_contracts.declarations.dispensing`, `src.shared_contracts.declarations.movement`, `src.shared_contracts.declarations.system_specs`, `src.shared_contracts.declarations.targeting`, `src.shared_contracts.declarations.tooling`, `src.shared_contracts.declarations.work_areas`.

Package-level import/export surface:

```python
from src.shared_contracts.declarations.dispensing import DispenseChannelDefinition
from src.shared_contracts.declarations.movement import MovementGroupDefinition, MovementGroupType
from src.shared_contracts.declarations.system_specs import ApplicationSpec, FolderSpec, RolePolicy, ServiceSpec, SettingsSpec, ShellSetup, SystemMetadata
from src.shared_contracts.declarations.targeting import RemoteTcpDefinition, TargetFrameDefinition
from src.shared_contracts.declarations.tooling import ToolDefinition, ToolSlotDefinition
from src.shared_contracts.declarations.work_areas import WorkAreaDefinition, WorkAreaObserverBinding
```

Module declarations (expressions are shown without evaluating them):

```python
__all__ = ['ApplicationSpec', 'DispenseChannelDefinition', 'FolderSpec', 'MovementGroupDefinition', 'MovementGroupType', 'RemoteTcpDefinition', 'RolePolicy', 'ServiceSpec', 'SettingsSpec', 'ShellSetup', 'SystemMetadata', 'TargetFrameDefinition', 'ToolDefinition', 'ToolSlotDefinition', 'WorkAreaDefinition', 'WorkAreaObserverBinding']
```

## `dispensing.py`

Source: [src/shared_contracts/declarations/dispensing.py](../../../src/shared_contracts/declarations/dispensing.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `dataclasses`, `typing`.

### `DispenseChannelDefinition`

```python
@dataclass(frozen=True)
class DispenseChannelDefinition:
```

Declared fields/defaults:

```python
id: str
label: str
weight_cell_id: int
pump_motor_address: int
default_glue_type: str = ''
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
@classmethod
def from_dict(cls, data: dict[str, Any]) -> 'DispenseChannelDefinition'
```

```python
def to_dict(self) -> dict[str, Any]
```

## `movement.py`

Source: [src/shared_contracts/declarations/movement.py](../../../src/shared_contracts/declarations/movement.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `dataclasses`, `enum`, `src.engine.robot.configuration`.

### `MovementGroupType`

```python
class MovementGroupType(Enum):
```

Declared fields/defaults:

```python
SINGLE_POSITION = 'single_position'
MULTI_POSITION = 'multi_position'
VELOCITY_ONLY = 'velocity_only'
```

### `MovementGroupDefinition`

```python
@dataclass(frozen=True)
class MovementGroupDefinition:
```

Declared fields/defaults:

```python
id: str
group_type: MovementGroupType
label: str = ''
has_iterations: bool = False
has_trajectory_execution: bool = False
removable: bool = False
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def build_default_group(self) -> MovementGroup
```

## `system_specs.py`

Source: [src/shared_contracts/declarations/system_specs.py](../../../src/shared_contracts/declarations/system_specs.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `dataclasses`, `os`, `src.engine.repositories.interfaces`, `typing`.

### `FolderSpec`

```python
@dataclass(frozen=True)
class FolderSpec:
```

Declared fields/defaults:

```python
folder_id: int
name: str
display_name: str
translation_key: str = ''
```

### `ApplicationSpec`

```python
@dataclass(frozen=True)
class ApplicationSpec:
```

Declared fields/defaults:

```python
name: str
folder_id: int
icon: str = 'fa5s.cog'
factory: Optional[Callable] = field(default=None, compare=False)
app_id: str = ''
```

### `ShellSetup`

```python
@dataclass(frozen=True)
class ShellSetup:
```

Declared fields/defaults:

```python
folders: List[FolderSpec] = field(default_factory=list)
applications: List[ApplicationSpec] = field(default_factory=list)
```

### `RolePolicy`

```python
@dataclass(frozen=True)
class RolePolicy:
```

Declared fields/defaults:

```python
role_values: List[str] = field(default_factory=list)
admin_role_value: str = 'Admin'
default_permission_role_values: List[str] = field(default_factory=list)
protected_app_role_values: Dict[str, List[str]] = field(default_factory=dict)
```

### `ServiceSpec`

```python
@dataclass(frozen=True)
class ServiceSpec:
```

Declared fields/defaults:

```python
name: str
service_type: Type
required: bool = True
description: str = ''
builder: Optional[Callable] = field(default=None, compare=False)
```

### `SystemMetadata`

```python
@dataclass(frozen=True)
class SystemMetadata:
```

Declared fields/defaults:

```python
name: str
version: str = '1.0.0'
description: str = ''
author: str = ''
settings_root: str = os.path.join('storage', 'settings')
translations_root: str = os.path.join('storage', 'translations')
```

### `SettingsSpec`

```python
@dataclass(frozen=True)
class SettingsSpec:
```

Declared fields/defaults:

```python
name: str
serializer: ISettingsSerializer
storage_key: str
required: bool = True
```

## `targeting.py`

Source: [src/shared_contracts/declarations/targeting.py](../../../src/shared_contracts/declarations/targeting.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `dataclasses`, `typing`.

### `RemoteTcpDefinition`

```python
@dataclass(frozen=True)
class RemoteTcpDefinition:
```

Declared fields/defaults:

```python
name: str
display_name: str = ''
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
@classmethod
def from_dict(cls, data: dict[str, Any]) -> 'RemoteTcpDefinition'
```

```python
def to_dict(self) -> dict[str, Any]
```

### `TargetFrameDefinition`

```python
@dataclass(frozen=True)
class TargetFrameDefinition:
```

Declared fields/defaults:

```python
name: str
work_area_id: str = ''
source_navigation_group: str = ''
target_navigation_group: str = ''
use_height_correction: bool = False
display_name: str = ''
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
@classmethod
def from_dict(cls, data: dict[str, Any]) -> 'TargetFrameDefinition'
```

```python
def to_dict(self) -> dict[str, Any]
```

## `tooling.py`

Source: [src/shared_contracts/declarations/tooling.py](../../../src/shared_contracts/declarations/tooling.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `dataclasses`, `typing`.

### `ToolDefinition`

```python
@dataclass(frozen=True)
class ToolDefinition:
```

Declared fields/defaults:

```python
id: int
name: str
reference_tool_id: int | None = None
relative_transform: tuple[float, float, float, float, float, float] = (0, 0, 0, 0, 0, 0)
collision_profile: str = ''
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
@classmethod
def from_dict(cls, data: dict[str, Any]) -> 'ToolDefinition'
```

```python
def to_dict(self) -> dict[str, Any]
```

### `ToolSlotDefinition`

```python
@dataclass(frozen=True)
class ToolSlotDefinition:
```

Declared fields/defaults:

```python
id: int
tool_id: int | None = None
pickup_movement_group_id: str = ''
dropoff_movement_group_id: str = ''
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
@classmethod
def from_dict(cls, data: dict[str, Any]) -> 'ToolSlotDefinition'
```

```python
def to_dict(self) -> dict[str, Any]
```

## `work_areas.py`

Source: [src/shared_contracts/declarations/work_areas.py](../../../src/shared_contracts/declarations/work_areas.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `dataclasses`.

### `WorkAreaDefinition`

```python
@dataclass(frozen=True)
class WorkAreaDefinition:
```

Declared fields/defaults:

```python
id: str
label: str
color: str
threshold_profile: str = 'default'
supports_detection_roi: bool = True
supports_brightness_roi: bool = False
supports_height_mapping: bool = False
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def detection_area_key(self) -> str
```

```python
def brightness_area_key(self) -> str
```

```python
def height_mapping_area_key(self) -> str
```

### `WorkAreaObserverBinding`

```python
@dataclass(frozen=True)
class WorkAreaObserverBinding:
```

Declared fields/defaults:

```python
area_id: str
movement_group_id: str
```
