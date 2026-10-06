# Module reference: `src/applications/height_measuring`

[Package guide](README.md) · [Complete source index](../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [example_usage.py](#example_usagepy)
- [height_measuring_factory.py](#height_measuring_factorypy)

## `__init__.py`

Source: [src/applications/height_measuring/__init__.py](../../../src/applications/height_measuring/__init__.py).

Imports (including optional/function-local imports; not a startup dependency list): `src.applications.height_measuring.service.i_height_measuring_app_service`.

Package-level import/export surface:

```python
from src.applications.height_measuring.service.i_height_measuring_app_service import IHeightMeasuringAppService
```

Module declarations (expressions are shown without evaluating them):

```python
__all__ = ['IHeightMeasuringAppService']
```

## `example_usage.py`

Source: [src/applications/height_measuring/example_usage.py](../../../src/applications/height_measuring/example_usage.py).

Imports (including optional/function-local imports; not a startup dependency list): `PyQt6.QtWidgets`, `src.applications.height_measuring.height_measuring_factory`, `src.applications.height_measuring.service.stub_height_measuring_app_service`, `sys`.

### `run_standalone`

```python
def run_standalone()
```

## `height_measuring_factory.py`

Source: [src/applications/height_measuring/height_measuring_factory.py](../../../src/applications/height_measuring/height_measuring_factory.py).

Imports (including optional/function-local imports; not a startup dependency list): `src.applications.base.application_factory`, `src.applications.base.i_application_controller`, `src.applications.height_measuring.controller.height_measuring_controller`, `src.applications.height_measuring.model.height_measuring_model`, `src.applications.height_measuring.service.i_height_measuring_app_service`, `src.applications.height_measuring.view.height_measuring_view`.

### `HeightMeasuringFactory`

```python
class HeightMeasuringFactory(ApplicationFactory):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self)
```

```python
def build(self, service, messaging=None, jog_service=None)
```
