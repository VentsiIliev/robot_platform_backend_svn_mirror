# Module reference: `src/applications/remote_support/model`

[Package guide](README.md) · [Complete source index](../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [remote_support_model.py](#remote_support_modelpy)

## `__init__.py`

Source: [src/applications/remote_support/model/__init__.py](../../../../src/applications/remote_support/model/__init__.py).

No top-level functions, classes or public value declarations; inspect the source for imports or entry-point statements.

## `remote_support_model.py`

Source: [src/applications/remote_support/model/remote_support_model.py](../../../../src/applications/remote_support/model/remote_support_model.py).

Imports (including optional/function-local imports; not a startup dependency list): `src.applications.base.i_application_model`, `src.applications.remote_support.service.i_remote_support_service`.

### `RemoteSupportModel`

```python
class RemoteSupportModel(IApplicationModel):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, service: IRemoteSupportService)
```

```python
def load(self) -> dict
```

```python
def save(self, enabled: bool, duration_seconds: int=900) -> None
```

```python
def get_remote_support_status(self) -> dict
```

```python
def set_remote_support_enabled(self, enabled: bool, duration_seconds: int=900) -> None
```

```python
def get_password_status(self) -> dict
```

```python
def set_unattended_password(self, admin_id: str, admin_password: str, password: str, confirmation: str) -> None
```

```python
def remove_unattended_password(self, admin_id: str, admin_password: str) -> None
```
