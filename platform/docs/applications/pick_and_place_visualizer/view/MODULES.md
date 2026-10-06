# Module reference: `src/applications/pick_and_place_visualizer/view`

[Package guide](README.md) · [Complete source index](../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [pick_and_place_visualizer_view.py](#pick_and_place_visualizer_viewpy)
- [plane_canvas.py](#plane_canvaspy)

## `__init__.py`

Source: [src/applications/pick_and_place_visualizer/view/__init__.py](../../../../src/applications/pick_and_place_visualizer/view/__init__.py).

No top-level functions, classes or public value declarations; inspect the source for imports or entry-point statements.

## `pick_and_place_visualizer_view.py`

Source: [src/applications/pick_and_place_visualizer/view/pick_and_place_visualizer_view.py](../../../../src/applications/pick_and_place_visualizer/view/pick_and_place_visualizer_view.py).

Imports (including optional/function-local imports; not a startup dependency list): `PyQt6.QtCore`, `PyQt6.QtGui`, `PyQt6.QtWidgets`, `cv2`, `numpy`, `pl_gui.settings.settings_view.styles`, `src.applications.base.app_styles`, `src.applications.base.i_application_view`, `src.applications.pick_and_place_visualizer.service.i_pick_and_place_visualizer_service`, `src.applications.pick_and_place_visualizer.view.plane_canvas`, `typing`.

### `PickAndPlaceVisualizerView`

```python
class PickAndPlaceVisualizerView(IApplicationView):
```

Declared fields/defaults:

```python
SHOW_JOG_WIDGET = True
JOG_FRAME_SELECTOR_ENABLED = True
simulation_toggled = pyqtSignal(bool)
step_mode_toggled = pyqtSignal(bool)
start_process_requested = pyqtSignal()
stop_process_requested = pyqtSignal()
pause_process_requested = pyqtSignal()
reset_process_requested = pyqtSignal()
step_process_requested = pyqtSignal()
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
def set_matched_items(self, items: List[MatchedItem]) -> None
```

```python
def set_simulation_result(self, result: SimResult) -> None
```

```python
def set_plane_bounds(self, x_min, x_max, y_min, y_max, spacing) -> None
```

```python
def set_process_state(self, state: str) -> None
```

```python
def set_step_mode(self, enabled: bool) -> None
```

```python
def set_step_status(self, checkpoint: Optional[str], waiting: bool, step_budget: int, current_workpiece: Optional[str]=None) -> None
```

```python
def add_placed_item(self, item) -> None
```

```python
def reset_plane(self) -> None
```

```python
def append_log(self, text: str) -> None
```

```python
def set_busy(self, busy: bool) -> None
```

```python
def clean_up(self) -> None
```

## `plane_canvas.py`

Source: [src/applications/pick_and_place_visualizer/view/plane_canvas.py](../../../../src/applications/pick_and_place_visualizer/view/plane_canvas.py).

Imports (including optional/function-local imports; not a startup dependency list): `PyQt6.QtCore`, `PyQt6.QtGui`, `PyQt6.QtWidgets`, `src.applications.pick_and_place_visualizer.service.i_pick_and_place_visualizer_service`, `typing`.

### `PlaneCanvas`

```python
class PlaneCanvas(QWidget):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, parent=None)
```

```python
def set_bounds(self, x_min: float, x_max: float, y_min: float, y_max: float, spacing: float) -> None
```

```python
def set_placed(self, items: List[PlacedItem]) -> None
```

```python
def clear(self) -> None
```

```python
def add_item(self, item) -> None
```

```python
def paintEvent(self, _event) -> None
```
