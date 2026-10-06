# Module reference: `src/applications/calibration/controller`

[Package guide](README.md) · [Complete source index](../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [calibration_controller.py](#calibration_controllerpy)

## `__init__.py`

Source: [src/applications/calibration/controller/__init__.py](../../../../src/applications/calibration/controller/__init__.py).

No top-level functions, classes or public value declarations; inspect the source for imports or entry-point statements.

## `calibration_controller.py`

Source: [src/applications/calibration/controller/calibration_controller.py](../../../../src/applications/calibration/controller/calibration_controller.py).

Imports (including optional/function-local imports; not a startup dependency list): `PyQt6.QtCore`, `logging`, `src.applications.base.i_application_controller`, `src.applications.calibration.model.calibration_model`, `src.applications.calibration.view.calibration_view`, `src.applications.calibration.view.depth_map_dialog`, `src.applications.calibration_settings.mapper`, `src.applications.height_measuring.service.i_height_measuring_app_service`, `src.applications.intrinsic_calibration_capture.service.i_intrinsic_capture_service`, `src.engine.core.i_messaging_service`, `src.robot_systems.glue.component_ids`, `src.shared_contracts.events.process_events`, `src.shared_contracts.events.robot_events`, `src.shared_contracts.events.vision_events`, `typing`.

### `_Worker`

```python
class _Worker(QObject):
```

Declared fields/defaults:

```python
finished = pyqtSignal(object)
failed = pyqtSignal(str)
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, fn: Callable)
```

```python
def run(self) -> None
```

### `_Bridge`

```python
class _Bridge(QObject):
```

Declared fields/defaults:

```python
camera_frame = pyqtSignal(object)
robot_calibration_status = pyqtSignal(object)
log_received = pyqtSignal(str)
process_finished = pyqtSignal(bool, str)
camera_process_finished = pyqtSignal(bool, str)
stop_btn_enabled = pyqtSignal(bool)
test_btn_enabled = pyqtSignal(bool)
camera_tcp_btn_enabled = pyqtSignal(bool)
camera_z_shift_btn_enabled = pyqtSignal(bool)
marker_height_btn_enabled = pyqtSignal(bool)
area_grid_btn_enabled = pyqtSignal(bool)
test_finished = pyqtSignal(bool, str)
marker_height_finished = pyqtSignal(bool, str)
laser_calibration_finished = pyqtSignal(bool, str)
laser_detect_finished = pyqtSignal(object)
area_grid_finished = pyqtSignal(bool, str)
area_grid_verified = pyqtSignal(bool, str, dict)
area_grid_verify_progress = pyqtSignal(str, str, int, int)
depth_map_btn_enabled = pyqtSignal(bool)
```

### `CalibrationController`

```python
class CalibrationController(IApplicationController):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, model: CalibrationModel, view: CalibrationView, messaging: IMessagingService)
```

```python
def load(self) -> None
```

```python
def stop(self) -> None
```

```python
def is_calibrating(self) -> bool
```
