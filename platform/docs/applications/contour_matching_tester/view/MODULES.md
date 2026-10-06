# Module reference: `src/applications/contour_matching_tester/view`

[Package guide](README.md) · [Complete source index](../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [contour_matching_tester_view.py](#contour_matching_tester_viewpy)

## `__init__.py`

Source: [src/applications/contour_matching_tester/view/__init__.py](../../../../src/applications/contour_matching_tester/view/__init__.py).

No top-level functions, classes or public value declarations; inspect the source for imports or entry-point statements.

## `contour_matching_tester_view.py`

Source: [src/applications/contour_matching_tester/view/contour_matching_tester_view.py](../../../../src/applications/contour_matching_tester/view/contour_matching_tester_view.py).

Imports (including optional/function-local imports; not a startup dependency list): `PyQt6.QtCore`, `PyQt6.QtGui`, `PyQt6.QtWidgets`, `cv2`, `numpy`, `pl_gui.settings.settings_view.styles`, `pl_gui.utils.utils_widgets.camera_view`, `pl_gui.utils.utils_widgets.table_helpers`, `src.applications.base.app_styles`, `src.applications.base.i_application_view`, `typing`.

### `ContourMatchingTesterView`

```python
class ContourMatchingTesterView(IApplicationView):
```

Declared fields/defaults:

```python
SHOW_JOG_WIDGET = True
JOG_FRAME_SELECTOR_ENABLED = True
load_workpieces_requested = pyqtSignal()
match_requested = pyqtSignal()
capture_requested = pyqtSignal()
workpiece_selected = pyqtSignal(int)
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, parent=None)
```

```python
def setup_ui(self) -> None
```

```python
def update_camera_view(self, image: np.ndarray) -> None
```

```python
def set_capture_state(self, captured: bool) -> None
```

```python
def set_workpieces(self, workpieces: list) -> None
```

```python
def set_selected_workpiece(self, row: int) -> None
```

```python
def clear_match_results(self) -> None
```

```python
def show_thumbnail(self, name: str, thumbnail_bytes: Optional[bytes]) -> None
```

```python
def set_match_results(self, results: dict, no_match_count: int) -> None
```

```python
def set_matching_busy(self, busy: bool) -> None
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
