# Module reference: `tests/engine/auth`

[Package guide](README.md) · [Complete source index](../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [test_authorization_service.py](#test_authorization_servicepy)
- [test_i_authenticated_user.py](#test_i_authenticated_userpy)
- [test_i_authentication_service.py](#test_i_authentication_servicepy)
- [test_i_permissions_repository.py](#test_i_permissions_repositorypy)
- [test_session_service.py](#test_session_servicepy)

## `__init__.py`

Source: [tests/engine/auth/__init__.py](../../../../tests/engine/auth/__init__.py).

No top-level functions, classes or public value declarations; inspect the source for imports or entry-point statements.

## `test_authorization_service.py`

Source: [tests/engine/auth/test_authorization_service.py](../../../../tests/engine/auth/test_authorization_service.py).

Tests for src/engine/auth/authorization_service.y_pixels Covers visible-app filtering, can_access, get_all_permissions, set_permissions, and the Admin-always-has-access invariant on user_management.

Imports (including optional/function-local imports; not a startup dependency list): `enum`, `src.engine.auth.authorization_service`, `src.engine.auth.i_authenticated_user`, `src.engine.auth.i_permissions_repository`, `src.shared_contracts.declarations`, `unittest`, `unittest.mock`.

### `_Role`

```python
class _Role(Enum):
```

Declared fields/defaults:

```python
ADMIN = 'Admin'
OPERATOR = 'Operator'
VIEWER = 'Viewer'
```

### `_user`

```python
def _user(role: _Role) -> IAuthenticatedUser
```

### `_repo`

```python
def _repo(data: dict) -> IPermissionsRepository
```

Build a mock IPermissionsRepository from a plain dict.

### `_spec`

```python
def _spec(app_id: str) -> ApplicationSpec
```

### `TestGetVisibleApps`

```python
class TestGetVisibleApps(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_admin_sees_all_apps(self)
```

```python
def test_operator_only_sees_permitted_apps(self)
```

```python
def test_viewer_sees_only_viewer_apps(self)
```

```python
def test_unlisted_app_defaults_to_admin_only(self)
```

```python
def test_returns_empty_list_when_no_specs_match(self)
```

### `TestCanAccess`

```python
class TestCanAccess(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_returns_true_when_role_is_allowed(self)
```

```python
def test_returns_false_when_role_is_not_allowed(self)
```

```python
def test_unlisted_app_denies_non_admin(self)
```

```python
def test_unlisted_app_allows_admin(self)
```

### `TestGetAllPermissions`

```python
class TestGetAllPermissions(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_returns_full_map_from_repository(self)
```

### `TestSetPermissions`

```python
class TestSetPermissions(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_delegates_to_repository(self)
```

```python
def test_user_management_always_retains_admin(self)
```

```python
def test_user_management_retains_other_roles_alongside_admin(self)
```

```python
def test_other_apps_not_forced_to_include_admin(self)
```

## `test_i_authenticated_user.py`

Source: [tests/engine/auth/test_i_authenticated_user.py](../../../../tests/engine/auth/test_i_authenticated_user.py).

Tests for src/engine/auth/i_authenticated_user.y_pixels

Imports (including optional/function-local imports; not a startup dependency list): `enum`, `src.engine.auth.i_authenticated_user`, `unittest`.

### `_DummyRole`

```python
class _DummyRole(Enum):
```

Declared fields/defaults:

```python
ADMIN = 'Admin'
OPERATOR = 'Operator'
```

### `_ConcreteUser`

```python
class _ConcreteUser(IAuthenticatedUser):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
@property
def user_id(self) -> str
```

```python
@property
def role(self) -> Enum
```

### `TestIAuthenticatedUser`

```python
class TestIAuthenticatedUser(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_cannot_instantiate_directly(self)
```

```python
def test_concrete_subclass_instantiates(self)
```

```python
def test_user_id_returns_string(self)
```

```python
def test_role_returns_enum(self)
```

```python
def test_role_value_is_accessible(self)
```

```python
def test_missing_user_id_raises_on_instantiation(self)
```

```python
def test_missing_role_raises_on_instantiation(self)
```

## `test_i_authentication_service.py`

Source: [tests/engine/auth/test_i_authentication_service.py](../../../../tests/engine/auth/test_i_authentication_service.py).

Tests for src/engine/auth/i_authentication_service.y_pixels Verifies the interface contract using a minimal stub.

Imports (including optional/function-local imports; not a startup dependency list): `enum`, `src.engine.auth.i_authenticated_user`, `src.engine.auth.i_authentication_service`, `unittest`, `unittest.mock`.

### `_DummyUser`

```python
class _DummyUser(IAuthenticatedUser):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
@property
def user_id(self) -> str
```

```python
@property
def role(self) -> Enum
```

### `_StubAuthenticationService`

```python
class _StubAuthenticationService(IAuthenticationService):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def authenticate(self, user_id: str, password: str)
```

```python
def authenticate_qr(self, qr_payload: str)
```

### `TestIAuthenticationService`

```python
class TestIAuthenticationService(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_cannot_instantiate_directly(self)
```

```python
def test_stub_satisfies_interface(self)
```

```python
def test_authenticate_returns_user_on_valid_credentials(self)
```

```python
def test_authenticate_returns_none_on_invalid_credentials(self)
```

```python
def test_authenticate_qr_returns_user_on_valid_payload(self)
```

```python
def test_authenticate_qr_returns_none_on_invalid_payload(self)
```

## `test_i_permissions_repository.py`

Source: [tests/engine/auth/test_i_permissions_repository.py](../../../../tests/engine/auth/test_i_permissions_repository.py).

Tests for src/engine/auth/i_permissions_repository.y_pixels Verifies the interface contract: any implementation must satisfy these behaviours. Uses a minimal in-memory stub to prove the contract, not the JSON-backed implementation.

Imports (including optional/function-local imports; not a startup dependency list): `src.engine.auth.i_permissions_repository`, `unittest`.

### `_InMemoryPermissionsRepository`

```python
class _InMemoryPermissionsRepository(IPermissionsRepository):
```

Minimal in-memory stub — used only to verify the interface contract.

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, data: dict=None)
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

### `TestIPermissionsRepository`

```python
class TestIPermissionsRepository(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_cannot_instantiate_directly(self)
```

```python
def test_get_allowed_role_values_returns_list_of_strings(self)
```

```python
def test_get_allowed_role_values_defaults_to_admin_when_missing(self)
```

```python
def test_set_allowed_role_values_persists(self)
```

```python
def test_set_allowed_role_values_overwrites_existing(self)
```

```python
def test_get_all_returns_full_mapping(self)
```

```python
def test_get_all_returns_copy_not_reference(self)
```

```python
def test_set_does_not_store_reference_to_input_list(self)
```

## `test_session_service.py`

Source: [tests/engine/auth/test_session_service.py](../../../../tests/engine/auth/test_session_service.py).

Tests for src/engine/auth/user_session.y_pixels Covers login, logout, current_user/current_role properties, is_authenticated, and thread safety under concurrent access.

Imports (including optional/function-local imports; not a startup dependency list): `enum`, `src.engine.auth.i_authenticated_user`, `src.engine.auth.i_session_service`, `src.engine.auth.user_session`, `threading`, `unittest`, `unittest.mock`.

### `_Role`

```python
class _Role(Enum):
```

Declared fields/defaults:

```python
ADMIN = 'Admin'
OPERATOR = 'Operator'
```

### `_make_user`

```python
def _make_user(role: _Role=_Role.ADMIN) -> IAuthenticatedUser
```

### `TestISessionService`

```python
class TestISessionService(unittest.TestCase):
```

Verify UserSession satisfies ISessionService.

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_is_instance_of_i_session_service(self)
```

### `TestUserSessionLogin`

```python
class TestUserSessionLogin(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def setUp(self)
```

```python
def test_not_authenticated_initially(self)
```

```python
def test_current_user_is_none_initially(self)
```

```python
def test_current_role_is_none_initially(self)
```

```python
def test_login_sets_authenticated(self)
```

```python
def test_login_sets_current_user(self)
```

```python
def test_login_sets_current_role(self)
```

### `TestUserSessionLogout`

```python
class TestUserSessionLogout(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def setUp(self)
```

```python
def test_logout_clears_authenticated(self)
```

```python
def test_logout_clears_current_user(self)
```

```python
def test_logout_clears_current_role(self)
```

```python
def test_logout_when_already_logged_out_is_safe(self)
```

### `TestUserSessionThreadSafety`

```python
class TestUserSessionThreadSafety(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_concurrent_login_logout_leaves_session_consistent(self)
```
