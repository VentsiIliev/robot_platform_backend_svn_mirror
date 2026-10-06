# Module reference: `src/applications/pick_target/service`

[Package guide](README.md) · [Complete source index](../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [i_pick_target_service.py](#i_pick_target_servicepy)
- [pick_target_application_service.py](#pick_target_application_servicepy)
- [stub_pick_target_service.py](#stub_pick_target_servicepy)

## `__init__.py`

Source: [src/applications/pick_target/service/__init__.py](../../../../src/applications/pick_target/service/__init__.py).

No top-level functions, classes or public value declarations; inspect the source for imports or entry-point statements.

## `i_pick_target_service.py`

Source: [src/applications/pick_target/service/i_pick_target_service.py](../../../../src/applications/pick_target/service/i_pick_target_service.py).

Imports (including optional/function-local imports; not a startup dependency list): `abc`, `numpy`, `typing`.

Module declarations (expressions are shown without evaluating them):

```python
RobotPose = Tuple[float, float, float, float, float, float]
```

### `IPickTargetService`

```python
class IPickTargetService(ABC):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
@abstractmethod
def capture(self) -> Tuple[Optional[np.ndarray], List[Tuple[float, float]], List[RobotPose]]
```

Snapshot the current vision state. Returns (frame, pixel_centroids [(x_pixels, y_pixels)], robot_targets [(x, y, z, rx_degrees, ry_degrees, rz_degrees)]). Each robot target is a complete height-corrected approach pose. frame may be None if vision is unavailable.

```python
@abstractmethod
def move_to(self, x: float, y: float, z: float, rx: float, ry: float, rz: float) -> bool
```

Move robot to the given pose. z is the pre-computed height-corrected approach height.

```python
@abstractmethod
def move_to_base(self, x: float, y: float, rx: float, ry: float, rz: float, z: float | None=None) -> bool
```

Move robot to (x, y) at base Z with the given orientation — no height correction.

```python
@abstractmethod
def move_to_with_live_height(self, x: float, y: float, rx: float, ry: float, rz: float, z: float | None=None) -> bool
```

Move to (x, y) at base Z, measure surface height live, then adjust Z.

```python
@abstractmethod
def move_to_calibration_position(self) -> bool
```

Move robot to the mode-appropriate start position. Returns success.

```python
@abstractmethod
def set_target(self, target: str) -> None
```

Select the target reference: camera, tool, or gripper.

```python
@abstractmethod
def set_use_pickup_plane(self, enabled: bool) -> None
```

When True, map transformed points into the pickup plane and use pickup orientation.

```python
@abstractmethod
def set_pickup_plane_rz(self, rz: float) -> None
```

Set the pickup-plane RZ orientation used for manual testing.

```python
@abstractmethod
def capture_contour_trajectory(self) -> List[np.ndarray]
```

Transform the latest detected contours to robot-space waypoints. Returns a list of (N, 2) float32 arrays — one per detected contour. Each row is (robot_x, robot_y) in mm.

```python
@abstractmethod
def execute_contour_trajectory(self, contour_robot_pts: List[np.ndarray], z: float, vel: float, acc: float) -> Tuple[bool, str]
```

Execute a robot trajectory that traces the supplied contour waypoints. contour_robot_pts: list of (N, 2) float32 arrays in robot-space mm. z: fixed Z height in mm. vel / acc: normalised 0–1 speed fraction. Returns (success, message).

## `pick_target_application_service.py`

Source: [src/applications/pick_target/service/pick_target_application_service.py](../../../../src/applications/pick_target/service/pick_target_application_service.py).

Imports (including optional/function-local imports; not a startup dependency list): `cv2`, `datetime`, `logging`, `numpy`, `os`, `src.applications.pick_target.service.i_pick_target_service`, `src.engine.robot.height_measuring.i_height_correction_service`, `src.engine.robot.height_measuring.i_height_measuring_service`, `src.engine.robot.interfaces.i_robot_service`, `src.engine.robot.targeting`, `src.engine.vision.i_capture_snapshot_service`, `src.engine.vision.i_vision_service`, `src.engine.vision.implementation.VisionSystem.core.models.contour`, `typing`.

### `_rounded`

```python
def _rounded(values) -> list[float] | None
```

### `PickTargetApplicationService`

```python
class PickTargetApplicationService(IPickTargetService):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, vision_service: Optional[IVisionService], capture_snapshot_service: Optional[ICaptureSnapshotService], robot_service: Optional[IRobotService], resolver: Optional[VisionTargetResolver], resolver_getter=None, robot_config=None, robot_config_getter=None, navigation=None, height_measuring: Optional[IHeightMeasuringService]=None, default_target_name: str='', calibration_frame_name: str='', pickup_frame_name: str='', active_frame_name_getter: Optional[Callable[[], str]]=None, active_capture_group_getter: Optional[Callable[[], str]]=None)
```

```python
def set_target(self, target: str) -> None
```

```python
def set_use_pickup_plane(self, enabled: bool) -> None
```

```python
def set_pickup_plane_rz(self, rz: float) -> None
```

```python
def get_jog_reference_rz(self) -> float
```

```python
def capture(self) -> Tuple[Optional[np.ndarray], List[Tuple[float, float]], List[Tuple[float, float, float, float, float, float]]]
```

```python
def move_to(self, x: float, y: float, z: float, rx: float, ry: float, rz: float) -> bool
```

```python
def move_to_base(self, robot_x: float, robot_y: float, rx: float, ry: float, rz: float, z: float | None=None) -> bool
```

```python
def move_to_with_live_height(self, robot_x: float, robot_y: float, rx: float, ry: float, rz: float, z: float | None=None) -> bool
```

```python
def move_to_calibration_position(self) -> bool
```

```python
def capture_contour_trajectory(self) -> List[np.ndarray]
```

```python
def execute_contour_trajectory(self, contour_robot_pts: List[np.ndarray], z: float, vel: float, acc: float) -> Tuple[bool, str]
```

## `stub_pick_target_service.py`

Source: [src/applications/pick_target/service/stub_pick_target_service.py](../../../../src/applications/pick_target/service/stub_pick_target_service.py).

Imports (including optional/function-local imports; not a startup dependency list): `logging`, `numpy`, `src.applications.pick_target.service.i_pick_target_service`, `src.robot_systems.glue.targeting.registry`, `typing`.

### `StubPickTargetService`

```python
class StubPickTargetService(IPickTargetService):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self)
```

```python
def capture(self) -> Tuple[Optional[np.ndarray], List[Tuple[float, float]], List[Tuple[float, float, float, float, float, float]]]
```

```python
def move_to(self, x: float, y: float, z: float, rx: float, ry: float, rz: float) -> bool
```

```python
def move_to_base(self, x: float, y: float, rx: float, ry: float, rz: float) -> bool
```

```python
def move_to_with_live_height(self, x: float, y: float, rx: float, ry: float, rz: float) -> bool
```

```python
def move_to_calibration_position(self) -> bool
```

```python
def set_target(self, target: str) -> None
```

```python
def set_use_pickup_plane(self, enabled: bool) -> None
```

```python
def set_pickup_plane_rz(self, rz: float) -> None
```

```python
def capture_contour_trajectory(self) -> List[np.ndarray]
```

```python
def execute_contour_trajectory(self, contour_robot_pts: List[np.ndarray], z: float, vel: float, acc: float) -> Tuple[bool, str]
```
