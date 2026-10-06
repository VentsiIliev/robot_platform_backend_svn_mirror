# Module reference: `src/engine/robot/calibration/intrinsic_capture`

[Package guide](README.md) · [Complete source index](../../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [runner.py](#runnerpy)
- [types.py](#typespy)
- [vision_helpers.py](#vision_helperspy)

## `__init__.py`

Source: [src/engine/robot/calibration/intrinsic_capture/__init__.py](../../../../../src/engine/robot/calibration/intrinsic_capture/__init__.py).

Imports (including optional/function-local imports; not a startup dependency list): `src.engine.robot.calibration.intrinsic_capture.runner`, `src.engine.robot.calibration.intrinsic_capture.types`.

Package-level import/export surface:

```python
from src.engine.robot.calibration.intrinsic_capture.runner import capture_intrinsic_dataset
from src.engine.robot.calibration.intrinsic_capture.types import BoardDetection, BoardType, CaptureSample, FeasibleRegion, ImageInfo, LocalJacobian2D, TargetRegion, TiltAxis
```

Module declarations (expressions are shown without evaluating them):

```python
__all__ = ['BoardDetection', 'BoardType', 'CaptureSample', 'FeasibleRegion', 'ImageInfo', 'LocalJacobian2D', 'TargetRegion', 'TiltAxis', 'capture_intrinsic_dataset']
```

## `runner.py`

Source: [src/engine/robot/calibration/intrinsic_capture/runner.py](../../../../../src/engine/robot/calibration/intrinsic_capture/runner.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `logging`, `numpy`, `src.engine.robot.calibration.intrinsic_capture.types`, `src.engine.robot.calibration.intrinsic_capture.vision_helpers`, `src.engine.vision.implementation.VisionSystem.features.calibration.charuco`, `threading`, `time`, `typing`.

### `_detect_with_retry`

```python
def _detect_with_retry(grab_frame_fn: Callable[[], np.ndarray], detect_fn: Callable[[np.ndarray], BoardDetection], max_retries: int=1) -> Tuple[np.ndarray, BoardDetection]
```

### `estimate_local_xy_jacobian`

```python
def estimate_local_xy_jacobian(get_pose_fn: Callable[[], List[float]], move_relative_fn: Callable[..., bool], move_absolute_fn: Callable[[List[float]], bool], grab_frame_fn: Callable[[], np.ndarray], detect_fn: Callable[[np.ndarray], BoardDetection], probe_dx_mm: float=20.0, probe_dy_mm: float=20.0, probe_drx_deg: float=3.0, probe_dry_deg: float=3.0, probe_drz_deg: float=0.0, max_detection_retries: int=1, move_absolute_fast_fn: Optional[Callable[[List[float]], bool]]=None) -> LocalJacobian2D
```

### `_inside_target_region`

```python
def _inside_target_region(det: BoardDetection, region: TargetRegion) -> bool
```

### `move_board_center_near_region`

```python
def move_board_center_near_region(grab_frame_fn: Callable[[], np.ndarray], move_relative_fn: Callable[..., bool], detect_fn: Callable[[np.ndarray], BoardDetection], region: TargetRegion, jacobian: LocalJacobian2D, max_refines: int=2, gain: float=0.9, max_detection_retries: int=1) -> bool
```

### `_predict_tilt_sign`

```python
def _predict_tilt_sign(board_center: Tuple[float, float], image_info: ImageInfo, tilt_axis: TiltAxis, tilt_deg: float, jacobian: LocalJacobian2D, margin_px: float=40.0) -> float
```

### `capture_charuco_sweep_dataset`

```python
def capture_charuco_sweep_dataset(get_pose_fn: Callable[[], List[float]], move_relative_fn: Callable[..., bool], move_absolute_fn: Callable[[List[float]], bool], grab_frame_fn: Callable[[], np.ndarray], save_frame_fn: Callable[[np.ndarray, str], Optional[str]], image_info: ImageInfo, pattern_size: Tuple[int, int], square_size_mm: float, marker_size_mm: float, aruco_dict_id: int, grid_rows: int, grid_cols: int, sweep_x_mm: float, sweep_y_mm: float, tilt_deg: float, z_delta_mm: float, min_corners: int, stabilization_delay_s: float, stop_event: threading.Event, progress_cb: Callable[[str], None], initial_detection_attempts: int=5, initial_detection_delay_s: float=1.0, max_detection_retries: int=1, detection_callback: Optional[Callable]=None, rz_deg: float=0.0, margin_px: float=60.0, probe_dx_mm: float=20.0, probe_dy_mm: float=20.0) -> List[CaptureSample]
```

### `capture_intrinsic_dataset`

```python
def capture_intrinsic_dataset(get_pose_fn: Callable[[], List[float]], move_relative_fn: Callable[..., bool], move_absolute_fn: Callable[[List[float]], bool], grab_frame_fn: Callable[[], np.ndarray], save_frame_fn: Callable[[np.ndarray, str], Optional[str]], image_info: ImageInfo, pattern_size: Tuple[int, int], board_type: BoardType, square_size_mm: float, marker_size_mm: float, aruco_dict_id: int, grid_rows: int, grid_cols: int, margin_px: float, tilt_deg: float, z_delta_mm: float, probe_dx_mm: float, probe_dy_mm: float, probe_drx_deg: float, probe_dry_deg: float, probe_drz_deg: float, stabilization_delay_s: float, stop_event: threading.Event, progress_cb: Callable[[str], None], max_detection_retries: int=1, initial_detection_attempts: int=5, initial_detection_delay_s: float=1.0, charuco_sweep_x_mm: float=100.0, charuco_sweep_y_mm: float=100.0, charuco_min_corners: int=6, charuco_rz_deg: float=0.0, detection_callback: Optional[Callable]=None) -> List[CaptureSample]
```

## `types.py`

Source: [src/engine/robot/calibration/intrinsic_capture/types.py](../../../../../src/engine/robot/calibration/intrinsic_capture/types.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `dataclasses`, `enum`, `numpy`, `typing`.

### `BoardType`

```python
class BoardType(str, Enum):
```

Declared fields/defaults:

```python
CHESSBOARD = 'chessboard'
CHARUCO = 'charuco'
```

### `BoardDetection`

```python
@dataclass
class BoardDetection:
```

Declared fields/defaults:

```python
found: bool
corners_px: Optional[np.ndarray] = None
center_px: Optional[Tuple[float, float]] = None
bbox_px: Optional[Tuple[float, float, float, float]] = None
width_px: Optional[float] = None
height_px: Optional[float] = None
```

### `ImageInfo`

```python
@dataclass
class ImageInfo:
```

Declared fields/defaults:

```python
width: int
height: int
```

### `FeasibleRegion`

```python
@dataclass
class FeasibleRegion:
```

Declared fields/defaults:

```python
min_cx: float
min_cy: float
max_cx: float
max_cy: float
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def contains(self, cx: float, cy: float) -> bool
```

### `TargetRegion`

```python
@dataclass
class TargetRegion:
```

Declared fields/defaults:

```python
name: str
center_px: Tuple[float, float]
tol_px: Tuple[float, float]
```

### `CaptureSample`

```python
@dataclass
class CaptureSample:
```

Declared fields/defaults:

```python
region_name: str
mode: str
pose: list
image_path: Optional[str] = None
```

### `TiltAxis`

```python
class TiltAxis(str, Enum):
```

Declared fields/defaults:

```python
ROLL = 'roll'
PITCH = 'pitch'
YAW = 'yaw'
```

### `LocalJacobian2D`

```python
@dataclass
class LocalJacobian2D:
```

Declared fields/defaults:

```python
J: np.ndarray
tilt_sensitivity: Optional[dict] = None
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def robot_delta_from_pixel_error(self, du: float, dv: float) -> Tuple[float, float]
```

```python
def predict_board_shift_px(self, axis: TiltAxis, angle_deg: float) -> Optional[Tuple[float, float]]
```

## `vision_helpers.py`

Source: [src/engine/robot/calibration/intrinsic_capture/vision_helpers.py](../../../../../src/engine/robot/calibration/intrinsic_capture/vision_helpers.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `cv2`, `logging`, `numpy`, `src.engine.robot.calibration.intrinsic_capture.types`, `src.engine.vision.implementation.VisionSystem.features.calibration.charuco`, `typing`.

### `detect_board`

```python
def detect_board(frame: np.ndarray, pattern_size: Tuple[int, int], board_type: BoardType, square_size_mm: float=25.0, marker_size_mm: float=0.0, aruco_dict_id: int=cv2.aruco.DICT_4X4_250) -> BoardDetection
```

### `detect_chessboard`

```python
def detect_chessboard(frame: np.ndarray, pattern_size: Tuple[int, int]) -> BoardDetection
```

### `detect_charuco_board`

```python
def detect_charuco_board(frame: np.ndarray, pattern_size: Tuple[int, int], square_size_mm: float=25.0, marker_size_mm: float=0.0, aruco_dict_id: int=cv2.aruco.DICT_4X4_250) -> BoardDetection
```

### `_board_detection_from_corners`

```python
def _board_detection_from_corners(corners: np.ndarray) -> BoardDetection
```

### `compute_feasible_region`

```python
def compute_feasible_region(image: ImageInfo, det: BoardDetection, margin_px: float=60.0) -> FeasibleRegion
```

### `make_grid_regions`

```python
def make_grid_regions(feasible: FeasibleRegion, grid_rows: int=3, grid_cols: int=3, tol_ratio: float=0.25) -> List[TargetRegion]
```
