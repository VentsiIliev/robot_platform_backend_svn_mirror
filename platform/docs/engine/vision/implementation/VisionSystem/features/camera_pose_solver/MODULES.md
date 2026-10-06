# Module reference: `src/engine/vision/implementation/VisionSystem/features/camera_pose_solver`

[Package guide](README.md) · [Complete source index](../../../../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [helpers.py](#helperspy)
- [pose_solver.py](#pose_solverpy)

## `__init__.py`

Source: [src/engine/vision/implementation/VisionSystem/features/camera_pose_solver/__init__.py](../../../../../../../src/engine/vision/implementation/VisionSystem/features/camera_pose_solver/__init__.py).

No top-level functions, classes or public value declarations; inspect the source for imports or entry-point statements.

## `helpers.py`

Source: [src/engine/vision/implementation/VisionSystem/features/camera_pose_solver/helpers.py](../../../../../../../src/engine/vision/implementation/VisionSystem/features/camera_pose_solver/helpers.py).

Imports (including optional/function-local imports; not a startup dependency list): `logging`, `numpy`.

### `print_pose_explained`

```python
def print_pose_explained(pose_matrix)
```

## `pose_solver.py`

Source: [src/engine/vision/implementation/VisionSystem/features/camera_pose_solver/pose_solver.py](../../../../../../../src/engine/vision/implementation/VisionSystem/features/camera_pose_solver/pose_solver.py).

Imports (including optional/function-local imports; not a startup dependency list): `core.services.vision`, `core.services.vision.VisionService`, `cv2`, `dataclasses`, `logging`, `modules.VisionSystem.calibration.cameraCalibration.CameraCalibrationService`, `modules.VisionSystem.camera_pose_solver.helpers`, `numpy`, `threading`, `time`.

### `PnPConfig`

```python
@dataclass
class PnPConfig:
```

Declared fields/defaults:

```python
camera_matrix: np.ndarray
dist_coeffs: np.ndarray
units: str = 'mm'
```

### `CameraPoseSolver`

```python
class CameraPoseSolver:
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, config: PnPConfig)
```

```python
def solve_pnp(self, object_points: np.ndarray, image_points: np.ndarray, flags=cv2.SOLVEPNP_ITERATIVE)
```

Solve PnP for a given set of 3D object points and corresponding 2D image points. Args: object_points (np.ndarray): Nx3 array of 3D points in the object frame (same units as self.units). image_points (np.ndarray): Nx2 array of 2D points in image coordinates. flags: cv2 solvePnP flag Returns: rvec (np.ndarray): Rotation vector (3x1) tvec (np.ndarray): Translation vector (3x1) pose_matrix (np.ndarray): 4x4 homogeneous transformation matrix reproj_error (float): RMS reprojection error in pixels
