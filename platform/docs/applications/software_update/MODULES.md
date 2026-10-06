# Module reference: `src/applications/software_update`

[Package guide](README.md) · [Complete source index](../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [build_application.py](#build_applicationpy)
- [example_usage.py](#example_usagepy)
- [software_update_application.py](#software_update_applicationpy)
- [software_update_factory.py](#software_update_factorypy)

## `__init__.py`

Source: [src/applications/software_update/__init__.py](../../../src/applications/software_update/__init__.py).

Imports (including optional/function-local imports; not a startup dependency list): `.service.i_software_update_service`, `.software_update_application`.

Package-level import/export surface:

```python
from .software_update_application import SoftwareUpdateApplication
from .service.i_software_update_service import ISoftwareUpdateService
```

Module declarations (expressions are shown without evaluating them):

```python
__all__ = ['SoftwareUpdateApplication', 'ISoftwareUpdateService']
```

## `build_application.py`

Source: [src/applications/software_update/build_application.py](../../../src/applications/software_update/build_application.py).

Shared application composition; each system supplies its maintenance gate.

Imports (including optional/function-local imports; not a startup dependency list): `.service.software_update_service`, `.software_update_application`.

### `build_software_update_application`

```python
def build_software_update_application(can_schedule)
```

## `example_usage.py`

Source: [src/applications/software_update/example_usage.py](../../../src/applications/software_update/example_usage.py).

Imports (including optional/function-local imports; not a startup dependency list): `PyQt6.QtWidgets`, `pathlib`, `src.applications.software_update`, `src.applications.software_update.service.stub_software_update_service`, `src.applications.software_update.software_update_factory`, `sys`.

### `run_standalone`

```python
def run_standalone()
```

## `software_update_application.py`

Source: [src/applications/software_update/software_update_application.py](../../../src/applications/software_update/software_update_application.py).

Imports (including optional/function-local imports; not a startup dependency list): `.software_update_factory`, `src.applications.base.widget_application`.

### `SoftwareUpdateApplication`

```python
class SoftwareUpdateApplication(WidgetApplication):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, service)
```

## `software_update_factory.py`

Source: [src/applications/software_update/software_update_factory.py](../../../src/applications/software_update/software_update_factory.py).

Imports (including optional/function-local imports; not a startup dependency list): `.controller.software_update_controller`, `.model.software_update_model`, `.view.software_update_view`, `src.applications.base.application_factory`.

### `SoftwareUpdateFactory`

```python
class SoftwareUpdateFactory(ApplicationFactory):
```
