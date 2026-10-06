# Module reference: `src/applications/APPLICATION_BLUEPRINT/controller`

[Package guide](README.md) · [Complete source index](../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [my_controller.py](#my_controllerpy)

## `__init__.py`

Source: [src/applications/APPLICATION_BLUEPRINT/controller/__init__.py](../../../../src/applications/APPLICATION_BLUEPRINT/controller/__init__.py).

No top-level functions, classes or public value declarations; inspect the source for imports or entry-point statements.

## `my_controller.py`

Source: [src/applications/APPLICATION_BLUEPRINT/controller/my_controller.py](../../../../src/applications/APPLICATION_BLUEPRINT/controller/my_controller.py).

Imports (including optional/function-local imports; not a startup dependency list): `logging`, `src.applications.APPLICATION_BLUEPRINT.model.my_model`, `src.applications.APPLICATION_BLUEPRINT.view.my_view`, `src.applications.base.i_application_controller`.

### `MyController`

```python
class MyController(IApplicationController):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, model: MyModel, view: MyView)
```

```python
def load(self) -> None
```

```python
def stop(self) -> None
```
