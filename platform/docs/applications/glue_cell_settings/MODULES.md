# Module reference: `src/applications/glue_cell_settings`

[Package guide](README.md) · [Complete source index](../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [example_usage.py](#example_usagepy)
- [glue_cell_settings_application.py](#glue_cell_settings_applicationpy)
- [glue_cell_settings_factory.py](#glue_cell_settings_factorypy)

## `__init__.py`

Source: [src/applications/glue_cell_settings/__init__.py](../../../src/applications/glue_cell_settings/__init__.py).

Imports (including optional/function-local imports; not a startup dependency list): `src.applications.glue_cell_settings.glue_cell_settings_factory`, `src.applications.glue_cell_settings.service.glue_cell_settings_service`.

Package-level import/export surface:

```python
from src.applications.glue_cell_settings.glue_cell_settings_factory import GlueCellSettingsFactory
from src.applications.glue_cell_settings.service.glue_cell_settings_service import GlueCellSettingsService
```

Module declarations (expressions are shown without evaluating them):

```python
__all__ = ['GlueCellSettingsFactory', 'GlueCellSettingsService']
```

## `example_usage.py`

Source: [src/applications/glue_cell_settings/example_usage.py](../../../src/applications/glue_cell_settings/example_usage.py).

No top-level functions, classes or public value declarations; inspect the source for imports or entry-point statements.

## `glue_cell_settings_application.py`

Source: [src/applications/glue_cell_settings/glue_cell_settings_application.py](../../../src/applications/glue_cell_settings/glue_cell_settings_application.py).

Imports (including optional/function-local imports; not a startup dependency list): `src.applications.base.widget_application`, `src.applications.glue_cell_settings.glue_cell_settings_factory`, `src.applications.glue_cell_settings.service.i_glue_cell_settings_service`, `src.engine.core.i_messaging_service`.

### `GlueCellSettingsApplication`

```python
class GlueCellSettingsApplication(WidgetApplication):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, service: IGlueCellSettingsService)
```

## `glue_cell_settings_factory.py`

Source: [src/applications/glue_cell_settings/glue_cell_settings_factory.py](../../../src/applications/glue_cell_settings/glue_cell_settings_factory.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `logging`, `src.applications.base.application_factory`, `src.applications.base.i_application_controller`, `src.applications.base.i_application_model`, `src.applications.base.i_application_view`, `src.applications.glue_cell_settings.controller.glue_cell_settings_controller`, `src.applications.glue_cell_settings.model.glue_cell_settings_model`, `src.applications.glue_cell_settings.service.i_glue_cell_settings_service`, `src.applications.glue_cell_settings.view.glue_cell_settings_view`, `src.engine.core.i_messaging_service`.

### `GlueCellSettingsFactory`

```python
class GlueCellSettingsFactory:
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def build(self, service: IGlueCellSettingsService, messaging: IMessagingService, jog_service=None)
```
