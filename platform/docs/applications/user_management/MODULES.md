# Module reference: `src/applications/user_management`

[Package guide](README.md) · [Complete source index](../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [example_usage.py](#example_usagepy)
- [user_management_factory.py](#user_management_factorypy)

## `__init__.py`

Source: [src/applications/user_management/__init__.py](../../../src/applications/user_management/__init__.py).

Imports (including optional/function-local imports; not a startup dependency list): `src.applications.user_management.service.i_user_management_service`, `src.applications.user_management.service.stub_user_management_service`, `src.applications.user_management.user_management_factory`.

Package-level import/export surface:

```python
from src.applications.user_management.service.i_user_management_service import IUserManagementService
from src.applications.user_management.service.stub_user_management_service import StubUserManagementService
from src.applications.user_management.user_management_factory import UserManagementFactory
```

No top-level functions, classes or public value declarations; inspect the source for imports or entry-point statements.

## `example_usage.py`

Source: [src/applications/user_management/example_usage.py](../../../src/applications/user_management/example_usage.py).

Imports (including optional/function-local imports; not a startup dependency list): `PyQt6.QtWidgets`, `logging`, `os`, `src.applications.user_management.service.stub_user_management_service`, `src.applications.user_management.user_management_factory`, `sys`.

### `run_standalone`

```python
def run_standalone()
```

## `user_management_factory.py`

Source: [src/applications/user_management/user_management_factory.py](../../../src/applications/user_management/user_management_factory.py).

Imports (including optional/function-local imports; not a startup dependency list): `src.applications.base.application_factory`, `src.applications.base.i_application_controller`, `src.applications.base.i_application_model`, `src.applications.base.i_application_view`, `src.applications.user_management.controller.permissions_controller`, `src.applications.user_management.controller.user_management_controller`, `src.applications.user_management.model.permissions_model`, `src.applications.user_management.model.user_management_model`, `src.applications.user_management.service.i_user_management_service`, `src.applications.user_management.view.permissions_view`, `src.applications.user_management.view.user_management_view`, `src.engine.auth.i_permissions_admin_service`, `typing`.

### `UserManagementFactory`

```python
class UserManagementFactory(ApplicationFactory):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def build(self, service: IUserManagementService, permissions_service: Optional[IPermissionsAdminService]=None, known_app_ids: Optional[List[str]]=None, role_values: Optional[List[str]]=None, default_role_values: Optional[List[str]]=None, messaging=None, jog_service=None)
```
