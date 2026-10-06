# Module reference: `src/applications/network_settings/controller`

[Package guide](README.md) · [Complete source index](../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [network_settings_controller.py](#network_settings_controllerpy)

## `__init__.py`

Source: [src/applications/network_settings/controller/__init__.py](../../../../src/applications/network_settings/controller/__init__.py).

No top-level functions, classes or public value declarations; inspect the source for imports or entry-point statements.

## `network_settings_controller.py`

Source: [src/applications/network_settings/controller/network_settings_controller.py](../../../../src/applications/network_settings/controller/network_settings_controller.py).

Imports (including optional/function-local imports; not a startup dependency list): `PyQt6.QtCore`, `functools`, `src.applications.base.background_worker`, `src.applications.base.i_application_controller`, `src.applications.network_settings.model.network_settings_model`, `src.applications.network_settings.view.network_settings_view`.

### `NetworkSettingsController`

```python
class NetworkSettingsController(IApplicationController, BackgroundWorker):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, model: NetworkSettingsModel, view: NetworkSettingsView) -> None
```

```python
def load(self) -> None
```

```python
def stop(self) -> None
```
