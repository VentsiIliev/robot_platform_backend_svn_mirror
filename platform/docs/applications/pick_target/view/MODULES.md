# Module reference: `src/applications/pick_target/view`

[Package guide](README.md) · [Complete source index](../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [pick_target_view.py](#pick_target_viewpy)

## `__init__.py`

Source: [src/applications/pick_target/view/__init__.py](../../../../src/applications/pick_target/view/__init__.py).

No top-level functions, classes or public value declarations; inspect the source for imports or entry-point statements.

## `pick_target_view.py`

Source: [src/applications/pick_target/view/pick_target_view.py](../../../../src/applications/pick_target/view/pick_target_view.py).

Imports (including optional/function-local imports; not a startup dependency list): `PyQt6.QtCore`, `PyQt6.QtGui`, `PyQt6.QtWidgets`, `cv2`, `numpy`, `pl_gui.settings.settings_view.styles`, `src.applications.base.app_styles`, `src.applications.base.i_application_view`.

### `_ZoomableImageWidget`

```python
class _ZoomableImageWidget(QWidget):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, parent=None)
```

```python
def set_frame(self, frame: np.ndarray) -> None
```

```python
def zoom_in(self) -> None
```

```python
def zoom_out(self) -> None
```

```python
def reset_zoom(self) -> None
```

```python
def eventFilter(self, obj: QObject, event: QEvent) -> bool
```

### `PickTargetView`

```python
class PickTargetView(IApplicationView):
```

Declared fields/defaults:

```python
SHOW_JOG_WIDGET = True
JOG_FRAME_SELECTOR_ENABLED = True
capture_requested = pyqtSignal()
move_requested = pyqtSignal()
calibration_pos_requested = pyqtSignal()
target_changed = pyqtSignal(str)
pickup_plane_toggled = pyqtSignal(bool)
pickup_plane_rz_changed = pyqtSignal(float)
execute_trajectory_requested = pyqtSignal()
z_mode_toggled = pyqtSignal(bool)
apply_correction_requested = pyqtSignal()
measure_height_toggled = pyqtSignal(bool)
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, parent=None)
```

```python
def setup_ui(self) -> None
```

```python
def update_camera_frame(self, frame: np.ndarray) -> None
```

```python
def update_captured_frame(self, frame: np.ndarray) -> None
```

```python
def append_log(self, text: str) -> None
```

```python
def set_move_enabled(self, enabled: bool) -> None
```

```python
def set_trajectory_enabled(self, enabled: bool) -> None
```

```python
def set_correction_available(self, available: bool) -> None
```

```python
def set_busy(self, busy: bool) -> None
```

```python
def get_move_delay(self) -> float
```

```python
def get_trajectory_vel(self) -> float
```

```python
def get_trajectory_acc(self) -> float
```

```python
def get_trajectory_z(self) -> float
```

```python
def get_pickup_plane_rz(self) -> float
```

```python
def get_target(self) -> str
```

```python
def clean_up(self) -> None
```
