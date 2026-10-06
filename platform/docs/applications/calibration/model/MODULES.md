# Module reference: `src/applications/calibration/model`

[Package guide](README.md) · [Complete source index](../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [calibration_model.py](#calibration_modelpy)

## `__init__.py`

Source: [src/applications/calibration/model/__init__.py](../../../../src/applications/calibration/model/__init__.py).

No top-level functions, classes or public value declarations; inspect the source for imports or entry-point statements.

## `calibration_model.py`

Source: [src/applications/calibration/model/calibration_model.py](../../../../src/applications/calibration/model/calibration_model.py).

Imports (including optional/function-local imports; not a startup dependency list): `src.applications.base.i_application_model`, `src.applications.calibration.service.i_calibration_service`, `src.applications.calibration_settings.calibration_settings_data`, `src.applications.height_measuring.service.i_height_measuring_app_service`, `src.applications.intrinsic_calibration_capture.service.i_intrinsic_capture_service`, `src.shared_contracts.declarations`.

### `CalibrationModel`

```python
class CalibrationModel(IApplicationModel):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, service: ICalibrationService)
```

```python
def load(self) -> None
```

```python
def save(self, *args, **kwargs) -> None
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
def save_height_mapping_area(self, area_key: str, corners_norm) -> tuple[bool, str]
```

```python
def get_height_mapping_area(self, area_key: str) -> list[tuple[float, float]]
```

```python
def generate_area_grid(self, corners_norm, rows: int, cols: int) -> list[tuple[float, float]]
```

```python
def measure_area_grid(self, area_id: str, corners_norm, rows: int, cols: int) -> tuple[bool, str]
```

```python
def verify_area_grid(self, corners_norm, rows: int, cols: int, progress_callback=None) -> tuple[bool, str, dict]
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
