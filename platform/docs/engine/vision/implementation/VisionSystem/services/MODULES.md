# Module reference: `src/engine/vision/implementation/VisionSystem/services`

[Package guide](README.md) · [Complete source index](../../../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [aruco_detection_service.py](#aruco_detection_servicepy)
- [brightness_service.py](#brightness_servicepy)
- [calibration_service.py](#calibration_servicepy)
- [contour_detection_service.py](#contour_detection_servicepy)
- [qr_detection_service.py](#qr_detection_servicepy)

## `__init__.py`

Source: [src/engine/vision/implementation/VisionSystem/services/__init__.py](../../../../../../src/engine/vision/implementation/VisionSystem/services/__init__.py).

Imports (including optional/function-local imports; not a startup dependency list): `src.engine.vision.implementation.VisionSystem.services.aruco_detection_service`, `src.engine.vision.implementation.VisionSystem.services.brightness_service`, `src.engine.vision.implementation.VisionSystem.services.calibration_service`, `src.engine.vision.implementation.VisionSystem.services.contour_detection_service`, `src.engine.vision.implementation.VisionSystem.services.qr_detection_service`.

Package-level import/export surface:

```python
from src.engine.vision.implementation.VisionSystem.services.contour_detection_service import ContourDetectionService
from src.engine.vision.implementation.VisionSystem.services.calibration_service import CalibrationService, CalibrationOutcome
from src.engine.vision.implementation.VisionSystem.services.aruco_detection_service import ArucoDetectionService
from src.engine.vision.implementation.VisionSystem.services.brightness_service import BrightnessService
from src.engine.vision.implementation.VisionSystem.services.qr_detection_service import QrDetectionService
```

No top-level functions, classes or public value declarations; inspect the source for imports or entry-point statements.

## `aruco_detection_service.py`

Source: [src/engine/vision/implementation/VisionSystem/services/aruco_detection_service.py](../../../../../../src/engine/vision/implementation/VisionSystem/services/aruco_detection_service.py).

Imports (including optional/function-local imports; not a startup dependency list): `cv2`, `logging`, `numpy`, `src.engine.vision.implementation.VisionSystem.core.settings.CameraSettings`, `src.engine.vision.implementation.plvision.PLVision.arucoModule`, `typing`.

### `ArucoDetectionService`

```python
class ArucoDetectionService:
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, camera_settings: CameraSettings)
```

```python
def detect(self, corrected_image: Optional[np.ndarray], flip: Optional[bool]=None, image: Optional[np.ndarray]=None) -> Tuple
```

## `brightness_service.py`

Source: [src/engine/vision/implementation/VisionSystem/services/brightness_service.py](../../../../../../src/engine/vision/implementation/VisionSystem/services/brightness_service.py).

Imports (including optional/function-local imports; not a startup dependency list): `logging`, `numpy`, `src.engine.vision.implementation.VisionSystem.core.settings.CameraSettings`, `src.engine.vision.implementation.plvision.PLVision.PID.BrightnessController`, `typing`.

### `BrightnessService`

```python
class BrightnessService:
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, camera_settings: CameraSettings, area_points_provider: Optional[Callable[[], np.ndarray | None]]=None, area_key_provider: Optional[Callable[[], str]]=None)
```

```python
def on_brightness_toggle(self, mode: str) -> None
```

```python
def adjust(self, image: np.ndarray) -> np.ndarray
```

```python
def lock_current_area(self) -> bool
```

```python
def unlock_area(self) -> None
```

```python
def lock_adjustment(self) -> None
```

```python
def unlock_adjustment(self) -> None
```

## `calibration_service.py`

Source: [src/engine/vision/implementation/VisionSystem/services/calibration_service.py](../../../../../../src/engine/vision/implementation/VisionSystem/services/calibration_service.py).

Imports (including optional/function-local imports; not a startup dependency list): `dataclasses`, `logging`, `numpy`, `src.engine.vision.implementation.VisionSystem.core.settings.CameraSettings`, `src.engine.vision.implementation.VisionSystem.features.calibration.cameraCalibration.CameraCalibrationService`, `typing`.

### `CalibrationOutcome`

```python
@dataclass
class CalibrationOutcome:
```

Declared fields/defaults:

```python
success: bool
message: str
camera_matrix: Optional[np.ndarray] = field(default=None)
distortion_coefficients: Optional[np.ndarray] = field(default=None)
perspective_matrix: Optional[np.ndarray] = field(default=None)
```

### `CalibrationService`

```python
class CalibrationService:
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, camera_settings: CameraSettings, storage_path: str, message_publisher=None, messaging_service=None)
```

```python
def capture_image(self, raw_image: Optional[np.ndarray]) -> tuple[bool, str]
```

```python
def calibrate(self, raw_image: Optional[np.ndarray]) -> CalibrationOutcome
```

## `contour_detection_service.py`

Source: [src/engine/vision/implementation/VisionSystem/services/contour_detection_service.py](../../../../../../src/engine/vision/implementation/VisionSystem/services/contour_detection_service.py).

Imports (including optional/function-local imports; not a startup dependency list): `cv2`, `logging`, `numpy`, `src.engine.robot.path_interpolation.new_interpolation.interpolation_pipeline`, `src.engine.vision.implementation.VisionSystem.core.settings.CameraSettings`, `src.engine.vision.implementation.plvision.PLVision`, `typing`.

### `ContourDetectionService`

```python
class ContourDetectionService:
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, camera_settings: CameraSettings, message_publisher=None)
```

```python
def detect(self, image: np.ndarray, threshold: int, is_calibrated: bool, correct_image_fn: Callable[[np.ndarray], np.ndarray], spray_area_points: Optional[np.ndarray], sort: bool=False, publish_images: bool=True) -> Tuple[Optional[List], Optional[np.ndarray], None]
```

## `qr_detection_service.py`

Source: [src/engine/vision/implementation/VisionSystem/services/qr_detection_service.py](../../../../../../src/engine/vision/implementation/VisionSystem/services/qr_detection_service.py).

Imports (including optional/function-local imports; not a startup dependency list): `cv2`, `logging`, `numpy`, `pyzbar.pyzbar`, `typing`.

### `QrDetectionService`

```python
class QrDetectionService:
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def detect(self, image: Optional[np.ndarray]) -> Optional[str]
```
