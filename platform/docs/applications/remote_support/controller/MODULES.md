# Module reference: `src/applications/remote_support/controller`

[Package guide](README.md) · [Complete source index](../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [remote_support_controller.py](#remote_support_controllerpy)

## `__init__.py`

Source: [src/applications/remote_support/controller/__init__.py](../../../../src/applications/remote_support/controller/__init__.py).

No top-level functions, classes or public value declarations; inspect the source for imports or entry-point statements.

## `remote_support_controller.py`

Source: [src/applications/remote_support/controller/remote_support_controller.py](../../../../src/applications/remote_support/controller/remote_support_controller.py).

Imports (including optional/function-local imports; not a startup dependency list): `PyQt6.QtCore`, `functools`, `src.applications.base.background_worker`, `src.applications.base.i_application_controller`.

### `RemoteSupportController`

```python
class RemoteSupportController(IApplicationController, BackgroundWorker):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, model, view)
```

```python
def load(self) -> None
```

```python
def stop(self) -> None
```
