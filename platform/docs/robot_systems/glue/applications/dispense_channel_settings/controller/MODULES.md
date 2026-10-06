# Module reference: `src/robot_systems/glue/applications/dispense_channel_settings/controller`

[Package guide](README.md) · [Complete source index](../../../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [dispense_channel_settings_controller.py](#dispense_channel_settings_controllerpy)

## `dispense_channel_settings_controller.py`

Source: [src/robot_systems/glue/applications/dispense_channel_settings/controller/dispense_channel_settings_controller.py](../../../../../../src/robot_systems/glue/applications/dispense_channel_settings/controller/dispense_channel_settings_controller.py).

Imports (including optional/function-local imports; not a startup dependency list): `PyQt6.QtCore`, `__future__`, `logging`, `src.applications.base.broker_subscription_mixin`, `src.applications.base.i_application_controller`, `src.engine.core.i_messaging_service`, `src.robot_systems.glue.applications.dispense_channel_settings.model.dispense_channel_settings_model`, `src.robot_systems.glue.applications.dispense_channel_settings.view.dispense_channel_settings_view`, `src.shared_contracts.events.weight_events`.

### `_Bridge`

```python
class _Bridge(SignalBridge):
```

Declared fields/defaults:

```python
weight_updated = pyqtSignal(str, float)
state_updated = pyqtSignal(str, str)
```

### `DispenseChannelSettingsController`

```python
class DispenseChannelSettingsController(IApplicationController, BrokerSubscriptionMixin):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, model: DispenseChannelSettingsModel, view: DispenseChannelSettingsView, broker: IMessagingService)
```

```python
def load(self) -> None
```

```python
def stop(self) -> None
```
