# Module reference: `src/applications/device_control`

[Package guide](README.md) · [Complete source index](../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [device_control_factory.py](#device_control_factorypy)
- [example_usage.py](#example_usagepy)

## `__init__.py`

Source: [src/applications/device_control/__init__.py](../../../src/applications/device_control/__init__.py).

Imports (including optional/function-local imports; not a startup dependency list): `src.applications.device_control.device_control_factory`, `src.applications.device_control.service.i_device_control_service`.

Package-level import/export surface:

```python
from src.applications.device_control.device_control_factory import DeviceControlFactory
from src.applications.device_control.service.i_device_control_service import IDeviceControlService
```

Module declarations (expressions are shown without evaluating them):

```python
__all__ = ['DeviceControlFactory', 'IDeviceControlService']
```

## `device_control_factory.py`

Source: [src/applications/device_control/device_control_factory.py](../../../src/applications/device_control/device_control_factory.py).

Imports (including optional/function-local imports; not a startup dependency list): `src.applications.base.application_factory`, `src.applications.base.i_application_controller`, `src.applications.base.i_application_model`, `src.applications.base.i_application_view`, `src.applications.device_control.controller.device_control_controller`, `src.applications.device_control.dryer.controller`, `src.applications.device_control.dryer.model`, `src.applications.device_control.dryer.view`, `src.applications.device_control.model.device_control_model`, `src.applications.device_control.service.i_device_control_service`, `src.applications.device_control.view.device_control_view`.

### `DeviceControlFactory`

```python
class DeviceControlFactory(ApplicationFactory):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, dryer_control_service=None, extra_panels=()) -> None
```

## `example_usage.py`

Source: [src/applications/device_control/example_usage.py](../../../src/applications/device_control/example_usage.py).

Imports (including optional/function-local imports; not a startup dependency list): `PyQt6.QtWidgets`, `src.applications.device_control.device_control_factory`, `src.applications.device_control.service.stub_device_control_service`, `sys`.

### `run_standalone`

```python
def run_standalone()
```
