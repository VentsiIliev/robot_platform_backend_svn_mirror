# Module reference: `src/robot_systems/paint/applications/paint_motion_plane_setup/view`

[Package guide](README.md) · [Complete source index](../../../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [paint_motion_plane_setup_view.py](#paint_motion_plane_setup_viewpy)

## `paint_motion_plane_setup_view.py`

Source: [src/robot_systems/paint/applications/paint_motion_plane_setup/view/paint_motion_plane_setup_view.py](../../../../../../src/robot_systems/paint/applications/paint_motion_plane_setup/view/paint_motion_plane_setup_view.py).

Imports (including optional/function-local imports; not a startup dependency list): `PyQt6.QtCore`, `PyQt6.QtGui`, `PyQt6.QtWidgets`, `__future__`, `json`, `math`, `pl_gui.settings.settings_view.styles`, `src.applications.base.i_application_view`, `src.applications.base.styled_message_box`, `src.robot_systems.paint.applications.paint_motion_plane_setup.domain.plane_inference`.

### `_t`

```python
def _t(text: str) -> str
```

### `_pose_text`

```python
def _pose_text(pose: Pose6D | None) -> str
```

### `_button`

```python
def _button(text: str, *, primary: bool=True) -> QPushButton
```

### `_PoseReadout`

```python
class _PoseReadout(QFrame):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, label: str) -> None
```

```python
def set_pose(self, pose: Pose6D | None) -> None
```

### `_GuideIllustration`

```python
class _GuideIllustration(QWidget):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, mode: str) -> None
```

```python
def sizeHint(self) -> QSize
```

```python
def set_selected_axis(self, axis: str | None, delta: float=0.0) -> None
```

```python
def paintEvent(self, _event) -> None
```

### `_WizardPage`

```python
class _WizardPage(QWizardPage):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, title: str, help_text: str) -> None
```

```python
@property
def content_layout(self) -> QVBoxLayout
```

```python
def set_complete(self, complete: bool) -> None
```

```python
def isComplete(self) -> bool
```

### `_ResultPage`

```python
class _ResultPage(_WizardPage):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self) -> None
```

### `PaintMotionPlaneSetupView`

```python
class PaintMotionPlaneSetupView(IApplicationView):
```

Declared fields/defaults:

```python
SHOW_JOG_WIDGET = True
JOG_FRAME_SELECTOR_ENABLED = True
JOG_DRAWER_WIDTH = 330
move_to_paint_pose_requested = pyqtSignal()
paint_group_selected = pyqtSignal(str)
capture_reference_requested = pyqtSignal()
capture_translation_requested = pyqtSignal()
capture_rotation_requested = pyqtSignal()
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self) -> None
```

```python
def setup_ui(self) -> None
```

```python
def clean_up(self) -> None
```

```python
def set_jog_position(self, pos: list) -> None
```

```python
def set_current_pose(self, pose: Pose6D | None) -> None
```

```python
def set_paint_pose(self, pose: Pose6D | None) -> None
```

```python
def set_paint_groups(self, group_ids: list[str], selected_group_id: str='') -> None
```

```python
def set_paint_move_complete(self, complete: bool) -> None
```

```python
def set_reference_pose(self, pose: Pose6D | None) -> None
```

```python
def set_translation_pose(self, pose: Pose6D | None) -> None
```

```python
def set_rotation_pose(self, pose: Pose6D | None) -> None
```

```python
def set_result(self, result: dict | None, warnings: tuple[str, ...]=(), paint_plane_config: dict | None=None) -> None
```

```python
def set_busy(self, busy: bool, message: str='') -> None
```

```python
def show_error(self, title: str, message: str) -> None
```

```python
def confirm_move_to_paint_pose(self) -> bool
```
