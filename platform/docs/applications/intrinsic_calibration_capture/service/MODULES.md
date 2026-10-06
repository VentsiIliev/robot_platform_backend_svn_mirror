# Module reference: `src/applications/intrinsic_calibration_capture/service`

[Package guide](README.md) · [Complete source index](../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [i_intrinsic_capture_service.py](#i_intrinsic_capture_servicepy)
- [intrinsic_capture_service.py](#intrinsic_capture_servicepy)

## `__init__.py`

Source: [src/applications/intrinsic_calibration_capture/service/__init__.py](../../../../src/applications/intrinsic_calibration_capture/service/__init__.py).

No top-level functions, classes or public value declarations; inspect the source for imports or entry-point statements.

## `i_intrinsic_capture_service.py`

Source: [src/applications/intrinsic_calibration_capture/service/i_intrinsic_capture_service.py](../../../../src/applications/intrinsic_calibration_capture/service/i_intrinsic_capture_service.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `abc`, `cv2`, `dataclasses`, `numpy`, `typing`.

Module declarations (expressions are shown without evaluating them):

```python
INTRINSIC_CAPTURE_PROGRESS_TOPIC = 'INTRINSIC_CAPTURE_PROGRESS'
ARUCO_DICT_OPTIONS = {'4x4_50': cv2.aruco.DICT_4X4_50, '4x4_100': cv2.aruco.DICT_4X4_100, '4x4_250': cv2.aruco.DICT_4X4_250, '4x4_1000': cv2.aruco.DICT_4X4_1000, '5x5_50': cv2.aruco.DICT_5X5_50, '5x5_100': cv2.aruco.DICT_5X5_100, '5x5_250': cv2.aruco.DICT_5X5_250, '6x6_250': cv2.aruco.DICT_6X6_250}
```

### `IntrinsicCaptureConfig`

```python
@dataclass
class IntrinsicCaptureConfig:
```

Declared fields/defaults:

```python
board_type: str = 'chessboard'
chessboard_width: int = 0
chessboard_height: int = 0
square_size_mm: float = 0.0
aruco_dict: str = '4x4_250'
marker_size_mm: float = 0.0
grid_rows: int = 3
grid_cols: int = 3
margin_px: float = 60.0
tilt_deg: float = 5.0
z_delta_mm: float = 40.0
probe_dx_mm: float = 20.0
probe_dy_mm: float = 20.0
probe_drx_deg: float = 3.0
probe_dry_deg: float = 3.0
probe_drz_deg: float = 0.0
charuco_sweep_x_mm: float = 100.0
charuco_sweep_y_mm: float = 100.0
charuco_min_corners: int = 6
charuco_rz_deg: float = 15.0
charuco_compute_hand_eye: bool = True
velocity: int = 20
acceleration: int = 10
stabilization_delay_s: float = 0.5
max_detection_retries: int = 1
initial_detection_attempts: int = 5
initial_detection_delay_s: float = 1.0
output_dir: str = field(default='')
```

### `IIntrinsicCaptureService`

```python
class IIntrinsicCaptureService(ABC):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
@abstractmethod
def start_capture(self) -> None
```

```python
@abstractmethod
def stop_capture(self) -> None
```

```python
@abstractmethod
def is_running(self) -> bool
```

```python
@abstractmethod
def get_latest_frame(self) -> Optional[np.ndarray]
```

```python
@abstractmethod
def get_config(self) -> IntrinsicCaptureConfig
```

```python
@abstractmethod
def save_config(self, config: IntrinsicCaptureConfig) -> None
```

## `intrinsic_capture_service.py`

Source: [src/applications/intrinsic_calibration_capture/service/intrinsic_capture_service.py](../../../../src/applications/intrinsic_calibration_capture/service/intrinsic_capture_service.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `cv2`, `dataclasses`, `json`, `logging`, `numpy`, `os`, `src.applications.intrinsic_calibration_capture.service.i_intrinsic_capture_service`, `src.engine.common_settings_ids`, `src.engine.robot.calibration.intrinsic_capture`, `src.engine.vision.implementation.VisionSystem.features.calibration.cameraCalibration.CameraCalibrationService`, `src.engine.vision.implementation.VisionSystem.features.calibration.charuco`, `threading`, `typing`.

### `IntrinsicCaptureService`

```python
class IntrinsicCaptureService(IIntrinsicCaptureService):
```

Drives the automated intrinsic calibration dataset capture using the platform's IRobotService and IVisionService.

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, robot_service, vision_service, robot_config, messaging=None, default_output_dir: str | None=None, settings_service=None)
```

```python
def start_capture(self) -> None
```

```python
def stop_capture(self) -> None
```

```python
def is_running(self) -> bool
```

```python
def get_latest_frame(self) -> Optional[np.ndarray]
```

```python
def get_config(self) -> IntrinsicCaptureConfig
```

```python
def save_config(self, config: IntrinsicCaptureConfig) -> None
```
