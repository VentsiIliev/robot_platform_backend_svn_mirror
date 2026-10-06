# Module reference: `src/robot_systems/paint/applications/paint_adjustment/controller`

[Package guide](README.md) · [Complete source index](../../../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [paint_adjustment_controller.py](#paint_adjustment_controllerpy)

## `__init__.py`

Source: [src/robot_systems/paint/applications/paint_adjustment/controller/__init__.py](../../../../../../src/robot_systems/paint/applications/paint_adjustment/controller/__init__.py).

Paint Adjustment controller.

No top-level functions, classes or public value declarations; inspect the source for imports or entry-point statements.

## `paint_adjustment_controller.py`

Source: [src/robot_systems/paint/applications/paint_adjustment/controller/paint_adjustment_controller.py](../../../../../../src/robot_systems/paint/applications/paint_adjustment/controller/paint_adjustment_controller.py).

Imports (including optional/function-local imports; not a startup dependency list): `..model.paint_adjustment_model`, `..service.i_paint_adjustment_service`, `..view.paint_adjustment_view`, `PyQt6.QtCore`, `PyQt6.QtGui`, `concurrent.futures`, `cv2`, `functools`, `logging`, `src.applications.base.i_application_controller`, `src.engine.core.i_messaging_service`, `src.robot_systems.paint.component_ids`, `src.shared_contracts.events.process_events`, `src.shared_contracts.events.vision_events`, `threading`.

### `_AdjustmentRelay`

```python
class _AdjustmentRelay(QObject):
```

Declared fields/defaults:

```python
finished = pyqtSignal(object)
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, on_finished) -> None
```

### `PaintAdjustmentController`

```python
class PaintAdjustmentController(IApplicationController):
```

Display the auxiliary stream and dispatch serial I/O off the UI thread.

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, model: PaintAdjustmentModel, view: PaintAdjustmentView, messaging: IMessagingService) -> None
```

```python
def load(self) -> None
```

```python
def stop(self) -> None
```
