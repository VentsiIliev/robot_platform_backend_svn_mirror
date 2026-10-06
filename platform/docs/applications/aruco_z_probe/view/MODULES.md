# Module reference: `src/applications/aruco_z_probe/view`

[Package guide](README.md) · [Complete source index](../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [aruco_z_probe_view.py](#aruco_z_probe_viewpy)

## `__init__.py`

Source: [src/applications/aruco_z_probe/view/__init__.py](../../../../src/applications/aruco_z_probe/view/__init__.py).

No top-level functions, classes or public value declarations; inspect the source for imports or entry-point statements.

## `aruco_z_probe_view.py`

Source: [src/applications/aruco_z_probe/view/aruco_z_probe_view.py](../../../../src/applications/aruco_z_probe/view/aruco_z_probe_view.py).

Imports (including optional/function-local imports; not a startup dependency list): `PyQt6.QtCore`, `PyQt6.QtGui`, `PyQt6.QtWidgets`, `__future__`, `numpy`, `pl_gui.settings.settings_view.styles`, `src.applications.base.app_styles`, `src.applications.base.i_application_view`.

### `ArucoZProbeView`

```python
class ArucoZProbeView(IApplicationView):
```

Declared fields/defaults:

```python
calibration_pos_requested = pyqtSignal()
sweep_requested = pyqtSignal()
stop_requested = pyqtSignal()
predict_requested = pyqtSignal()
verify_requested = pyqtSignal()
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
def update_camera_frame(self, frame: np.ndarray) -> None
```

```python
def get_marker_id(self) -> int
```

```python
def get_min_z(self) -> float
```

```python
def get_sample_count(self) -> int
```

```python
def get_detection_attempts(self) -> int
```

```python
def get_stabilization_delay(self) -> float
```

```python
def append_log(self, text: str) -> None
```

```python
def get_query_z(self) -> float
```

```python
def set_model_ready(self, ready: bool) -> None
```

```python
def show_prediction(self, z: float, dx: float, dy: float) -> None
```

```python
def set_busy(self, busy: bool) -> None
```
