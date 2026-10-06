# Module reference: `src/robot_systems/paint/applications/paint_motion_plane_setup/controller`

[Package guide](README.md) · [Complete source index](../../../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [paint_motion_plane_setup_controller.py](#paint_motion_plane_setup_controllerpy)

## `paint_motion_plane_setup_controller.py`

Source: [src/robot_systems/paint/applications/paint_motion_plane_setup/controller/paint_motion_plane_setup_controller.py](../../../../../../src/robot_systems/paint/applications/paint_motion_plane_setup/controller/paint_motion_plane_setup_controller.py).

Imports (including optional/function-local imports; not a startup dependency list): `PyQt6.QtCore`, `__future__`, `logging`, `src.applications.base.i_application_controller`, `src.robot_systems.paint.applications.paint_motion_plane_setup.domain.plane_inference`, `src.robot_systems.paint.applications.paint_motion_plane_setup.model.paint_motion_plane_setup_model`, `src.robot_systems.paint.applications.paint_motion_plane_setup.view.paint_motion_plane_setup_view`.

### `_Worker`

```python
class _Worker(QObject):
```

Declared fields/defaults:

```python
finished = pyqtSignal(object)
failed = pyqtSignal(str)
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, fn) -> None
```

```python
def run(self) -> None
```

### `PaintMotionPlaneSetupController`

```python
class PaintMotionPlaneSetupController(IApplicationController):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, model: PaintMotionPlaneSetupModel, view: PaintMotionPlaneSetupView) -> None
```

```python
def load(self) -> None
```

```python
def stop(self) -> None
```
