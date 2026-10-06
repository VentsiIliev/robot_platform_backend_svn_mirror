# Module reference: `src/applications/work_area_settings/view`

[Package guide](README.md) · [Complete source index](../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [work_area_settings_view.py](#work_area_settings_viewpy)

## `__init__.py`

Source: [src/applications/work_area_settings/view/__init__.py](../../../../src/applications/work_area_settings/view/__init__.py).

Imports (including optional/function-local imports; not a startup dependency list): `src.applications.work_area_settings.view.work_area_settings_view`.

Package-level import/export surface:

```python
from src.applications.work_area_settings.view.work_area_settings_view import WorkAreaSettingsView
```

No top-level functions, classes or public value declarations; inspect the source for imports or entry-point statements.

## `work_area_settings_view.py`

Source: [src/applications/work_area_settings/view/work_area_settings_view.py](../../../../src/applications/work_area_settings/view/work_area_settings_view.py).

Imports (including optional/function-local imports; not a startup dependency list): `PyQt6.QtCore`, `PyQt6.QtGui`, `PyQt6.QtWidgets`, `__future__`, `cv2`, `html`, `pl_gui.settings.settings_view.styles`, `pl_gui.utils.utils_widgets.camera_view`, `src.applications.base.i_application_view`, `src.shared_contracts.declarations`.

### `WorkAreaSettingsView`

```python
class WorkAreaSettingsView(IApplicationView):
```

Declared fields/defaults:

```python
SHOW_JOG_WIDGET = True
JOG_FRAME_SELECTOR_ENABLED = True
work_area_changed = pyqtSignal(str)
save_area_requested = pyqtSignal(str)
vision_state_changed = pyqtSignal(str)
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, work_area_definitions: list[WorkAreaDefinition] | None=None, parent=None)
```

```python
def setup_ui(self) -> None
```

```python
def set_work_area_options(self, definitions: list[WorkAreaDefinition]) -> None
```

```python
def set_current_work_area_id(self, area_id: str) -> None
```

```python
def current_work_area_id(self) -> str
```

```python
def current_work_area_definition(self) -> WorkAreaDefinition | None
```

```python
@property
def work_area_definitions(self) -> list[WorkAreaDefinition]
```

```python
def set_active_area_key(self, area_key: str) -> None
```

```python
def set_vision_state(self, state: str) -> None
```

```python
def update_camera_view(self, image) -> None
```

```python
def set_area_corners(self, area_name: str, normalized_points: list) -> None
```

```python
def mark_area_saved(self, area_name: str) -> None
```

```python
def get_area_corners(self, area_name: str) -> list
```

```python
@property
def preview_label(self) -> CameraView
```

```python
def retranslateUi(self) -> None
```

```python
def changeEvent(self, event) -> None
```
