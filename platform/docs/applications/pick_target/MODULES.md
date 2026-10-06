# Module reference: `src/applications/pick_target`

[Package guide](README.md) · [Complete source index](../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [example_usage.py](#example_usagepy)
- [pick_target_factory.py](#pick_target_factorypy)

## `__init__.py`

Source: [src/applications/pick_target/__init__.py](../../../src/applications/pick_target/__init__.py).

No top-level functions, classes or public value declarations; inspect the source for imports or entry-point statements.

## `example_usage.py`

Source: [src/applications/pick_target/example_usage.py](../../../src/applications/pick_target/example_usage.py).

Imports (including optional/function-local imports; not a startup dependency list): `PyQt6.QtWidgets`, `src.applications.pick_target.pick_target_factory`, `src.applications.pick_target.service.stub_pick_target_service`, `sys`.

### `run_standalone`

```python
def run_standalone() -> None
```

## `pick_target_factory.py`

Source: [src/applications/pick_target/pick_target_factory.py](../../../src/applications/pick_target/pick_target_factory.py).

Imports (including optional/function-local imports; not a startup dependency list): `src.applications.base.application_factory`, `src.applications.pick_target.controller.pick_target_controller`, `src.applications.pick_target.model.pick_target_model`, `src.applications.pick_target.service.i_pick_target_service`, `src.applications.pick_target.view.pick_target_view`.

### `PickTargetFactory`

```python
class PickTargetFactory(ApplicationFactory):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self)
```

```python
def build(self, service, messaging=None, jog_service=None)
```
