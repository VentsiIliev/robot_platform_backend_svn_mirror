# Module reference: `src/robot_systems/paint/applications/paint_motion_plane_setup/model`

[Package guide](README.md) · [Complete source index](../../../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [paint_motion_plane_setup_model.py](#paint_motion_plane_setup_modelpy)

## `paint_motion_plane_setup_model.py`

Source: [src/robot_systems/paint/applications/paint_motion_plane_setup/model/paint_motion_plane_setup_model.py](../../../../../../src/robot_systems/paint/applications/paint_motion_plane_setup/model/paint_motion_plane_setup_model.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `src.applications.base.i_application_model`, `src.robot_systems.paint.applications.paint_motion_plane_setup.domain.plane_inference`, `src.robot_systems.paint.applications.paint_motion_plane_setup.service.i_paint_motion_plane_setup_service`.

### `PaintMotionPlaneSetupModel`

```python
class PaintMotionPlaneSetupModel(IApplicationModel):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, service: IPaintMotionPlaneSetupService) -> None
```

```python
def load(self) -> None
```

```python
def save(self, *args, **kwargs) -> None
```

```python
def get_current_pose(self) -> Pose6D
```

```python
def select_paint_group(self, group_id: str) -> Pose6D | None
```

```python
def move_to_paint_pose(self) -> bool
```

```python
def update_inference(self) -> PlaneInference | None
```
