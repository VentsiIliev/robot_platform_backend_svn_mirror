# Module reference: `src/applications/pick_target/controller`

[Package guide](README.md) · [Complete source index](../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [pick_target_controller.py](#pick_target_controllerpy)

## `__init__.py`

Source: [src/applications/pick_target/controller/__init__.py](../../../../src/applications/pick_target/controller/__init__.py).

No top-level functions, classes or public value declarations; inspect the source for imports or entry-point statements.

## `pick_target_controller.py`

Source: [src/applications/pick_target/controller/pick_target_controller.py](../../../../src/applications/pick_target/controller/pick_target_controller.py).

Imports (including optional/function-local imports; not a startup dependency list): `PyQt6.QtCore`, `__future__`, `cv2`, `logging`, `numpy`, `src.applications.base.i_application_controller`, `src.applications.base.styled_message_box`, `src.applications.pick_target.model.pick_target_model`, `src.applications.pick_target.view.pick_target_view`, `src.engine.core.i_messaging_service`, `src.shared_contracts.events.vision_events`, `time`, `typing`.

### `_Bridge`

```python
class _Bridge(QObject):
```

Routes broker callbacks (background thread) safely to the main thread.

Declared fields/defaults:

```python
camera_frame = pyqtSignal(object)
```

### `_MoveWorker`

```python
class _MoveWorker(QObject):
```

Iterates captured robot coords and moves to each one.

Declared fields/defaults:

```python
log_message = pyqtSignal(str)
finished = pyqtSignal()
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, model: PickTargetModel, coords: List[Tuple[float, float, float, float, float, float]], delay: float=0.0, override_z: float | None=None, use_base_z: bool=False, use_live_height: bool=False)
```

```python
def request_stop(self) -> None
```

```python
def run(self) -> None
```

### `_CalibWorker`

```python
class _CalibWorker(QObject):
```

Moves robot to the mode-appropriate start position.

Declared fields/defaults:

```python
log_message = pyqtSignal(str)
finished = pyqtSignal()
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, model: PickTargetModel)
```

```python
def run(self) -> None
```

### `_TrajectoryWorker`

```python
class _TrajectoryWorker(QObject):
```

Executes a contour trajectory on the robot.

Declared fields/defaults:

```python
log_message = pyqtSignal(str)
finished = pyqtSignal()
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, model: PickTargetModel, contour_robot_pts, z: float, vel: float, acc: float)
```

```python
def run(self) -> None
```

### `PickTargetController`

```python
class PickTargetController(IApplicationController):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, model: PickTargetModel, view: PickTargetView, messaging: Optional[IMessagingService]=None)
```

```python
def load(self) -> None
```

```python
def stop(self) -> None
```
