# Module reference: `pl_gui/dashboard/widgets`

[Package guide](README.md) · [Complete source index](../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [ControlButtonsWidget.py](#controlbuttonswidgetpy)
- [RobotTrajectoryWidget.py](#robottrajectorywidgetpy)
- [__init__.py](#__init__py)

## `ControlButtonsWidget.py`

Source: [pl_gui/dashboard/widgets/ControlButtonsWidget.py](../../../../pl_gui/dashboard/widgets/ControlButtonsWidget.py).

Imports (including optional/function-local imports; not a startup dependency list): `PyQt6.QtCore`, `PyQt6.QtWidgets`, `pl_gui.utils.utils_widgets.MaterialButton`.

### `ControlButtonsWidget`

```python
class ControlButtonsWidget(QWidget):
```

Pure UI widget: Start / Stop / Pause buttons. Zero knowledge of ApplicationState, MessageBroker, or topics. The adapter drives all state changes via the public setter API.

Declared fields/defaults:

```python
start_clicked = pyqtSignal()
stop_clicked = pyqtSignal()
pause_clicked = pyqtSignal()
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, parent: QWidget | None=None) -> None
```

```python
def init_ui(self) -> None
```

```python
def connect_signals(self) -> None
```

```python
def set_start_enabled(self, enabled: bool) -> None
```

```python
def set_stop_enabled(self, enabled: bool) -> None
```

```python
def set_pause_enabled(self, enabled: bool) -> None
```

```python
def set_pause_text(self, text: str) -> None
```

```python
def retranslateUi(self) -> None
```

```python
def changeEvent(self, event) -> None
```

## `RobotTrajectoryWidget.py`

Source: [pl_gui/dashboard/widgets/RobotTrajectoryWidget.py](../../../../pl_gui/dashboard/widgets/RobotTrajectoryWidget.py).

Imports (including optional/function-local imports; not a startup dependency list): `...core.IconLoader`, `PIL`, `PyQt6.QtCore`, `PyQt6.QtGui`, `PyQt6.QtWidgets`, `collections`, `cv2`, `dashboard.core.IconLoader`, `dashboard.styles`, `numpy`, `os`, `random`, `src.dashboard.resources.styles`, `threading`, `time`.

### `CompactTimeMetric`

```python
class CompactTimeMetric(QWidget):
```

Compact time metric with horizontal layout

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, title, value='0.00 s', color=None, parent=None)
```

```python
def init_ui(self, title, value)
```

```python
def update_value(self, value)
```

### `TrajectoryManager`

```python
class TrajectoryManager:
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, trail_length: int=100)
```

```python
def add_interpolated_points(self, start_pos, end_pos, num_interpolated=3)
```

```python
def update_position(self, position)
```

```python
def break_trajectory(self)
```

```python
def clear_trail(self)
```

```python
def get_trajectory_copy(self)
```

### `draw_icon_at_position`

```python
def draw_icon_at_position(icon, image, position)
```

### `draw_smooth_trail`

```python
def draw_smooth_trail(image, trajectory_points_with_breaks)
```

### `load_logo_icon`

```python
def load_logo_icon()
```

### `RobotTrajectoryWidget`

```python
class RobotTrajectoryWidget(QWidget):
```

Pure UI widget: displays a background camera frame and draws a robot trajectory trail on top. Has zero knowledge of MessageBroker or topics. Call set_image(), update_trajectory_point(), break_trajectory(), enable_drawing(), disable_drawing() from the adapter.

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, image_width=640, image_height=360, fps_ms: int=30, trail_length: int=100)
```

```python
def init_ui(self)
```

```python
def load_placeholder_image(self)
```

```python
def update_trajectory_point(self, message=None) -> None
```

Receive a trajectory point message and update the manager.

```python
def break_trajectory(self) -> None
```

```python
def set_image(self, message=None) -> None
```

```python
def enable_drawing(self, _=None) -> None
```

```python
def disable_drawing(self, _=None) -> None
```

```python
def update_display(self)
```

```python
def get_image_dimensions(self)
```

```python
def closeEvent(self, event)
```

## `__init__.py`

Source: [pl_gui/dashboard/widgets/__init__.py](../../../../pl_gui/dashboard/widgets/__init__.py).

No top-level functions, classes or public value declarations; inspect the source for imports or entry-point statements.
