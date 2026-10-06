# Module reference: `src/applications/software_update/controller`

[Package guide](README.md) · [Complete source index](../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [software_update_controller.py](#software_update_controllerpy)

## `software_update_controller.py`

Source: [src/applications/software_update/controller/software_update_controller.py](../../../../src/applications/software_update/controller/software_update_controller.py).

Imports (including optional/function-local imports; not a startup dependency list): `src.applications.base.background_worker`, `src.applications.base.i_application_controller`.

### `SoftwareUpdateController`

```python
class SoftwareUpdateController(IApplicationController, BackgroundWorker):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, model, view)
```

```python
def load(self)
```

```python
def stop(self)
```
