# Module reference: `src/applications/tool_settings/service`

[Package guide](README.md) · [Complete source index](../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [i_tool_settings_service.py](#i_tool_settings_servicepy)
- [stub_tool_settings_service.py](#stub_tool_settings_servicepy)
- [tool_settings_application_service.py](#tool_settings_application_servicepy)

## `__init__.py`

Source: [src/applications/tool_settings/service/__init__.py](../../../../src/applications/tool_settings/service/__init__.py).

No top-level functions, classes or public value declarations; inspect the source for imports or entry-point statements.

## `i_tool_settings_service.py`

Source: [src/applications/tool_settings/service/i_tool_settings_service.py](../../../../src/applications/tool_settings/service/i_tool_settings_service.py).

Imports (including optional/function-local imports; not a startup dependency list): `abc`, `src.engine.robot.interfaces.tool_definition`, `src.engine.robot.tool_changer`, `typing`.

### `IToolSettingsService`

```python
class IToolSettingsService(ABC):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
@abstractmethod
def get_tools(self) -> List[ToolDefinition]
```

```python
@abstractmethod
def add_tool(self, tool_id: int, name: str) -> Tuple[bool, str]
```

```python
@abstractmethod
def update_tool(self, tool_id: int, name: str) -> Tuple[bool, str]
```

```python
@abstractmethod
def remove_tool(self, tool_id: int) -> Tuple[bool, str]
```

```python
@abstractmethod
def get_slots(self) -> List[SlotConfig]
```

```python
@abstractmethod
def update_slot(self, slot_id: int, tool_id: int) -> Tuple[bool, str]
```

```python
@abstractmethod
def add_slot(self, slot_id: int, tool_id: int) -> Tuple[bool, str]
```

```python
@abstractmethod
def remove_slot(self, slot_id: int) -> Tuple[bool, str]
```

```python
@abstractmethod
def update_tool_geometry(self, tool_id: int, relative_transform: list[float], collision_profile: str) -> Tuple[bool, str]
```

```python
@abstractmethod
def update_slot_sequences(self, slot_id: int, pickup: list[dict], dropoff: list[dict]) -> Tuple[bool, str]
```

```python
@abstractmethod
def capture_reference_contact(self) -> Tuple[bool, str]
```

```python
@abstractmethod
def capture_tool_contact(self) -> Tuple[bool, str, dict]
```

```python
@abstractmethod
def solve_tool_calibration(self, tool_id: int) -> Tuple[bool, str, dict]
```

```python
@abstractmethod
def activate_tool(self, tool_id: int) -> Tuple[bool, str]
```

```python
@abstractmethod
def get_current_motion_pose(self) -> Tuple[bool, str, list[float]]
```

## `stub_tool_settings_service.py`

Source: [src/applications/tool_settings/service/stub_tool_settings_service.py](../../../../src/applications/tool_settings/service/stub_tool_settings_service.py).

Imports (including optional/function-local imports; not a startup dependency list): `.i_tool_settings_service`, `logging`, `src.engine.robot.interfaces.tool_definition`, `src.engine.robot.tool_changer`, `typing`.

### `StubToolSettingsService`

```python
class StubToolSettingsService(IToolSettingsService):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self)
```

```python
def get_tools(self) -> List[ToolDefinition]
```

```python
def add_tool(self, tool_id: int, name: str) -> Tuple[bool, str]
```

```python
def update_tool(self, tool_id: int, name: str) -> Tuple[bool, str]
```

```python
def remove_tool(self, tool_id: int) -> Tuple[bool, str]
```

```python
def get_slots(self) -> List[SlotConfig]
```

```python
def update_slot(self, slot_id: int, tool_id: int) -> Tuple[bool, str]
```

```python
def add_slot(self, slot_id: int, tool_id: int) -> Tuple[bool, str]
```

```python
def remove_slot(self, slot_id: int) -> Tuple[bool, str]
```

```python
def update_tool_geometry(self, tool_id, relative_transform, collision_profile='')
```

```python
def update_slot_sequences(self, slot_id, pickup, dropoff)
```

```python
def capture_reference_contact(self)
```

```python
def capture_tool_contact(self)
```

```python
def solve_tool_calibration(self, tool_id)
```

```python
def activate_tool(self, tool_id)
```

```python
def get_current_motion_pose(self)
```

## `tool_settings_application_service.py`

Source: [src/applications/tool_settings/service/tool_settings_application_service.py](../../../../src/applications/tool_settings/service/tool_settings_application_service.py).

### `ToolSettingsApplicationService`

```python
class ToolSettingsApplicationService(IToolSettingsService):
```

```python
def __init__(self, settings_service: ISettingsService, robot_service=None, tool_registry_client=None, tool_service: IToolService | None=None)
```

```python
def get_tools(self) -> List[ToolDefinition]
```

```python
def add_tool(self, tool_id: int, name: str) -> Tuple[bool, str]
```

```python
def update_tool(self, tool_id: int, name: str) -> Tuple[bool, str]
```

```python
def remove_tool(self, tool_id: int) -> Tuple[bool, str]
```

```python
def get_slots(self) -> List[SlotConfig]
```

```python
def update_slot(self, slot_id: int, tool_id) -> Tuple[bool, str]
```

tool_id=None unassigns the slot.

```python
def add_slot(self, slot_id: int, tool_id) -> Tuple[bool, str]
```

tool_id=None creates an unassigned slot.

```python
def remove_slot(self, slot_id: int) -> Tuple[bool, str]
```

```python
def update_tool_geometry(self, tool_id: int, relative_transform: list[float], collision_profile: str='') -> Tuple[bool, str]
```

```python
def update_slot_sequences(self, slot_id: int, pickup: list[dict], dropoff: list[dict]) -> Tuple[bool, str]
```

```python
def capture_reference_contact(self) -> Tuple[bool, str]
```

```python
def capture_tool_contact(self) -> Tuple[bool, str, dict]
```

```python
def solve_tool_calibration(self, tool_id: int) -> Tuple[bool, str, dict]
```

```python
def activate_tool(self, tool_id: int) -> Tuple[bool, str]
```

```python
def get_current_motion_pose(self) -> Tuple[bool, str, list[float]]
```

```python
def execute_sequence(self, slot_id: int, steps: list[dict], cancelled) -> Tuple[bool, str]
```

Run the editor draft using the system's shared tool executor.

```python
def stop_sequence_motion(self) -> Tuple[bool, str]
```
