# Module reference: `src/applications/intrinsic_calibration_capture/controller`

[Package guide](README.md) · [Complete source index](../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [intrinsic_capture_controller.py](#intrinsic_capture_controllerpy)

## `__init__.py`

Source: [src/applications/intrinsic_calibration_capture/controller/__init__.py](../../../../src/applications/intrinsic_calibration_capture/controller/__init__.py).

No top-level functions, classes or public value declarations; inspect the source for imports or entry-point statements.

## `intrinsic_capture_controller.py`

Source: [src/applications/intrinsic_calibration_capture/controller/intrinsic_capture_controller.py](../../../../src/applications/intrinsic_calibration_capture/controller/intrinsic_capture_controller.py).

Imports (including optional/function-local imports; not a startup dependency list): `PyQt6.QtCore`, `__future__`, `src.applications.base.i_application_controller`, `src.applications.intrinsic_calibration_capture.model.intrinsic_capture_model`, `src.applications.intrinsic_calibration_capture.service.i_intrinsic_capture_service`, `src.applications.intrinsic_calibration_capture.view.intrinsic_capture_view`.

### `_Bridge`

```python
class _Bridge(QObject):
```

Safely delivers broker callbacks to the Qt thread.

Declared fields/defaults:

```python
message_received = pyqtSignal(str)
```

### `IntrinsicCaptureController`

```python
class IntrinsicCaptureController(IApplicationController):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, model: IntrinsicCaptureModel, view: IntrinsicCaptureView, messaging=None)
```

```python
def load(self) -> None
```

```python
def stop(self) -> None
```
