# Module reference: `src/engine/vision`

[Package guide](README.md) · [Complete source index](../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [calibration_vision_settings.py](#calibration_vision_settingspy)
- [camera_device_settings.py](#camera_device_settingspy)
- [camera_settings_serializer.py](#camera_settings_serializerpy)
- [camera_stream_publisher.py](#camera_stream_publisherpy)
- [capture_snapshot_service.py](#capture_snapshot_servicepy)
- [frame_orientation.py](#frame_orientationpy)
- [homography_residual_transformer.py](#homography_residual_transformerpy)
- [homography_transformer.py](#homography_transformerpy)
- [i_capture_snapshot_service.py](#i_capture_snapshot_servicepy)
- [i_exposure_control.py](#i_exposure_controlpy)
- [i_vision_service.py](#i_vision_servicepy)
- [simulation_coordinate_transformer.py](#simulation_coordinate_transformerpy)
- [vision_service.py](#vision_servicepy)

## `__init__.py`

Source: [src/engine/vision/__init__.py](../../../src/engine/vision/__init__.py).

Imports (including optional/function-local imports; not a startup dependency list): `src.engine.vision.capture_snapshot_service`, `src.engine.vision.i_capture_snapshot_service`, `src.engine.vision.i_vision_service`, `src.engine.vision.vision_service`.

Package-level import/export surface:

```python
from src.engine.vision.capture_snapshot_service import CaptureSnapshotService
from src.engine.vision.i_capture_snapshot_service import ICaptureSnapshotService, VisionCaptureSnapshot
from src.engine.vision.i_vision_service import IVisionService
from src.engine.vision.vision_service import VisionService
```

Module declarations (expressions are shown without evaluating them):

```python
__all__ = ['CaptureSnapshotService', 'ICaptureSnapshotService', 'IVisionService', 'VisionCaptureSnapshot', 'VisionService']
```

## `calibration_vision_settings.py`

Source: [src/engine/vision/calibration_vision_settings.py](../../../src/engine/vision/calibration_vision_settings.py).

Imports (including optional/function-local imports; not a startup dependency list): `dataclasses`, `src.engine.repositories.interfaces.settings_serializer`, `typing`.

### `CoordinateCalibrationProfile`

```python
@dataclass(frozen=True)
class CoordinateCalibrationProfile:
```

A named pixel-to-robot calibration and the frame it was captured in.

Declared fields/defaults:

```python
matrix_path: str = ''
reference_frame: str = 'calibration'
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def to_dict(self) -> Dict[str, Any]
```

```python
@classmethod
def from_dict(cls, data: Dict[str, Any]) -> 'CoordinateCalibrationProfile'
```

### `CalibrationVisionSettings`

```python
@dataclass
class CalibrationVisionSettings:
```

Declared fields/defaults:

```python
chessboard_width: int = 32
chessboard_height: int = 20
square_size_mm: float = 25.0
reference_board_mode: str = 'auto'
charuco_board_width: int = 0
charuco_board_height: int = 0
charuco_square_size_mm: float = 0.0
charuco_marker_size_mm: float = 0.0
calibration_skip_frames: int = 30
coordinate_calibration_mode: str = 'global'
calibration_target_work_area: str = 'global'
coordinate_calibration_profiles: Dict[str, CoordinateCalibrationProfile] = field(default_factory=dict)
work_area_calibration_profiles: Dict[str, str] = field(default_factory=dict)
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def to_dict(self) -> Dict[str, Any]
```

```python
@classmethod
def from_dict(cls, data: Dict[str, Any]) -> 'CalibrationVisionSettings'
```

### `CalibrationVisionSettingsSerializer`

```python
class CalibrationVisionSettingsSerializer(ISettingsSerializer[CalibrationVisionSettings]):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
@property
def settings_type(self) -> str
```

```python
def get_default(self) -> CalibrationVisionSettings
```

```python
def to_dict(self, settings: CalibrationVisionSettings) -> Dict[str, Any]
```

```python
def from_dict(self, data: Dict[str, Any]) -> CalibrationVisionSettings
```

## `camera_device_settings.py`

Source: [src/engine/vision/camera_device_settings.py](../../../src/engine/vision/camera_device_settings.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `dataclasses`, `src.engine.repositories.interfaces.settings_serializer`, `src.engine.vision.frame_orientation`, `typing`.

Module declarations (expressions are shown without evaluating them):

```python
CameraDevice = int | str
```

### `CameraDeviceSpec`

```python
@dataclass(frozen=True)
class CameraDeviceSpec:
```

Declared fields/defaults:

```python
device: CameraDevice
width: int = 1280
height: int = 720
required: bool = False
flip_horizontal: bool = False
flip_vertical: bool = False
rotate_degrees: int = 0
```

### `CameraDevicesConfig`

```python
@dataclass
class CameraDevicesConfig:
```

Declared fields/defaults:

```python
cameras: dict[str, CameraDeviceSpec] = field(default_factory=dict)
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def get(self, role: str) -> CameraDeviceSpec | None
```

### `CameraDevicesConfigSerializer`

```python
class CameraDevicesConfigSerializer(ISettingsSerializer[CameraDevicesConfig]):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
@property
def settings_type(self) -> str
```

```python
def get_default(self) -> CameraDevicesConfig
```

```python
def to_dict(self, settings: CameraDevicesConfig) -> dict[str, Any]
```

```python
def from_dict(self, data: dict[str, Any]) -> CameraDevicesConfig
```

## `camera_settings_serializer.py`

Source: [src/engine/vision/camera_settings_serializer.py](../../../src/engine/vision/camera_settings_serializer.py).

Imports (including optional/function-local imports; not a startup dependency list): `dataclasses`, `src.engine.repositories.interfaces.settings_serializer`, `src.engine.vision.implementation.VisionSystem.core.settings.CameraSettings`, `typing`.

### `CameraSettings`

```python
@dataclass
class CameraSettings:
```

Declared fields/defaults:

```python
data: Dict[str, Any] = field(default_factory=dict)
```

### `CameraSettingsSerializer`

```python
class CameraSettingsSerializer(ISettingsSerializer[CameraSettings]):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
@property
def settings_type(self) -> str
```

```python
def get_default(self) -> CameraSettings
```

```python
def to_dict(self, settings: CameraSettings) -> Dict[str, Any]
```

```python
def from_dict(self, data: Dict[str, Any]) -> CameraSettings
```

## `camera_stream_publisher.py`

Source: [src/engine/vision/camera_stream_publisher.py](../../../src/engine/vision/camera_stream_publisher.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `cv2`, `logging`, `src.engine.core.i_messaging_service`, `src.engine.vision.frame_orientation`, `src.shared_contracts.events.vision_events`, `threading`, `time`.

### `CameraStreamPublisher`

```python
class CameraStreamPublisher:
```

Own one V4L2 camera and publish its frames on a role-specific topic.

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, role: str, device: str | int, messaging: IMessagingService, width: int=640, height: int=480, fps: int=15, flip_horizontal: bool=False, flip_vertical: bool=False, rotate_degrees: int=0) -> None
```

```python
def start(self) -> None
```

```python
def set_orientation(self, horizontal: bool, vertical: bool, rotate_degrees: int=0) -> None
```

Apply a new capture orientation to every frame published from now on.

```python
def stop(self) -> None
```

## `capture_snapshot_service.py`

Source: [src/engine/vision/capture_snapshot_service.py](../../../src/engine/vision/capture_snapshot_service.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `logging`, `src.engine.robot.interfaces.i_robot_service`, `src.engine.vision.i_capture_snapshot_service`, `src.engine.vision.i_vision_service`, `src.engine.work_areas.i_work_area_service`, `time`, `typing`.

### `ActiveWorkAreaVerificationError`

```python
class ActiveWorkAreaVerificationError(RuntimeError):
```

Raised when a vision capture is blocked by unverified work-area state.

### `CaptureSnapshotService`

```python
class CaptureSnapshotService(ICaptureSnapshotService):
```

Capture the latest vision data and robot pose as one runtime snapshot.

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, vision_service: Optional[IVisionService], robot_service: Optional[IRobotService], work_area_service: Optional[IWorkAreaService]=None, active_work_area_validator: Optional[Callable[[str, Optional[list[float]]], tuple[bool, str]]]=None) -> None
```

```python
def capture_snapshot(self, source: str='') -> VisionCaptureSnapshot
```

## `frame_orientation.py`

Source: [src/engine/vision/frame_orientation.py](../../../src/engine/vision/frame_orientation.py).

Shared capture-frame orientation transform. Every camera capture path applies the same flip/rotate transform before a frame is handed to any consumer: the primary ``FrameGrabber`` and each auxiliary ``CameraStreamPublisher``. The transform lives here so the two paths cannot drift apart. Ordering is fixed and load-bearing: rotation is applied first, then the mirror. That keeps ``flip_vertical`` meaning "mirror the image as displayed" regardless of the configured rotation.

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `cv2`.

Module declarations (expressions are shown without evaluating them):

```python
VALID_ROTATION_DEGREES = (0, 90, 180, 270)
TRANSPOSING_ROTATION_DEGREES = (90, 270)
```

### `normalize_rotation`

```python
def normalize_rotation(degrees) -> int
```

Validate a configured rotation and return its canonical value. Accepts any integer degree count and folds it into 0/90/180/270. ``bool`` is rejected explicitly because it is an ``int`` subclass and would otherwise silently normalize to 0 or 1.

### `is_transposing`

```python
def is_transposing(rotate_degrees: int) -> bool
```

True when *rotate_degrees* swaps the frame width and height.

### `apply_orientation`

```python
def apply_orientation(frame, horizontal: bool=False, vertical: bool=False, rotate_degrees: int=0)
```

Rotate then mirror *frame*, returning a new array. The input is never modified. An identity orientation returns *frame* unchanged, so the caller pays nothing for the default configuration.

## `homography_residual_transformer.py`

Source: [src/engine/vision/homography_residual_transformer.py](../../../src/engine/vision/homography_residual_transformer.py).

Imports (including optional/function-local imports; not a startup dependency list): `json`, `logging`, `numpy`, `os`, `scipy.optimize`, `src.engine.core.i_coordinate_transformer`, `src.engine.robot.calibration.robot_calibration.metrics`, `typing`.

### `_env_flag`

```python
def _env_flag(name: str, default: bool=False) -> bool
```

### `HomographyResidualTransformer`

```python
class HomographyResidualTransformer(ICoordinateTransformer):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, matrix_path: str, camera_to_tcp_x_offset: float=_MISSING, camera_to_tcp_y_offset: float=_MISSING)
```

```python
def is_available(self) -> bool
```

```python
def reload(self) -> bool
```

```python
def transform(self, x: float, y: float) -> Tuple[float, float]
```

```python
def transform_to_tcp(self, x: float, y: float) -> Tuple[float, float]
```

```python
def inverse_transform(self, x: float, y: float) -> Tuple[float, float]
```

```python
def inverse_transform_points(self, robot_xy_points) -> np.ndarray
```

Batch inverse for dense editor previews without one optimizer per point.

## `homography_transformer.py`

Source: [src/engine/vision/homography_transformer.py](../../../src/engine/vision/homography_transformer.py).

Imports (including optional/function-local imports; not a startup dependency list): `logging`, `numpy`, `src.engine.core.i_coordinate_transformer`, `typing`.

### `HomographyTransformer`

```python
class HomographyTransformer(ICoordinateTransformer):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, matrix_path: str, camera_to_tcp_x_offset: float=_MISSING, camera_to_tcp_y_offset: float=_MISSING)
```

```python
def is_available(self) -> bool
```

```python
def reload(self) -> bool
```

```python
def transform(self, x: float, y: float) -> Tuple[float, float]
```

```python
def transform_to_tcp(self, x: float, y: float) -> Tuple[float, float]
```

```python
def inverse_transform(self, x: float, y: float) -> Tuple[float, float]
```

## `i_capture_snapshot_service.py`

Source: [src/engine/vision/i_capture_snapshot_service.py](../../../src/engine/vision/i_capture_snapshot_service.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `abc`, `dataclasses`, `numpy`, `typing`.

### `VisionCaptureSnapshot`

```python
@dataclass(frozen=True)
class VisionCaptureSnapshot:
```

Frame/contour snapshot paired with robot pose at capture time.

Declared fields/defaults:

```python
frame: Optional[np.ndarray]
contours: List = field(default_factory=list)
robot_pose: Optional[List[float]] = None
timestamp_s: float = 0.0
source: str = ''
work_area_id: str = ''
```

### `ICaptureSnapshotService`

```python
class ICaptureSnapshotService(ABC):
```

Captures vision data and robot pose as one consistent runtime snapshot.

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
@abstractmethod
def capture_snapshot(self, source: str='') -> VisionCaptureSnapshot
```

Return the latest frame/contours paired with the current robot pose.

## `i_exposure_control.py`

Source: [src/engine/vision/i_exposure_control.py](../../../src/engine/vision/i_exposure_control.py).

Imports (including optional/function-local imports; not a startup dependency list): `abc`.

### `IExposureControl`

```python
class IExposureControl(ABC):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
@abstractmethod
def set_auto_exposure(self, enabled: bool) -> None
```

## `i_vision_service.py`

Source: [src/engine/vision/i_vision_service.py](../../../src/engine/vision/i_vision_service.py).

Imports (including optional/function-local imports; not a startup dependency list): `abc`, `numpy`, `typing`.

### `VisionFrameUnavailableError`

```python
class VisionFrameUnavailableError(RuntimeError):
```

Raised when a fresh camera frame is required but unavailable.

### `IVisionService`

```python
class IVisionService(ABC):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
@abstractmethod
def start(self) -> None
```

```python
@abstractmethod
def stop(self) -> None
```

```python
def pause_processing(self) -> None
```

Suspend acquisition/processing without closing the camera.

```python
def resume_processing(self) -> None
```

Resume acquisition/processing and require fresh frames.

```python
def set_camera_orientation(self, horizontal: bool, vertical: bool, rotate_degrees: int=0) -> None
```

Apply capture orientation to newly acquired frames. ``rotate_degrees`` must be a multiple of 90. A 90 or 270 degree rotation transposes the frame, which ``get_camera_width()`` and ``get_camera_height()`` already account for.

```python
@abstractmethod
def set_raw_mode(self, enabled: bool) -> None
```

```python
@abstractmethod
def capture_calibration_image(self) -> tuple[bool, str]
```

```python
@abstractmethod
def calibrate_camera(self) -> tuple[bool, str]
```

```python
@abstractmethod
def update_settings(self, settings: dict) -> tuple[bool, str]
```

```python
@abstractmethod
def save_work_area(self, area_type: str, pixel_points: List[Tuple[int, int]]) -> tuple[bool, str]
```

```python
@abstractmethod
def get_latest_contours(self) -> list
```

```python
@abstractmethod
def compute_contours_for_latest_frame(self) -> tuple[np.ndarray | None, list]
```

```python
@abstractmethod
def get_work_area(self, area_type: str) -> tuple[bool, str, any]
```

```python
@abstractmethod
def run_matching(self, workpieces: list, contours: list) -> Tuple[dict, int, List, List]
```

```python
@abstractmethod
def get_latest_frame(self) -> np.ndarray
```

```python
@abstractmethod
def get_latest_corrected_frame(self) -> np.ndarray | None
```

```python
@abstractmethod
def get_latest_raw_frame(self) -> np.ndarray | None
```

```python
@abstractmethod
def detect_aruco_markers(self, image: np.ndarray) -> tuple
```

```python
@abstractmethod
def get_camera_width(self) -> int
```

Width of the frames handed out, in pixels, after capture orientation.

```python
@abstractmethod
def get_camera_height(self) -> int
```

Height of the frames handed out, in pixels, after capture orientation.

```python
@abstractmethod
def get_chessboard_width(self) -> int
```

```python
@abstractmethod
def get_chessboard_height(self) -> int
```

```python
@abstractmethod
def get_square_size_mm(self) -> float
```

```python
@abstractmethod
def set_draw_contours(self, enabled: bool) -> None
```

```python
@abstractmethod
def get_auto_brightness_enabled(self) -> bool
```

```python
@abstractmethod
def set_auto_brightness_enabled(self, enabled: bool) -> None
```

```python
@abstractmethod
def lock_auto_brightness_region(self) -> bool
```

```python
@abstractmethod
def unlock_auto_brightness_region(self) -> None
```

```python
@abstractmethod
def lock_auto_brightness_adjustment(self) -> None
```

```python
@abstractmethod
def unlock_auto_brightness_adjustment(self) -> None
```

```python
@property
@abstractmethod
def camera_to_robot_matrix_path(self) -> str
```

```python
@abstractmethod
def set_active_work_area(self, area_id: str | None) -> None
```

Switch the active work area used by vision.

```python
@abstractmethod
def set_detection_area(self, area: str) -> None
```

Compatibility wrapper for switching the active work area.

```python
@abstractmethod
def get_capture_pos_offset(self) -> float
```

## `simulation_coordinate_transformer.py`

Source: [src/engine/vision/simulation_coordinate_transformer.py](../../../src/engine/vision/simulation_coordinate_transformer.py).

No top-level functions, classes or public value declarations; inspect the source for imports or entry-point statements.

## `vision_service.py`

Source: [src/engine/vision/vision_service.py](../../../src/engine/vision/vision_service.py).

Imports (including optional/function-local imports; not a startup dependency list): `logging`, `numpy`, `src.engine.core.i_health_checkable`, `src.engine.vision.i_exposure_control`, `src.engine.vision.i_vision_service`, `src.engine.vision.implementation.VisionSystem.core.external_communication.system_state_management`, `src.engine.vision.implementation.VisionSystem.features.contour_matching`, `src.engine.work_areas.i_work_area_service`.

### `VisionService`

```python
class VisionService(IVisionService, IHealthCheckable, IExposureControl):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, vision_system, work_area_service: IWorkAreaService | None=None)
```

```python
def start(self) -> None
```

```python
def stop(self) -> None
```

```python
def pause_processing(self) -> None
```

```python
def resume_processing(self) -> None
```

```python
def set_raw_mode(self, enabled: bool) -> None
```

```python
def set_camera_orientation(self, horizontal: bool, vertical: bool, rotate_degrees: int=0) -> None
```

```python
def capture_calibration_image(self) -> tuple[bool, str]
```

```python
def calibrate_camera(self) -> tuple[bool, str]
```

```python
def update_settings(self, settings: dict) -> tuple[bool, str]
```

```python
def is_healthy(self) -> bool
```

```python
def get_health_details(self) -> dict
```

```python
def save_work_area(self, area_type: str, pixel_points) -> tuple[bool, str]
```

```python
def get_latest_contours(self) -> list
```

```python
def compute_contours_for_latest_frame(self) -> tuple[np.ndarray | None, list]
```

```python
def get_latest_frame(self) -> np.ndarray
```

```python
def get_latest_corrected_frame(self) -> np.ndarray | None
```

```python
def get_latest_raw_frame(self) -> np.ndarray | None
```

```python
def detect_aruco_markers(self, image: np.ndarray) -> tuple
```

```python
def get_camera_width(self) -> int
```

```python
def get_camera_height(self) -> int
```

```python
def get_chessboard_width(self) -> int
```

```python
def get_chessboard_height(self) -> int
```

```python
def get_square_size_mm(self) -> float
```

```python
def set_draw_contours(self, enabled: bool) -> None
```

```python
def get_auto_brightness_enabled(self) -> bool
```

```python
def set_auto_brightness_enabled(self, enabled: bool) -> None
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

```python
def get_perspective_matrix(self)
```

```python
@property
def camera_to_robot_matrix_path(self) -> str
```

```python
def get_work_area(self, area_type: str) -> tuple[bool, str, any]
```

```python
def run_matching(self, workpieces: list, contours: list)
```

```python
def set_auto_exposure(self, enabled: bool) -> None
```

```python
def set_detection_area(self, area: str) -> None
```

```python
def set_active_work_area(self, area_id: str | None) -> None
```

```python
def get_capture_pos_offset(self) -> float
```
