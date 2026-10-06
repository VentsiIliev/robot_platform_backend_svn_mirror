# Module reference: `src/applications/user_management/ui`

[Package guide](README.md) · [Complete source index](../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [UserDashboard.py](#userdashboardpy)
- [UserManagementAppWidget.py](#usermanagementappwidgetpy)
- [__init__.py](#__init__py)

## `UserDashboard.py`

Source: [src/applications/user_management/ui/UserDashboard.py](../../../../src/applications/user_management/ui/UserDashboard.py).

Imports (including optional/function-local imports; not a startup dependency list): `PyQt6.QtCore`, `PyQt6.QtGui`, `PyQt6.QtWidgets`, `frontend.core.utils.IconLoader`, `frontend.core.utils.localization`, `frontend.virtualKeyboard.VirtualKeyboard`, `frontend.widgets.AccessCard`, `frontend.widgets.MaterialButton`, `frontend.widgets.ToastWidget`, `modules.shared.core.email.emailSender`, `modules.shared.core.user.CSVUsersRepository`, `modules.shared.core.user.User`, `modules.shared.core.user.UserService`, `os`, `qrcode`, `sys`.

### `UserTableModel`

```python
class UserTableModel:
```

Model to handle user data for the table

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, users=None)
```

```python
def get_user_data(self, user)
```

Convert user object to a list for table display

```python
def update_users(self, users)
```

Update the user list

### `UserDialog`

```python
class UserDialog(TranslatableDialog):
```

Dialog for adding/editing users

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, parent=None, user=None, title='')
```

```python
def setup_ui(self)
```

```python
def retranslate(self)
```

Update all text labels for language changes - called automatically

```python
def populate_fields(self)
```

Populate fields when editing existing user

```python
def get_user_data(self)
```

Get user data from form

### `UserManagementWidget`

```python
class UserManagementWidget(TranslatableWidget):
```

Main widget for user management

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, csv_file_path='users.csv')
```

```python
def setup_service(self)
```

Initialize the user service and repository

```python
def setup_inline_user_form(self)
```

Setup the inline user form

```python
def setup_ui(self)
```

Setup the user interface

```python
def setup_styles(self)
```

Apply custom styles to the widget

```python
def load_users(self)
```

Load users from the repository and display in table

```python
def populate_table(self, users)
```

Populate the table with user data

```python
def show_add_user_form(self)
```

Show the inline form for adding a new user

```python
def show_edit_user_form(self)
```

Show the inline form for editing selected user

```python
def hide_user_form(self)
```

Hide the user form

```python
def clear_user_form(self)
```

Clear all form fields

```python
def populate_user_form(self, user)
```

Populate form fields with user data

```python
def save_user_form(self)
```

Save the user form data

```python
def delete_user(self)
```

Delete selected user

```python
def apply_filter(self)
```

Apply filter to the table

```python
def clear_filter(self)
```

Clear the filter and show all users

```python
def on_selection_changed(self)
```

Handle table selection changes

```python
def show_error(self, message)
```

Show error message dialog

```python
def show_info(self, message)
```

Show info message dialog

```python
def generateQrCode(self)
```

Generate a QR code with user ID and password

```python
def send_access_package(self, user, qr_image_path)
```

Send user access package via email

```python
def emailQrCode(self, user, qr_image_path)
```

```python
def retranslate(self)
```

Update all UI texts for language changes - called automatically

### `UserManagementWindow`

```python
class UserManagementWindow(QMainWindow):
```

Main window containing the user management widget

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self)
```

### `main`

```python
def main()
```

Main function to run the application

## `UserManagementAppWidget.py`

Source: [src/applications/user_management/ui/UserManagementAppWidget.py](../../../../src/applications/user_management/ui/UserManagementAppWidget.py).

Imports (including optional/function-local imports; not a startup dependency list): `core.application.ApplicationContext`, `frontend.core.shared.base_widgets.AppWidget`, `os`, `plugins.core.user_management.ui.UserDashboard`, `traceback`.

Module declarations (expressions are shown without evaluating them):

```python
application_users_storage = get_users_storage_path()
```

### `UserManagementAppWidget`

```python
class UserManagementAppWidget(AppWidget):
```

Specialized widget for User Management application

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, parent=None)
```

```python
def setup_ui(self)
```

Set up the user management specific UI

## `__init__.py`

Source: [src/applications/user_management/ui/__init__.py](../../../../src/applications/user_management/ui/__init__.py).

No top-level functions, classes or public value declarations; inspect the source for imports or entry-point statements.
