# Module reference: `src/applications/device_control/view`

[Package guide](README.md) · [Complete source index](../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [device_control_view.py](#device_control_viewpy)

## `device_control_view.py`

Source: [src/applications/device_control/view/device_control_view.py](../../../../src/applications/device_control/view/device_control_view.py).

Imports (including optional/function-local imports; not a startup dependency list): `PyQt6.QtCore`, `PyQt6.QtWidgets`, `__future__`, `functools`, `pl_gui.settings.settings_view.styles`, `pl_gui.utils.utils_widgets.SwitchButton`, `src.applications.base.app_styles`, `src.applications.base.i_application_view`, `src.applications.device_control.service.i_device_control_service`, `typing`.

### `DeviceControlView`

```python
class DeviceControlView(IApplicationView):
```

Declared fields/defaults:

```python
laser_on_requested = pyqtSignal()
laser_off_requested = pyqtSignal()
vacuum_pump_on_requested = pyqtSignal()
vacuum_pump_off_requested = pyqtSignal()
motor_on_requested = pyqtSignal(int)
motor_off_requested = pyqtSignal(int)
generator_on_requested = pyqtSignal()
generator_off_requested = pyqtSignal()
device_action_requested = pyqtSignal(str, str)
device_enabled_requested = pyqtSignal(str, bool)
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, parent=None)
```

```python
def setup_ui(self) -> None
```

```python
def setup_devices(self, devices: List[IDeviceControlDevice]) -> None
```

```python
def set_device_panel(self, device_key: str, panel: QWidget) -> None
```

Add an optional device-specific panel to an existing device tab.

```python
def add_custom_tab(self, key: str, label: str, panel: QWidget) -> None
```

Add a lifecycle-managed extension panel without device toggles.

```python
def set_device_state(self, device_key: str, state: dict[str, object]) -> None
```

```python
def set_device_busy(self, device_key: str, busy: bool) -> None
```

```python
def set_device_enabled(self, device_key: str, enabled: bool) -> None
```

```python
def set_device_action_result(self, device_key: str, success: bool) -> None
```

```python
def setup_motors(self, motors: List[MotorEntry]) -> None
```

```python
def set_device_available(self, key: str, available: bool) -> None
```

```python
def set_motors_available(self, available: bool) -> None
```

```python
def set_device_active(self, key: str, active: bool) -> None
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
