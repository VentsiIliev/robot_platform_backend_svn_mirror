# Module reference: `src/applications/hand_eye_calibration/core`

[Package guide](README.md) · [Complete source index](../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [hand_eye_core.py](#hand_eye_corepy)

## `__init__.py`

Source: [src/applications/hand_eye_calibration/core/__init__.py](../../../../src/applications/hand_eye_calibration/core/__init__.py).

No top-level functions, classes or public value declarations; inspect the source for imports or entry-point statements.

## `hand_eye_core.py`

Source: [src/applications/hand_eye_calibration/core/hand_eye_core.py](../../../../src/applications/hand_eye_calibration/core/hand_eye_core.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `cv2`, `math`, `numpy`, `typing`.

### `BoardInfo`

```python
class BoardInfo(NamedTuple):
```

Declared fields/defaults:

```python
cx: float
cy: float
bbox_w: float
bbox_h: float
area: float
```

### `euler_to_rotmat`

```python
def euler_to_rotmat(rx_deg: float, ry_deg: float, rz_deg: float) -> np.ndarray
```

ZYX convention: Rz @ Ry @ Rx — matches Fairino TCP format (degrees in).

### `tcp_to_matrix`

```python
def tcp_to_matrix(pose: List[float]) -> np.ndarray
```

[x_mm, y_mm, z_mm, rx_deg, ry_deg, rz_deg] → 4×4 homogeneous transform.

### `generate_diverse_poses`

```python
def generate_diverse_poses(home_pose: List[float], n_poses: int, rx_range_deg: float, ry_range_deg: float, rz_range_deg: float, xy_range_mm: float, z_range_mm: float, rng_seed: int=42) -> List[List[float]]
```

Sample n_poses absolute poses within specified ranges around home_pose. Uses a scrambled Latin-hypercube strategy across all 6 axes so that samples are spread evenly — avoids clustering that pure random gives. Returns list of [x, y, z, rx, ry, rz] in mm / degrees.

### `detect_board_center`

```python
def detect_board_center(frame: np.ndarray, pattern_size: Tuple[int, int]) -> Optional[Tuple[float, float]]
```

Legacy wrapper — returns (cx, cy) only.

### `detect_board_info`

```python
def detect_board_info(frame: np.ndarray, pattern_size: Tuple[int, int]) -> Optional[BoardInfo]
```

Lightweight chessboard detection returning center, bounding-box dimensions and area in pixels — no PnP, no camera params required. Used in the servo loop. Returns None if the board is not found.

### `detect_chessboard_pose`

```python
def detect_chessboard_pose(frame: np.ndarray, pattern_size: Tuple[int, int], square_size_mm: float, camera_matrix: np.ndarray, dist_coeffs: np.ndarray) -> Tuple[Optional[np.ndarray], Optional[np.ndarray], np.ndarray]
```

Detect chessboard inner corners and compute board-to-camera transform. pattern_size = (inner_cols, inner_rows) Returns: R_cam — 3×3 rotation (board frame → camera frame), or None if not found t_cam — 3×1 translation (mm), or None if not found annotated_frame — copy of frame with corners / axes drawn

### `compute_hand_eye`

```python
def compute_hand_eye(R_robot: List[np.ndarray], t_robot: List[np.ndarray], R_cam: List[np.ndarray], t_cam: List[np.ndarray], method: int=cv2.CALIB_HAND_EYE_TSAI) -> np.ndarray
```

Run cv2.calibrateHandEye and return the 4×4 camera-to-flange transform. Input lists must all have the same length (≥ 4 samples).
