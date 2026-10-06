# Module reference: `src/applications/modbus_settings`

[Package guide](README.md) · [Complete source index](../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [example_usage.py](#example_usagepy)
- [modbus_settings_factory.py](#modbus_settings_factorypy)
- [modbus_settings_plugin.py](#modbus_settings_pluginpy)

## `__init__.py`

Source: [src/applications/modbus_settings/__init__.py](../../../src/applications/modbus_settings/__init__.py).

Imports (including optional/function-local imports; not a startup dependency list): `src.applications.modbus_settings.modbus_settings_factory`, `src.applications.modbus_settings.service.i_modbus_settings_service`, `src.applications.modbus_settings.service.modbus_settings_application_service`.

Package-level import/export surface:

```python
from src.applications.modbus_settings.modbus_settings_factory import ModbusSettingsFactory
from src.applications.modbus_settings.service.i_modbus_settings_service import IModbusSettingsService
from src.applications.modbus_settings.service.modbus_settings_application_service import ModbusSettingsApplicationService
```

Module declarations (expressions are shown without evaluating them):

```python
__all__ = ['ModbusSettingsFactory', 'IModbusSettingsService', 'ModbusSettingsApplicationService']
```

## `example_usage.py`

Source: [src/applications/modbus_settings/example_usage.py](../../../src/applications/modbus_settings/example_usage.py).

Imports (including optional/function-local imports; not a startup dependency list): `PyQt6.QtWidgets`, `src.applications.modbus_settings.modbus_settings_factory`, `src.applications.modbus_settings.service.stub_modbus_action_service`, `src.applications.modbus_settings.service.stub_modbus_settings_service`, `sys`.

### `run_standalone`

```python
def run_standalone() -> None
```

## `modbus_settings_factory.py`

Source: [src/applications/modbus_settings/modbus_settings_factory.py](../../../src/applications/modbus_settings/modbus_settings_factory.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `src.applications.base.application_factory`, `src.applications.base.i_application_controller`, `src.applications.base.i_application_model`, `src.applications.base.i_application_view`, `src.applications.modbus_settings.controller.modbus_settings_controller`, `src.applications.modbus_settings.model.modbus_settings_model`, `src.applications.modbus_settings.service.i_modbus_settings_service`, `src.applications.modbus_settings.view.modbus_settings_view`, `src.engine.hardware.communication.modbus.i_modbus_action_service`.

### `ModbusSettingsFactory`

```python
class ModbusSettingsFactory(ApplicationFactory):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def build(self, settings_service: IModbusSettingsService, action_service: IModbusActionService, messaging=None, jog_service=None)
```

Override — two services required instead of one.

## `modbus_settings_plugin.py`

Source: [src/applications/modbus_settings/modbus_settings_plugin.py](../../../src/applications/modbus_settings/modbus_settings_plugin.py).

Imports (including optional/function-local imports; not a startup dependency list): `logging`, `pl_gui.shell.base_app_widget.AppWidget`, `src.applications.base.application_interface`, `src.applications.modbus_settings.modbus_settings_factory`, `src.applications.modbus_settings.service.i_modbus_settings_service`, `src.engine.core.i_messaging_service`, `src.engine.hardware.communication.modbus.i_modbus_action_service`.

### `ModbusSettingsApplication`

```python
class ModbusSettingsApplication(IApplication):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, settings_service: IModbusSettingsService, action_service: IModbusActionService)
```

```python
def register(self, messaging_service: IMessagingService) -> None
```

```python
def create_widget(self) -> AppWidget
```
