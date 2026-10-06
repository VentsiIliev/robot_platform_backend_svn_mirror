# Module reference: `src/applications/camera_settings/controller`

[Package guide](README.md) · [Complete source index](../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [camera_devices_controller.py](#camera_devices_controllerpy)
- [camera_settings_controller.py](#camera_settings_controllerpy)

## `camera_devices_controller.py`

Source: [src/applications/camera_settings/controller/camera_devices_controller.py](../../../../src/applications/camera_settings/controller/camera_devices_controller.py).

Imports (including optional/function-local imports; not a startup dependency list): `PyQt6.QtCore`, `__future__`, `src.applications.base.background_worker`, `src.applications.base.i_application_controller`, `src.applications.camera_settings.model.camera_settings_model`, `src.applications.camera_settings.service.i_camera_settings_service`, `src.applications.camera_settings.view.camera_devices_widget`, `src.engine.core.i_messaging_service`, `src.shared_contracts.events.vision_events`, `threading`.

### `CameraDevicesController`

```python
class CameraDevicesController(IApplicationController, BackgroundWorker):
```

Reusable controller for the camera-role assignment and preview panel.

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, model: CameraSettingsModel, view: CameraDevicesWidget, messaging: IMessagingService) -> None
```

```python
def load(self) -> None
```

```python
def stop(self) -> None
```

## `camera_settings_controller.py`

Source: [src/applications/camera_settings/controller/camera_settings_controller.py](../../../../src/applications/camera_settings/controller/camera_settings_controller.py).

Imports (including optional/function-local imports; not a startup dependency list): `PyQt6.QtCore`, `logging`, `src.applications.base.background_worker`, `src.applications.base.broker_subscription_mixin`, `src.applications.base.i_application_controller`, `src.applications.camera_settings.mapper`, `src.applications.camera_settings.model.camera_settings_model`, `src.applications.camera_settings.service.i_camera_settings_service`, `src.applications.camera_settings.view.camera_settings_view`, `src.engine.core.i_messaging_service`, `src.shared_contracts.events.vision_events`.

### `_Bridge`

```python
class _Bridge(SignalBridge):
```

Declared fields/defaults:

```python
camera_frame = pyqtSignal(object)
threshold_frame = pyqtSignal(object)
vision_state = pyqtSignal(str)
```

### `CameraSettingsController`

```python
class CameraSettingsController(IApplicationController, BrokerSubscriptionMixin, BackgroundWorker):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, model: CameraSettingsModel, view: CameraSettingsView, messaging: IMessagingService)
```

```python
def load(self) -> None
```

```python
def stop(self) -> None
```
