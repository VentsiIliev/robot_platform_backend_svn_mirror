# Module reference: `src/engine/vision/implementation/VisionSystem/features/hand_eye`

[Package guide](README.md) · [Complete source index](../../../../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [collect_robot_poses.py](#collect_robot_posespy)
- [eye_in_hand_calibration.py](#eye_in_hand_calibrationpy)
- [ttest_eye_in_hand.py](#ttest_eye_in_handpy)

## `__init__.py`

Source: [src/engine/vision/implementation/VisionSystem/features/hand_eye/__init__.py](../../../../../../../src/engine/vision/implementation/VisionSystem/features/hand_eye/__init__.py).

No top-level functions, classes or public value declarations; inspect the source for imports or entry-point statements.

## `collect_robot_poses.py`

Source: [src/engine/vision/implementation/VisionSystem/features/hand_eye/collect_robot_poses.py](../../../../../../../src/engine/vision/implementation/VisionSystem/features/hand_eye/collect_robot_poses.py).

Imports (including optional/function-local imports; not a startup dependency list): `core.application`, `core.application.ApplicationContext`, `core.application.interfaces.application_settings_interface`, `core.base_robot_application`, `core.model.robot`, `core.model.robot.robot_types`, `core.services.robot_service.impl.RobotStateManager`, `core.services.robot_service.impl.base_robot_service`, `core.services.robot_service.impl.robot_monitor.robot_monitor_factory`, `core.services.settings.SettingsService`, `core.services.vision.VisionService`, `cv2`, `logging`, `modules.VisionSystem.laser_detection.laser_detection_service`, `modules.shared.tools.Laser`, `threading`, `time`.

Module declarations (expressions are shown without evaluating them):

```python
USE_CHESSBOARD = True
BOARD_SIZE = (17, 11)
```

### `main`

```python
def main()
```

## `eye_in_hand_calibration.py`

Source: [src/engine/vision/implementation/VisionSystem/features/hand_eye/eye_in_hand_calibration.py](../../../../../../../src/engine/vision/implementation/VisionSystem/features/hand_eye/eye_in_hand_calibration.py).

Imports (including optional/function-local imports; not a startup dependency list): `core.application`, `core.application.ApplicationContext`, `core.application.interfaces.application_settings_interface`, `core.base_robot_application`, `core.model.robot`, `core.model.robot.robot_types`, `core.services.robot_service.impl.RobotStateManager`, `core.services.robot_service.impl.base_robot_service`, `core.services.robot_service.impl.robot_monitor.robot_monitor_factory`, `core.services.settings.SettingsService`, `core.services.vision.VisionService`, `cv2`, `logging`, `numpy`, `threading`, `time`.

Module declarations (expressions are shown without evaluating them):

```python
USE_CHESSBOARD = True
BOARD_SIZE = (17, 11)
SQUARE_SIZE = 15.0
MIN_Z = 300
POSES = [[-19.961, 332.22, 819.139, 179.872, 0.021, 0.0], [296.946, 426.645, 494.714, 166.919, 12.173, -22.76], [39.719, 282.852, 502.54, -168.716, 6.191, -3.811], [-31.286, 595.141, 461.606, 153.23, -0.117, -6.009], [-356.514, 453.0, 406.893, 167.567, -31.56, 10.675], [-21.758, 551.845, 528.024, 166.311, -20.532, -72.128], [-208.61, 593.086, 450.321, 148.397, -10.375, 35.123], [255.291, 524.126, 486.553, 159.341, 5.838, -34.464], [-39.079, 384.35, 422.272, 178.944, 3.165, -2.582]]
objp = np.zeros((BOARD_SIZE[0] * BOARD_SIZE[1], 3), np.float32)
```

### `deg2rad`

```python
def deg2rad(deg)
```

### `wrap_angle_180`

```python
def wrap_angle_180(angle)
```

### `enforce_limits`

```python
def enforce_limits(pose)
```

### `euler_to_rotmat`

```python
def euler_to_rotmat(rx, ry, rz)
```

Convert Euler angles (degrees) to rotation matrix

### `tcp_to_matrix`

```python
def tcp_to_matrix(tcp_pose)
```

### `show_camera`

```python
def show_camera(vs, stop_event)
```

### `move_robot_to_pose`

```python
def move_robot_to_pose(robot_service: RobotService, pose)
```

### `wait_for_chessboard`

```python
def wait_for_chessboard(vs, timeout=15)
```

### `collect_hand_eye_samples`

```python
def collect_hand_eye_samples(robot_service: RobotService, vs)
```

### `compute_hand_eye`

```python
def compute_hand_eye()
```

### `run_hand_eye`

```python
def run_hand_eye()
```

## `ttest_eye_in_hand.py`

Source: [src/engine/vision/implementation/VisionSystem/features/hand_eye/ttest_eye_in_hand.py](../../../../../../../src/engine/vision/implementation/VisionSystem/features/hand_eye/ttest_eye_in_hand.py).

Imports (including optional/function-local imports; not a startup dependency list): `core.application`, `core.application.ApplicationContext`, `core.application.interfaces.application_settings_interface`, `core.base_robot_application`, `core.model.robot`, `core.model.robot.robot_types`, `core.services.robot_service.impl.RobotStateManager`, `core.services.robot_service.impl.base_robot_service`, `core.services.robot_service.impl.robot_monitor.robot_monitor_factory`, `core.services.settings.SettingsService`, `core.services.vision.VisionService`, `cv2`, `logging`, `numpy`, `threading`, `time`.

Module declarations (expressions are shown without evaluating them):

```python
USE_CHESSBOARD = True
BOARD_SIZE = (17, 11)
SQUARE_SIZE = 15.0
objp = np.zeros((BOARD_SIZE[0] * BOARD_SIZE[1], 3), np.float32)
```

### `main`

```python
def main()
```
