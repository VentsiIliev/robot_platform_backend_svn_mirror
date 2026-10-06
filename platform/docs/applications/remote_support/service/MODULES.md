# Module reference: `src/applications/remote_support/service`

[Package guide](README.md) · [Complete source index](../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [i_remote_support_service.py](#i_remote_support_servicepy)
- [remote_support_application_service.py](#remote_support_application_servicepy)
- [stub_remote_support_service.py](#stub_remote_support_servicepy)

## `__init__.py`

Source: [src/applications/remote_support/service/__init__.py](../../../../src/applications/remote_support/service/__init__.py).

No top-level functions, classes or public value declarations; inspect the source for imports or entry-point statements.

## `i_remote_support_service.py`

Source: [src/applications/remote_support/service/i_remote_support_service.py](../../../../src/applications/remote_support/service/i_remote_support_service.py).

Imports (including optional/function-local imports; not a startup dependency list): `abc`.

### `IRemoteSupportService`

```python
class IRemoteSupportService(ABC):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
@abstractmethod
def get_remote_support_status(self) -> dict
```

```python
@abstractmethod
def set_remote_support_enabled(self, enabled: bool, duration_seconds: int=900) -> None
```

```python
@abstractmethod
def get_password_status(self) -> dict
```

```python
@abstractmethod
def set_unattended_password(self, admin_id: str, admin_password: str, password: str) -> None
```

```python
@abstractmethod
def remove_unattended_password(self, admin_id: str, admin_password: str) -> None
```

## `remote_support_application_service.py`

Source: [src/applications/remote_support/service/remote_support_application_service.py](../../../../src/applications/remote_support/service/remote_support_application_service.py).

Imports (including optional/function-local imports; not a startup dependency list): `.i_remote_support_service`, `src.engine.auth.i_authentication_service`, `src.engine.remote_support.client`, `src.engine.remote_support.password_client`, `sys`.

### `RemoteSupportApplicationService`

```python
class RemoteSupportApplicationService(IRemoteSupportService):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, client=None, platform: str | None=None, *, password_client=None, authentication_service: IAuthenticationService | None=None, admin_role_value: str='Admin')
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
def set_unattended_password(self, admin_id: str, admin_password: str, password: str) -> None
```

```python
def remove_unattended_password(self, admin_id: str, admin_password: str) -> None
```

## `stub_remote_support_service.py`

Source: [src/applications/remote_support/service/stub_remote_support_service.py](../../../../src/applications/remote_support/service/stub_remote_support_service.py).

Imports (including optional/function-local imports; not a startup dependency list): `.i_remote_support_service`, `time`.

### `StubRemoteSupportService`

```python
class StubRemoteSupportService(IRemoteSupportService):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self)
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
def set_unattended_password(self, admin_id: str, admin_password: str, password: str) -> None
```

```python
def remove_unattended_password(self, admin_id: str, admin_password: str) -> None
```
