# Module reference: `src/applications/aruco_z_probe/controller`

[Package guide](README.md) · [Complete source index](../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [aruco_z_probe_controller.py](#aruco_z_probe_controllerpy)

## `__init__.py`

Source: [src/applications/aruco_z_probe/controller/__init__.py](../../../../src/applications/aruco_z_probe/controller/__init__.py).

No top-level functions, classes or public value declarations; inspect the source for imports or entry-point statements.

## `aruco_z_probe_controller.py`

Source: [src/applications/aruco_z_probe/controller/aruco_z_probe_controller.py](../../../../src/applications/aruco_z_probe/controller/aruco_z_probe_controller.py).

Imports (including optional/function-local imports; not a startup dependency list): `PyQt6.QtCore`, `__future__`, `logging`, `numpy`, `src.applications.aruco_z_probe.model.aruco_z_probe_model`, `src.applications.aruco_z_probe.service.i_aruco_z_probe_service`, `src.applications.aruco_z_probe.view.aruco_z_probe_view`, `src.applications.base.i_application_controller`, `src.engine.core.i_messaging_service`, `src.shared_contracts.events.vision_events`, `threading`, `typing`.

### `_Bridge`

```python
class _Bridge(QObject):
```

Declared fields/defaults:

```python
camera_frame = pyqtSignal(object)
log_message = pyqtSignal(str)
sweep_done = pyqtSignal(bool, str, object)
verify_done = pyqtSignal(bool, str, object)
```

### `_CalibWorker`

```python
class _CalibWorker(QObject):
```

Declared fields/defaults:

```python
log_message = pyqtSignal(str)
finished = pyqtSignal()
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, model: ArucoZProbeModel)
```

```python
def run(self) -> None
```

### `_SweepWorker`

```python
class _SweepWorker(QObject):
```

Declared fields/defaults:

```python
sweep_done = pyqtSignal(bool, str, object)
finished = pyqtSignal()
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, model: ArucoZProbeModel, marker_id: int, min_z: float, sample_count: int, detection_attempts: int, bridge: _Bridge, stabilization_delay: float=0.3)
```

```python
def request_stop(self) -> None
```

```python
def run(self) -> None
```

### `_VerifyWorker`

```python
class _VerifyWorker(QObject):
```

Declared fields/defaults:

```python
verify_done = pyqtSignal(bool, str, object)
finished = pyqtSignal()
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, model: ArucoZProbeModel, z_heights: List[float], marker_id: int, detection_attempts: int, bridge: _Bridge, stabilization_delay: float=0.3)
```

```python
def request_stop(self) -> None
```

```python
def run(self) -> None
```

### `ArucoZProbeController`

```python
class ArucoZProbeController(IApplicationController):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, model: ArucoZProbeModel, view: ArucoZProbeView, messaging: Optional[IMessagingService]=None)
```

```python
def load(self) -> None
```

```python
def stop(self) -> None
```
