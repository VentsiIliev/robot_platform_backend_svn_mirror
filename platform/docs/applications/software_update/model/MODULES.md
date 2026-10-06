# Module reference: `src/applications/software_update/model`

[Package guide](README.md) · [Complete source index](../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [software_update_model.py](#software_update_modelpy)

## `software_update_model.py`

Source: [src/applications/software_update/model/software_update_model.py](../../../../src/applications/software_update/model/software_update_model.py).

Imports (including optional/function-local imports; not a startup dependency list): `src.applications.base.i_application_model`, `src.applications.software_update.service.i_software_update_service`.

### `SoftwareUpdateModel`

```python
class SoftwareUpdateModel(IApplicationModel):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, service: ISoftwareUpdateService)
```

```python
def load(self) -> dict
```

```python
def save(self) -> None
```

```python
def check(self) -> dict
```

```python
def download(self) -> dict
```
