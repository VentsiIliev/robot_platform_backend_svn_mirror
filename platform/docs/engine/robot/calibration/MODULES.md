# Module reference: `src/engine/robot/calibration`

[Package guide](README.md) · [Complete source index](../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [aruco_marker_height_mapping_service.py](#aruco_marker_height_mapping_servicepy)
- [calibration_navigation_service.py](#calibration_navigation_servicepy)
- [camera_tcp_offset_calibration_service.py](#camera_tcp_offset_calibration_servicepy)
- [camera_z_shift_calibration_service.py](#camera_z_shift_calibration_servicepy)
- [i_robot_calibration_service.py](#i_robot_calibration_servicepy)
- [robot_calibration_process.py](#robot_calibration_processpy)
- [robot_calibration_service.py](#robot_calibration_servicepy)
- [robot_system_calibration_provider.py](#robot_system_calibration_providerpy)
- [ros_tool_registry_client.py](#ros_tool_registry_clientpy)
- [service_builders.py](#service_builderspy)
- [tool_tcp_calibration_data.py](#tool_tcp_calibration_datapy)
- [tool_tcp_calibration_service.py](#tool_tcp_calibration_servicepy)
- [tool_tcp_pivot_solver.py](#tool_tcp_pivot_solverpy)

## `__init__.py`

Source: [src/engine/robot/calibration/__init__.py](../../../../src/engine/robot/calibration/__init__.py).

Imports (including optional/function-local imports; not a startup dependency list): `src.engine.robot.calibration.calibration_navigation_service`, `src.engine.robot.calibration.i_robot_calibration_service`, `src.engine.robot.calibration.robot_system_calibration_provider`, `src.engine.robot.calibration.service_builders`.

Package-level import/export surface:

```python
from src.engine.robot.calibration.calibration_navigation_service import CalibrationNavigationService
from src.engine.robot.calibration.i_robot_calibration_service import IRobotCalibrationService
from src.engine.robot.calibration.robot_system_calibration_provider import RobotSystemCalibrationProvider
from src.engine.robot.calibration.service_builders import build_robot_system_calibration_service
```

Module declarations (expressions are shown without evaluating them):

```python
__all__ = ['CalibrationNavigationService', 'IRobotCalibrationService', 'RobotSystemCalibrationProvider', 'build_robot_system_calibration_service']
```

## `aruco_marker_height_mapping_service.py`

Source: [src/engine/robot/calibration/aruco_marker_height_mapping_service.py](../../../../src/engine/robot/calibration/aruco_marker_height_mapping_service.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `logging`, `os`, `src.engine.core.i_coordinate_transformer`, `src.engine.robot.height_measuring.area_grid_height_model`, `src.engine.robot.height_measuring.piecewise_bilinear_height_model`, `src.engine.vision.i_vision_service`, `threading`, `time`, `typing`.

### `_IRobotService`

```python
class _IRobotService(Protocol):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def get_current_position(self) -> list
```

```python
def move_ptp(self, position, tool, user, velocity, acceleration, wait_to_reach=False) -> bool
```

```python
def stop_motion(self) -> bool
```

```python
def enable_safety_walls(self) -> bool
```

```python
def disable_safety_walls(self) -> bool
```

```python
def are_safety_walls_enabled(self)
```

### `_IHeightService`

```python
class _IHeightService(Protocol):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def is_calibrated(self) -> bool
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

```python
def get_calibration_data(self)
```

```python
def save_height_map(self, samples: list[list[float]], area_id: str='', marker_ids: Optional[list[int]]=None, point_labels: Optional[list[str]]=None, grid_rows: int=0, grid_cols: int=0, planned_points: Optional[list[list[float]]]=None, planned_point_labels: Optional[list[str]]=None, unavailable_point_labels: Optional[list[str]]=None) -> None
```

```python
def get_depth_map_data(self, area_id: str='')
```

### `_IRobotConfig`

```python
class _IRobotConfig(Protocol):
```

Declared fields/defaults:

```python
robot_tool: int
robot_user: int
```

### `_ICalibConfig`

```python
class _ICalibConfig(Protocol):
```

Declared fields/defaults:

```python
required_ids: list
z_target: int
velocity: int
acceleration: int
```

### `ArucoMarkerHeightMappingService`

```python
class ArucoMarkerHeightMappingService:
```

Measure heights at detected ArUco marker positions using the current homography.

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, vision_service: IVisionService, robot_service: _IRobotService, height_service: _IHeightService, robot_config: _IRobotConfig, calib_config: _ICalibConfig, transformer: ICoordinateTransformer, *, use_marker_centre: bool=False)
```

```python
def stop(self) -> None
```

```python
def restore_pending_safety_walls(self) -> bool
```

```python
def is_ready(self) -> bool
```

```python
def measure_marker_heights(self) -> tuple[bool, str]
```

```python
def generate_area_grid(self, corners_norm: Sequence[tuple[float, float]], rows: int, cols: int) -> list[tuple[float, float]]
```

```python
def measure_area_grid(self, area_id: str, corners_norm: Sequence[tuple[float, float]], rows: int, cols: int, support_points_mm: list[tuple[str, float, float]] | None=None, skip_labels: set[str] | None=None, measurement_pose: list[float] | None=None) -> tuple[bool, str]
```

```python
def verify_height_model(self, area_id: str='', measurement_pose: list[float] | None=None) -> tuple[bool, str]
```

## `calibration_navigation_service.py`

Source: [src/engine/robot/calibration/calibration_navigation_service.py](../../../../src/engine/robot/calibration/calibration_navigation_service.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `src.engine.robot.features.navigation_service`, `typing`.

### `CalibrationNavigationService`

```python
class CalibrationNavigationService:
```

Generic calibration move helper built on the standard NavigationService. This adapter standardizes the calibration entry move around a named navigation group, which defaults to ``"CALIBRATION"``. Robot-system-specific side effects should be injected explicitly via ``before_move``. For example, the glue system uses that hook to switch the active work area to ``"spray"`` before moving, instead of hiding that behavior inside a robot-system navigation facade.

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, navigation: NavigationService, *, calibration_group: str='CALIBRATION', calibration_group_getter: Optional[Callable[[], str]]=None, before_move: Optional[Callable[[], None]]=None, after_move: Optional[Callable[[], None]]=None) -> None
```

```python
def move_to_calibration_position(self, wait_cancelled=None) -> bool
```

## `camera_tcp_offset_calibration_service.py`

Source: [src/engine/robot/calibration/camera_tcp_offset_calibration_service.py](../../../../src/engine/robot/calibration/camera_tcp_offset_calibration_service.py).

Imports (including optional/function-local imports; not a startup dependency list): `collections.abc`, `dataclasses`, `logging`, `math`, `numpy`, `src.engine.common_settings_ids`, `src.engine.repositories.interfaces.i_settings_service`, `src.engine.robot.configuration`, `src.engine.robot.configuration.robot_calibration_settings`, `src.engine.robot.enums.axis`, `src.engine.robot.targeting.target_point_geometry`, `src.engine.vision.homography_residual_transformer`, `threading`, `time`, `typing`.

### `_IRobotService`

```python
class _IRobotService(Protocol):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def get_current_position(self) -> list
```

```python
def move_ptp(self, position, tool, user, velocity, acceleration, wait_to_reach=False) -> bool
```

```python
def move_linear(self, position, tool, user, velocity, acceleration, blendR=0.0, wait_to_reach=False) -> bool
```

```python
def stop_motion(self) -> bool
```

### `_IVisionService`

```python
class _IVisionService(Protocol):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def get_latest_frame(self)
```

```python
def detect_aruco_markers(self, image)
```

```python
def get_camera_width(self) -> int
```

```python
def get_camera_height(self) -> int
```

```python
@property
def camera_to_robot_matrix_path(self) -> str
```

### `_INavigationService`

```python
class _INavigationService(Protocol):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def move_to_calibration_position(self, wait_cancelled=None) -> bool
```

### `_MarkerSample`

```python
@dataclass(frozen=True)
class _MarkerSample:
```

Declared fields/defaults:

```python
sample_index: int
rz: float
marker_px: float
marker_py: float
current_pose_x: float
current_pose_y: float
measured_world_dx: float
measured_world_dy: float
local_dx: float
local_dy: float
pixel_error_x: float
pixel_error_y: float
pixel_error_norm: float
```

### `_StandaloneTcpAxisCalibration`

```python
@dataclass(frozen=True)
class _StandaloneTcpAxisCalibration:
```

Declared fields/defaults:

```python
mapping: ImageToRobotMapping
image_delta_per_robot_x_mm: tuple[float, float]
image_delta_per_robot_y_mm: tuple[float, float]
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def map_pixel_error_to_robot_delta(self, pixel_error_x: float, pixel_error_y: float) -> tuple[float, float]
```

### `_build_tcp_offset_summary`

```python
def _build_tcp_offset_summary(samples: list[_MarkerSample], *, offset_x: float, offset_y: float, std_x: float, std_y: float, marker_id: int, approach_pose: list[float], local_scale_x: float, local_scale_y: float, reference_rz: float, rotation_step_deg: float, iterations: int) -> str
```

### `CameraTcpOffsetCalibrationService`

```python
class CameraTcpOffsetCalibrationService:
```

Calibrate camera-center to robot-TCP XY offsets using one ArUco marker.

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, *, vision_service: _IVisionService, robot_service: _IRobotService, navigation_service: Optional[_INavigationService], settings_service: ISettingsService, robot_config_key, robot_config: RobotSettings, calibration_settings: RobotCalibrationSettings, robot_tool: int, robot_user: int, on_offsets_saved: Callable[[], None] | None=None, target_area_id_getter: Callable[[], str] | None=None, matrix_path_getter: Callable[[str], str] | None=None)
```

```python
def stop(self) -> None
```

```python
def calibrate(self) -> tuple[bool, str]
```

## `camera_z_shift_calibration_service.py`

Source: [src/engine/robot/calibration/camera_z_shift_calibration_service.py](../../../../src/engine/robot/calibration/camera_z_shift_calibration_service.py).

Imports (including optional/function-local imports; not a startup dependency list): `dataclasses`, `json`, `logging`, `numpy`, `pathlib`, `src.engine.repositories.interfaces.i_settings_service`, `src.engine.robot.configuration`, `src.engine.vision.homography_residual_transformer`, `threading`, `time`, `typing`.

### `_IRobotService`

```python
class _IRobotService(Protocol):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def get_current_position(self) -> list
```

```python
def move_ptp(self, position, tool, user, velocity, acceleration, wait_to_reach=False) -> bool
```

```python
def stop_motion(self) -> bool
```

### `_IVisionService`

```python
class _IVisionService(Protocol):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def get_latest_frame(self)
```

```python
def detect_aruco_markers(self, image)
```

```python
def get_camera_width(self) -> int
```

```python
def get_camera_height(self) -> int
```

```python
@property
def camera_to_robot_matrix_path(self) -> str
```

### `_INavigationService`

```python
class _INavigationService(Protocol):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def move_to_calibration_position(self, wait_cancelled=None) -> bool
```

### `_ZShiftSample`

```python
@dataclass(frozen=True)
class _ZShiftSample:
```

Declared fields/defaults:

```python
sample_index: int
reference_z: float
sample_z: float
z_delta_mm: float
marker_x_px: float
marker_y_px: float
image_dx_px: float
image_dy_px: float
local_dx_mm: float
local_dy_mm: float
```

### `CameraZShiftCalibrationService`

```python
class CameraZShiftCalibrationService:
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, *, vision_service: _IVisionService, robot_service: _IRobotService, navigation_service: Optional[_INavigationService], settings_service: ISettingsService, robot_config_key, robot_config: RobotSettings, calibration_settings: RobotCalibrationSettings, robot_tool: int, robot_user: int)
```

```python
def stop(self) -> None
```

```python
def calibrate(self, marker_id: int, samples: int, z_step_mm: float, settle_time_s: float) -> tuple[bool, str]
```

## `i_robot_calibration_service.py`

Source: [src/engine/robot/calibration/i_robot_calibration_service.py](../../../../src/engine/robot/calibration/i_robot_calibration_service.py).

Imports (including optional/function-local imports; not a startup dependency list): `abc`.

### `IRobotCalibrationService`

```python
class IRobotCalibrationService(ABC):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
@abstractmethod
def run_calibration(self) -> tuple[bool, str]
```

```python
@abstractmethod
def stop_calibration(self) -> None
```

```python
@abstractmethod
def is_calibrated(self) -> bool
```

```python
@abstractmethod
def get_status(self) -> str
```

## `robot_calibration_process.py`

Source: [src/engine/robot/calibration/robot_calibration_process.py](../../../../src/engine/robot/calibration/robot_calibration_process.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `src.engine.core.i_messaging_service`, `src.engine.process.base_process`, `src.engine.process.process_requirements`, `src.engine.robot.calibration.i_robot_calibration_service`, `src.engine.system.i_system_manager`, `threading`, `typing`.

### `RobotCalibrationProcess`

```python
class RobotCalibrationProcess(BaseProcess):
```

Runs IRobotCalibrationService.run_calibration() in a background thread. Transitions to STOPPED on success, ERROR on failure. _on_stop() signals stop_calibration() but does NOT join — called while the lock is held.

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, calibration_service: IRobotCalibrationService, messaging: IMessagingService, process_id: str=_DEFAULT_PROCESS_ID, system_manager: Optional[ISystemManager]=None, requirements: Optional[ProcessRequirements]=None, service_checker: Optional[Callable[[str], bool]]=None)
```

## `robot_calibration_service.py`

Source: [src/engine/robot/calibration/robot_calibration_service.py](../../../../src/engine/robot/calibration/robot_calibration_service.py).

Imports (including optional/function-local imports; not a startup dependency list): `logging`, `src.engine.robot.calibration.i_robot_calibration_service`, `src.engine.robot.calibration.robot_calibration.config_helpers`, `src.engine.robot.calibration.robot_calibration.robot_calibration_pipeline`.

### `_BrokerLogHandler`

```python
class _BrokerLogHandler(logging.Handler):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, broker, topic)
```

```python
def emit(self, record)
```

### `RobotCalibrationService`

```python
class RobotCalibrationService(IRobotCalibrationService):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, config: RobotCalibrationConfig, adaptive_config: AdaptiveMovementConfig=None, events_config: RobotCalibrationEventsConfig=None)
```

```python
def run_calibration(self) -> tuple[bool, str]
```

```python
def stop_calibration(self) -> None
```

```python
def is_calibrated(self) -> bool
```

```python
def get_status(self) -> str
```

## `robot_system_calibration_provider.py`

Source: [src/engine/robot/calibration/robot_system_calibration_provider.py](../../../../src/engine/robot/calibration/robot_system_calibration_provider.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `abc`.

### `RobotSystemCalibrationProvider`

```python
class RobotSystemCalibrationProvider(ABC):
```

Robot-system adapter that supplies the system-specific calibration move.

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
@abstractmethod
def build_calibration_navigation(self, calibration_target_area_id_getter=None)
```

## `ros_tool_registry_client.py`

Source: [src/engine/robot/calibration/ros_tool_registry_client.py](../../../../src/engine/robot/calibration/ros_tool_registry_client.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `logging`, `requests`, `typing`.

### `RosToolRegistryClient`

```python
class RosToolRegistryClient:
```

Small REST adapter for ROS2 runtime tool registry and flange-pose endpoints.

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, server_url: str='http://localhost:5000', *, timeout_s: float=5.0)
```

```python
@property
def server_url(self) -> str
```

```python
def get_tool_registry(self) -> dict | None
```

```python
def update_tool(self, tool_id: int, name: str | None, transform: Sequence[float], *, persist: bool, collision_profile: str | None=None) -> tuple[bool, str]
```

```python
def get_current_flange_position(self) -> list[float] | None
```

## `service_builders.py`

Source: [src/engine/robot/calibration/service_builders.py](../../../../src/engine/robot/calibration/service_builders.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `os`, `src.engine.common_settings_ids`, `src.engine.robot.calibration.robot_calibration.config_helpers`, `src.engine.robot.calibration.robot_calibration_service`, `src.shared_contracts.events.robot_events`.

### `_CalibrationArtifactVisionProxy`

```python
class _CalibrationArtifactVisionProxy:
```

Delegate vision operations while routing calibration output to the selected profile.

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, vision_service, settings_service)
```

```python
@property
def camera_to_robot_matrix_path(self) -> str
```

```python
@property
def intrinsic_camera_calibration_path(self) -> str
```

```python
def begin_calibration(self) -> None
```

```python
def end_calibration(self) -> None
```

```python
def get_calibration_target_area_id(self) -> str
```

```python
def matrix_path_for_area(self, area_id: str) -> str
```

Read the matrix assigned to an area, including a shared global profile.

### `build_calibration_artifact_vision_proxy`

```python
def build_calibration_artifact_vision_proxy(vision_service, settings_service)
```

Route calibration artifacts using the currently selected destination.

### `build_robot_system_calibration_service`

```python
def build_robot_system_calibration_service(robot_system) -> RobotCalibrationService
```

Build a standard RobotCalibrationService from robot-system runtime state.

## `tool_tcp_calibration_data.py`

Source: [src/engine/robot/calibration/tool_tcp_calibration_data.py](../../../../src/engine/robot/calibration/tool_tcp_calibration_data.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `dataclasses`, `math`, `typing`.

Module declarations (expressions are shown without evaluating them):

```python
Pose6 = tuple[float, float, float, float, float, float]
Point3 = tuple[float, float, float]
```

### `ToolTcpSample`

```python
@dataclass(frozen=True)
class ToolTcpSample:
```

One flange pose captured while the physical TCP touches the pivot point.

Declared fields/defaults:

```python
flange_pose: Pose6
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
@classmethod
def from_pose(cls, pose: Sequence[float]) -> 'ToolTcpSample'
```

```python
def to_dict(self) -> dict
```

### `ToolTcpCalibrationResult`

```python
@dataclass(frozen=True)
class ToolTcpCalibrationResult:
```

Solved flange-to-TCP offset and fit quality from pivot calibration samples.

Declared fields/defaults:

```python
tool_offset: Pose6
pivot_point: Point3
residual_rms_mm: float
residual_max_mm: float
sample_count: int
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
@classmethod
def from_values(cls, tool_offset: Sequence[float], pivot_point: Sequence[float], residual_rms_mm: float, residual_max_mm: float, sample_count: int) -> 'ToolTcpCalibrationResult'
```

```python
def to_dict(self) -> dict
```

### `_pose6`

```python
def _pose6(values: Sequence[float]) -> Pose6
```

### `_point3`

```python
def _point3(values: Sequence[float]) -> Point3
```

### `_finite_float`

```python
def _finite_float(value: float) -> float
```

## `tool_tcp_calibration_service.py`

Source: [src/engine/robot/calibration/tool_tcp_calibration_service.py](../../../../src/engine/robot/calibration/tool_tcp_calibration_service.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `collections.abc`, `logging`, `src.engine.robot.calibration.tool_tcp_calibration_data`, `src.engine.robot.calibration.tool_tcp_pivot_solver`, `typing`.

### `_RobotService`

```python
class _RobotService(Protocol):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def get_current_position(self) -> list
```

```python
def stop_motion(self) -> bool
```

### `_ToolRegistryClient`

```python
class _ToolRegistryClient(Protocol):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def update_tool(self, tool_id: int, name: str | None, transform: Sequence[float], *, persist: bool) -> tuple[bool, str]
```

### `ToolTcpCalibrationService`

```python
class ToolTcpCalibrationService:
```

Manual pivot calibration workflow for flange-to-physical-TCP offset.

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, *, robot_service: _RobotService | None=None, tool_registry_client: _ToolRegistryClient | None=None, flange_pose_provider: Callable[[], Sequence[float] | None] | None=None, min_samples: int=6, persist_on_save: bool=True)
```

```python
@property
def active_tool_id(self) -> int | None
```

```python
@property
def latest_result(self) -> ToolTcpCalibrationResult | None
```

```python
def get_samples(self) -> list[ToolTcpSample]
```

```python
def start(self, tool_id: int) -> None
```

```python
def capture_sample(self) -> ToolTcpSample
```

```python
def clear_samples(self) -> None
```

```python
def solve(self) -> ToolTcpCalibrationResult
```

```python
def save(self, result: ToolTcpCalibrationResult | None=None) -> tuple[bool, str]
```

```python
def stop(self) -> None
```

## `tool_tcp_pivot_solver.py`

Source: [src/engine/robot/calibration/tool_tcp_pivot_solver.py](../../../../src/engine/robot/calibration/tool_tcp_pivot_solver.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `math`, `numpy`, `src.engine.robot.calibration.tool_tcp_calibration_data`, `typing`.

### `solve_tool_tcp_pivot`

```python
def solve_tool_tcp_pivot(samples: Iterable[ToolTcpSample | Sequence[float]], *, min_samples: int=_DEFAULT_MIN_SAMPLES) -> ToolTcpCalibrationResult
```

### `_sample_pose`

```python
def _sample_pose(sample: ToolTcpSample | Sequence[float]) -> tuple[float, float, float, float, float, float]
```

### `_rotation_matrix_xyz_degrees`

```python
def _rotation_matrix_xyz_degrees(rx: float, ry: float, rz: float) -> np.ndarray
```
