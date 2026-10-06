# Module reference: `src/applications/glue_cell_settings/controller`

[Package guide](README.md) · [Complete source index](../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [glue_cell_settings_controller.py](#glue_cell_settings_controllerpy)

## `__init__.py`

Source: [src/applications/glue_cell_settings/controller/__init__.py](../../../../src/applications/glue_cell_settings/controller/__init__.py).

No top-level functions, classes or public value declarations; inspect the source for imports or entry-point statements.

## `glue_cell_settings_controller.py`

Source: [src/applications/glue_cell_settings/controller/glue_cell_settings_controller.py](../../../../src/applications/glue_cell_settings/controller/glue_cell_settings_controller.py).

Imports (including optional/function-local imports; not a startup dependency list): `PyQt6.QtCore`, `__future__`, `logging`, `src.applications.base.broker_subscription_mixin`, `src.applications.base.i_application_controller`, `src.applications.glue_cell_settings.model.glue_cell_settings_model`, `src.applications.glue_cell_settings.view.glue_cell_settings_view`, `src.engine.core.i_messaging_service`, `src.shared_contracts.events.weight_events`.

### `_Bridge`

```python
class _Bridge(SignalBridge):
```

Declared fields/defaults:

```python
weight_updated = pyqtSignal(int, float)
state_updated = pyqtSignal(int, str)
```

### `GlueCellSettingsController`

```python
class GlueCellSettingsController(IApplicationController, BrokerSubscriptionMixin):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, model: GlueCellSettingsModel, view: GlueCellSettingsView, broker: IMessagingService)
```

```python
def load(self) -> None
```

```python
def stop(self) -> None
```
