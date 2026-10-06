# Module reference: `src/engine/robot/height_measuring`

[Package guide](README.md) · [Complete source index](../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [area_grid_height_model.py](#area_grid_height_modelpy)
- [depth_map_data.py](#depth_map_datapy)
- [height_correction_service.py](#height_correction_servicepy)
- [height_measuring_service.py](#height_measuring_servicepy)
- [i_height_correction_service.py](#i_height_correction_servicepy)
- [i_height_measuring_service.py](#i_height_measuring_servicepy)
- [laser_calibration_data.py](#laser_calibration_datapy)
- [laser_calibration_service.py](#laser_calibration_servicepy)
- [laser_detection_service.py](#laser_detection_servicepy)
- [laser_detector.py](#laser_detectorpy)
- [piecewise_bilinear_height_model.py](#piecewise_bilinear_height_modelpy)
- [robot_system_height_measuring_provider.py](#robot_system_height_measuring_providerpy)
- [service_builders.py](#service_builderspy)
- [settings.py](#settingspy)

## `__init__.py`

Source: [src/engine/robot/height_measuring/__init__.py](../../../../src/engine/robot/height_measuring/__init__.py).

Imports (including optional/function-local imports; not a startup dependency list): `src.engine.robot.height_measuring.depth_map_data`, `src.engine.robot.height_measuring.height_measuring_service`, `src.engine.robot.height_measuring.i_height_measuring_service`, `src.engine.robot.height_measuring.laser_calibration_data`, `src.engine.robot.height_measuring.laser_calibration_service`, `src.engine.robot.height_measuring.laser_detection_service`, `src.engine.robot.height_measuring.laser_detector`, `src.engine.robot.height_measuring.robot_system_height_measuring_provider`, `src.engine.robot.height_measuring.service_builders`, `src.engine.robot.height_measuring.settings`.

Package-level import/export surface:

```python
from src.engine.robot.height_measuring.i_height_measuring_service import IHeightMeasuringService
from src.engine.robot.height_measuring.settings import LaserDetectionSettings, LaserCalibrationSettings, HeightMeasuringSettings, HeightMeasuringModuleSettings, HeightMeasuringSettingsSerializer
from src.engine.robot.height_measuring.laser_calibration_data import LaserCalibrationData, LaserCalibrationDataSerializer, LaserCalibrationRepository
from src.engine.robot.height_measuring.depth_map_data import DepthMapData, DepthMapDataSerializer, DepthMapRepository
from src.engine.robot.height_measuring.laser_detector import LaserDetector
from src.engine.robot.height_measuring.laser_detection_service import LaserDetectionService
from src.engine.robot.height_measuring.laser_calibration_service import LaserCalibrationService
from src.engine.robot.height_measuring.height_measuring_service import HeightMeasuringService
from src.engine.robot.height_measuring.robot_system_height_measuring_provider import RobotSystemHeightMeasuringProvider
from src.engine.robot.height_measuring.service_builders import build_robot_system_height_measuring_services
```

Module declarations (expressions are shown without evaluating them):

```python
__all__ = ['IHeightMeasuringService', 'LaserDetectionSettings', 'LaserCalibrationSettings', 'HeightMeasuringSettings', 'HeightMeasuringModuleSettings', 'HeightMeasuringSettingsSerializer', 'LaserCalibrationData', 'LaserCalibrationDataSerializer', 'LaserCalibrationRepository', 'LaserDetector', 'LaserDetectionService', 'LaserCalibrationService', 'HeightMeasuringService', 'RobotSystemHeightMeasuringProvider', 'build_robot_system_height_measuring_services']
```

## `area_grid_height_model.py`

Source: [src/engine/robot/height_measuring/area_grid_height_model.py](../../../../src/engine/robot/height_measuring/area_grid_height_model.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `dataclasses`, `math`, `matplotlib.tri`, `numpy`, `re`, `src.engine.robot.height_measuring.depth_map_data`.

### `AreaGridVerificationPoint`

```python
@dataclass(frozen=True)
class AreaGridVerificationPoint:
```

Declared fields/defaults:

```python
name: str
source: str
interpolation_mode: str
x: float
y: float
predicted_height: float
```

### `AreaGridCellPrediction`

```python
@dataclass(frozen=True)
class AreaGridCellPrediction:
```

Declared fields/defaults:

```python
row: int
col: int
source: str
interpolation_mode: str
x: float
y: float
z: float
```

### `AreaGridHeightModel`

```python
class AreaGridHeightModel:
```

Grid-aware height model that reconstructs missing planned nodes for rendering and inference.

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, rows: int, cols: int, planned_xy_by_rc: dict[tuple[int, int], tuple[float, float]], measured_xyz_by_rc: dict[tuple[int, int], tuple[float, float, float]], unavailable_rc: set[tuple[int, int]] | None=None, support_xyz: list[tuple[float, float, float]] | None=None)
```

```python
@classmethod
def from_depth_map(cls, data: DepthMapData) -> 'AreaGridHeightModel'
```

```python
def is_supported(self) -> bool
```

```python
def point_items(self) -> list[tuple[str, tuple[float, float, float]]]
```

```python
def point_status_items(self) -> list[tuple[str, tuple[float, float, float], str]]
```

```python
def missing_labels(self) -> list[str]
```

```python
def triangulation(self) -> Triangulation | None
```

```python
def triangulation_data(self)
```

```python
def interpolate_height(self, x: float, y: float) -> tuple[float | None, str]
```

```python
def verification_points(self) -> list[AreaGridVerificationPoint]
```

## `depth_map_data.py`

Source: [src/engine/robot/height_measuring/depth_map_data.py](../../../../src/engine/robot/height_measuring/depth_map_data.py).

Imports (including optional/function-local imports; not a startup dependency list): `dataclasses`, `src.engine.repositories.interfaces.settings_serializer`, `src.engine.repositories.json.base_json_settings_repository`, `typing`.

### `DepthMapData`

```python
@dataclass
class DepthMapData:
```

Declared fields/defaults:

```python
area_id: str = ''
points: List[List[float]] = field(default_factory=list)
marker_ids: List[int] = field(default_factory=list)
point_labels: List[str] = field(default_factory=list)
grid_rows: int = 0
grid_cols: int = 0
planned_points: List[List[float]] = field(default_factory=list)
planned_point_labels: List[str] = field(default_factory=list)
unavailable_point_labels: List[str] = field(default_factory=list)
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def has_data(self) -> bool
```

### `DepthMapLibraryData`

```python
@dataclass
class DepthMapLibraryData:
```

Declared fields/defaults:

```python
maps: Dict[str, DepthMapData] = field(default_factory=dict)
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def get(self, area_id: str) -> DepthMapData | None
```

```python
def set(self, area_id: str, data: DepthMapData) -> None
```

### `DepthMapLibraryDataSerializer`

```python
class DepthMapLibraryDataSerializer(ISettingsSerializer[DepthMapLibraryData]):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
@property
def settings_type(self) -> str
```

```python
def get_default(self) -> DepthMapLibraryData
```

```python
def to_dict(self, data: DepthMapLibraryData) -> Dict[str, Any]
```

```python
def from_dict(self, raw: Dict[str, Any]) -> DepthMapLibraryData
```

### `DepthMapDataSerializer`

```python
class DepthMapDataSerializer(DepthMapLibraryDataSerializer):
```

Backwards-compatible alias for the common depth-map settings spec.

### `DepthMapRepository`

```python
class DepthMapRepository(BaseJsonSettingsRepository[DepthMapLibraryData]):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, file_path: str)
```

### `_depth_map_to_dict`

```python
def _depth_map_to_dict(data: DepthMapData) -> Dict[str, Any]
```

### `_depth_map_from_dict`

```python
def _depth_map_from_dict(raw: Dict[str, Any]) -> DepthMapData
```

## `height_correction_service.py`

Source: [src/engine/robot/height_measuring/height_correction_service.py](../../../../src/engine/robot/height_measuring/height_correction_service.py).

Imports (including optional/function-local imports; not a startup dependency list): `logging`, `src.engine.robot.height_measuring.area_grid_height_model`, `src.engine.robot.height_measuring.i_height_correction_service`, `src.engine.robot.height_measuring.i_height_measuring_service`, `typing`.

### `HeightCorrectionService`

```python
class HeightCorrectionService(IHeightCorrectionService):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, height_service: 'IHeightMeasuringService', area_id: str='')
```

```python
def reload(self) -> None
```

```python
def predict_z(self, x: float, y: float) -> float | None
```

## `height_measuring_service.py`

Source: [src/engine/robot/height_measuring/height_measuring_service.py](../../../../src/engine/robot/height_measuring/height_measuring_service.py).

Imports (including optional/function-local imports; not a startup dependency list): `logging`, `numpy`, `sklearn.linear_model`, `sklearn.preprocessing`, `src.engine.repositories.interfaces.settings_repository`, `src.engine.robot.height_measuring.depth_map_data`, `src.engine.robot.height_measuring.i_height_measuring_service`, `src.engine.robot.height_measuring.laser_calibration_data`, `src.engine.robot.height_measuring.laser_detection_service`, `src.engine.robot.height_measuring.settings`, `src.engine.robot.interfaces`, `time`, `typing`.

### `HeightMeasuringService`

```python
class HeightMeasuringService(IHeightMeasuringService):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, laser_service: LaserDetectionService, robot_service: IRobotService, repository: ISettingsRepository, config: Optional[HeightMeasuringSettings]=None, tool: int=0, user: int=0, depth_map_repository: Optional[ISettingsRepository]=None)
```

```python
def is_calibrated(self) -> bool
```

```python
def get_calibration_data(self) -> Optional[LaserCalibrationData]
```

```python
def reload_calibration(self) -> None
```

```python
def save_height_map(self, samples: List[List[float]], area_id: str='', marker_ids: Optional[List[int]]=None, point_labels: Optional[List[str]]=None, grid_rows: int=0, grid_cols: int=0, planned_points: Optional[List[List[float]]]=None, planned_point_labels: Optional[List[str]]=None, unavailable_point_labels: Optional[List[str]]=None) -> None
```

```python
def get_depth_map_data(self, area_id: str='') -> Optional[DepthMapData]
```

```python
def begin_measurement_session(self) -> None
```

```python
def end_measurement_session(self) -> None
```

```python
def measure_at(self, x: float, y: float, *, already_at_xy: bool=False) -> Optional[float]
```

## `i_height_correction_service.py`

Source: [src/engine/robot/height_measuring/i_height_correction_service.py](../../../../src/engine/robot/height_measuring/i_height_correction_service.py).

Imports (including optional/function-local imports; not a startup dependency list): `abc`.

### `IHeightCorrectionService`

```python
class IHeightCorrectionService(ABC):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
@abstractmethod
def predict_z(self, x: float, y: float) -> float | None
```

Interpolated surface height in mm at robot position (x, y). Returns None when no model is loaded or the point cannot be covered.

```python
@abstractmethod
def reload(self) -> None
```

Discard cached model — next predict_z call rebuilds from storage.

## `i_height_measuring_service.py`

Source: [src/engine/robot/height_measuring/i_height_measuring_service.py](../../../../src/engine/robot/height_measuring/i_height_measuring_service.py).

Imports (including optional/function-local imports; not a startup dependency list): `abc`, `src.engine.robot.height_measuring.depth_map_data`, `src.engine.robot.height_measuring.laser_calibration_data`, `typing`.

### `IHeightMeasuringService`

```python
class IHeightMeasuringService(ABC):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
@abstractmethod
def begin_measurement_session(self) -> None
```

```python
@abstractmethod
def end_measurement_session(self) -> None
```

```python
@abstractmethod
def measure_at(self, x: float, y: float, *, already_at_xy: bool=False) -> Optional[float]
```

```python
@abstractmethod
def is_calibrated(self) -> bool
```

```python
@abstractmethod
def get_calibration_data(self) -> Optional['LaserCalibrationData']
```

```python
@abstractmethod
def reload_calibration(self) -> None
```

```python
@abstractmethod
def save_height_map(self, samples: List[List[float]], area_id: str='', marker_ids: Optional[List[int]]=None, point_labels: Optional[List[str]]=None, grid_rows: int=0, grid_cols: int=0, planned_points: Optional[List[List[float]]]=None, planned_point_labels: Optional[List[str]]=None, unavailable_point_labels: Optional[List[str]]=None) -> None
```

```python
@abstractmethod
def get_depth_map_data(self, area_id: str='') -> Optional['DepthMapData']
```

## `laser_calibration_data.py`

Source: [src/engine/robot/height_measuring/laser_calibration_data.py](../../../../src/engine/robot/height_measuring/laser_calibration_data.py).

Imports (including optional/function-local imports; not a startup dependency list): `dataclasses`, `src.engine.repositories.interfaces.settings_serializer`, `src.engine.repositories.json.base_json_settings_repository`, `typing`.

### `LaserCalibrationData`

```python
@dataclass
class LaserCalibrationData:
```

Declared fields/defaults:

```python
zero_reference_coords: Optional[List[float]] = None
robot_initial_position: Optional[List[float]] = None
calibration_points: List[List[float]] = field(default_factory=list)
polynomial_coefficients: List[float] = field(default_factory=list)
polynomial_intercept: float = 0.0
polynomial_degree: int = 1
polynomial_mse: float = 0.0
zero_height_offset_mm: float = 0.0
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def is_calibrated(self) -> bool
```

### `LaserCalibrationDataSerializer`

```python
class LaserCalibrationDataSerializer(ISettingsSerializer[LaserCalibrationData]):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
@property
def settings_type(self) -> str
```

```python
def get_default(self) -> LaserCalibrationData
```

```python
def to_dict(self, data: LaserCalibrationData) -> Dict[str, Any]
```

```python
def from_dict(self, raw: Dict[str, Any]) -> LaserCalibrationData
```

### `LaserCalibrationRepository`

```python
class LaserCalibrationRepository(BaseJsonSettingsRepository[LaserCalibrationData]):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, file_path: str)
```

## `laser_calibration_service.py`

Source: [src/engine/robot/height_measuring/laser_calibration_service.py](../../../../src/engine/robot/height_measuring/laser_calibration_service.py).

Imports (including optional/function-local imports; not a startup dependency list): `logging`, `numpy`, `sklearn.linear_model`, `sklearn.model_selection`, `sklearn.preprocessing`, `src.engine.repositories.interfaces.settings_repository`, `src.engine.robot.height_measuring.laser_calibration_data`, `src.engine.robot.height_measuring.laser_detection_service`, `src.engine.robot.height_measuring.settings`, `src.engine.robot.interfaces`, `threading`, `time`, `typing`.

### `LaserCalibrationService`

```python
class LaserCalibrationService:
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, laser_service: LaserDetectionService, robot_service: IRobotService, repository: ISettingsRepository, config: Optional[LaserCalibrationSettings]=None, tool: int=0, user: int=0)
```

```python
def get_calibration_data(self) -> Optional[LaserCalibrationData]
```

```python
def calibrate(self, initial_position: Optional[List[float]]=None, stop_event: threading.Event=None) -> bool
```

## `laser_detection_service.py`

Source: [src/engine/robot/height_measuring/laser_detection_service.py](../../../../src/engine/robot/height_measuring/laser_detection_service.py).

Imports (including optional/function-local imports; not a startup dependency list): `logging`, `numpy`, `src.engine.hardware.laser.i_laser_control`, `src.engine.robot.height_measuring.laser_detector`, `src.engine.robot.height_measuring.settings`, `src.engine.vision.i_exposure_control`, `src.engine.vision.i_vision_service`, `time`, `typing`.

### `LaserDetectionService`

```python
class LaserDetectionService:
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, detector: LaserDetector, laser: ILaserControl, vision_service: IVisionService, config: Optional[LaserDetectionSettings]=None, exposure_control: Optional[IExposureControl]=None)
```

```python
def begin_measurement_session(self) -> None
```

```python
def end_measurement_session(self) -> None
```

```python
def detect(self) -> Tuple[Optional[np.ndarray], Optional[tuple], Optional[Tuple[float, float]]]
```

```python
@property
def laser(self) -> ILaserControl
```

```python
def restore(self) -> None
```

```python
def turn_on(self) -> None
```

```python
def turn_off(self) -> None
```

## `laser_detector.py`

Source: [src/engine/robot/height_measuring/laser_detector.py](../../../../src/engine/robot/height_measuring/laser_detector.py).

Imports (including optional/function-local imports; not a startup dependency list): `cv2`, `logging`, `numpy`, `src.engine.robot.height_measuring.settings`, `typing`.

### `LaserDetector`

```python
class LaserDetector:
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, config: LaserDetectionSettings)
```

```python
def detect_laser_line(self, on_frame: np.ndarray, off_frame: np.ndarray, axis: Optional[str]=None) -> Tuple[Optional[np.ndarray], Optional[tuple], Optional[Tuple[float, float]]]
```

## `piecewise_bilinear_height_model.py`

Source: [src/engine/robot/height_measuring/piecewise_bilinear_height_model.py](../../../../src/engine/robot/height_measuring/piecewise_bilinear_height_model.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `dataclasses`, `matplotlib.tri`, `numpy`, `src.engine.robot.height_measuring.depth_map_data`, `typing`.

Module declarations (expressions are shown without evaluating them):

```python
MARKER_LABELS = {0: 'top left', 1: 'top mid', 2: 'top right', 3: 'mid left', 4: 'mid mid', 5: 'mid right', 6: 'bottom left', 8: 'bottom right', 100: 'center 0/1/3/4', 101: 'center 1/2/4/5', 102: 'center 3/4/6', 103: 'center 4/5/8'}
TOP_LEFT_CENTER = 100
TOP_RIGHT_CENTER = 101
BOTTOM_LEFT_CENTER = 102
BOTTOM_RIGHT_CENTER = 103
```

### `TrianglePatch`

```python
@dataclass(frozen=True)
class TrianglePatch:
```

Declared fields/defaults:

```python
name: str
marker_ids: tuple[int, int, int]
points: np.ndarray
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def centroid(self) -> tuple[float, float, float]
```

### `VerificationPoint`

```python
@dataclass(frozen=True)
class VerificationPoint:
```

Declared fields/defaults:

```python
name: str
patch_name: str
x: float
y: float
predicted_height: float
```

### `PiecewiseBilinearHeightModel`

```python
class PiecewiseBilinearHeightModel:
```

Triangle-based height model over the calibrated marker layout. The class name is kept for compatibility with existing call sites, but the interpolation surface now uses piecewise planar triangles instead of quad bilinear patches.

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, points_by_id: dict[int, tuple[float, float, float]])
```

```python
@classmethod
def from_depth_map(cls, data: DepthMapData) -> 'PiecewiseBilinearHeightModel'
```

```python
def is_supported(self) -> bool
```

```python
def patches(self) -> List[TrianglePatch]
```

```python
def points_by_id(self) -> dict[int, tuple[float, float, float]]
```

```python
def triangulation_data(self) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]
```

```python
def triangulation(self) -> Triangulation | None
```

```python
def verification_points(self) -> list[VerificationPoint]
```

```python
def interpolate_height(self, x: float, y: float) -> float | None
```

## `robot_system_height_measuring_provider.py`

Source: [src/engine/robot/height_measuring/robot_system_height_measuring_provider.py](../../../../src/engine/robot/height_measuring/robot_system_height_measuring_provider.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `abc`.

### `RobotSystemHeightMeasuringProvider`

```python
class RobotSystemHeightMeasuringProvider(ABC):
```

Robot-system adapter that supplies the laser-control implementation.

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
@abstractmethod
def build_laser_control(self)
```

## `service_builders.py`

Source: [src/engine/robot/height_measuring/service_builders.py](../../../../src/engine/robot/height_measuring/service_builders.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `src.engine.common_settings_ids`, `src.engine.robot.height_measuring.height_measuring_service`, `src.engine.robot.height_measuring.laser_calibration_service`, `src.engine.robot.height_measuring.laser_detection_service`, `src.engine.robot.height_measuring.laser_detector`.

### `build_robot_system_height_measuring_services`

```python
def build_robot_system_height_measuring_services(robot_system)
```

Build the standard height-measuring service trio for a robot system.

## `settings.py`

Source: [src/engine/robot/height_measuring/settings.py](../../../../src/engine/robot/height_measuring/settings.py).

Imports (including optional/function-local imports; not a startup dependency list): `dataclasses`, `src.engine.repositories.interfaces.settings_serializer`, `typing`.

### `LaserDetectionSettings`

```python
@dataclass
class LaserDetectionSettings:
```

Declared fields/defaults:

```python
min_intensity: float = 10.0
gaussian_blur_kernel: tuple = (21, 21)
gaussian_blur_sigma: float = 0.0
default_axis: str = 'y'
detection_delay_ms: int = 200
image_capture_delay_ms: int = 10
detection_samples: int = 5
max_detection_retries: int = 5
```

### `LaserCalibrationSettings`

```python
@dataclass
class LaserCalibrationSettings:
```

Declared fields/defaults:

```python
step_size_mm: float = 1.0
num_iterations: int = 50
calibration_velocity: float = 50.0
calibration_acceleration: float = 10.0
movement_threshold: float = 0.2
movement_timeout: float = 2.0
delay_between_move_detect_ms: int = 1000
calibration_max_attempts: int = 5
max_polynomial_degree: int = 6
calibration_initial_position: List[float] = field(default_factory=lambda: [0.0, 0.0, 0.0, 180.0, 0.0, 0.0])
```

### `HeightMeasuringSettings`

```python
@dataclass
class HeightMeasuringSettings:
```

Declared fields/defaults:

```python
measurement_velocity: float = 20.0
measurement_acceleration: float = 10.0
measurement_threshold: float = 0.25
measurement_timeout: float = 10.0
delay_between_move_detect_ms: int = 500
```

### `HeightMeasuringModuleSettings`

```python
@dataclass
class HeightMeasuringModuleSettings:
```

Declared fields/defaults:

```python
detection: LaserDetectionSettings = field(default_factory=LaserDetectionSettings)
calibration: LaserCalibrationSettings = field(default_factory=LaserCalibrationSettings)
measuring: HeightMeasuringSettings = field(default_factory=HeightMeasuringSettings)
```

### `HeightMeasuringSettingsSerializer`

```python
class HeightMeasuringSettingsSerializer(ISettingsSerializer[HeightMeasuringModuleSettings]):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
@property
def settings_type(self) -> str
```

```python
def get_default(self) -> HeightMeasuringModuleSettings
```

```python
def to_dict(self, s: HeightMeasuringModuleSettings) -> Dict[str, Any]
```

```python
def from_dict(self, data: Dict[str, Any]) -> HeightMeasuringModuleSettings
```
