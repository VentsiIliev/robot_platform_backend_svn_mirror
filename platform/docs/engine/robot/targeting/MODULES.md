# Module reference: `src/engine/robot/targeting`

[Package guide](README.md) · [Complete source index](../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [end_effector_point.py](#end_effector_pointpy)
- [jog_frame_pose_resolver.py](#jog_frame_pose_resolverpy)
- [point_registry.py](#point_registrypy)
- [remote_tcp_settings.py](#remote_tcp_settingspy)
- [robot_system_targeting_provider.py](#robot_system_targeting_providerpy)
- [target_frame.py](#target_framepy)
- [target_frame_settings.py](#target_frame_settingspy)
- [target_point_geometry.py](#target_point_geometrypy)
- [targeting_settings.py](#targeting_settingspy)
- [vision_pose_request.py](#vision_pose_requestpy)
- [vision_target_resolver.py](#vision_target_resolverpy)

## `__init__.py`

Source: [src/engine/robot/targeting/__init__.py](../../../../src/engine/robot/targeting/__init__.py).

Imports (including optional/function-local imports; not a startup dependency list): `src.engine.robot.targeting.end_effector_point`, `src.engine.robot.targeting.jog_frame_pose_resolver`, `src.engine.robot.targeting.point_registry`, `src.engine.robot.targeting.remote_tcp_settings`, `src.engine.robot.targeting.robot_system_targeting_provider`, `src.engine.robot.targeting.target_frame`, `src.engine.robot.targeting.target_frame_settings`, `src.engine.robot.targeting.target_point_geometry`, `src.engine.robot.targeting.targeting_settings`, `src.engine.robot.targeting.vision_pose_request`, `src.engine.robot.targeting.vision_target_resolver`, `src.shared_contracts.declarations`.

Package-level import/export surface:

```python
from src.engine.robot.targeting.end_effector_point import EndEffectorPoint
from src.engine.robot.targeting.vision_pose_request import VisionPoseRequest
from src.engine.robot.targeting.jog_frame_pose_resolver import JogFramePoseResolver
from src.engine.robot.targeting.point_registry import PointRegistry
from src.engine.robot.targeting.remote_tcp_settings import RemoteTcpSettings
from src.engine.robot.targeting.robot_system_targeting_provider import RobotSystemTargetingProvider
from src.engine.robot.targeting.target_frame import TargetFrame
from src.engine.robot.targeting.target_frame_settings import TargetFrameSettings
from src.engine.robot.targeting.target_point_geometry import command_xyz_from_selected_xyz, command_xy_from_selected_xy, rotate_offset_xy, rotate_offset_xyz, selected_xyz_from_command_xyz, selected_xy_from_command_xy, tcp_delta_xy, tcp_delta_xyz
from src.engine.robot.targeting.targeting_settings import TargetingSettings, TargetingSettingsSerializer
from src.engine.robot.targeting.vision_target_resolver import VisionTargetResolver, TargetTransformResult
from src.shared_contracts.declarations import RemoteTcpDefinition, TargetFrameDefinition
```

Module declarations (expressions are shown without evaluating them):

```python
__all__ = ['EndEffectorPoint', 'VisionPoseRequest', 'JogFramePoseResolver', 'PointRegistry', 'RemoteTcpDefinition', 'RemoteTcpSettings', 'RobotSystemTargetingProvider', 'TargetFrame', 'TargetFrameDefinition', 'TargetFrameSettings', 'rotate_offset_xy', 'rotate_offset_xyz', 'tcp_delta_xy', 'tcp_delta_xyz', 'selected_xy_from_command_xy', 'selected_xyz_from_command_xyz', 'command_xy_from_selected_xy', 'command_xyz_from_selected_xyz', 'TargetingSettings', 'TargetingSettingsSerializer', 'VisionTargetResolver', 'TargetTransformResult']
```

## `end_effector_point.py`

Source: [src/engine/robot/targeting/end_effector_point.py](../../../../src/engine/robot/targeting/end_effector_point.py).

Imports (including optional/function-local imports; not a startup dependency list): `dataclasses`.

### `EndEffectorPoint`

```python
@dataclass(frozen=True)
class EndEffectorPoint:
```

A named physical point on the robot end-effector. ``offset_x`` and ``offset_y`` are the measured offset from the camera center to this point, expressed in the local robot wrist frame (mm). The camera center itself has zero offsets.

Declared fields/defaults:

```python
name: str
offset_x: float = 0.0
offset_y: float = 0.0
```

## `jog_frame_pose_resolver.py`

Source: [src/engine/robot/targeting/jog_frame_pose_resolver.py](../../../../src/engine/robot/targeting/jog_frame_pose_resolver.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `logging`, `math`, `src.engine.robot.targeting.end_effector_point`, `src.engine.robot.targeting.point_registry`, `src.engine.robot.targeting.target_point_geometry`, `typing`.

### `JogFramePoseResolver`

```python
class JogFramePoseResolver:
```

Resolve incremental jog commands so a selected end-effector point stays consistent.

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, registry: PointRegistry, camera_to_tcp_x_offset: float=0.0, camera_to_tcp_y_offset: float=0.0, reference_rz_provider: Optional[Callable[[], float]]=None) -> None
```

```python
def point_for_name(self, frame_name: str) -> Optional[EndEffectorPoint]
```

```python
def available_frames(self) -> list[str]
```

```python
def resolve(self, current_pose: Sequence[float], axis: str, direction: str, step: float, point: EndEffectorPoint) -> list[float] | None
```

### `_tool_frame_delta`

```python
def _tool_frame_delta(position: Sequence[float], axis_idx: int, direction_value: float, step: float) -> tuple[float, float, float]
```

## `point_registry.py`

Source: [src/engine/robot/targeting/point_registry.py](../../../../src/engine/robot/targeting/point_registry.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `src.engine.robot.targeting.end_effector_point`, `typing`.

### `PointRegistry`

```python
class PointRegistry:
```

Store named end-effector points with optional alias resolution.

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, points: Iterable[EndEffectorPoint], aliases: Mapping[str, str] | None=None) -> None
```

```python
def by_name(self, name: str) -> EndEffectorPoint
```

```python
def names(self) -> List[str]
```

## `remote_tcp_settings.py`

Source: [src/engine/robot/targeting/remote_tcp_settings.py](../../../../src/engine/robot/targeting/remote_tcp_settings.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `dataclasses`, `typing`.

### `RemoteTcpSettings`

```python
@dataclass
class RemoteTcpSettings:
```

Declared fields/defaults:

```python
name: str
display_name: str = ''
x_mm: float = 0.0
y_mm: float = 0.0
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
@classmethod
def from_dict(cls, data: dict[str, Any]) -> 'RemoteTcpSettings'
```

```python
def to_dict(self) -> dict[str, Any]
```

## `robot_system_targeting_provider.py`

Source: [src/engine/robot/targeting/robot_system_targeting_provider.py](../../../../src/engine/robot/targeting/robot_system_targeting_provider.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `abc`, `src.engine.robot.targeting.point_registry`, `src.engine.robot.targeting.target_frame`.

### `RobotSystemTargetingProvider`

```python
class RobotSystemTargetingProvider(ABC):
```

Robot-system adapter that supplies generic targeting runtime pieces.

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
@abstractmethod
def build_point_registry(self) -> PointRegistry
```

```python
@abstractmethod
def build_frames(self) -> dict[str, TargetFrame]
```

```python
@abstractmethod
def get_target_options(self) -> list[tuple[str, str]]
```

```python
@abstractmethod
def get_default_target_name(self) -> str
```

## `target_frame.py`

Source: [src/engine/robot/targeting/target_frame.py](../../../../src/engine/robot/targeting/target_frame.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `src.engine.robot.height_measuring.i_height_correction_service`, `src.engine.robot.plane_pose_mapper`, `typing`.

### `TargetFrame`

```python
class TargetFrame:
```

A named coordinate frame bundling its plane mapper and height correction. Instances are registered with ``VisionTargetResolver`` via the ``frames=`` constructor argument. The resolver uses ``mapper`` for XY plane conversion; the application layer uses ``height_correction`` for Z.

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, name: str, work_area_id: str='', mapper: Optional['PlanePoseMapper']=None, height_correction: Optional['IHeightCorrectionService']=None) -> None
```

```python
def get_z_correction(self, x: float, y: float) -> float
```

Return the height-correction contribution in mm at robot position (x, y).

## `target_frame_settings.py`

Source: [src/engine/robot/targeting/target_frame_settings.py](../../../../src/engine/robot/targeting/target_frame_settings.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `dataclasses`, `typing`.

### `TargetFrameSettings`

```python
@dataclass
class TargetFrameSettings:
```

Declared fields/defaults:

```python
name: str
source_navigation_group: str = ''
target_navigation_group: str = ''
use_height_correction: bool = False
work_area_id: str = ''
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
@classmethod
def from_dict(cls, data: dict[str, Any]) -> 'TargetFrameSettings'
```

```python
def to_dict(self) -> dict[str, Any]
```

## `target_point_geometry.py`

Source: [src/engine/robot/targeting/target_point_geometry.py](../../../../src/engine/robot/targeting/target_point_geometry.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `math`, `src.engine.geometry.planar`, `typing`.

### `camera_to_tcp_rotation_residual_xy`

```python
def camera_to_tcp_rotation_residual_xy(residuals: Sequence[Mapping[str, float]] | None, current_rz: float, reference_rz: float=0.0) -> Tuple[float, float]
```

Interpolate a verified command-space XY correction without extrapolation.

### `rotate_offset_xy`

```python
def rotate_offset_xy(offset_x: float, offset_y: float, rz_degrees: float) -> Tuple[float, float]
```

Rotate a local target-point offset into robot XY for the given wrist angle.

### `rotate_offset_xyz`

```python
def rotate_offset_xyz(offset_x: float, offset_y: float, offset_z: float=0.0, *, rx_degrees: float, ry_degrees: float, rz_degrees: float) -> Tuple[float, float, float]
```

Rotate a local target-point offset into robot XYZ for the given tool orientation.

### `_flat_rz_compatible`

```python
def _flat_rz_compatible(rx_degrees: float, ry_degrees: float) -> bool
```

Return True when legacy XY/RZ targeting is the better compatibility model.

### `_orientation3`

```python
def _orientation3(values: Sequence[float] | None, fallback_rz: float=0.0) -> tuple[float, float, float]
```

### `tcp_delta_xyz`

```python
def tcp_delta_xyz(camera_to_tcp_x_offset: float, camera_to_tcp_y_offset: float, *, current_orientation: Sequence[float], reference_orientation: Sequence[float] | None=None) -> Tuple[float, float, float]
```

Return the camera-to-TCP sweep delta between two full tool orientations.

### `selected_xyz_from_command_xyz`

```python
def selected_xyz_from_command_xyz(command_x: float, command_y: float, command_z: float, *, orientation: Sequence[float], point_offset_x: float=0.0, point_offset_y: float=0.0, camera_to_tcp_x_offset: float=0.0, camera_to_tcp_y_offset: float=0.0, reference_orientation: Sequence[float] | None=None) -> Tuple[float, float, float]
```

Convert commanded robot XYZ into selected-point XYZ on the work plane.

### `command_xyz_from_selected_xyz`

```python
def command_xyz_from_selected_xyz(selected_x: float, selected_y: float, selected_z: float, *, orientation: Sequence[float], point_offset_x: float=0.0, point_offset_y: float=0.0, camera_to_tcp_x_offset: float=0.0, camera_to_tcp_y_offset: float=0.0, reference_orientation: Sequence[float] | None=None, camera_to_tcp_rotation_residuals: Sequence[Mapping[str, float]] | None=None) -> Tuple[float, float, float]
```

Convert selected-point XYZ on the work plane into commanded robot XYZ.

### `tcp_delta_xy`

```python
def tcp_delta_xy(camera_to_tcp_x_offset: float, camera_to_tcp_y_offset: float, current_rz: float, reference_rz: float=0.0) -> Tuple[float, float]
```

Return the camera-to-TCP sweep delta between reference and current wrist angles.

### `selected_xy_from_command_xy`

```python
def selected_xy_from_command_xy(command_x: float, command_y: float, rz_degrees: float, point_offset_x: float=0.0, point_offset_y: float=0.0, camera_to_tcp_x_offset: float=0.0, camera_to_tcp_y_offset: float=0.0, reference_rz: float=0.0) -> Tuple[float, float]
```

Convert commanded robot XY into selected-point XY on the work plane.

### `command_xy_from_selected_xy`

```python
def command_xy_from_selected_xy(selected_x: float, selected_y: float, rz_degrees: float, point_offset_x: float=0.0, point_offset_y: float=0.0, camera_to_tcp_x_offset: float=0.0, camera_to_tcp_y_offset: float=0.0, reference_rz: float=0.0) -> Tuple[float, float]
```

Convert selected-point XY on the work plane into commanded robot XY.

## `targeting_settings.py`

Source: [src/engine/robot/targeting/targeting_settings.py](../../../../src/engine/robot/targeting/targeting_settings.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `dataclasses`, `src.engine.repositories.interfaces`, `src.engine.robot.targeting`, `typing`.

### `TargetingSettings`

```python
@dataclass
class TargetingSettings:
```

Declared fields/defaults:

```python
points: list[RemoteTcpSettings] = field(default_factory=list)
frames: list[TargetFrameSettings] = field(default_factory=list)
point_mode: str = 'global'
area_points: dict[str, list[RemoteTcpSettings]] = field(default_factory=dict)
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
@classmethod
def defaults(cls) -> 'TargetingSettings'
```

```python
@classmethod
def from_dict(cls, data: dict[str, Any]) -> 'TargetingSettings'
```

```python
def to_dict(self) -> dict[str, Any]
```

```python
def ensure_defaults(self) -> None
```

```python
def points_for_area(self, area_id: str) -> list[RemoteTcpSettings]
```

### `_dedupe_points`

```python
def _dedupe_points(points: list[RemoteTcpSettings]) -> list[RemoteTcpSettings]
```

### `_dedupe_frames`

```python
def _dedupe_frames(frames: list[TargetFrameSettings]) -> list[TargetFrameSettings]
```

### `TargetingSettingsSerializer`

```python
class TargetingSettingsSerializer(ISettingsSerializer[TargetingSettings]):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
@property
def settings_type(self) -> str
```

```python
def get_default(self) -> TargetingSettings
```

```python
def to_dict(self, settings: TargetingSettings) -> dict[str, Any]
```

```python
def from_dict(self, data: dict[str, Any]) -> TargetingSettings
```

## `vision_pose_request.py`

Source: [src/engine/robot/targeting/vision_pose_request.py](../../../../src/engine/robot/targeting/vision_pose_request.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `dataclasses`.

### `VisionPoseRequest`

```python
@dataclass(frozen=True)
class VisionPoseRequest:
```

Describe the pose you want, using image pixels for XY and robot units for Z/RX/RY/RZ. Simple mental model: - ``x_pixels`` / ``y_pixels`` say which image point should be targeted - ``z_mm`` says the base robot Z height you want - ``rx_degrees`` / ``ry_degrees`` / ``rz_degrees`` say the final tool orientation ``VisionTargetResolver`` takes this request, applies all XY targeting math (homography, plane mapping, TCP delta, end-effector point offset) and then adds any frame height correction on top of ``z_mm`` to produce the final robot pose.

Declared fields/defaults:

```python
x_pixels: float
y_pixels: float
z_mm: float
rz_degrees: float
rx_degrees: float
ry_degrees: float
```

## `vision_target_resolver.py`

Source: [src/engine/robot/targeting/vision_target_resolver.py](../../../../src/engine/robot/targeting/vision_target_resolver.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `dataclasses`, `logging`, `math`, `src.engine.core.i_coordinate_transformer`, `src.engine.robot.plane_pose_mapper`, `src.engine.robot.targeting.end_effector_point`, `src.engine.robot.targeting.point_registry`, `src.engine.robot.targeting.target_frame`, `src.engine.robot.targeting.target_point_geometry`, `src.engine.robot.targeting.vision_pose_request`, `typing`.

Module declarations (expressions are shown without evaluating them):

```python
TRACE_LOG_LEVEL = logging.DEBUG - 5
```

### `TargetTransformResult`

```python
@dataclass(frozen=True)
class TargetTransformResult:
```

Declared fields/defaults:

```python
calibration_xy: Tuple[float, float]
plane_xy: Tuple[float, float]
final_xy: Tuple[float, float]
rx: float = 0.0
ry: float = 0.0
rz: float = 0.0
z: float = 0.0
pickup_plane_reference_delta_xy: Tuple[float, float] = (0.0, 0.0)
target_delta_xy: Tuple[float, float] = (0.0, 0.0)
reference_rz: Optional[float] = None
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def robot_pose(self) -> Tuple[float, float, float, float, float, float]
```

### `VisionTargetResolver`

```python
class VisionTargetResolver:
```

Resolve an image target into a final robot pose for a chosen end-effector point.

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, base_transformer: ICoordinateTransformer, registry: PointRegistry, camera_to_tcp_x_offset: float=0.0, camera_to_tcp_y_offset: float=0.0, camera_to_tcp_rotation_residuals=None, frames: Optional[Dict[str, TargetFrame]]=None, calibration_mode: str='global', profile_transformers: Optional[Dict[str, ICoordinateTransformer]]=None, work_area_profile_ids: Optional[Dict[str, str]]=None, profile_reference_frames: Optional[Dict[str, str]]=None, global_reference_frame: str='calibration', area_registries: Optional[Dict[str, PointRegistry]]=None, area_tcp: Optional[Dict[str, tuple[float, float, list[dict]]]]=None) -> None
```

```python
def resolve(self, target: VisionPoseRequest, point: EndEffectorPoint, *, frame: str='', mapper: Optional[PlanePoseMapper]=None, area_id: str='') -> TargetTransformResult
```

```python
@property
def registry(self) -> PointRegistry
```

```python
def get_frame(self, name: str) -> Optional[TargetFrame]
```

```python
def registry_for_area(self, area_id: str) -> PointRegistry
```

```python
def registry_for_frame(self, frame_name: str) -> PointRegistry
```

### `_map_plane`

```python
def _map_plane(xy: Tuple[float, float], mapper: Optional[PlanePoseMapper]) -> Tuple[float, float]
```

### `_reference_rz`

```python
def _reference_rz(mapper: Optional[PlanePoseMapper]) -> float
```

### `_is_camera_point`

```python
def _is_camera_point(point: EndEffectorPoint) -> bool
```
