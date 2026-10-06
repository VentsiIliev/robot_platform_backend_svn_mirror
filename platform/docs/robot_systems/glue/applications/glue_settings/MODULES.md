# Module reference: `src/robot_systems/glue/applications/glue_settings`

[Package guide](README.md) · [Complete source index](../../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [example_usage.py](#example_usagepy)
- [glue_settings_factory.py](#glue_settings_factorypy)

## `__init__.py`

Source: [src/robot_systems/glue/applications/glue_settings/__init__.py](../../../../../src/robot_systems/glue/applications/glue_settings/__init__.py).

Imports (including optional/function-local imports; not a startup dependency list): `src.robot_systems.glue.applications.glue_settings.glue_settings_factory`, `src.robot_systems.glue.applications.glue_settings.service.glue_settings_application_service`, `src.robot_systems.glue.applications.glue_settings.service.i_glue_settings_service`.

Package-level import/export surface:

```python
from src.robot_systems.glue.applications.glue_settings.service.i_glue_settings_service import IGlueSettingsService
from src.robot_systems.glue.applications.glue_settings.service.glue_settings_application_service import GlueSettingsApplicationService
from src.robot_systems.glue.applications.glue_settings.glue_settings_factory import GlueSettingsFactory
```

Module declarations (expressions are shown without evaluating them):

```python
__all__ = ['GlueSettingsFactory', 'IGlueSettingsService', 'GlueSettingsApplicationService']
```

## `example_usage.py`

Source: [src/robot_systems/glue/applications/glue_settings/example_usage.py](../../../../../src/robot_systems/glue/applications/glue_settings/example_usage.py).

Imports (including optional/function-local imports; not a startup dependency list): `PyQt6.QtWidgets`, `src.robot_systems.glue.applications.glue_settings`, `src.robot_systems.glue.applications.glue_settings.service.stub_glue_settings_service`, `sys`.

### `run_standalone`

```python
def run_standalone() -> None
```

## `glue_settings_factory.py`

Source: [src/robot_systems/glue/applications/glue_settings/glue_settings_factory.py](../../../../../src/robot_systems/glue/applications/glue_settings/glue_settings_factory.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `src.applications.base.application_factory`, `src.applications.base.i_application_controller`, `src.applications.base.i_application_model`, `src.applications.base.i_application_view`, `src.robot_systems.glue.applications.glue_settings.controller.glue_settings_controller`, `src.robot_systems.glue.applications.glue_settings.model.glue_settings_model`, `src.robot_systems.glue.applications.glue_settings.service.i_glue_settings_service`, `src.robot_systems.glue.applications.glue_settings.view.glue_settings_view`.

### `GlueSettingsFactory`

```python
class GlueSettingsFactory(ApplicationFactory):
```
