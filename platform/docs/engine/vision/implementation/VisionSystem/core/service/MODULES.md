# Module reference: `src/engine/vision/implementation/VisionSystem/core/service`

[Package guide](README.md) · [Complete source index](../../../../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [internal_service.py](#internal_servicepy)

## `__init__.py`

Source: [src/engine/vision/implementation/VisionSystem/core/service/__init__.py](../../../../../../../src/engine/vision/implementation/VisionSystem/core/service/__init__.py).

No top-level functions, classes or public value declarations; inspect the source for imports or entry-point statements.

## `internal_service.py`

Source: [src/engine/vision/implementation/VisionSystem/core/service/internal_service.py](../../../../../../../src/engine/vision/implementation/VisionSystem/core/service/internal_service.py).

Imports (including optional/function-local imports; not a startup dependency list): `logging`, `src.engine.vision.implementation.VisionSystem.core.data_loading`, `src.engine.vision.implementation.VisionSystem.core.path_resolver`, `src.engine.vision.implementation.VisionSystem.core.service.interfaces.i_service`, `src.engine.vision.implementation.VisionSystem.core.settings.CameraSettings`, `src.engine.vision.implementation.VisionSystem.core.settings.settings_manager`.

### `Service`

```python
class Service(IService):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, data_storage_path, settings_file_path: str=None)
```

```python
def loadSettings(self)
```

```python
def updateSettings(self, camera_settings, settings: dict, brightness_controller=None, reinit_camera=None) -> tuple[bool, str]
```

```python
def saveSettings(self, settings: dict) -> None
```

```python
def loadPerspectiveMatrix(self)
```

```python
def loadCameraCalibrationData(self)
```

```python
def loadCameraToRobotMatrix(self)
```

```python
def loadWorkAreaPoints(self)
```

```python
def saveWorkAreaPoints(self, data)
```

```python
@property
def cameraData(self)
```

```python
@property
def camera_to_robot_matrix_path(self)
```

```python
@property
def cameraToRobotMatrix(self)
```

```python
@cameraToRobotMatrix.setter
def cameraToRobotMatrix(self, value)
```

```python
@property
def perspectiveMatrix(self)
```

```python
@perspectiveMatrix.setter
def perspectiveMatrix(self, value)
```

```python
@property
def sprayAreaPoints(self)
```

```python
@property
def pickupAreaPoints(self)
```

```python
@property
def workAreaPoints(self)
```

```python
def get_camera_matrix(self)
```

```python
def get_distortion_coefficients(self)
```

```python
@property
def isCalibrated(self) -> bool
```
