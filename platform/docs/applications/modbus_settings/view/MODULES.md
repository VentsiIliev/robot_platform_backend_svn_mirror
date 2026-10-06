# Module reference: `src/applications/modbus_settings/view`

[Package guide](README.md) · [Complete source index](../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [modbus_settings_schema.py](#modbus_settings_schemapy)
- [modbus_settings_view.py](#modbus_settings_viewpy)

## `__init__.py`

Source: [src/applications/modbus_settings/view/__init__.py](../../../../src/applications/modbus_settings/view/__init__.py).

No top-level functions, classes or public value declarations; inspect the source for imports or entry-point statements.

## `modbus_settings_schema.py`

Source: [src/applications/modbus_settings/view/modbus_settings_schema.py](../../../../src/applications/modbus_settings/view/modbus_settings_schema.py).

Imports (including optional/function-local imports; not a startup dependency list): `pl_gui.settings.settings_view.schema`.

Module declarations (expressions are shown without evaluating them):

```python
CONNECTION_GROUP = SettingGroup('Connection', [SettingField('baudrate', 'Baudrate', 'combo', default='115200', choices=['9600', '19200', '38400', '57600', '115200', '230400', '460800']), SettingField('parity', 'Parity', 'combo', default='N', choices=['N', 'E', 'O', 'M', 'S']), SettingField('bytesize', 'Byte Size', 'combo', default='8', choices=['5', '6', '7', '8']), SettingField('stopbits', 'Stop Bits', 'combo', default='1', choices=['1', '2']), SettingField('timeout', 'Timeout', 'double_spinbox', default=0.01, min_val=0.001, max_val=10.0, decimals=3, suffix=' s', step=0.001, step_options=[0.001, 0.01, 0.1, 1.0])])
DEVICE_GROUP = SettingGroup('Device', [SettingField('slave_address', 'Slave Address', 'spinbox', default=10, min_val=1, max_val=247, step=1, step_options=[1, 5, 10]), SettingField('max_retries', 'Max Retries', 'spinbox', default=30, min_val=1, max_val=100, step=1, step_options=[1, 5, 10])])
```

## `modbus_settings_view.py`

Source: [src/applications/modbus_settings/view/modbus_settings_view.py](../../../../src/applications/modbus_settings/view/modbus_settings_view.py).

Imports (including optional/function-local imports; not a startup dependency list): `PyQt6.QtCore`, `PyQt6.QtWidgets`, `copy`, `pl_gui.settings.settings_view.group_widget`, `pl_gui.settings.settings_view.styles`, `src.applications.base.app_dialog`, `src.applications.base.i_application_view`, `src.applications.base.keyboard_settings_view`, `src.applications.base.styled_message_box`, `src.applications.base.widgets.custom_virtual_keyboard`, `src.applications.base.widgets.keyboard_number_field`, `src.applications.modbus_settings.model.mapper`, `src.applications.modbus_settings.view.modbus_settings_schema`, `src.engine.hardware.communication.transport_registry`.

### `_make_scroll`

```python
def _make_scroll(widget: QWidget) -> QScrollArea
```

Vertical scroll only — horizontal never overflows.

### `ModbusSettingsView`

```python
class ModbusSettingsView(IApplicationView):
```

View — pure Qt widget. No services, no model, no business logic.

Declared fields/defaults:

```python
save_requested = pyqtSignal(dict)
detect_ports_requested = pyqtSignal()
grant_permission_requested = pyqtSignal()
set_low_latency_requested = pyqtSignal()
test_connection_requested = pyqtSignal()
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, parent=None)
```

```python
def setup_ui(self) -> None
```

```python
def load_config(self, config) -> None
```

```python
def get_values(self) -> dict
```

```python
def get_profile_values(self) -> dict[str, dict]
```

```python
def get_slave_values(self) -> dict[str, dict]
```

```python
def set_detected_ports(self, ports: list) -> None
```

```python
def set_connection_result(self, success: bool, port: str='') -> None
```

```python
def set_save_result(self, success: bool, message: str) -> None
```

```python
def set_permission_result(self, success: bool, ports: list) -> None
```

```python
def set_low_latency_result(self, success: bool, ports: list, error: str='') -> None
```

```python
def set_busy(self, busy: bool) -> None
```

```python
def clean_up(self) -> None
```

```python
def retranslateUi(self) -> None
```

```python
def changeEvent(self, event) -> None
```

### `_ModbusProfileDialog`

```python
class _ModbusProfileDialog(AppDialog):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, values: dict | None=None, name: str='', parent=None)
```

```python
def get_values(self) -> tuple[str, dict]
```

### `_ModbusSlaveDialog`

```python
class _ModbusSlaveDialog(AppDialog):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, values: dict | None=None, name: str='', profile_names: list[str] | None=None, transport_descriptors=(), parent=None)
```

```python
def get_values(self) -> tuple[str, dict]
```
