# Module reference: `src/applications/device_control/controller`

[Package guide](README.md) · [Complete source index](../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [device_control_controller.py](#device_control_controllerpy)

## `device_control_controller.py`

Source: [src/applications/device_control/controller/device_control_controller.py](../../../../src/applications/device_control/controller/device_control_controller.py).

Imports (including optional/function-local imports; not a startup dependency list): `PyQt6.QtCore`, `__future__`, `concurrent.futures`, `functools`, `logging`, `src.applications.base.background_worker`, `src.applications.base.i_application_controller`, `src.applications.device_control.model.device_control_model`, `src.applications.device_control.view.device_control_view`.

### `_DeviceUiRelay`

```python
class _DeviceUiRelay(QObject):
```

Declared fields/defaults:

```python
action_finished = pyqtSignal(str, bool)
enabled_finished = pyqtSignal(str, bool)
states_finished = pyqtSignal(object)
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, on_action_finished, on_states_finished) -> None
```

### `DeviceControlController`

```python
class DeviceControlController(IApplicationController, BackgroundWorker):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, model: DeviceControlModel, view: DeviceControlView, dryer_view=None, dryer_controller=None, extra_panels=()) -> None
```

```python
def load(self) -> None
```

```python
def stop(self) -> None
```
