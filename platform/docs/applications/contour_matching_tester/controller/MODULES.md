# Module reference: `src/applications/contour_matching_tester/controller`

[Package guide](README.md) · [Complete source index](../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [contour_matching_tester_controller.py](#contour_matching_tester_controllerpy)

## `__init__.py`

Source: [src/applications/contour_matching_tester/controller/__init__.py](../../../../src/applications/contour_matching_tester/controller/__init__.py).

No top-level functions, classes or public value declarations; inspect the source for imports or entry-point statements.

## `contour_matching_tester_controller.py`

Source: [src/applications/contour_matching_tester/controller/contour_matching_tester_controller.py](../../../../src/applications/contour_matching_tester/controller/contour_matching_tester_controller.py).

Imports (including optional/function-local imports; not a startup dependency list): `PyQt6.QtCore`, `cv2`, `functools`, `logging`, `numpy`, `src.applications.base.i_application_controller`, `src.applications.contour_matching_tester.model.contour_matching_tester_model`, `src.applications.contour_matching_tester.view.contour_matching_tester_view`, `src.engine.core.i_messaging_service`, `src.shared_contracts.events.vision_events`, `typing`.

### `_Bridge`

```python
class _Bridge(QObject):
```

Declared fields/defaults:

```python
camera_frame = pyqtSignal(object)
```

### `_Worker`

```python
class _Worker(QObject):
```

Declared fields/defaults:

```python
finished = pyqtSignal(object)
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, fn)
```

```python
def run(self) -> None
```

### `ContourMatchingTesterController`

```python
class ContourMatchingTesterController(IApplicationController):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, model: ContourMatchingTesterModel, view: ContourMatchingTesterView, messaging: Optional[IMessagingService]=None)
```

```python
def load(self) -> None
```

```python
def stop(self) -> None
```
