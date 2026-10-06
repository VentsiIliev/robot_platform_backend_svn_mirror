# Module reference: `src/applications/user_management/model`

[Package guide](README.md) · [Complete source index](../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [permissions_model.py](#permissions_modelpy)
- [user_management_model.py](#user_management_modelpy)

## `__init__.py`

Source: [src/applications/user_management/model/__init__.py](../../../../src/applications/user_management/model/__init__.py).

No top-level functions, classes or public value declarations; inspect the source for imports or entry-point statements.

## `permissions_model.py`

Source: [src/applications/user_management/model/permissions_model.py](../../../../src/applications/user_management/model/permissions_model.py).

Imports (including optional/function-local imports; not a startup dependency list): `src.engine.auth.i_permissions_admin_service`.

### `PermissionsModel`

```python
class PermissionsModel:
```

Pure-logic model for the App Permissions tab. Wraps IPermissionsAdminService and filters results to only the known app_ids registered in the current RobotSystem shell. Each set_permission call persists immediately — no separate save step needed.

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, service: IPermissionsAdminService, known_app_ids: list[str], role_values: list[str], default_role_values: list[str]) -> None
```

```python
def get_known_app_ids(self) -> list[str]
```

```python
def get_role_values(self) -> list[str]
```

Column headers for the permissions table.

```python
def get_permissions(self) -> dict[str, list[str]]
```

Return permissions for known apps only. Apps missing from the service default to ['Admin'].

```python
def set_permission(self, app_id: str, role_value: str, allowed: bool) -> None
```

Toggle a single role for an app and persist immediately.

## `user_management_model.py`

Source: [src/applications/user_management/model/user_management_model.py](../../../../src/applications/user_management/model/user_management_model.py).

Imports (including optional/function-local imports; not a startup dependency list): `src.applications.base.i_application_model`, `src.applications.user_management.domain.user_schema`, `src.applications.user_management.service.i_user_management_service`, `typing`.

### `UserManagementModel`

```python
class UserManagementModel(IApplicationModel):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, service: IUserManagementService)
```

```python
@property
def schema(self) -> UserSchema
```

```python
def load(self) -> List[UserRecord]
```

```python
def save(self, *args, **kwargs) -> None
```

```python
def get_users(self) -> List[UserRecord]
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
def send_access_package(self, record: UserRecord, qr_path: str) -> tuple[bool, str]
```
