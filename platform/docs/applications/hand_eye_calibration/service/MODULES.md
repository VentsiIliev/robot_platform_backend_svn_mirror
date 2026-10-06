# Module reference: `src/applications/hand_eye_calibration/service`

[Package guide](README.md) · [Complete source index](../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [hand_eye_service.py](#hand_eye_servicepy)
- [i_hand_eye_service.py](#i_hand_eye_servicepy)

## `__init__.py`

Source: [src/applications/hand_eye_calibration/service/__init__.py](../../../../src/applications/hand_eye_calibration/service/__init__.py).

No top-level functions, classes or public value declarations; inspect the source for imports or entry-point statements.

## `hand_eye_service.py`

Source: [src/applications/hand_eye_calibration/service/hand_eye_service.py](../../../../src/applications/hand_eye_calibration/service/hand_eye_service.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `cv2`, `logging`, `math`, `numpy`, `os`, `src.applications.hand_eye_calibration.core.hand_eye_core`, `src.applications.hand_eye_calibration.service.i_hand_eye_service`, `src.engine.vision.i_capture_snapshot_service`, `threading`, `time`, `typing`.

### `HandEyeCalibrationService`

```python
class HandEyeCalibrationService(IHandEyeCalibrationService):
```

Automated hand-eye calibration service. Moves the robot through a set of diverse poses, captures a chessboard detection at each, and runs cv2.calibrateHandEye() to produce the camera-to-flange transform.

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, snapshot_service: ICaptureSnapshotService, robot_service, vision_service, robot_config, messaging=None)
```

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
def get_latest_annotated_frame(self) -> Optional[np.ndarray]
```

```python
def get_config(self) -> HandEyeConfig
```

```python
def save_config(self, config: HandEyeConfig) -> None
```

## `i_hand_eye_service.py`

Source: [src/applications/hand_eye_calibration/service/i_hand_eye_service.py](../../../../src/applications/hand_eye_calibration/service/i_hand_eye_service.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `abc`, `dataclasses`, `numpy`, `typing`.

Module declarations (expressions are shown without evaluating them):

```python
HAND_EYE_PROGRESS_TOPIC = 'HAND_EYE_PROGRESS'
HAND_EYE_COMPLETE_TOPIC = 'HAND_EYE_COMPLETE'
HAND_EYE_SAMPLE_COUNT_TOPIC = 'HAND_EYE_SAMPLE_COUNT'
```

### `HandEyeConfig`

```python
@dataclass
class HandEyeConfig:
```

Declared fields/defaults:

```python
chessboard_width: int = 17
chessboard_height: int = 11
square_size_mm: float = 15.0
n_poses: int = 20
rx_range_deg: float = 15.0
ry_range_deg: float = 15.0
rz_range_deg: float = 15.0
xy_range_mm: float = 60.0
z_range_mm: float = 80.0
stabilization_delay_s: float = 1.0
servo_stabilization_delay_s: float = 0.2
velocity: int = 20
acceleration: int = 10
probe_dx_mm: float = 15.0
probe_dy_mm: float = 15.0
probe_dz_mm: float = 15.0
probe_rotations: bool = True
probe_drx_deg: float = 8.0
probe_dry_deg: float = 8.0
probe_drz_deg: float = 8.0
servo_tol_px: int = 40
servo_max_iter: int = 8
servo_max_step_mm: float = 25.0
feedforward_max_step_mm: float = 20.0
search_radius_mm: float = 50.0
```

### `IHandEyeCalibrationService`

```python
class IHandEyeCalibrationService(ABC):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
@abstractmethod
def start_capture(self) -> None
```

Start automated pose collection and calibration in a background thread.

```python
@abstractmethod
def stop_capture(self) -> None
```

Request the background thread to stop.

```python
@abstractmethod
def is_running(self) -> bool
```

Return True while the background thread is alive.

```python
@abstractmethod
def get_latest_annotated_frame(self) -> Optional[np.ndarray]
```

Return the latest camera frame with detected chessboard corners overlaid.

```python
@abstractmethod
def get_config(self) -> HandEyeConfig
```

Return the current configuration.

```python
@abstractmethod
def save_config(self, config: HandEyeConfig) -> None
```

Persist a new configuration.
