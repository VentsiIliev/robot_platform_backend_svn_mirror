# Module reference: `src/applications/shaft_alignment`

[Package guide](README.md) · [Complete source index](../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [example_usage.py](#example_usagepy)
- [shaft_alignment_application.py](#shaft_alignment_applicationpy)
- [shaft_alignment_factory.py](#shaft_alignment_factorypy)

## `__init__.py`

Source: [src/applications/shaft_alignment/__init__.py](../../../src/applications/shaft_alignment/__init__.py).

Imports (including optional/function-local imports; not a startup dependency list): `src.applications.shaft_alignment.service.i_shaft_alignment_service`, `src.applications.shaft_alignment.shaft_alignment_application`.

Package-level import/export surface:

```python
from src.applications.shaft_alignment.service.i_shaft_alignment_service import IShaftAlignmentService
from src.applications.shaft_alignment.shaft_alignment_application import ShaftAlignmentApplication
```

Module declarations (expressions are shown without evaluating them):

```python
__all__ = ['IShaftAlignmentService', 'ShaftAlignmentApplication']
```

## `example_usage.py`

Source: [src/applications/shaft_alignment/example_usage.py](../../../src/applications/shaft_alignment/example_usage.py).

Imports (including optional/function-local imports; not a startup dependency list): `PyQt6.QtWidgets`, `src.applications.shaft_alignment.service.paint_vision_shaft_alignment_service`, `src.applications.shaft_alignment.shaft_alignment_factory`, `sys`.

### `run_standalone`

```python
def run_standalone() -> None
```

## `shaft_alignment_application.py`

Source: [src/applications/shaft_alignment/shaft_alignment_application.py](../../../src/applications/shaft_alignment/shaft_alignment_application.py).

Imports (including optional/function-local imports; not a startup dependency list): `logging`, `pl_gui.shell.base_app_widget.AppWidget`, `src.applications.base.application_interface`, `src.applications.shaft_alignment.service.i_shaft_alignment_service`, `src.applications.shaft_alignment.shaft_alignment_factory`, `src.engine.core.i_messaging_service`.

### `ShaftAlignmentApplication`

```python
class ShaftAlignmentApplication(IApplication):
```

Optional application entry point; not registered with any robot system.

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, service: IShaftAlignmentService) -> None
```

```python
def register(self, messaging_service: IMessagingService) -> None
```

```python
def create_widget(self) -> AppWidget
```

## `shaft_alignment_factory.py`

Source: [src/applications/shaft_alignment/shaft_alignment_factory.py](../../../src/applications/shaft_alignment/shaft_alignment_factory.py).

Imports (including optional/function-local imports; not a startup dependency list): `src.applications.base.application_factory`, `src.applications.shaft_alignment.controller.shaft_alignment_controller`, `src.applications.shaft_alignment.model.shaft_alignment_model`, `src.applications.shaft_alignment.service.i_shaft_alignment_service`, `src.applications.shaft_alignment.view.shaft_alignment_view`.

### `ShaftAlignmentFactory`

```python
class ShaftAlignmentFactory(ApplicationFactory):
```
