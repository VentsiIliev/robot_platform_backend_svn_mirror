# Module reference: `src/engine/auth`

[Package guide](README.md) · [Complete source index](../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [auth_user_record.py](#auth_user_recordpy)
- [authenticated_user.py](#authenticated_userpy)
- [authentication_service.py](#authentication_servicepy)
- [authorization_service.py](#authorization_servicepy)
- [i_auth_user_repository.py](#i_auth_user_repositorypy)
- [i_authenticated_user.py](#i_authenticated_userpy)
- [i_authentication_service.py](#i_authentication_servicepy)
- [i_authorization_service.py](#i_authorization_servicepy)
- [i_permissions_admin_service.py](#i_permissions_admin_servicepy)
- [i_permissions_repository.py](#i_permissions_repositorypy)
- [i_session_service.py](#i_session_servicepy)
- [json_permissions_repository.py](#json_permissions_repositorypy)
- [permissions_migrator.py](#permissions_migratorpy)
- [user_session.py](#user_sessionpy)

## `__init__.py`

Source: [src/engine/auth/__init__.py](../../../src/engine/auth/__init__.py).

Imports (including optional/function-local imports; not a startup dependency list): `src.engine.auth.auth_user_record`, `src.engine.auth.authenticated_user`, `src.engine.auth.authentication_service`, `src.engine.auth.authorization_service`, `src.engine.auth.i_auth_user_repository`, `src.engine.auth.i_authenticated_user`, `src.engine.auth.i_authentication_service`, `src.engine.auth.i_authorization_service`, `src.engine.auth.i_permissions_admin_service`, `src.engine.auth.i_permissions_repository`, `src.engine.auth.i_session_service`, `src.engine.auth.json_permissions_repository`, `src.engine.auth.permissions_migrator`, `src.engine.auth.user_session`.

Package-level import/export surface:

```python
from src.engine.auth.auth_user_record import AuthUserRecord
from src.engine.auth.authenticated_user import AuthenticatedUser
from src.engine.auth.authentication_service import AuthenticationService
from src.engine.auth.authorization_service import AuthorizationService
from src.engine.auth.json_permissions_repository import JsonPermissionsRepository
from src.engine.auth.i_authenticated_user import IAuthenticatedUser
from src.engine.auth.i_authentication_service import IAuthenticationService
from src.engine.auth.i_authorization_service import IAuthorizationService
from src.engine.auth.i_auth_user_repository import IAuthUserRepository
from src.engine.auth.i_permissions_admin_service import IPermissionsAdminService
from src.engine.auth.i_permissions_repository import IPermissionsRepository
from src.engine.auth.i_session_service import ISessionService
from src.engine.auth.permissions_migrator import ensure_permissions_current
from src.engine.auth.user_session import UserSession
```

Module declarations (expressions are shown without evaluating them):

```python
__all__ = ['AuthUserRecord', 'AuthenticatedUser', 'AuthenticationService', 'AuthorizationService', 'JsonPermissionsRepository', 'IAuthenticatedUser', 'IAuthenticationService', 'IAuthorizationService', 'IAuthUserRepository', 'IPermissionsAdminService', 'IPermissionsRepository', 'ISessionService', 'ensure_permissions_current', 'UserSession']
```

## `auth_user_record.py`

Source: [src/engine/auth/auth_user_record.py](../../../src/engine/auth/auth_user_record.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `dataclasses`, `enum`, `typing`.

### `AuthUserRecord`

```python
@dataclass(frozen=True)
class AuthUserRecord:
```

Minimal auth-facing user record. This stays intentionally narrow so authentication can be reused across robot systems regardless of the underlying user storage implementation.

Declared fields/defaults:

```python
user_id: str
password: str
role: Enum
payload: dict[str, Any] = field(default_factory=dict)
```

## `authenticated_user.py`

Source: [src/engine/auth/authenticated_user.py](../../../src/engine/auth/authenticated_user.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `enum`, `src.engine.auth.auth_user_record`, `src.engine.auth.i_authenticated_user`.

### `AuthenticatedUser`

```python
class AuthenticatedUser(IAuthenticatedUser):
```

Default engine-level authenticated user wrapper.

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, record: AuthUserRecord) -> None
```

```python
@property
def user_id(self) -> str
```

```python
@property
def role(self) -> Enum
```

```python
@property
def record(self) -> AuthUserRecord
```

## `authentication_service.py`

Source: [src/engine/auth/authentication_service.py](../../../src/engine/auth/authentication_service.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `src.engine.auth.authenticated_user`, `src.engine.auth.i_auth_user_repository`, `src.engine.auth.i_authenticated_user`, `src.engine.auth.i_authentication_service`, `typing`.

### `AuthenticationService`

```python
class AuthenticationService(IAuthenticationService):
```

Reusable credential verification backed by IAuthUserRepository.

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, repository: IAuthUserRepository) -> None
```

```python
def authenticate(self, user_id: str, password: str) -> Optional[IAuthenticatedUser]
```

```python
def authenticate_qr(self, qr_payload: str) -> Optional[IAuthenticatedUser]
```

## `authorization_service.py`

Source: [src/engine/auth/authorization_service.py](../../../src/engine/auth/authorization_service.py).

Imports (including optional/function-local imports; not a startup dependency list): `src.engine.auth.i_authenticated_user`, `src.engine.auth.i_permissions_admin_service`, `src.engine.auth.i_permissions_repository`.

### `AuthorizationService`

```python
class AuthorizationService(IPermissionsAdminService):
```

Role-based app filtering backed by IPermissionsRepository. Comparison is done on role.value strings — no concrete Role type is imported.

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, repository: IPermissionsRepository, protected_app_role_values: dict[str, list[str]] | None=None) -> None
```

```python
def get_visible_apps(self, user: IAuthenticatedUser, all_specs: list) -> list
```

```python
def can_access(self, user: IAuthenticatedUser, app_id: str) -> bool
```

```python
def get_all_permissions(self) -> dict[str, list[str]]
```

```python
def set_permissions(self, app_id: str, role_values: list[str]) -> None
```

## `i_auth_user_repository.py`

Source: [src/engine/auth/i_auth_user_repository.py](../../../src/engine/auth/i_auth_user_repository.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `abc`, `src.engine.auth.auth_user_record`, `typing`.

### `IAuthUserRepository`

```python
class IAuthUserRepository(ABC):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
@abstractmethod
def get_by_id(self, user_id: str) -> Optional[AuthUserRecord]
```

Return the auth-facing record for the given user id, or None.

## `i_authenticated_user.py`

Source: [src/engine/auth/i_authenticated_user.py](../../../src/engine/auth/i_authenticated_user.py).

Imports (including optional/function-local imports; not a startup dependency list): `abc`, `enum`.

### `IAuthenticatedUser`

```python
class IAuthenticatedUser(ABC):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
@property
@abstractmethod
def user_id(self) -> str
```

Stable identifier for this user.

```python
@property
@abstractmethod
def role(self) -> Enum
```

The user's role. Compared via .value — no concrete Role type assumed.

## `i_authentication_service.py`

Source: [src/engine/auth/i_authentication_service.py](../../../src/engine/auth/i_authentication_service.py).

Imports (including optional/function-local imports; not a startup dependency list): `abc`, `src.engine.auth.i_authenticated_user`, `typing`.

### `IAuthenticationService`

```python
class IAuthenticationService(ABC):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
@abstractmethod
def authenticate(self, user_id: str, password: str) -> Optional[IAuthenticatedUser]
```

Verify credentials. Returns IAuthenticatedUser on success, None on failure. Lockout tracking is handled internally — not exposed on this interface.

```python
@abstractmethod
def authenticate_qr(self, qr_payload: str) -> Optional[IAuthenticatedUser]
```

Decode a QR payload and verify the embedded credentials.

## `i_authorization_service.py`

Source: [src/engine/auth/i_authorization_service.py](../../../src/engine/auth/i_authorization_service.py).

Imports (including optional/function-local imports; not a startup dependency list): `abc`, `src.engine.auth.i_authenticated_user`, `typing`.

### `IAuthorizationService`

```python
class IAuthorizationService(ABC):
```

Read-only authorization contract. Used by main.y_pixels and any runtime access guard. Does not expose write operations — callers get only the access they need.

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
@abstractmethod
def get_visible_apps(self, user: IAuthenticatedUser, all_specs: list) -> list
```

Return the subset of all_specs the user's role may access.

```python
@abstractmethod
def can_access(self, user: IAuthenticatedUser, app_id: str) -> bool
```

Return True if the user's role is allowed to access app_id.

## `i_permissions_admin_service.py`

Source: [src/engine/auth/i_permissions_admin_service.py](../../../src/engine/auth/i_permissions_admin_service.py).

Imports (including optional/function-local imports; not a startup dependency list): `abc`, `src.engine.auth.i_authorization_service`, `typing`.

### `IPermissionsAdminService`

```python
class IPermissionsAdminService(IAuthorizationService):
```

Extends IAuthorizationService with admin write operations. Only the permissions editor model should depend on this interface. main.y_pixels and runtime guards use the narrower IAuthorizationService.

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
@abstractmethod
def get_all_permissions(self) -> dict[str, list[str]]
```

Return the full app_id → role_values map for the admin editor UI.

```python
@abstractmethod
def set_permissions(self, app_id: str, role_values: list[str]) -> None
```

Update and persist role access for app_id. Implementations may enforce robot-system-specific protected role invariants.

## `i_permissions_repository.py`

Source: [src/engine/auth/i_permissions_repository.py](../../../src/engine/auth/i_permissions_repository.py).

Imports (including optional/function-local imports; not a startup dependency list): `abc`.

### `IPermissionsRepository`

```python
class IPermissionsRepository(ABC):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
@abstractmethod
def get_allowed_role_values(self, app_id: str) -> list[str]
```

Return role value strings for this app_id. Defaults to ['Admin'] if the app_id is not present.

```python
@abstractmethod
def set_allowed_role_values(self, app_id: str, role_values: list[str]) -> None
```

Persist the given role values for app_id immediately. Must store a copy — mutations to the input list must not affect stored data.

```python
@abstractmethod
def get_all(self) -> dict[str, list[str]]
```

Return a full copy of the permissions map keyed by app_id.

## `i_session_service.py`

Source: [src/engine/auth/i_session_service.py](../../../src/engine/auth/i_session_service.py).

Imports (including optional/function-local imports; not a startup dependency list): `abc`, `enum`, `src.engine.auth.i_authenticated_user`, `typing`.

### `ISessionService`

```python
class ISessionService(ABC):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
@abstractmethod
def login(self, user: IAuthenticatedUser) -> None
```

Store the authenticated user as the current session.

```python
@abstractmethod
def logout(self) -> None
```

Clear the current session. Safe to call when already logged out.

```python
@property
@abstractmethod
def current_user(self) -> Optional[IAuthenticatedUser]
```

The currently logged-in user, or None if not authenticated.

```python
@property
@abstractmethod
def current_role(self) -> Optional[Enum]
```

The current user's role, or None if not authenticated.

```python
@abstractmethod
def is_authenticated(self) -> bool
```

True if a user is currently logged in.

## `json_permissions_repository.py`

Source: [src/engine/auth/json_permissions_repository.py](../../../src/engine/auth/json_permissions_repository.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `json`, `os`, `src.engine.auth.i_permissions_repository`.

### `JsonPermissionsRepository`

```python
class JsonPermissionsRepository(IPermissionsRepository):
```

JSON-backed permissions store.

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, file_path: str, default_role_values: list[str] | None=None) -> None
```

```python
def get_allowed_role_values(self, app_id: str) -> list[str]
```

```python
def set_allowed_role_values(self, app_id: str, role_values: list[str]) -> None
```

```python
def get_all(self) -> dict[str, list[str]]
```

## `permissions_migrator.py`

Source: [src/engine/auth/permissions_migrator.py](../../../src/engine/auth/permissions_migrator.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `src.engine.auth.i_permissions_repository`.

### `ensure_permissions_current`

```python
def ensure_permissions_current(repo: IPermissionsRepository, known_app_ids: list[str], default_role_values: list[str]) -> None
```

Add missing app ids with the configured default role values.

## `user_session.py`

Source: [src/engine/auth/user_session.py](../../../src/engine/auth/user_session.py).

Imports (including optional/function-local imports; not a startup dependency list): `enum`, `src.engine.auth.i_authenticated_user`, `src.engine.auth.i_session_service`, `threading`, `typing`.

### `UserSession`

```python
class UserSession(ISessionService):
```

Thread-safe session holder. Instantiated once in main.y_pixels and injected everywhere as ISessionService. Never access via a global — always inject.

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self) -> None
```

```python
def login(self, user: IAuthenticatedUser) -> None
```

```python
def logout(self) -> None
```

```python
@property
def current_user(self) -> Optional[IAuthenticatedUser]
```

```python
@property
def current_role(self) -> Optional[Enum]
```

```python
def is_authenticated(self) -> bool
```
