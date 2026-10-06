# Module reference: `src/engine/vision/implementation/VisionSystem`

[Package guide](README.md) · [Complete source index](../../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [VisionSystem.py](#visionsystempy)
- [__init__.py](#__init__py)
- [camera_initialization.py](#camera_initializationpy)

## `VisionSystem.py`

Source: [src/engine/vision/implementation/VisionSystem/VisionSystem.py](../../../../../src/engine/vision/implementation/VisionSystem/VisionSystem.py).

Imports (including optional/function-local imports; not a startup dependency list): `cv2`, `logging`, `numpy`, `os`, `src.engine.vision.i_vision_service`, `src.engine.vision.implementation.VisionSystem.camera_initialization`, `src.engine.vision.implementation.VisionSystem.core.camera.frame_grabber`, `src.engine.vision.implementation.VisionSystem.core.camera.remote_camera`, `src.engine.vision.implementation.VisionSystem.core.external_communication.system_state_management`, `src.engine.vision.implementation.VisionSystem.core.path_resolver`, `src.engine.vision.implementation.VisionSystem.core.service.internal_service`, `src.engine.vision.implementation.VisionSystem.services`, `src.engine.vision.implementation.plvision.PLVision.Camera`, `src.engine.work_areas.i_work_area_service`, `threading`, `typing`.

Module declarations (expressions are shown without evaluating them):

```python
DEFAULT_STORAGE_PATH = str(get_path_resolver().vision_system_root / 'storage')
```

### `VisionSystem`

```python
class VisionSystem:
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, storage_path=None, messaging_service=None, service=None, work_area_service: IWorkAreaService | None=None, camera_device: int | str | None=None, camera_resolution: tuple[int, int] | None=None, allow_camera_fallback: bool=True, camera_orientation: tuple[bool, bool, int]=(False, False, 0))
```

```python
def setup_external_communication(self) -> None
```

```python
def setup_camera(self, should_cancel=None) -> None
```

```python
def load_calibration_data(self) -> None
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
def stateTopic(self)
```

```python
@property
def threshold_by_area(self) -> str
```

```python
@threshold_by_area.setter
def threshold_by_area(self, value: str) -> None
```

```python
def run(self)
```

```python
def compute_contours_for_latest_frame(self) -> tuple[np.ndarray | None, list]
```

```python
def correctImage(self, image)
```

```python
def get_latest_frame_for_snapshot(self)
```

```python
def captureCalibrationImage(self) -> tuple[bool, str]
```

```python
def calibrateCamera(self) -> tuple[bool, str]
```

```python
def detectArucoMarkers(self, flip=False, image=None)
```

```python
def detectQrCode(self) -> Optional[str]
```

```python
def updateSettings(self, settings: dict) -> tuple[bool, str]
```

```python
def get_camera_settings(self)
```

```python
def saveWorkAreaPoints(self, data)
```

```python
def getWorkAreaPoints(self, area_type)
```

```python
def on_threshold_update(self, message) -> None
```

```python
def get_thresh_by_area(self, area: str) -> int
```

```python
def start_system(self) -> None
```

```python
def pause_processing(self) -> None
```

Suspend capture and image processing while keeping the camera open.

```python
def resume_processing(self) -> None
```

Resume capture and processing from fresh frames.

```python
def stop_system(self) -> None
```

```python
def lock_auto_brightness_region(self) -> bool
```

```python
def unlock_auto_brightness_region(self) -> None
```

```python
def lock_auto_brightness_adjustment(self) -> None
```

```python
def unlock_auto_brightness_adjustment(self) -> None
```

## `__init__.py`

Source: [src/engine/vision/implementation/VisionSystem/__init__.py](../../../../../src/engine/vision/implementation/VisionSystem/__init__.py).

No top-level functions, classes or public value declarations; inspect the source for imports or entry-point statements.

## `camera_initialization.py`

Source: [src/engine/vision/implementation/VisionSystem/camera_initialization.py](../../../../../src/engine/vision/implementation/VisionSystem/camera_initialization.py).

Imports (including optional/function-local imports; not a startup dependency list): `cv2`, `logging`, `modules.shared.utils`, `platform`, `re`, `src.engine.vision.implementation.plvision.PLVision.Camera`, `time`.

### `CameraInitializer`

```python
class CameraInitializer:
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, width, height)
```

```python
def initializeCameraWithRetry(self, camera_device, max_retries=10, retry_delay=1.0, should_cancel=None, allow_fallback=True)
```

```python
def find_first_available_camera(self, max_devices=10)
```
