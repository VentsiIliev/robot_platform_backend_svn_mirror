# Module reference: `src/engine/vision/implementation/VisionSystem/features/calibration/charuco`

[Package guide](README.md) · [Complete source index](../../../../../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [charuco_calibrator.py](#charuco_calibratorpy)
- [charuco_detector.py](#charuco_detectorpy)

## `__init__.py`

Source: [src/engine/vision/implementation/VisionSystem/features/calibration/charuco/__init__.py](../../../../../../../../src/engine/vision/implementation/VisionSystem/features/calibration/charuco/__init__.py).

Imports (including optional/function-local imports; not a startup dependency list): `.charuco_calibrator`, `.charuco_detector`.

Package-level import/export surface:

```python
from .charuco_detector import AutoCharucoBoardDetector, CharucoBoardDetector, DetectionResult
from .charuco_calibrator import CharucoCalibrator
```

Module declarations (expressions are shown without evaluating them):

```python
__all__ = ['DetectionResult', 'CharucoBoardDetector', 'AutoCharucoBoardDetector', 'CharucoCalibrator']
```

## `charuco_calibrator.py`

Source: [src/engine/vision/implementation/VisionSystem/features/calibration/charuco/charuco_calibrator.py](../../../../../../../../src/engine/vision/implementation/VisionSystem/features/calibration/charuco/charuco_calibrator.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `cv2`, `logging`, `numpy`, `typing`.

### `CharucoCalibrator`

```python
class CharucoCalibrator:
```

Collects ChArUco corner detections across multiple frames and runs cv2.calibrateCamera to produce camera intrinsics. Typical usage:: calibrator = CharucoCalibrator(detector.normal.board) for image, corners, ids in frames: calibrator.add_frame(image, corners, ids) rms, K, dist, rvecs, tvecs = calibrator.calibrate()

Declared fields/defaults:

```python
MIN_CORNERS_PER_FRAME = 6
MIN_FRAMES = 5
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, board: cv2.aruco.CharucoBoard) -> None
```

```python
@property
def frame_count(self) -> int
```

```python
def add_frame(self, image: np.ndarray, charuco_corners: Optional[np.ndarray], charuco_ids: Optional[np.ndarray]) -> bool
```

Add one detection to the calibration set. Returns True if the frame was accepted (enough corners detected).

```python
def clear(self) -> None
```

```python
def calibrate(self) -> Tuple[float, np.ndarray, np.ndarray, list, list]
```

Run calibration on all collected frames. Returns: (rms, camera_matrix, dist_coeffs, rvecs, tvecs) Raises: RuntimeError if not enough valid frames.

## `charuco_detector.py`

Source: [src/engine/vision/implementation/VisionSystem/features/calibration/charuco/charuco_detector.py](../../../../../../../../src/engine/vision/implementation/VisionSystem/features/calibration/charuco/charuco_detector.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `cv2`, `dataclasses`, `numpy`, `typing`.

### `DetectionResult`

```python
@dataclass
class DetectionResult:
```

Declared fields/defaults:

```python
mode: str
charuco_corners: Optional[np.ndarray]
charuco_ids: Optional[np.ndarray]
marker_corners: Tuple[np.ndarray, ...]
marker_ids: Optional[np.ndarray]
vis: np.ndarray
rvec: Optional[np.ndarray]
tvec: Optional[np.ndarray]
```

### `CharucoBoardDetector`

```python
class CharucoBoardDetector:
```

Single ChArUco detector for one board convention (normal or legacy).

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, squares_x: int=5, squares_y: int=6, square_length: float=0.04, marker_length: float=0.02, dictionary_id: int=cv2.aruco.DICT_4X4_50, legacy_pattern: bool=False) -> None
```

```python
def generate_board_image(self, out_size: Tuple[int, int]=(900, 1100), margin_size: int=20, border_bits: int=1) -> np.ndarray
```

```python
def detect_raw(self, image: np.ndarray)
```

### `AutoCharucoBoardDetector`

```python
class AutoCharucoBoardDetector:
```

Try new convention first, then legacy convention — keep the better result. Also estimates board pose and draws coordinate axes when enough ChArUco corners are detected.

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, squares_x: int=5, squares_y: int=6, square_length: float=0.04, marker_length: float=0.02, dictionary_id: int=cv2.aruco.DICT_4X4_50) -> None
```

```python
def detect(self, image: np.ndarray, camera_matrix: Optional[np.ndarray]=None, dist_coeffs: Optional[np.ndarray]=None) -> DetectionResult
```

Detect ChArUco corners in *image*. Optionally pass *camera_matrix* and *dist_coeffs* so that the pose estimate and axis overlay use real intrinsics instead of the demo approximation.
