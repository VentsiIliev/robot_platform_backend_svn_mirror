# Module reference: `src/applications/calibration/service`

[Package guide](README.md) · [Complete source index](../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [calibration_application_service.py](#calibration_application_servicepy)
- [calibration_settings_bridge.py](#calibration_settings_bridgepy)
- [i_calibration_service.py](#i_calibration_servicepy)
- [stub_calibration_service.py](#stub_calibration_servicepy)

## `__init__.py`

Source: [src/applications/calibration/service/__init__.py](../../../../src/applications/calibration/service/__init__.py).

No top-level functions, classes or public value declarations; inspect the source for imports or entry-point statements.

## `calibration_application_service.py`

Source: [src/applications/calibration/service/calibration_application_service.py](../../../../src/applications/calibration/service/calibration_application_service.py).

Imports (including optional/function-local imports; not a startup dependency list): `cv2`, `json`, `logging`, `math`, `numpy`, `os`, `re`, `src.applications.calibration.service.calibration_settings_bridge`, `src.applications.calibration.service.i_calibration_service`, `src.applications.calibration_settings.calibration_settings_data`, `src.applications.calibration_settings.service.i_calibration_settings_service`, `src.applications.height_measuring.service.i_height_measuring_app_service`, `src.applications.intrinsic_calibration_capture.service.i_intrinsic_capture_service`, `src.engine.common_settings_ids`, `src.engine.core.i_coordinate_transformer`, `src.engine.repositories.interfaces.i_settings_service`, `src.engine.robot.calibration.robot_calibration`, `src.engine.robot.calibration.robot_calibration.target_planning`, `src.engine.vision.i_vision_service`, `src.engine.work_areas.i_work_area_service`, `src.shared_contracts.declarations`, `threading`, `time`, `typing`.

### `_parse_grid_label`

```python
def _parse_grid_label(label: str) -> tuple[int, int] | None
```

Return zero-based (row, col) from a label like 'r3c2', or None.

### `_point_in_polygon`

```python
def _point_in_polygon(px: float, py: float, polygon: list[tuple[float, float]]) -> bool
```

Ray-casting containment test for a simple polygon.

### `_format_marker_id_log_block`

```python
def _format_marker_id_log_block(title: str, marker_ids: list[int] | tuple[int, ...] | set[int]) -> str
```

### `_IProcessController`

```python
class _IProcessController(Protocol):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def calibrate(self) -> None
```

```python
def stop_calibration(self) -> None
```

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
def set_active_tool(self, tool: int) -> bool
```

```python
def set_active_workobject(self, user: int) -> bool
```

```python
def validate_pose(self, start_position, target_position, tool: int=0, user: int=0, start_joint_state: dict | None=None) -> dict
```

```python
def enable_safety_walls(self) -> bool
```

```python
def disable_safety_walls(self) -> bool
```

```python
def are_safety_walls_enabled(self) -> Optional[bool]
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
def get_calibration_data(self)
```

```python
def measure_at(self, x: float, y: float, *, already_at_xy: bool=False) -> Optional[float]
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

### `_ICameraTcpOffsetCalibrator`

```python
class _ICameraTcpOffsetCalibrator(Protocol):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def calibrate(self) -> tuple[bool, str]
```

```python
def stop(self) -> None
```

### `_ICameraZShiftCalibrator`

```python
class _ICameraZShiftCalibrator(Protocol):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def calibrate(self, marker_id: int, samples: int, z_step_mm: float, settle_time_s: float) -> tuple[bool, str]
```

```python
def stop(self) -> None
```

### `_IToolTcpCalibrator`

```python
class _IToolTcpCalibrator(Protocol):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
@property
def active_tool_id(self) -> int | None
```

```python
def start(self, tool_id: int) -> None
```

```python
def capture_sample(self)
```

```python
def clear_samples(self) -> None
```

```python
def solve(self)
```

```python
def save(self, result=None) -> tuple[bool, str]
```

```python
def stop(self) -> None
```

### `_IMarkerHeightMappingService`

```python
class _IMarkerHeightMappingService(Protocol):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

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

```python
def stop(self) -> None
```

```python
def is_ready(self) -> bool
```

### `_ILaserCalibrator`

```python
class _ILaserCalibrator(Protocol):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def calibrate(self, initial_position: list, stop_event: threading.Event | None=None) -> bool
```

### `_ILaserOps`

```python
class _ILaserOps(Protocol):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def detect(self) -> tuple
```

```python
def restore(self) -> None
```

### `_IIntrinsicCaptureService`

```python
class _IIntrinsicCaptureService(Protocol):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

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
def get_config(self) -> IntrinsicCaptureConfig
```

```python
def save_config(self, config: IntrinsicCaptureConfig) -> None
```

### `CalibrationApplicationService`

```python
class CalibrationApplicationService(ICalibrationService):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, vision_service: IVisionService, process_controller: _IProcessController, robot_service: _IRobotService=None, height_service: _IHeightService=None, robot_config: _IRobotConfig=None, calib_config: _ICalibConfig=None, transformer: ICoordinateTransformer=None, transformer_provider: Optional[Callable[[], ICoordinateTransformer]]=None, work_area_service: Optional[IWorkAreaService]=None, camera_tcp_offset_calibrator: Optional[_ICameraTcpOffsetCalibrator]=None, camera_z_shift_calibrator: Optional[_ICameraZShiftCalibrator]=None, tool_tcp_calibrator: Optional[_IToolTcpCalibrator]=None, marker_height_mapping_service: Optional[_IMarkerHeightMappingService]=None, calibration_settings_service: Optional[ICalibrationSettingsService]=None, settings_service: Optional[ISettingsService]=None, laser_calibration_service: Optional[_ILaserCalibrator]=None, laser_ops: Optional[_ILaserOps]=None, intrinsic_capture_service: Optional[_IIntrinsicCaptureService]=None, observer_group_provider: Optional[Callable[[str], str | None]]=None, observer_position_provider: Optional[Callable[[str], list[float] | None]]=None, use_marker_centre: bool=False, work_area_definitions: Optional[list[WorkAreaDefinition]]=None)
```

```python
def load_calibration_settings(self) -> CalibrationSettingsData | None
```

```python
def save_calibration_settings(self, settings: CalibrationSettingsData) -> None
```

```python
def capture_calibration_image(self) -> tuple[bool, str]
```

```python
def calibrate_camera(self) -> tuple[bool, str]
```

```python
def get_intrinsic_capture_config(self) -> IntrinsicCaptureConfig
```

```python
def save_intrinsic_capture_config(self, config: IntrinsicCaptureConfig) -> None
```

```python
def start_intrinsic_auto_capture(self) -> tuple[bool, str]
```

```python
def stop_intrinsic_auto_capture(self) -> None
```

```python
def is_intrinsic_auto_capture_running(self) -> bool
```

```python
def calibrate_robot(self) -> tuple[bool, str]
```

```python
def select_robot_calibration_target(self, area_id: str) -> tuple[bool, str]
```

```python
def preview_robot_calibration(self) -> RobotCalibrationPreview
```

```python
def calibrate_camera_and_robot(self) -> tuple[bool, str]
```

```python
def calibrate_camera_tcp_offset(self) -> tuple[bool, str]
```

```python
def validate_camera_tcp_calibration_target(self, area_id: str) -> tuple[bool, str]
```

```python
def calibrate_camera_z_shift(self, marker_id: int, samples: int, z_step_mm: float, settle_time_s: float) -> tuple[bool, str]
```

```python
def start_tool_tcp_calibration(self, tool_id: int) -> tuple[bool, str]
```

```python
def capture_tool_tcp_sample(self) -> tuple[bool, str]
```

```python
def solve_tool_tcp_calibration(self) -> tuple[bool, str, dict]
```

```python
def save_tool_tcp_calibration(self) -> tuple[bool, str]
```

```python
def clear_tool_tcp_calibration(self) -> tuple[bool, str]
```

```python
def capture_workobject_point(self, point_name: str) -> tuple[bool, str, dict]
```

```python
def solve_workobject(self, user_id: int, name: str='') -> tuple[bool, str, dict]
```

```python
def save_workobject(self, user_id: int, name: str='', persist: bool=True) -> tuple[bool, str, dict]
```

```python
def calibrate_laser(self) -> tuple[bool, str]
```

```python
def detect_laser_once(self) -> LaserDetectionResult
```

```python
def stop_calibration(self) -> None
```

```python
def ensure_active_work_area_observed(self) -> tuple[bool, str]
```

```python
def is_calibrated(self) -> bool
```

```python
def test_calibration(self, model_name: str='homography') -> tuple[bool, str]
```

```python
def stop_test_calibration(self) -> None
```

```python
def measure_marker_heights(self) -> tuple[bool, str]
```

```python
def get_work_area_definitions(self) -> list[WorkAreaDefinition]
```

```python
def get_active_work_area_id(self) -> str
```

```python
def set_active_work_area_id(self, area_id: str) -> None
```

```python
def save_height_mapping_area(self, area_key: str, corners_norm: Sequence[tuple[float, float]]) -> tuple[bool, str]
```

```python
def get_height_mapping_area(self, area_key: str) -> list[tuple[float, float]]
```

```python
def generate_area_grid(self, corners_norm: Sequence[tuple[float, float]], rows: int, cols: int) -> list[tuple[float, float]]
```

```python
def measure_area_grid(self, area_id: str, corners_norm: Sequence[tuple[float, float]], rows: int, cols: int) -> tuple[bool, str]
```

```python
def verify_area_grid(self, corners_norm: Sequence[tuple[float, float]], rows: int, cols: int, progress_callback: Callable[[str, str, int, int], None] | None=None) -> tuple[bool, str, dict]
```

```python
def find_substitute_points(self, unreachable_xy: tuple[float, float], unreachable_label: str, point_states: list[tuple[str, list[float]]], area_corners_robot_xy: list[tuple[float, float]], existing_grid_xy: list[tuple[float, float]], pose_suffix: list[float], anchor_state: Sequence[float], anchor_joint_seed: dict | None, tool: int, user: int, max_substitutes: int=2, step_mm: float=10.0, max_radius_mm: float=150.0) -> list[tuple[float, float, float]]
```

Find up to *max_substitutes* reachable support points near an unreachable grid point. Strategy -------- 1. **Column search** — find the nearest same-column grid neighbour, build a cell-band polygon spanning that neighbour row to the unreachable row (±1 col), then divide the segment [neighbour → unreachable] into *max_substitutes + 1* equal parts and validate each interior point. 2. **Spiral fallback** — if column search finds nothing, search outward in expanding rings of *step_mm* (8 angles per ring). In both phases the search polygon is the cell-band (when a column neighbour exists) so candidates can never escape past the neighbouring row. Returns list of (x_mm, y_mm, dist_from_unreachable_mm).

```python
def stop_marker_height_measurement(self) -> None
```

```python
def can_measure_marker_heights(self) -> bool
```

```python
def verify_height_model(self, area_id: str='') -> tuple[bool, str]
```

```python
def has_saved_height_model(self, area_id: str='') -> bool
```

```python
def get_height_calibration_data(self, area_id: str='')
```

```python
def restore_pending_safety_walls(self) -> bool
```

## `calibration_settings_bridge.py`

Source: [src/applications/calibration/service/calibration_settings_bridge.py](../../../../src/applications/calibration/service/calibration_settings_bridge.py).

Imports (including optional/function-local imports; not a startup dependency list): `src.applications.calibration_settings.calibration_settings_data`, `src.applications.calibration_settings.service.i_calibration_settings_service`.

### `CalibrationSettingsBridge`

```python
class CalibrationSettingsBridge:
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, service: ICalibrationSettingsService | None)
```

```python
def load(self) -> CalibrationSettingsData | None
```

```python
def save(self, settings: CalibrationSettingsData) -> None
```

```python
def capture_workobject_point(self, point_name: str) -> tuple[bool, str, dict]
```

```python
def solve_workobject(self, user_id: int, name: str='') -> tuple[bool, str, dict]
```

```python
def save_workobject(self, user_id: int, name: str='', persist: bool=True) -> tuple[bool, str, dict]
```

## `i_calibration_service.py`

Source: [src/applications/calibration/service/i_calibration_service.py](../../../../src/applications/calibration/service/i_calibration_service.py).

Imports (including optional/function-local imports; not a startup dependency list): `abc`, `dataclasses`, `numpy`, `src.applications.calibration_settings.calibration_settings_data`, `src.applications.height_measuring.service.i_height_measuring_app_service`, `src.applications.intrinsic_calibration_capture.service.i_intrinsic_capture_service`, `src.shared_contracts.declarations`, `typing`.

### `RobotCalibrationPreview`

```python
@dataclass(frozen=True)
class RobotCalibrationPreview:
```

Declared fields/defaults:

```python
ok: bool
message: str
frame: np.ndarray | None = None
available_ids: list[int] | None = None
selected_ids: list[int] | None = None
report: dict | None = None
```

### `ICalibrationService`

```python
class ICalibrationService(ABC):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
@abstractmethod
def load_calibration_settings(self) -> CalibrationSettingsData | None
```

```python
@abstractmethod
def save_calibration_settings(self, settings: CalibrationSettingsData) -> None
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
def get_intrinsic_capture_config(self) -> IntrinsicCaptureConfig
```

```python
@abstractmethod
def save_intrinsic_capture_config(self, config: IntrinsicCaptureConfig) -> None
```

```python
@abstractmethod
def start_intrinsic_auto_capture(self) -> tuple[bool, str]
```

```python
@abstractmethod
def stop_intrinsic_auto_capture(self) -> None
```

```python
@abstractmethod
def is_intrinsic_auto_capture_running(self) -> bool
```

```python
@abstractmethod
def calibrate_robot(self) -> tuple[bool, str]
```

```python
@abstractmethod
def select_robot_calibration_target(self, area_id: str) -> tuple[bool, str]
```

```python
@abstractmethod
def preview_robot_calibration(self) -> RobotCalibrationPreview
```

```python
@abstractmethod
def calibrate_camera_and_robot(self) -> tuple[bool, str]
```

```python
@abstractmethod
def calibrate_camera_tcp_offset(self) -> tuple[bool, str]
```

```python
@abstractmethod
def validate_camera_tcp_calibration_target(self, area_id: str) -> tuple[bool, str]
```

```python
@abstractmethod
def calibrate_camera_z_shift(self, marker_id: int, samples: int, z_step_mm: float, settle_time_s: float) -> tuple[bool, str]
```

```python
@abstractmethod
def start_tool_tcp_calibration(self, tool_id: int) -> tuple[bool, str]
```

```python
@abstractmethod
def capture_tool_tcp_sample(self) -> tuple[bool, str]
```

```python
@abstractmethod
def solve_tool_tcp_calibration(self) -> tuple[bool, str, dict]
```

```python
@abstractmethod
def save_tool_tcp_calibration(self) -> tuple[bool, str]
```

```python
@abstractmethod
def clear_tool_tcp_calibration(self) -> tuple[bool, str]
```

```python
def capture_workobject_point(self, point_name: str) -> tuple[bool, str, dict]
```

```python
def solve_workobject(self, user_id: int, name: str='') -> tuple[bool, str, dict]
```

```python
def save_workobject(self, user_id: int, name: str='', persist: bool=True) -> tuple[bool, str, dict]
```

```python
@abstractmethod
def calibrate_laser(self) -> tuple[bool, str]
```

```python
@abstractmethod
def detect_laser_once(self) -> LaserDetectionResult
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
def test_calibration(self, model_name: str='homography') -> tuple[bool, str]
```

```python
@abstractmethod
def stop_test_calibration(self) -> None
```

```python
@abstractmethod
def measure_marker_heights(self) -> tuple[bool, str]
```

```python
@abstractmethod
def get_work_area_definitions(self) -> list[WorkAreaDefinition]
```

```python
@abstractmethod
def get_active_work_area_id(self) -> str
```

```python
@abstractmethod
def set_active_work_area_id(self, area_id: str) -> None
```

```python
@abstractmethod
def save_height_mapping_area(self, area_key: str, corners_norm: Sequence[tuple[float, float]]) -> tuple[bool, str]
```

```python
@abstractmethod
def get_height_mapping_area(self, area_key: str) -> list[tuple[float, float]]
```

```python
@abstractmethod
def generate_area_grid(self, corners_norm: Sequence[tuple[float, float]], rows: int, cols: int) -> list[tuple[float, float]]
```

```python
@abstractmethod
def measure_area_grid(self, area_id: str, corners_norm: Sequence[tuple[float, float]], rows: int, cols: int) -> tuple[bool, str]
```

```python
@abstractmethod
def verify_area_grid(self, corners_norm: Sequence[tuple[float, float]], rows: int, cols: int, progress_callback: Callable[[str, str, int, int], None] | None=None) -> tuple[bool, str, dict]
```

```python
@abstractmethod
def ensure_active_work_area_observed(self) -> tuple[bool, str]
```

```python
@abstractmethod
def stop_marker_height_measurement(self) -> None
```

```python
@abstractmethod
def can_measure_marker_heights(self) -> bool
```

```python
@abstractmethod
def verify_height_model(self, area_id: str='') -> tuple[bool, str]
```

```python
@abstractmethod
def get_height_calibration_data(self, area_id: str='')
```

```python
@abstractmethod
def has_saved_height_model(self, area_id: str='') -> bool
```

```python
@abstractmethod
def restore_pending_safety_walls(self) -> bool
```

## `stub_calibration_service.py`

Source: [src/applications/calibration/service/stub_calibration_service.py](../../../../src/applications/calibration/service/stub_calibration_service.py).

Imports (including optional/function-local imports; not a startup dependency list): `logging`, `src.applications.calibration.service.i_calibration_service`, `src.applications.calibration_settings.calibration_settings_data`, `src.applications.height_measuring.service.i_height_measuring_app_service`, `src.applications.intrinsic_calibration_capture.service.i_intrinsic_capture_service`, `src.engine.robot.configuration`, `src.engine.robot.height_measuring.settings`, `src.engine.vision.calibration_vision_settings`, `src.shared_contracts.declarations`, `typing`.

### `StubCalibrationService`

```python
class StubCalibrationService(ICalibrationService):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def get_intrinsic_capture_config(self) -> IntrinsicCaptureConfig
```

```python
def save_intrinsic_capture_config(self, config: IntrinsicCaptureConfig) -> None
```

```python
def start_intrinsic_auto_capture(self) -> tuple[bool, str]
```

```python
def stop_intrinsic_auto_capture(self) -> None
```

```python
def is_intrinsic_auto_capture_running(self) -> bool
```

```python
def load_calibration_settings(self) -> CalibrationSettingsData | None
```

```python
def save_calibration_settings(self, settings: CalibrationSettingsData) -> None
```

```python
def capture_calibration_image(self) -> tuple[bool, str]
```

```python
def calibrate_camera(self) -> tuple[bool, str]
```

```python
def calibrate_robot(self) -> tuple[bool, str]
```

```python
def select_robot_calibration_target(self, area_id: str) -> tuple[bool, str]
```

```python
def preview_robot_calibration(self) -> RobotCalibrationPreview
```

```python
def calibrate_camera_and_robot(self) -> tuple[bool, str]
```

```python
def calibrate_camera_tcp_offset(self) -> tuple[bool, str]
```

```python
def validate_camera_tcp_calibration_target(self, area_id: str) -> tuple[bool, str]
```

```python
def calibrate_camera_z_shift(self, marker_id: int, samples: int, z_step_mm: float, settle_time_s: float) -> tuple[bool, str]
```

```python
def start_tool_tcp_calibration(self, tool_id: int) -> tuple[bool, str]
```

```python
def capture_tool_tcp_sample(self) -> tuple[bool, str]
```

```python
def solve_tool_tcp_calibration(self) -> tuple[bool, str, dict]
```

```python
def save_tool_tcp_calibration(self) -> tuple[bool, str]
```

```python
def clear_tool_tcp_calibration(self) -> tuple[bool, str]
```

```python
def calibrate_laser(self) -> tuple[bool, str]
```

```python
def detect_laser_once(self)
```

```python
def stop_calibration(self) -> None
```

```python
def is_calibrated(self) -> bool
```

```python
def test_calibration(self, model_name: str='homography') -> tuple[bool, str]
```

```python
def stop_test_calibration(self) -> None
```

```python
def measure_marker_heights(self) -> tuple[bool, str]
```

```python
def get_work_area_definitions(self) -> list[WorkAreaDefinition]
```

```python
def get_active_work_area_id(self) -> str
```

```python
def set_active_work_area_id(self, area_id: str) -> None
```

```python
def save_height_mapping_area(self, area_key: str, corners_norm: Sequence[tuple[float, float]]) -> tuple[bool, str]
```

```python
def get_height_mapping_area(self, area_key: str) -> list[tuple[float, float]]
```

```python
def generate_area_grid(self, corners_norm: Sequence[tuple[float, float]], rows: int, cols: int) -> list[tuple[float, float]]
```

```python
def measure_area_grid(self, area_id: str, corners_norm: Sequence[tuple[float, float]], rows: int, cols: int) -> tuple[bool, str]
```

```python
def verify_area_grid(self, corners_norm: Sequence[tuple[float, float]], rows: int, cols: int, progress_callback: Callable[[str, str, int, int], None] | None=None) -> tuple[bool, str, dict]
```

```python
def ensure_active_work_area_observed(self) -> tuple[bool, str]
```

```python
def stop_marker_height_measurement(self) -> None
```

```python
def can_measure_marker_heights(self) -> bool
```

```python
def verify_height_model(self, area_id: str='') -> tuple[bool, str]
```

```python
def get_height_calibration_data(self, area_id: str='')
```

```python
def has_saved_height_model(self, area_id: str='') -> bool
```

```python
def restore_pending_safety_walls(self) -> bool
```
