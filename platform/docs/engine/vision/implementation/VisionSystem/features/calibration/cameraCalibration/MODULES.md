# Module reference: `src/engine/vision/implementation/VisionSystem/features/calibration/cameraCalibration`

[Package guide](README.md) · [Complete source index](../../../../../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [CameraCalibrationService.py](#cameracalibrationservicepy)
- [__init__.py](#__init__py)

## `CameraCalibrationService.py`

Source: [src/engine/vision/implementation/VisionSystem/features/calibration/cameraCalibration/CameraCalibrationService.py](../../../../../../../../src/engine/vision/implementation/VisionSystem/features/calibration/cameraCalibration/CameraCalibrationService.py).

Imports (including optional/function-local imports; not a startup dependency list): `cv2`, `cv2.aruco`, `dataclasses`, `logging`, `numpy`, `os`, `src.engine.vision.implementation.plvision.PLVision.Calibration`, `traceback`, `typing`.

### `CameraCalibrationServiceResult`

```python
@dataclass
class CameraCalibrationServiceResult:
```

Result class for camera calibration operations. Contains all the data returned from a calibration operation including success status, calibration matrices, and diagnostic information.

Declared fields/defaults:

```python
success: bool
message: str
camera_matrix: Optional[np.ndarray] = None
distortion_coefficients: Optional[np.ndarray] = None
perspective_matrix: Optional[np.ndarray] = None
rotation_vectors: Optional[List[np.ndarray]] = None
translation_vectors: Optional[List[np.ndarray]] = None
valid_images_count: int = 0
calibration_error: Optional[float] = None
storage_path: Optional[str] = None
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
@property
def calibration_data(self) -> Optional[List[np.ndarray]]
```

Legacy format: [distortion_coefficients, camera_matrix] For backward compatibility with existing code.

```python
@property
def is_calibrated(self) -> bool
```

Check if calibration was successful and has valid data.

```python
def to_legacy_tuple(self) -> tuple
```

Convert to legacy tuple format for backward compatibility. Returns: (success, calibration_data, perspective_matrix, message)

### `CameraCalibrationService`

```python
class CameraCalibrationService:
```

Declared fields/defaults:

```python
DEFAULT_STORAGE_PATH = os.path.join(os.path.dirname(__file__), 'storage', 'calibration_result')
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, chessboardWidth, chessboardHeight, squareSizeMM, skipFrames, message_publisher, storagePath, onDetectionFailed=None, messaging_service=None)
```

```python
@property
def PERSPECTIVE_MATRIX_PATH(self)
```

Dynamic path to a perspective transform matrix file

```python
@property
def CAMERA_TO_ROBOT_MATRIX_PATH(self)
```

Dynamic path to camera-to-robot matrix file

```python
def detectArucoMarkers(self, flip=False, image=None)
```

Detects ArUco markers in the provided image. Returns corners, ids, and the (possibly flipped) image.

```python
def detectPerspectiveCorrectionMarkers(self, image)
```

Detect ArUco markers (IDs 30, 31, 32, 33) for perspective correction. Returns corners in order: top-left (30), top-right (31), bottom-right (32), bottom-left (33)

```python
def computePerspectiveCorrection(self, image, src_corners, output_size=(1280, 720))
```

Compute perspective transformation matrix and apply correction.

```python
def cleanupOldCalibrationFiles(self)
```

Delete old calibration files to ensure fresh calibration.

```python
def run(self, image, debug=True) -> CameraCalibrationServiceResult
```

Main calibration workflow with perspective correction support. Returns CameraCalibrationServiceResult containing all calibration data.

```python
def publish(self, message)
```

```python
def compute_total_reprojection_error(self, objpoints, imgpoints, rvecs, tvecs, camera_matrix, dist_coeffs)
```

Compute the total mean reprojection error for all calibration images. Parameters: objpoints : list of np.ndarray, 3D object points in world coordinates imgpoints : list of np.ndarray, 2D image points detected rvecs : list of np.ndarray, rotation vectors from calibration tvecs : list of np.ndarray, translation vectors from calibration camera_matrix: np.ndarray, intrinsic camera matrix dist_coeffs : np.ndarray, distortion coefficients Returns: mean_error : float, average reprojection error in pixels

```python
def visualize_reprojection(self, objpoints, imgpoints, rvecs, tvecs, camera_matrix, dist_coeffs)
```

Visualize reprojection of 3D points onto calibration images. objpoints: list of 3D object points imgpoints: list of detected 2D image points rvecs, tvecs: rotation and translation vectors from calibrateCamera camera_matrix, dist_coeffs: calibration parameters

```python
def visualize_corner_coverage(self, img_shape=None, point_size=3)
```

Draw all detected chessboard corners from all calibration images onto a single black-and-white canvas to visualize coverage. img_shape: tuple (height, width), optional. Defaults to first image shape. point_size: int, radius of circles to draw

## `__init__.py`

Source: [src/engine/vision/implementation/VisionSystem/features/calibration/cameraCalibration/__init__.py](../../../../../../../../src/engine/vision/implementation/VisionSystem/features/calibration/cameraCalibration/__init__.py).

No top-level functions, classes or public value declarations; inspect the source for imports or entry-point statements.
