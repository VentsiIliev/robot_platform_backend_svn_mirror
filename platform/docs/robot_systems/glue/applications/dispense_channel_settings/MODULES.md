# Module reference: `src/robot_systems/glue/applications/dispense_channel_settings`

[Package guide](README.md) · [Complete source index](../../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [dispense_channel_settings_application.py](#dispense_channel_settings_applicationpy)
- [dispense_channel_settings_factory.py](#dispense_channel_settings_factorypy)

## `__init__.py`

Source: [src/robot_systems/glue/applications/dispense_channel_settings/__init__.py](../../../../../src/robot_systems/glue/applications/dispense_channel_settings/__init__.py).

Imports (including optional/function-local imports; not a startup dependency list): `src.robot_systems.glue.applications.dispense_channel_settings.dispense_channel_settings_application`, `src.robot_systems.glue.applications.dispense_channel_settings.dispense_channel_settings_factory`, `src.robot_systems.glue.applications.dispense_channel_settings.service.dispense_channel_settings_service`, `src.robot_systems.glue.applications.dispense_channel_settings.service.i_dispense_channel_settings_service`.

Package-level import/export surface:

```python
from src.robot_systems.glue.applications.dispense_channel_settings.dispense_channel_settings_application import DispenseChannelSettingsApplication
from src.robot_systems.glue.applications.dispense_channel_settings.dispense_channel_settings_factory import DispenseChannelSettingsFactory
from src.robot_systems.glue.applications.dispense_channel_settings.service.dispense_channel_settings_service import DispenseChannelSettingsService
from src.robot_systems.glue.applications.dispense_channel_settings.service.i_dispense_channel_settings_service import IDispenseChannelSettingsService
```

Module declarations (expressions are shown without evaluating them):

```python
__all__ = ['DispenseChannelSettingsApplication', 'DispenseChannelSettingsFactory', 'DispenseChannelSettingsService', 'IDispenseChannelSettingsService']
```

## `dispense_channel_settings_application.py`

Source: [src/robot_systems/glue/applications/dispense_channel_settings/dispense_channel_settings_application.py](../../../../../src/robot_systems/glue/applications/dispense_channel_settings/dispense_channel_settings_application.py).

Imports (including optional/function-local imports; not a startup dependency list): `src.applications.base.widget_application`, `src.robot_systems.glue.applications.dispense_channel_settings.dispense_channel_settings_factory`, `src.robot_systems.glue.applications.dispense_channel_settings.service.i_dispense_channel_settings_service`.

### `DispenseChannelSettingsApplication`

```python
class DispenseChannelSettingsApplication(WidgetApplication):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, service: IDispenseChannelSettingsService)
```

## `dispense_channel_settings_factory.py`

Source: [src/robot_systems/glue/applications/dispense_channel_settings/dispense_channel_settings_factory.py](../../../../../src/robot_systems/glue/applications/dispense_channel_settings/dispense_channel_settings_factory.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `logging`, `src.applications.base.application_factory`, `src.engine.core.i_messaging_service`, `src.robot_systems.glue.applications.dispense_channel_settings.controller.dispense_channel_settings_controller`, `src.robot_systems.glue.applications.dispense_channel_settings.model.dispense_channel_settings_model`, `src.robot_systems.glue.applications.dispense_channel_settings.service.i_dispense_channel_settings_service`, `src.robot_systems.glue.applications.dispense_channel_settings.view.dispense_channel_settings_view`.

### `DispenseChannelSettingsFactory`

```python
class DispenseChannelSettingsFactory:
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def build(self, service: IDispenseChannelSettingsService, messaging: IMessagingService, jog_service=None)
```
