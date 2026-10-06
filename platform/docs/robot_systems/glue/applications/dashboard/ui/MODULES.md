# Module reference: `src/robot_systems/glue/applications/dashboard/ui`

[Package guide](README.md) · [Complete source index](../../../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [dashboard_preview_widget.py](#dashboard_preview_widgetpy)
- [glue_change_guide_wizard.py](#glue_change_guide_wizardpy)
- [system_status_widget.py](#system_status_widgetpy)

## `__init__.py`

Source: [src/robot_systems/glue/applications/dashboard/ui/__init__.py](../../../../../../src/robot_systems/glue/applications/dashboard/ui/__init__.py).

No top-level functions, classes or public value declarations; inspect the source for imports or entry-point statements.

## `dashboard_preview_widget.py`

Source: [src/robot_systems/glue/applications/dashboard/ui/dashboard_preview_widget.py](../../../../../../src/robot_systems/glue/applications/dashboard/ui/dashboard_preview_widget.py).

Imports (including optional/function-local imports; not a startup dependency list): `PyQt6.QtCore`, `PyQt6.QtGui`, `PyQt6.QtWidgets`, `__future__`, `cv2`, `enum`, `numpy`, `pl_gui.dashboard.widgets.RobotTrajectoryWidget`, `pl_gui.settings.settings_view.styles`.

### `PreviewDisplayMode`

```python
class PreviewDisplayMode(str, Enum):
```

Declared fields/defaults:

```python
LIVE = 'live'
JOB_PROGRESS = 'job_progress'
```

### `DashboardPreviewWidget`

```python
class DashboardPreviewWidget(QWidget):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, image_width: int=640, image_height: int=360, fps_ms: int=30, trail_length: int=100)
```

```python
def set_image(self, message=None) -> None
```

```python
def set_live_frame(self, message=None) -> None
```

```python
def set_progress_snapshot(self, image, segments: list[dict]) -> None
```

```python
def clear_progress_snapshot(self) -> None
```

```python
def set_progress_state(self, snapshot: dict | None) -> None
```

```python
def set_progress_robot_point(self, point) -> None
```

```python
def set_primary_mode(self, mode: PreviewDisplayMode | str) -> None
```

```python
def set_inset_enabled(self, enabled: bool) -> None
```

```python
def update_trajectory_point(self, message=None) -> None
```

```python
def break_trajectory(self) -> None
```

```python
def enable_drawing(self, _=None) -> None
```

```python
def disable_drawing(self, _=None) -> None
```

```python
def retranslateUi(self) -> None
```

```python
def changeEvent(self, event) -> None
```

## `glue_change_guide_wizard.py`

Source: [src/robot_systems/glue/applications/dashboard/ui/glue_change_guide_wizard.py](../../../../../../src/robot_systems/glue/applications/dashboard/ui/glue_change_guide_wizard.py).

Glue Change Wizard - uses generic wizard framework.

Imports (including optional/function-local imports; not a startup dependency list): `PyQt6.QtWidgets`, `dashboard.ui.wizards`, `pathlib`, `pl_gui.utils.utils_widgets.wizards`, `sys`, `typing`.

### `create_glue_change_wizard`

```python
def create_glue_change_wizard(glue_type_names: Optional[list]=None)
```

Factory function to create a glue change wizard. Args: glue_type_names: List of available glue type names Returns: ConfigurableWizard instance

### `generate_glue_change_summary`

```python
def generate_glue_change_summary(wizard: ConfigurableWizard) -> str
```

Generate HTML summary for glue change wizard.

### `on_glue_change_finished`

```python
def on_glue_change_finished(wizard: ConfigurableWizard)
```

Callback when glue change wizard finishes.

### `main`

```python
def main()
```

Standalone test for glue change wizard.

## `system_status_widget.py`

Source: [src/robot_systems/glue/applications/dashboard/ui/system_status_widget.py](../../../../../../src/robot_systems/glue/applications/dashboard/ui/system_status_widget.py).

Imports (including optional/function-local imports; not a startup dependency list): `PyQt6.QtCore`, `PyQt6.QtWidgets`, `__future__`.

### `SystemStatusWidget`

```python
class SystemStatusWidget(QFrame):
```

Aux-grid panel — shows currently active process and vision_service busy state. Updated via set_process_state() / set_system_state() from the controller. No broker knowledge — pure display widget.

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, parent=None)
```

```python
def set_process_state(self, state: str) -> None
```

```python
def set_active_process(self, process_id: str) -> None
```

```python
def set_system_state(self, state: str) -> None
```

```python
def set_warning(self, message: str) -> None
```

```python
def changeEvent(self, event) -> None
```
