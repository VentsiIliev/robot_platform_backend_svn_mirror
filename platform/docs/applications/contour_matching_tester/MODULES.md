# Module reference: `src/applications/contour_matching_tester`

[Package guide](README.md) · [Complete source index](../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [contour_matching_tester_application.py](#contour_matching_tester_applicationpy)
- [contour_matching_tester_factory.py](#contour_matching_tester_factorypy)
- [example_usage.py](#example_usagepy)

## `__init__.py`

Source: [src/applications/contour_matching_tester/__init__.py](../../../src/applications/contour_matching_tester/__init__.py).

Imports (including optional/function-local imports; not a startup dependency list): `src.applications.contour_matching_tester.contour_matching_tester_factory`, `src.applications.contour_matching_tester.service.i_contour_matching_tester_service`.

Package-level import/export surface:

```python
from src.applications.contour_matching_tester.contour_matching_tester_factory import ContourMatchingTesterFactory
from src.applications.contour_matching_tester.service.i_contour_matching_tester_service import IContourMatchingTesterService
```

Module declarations (expressions are shown without evaluating them):

```python
__all__ = ['ContourMatchingTesterFactory', 'IContourMatchingTesterService']
```

## `contour_matching_tester_application.py`

Source: [src/applications/contour_matching_tester/contour_matching_tester_application.py](../../../src/applications/contour_matching_tester/contour_matching_tester_application.py).

Imports (including optional/function-local imports; not a startup dependency list): `logging`, `pl_gui.shell.base_app_widget.AppWidget`, `src.applications.base.application_interface`, `src.applications.contour_matching_tester.contour_matching_tester_factory`, `src.applications.contour_matching_tester.service.contour_matching_tester_service`, `src.engine.core.i_messaging_service`.

### `ContourMatchingTesterApplication`

```python
class ContourMatchingTesterApplication(IApplication):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, vision_service=None, workpiece_service=None)
```

```python
def register(self, messaging_service: IMessagingService) -> None
```

```python
def create_widget(self) -> AppWidget
```

## `contour_matching_tester_factory.py`

Source: [src/applications/contour_matching_tester/contour_matching_tester_factory.py](../../../src/applications/contour_matching_tester/contour_matching_tester_factory.py).

Imports (including optional/function-local imports; not a startup dependency list): `logging`, `pl_gui.shell.base_app_widget.AppWidget`, `src.applications.base.application_factory`, `src.applications.contour_matching_tester.controller.contour_matching_tester_controller`, `src.applications.contour_matching_tester.model.contour_matching_tester_model`, `src.applications.contour_matching_tester.service.i_contour_matching_tester_service`, `src.applications.contour_matching_tester.view.contour_matching_tester_view`, `src.engine.core.i_messaging_service`, `typing`.

### `ContourMatchingTesterFactory`

```python
class ContourMatchingTesterFactory:
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def build(self, service: IContourMatchingTesterService, messaging: Optional[IMessagingService]=None, jog_service=None) -> AppWidget
```

## `example_usage.py`

Source: [src/applications/contour_matching_tester/example_usage.py](../../../src/applications/contour_matching_tester/example_usage.py).

Imports (including optional/function-local imports; not a startup dependency list): `PyQt6.QtWidgets`, `src.applications.contour_matching_tester.contour_matching_tester_factory`, `src.applications.contour_matching_tester.service.stub_contour_matching_tester_service`, `sys`.

### `run_standalone`

```python
def run_standalone() -> None
```
