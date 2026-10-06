# Module reference: `src/applications/robot_settings`

[Package guide](README.md) · [Complete source index](../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [robot_settings_application.py](#robot_settings_applicationpy)
- [robot_settings_factory.py](#robot_settings_factorypy)

## `__init__.py`

Source: [src/applications/robot_settings/__init__.py](../../../src/applications/robot_settings/__init__.py).

Imports (including optional/function-local imports; not a startup dependency list): `src.applications.robot_settings.robot_settings_factory`, `src.applications.robot_settings.service.i_robot_settings_service`, `src.applications.robot_settings.service.robot_settings_application_service`.

Package-level import/export surface:

```python
from src.applications.robot_settings.robot_settings_factory import RobotSettingsFactory
from src.applications.robot_settings.service.i_robot_settings_service import IRobotSettingsService
from src.applications.robot_settings.service.robot_settings_application_service import RobotSettingsApplicationService
```

Module declarations (expressions are shown without evaluating them):

```python
__all__ = ['RobotSettingsFactory', 'IRobotSettingsService', 'RobotSettingsApplicationService']
```

## `robot_settings_application.py`

Source: [src/applications/robot_settings/robot_settings_application.py](../../../src/applications/robot_settings/robot_settings_application.py).

Imports (including optional/function-local imports; not a startup dependency list): `logging`, `pl_gui.shell.base_app_widget.AppWidget`, `src.applications.base.application_interface`, `src.applications.robot_settings.robot_settings_factory`, `src.applications.robot_settings.service.robot_settings_application_service`, `src.engine.common_settings_ids`, `src.engine.core.i_messaging_service`, `src.engine.repositories.interfaces.i_settings_service`.

### `RobotSettingsApplication`

```python
class RobotSettingsApplication(IApplication):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, settings_service: ISettingsService)
```

```python
def register(self, messaging_service: IMessagingService) -> None
```

```python
def create_widget(self) -> AppWidget
```

## `robot_settings_factory.py`

Source: [src/applications/robot_settings/robot_settings_factory.py](../../../src/applications/robot_settings/robot_settings_factory.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `src.applications.base.application_factory`, `src.applications.base.i_application_controller`, `src.applications.base.i_application_model`, `src.applications.base.i_application_view`, `src.applications.robot_settings.controller.robot_settings_controller`, `src.applications.robot_settings.model.robot_settings_model`, `src.applications.robot_settings.service.i_robot_settings_service`, `src.applications.robot_settings.view.robot_settings_view`, `src.shared_contracts.declarations`.

### `RobotSettingsFactory`

```python
class RobotSettingsFactory(ApplicationFactory):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, movement_group_definitions: list[MovementGroupDefinition] | None=None)
```

```python
def build(self, service, messaging=None, jog_service=None)
```
