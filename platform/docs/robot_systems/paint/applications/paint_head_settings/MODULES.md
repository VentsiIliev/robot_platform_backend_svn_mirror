# Module reference: `src/robot_systems/paint/applications/paint_head_settings`

[Package guide](README.md) · [Complete source index](../../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [i_paint_head_settings_service.py](#i_paint_head_settings_servicepy)
- [paint_head_settings_controller.py](#paint_head_settings_controllerpy)
- [paint_head_settings_model.py](#paint_head_settings_modelpy)
- [paint_head_settings_service.py](#paint_head_settings_servicepy)
- [paint_head_settings_view.py](#paint_head_settings_viewpy)

## `__init__.py`

Source: [src/robot_systems/paint/applications/paint_head_settings/__init__.py](../../../../../src/robot_systems/paint/applications/paint_head_settings/__init__.py).

Paint-head configuration panel for the Devices app.

No top-level functions, classes or public value declarations; inspect the source for imports or entry-point statements.

## `i_paint_head_settings_service.py`

Source: [src/robot_systems/paint/applications/paint_head_settings/i_paint_head_settings_service.py](../../../../../src/robot_systems/paint/applications/paint_head_settings/i_paint_head_settings_service.py).

Imports (including optional/function-local imports; not a startup dependency list): `abc`, `dataclasses`.

### `PaintHeadSettings`

```python
@dataclass(frozen=True)
class PaintHeadSettings:
```

Declared fields/defaults:

```python
more_paint_sign: int
preset_spacing: int
preset_count: int
min_value: int
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
@property
def max_value(self) -> int
```

### `IPaintHeadSettingsService`

```python
class IPaintHeadSettingsService(ABC):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
@abstractmethod
def load(self) -> PaintHeadSettings
```

```python
@abstractmethod
def save(self, sign: int, spacing: int, count: int) -> PaintHeadSettings
```

## `paint_head_settings_controller.py`

Source: [src/robot_systems/paint/applications/paint_head_settings/paint_head_settings_controller.py](../../../../../src/robot_systems/paint/applications/paint_head_settings/paint_head_settings_controller.py).

Imports (including optional/function-local imports; not a startup dependency list): `.paint_head_settings_model`, `.paint_head_settings_view`, `__future__`, `functools`, `src.applications.base.background_worker`.

### `PaintHeadSettingsController`

```python
class PaintHeadSettingsController(BackgroundWorker):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, model: PaintHeadSettingsModel, view: PaintHeadSettingsView) -> None
```

```python
def load(self) -> None
```

```python
def stop(self) -> None
```

## `paint_head_settings_model.py`

Source: [src/robot_systems/paint/applications/paint_head_settings/paint_head_settings_model.py](../../../../../src/robot_systems/paint/applications/paint_head_settings/paint_head_settings_model.py).

Imports (including optional/function-local imports; not a startup dependency list): `.i_paint_head_settings_service`.

### `PaintHeadSettingsModel`

```python
class PaintHeadSettingsModel:
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, service: IPaintHeadSettingsService) -> None
```

```python
def load(self) -> PaintHeadSettings
```

```python
def save(self, sign: int, spacing: int, count: int) -> PaintHeadSettings
```

## `paint_head_settings_service.py`

Source: [src/robot_systems/paint/applications/paint_head_settings/paint_head_settings_service.py](../../../../../src/robot_systems/paint/applications/paint_head_settings/paint_head_settings_service.py).

Imports (including optional/function-local imports; not a startup dependency list): `.i_paint_head_settings_service`, `__future__`, `dataclasses`, `src.engine.hardware.peripherals`, `src.engine.repositories.interfaces.i_settings_service`, `src.robot_systems.paint.component_ids`.

### `PaintHeadSettingsService`

```python
class PaintHeadSettingsService(IPaintHeadSettingsService):
```

Persist paint-head calibration in the shared settings cache and JSON file.

Declared fields/defaults:

```python
MAX_PRESET_COUNT = 24
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, settings: ISettingsService) -> None
```

```python
def load(self) -> PaintHeadSettings
```

```python
def save(self, sign: int, spacing: int, count: int) -> PaintHeadSettings
```

## `paint_head_settings_view.py`

Source: [src/robot_systems/paint/applications/paint_head_settings/paint_head_settings_view.py](../../../../../src/robot_systems/paint/applications/paint_head_settings/paint_head_settings_view.py).

Imports (including optional/function-local imports; not a startup dependency list): `PyQt6.QtCore`, `PyQt6.QtWidgets`, `__future__`, `pl_gui.settings.settings_view.styles`, `src.applications.base.widgets.keyboard_number_field`.

### `PaintHeadSettingsView`

```python
class PaintHeadSettingsView(QWidget):
```

Declared fields/defaults:

```python
save_requested = pyqtSignal(int, int, int)
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, parent=None) -> None
```

```python
def set_settings(self, sign: int, spacing: int, count: int, minimum: int) -> None
```

```python
def set_busy(self, busy: bool) -> None
```

```python
def set_saved(self, sign: int, spacing: int, count: int, minimum: int) -> None
```

```python
def set_error(self, message: str) -> None
```

```python
def retranslateUi(self) -> None
```

```python
def changeEvent(self, event) -> None
```
