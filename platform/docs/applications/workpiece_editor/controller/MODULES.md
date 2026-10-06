# Module reference: `src/applications/workpiece_editor/controller`

[Package guide](README.md) · [Complete source index](../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [workpiece_editor_controller.py](#workpiece_editor_controllerpy)

## `__init__.py`

Source: [src/applications/workpiece_editor/controller/__init__.py](../../../../src/applications/workpiece_editor/controller/__init__.py).

No top-level functions, classes or public value declarations; inspect the source for imports or entry-point statements.

## `workpiece_editor_controller.py`

Source: [src/applications/workpiece_editor/controller/workpiece_editor_controller.py](../../../../src/applications/workpiece_editor/controller/workpiece_editor_controller.py).

Imports (including optional/function-local imports; not a startup dependency list): `PyQt6.QtCore`, `PyQt6.QtGui`, `PyQt6.QtWidgets`, `copy`, `cv2`, `datetime`, `logging`, `numpy`, `os`, `src.applications.base.i_application_controller`, `src.applications.base.styled_message_box`, `src.applications.workpiece_editor.model`, `src.applications.workpiece_editor.service.i_workpiece_path_executor`, `src.applications.workpiece_editor.view.workpiece_editor_view`, `src.engine.core.i_messaging_service`, `src.engine.robot.path_interpolation.new_interpolation.debug_plotting`, `src.robot_systems.paint.processes.paint.config`, `src.shared_contracts.events.vision_events`, `src.shared_contracts.events.workpiece_events`, `time`, `traceback`, `typing`.

### `_Bridge`

```python
class _Bridge(QObject):
```

Declared fields/defaults:

```python
camera_frame = pyqtSignal(object)
load_workpiece_raw = pyqtSignal(dict)
```

### `WorkpieceEditorController`

```python
class WorkpieceEditorController(IApplicationController):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, model: WorkpieceEditorModel, view: WorkpieceEditorView, messaging: IMessagingService, custom_action_handler=None)
```

```python
def load(self) -> None
```

```python
def stop(self) -> None
```
