# Module reference: `src/applications/hand_eye_calibration/controller`

[Package guide](README.md) · [Complete source index](../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [hand_eye_controller.py](#hand_eye_controllerpy)

## `__init__.py`

Source: [src/applications/hand_eye_calibration/controller/__init__.py](../../../../src/applications/hand_eye_calibration/controller/__init__.py).

No top-level functions, classes or public value declarations; inspect the source for imports or entry-point statements.

## `hand_eye_controller.py`

Source: [src/applications/hand_eye_calibration/controller/hand_eye_controller.py](../../../../src/applications/hand_eye_calibration/controller/hand_eye_controller.py).

Imports (including optional/function-local imports; not a startup dependency list): `PyQt6.QtCore`, `__future__`, `src.applications.base.i_application_controller`, `src.applications.hand_eye_calibration.model.hand_eye_model`, `src.applications.hand_eye_calibration.service.i_hand_eye_service`, `src.applications.hand_eye_calibration.view.hand_eye_view`.

### `_Bridge`

```python
class _Bridge(QObject):
```

Safely delivers broker callbacks to the Qt main thread.

Declared fields/defaults:

```python
message_received = pyqtSignal(str)
complete_received = pyqtSignal(str)
sample_count_received = pyqtSignal(int)
```

### `HandEyeController`

```python
class HandEyeController(IApplicationController):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, model: HandEyeModel, view: HandEyeView, messaging=None)
```

```python
def load(self) -> None
```

```python
def stop(self) -> None
```
