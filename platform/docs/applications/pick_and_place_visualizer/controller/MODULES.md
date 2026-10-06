# Module reference: `src/applications/pick_and_place_visualizer/controller`

[Package guide](README.md) · [Complete source index](../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [pick_and_place_visualizer_controller.py](#pick_and_place_visualizer_controllerpy)

## `__init__.py`

Source: [src/applications/pick_and_place_visualizer/controller/__init__.py](../../../../src/applications/pick_and_place_visualizer/controller/__init__.py).

No top-level functions, classes or public value declarations; inspect the source for imports or entry-point statements.

## `pick_and_place_visualizer_controller.py`

Source: [src/applications/pick_and_place_visualizer/controller/pick_and_place_visualizer_controller.py](../../../../src/applications/pick_and_place_visualizer/controller/pick_and_place_visualizer_controller.py).

Imports (including optional/function-local imports; not a startup dependency list): `PyQt6.QtCore`, `__future__`, `logging`, `logging.handlers`, `src.applications.base.i_application_controller`, `src.applications.pick_and_place_visualizer.model.pick_and_place_visualizer_model`, `src.applications.pick_and_place_visualizer.service.i_pick_and_place_visualizer_service`, `src.applications.pick_and_place_visualizer.view.pick_and_place_visualizer_view`, `src.engine.core.i_messaging_service`, `src.robot_systems.glue.component_ids`, `src.shared_contracts.events.pick_and_place_events`, `src.shared_contracts.events.process_events`, `src.shared_contracts.events.vision_events`, `traceback`, `typing`.

### `_Bridge`

```python
class _Bridge(QObject):
```

Declared fields/defaults:

```python
camera_frame = pyqtSignal(object)
process_state = pyqtSignal(str)
log_record = pyqtSignal(str)
workpiece_placed = pyqtSignal(object)
plane_reset = pyqtSignal()
match_result = pyqtSignal(object)
diagnostics = pyqtSignal(object)
```

### `_BridgeLogHandler`

```python
class _BridgeLogHandler(logging.Handler):
```

Captures pick-and-place + matching log records and forwards via Qt signal.

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, bridge: _Bridge)
```

```python
def emit(self, record: logging.LogRecord) -> None
```

### `PickAndPlaceVisualizerController`

```python
class PickAndPlaceVisualizerController(IApplicationController):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, model: PickAndPlaceVisualizerModel, view: PickAndPlaceVisualizerView, messaging: Optional[IMessagingService]=None)
```

```python
def load(self) -> None
```

```python
def stop(self) -> None
```
