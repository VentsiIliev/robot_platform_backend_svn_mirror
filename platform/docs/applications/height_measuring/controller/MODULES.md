# Module reference: `src/applications/height_measuring/controller`

[Package guide](README.md) · [Complete source index](../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [height_measuring_controller.py](#height_measuring_controllerpy)

## `__init__.py`

Source: [src/applications/height_measuring/controller/__init__.py](../../../../src/applications/height_measuring/controller/__init__.py).

No top-level functions, classes or public value declarations; inspect the source for imports or entry-point statements.

## `height_measuring_controller.py`

Source: [src/applications/height_measuring/controller/height_measuring_controller.py](../../../../src/applications/height_measuring/controller/height_measuring_controller.py).

Imports (including optional/function-local imports; not a startup dependency list): `logging`, `src.applications.base.i_application_controller`, `src.applications.height_measuring.model.height_measuring_model`, `src.applications.height_measuring.model.mapper`, `src.applications.height_measuring.view.height_measuring_view`.

### `HeightMeasuringController`

```python
class HeightMeasuringController(IApplicationController):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, model, view, messaging)
```

```python
def is_calibrating(self) -> bool
```

```python
def load(self) -> None
```

```python
def stop(self) -> None
```
