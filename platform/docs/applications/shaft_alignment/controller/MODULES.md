# Module reference: `src/applications/shaft_alignment/controller`

[Package guide](README.md) · [Complete source index](../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [shaft_alignment_controller.py](#shaft_alignment_controllerpy)

## `__init__.py`

Source: [src/applications/shaft_alignment/controller/__init__.py](../../../../src/applications/shaft_alignment/controller/__init__.py).

Imports (including optional/function-local imports; not a startup dependency list): `src.applications.shaft_alignment.controller.shaft_alignment_controller`.

Package-level import/export surface:

```python
from src.applications.shaft_alignment.controller.shaft_alignment_controller import ShaftAlignmentController
```

Module declarations (expressions are shown without evaluating them):

```python
__all__ = ['ShaftAlignmentController']
```

## `shaft_alignment_controller.py`

Source: [src/applications/shaft_alignment/controller/shaft_alignment_controller.py](../../../../src/applications/shaft_alignment/controller/shaft_alignment_controller.py).

Imports (including optional/function-local imports; not a startup dependency list): `PyQt6.QtCore`, `__future__`, `logging`, `src.applications.base.i_application_controller`, `src.applications.shaft_alignment.model.shaft_alignment_model`, `src.applications.shaft_alignment.service.i_shaft_alignment_service`, `src.applications.shaft_alignment.view.shaft_alignment_view`.

### `ShaftAlignmentController`

```python
class ShaftAlignmentController(IApplicationController):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, model: ShaftAlignmentModel, view: ShaftAlignmentView) -> None
```

```python
def load(self) -> None
```

```python
def stop(self) -> None
```
