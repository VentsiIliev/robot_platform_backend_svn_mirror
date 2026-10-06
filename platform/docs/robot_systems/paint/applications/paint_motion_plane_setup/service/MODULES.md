# Module reference: `src/robot_systems/paint/applications/paint_motion_plane_setup/service`

[Package guide](README.md) · [Complete source index](../../../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [i_paint_motion_plane_setup_service.py](#i_paint_motion_plane_setup_servicepy)
- [paint_motion_plane_setup_service.py](#paint_motion_plane_setup_servicepy)

## `i_paint_motion_plane_setup_service.py`

Source: [src/robot_systems/paint/applications/paint_motion_plane_setup/service/i_paint_motion_plane_setup_service.py](../../../../../../src/robot_systems/paint/applications/paint_motion_plane_setup/service/i_paint_motion_plane_setup_service.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `abc`, `src.robot_systems.paint.applications.paint_motion_plane_setup.domain.plane_inference`.

### `IPaintMotionPlaneSetupService`

```python
class IPaintMotionPlaneSetupService(ABC):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
@abstractmethod
def get_paint_group_ids(self) -> list[str]
```

```python
@abstractmethod
def get_current_pose(self) -> Pose6D
```

```python
@abstractmethod
def get_paint_pose(self, group_id: str | None=None) -> Pose6D | None
```

```python
@abstractmethod
def move_to_paint_pose(self, group_id: str | None=None) -> bool
```

## `paint_motion_plane_setup_service.py`

Source: [src/robot_systems/paint/applications/paint_motion_plane_setup/service/paint_motion_plane_setup_service.py](../../../../../../src/robot_systems/paint/applications/paint_motion_plane_setup/service/paint_motion_plane_setup_service.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `logging`, `src.engine.robot.interfaces.i_robot_service`, `src.robot_systems.paint.applications.paint_motion_plane_setup.domain.plane_inference`, `src.robot_systems.paint.applications.paint_motion_plane_setup.service.i_paint_motion_plane_setup_service`.

### `PaintMotionPlaneSetupService`

```python
class PaintMotionPlaneSetupService(IPaintMotionPlaneSetupService):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, *, robot_service: IRobotService | None, navigation_service, paint_group_ids: list[str] | tuple[str, ...]) -> None
```

```python
def get_paint_group_ids(self) -> list[str]
```

```python
def get_current_pose(self) -> Pose6D
```

```python
def get_paint_pose(self, group_id: str | None=None) -> Pose6D | None
```

```python
def move_to_paint_pose(self, group_id: str | None=None) -> bool
```
