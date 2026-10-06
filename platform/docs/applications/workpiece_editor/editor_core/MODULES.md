# Module reference: `src/applications/workpiece_editor/editor_core`

[Package guide](README.md) · [Complete source index](../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [_version.py](#_versionpy)
- [builder.py](#builderpy)

## `__init__.py`

Source: [src/applications/workpiece_editor/editor_core/__init__.py](../../../../src/applications/workpiece_editor/editor_core/__init__.py).

Workpiece Editor Package Adds workpiece-specific functionality on top of the domain-agnostic contour_editor. This package handles workpiece data models, transformation adapters, and workpiece-aware handlers. Public API for workpiece-specific applications: - WorkpieceEditorBuilder: Builder that wraps ContourEditorBuilder with workpiece support - IWorkpieceDataAdapter: adapter contract implemented by each robot system - WorkpieceAdapter: legacy compatibility adapter - WorkpieceManager: Manage workpiece loading/exporting - Handlers: SaveWorkpieceHandler, CaptureDataHandler, load_workpiece - Models: BaseWorkpiece, GenericWorkpiece, WorkpieceFactory, WorkpieceField

Imports (including optional/function-local imports; not a startup dependency list): `._version`, `.adapters`, `.builder`, `.handlers`, `.managers`, `.models`, `contour_editor`.

Package-level import/export surface:

```python
from .builder import WorkpieceEditorBuilder
from .adapters import IWorkpieceDataAdapter
from .managers import WorkpieceManager
from .handlers import SaveWorkpieceHandler, CaptureDataHandler, StartHandler, CaptureHandler
from .models import BaseWorkpiece, GenericWorkpiece, WorkpieceFactory, WorkpieceField
from contour_editor import ContourEditorData, Segment, Layer, ISegmentManager, ISettingsProvider, BezierSegmentManager, SettingsConfig, SettingsGroup, MainApplicationFrame
from ._version import __version__, __version_info__
```

Module declarations (expressions are shown without evaluating them):

```python
__all__ = ['WorkpieceEditorBuilder', 'IWorkpieceDataAdapter', 'WorkpieceAdapter', 'WorkpieceManager', 'SaveWorkpieceHandler', 'CaptureDataHandler', 'StartHandler', 'CaptureHandler', 'BaseWorkpiece', 'GenericWorkpiece', 'WorkpieceFactory', 'WorkpieceField', 'ContourEditorData', 'Segment', 'Layer', 'ISegmentManager', 'ISettingsProvider', 'BezierSegmentManager', 'SettingsConfig', 'SettingsGroup', 'MainApplicationFrame']
```

### `__getattr__`

```python
def __getattr__(name)
```

## `_version.py`

Source: [src/applications/workpiece_editor/editor_core/_version.py](../../../../src/applications/workpiece_editor/editor_core/_version.py).

No top-level functions, classes or public value declarations; inspect the source for imports or entry-point statements.

## `builder.py`

Source: [src/applications/workpiece_editor/editor_core/builder.py](../../../../src/applications/workpiece_editor/editor_core/builder.py).

Workpiece Editor Builder Wraps ContourEditorBuilder and adds workpiece-specific functionality. This builder automatically configures workpiece-specific handlers, adapters, and managers.

Imports (including optional/function-local imports; not a startup dependency list): `.adapters.i_workpiece_data_adapter`, `.handlers`, `.managers.workpiece_manager`, `contour_editor`, `contour_editor.core.main_frame`, `typing`.

### `WorkpieceEditorBuilder`

```python
class WorkpieceEditorBuilder:
```

Builder for configuring and creating a workpiece-aware ContourEditor instance. This builder wraps ContourEditorBuilder and automatically injects workpiece-specific dependencies (WorkpieceAdapter, WorkpieceManager, handlers). Example: editor = (WorkpieceEditorBuilder() .with_segment_manager(MySegmentManager) .with_settings(my_config, my_provider) .with_form(my_form_factory) .on_save_workpiece(my_save_handler) .on_capture_workpiece(my_capture_handler) .build())

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self)
```

```python
def with_parent(self, parent)
```

Set parent widget

```python
def with_segment_manager(self, manager_class)
```

Configure segment manager backend (REQUIRED)

```python
def with_settings(self, config, provider=None)
```

```python
def with_layer_config(self, layer_config)
```

```python
def with_ui_config(self, ui_config)
```

```python
def with_form(self, form_factory)
```

Configure workpiece form (optional)

```python
def with_widgets(self, widget_factory)
```

Configure custom widgets (optional)

```python
def with_workpiece_data_adapter(self, adapter: IWorkpieceDataAdapter)
```

```python
def on_save(self, callback: Callable[[dict], None])
```

Set callback for save events. Callback receives merged form data + workpiece contour data.

```python
def on_capture(self, callback: Callable[[], None])
```

Set callback for capture events

```python
def on_execute(self, callback: Callable[[Any], None])
```

Set callback for execute events

```python
def on_custom_action(self, callback: Callable[[str], None])
```

```python
def on_update_camera_feed(self, callback: Callable[[], None])
```

Set callback for camera feed update events

```python
def build(self) -> MainApplicationFrame
```

Build and return configured editor instance with workpiece support

```python
def load_workpiece(self, workpiece)
```

Load a workpiece into the editor. Must be called after build().

```python
def export_workpiece_data(self) -> dict
```

Export current editor state as workpiece-compatible data. Must be called after build().

```python
def get_workpiece_manager(self) -> Optional[WorkpieceManager]
```

Get the WorkpieceManager instance (available after build())
