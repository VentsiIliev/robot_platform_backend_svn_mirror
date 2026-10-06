# Module reference: `src/applications/APPLICATION_BLUEPRINT`

[Package guide](README.md) · [Complete source index](../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [example_usage.py](#example_usagepy)
- [my_application.py](#my_applicationpy)
- [my_application_factory.py](#my_application_factorypy)

## `__init__.py`

Source: [src/applications/APPLICATION_BLUEPRINT/__init__.py](../../../src/applications/APPLICATION_BLUEPRINT/__init__.py).

Imports (including optional/function-local imports; not a startup dependency list): `src.applications.APPLICATION_BLUEPRINT.my_application`, `src.applications.APPLICATION_BLUEPRINT.service.i_my_service`.

Package-level import/export surface:

```python
from src.applications.APPLICATION_BLUEPRINT.my_application import MyApplication
from src.applications.APPLICATION_BLUEPRINT.service.i_my_service import IMyService
```

Module declarations (expressions are shown without evaluating them):

```python
__all__ = ['MyApplication', 'IMyService']
```

## `example_usage.py`

Source: [src/applications/APPLICATION_BLUEPRINT/example_usage.py](../../../src/applications/APPLICATION_BLUEPRINT/example_usage.py).

Imports (including optional/function-local imports; not a startup dependency list): `PyQt6.QtWidgets`, `src.applications.APPLICATION_BLUEPRINT.my_application_factory`, `src.applications.APPLICATION_BLUEPRINT.service.stub_my_service`, `sys`.

### `run_standalone`

```python
def run_standalone() -> None
```

## `my_application.py`

Source: [src/applications/APPLICATION_BLUEPRINT/my_application.py](../../../src/applications/APPLICATION_BLUEPRINT/my_application.py).

Imports (including optional/function-local imports; not a startup dependency list): `logging`, `pl_gui.shell.base_app_widget.AppWidget`, `src.applications.APPLICATION_BLUEPRINT.my_application_factory`, `src.applications.APPLICATION_BLUEPRINT.service.my_application_service`, `src.applications.base.application_interface`, `src.engine.core.i_messaging_service`.

### `MyApplication`

```python
class MyApplication(IApplication):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, settings_service=None)
```

```python
def register(self, messaging_service: IMessagingService) -> None
```

```python
def create_widget(self) -> AppWidget
```

## `my_application_factory.py`

Source: [src/applications/APPLICATION_BLUEPRINT/my_application_factory.py](../../../src/applications/APPLICATION_BLUEPRINT/my_application_factory.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `src.applications.APPLICATION_BLUEPRINT.controller.my_controller`, `src.applications.APPLICATION_BLUEPRINT.model.my_model`, `src.applications.APPLICATION_BLUEPRINT.service.i_my_service`, `src.applications.APPLICATION_BLUEPRINT.view.my_view`, `src.applications.base.application_factory`, `src.applications.base.i_application_controller`, `src.applications.base.i_application_model`, `src.applications.base.i_application_view`.

### `MyApplicationFactory`

```python
class MyApplicationFactory(ApplicationFactory):
```
