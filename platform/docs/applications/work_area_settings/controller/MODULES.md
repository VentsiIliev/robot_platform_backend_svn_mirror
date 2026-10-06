# Module reference: `src/applications/work_area_settings/controller`

[Package guide](README.md) · [Complete source index](../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [work_area_settings_controller.py](#work_area_settings_controllerpy)

## `__init__.py`

Source: [src/applications/work_area_settings/controller/__init__.py](../../../../src/applications/work_area_settings/controller/__init__.py).

Imports (including optional/function-local imports; not a startup dependency list): `src.applications.work_area_settings.controller.work_area_settings_controller`.

Package-level import/export surface:

```python
from src.applications.work_area_settings.controller.work_area_settings_controller import WorkAreaSettingsController
```

No top-level functions, classes or public value declarations; inspect the source for imports or entry-point statements.

## `work_area_settings_controller.py`

Source: [src/applications/work_area_settings/controller/work_area_settings_controller.py](../../../../src/applications/work_area_settings/controller/work_area_settings_controller.py).

Imports (including optional/function-local imports; not a startup dependency list): `PyQt6.QtCore`, `__future__`, `logging`, `src.applications.base.broker_subscription_mixin`, `src.applications.base.i_application_controller`, `src.applications.work_area_settings.model.work_area_settings_model`, `src.applications.work_area_settings.view.work_area_settings_view`, `src.engine.core.i_messaging_service`, `src.shared_contracts.events.vision_events`.

### `_Bridge`

```python
class _Bridge(SignalBridge):
```

Declared fields/defaults:

```python
camera_frame = pyqtSignal(object)
vision_state = pyqtSignal(str)
```

### `WorkAreaSettingsController`

```python
class WorkAreaSettingsController(IApplicationController, BrokerSubscriptionMixin):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, model: WorkAreaSettingsModel, view: WorkAreaSettingsView, messaging: IMessagingService)
```

```python
def load(self) -> None
```

```python
def stop(self) -> None
```
