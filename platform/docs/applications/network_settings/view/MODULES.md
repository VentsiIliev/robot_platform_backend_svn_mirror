# Module reference: `src/applications/network_settings/view`

[Package guide](README.md) · [Complete source index](../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [network_settings_view.py](#network_settings_viewpy)

## `__init__.py`

Source: [src/applications/network_settings/view/__init__.py](../../../../src/applications/network_settings/view/__init__.py).

No top-level functions, classes or public value declarations; inspect the source for imports or entry-point statements.

## `network_settings_view.py`

Source: [src/applications/network_settings/view/network_settings_view.py](../../../../src/applications/network_settings/view/network_settings_view.py).

Imports (including optional/function-local imports; not a startup dependency list): `PyQt6.QtCore`, `PyQt6.QtWidgets`, `__future__`, `pl_gui.settings.settings_view.styles`, `pl_gui.utils.utils_widgets.SwitchButton`, `src.applications.base.app_dialog`, `src.applications.base.i_application_view`, `src.applications.base.styled_message_box`, `src.applications.base.widgets.custom_virtual_keyboard`, `src.applications.base.widgets.keyboard_number_field`.

### `_PasswordDialog`

```python
class _PasswordDialog(AppDialog):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, ssid: str, parent=None) -> None
```

```python
def password(self) -> str
```

### `_IPv4Dialog`

```python
class _IPv4Dialog(AppDialog):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, current: dict, parent=None) -> None
```

```python
def settings(self) -> dict
```

### `NetworkSettingsView`

```python
class NetworkSettingsView(IApplicationView):
```

Declared fields/defaults:

```python
SHOW_JOG_WIDGET = False
refresh_wifi_requested = pyqtSignal()
refresh_wired_requested = pyqtSignal()
connect_wifi_requested = pyqtSignal(str, str, bool)
disconnect_wifi_requested = pyqtSignal()
forget_wifi_requested = pyqtSignal(str)
connect_wired_requested = pyqtSignal(str)
disconnect_wired_requested = pyqtSignal(str)
wifi_ipv4_requested = pyqtSignal()
wired_ipv4_requested = pyqtSignal(dict)
remote_support_requested = pyqtSignal(bool)
remote_support_refresh_requested = pyqtSignal()
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, parent=None, *, show_remote_support: bool=True) -> None
```

```python
def setup_ui(self) -> None
```

```python
def is_remote_support_visible(self) -> bool
```

```python
def set_remote_support_status(self, status: dict) -> None
```

```python
def set_remote_support_error(self, message: str) -> None
```

```python
def set_wifi_networks(self, networks: list[dict]) -> None
```

```python
def set_wired_devices(self, devices: list[dict]) -> None
```

```python
def set_busy(self, kind: str, busy: bool) -> None
```

```python
def set_status(self, message: str) -> None
```

```python
def set_error(self, message: str) -> None
```

```python
def edit_ipv4(self, current: dict) -> dict | None
```

```python
def retranslateUi(self) -> None
```

```python
def changeEvent(self, event) -> None
```

```python
def clean_up(self) -> None
```
