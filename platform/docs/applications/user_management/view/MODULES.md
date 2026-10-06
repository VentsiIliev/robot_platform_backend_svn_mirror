# Module reference: `src/applications/user_management/view`

[Package guide](README.md) · [Complete source index](../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [permissions_view.py](#permissions_viewpy)
- [user_management_view.py](#user_management_viewpy)

## `__init__.py`

Source: [src/applications/user_management/view/__init__.py](../../../../src/applications/user_management/view/__init__.py).

No top-level functions, classes or public value declarations; inspect the source for imports or entry-point statements.

## `permissions_view.py`

Source: [src/applications/user_management/view/permissions_view.py](../../../../src/applications/user_management/view/permissions_view.py).

Imports (including optional/function-local imports; not a startup dependency list): `PyQt6.QtCore`, `PyQt6.QtGui`, `PyQt6.QtWidgets`.

### `PermissionsView`

```python
class PermissionsView(QWidget):
```

App Permissions tab — checkbox table of app_id × role_value. Signals: permission_toggled(app_id, role_value, allowed)

Declared fields/defaults:

```python
permission_toggled = pyqtSignal(str, str, bool)
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, parent=None)
```

```python
def set_permissions(self, app_ids: list[str], role_values: list[str], permissions: dict[str, list[str]]) -> None
```

Populate the table. Suppresses checkbox signals during population.

```python
def set_notice(self, text: str) -> None
```

```python
def retranslateUi(self, *_) -> None
```

```python
def changeEvent(self, event) -> None
```

## `user_management_view.py`

Source: [src/applications/user_management/view/user_management_view.py](../../../../src/applications/user_management/view/user_management_view.py).

Imports (including optional/function-local imports; not a startup dependency list): `PyQt6.QtCore`, `PyQt6.QtGui`, `PyQt6.QtWidgets`, `pl_gui.utils.utils_widgets.table_helpers`, `src.applications.base.i_application_view`, `src.applications.base.widgets.custom_virtual_keyboard`, `src.applications.user_management.domain.user_schema`, `typing`.

### `UserManagementView`

```python
class UserManagementView(IApplicationView):
```

Declared fields/defaults:

```python
add_requested = pyqtSignal()
edit_requested = pyqtSignal(object)
delete_requested = pyqtSignal(object)
qr_requested = pyqtSignal(object)
refresh_requested = pyqtSignal()
filter_changed = pyqtSignal(str, str)
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, schema: UserSchema, parent=None)
```

```python
def setup_ui(self) -> None
```

```python
def add_permissions_tab(self, permissions_widget: QWidget) -> None
```

Attach the App Permissions tab. Called by the factory when the permissions service is available.

```python
def clean_up(self) -> None
```

```python
def set_users(self, records: List[UserRecord]) -> None
```

```python
def set_status(self, msg: str) -> None
```

```python
def selected_record(self) -> Optional[UserRecord]
```

```python
def retranslateUi(self) -> None
```
