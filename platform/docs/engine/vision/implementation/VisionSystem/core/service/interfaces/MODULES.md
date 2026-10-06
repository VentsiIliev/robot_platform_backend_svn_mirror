# Module reference: `src/engine/vision/implementation/VisionSystem/core/service/interfaces`

[Package guide](README.md) · [Complete source index](../../../../../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [i_service.py](#i_servicepy)

## `__init__.py`

Source: [src/engine/vision/implementation/VisionSystem/core/service/interfaces/__init__.py](../../../../../../../../src/engine/vision/implementation/VisionSystem/core/service/interfaces/__init__.py).

No top-level functions, classes or public value declarations; inspect the source for imports or entry-point statements.

## `i_service.py`

Source: [src/engine/vision/implementation/VisionSystem/core/service/interfaces/i_service.py](../../../../../../../../src/engine/vision/implementation/VisionSystem/core/service/interfaces/i_service.py).

Imports (including optional/function-local imports; not a startup dependency list): `abc`, `typing`.

### `IService`

```python
class IService(ABC):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
@abstractmethod
def updateSettings(self, camera_settings, settings: dict, brightness_controller=None, reinit_camera=None) -> Tuple[bool, str]
```

```python
@abstractmethod
def loadPerspectiveMatrix(self)
```

Load perspective matrix from storage

```python
@abstractmethod
def loadCameraCalibrationData(self)
```

Load camera calibration data

```python
@abstractmethod
def loadCameraToRobotMatrix(self)
```

Load camera-to-robot homography

```python
@abstractmethod
def loadWorkAreaPoints(self)
```

Load pickup, spray, and work area points

```python
@abstractmethod
def saveWorkAreaPoints(self, data: Any) -> Tuple[bool, str]
```

Save work area points

```python
@property
@abstractmethod
def cameraData(self)
```

```python
@property
@abstractmethod
def cameraToRobotMatrix(self)
```

```python
@cameraToRobotMatrix.setter
@abstractmethod
def cameraToRobotMatrix(self, value)
```

```python
@property
@abstractmethod
def perspectiveMatrix(self)
```

```python
@property
@abstractmethod
def camera_to_robot_matrix_path(self)
```

```python
@property
@abstractmethod
def sprayAreaPoints(self)
```

```python
@abstractmethod
def get_camera_matrix(self)
```

```python
@abstractmethod
def get_distortion_coefficients(self)
```

```python
@property
@abstractmethod
def isCalibrated(self) -> bool
```

True if the vision_service has both camera calibration data and camera-to-robot matrix.
