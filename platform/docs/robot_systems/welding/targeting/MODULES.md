# Module reference: `src/robot_systems/welding/targeting`

[Package guide](README.md) · [Complete source index](../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [frames.py](#framespy)
- [provider.py](#providerpy)
- [registry.py](#registrypy)
- [settings_adapter.py](#settings_adapterpy)

## `__init__.py`

Source: [src/robot_systems/welding/targeting/__init__.py](../../../../src/robot_systems/welding/targeting/__init__.py).

Imports (including optional/function-local imports; not a startup dependency list): `src.robot_systems.welding.targeting.frames`, `src.robot_systems.welding.targeting.provider`, `src.robot_systems.welding.targeting.registry`.

Package-level import/export surface:

```python
from src.robot_systems.welding.targeting.frames import build_welding_target_frames
from src.robot_systems.welding.targeting.provider import WeldingRobotSystemTargetingProvider
from src.robot_systems.welding.targeting.registry import build_welding_point_registry
```

Module declarations (expressions are shown without evaluating them):

```python
__all__ = ['WeldingRobotSystemTargetingProvider', 'build_welding_point_registry', 'build_welding_target_frames']
```

## `frames.py`

Source: [src/robot_systems/welding/targeting/frames.py](../../../../src/robot_systems/welding/targeting/frames.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `src.engine.robot.plane_pose_mapper`, `src.engine.robot.targeting`, `src.robot_systems.welding.navigation`, `typing`.

### `build_welding_target_frames`

```python
def build_welding_target_frames(frame_definitions: Iterable[TargetFrameDefinition] | None, navigation: Optional[WeldingNavigationService], height_correction=None) -> Dict[str, TargetFrame]
```

### `_build_mapper`

```python
def _build_mapper(definition: TargetFrameDefinition, navigation: Optional[WeldingNavigationService]) -> Optional[PlanePoseMapper]
```

## `provider.py`

Source: [src/robot_systems/welding/targeting/provider.py](../../../../src/robot_systems/welding/targeting/provider.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `src.engine.common_settings_ids`, `src.engine.robot.height_measuring.height_correction_service`, `src.engine.robot.targeting.robot_system_targeting_provider`, `src.robot_systems.welding.targeting.frames`, `src.robot_systems.welding.targeting.registry`.

### `WeldingRobotSystemTargetingProvider`

```python
class WeldingRobotSystemTargetingProvider(RobotSystemTargetingProvider):
```

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
def get_frame_for_work_area(self, work_area_id: str)
```

```python
def get_work_area_for_frame(self, frame_name: str) -> str | None
```

```python
def get_target_options(self) -> list[tuple[str, str]]
```

```python
def get_default_target_name(self) -> str
```

## `registry.py`

Source: [src/robot_systems/welding/targeting/registry.py](../../../../src/robot_systems/welding/targeting/registry.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `src.engine.robot.targeting`, `typing`.

### `build_welding_point_registry`

```python
def build_welding_point_registry(point_definitions: Iterable[dict]) -> PointRegistry
```

## `settings_adapter.py`

Source: [src/robot_systems/welding/targeting/settings_adapter.py](../../../../src/robot_systems/welding/targeting/settings_adapter.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `copy`, `src.engine.robot.targeting`.

### `to_editor_dict`

```python
def to_editor_dict(settings: TargetingSettings | None, point_definitions: list[RemoteTcpDefinition], frame_definitions: list[TargetFrameDefinition]) -> dict
```

### `from_editor_dict`

```python
def from_editor_dict(data: dict, base: TargetingSettings | None, point_definitions: list[RemoteTcpDefinition], frame_definitions: list[TargetFrameDefinition]) -> TargetingSettings
```
