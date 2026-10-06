# Module reference: `src/robot_systems/ROBOT_SYSTEM_BLUEPRINT/targeting`

[Package guide](README.md) · [Complete source index](../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [frames.py](#framespy)
- [provider.py](#providerpy)
- [registry.py](#registrypy)
- [settings_adapter.py](#settings_adapterpy)

## `__init__.py`

Source: [src/robot_systems/ROBOT_SYSTEM_BLUEPRINT/targeting/__init__.py](../../../../src/robot_systems/ROBOT_SYSTEM_BLUEPRINT/targeting/__init__.py).

Imports (including optional/function-local imports; not a startup dependency list): `src.robot_systems.ROBOT_SYSTEM_BLUEPRINT.targeting.frames`, `src.robot_systems.ROBOT_SYSTEM_BLUEPRINT.targeting.provider`, `src.robot_systems.ROBOT_SYSTEM_BLUEPRINT.targeting.registry`.

Package-level import/export surface:

```python
from src.robot_systems.ROBOT_SYSTEM_BLUEPRINT.targeting.frames import build_my_target_frames
from src.robot_systems.ROBOT_SYSTEM_BLUEPRINT.targeting.provider import MyRobotSystemTargetingProvider
from src.robot_systems.ROBOT_SYSTEM_BLUEPRINT.targeting.registry import build_my_point_registry
```

Module declarations (expressions are shown without evaluating them):

```python
__all__ = ['MyRobotSystemTargetingProvider', 'build_my_point_registry', 'build_my_target_frames']
```

## `frames.py`

Source: [src/robot_systems/ROBOT_SYSTEM_BLUEPRINT/targeting/frames.py](../../../../src/robot_systems/ROBOT_SYSTEM_BLUEPRINT/targeting/frames.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `src.engine.robot.targeting`, `typing`.

### `build_my_target_frames`

```python
def build_my_target_frames(frame_definitions: Iterable[TargetFrameDefinition] | None, navigation=None, height_correction=None) -> dict[str, TargetFrame]
```

TODO: Convert persisted frame settings into runtime TargetFrame objects.

## `provider.py`

Source: [src/robot_systems/ROBOT_SYSTEM_BLUEPRINT/targeting/provider.py](../../../../src/robot_systems/ROBOT_SYSTEM_BLUEPRINT/targeting/provider.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `src.engine.common_service_ids`, `src.engine.common_settings_ids`, `src.engine.robot.targeting.robot_system_targeting_provider`, `src.robot_systems.ROBOT_SYSTEM_BLUEPRINT.targeting.frames`, `src.robot_systems.ROBOT_SYSTEM_BLUEPRINT.targeting.registry`.

### `MyRobotSystemTargetingProvider`

```python
class MyRobotSystemTargetingProvider(RobotSystemTargetingProvider):
```

TODO: Build targeting runtime objects for the concrete robot system.

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, robot_system) -> None
```

```python
def build_point_registry(self)
```

```python
def build_frames(self)
```

```python
def get_target_options(self) -> list[tuple[str, str]]
```

```python
def get_default_target_name(self) -> str
```

## `registry.py`

Source: [src/robot_systems/ROBOT_SYSTEM_BLUEPRINT/targeting/registry.py](../../../../src/robot_systems/ROBOT_SYSTEM_BLUEPRINT/targeting/registry.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `src.engine.robot.targeting`, `typing`.

### `build_my_point_registry`

```python
def build_my_point_registry(point_definitions: Iterable[dict]) -> PointRegistry
```

TODO: Convert persisted target-point settings into a PointRegistry.

## `settings_adapter.py`

Source: [src/robot_systems/ROBOT_SYSTEM_BLUEPRINT/targeting/settings_adapter.py](../../../../src/robot_systems/ROBOT_SYSTEM_BLUEPRINT/targeting/settings_adapter.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `copy`, `src.engine.robot.targeting`.

### `to_editor_dict`

```python
def to_editor_dict(settings: TargetingSettings | None, point_definitions: list[RemoteTcpDefinition], frame_definitions: list[TargetFrameDefinition]) -> dict
```

### `from_editor_dict`

```python
def from_editor_dict(data: dict, base: TargetingSettings | None, point_definitions: list[RemoteTcpDefinition], frame_definitions: list[TargetFrameDefinition]) -> TargetingSettings
```
