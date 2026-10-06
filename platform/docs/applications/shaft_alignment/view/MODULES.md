# Module reference: `src/applications/shaft_alignment/view`

[Package guide](README.md) · [Complete source index](../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [shaft_alignment_view.py](#shaft_alignment_viewpy)

## `__init__.py`

Source: [src/applications/shaft_alignment/view/__init__.py](../../../../src/applications/shaft_alignment/view/__init__.py).

Imports (including optional/function-local imports; not a startup dependency list): `src.applications.shaft_alignment.view.shaft_alignment_view`.

Package-level import/export surface:

```python
from src.applications.shaft_alignment.view.shaft_alignment_view import ShaftAlignmentView
```

Module declarations (expressions are shown without evaluating them):

```python
__all__ = ['ShaftAlignmentView']
```

## `shaft_alignment_view.py`

Source: [src/applications/shaft_alignment/view/shaft_alignment_view.py](../../../../src/applications/shaft_alignment/view/shaft_alignment_view.py).

Imports (including optional/function-local imports; not a startup dependency list): `PyQt6.QtCore`, `PyQt6.QtGui`, `PyQt6.QtWidgets`, `__future__`, `dataclasses`, `numpy`, `pl_gui.settings.settings_view.styles`, `src.applications.base.i_application_view`, `src.applications.base.widgets.custom_virtual_keyboard`, `src.applications.shaft_alignment.service.i_shaft_alignment_service`, `src.applications.shaft_alignment.settings.shaft_alignment_settings`.

### `_CameraCanvas`

```python
class _CameraCanvas(QLabel):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self) -> None
```

```python
def set_frame(self, frame, corners, reference_corners, point_of_interest, misaligned: bool, detection_region=None, correction=None) -> None
```

```python
def paintEvent(self, event) -> None
```

### `ShaftAlignmentView`

```python
class ShaftAlignmentView(IApplicationView):
```

Declared fields/defaults:

```python
SHOW_JOG_WIDGET = True
capture_reference_requested = pyqtSignal(int)
thresholds_changed = pyqtSignal(float, float, float, float, float)
save_settings_requested = pyqtSignal(object)
check_alignment_requested = pyqtSignal()
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, parent=None) -> None
```

```python
def setup_ui(self) -> None
```

```python
def threshold_values(self) -> tuple[float, float, float, float, float]
```

```python
def set_settings(self, settings: ShaftAlignmentSettings) -> None
```

```python
def settings_values(self) -> ShaftAlignmentSettings
```

```python
def set_persisted_settings(self, settings: ShaftAlignmentSettings) -> None
```

Refresh hidden runtime state without disturbing editable controls.

```python
def set_snapshot(self, snapshot: AlignmentSnapshot) -> None
```

```python
def set_error(self, message: str) -> None
```

```python
def retranslateUi(self) -> None
```

```python
def clean_up(self) -> None
```

```python
def show_settings_saved(self) -> None
```

```python
def set_settings_error(self, message: str) -> None
```

```python
def show_alignment_check(self, aligned: bool) -> None
```
