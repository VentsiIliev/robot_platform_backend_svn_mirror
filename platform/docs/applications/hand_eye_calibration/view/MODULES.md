# Module reference: `src/applications/hand_eye_calibration/view`

[Package guide](README.md) · [Complete source index](../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [hand_eye_view.py](#hand_eye_viewpy)

## `__init__.py`

Source: [src/applications/hand_eye_calibration/view/__init__.py](../../../../src/applications/hand_eye_calibration/view/__init__.py).

No top-level functions, classes or public value declarations; inspect the source for imports or entry-point statements.

## `hand_eye_view.py`

Source: [src/applications/hand_eye_calibration/view/hand_eye_view.py](../../../../src/applications/hand_eye_calibration/view/hand_eye_view.py).

Imports (including optional/function-local imports; not a startup dependency list): `PyQt6.QtCore`, `PyQt6.QtGui`, `PyQt6.QtWidgets`, `__future__`, `numpy`, `src.applications.base.i_application_view`, `src.applications.hand_eye_calibration.service.i_hand_eye_service`.

### `HandEyeView`

```python
class HandEyeView(IApplicationView):
```

Declared fields/defaults:

```python
start_requested = pyqtSignal()
stop_requested = pyqtSignal()
save_config_requested = pyqtSignal(object)
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, parent=None)
```

```python
def setup_ui(self) -> None
```

```python
def clean_up(self) -> None
```

```python
def set_sample_count(self, n: int) -> None
```

```python
def get_config(self) -> HandEyeConfig
```

```python
def set_config(self, config: HandEyeConfig) -> None
```

```python
def set_running(self, running: bool) -> None
```

```python
def append_log(self, message: str) -> None
```

```python
def set_frame(self, frame: np.ndarray) -> None
```
