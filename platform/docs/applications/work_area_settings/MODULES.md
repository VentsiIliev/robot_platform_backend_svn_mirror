# Module reference: `src/applications/work_area_settings`

[Package guide](README.md) · [Complete source index](../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [example_usage.py](#example_usagepy)
- [work_area_settings_application.py](#work_area_settings_applicationpy)
- [work_area_settings_factory.py](#work_area_settings_factorypy)

## `__init__.py`

Source: [src/applications/work_area_settings/__init__.py](../../../src/applications/work_area_settings/__init__.py).

Imports (including optional/function-local imports; not a startup dependency list): `src.applications.work_area_settings.service.i_work_area_settings_service`, `src.applications.work_area_settings.service.stub_work_area_settings_service`, `src.applications.work_area_settings.work_area_settings_factory`.

Package-level import/export surface:

```python
from src.applications.work_area_settings.service.i_work_area_settings_service import IWorkAreaSettingsService
from src.applications.work_area_settings.service.stub_work_area_settings_service import StubWorkAreaSettingsService
from src.applications.work_area_settings.work_area_settings_factory import WorkAreaSettingsFactory
```

No top-level functions, classes or public value declarations; inspect the source for imports or entry-point statements.

## `example_usage.py`

Source: [src/applications/work_area_settings/example_usage.py](../../../src/applications/work_area_settings/example_usage.py).

Imports (including optional/function-local imports; not a startup dependency list): `PyQt6.QtWidgets`, `src.applications.work_area_settings`, `src.engine.core.messaging_service`, `src.shared_contracts.declarations`, `sys`.

### `run_standalone`

```python
def run_standalone()
```

## `work_area_settings_application.py`

Source: [src/applications/work_area_settings/work_area_settings_application.py](../../../src/applications/work_area_settings/work_area_settings_application.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `src.applications.base.widget_application`.

### `WorkAreaSettingsApplication`

```python
class WorkAreaSettingsApplication(WidgetApplication):
```

## `work_area_settings_factory.py`

Source: [src/applications/work_area_settings/work_area_settings_factory.py](../../../src/applications/work_area_settings/work_area_settings_factory.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `src.applications.base.application_factory`, `src.applications.base.i_application_controller`, `src.applications.base.i_application_model`, `src.applications.base.i_application_view`, `src.applications.work_area_settings.controller.work_area_settings_controller`, `src.applications.work_area_settings.model.work_area_settings_model`, `src.applications.work_area_settings.service.i_work_area_settings_service`, `src.applications.work_area_settings.view.work_area_settings_view`, `src.shared_contracts.declarations`.

### `WorkAreaSettingsFactory`

```python
class WorkAreaSettingsFactory(ApplicationFactory):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, work_area_definitions: list[WorkAreaDefinition] | None=None)
```

```python
def build(self, service, messaging=None, jog_service=None)
```
