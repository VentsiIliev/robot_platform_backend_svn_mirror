# Module reference: `src/applications/intrinsic_calibration_capture`

[Package guide](README.md) · [Complete source index](../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [example_usage.py](#example_usagepy)
- [intrinsic_capture_factory.py](#intrinsic_capture_factorypy)

## `__init__.py`

Source: [src/applications/intrinsic_calibration_capture/__init__.py](../../../src/applications/intrinsic_calibration_capture/__init__.py).

No top-level functions, classes or public value declarations; inspect the source for imports or entry-point statements.

## `example_usage.py`

Source: [src/applications/intrinsic_calibration_capture/example_usage.py](../../../src/applications/intrinsic_calibration_capture/example_usage.py).

Standalone runner for the IntrinsicCaptureApplication. Uses mock robot and vision services so no hardware is required. Run with: python src/applications/intrinsic_calibration_capture/example_usage.py

Imports (including optional/function-local imports; not a startup dependency list): `PyQt6.QtWidgets`, `__future__`, `cv2`, `numpy`, `os`, `src.applications.intrinsic_calibration_capture.intrinsic_capture_factory`, `src.applications.intrinsic_calibration_capture.service.intrinsic_capture_service`, `sys`.

### `MockRobotConfig`

```python
class MockRobotConfig:
```

Declared fields/defaults:

```python
robot_tool = 0
robot_user = 0
```

### `MockRobotService`

```python
class MockRobotService:
```

Returns a fixed pose; all moves succeed instantly.

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self)
```

```python
def get_current_position(self)
```

```python
def move_ptp(self, position, tool=0, user=0, velocity=30, acceleration=10, wait_to_reach=True)
```

### `MockVisionService`

```python
class MockVisionService:
```

Returns a synthetic chessboard image so detection always succeeds. Chessboard: 9 cols × 6 rows inner corners, 60px squares, centred in 1280×720.

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self)
```

```python
def get_latest_frame(self) -> np.ndarray
```

```python
def get_chessboard_width(self) -> int
```

```python
def get_chessboard_height(self) -> int
```

```python
def get_camera_width(self) -> int
```

```python
def get_camera_height(self) -> int
```

### `main`

```python
def main()
```

## `intrinsic_capture_factory.py`

Source: [src/applications/intrinsic_calibration_capture/intrinsic_capture_factory.py](../../../src/applications/intrinsic_calibration_capture/intrinsic_capture_factory.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `src.applications.base.application_factory`, `src.applications.base.i_application_controller`, `src.applications.base.i_application_model`, `src.applications.base.i_application_view`, `src.applications.intrinsic_calibration_capture.controller.intrinsic_capture_controller`, `src.applications.intrinsic_calibration_capture.model.intrinsic_capture_model`, `src.applications.intrinsic_calibration_capture.view.intrinsic_capture_view`.

### `IntrinsicCaptureFactory`

```python
class IntrinsicCaptureFactory(ApplicationFactory):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, messaging=None)
```

```python
def build(self, service, messaging=None, jog_service=None)
```
