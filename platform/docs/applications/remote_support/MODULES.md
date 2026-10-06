# Module reference: `src/applications/remote_support`

[Package guide](README.md) · [Complete source index](../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [example_usage.py](#example_usagepy)
- [remote_support_application.py](#remote_support_applicationpy)
- [remote_support_application_factory.py](#remote_support_application_factorypy)

## `__init__.py`

Source: [src/applications/remote_support/__init__.py](../../../src/applications/remote_support/__init__.py).

Imports (including optional/function-local imports; not a startup dependency list): `src.applications.remote_support.remote_support_application`, `src.applications.remote_support.service.i_remote_support_service`.

Package-level import/export surface:

```python
from src.applications.remote_support.remote_support_application import RemoteSupportApplication
from src.applications.remote_support.service.i_remote_support_service import IRemoteSupportService
```

Module declarations (expressions are shown without evaluating them):

```python
__all__ = ['RemoteSupportApplication', 'IRemoteSupportService']
```

## `example_usage.py`

Source: [src/applications/remote_support/example_usage.py](../../../src/applications/remote_support/example_usage.py).

Standalone remote-support screen using a hardware-free stub.

Imports (including optional/function-local imports; not a startup dependency list): `PyQt6.QtWidgets`, `pathlib`, `src.applications.remote_support.remote_support_application_factory`, `src.applications.remote_support.service.stub_remote_support_service`, `sys`.

### `run_standalone`

```python
def run_standalone() -> None
```

## `remote_support_application.py`

Source: [src/applications/remote_support/remote_support_application.py](../../../src/applications/remote_support/remote_support_application.py).

Imports (including optional/function-local imports; not a startup dependency list): `.remote_support_application_factory`, `.service.i_remote_support_service`, `src.applications.base.widget_application`.

### `RemoteSupportApplication`

```python
class RemoteSupportApplication(WidgetApplication):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, service: IRemoteSupportService)
```

## `remote_support_application_factory.py`

Source: [src/applications/remote_support/remote_support_application_factory.py](../../../src/applications/remote_support/remote_support_application_factory.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `src.applications.base.application_factory`, `src.applications.base.i_application_controller`, `src.applications.base.i_application_model`, `src.applications.base.i_application_view`, `src.applications.remote_support.controller.remote_support_controller`, `src.applications.remote_support.model.remote_support_model`, `src.applications.remote_support.service.i_remote_support_service`, `src.applications.remote_support.view.remote_support_view`.

### `RemoteSupportApplicationFactory`

```python
class RemoteSupportApplicationFactory(ApplicationFactory):
```
