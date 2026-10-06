# Module reference: `src/applications/network_settings`

[Package guide](README.md) · [Complete source index](../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [build_application.py](#build_applicationpy)
- [example_usage.py](#example_usagepy)
- [network_settings_factory.py](#network_settings_factorypy)

## `__init__.py`

Source: [src/applications/network_settings/__init__.py](../../../src/applications/network_settings/__init__.py).

Imports (including optional/function-local imports; not a startup dependency list): `.network_settings_factory`, `.service.i_network_settings_service`, `.service.network_settings_service`.

Package-level import/export surface:

```python
from .network_settings_factory import NetworkSettingsFactory
from .service.i_network_settings_service import INetworkSettingsService
from .service.network_settings_service import NetworkSettingsService
```

Module declarations (expressions are shown without evaluating them):

```python
__all__ = ['NetworkSettingsFactory', 'INetworkSettingsService', 'NetworkSettingsService']
```

## `build_application.py`

Source: [src/applications/network_settings/build_application.py](../../../src/applications/network_settings/build_application.py).

Reusable shell wiring for every robot system.

Imports (including optional/function-local imports; not a startup dependency list): `.network_settings_factory`, `.service.network_settings_service`, `src.applications.base.widget_application`.

### `build_network_settings_application`

```python
def build_network_settings_application(_robot_system, *, show_remote_support: bool=True)
```

## `example_usage.py`

Source: [src/applications/network_settings/example_usage.py](../../../src/applications/network_settings/example_usage.py).

Run Network Settings with an in-memory adapter, without changing host networking.

Imports (including optional/function-local imports; not a startup dependency list): `PyQt6.QtWidgets`, `src.applications.network_settings.network_settings_factory`, `src.applications.network_settings.service.stub_network_settings_service`, `sys`.

### `run_standalone`

```python
def run_standalone() -> None
```

## `network_settings_factory.py`

Source: [src/applications/network_settings/network_settings_factory.py](../../../src/applications/network_settings/network_settings_factory.py).

Imports (including optional/function-local imports; not a startup dependency list): `src.applications.base.application_factory`, `src.applications.network_settings.controller.network_settings_controller`, `src.applications.network_settings.model.network_settings_model`, `src.applications.network_settings.view.network_settings_view`.

### `NetworkSettingsFactory`

```python
class NetworkSettingsFactory(ApplicationFactory):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, *, show_remote_support: bool=True)
```
