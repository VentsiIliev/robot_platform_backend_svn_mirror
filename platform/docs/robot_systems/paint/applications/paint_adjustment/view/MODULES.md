# Module reference: `src/robot_systems/paint/applications/paint_adjustment/view`

[Package guide](README.md) · [Complete source index](../../../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [paint_adjustment_view.py](#paint_adjustment_viewpy)
- [paint_head_dial.py](#paint_head_dialpy)

## `__init__.py`

Source: [src/robot_systems/paint/applications/paint_adjustment/view/__init__.py](../../../../../../src/robot_systems/paint/applications/paint_adjustment/view/__init__.py).

Paint Adjustment view.

No top-level functions, classes or public value declarations; inspect the source for imports or entry-point statements.

## `paint_adjustment_view.py`

Source: [src/robot_systems/paint/applications/paint_adjustment/view/paint_adjustment_view.py](../../../../../../src/robot_systems/paint/applications/paint_adjustment/view/paint_adjustment_view.py).

Imports (including optional/function-local imports; not a startup dependency list): `.paint_head_dial`, `PyQt6.QtCore`, `PyQt6.QtGui`, `PyQt6.QtWidgets`, `pl_gui.settings.settings_view.styles`, `src.applications.base.i_application_view`, `src.applications.base.widgets.keyboard_number_field`.

### `_CameraPreview`

```python
class _CameraPreview(QLabel):
```

Camera image with an inspection guide while no frame is available.

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, parent=None) -> None
```

```python
def set_empty_text(self, title: str, detail: str) -> None
```

```python
def paintEvent(self, event) -> None
```

### `PaintAdjustmentView`

```python
class PaintAdjustmentView(IApplicationView):
```

Auxiliary preview with paint-adjustment requests.

Declared fields/defaults:

```python
more_paint_requested = pyqtSignal(int)
less_paint_requested = pyqtSignal(int)
adjustment_released = pyqtSignal()
dial_drag_started = pyqtSignal()
position_dragged = pyqtSignal(int)
position_requested = pyqtSignal(int)
refresh_position_requested = pyqtSignal()
single_cycle_requested = pyqtSignal(float, float, float)
next_section_requested = pyqtSignal(float, float, float)
finish_dropoff_requested = pyqtSignal()
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, parent=None) -> None
```

```python
def setup_ui(self) -> None
```

```python
def set_frame(self, pixmap: QPixmap) -> None
```

```python
def set_waiting_for_camera(self) -> None
```

```python
def resizeEvent(self, event) -> None
```

```python
def set_adjustment_options(self, length: float, axis: float, perpendicular: float) -> None
```

```python
def set_adjustment_status(self, phase: str, travelled: float, total: float) -> None
```

```python
def set_cycle_state(self, state: str, message: str='') -> None
```

```python
def set_cycle_start_pending(self) -> None
```

```python
def set_cycle_start_failed(self) -> None
```

```python
def set_dial_config(self, minimum: int, spacing: int, count: int, enabled: bool) -> None
```

```python
def set_position_pending(self) -> None
```

```python
def set_confirmed_position(self, value: int | None) -> None
```

```python
def set_position_error(self, message: str) -> None
```

```python
def retranslateUi(self) -> None
```

```python
def changeEvent(self, event) -> None
```

```python
def clean_up(self) -> None
```

```python
def set_paint_head_available(self, available: bool) -> None
```

```python
def set_action_pending(self, held_direction: str | None=None, *, keep_dial_enabled: bool=False) -> None
```

```python
def set_action_result(self, value: int, register: int, *, wrote: bool, relative: bool) -> None
```

```python
def set_action_error(self, message: str) -> None
```

## `paint_head_dial.py`

Source: [src/robot_systems/paint/applications/paint_adjustment/view/paint_head_dial.py](../../../../../../src/robot_systems/paint/applications/paint_adjustment/view/paint_head_dial.py).

Imports (including optional/function-local imports; not a startup dependency list): `PyQt6.QtCore`, `PyQt6.QtGui`, `PyQt6.QtWidgets`, `__future__`, `math`, `pl_gui.settings.settings_view.styles`, `src.robot_systems.paint.applications.paint_adjustment.dial_geometry`.

### `PaintHeadDial`

```python
class PaintHeadDial(QWidget):
```

Paint-only visual of evenly spaced presets and register position.

Declared fields/defaults:

```python
drag_started = pyqtSignal()
position_dragged = pyqtSignal(int)
position_requested = pyqtSignal(int)
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, parent=None) -> None
```

```python
def configure(self, minimum: int, spacing: int, count: int) -> None
```

```python
def set_actual(self, value: int | None) -> None
```

```python
def set_preview(self, value: int | None) -> None
```

```python
def cancel_drag(self) -> None
```

```python
def mousePressEvent(self, event) -> None
```

```python
def mouseMoveEvent(self, event) -> None
```

```python
def mouseReleaseEvent(self, event) -> None
```

```python
@property
def actual_value(self) -> int | None
```

```python
@property
def preview_value(self) -> int | None
```

```python
def format_position(self, value: int) -> str
```

Display a register value on the setting scale, to one decimal place.

```python
def paintEvent(self, event) -> None
```
