# Module reference: `src/applications/user_management/service`

[Package guide](README.md) · [Complete source index](../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [i_user_management_service.py](#i_user_management_servicepy)
- [stub_user_management_service.py](#stub_user_management_servicepy)
- [user_management_application_service.py](#user_management_application_servicepy)

## `__init__.py`

Source: [src/applications/user_management/service/__init__.py](../../../../src/applications/user_management/service/__init__.py).

Imports (including optional/function-local imports; not a startup dependency list): `src.applications.user_management.service.i_user_management_service`, `src.applications.user_management.service.stub_user_management_service`, `src.applications.user_management.service.user_management_application_service`.

Package-level import/export surface:

```python
from src.applications.user_management.service.i_user_management_service import IUserManagementService
from src.applications.user_management.service.stub_user_management_service import StubUserManagementService
from src.applications.user_management.service.user_management_application_service import UserManagementApplicationService
```

No top-level functions, classes or public value declarations; inspect the source for imports or entry-point statements.

## `i_user_management_service.py`

Source: [src/applications/user_management/service/i_user_management_service.py](../../../../src/applications/user_management/service/i_user_management_service.py).

Imports (including optional/function-local imports; not a startup dependency list): `abc`, `src.applications.user_management.domain.user_schema`, `typing`.

### `IUserManagementService`

```python
class IUserManagementService(ABC):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
@abstractmethod
def get_schema(self) -> UserSchema
```

```python
@abstractmethod
def get_all_users(self) -> List[UserRecord]
```

```python
@abstractmethod
def add_user(self, record: UserRecord) -> tuple[bool, str]
```

```python
@abstractmethod
def update_user(self, record: UserRecord) -> tuple[bool, str]
```

```python
@abstractmethod
def delete_user(self, user_id) -> tuple[bool, str]
```

```python
@abstractmethod
def generate_qr(self, record: UserRecord) -> tuple[bool, str, Optional[str]]
```

Returns (success, message, qr_image_path).

```python
@abstractmethod
def send_access_package(self, record: UserRecord, qr_image_path: str) -> tuple[bool, str]
```

## `stub_user_management_service.py`

Source: [src/applications/user_management/service/stub_user_management_service.py](../../../../src/applications/user_management/service/stub_user_management_service.py).

Imports (including optional/function-local imports; not a startup dependency list): `logging`, `src.applications.user_management.domain.default_schema`, `src.applications.user_management.domain.user_schema`, `src.applications.user_management.service.i_user_management_service`, `typing`.

### `StubUserManagementService`

```python
class StubUserManagementService(IUserManagementService):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, schema: UserSchema=DEFAULT_USER_SCHEMA)
```

```python
def get_schema(self) -> UserSchema
```

```python
def get_all_users(self) -> List[UserRecord]
```

```python
def add_user(self, record: UserRecord) -> tuple[bool, str]
```

```python
def update_user(self, record: UserRecord) -> tuple[bool, str]
```

```python
def delete_user(self, user_id) -> tuple[bool, str]
```

```python
def generate_qr(self, record: UserRecord) -> tuple[bool, str, Optional[str]]
```

```python
def send_access_package(self, record: UserRecord, qr_image_path: str) -> tuple[bool, str]
```

## `user_management_application_service.py`

Source: [src/applications/user_management/service/user_management_application_service.py](../../../../src/applications/user_management/service/user_management_application_service.py).

Imports (including optional/function-local imports; not a startup dependency list): `logging`, `os`, `qrcode`, `src.applications.user_management.domain.i_user_repository`, `src.applications.user_management.domain.user_schema`, `src.applications.user_management.service._email_sender`, `src.applications.user_management.service.i_user_management_service`, `tempfile`, `typing`.

### `UserManagementApplicationService`

```python
class UserManagementApplicationService(IUserManagementService):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, repository: IUserRepository)
```

```python
def get_schema(self) -> UserSchema
```

```python
def get_all_users(self) -> List[UserRecord]
```

```python
def add_user(self, record: UserRecord) -> tuple[bool, str]
```

```python
def update_user(self, record: UserRecord) -> tuple[bool, str]
```

```python
def delete_user(self, user_id) -> tuple[bool, str]
```

```python
def generate_qr(self, record: UserRecord) -> tuple[bool, str, Optional[str]]
```

```python
def send_access_package(self, record: UserRecord, qr_image_path: str) -> tuple[bool, str]
```
