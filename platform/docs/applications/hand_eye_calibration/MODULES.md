# Module reference: `src/applications/hand_eye_calibration`

[Package guide](README.md) · [Complete source index](../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [example_usage.py](#example_usagepy)
- [hand_eye_calibration_factory.py](#hand_eye_calibration_factorypy)

## `__init__.py`

Source: [src/applications/hand_eye_calibration/__init__.py](../../../src/applications/hand_eye_calibration/__init__.py).

No top-level functions, classes or public value declarations; inspect the source for imports or entry-point statements.

## `example_usage.py`

Source: [src/applications/hand_eye_calibration/example_usage.py](../../../src/applications/hand_eye_calibration/example_usage.py).

Standalone runner for the Hand-Eye Calibration application. Uses mock services so no hardware is required: - MockSnapshotService — returns a synthetic chessboard frame + varied robot pose - MockVisionService — provides a placeholder camera matrix and output path - MockRobotService — accepts move_ptp commands instantly - MockRobotConfig — provides tool/user numbers Run: python src/applications/hand_eye_calibration/example_usage.py

Imports (including optional/function-local imports; not a startup dependency list): `PyQt6.QtWidgets`, `__future__`, `cv2`, `math`, `numpy`, `os`, `src.applications.hand_eye_calibration.hand_eye_calibration_factory`, `src.applications.hand_eye_calibration.service.hand_eye_service`, `src.applications.hand_eye_calibration.service.i_hand_eye_service`, `src.engine.vision.i_capture_snapshot_service`, `sys`, `tempfile`, `threading`, `time`, `typing`.

### `_make_synthetic_board_frame`

```python
def _make_synthetic_board_frame(rvec, tvec)
```

Render a synthetic chessboard visible in the camera with given pose.

### `MockSnapshotService`

```python
class MockSnapshotService(ICaptureSnapshotService):
```

Returns a synthetic chessboard frame and a varied robot pose.

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def capture_snapshot(self, source: str='') -> VisionCaptureSnapshot
```

### `MockVisionService`

```python
class MockVisionService:
```

Declared fields/defaults:

```python
cameraMatrix = _K
cameraDist = _DIST
camera_to_robot_matrix_path = os.path.join(tempfile.gettempdir(), 'mock_hand_eye_result.npy')
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def get_latest_frame(self) -> Optional[np.ndarray]
```

### `MockRobotService`

```python
class MockRobotService:
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def get_current_position(self) -> List[float]
```

```python
def move_ptp(self, position, tool, user, velocity, acceleration, wait_to_reach=True) -> bool
```

### `MockRobotConfig`

```python
class MockRobotConfig:
```

Declared fields/defaults:

```python
robot_tool = 1
robot_user = 1
```

### `main`

```python
def main()
```

## `hand_eye_calibration_factory.py`

Source: [src/applications/hand_eye_calibration/hand_eye_calibration_factory.py](../../../src/applications/hand_eye_calibration/hand_eye_calibration_factory.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `src.applications.base.application_factory`, `src.applications.base.i_application_controller`, `src.applications.base.i_application_model`, `src.applications.base.i_application_view`, `src.applications.hand_eye_calibration.controller.hand_eye_controller`, `src.applications.hand_eye_calibration.model.hand_eye_model`, `src.applications.hand_eye_calibration.view.hand_eye_view`.

### `HandEyeCalibrationFactory`

```python
class HandEyeCalibrationFactory(ApplicationFactory):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, messaging=None)
```

```python
def build(self, service, messaging=None, jog_service=None)
```
