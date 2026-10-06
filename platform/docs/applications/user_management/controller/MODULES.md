# Module reference: `src/applications/user_management/controller`

[Package guide](README.md) · [Complete source index](../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [permissions_controller.py](#permissions_controllerpy)
- [user_management_controller.py](#user_management_controllerpy)

## `__init__.py`

Source: [src/applications/user_management/controller/__init__.py](../../../../src/applications/user_management/controller/__init__.py).

No top-level functions, classes or public value declarations; inspect the source for imports or entry-point statements.

## `permissions_controller.py`

Source: [src/applications/user_management/controller/permissions_controller.py](../../../../src/applications/user_management/controller/permissions_controller.py).

Imports (including optional/function-local imports; not a startup dependency list): `PyQt6.QtCore`, `src.applications.user_management.model.permissions_model`, `src.shared_contracts.events.localization_events`.

### `_t`

```python
def _t(text: str) -> str
```

### `_Bridge`

```python
class _Bridge(QObject):
```

Declared fields/defaults:

```python
retranslate = pyqtSignal()
```

### `PermissionsController`

```python
class PermissionsController:
```

Wires PermissionsModel to the App Permissions tab view. The view must expose: - set_permissions(app_ids, role_values, permissions) — populate table - set_notice(text) — show deferral notice - permission_toggled signal(app_id, role_value, allowed)

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, model: PermissionsModel, view, messaging=None) -> None
```

```python
def load(self) -> None
```

```python
def stop(self, *_args) -> None
```

## `user_management_controller.py`

Source: [src/applications/user_management/controller/user_management_controller.py](../../../../src/applications/user_management/controller/user_management_controller.py).

Imports (including optional/function-local imports; not a startup dependency list): `PyQt6.QtCore`, `PyQt6.QtGui`, `PyQt6.QtWidgets`, `logging`, `src.applications.base.i_application_controller`, `src.applications.base.styled_message_box`, `src.applications.base.widgets.custom_virtual_keyboard`, `src.applications.user_management.domain.user_schema`, `src.applications.user_management.model.user_management_model`, `src.applications.user_management.view.user_management_view`, `typing`.

### `_t`

```python
def _t(text: str) -> str
```

### `UserManagementController`

```python
class UserManagementController(IApplicationController):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, model: UserManagementModel, view: UserManagementView, messaging=None)
```

```python
def load(self) -> None
```

```python
def stop(self) -> None
```

### `_UserDialog`

```python
class _UserDialog(QDialog):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, schema: UserSchema, parent=None, record: Optional[UserRecord]=None)
```

```python
def get_record(self) -> UserRecord
```

### `_QrDialog`

```python
class _QrDialog(QDialog):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, record: UserRecord, qr_path: Optional[str], model: UserManagementModel, parent=None)
```
