# Module reference: `scripts/paint_shaft_alignment`

[Package guide](README.md) · [Complete source index](../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [__main__.py](#__main__py)
- [alignment_reference.py](#alignment_referencepy)
- [cli.py](#clipy)
- [config.py](#configpy)
- [coordinate_mapper.py](#coordinate_mapperpy)
- [detector.py](#detectorpy)
- [models.py](#modelspy)
- [orientation.py](#orientationpy)
- [orientation_factory.py](#orientation_factorypy)
- [paint_vision_factory.py](#paint_vision_factorypy)
- [region.py](#regionpy)
- [stabilizer.py](#stabilizerpy)
- [tracker.py](#trackerpy)

## `__init__.py`

Source: [scripts/paint_shaft_alignment/__init__.py](../../../scripts/paint_shaft_alignment/__init__.py).

Standalone paint-shaft alignment experiments. The package intentionally depends on platform interfaces while keeping all shaft-specific semantics outside the paint robot system until they are stable.

Imports (including optional/function-local imports; not a startup dependency list): `.detector`, `.models`.

Package-level import/export surface:

```python
from .detector import ShaftMarkerDetector
from .models import DetectedMarker, MarkerDetection, MarkerDetectionStatus, ShaftMarkerConfig
```

Module declarations (expressions are shown without evaluating them):

```python
__all__ = ['DetectedMarker', 'MarkerDetection', 'MarkerDetectionStatus', 'ShaftMarkerConfig', 'ShaftMarkerDetector']
```

## `__main__.py`

Source: [scripts/paint_shaft_alignment/__main__.py](../../../scripts/paint_shaft_alignment/__main__.py).

Imports (including optional/function-local imports; not a startup dependency list): `.cli`, `__future__`, `os`, `scripts.paint_shaft_alignment.cli`, `sys`.

No top-level functions, classes or public value declarations; inspect the source for imports or entry-point statements.

## `alignment_reference.py`

Source: [scripts/paint_shaft_alignment/alignment_reference.py](../../../scripts/paint_shaft_alignment/alignment_reference.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `dataclasses`, `math`, `statistics`.

### `AlignmentReference`

```python
@dataclass(frozen=True)
class AlignmentReference:
```

Declared fields/defaults:

```python
x_mm: float
y_mm: float
orientation_deg: float
marker_width_mm: float
marker_height_mm: float
```

### `AlignmentMisalignment`

```python
@dataclass(frozen=True)
class AlignmentMisalignment:
```

Declared fields/defaults:

```python
available: bool
dx_mm: float | None = None
dy_mm: float | None = None
orientation_difference_deg: float | None = None
marker_width_difference_mm: float | None = None
marker_height_difference_mm: float | None = None
message: str = ''
```

### `MisalignmentThresholds`

```python
@dataclass(frozen=True)
class MisalignmentThresholds:
```

Declared fields/defaults:

```python
dx_mm: float
dy_mm: float
orientation_deg: float
marker_width_mm: float
marker_height_mm: float
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def exceeded_by(self, value: AlignmentMisalignment) -> tuple[str, ...]
```

### `AlignmentReferenceCapture`

```python
class AlignmentReferenceCapture:
```

Collect a robust reference and compare subsequent marker observations.

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, required_samples: int) -> None
```

```python
@property
def required_samples(self) -> int
```

```python
@property
def sample_count(self) -> int
```

```python
@property
def capturing(self) -> bool
```

```python
@property
def reference(self) -> AlignmentReference | None
```

```python
def start(self, required_samples: int | None=None) -> None
```

```python
def restore(self, reference: AlignmentReference) -> None
```

```python
def record(self, x_mm: float, y_mm: float, orientation_deg: float, marker_width_mm: float, marker_height_mm: float) -> bool
```

```python
def compare(self, x_mm: float, y_mm: float, orientation_deg: float, marker_width_mm: float, marker_height_mm: float) -> AlignmentMisalignment
```

## `cli.py`

Source: [scripts/paint_shaft_alignment/cli.py](../../../scripts/paint_shaft_alignment/cli.py).

Imports (including optional/function-local imports; not a startup dependency list): `.alignment_reference`, `.config`, `.coordinate_mapper`, `.detector`, `.models`, `.orientation_factory`, `.paint_vision_factory`, `.region`, `.stabilizer`, `.tracker`, `__future__`, `cv2`, `logging`, `numpy`, `time`.

### `_MisalignmentThresholdControls`

```python
class _MisalignmentThresholdControls:
```

OpenCV trackbars backed by thresholds with 0.1-unit resolution.

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, window_title: str, initial: MisalignmentThresholds) -> None
```

```python
def thresholds(self) -> MisalignmentThresholds
```

### `_ReferenceCaptureControls`

```python
class _ReferenceCaptureControls:
```

Control the sample count used by the next baseline capture.

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, window_title: str, capture: AlignmentReferenceCapture, initial_samples: int) -> None
```

```python
def start_capture(self) -> None
```

```python
def selected_samples(self) -> int
```

### `_draw_controls_panel`

```python
def _draw_controls_panel(thresholds: MisalignmentThresholds, selected_samples: int, active_capture_samples: int | None)
```

### `_DetectionRegionMouseHandler`

```python
class _DetectionRegionMouseHandler:
```

Translates OpenCV mouse gestures into base-region selections.

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, provider: SelectableDetectionRegionProvider, on_changed) -> None
```

```python
def set_button(self, region: PixelRegion, callback) -> None
```

### `_draw_detection`

```python
def _draw_detection(frame, result: MarkerDetection, *, draw_all_markers: bool, draw_detection_region: bool, debug_region: PixelRegion | None, tracker_state: str, robot_position: MarkerRobotPosition, draw_robot_coordinates: bool, stable_estimate: StableMarkerEstimate, planar_size: MarkerPlanarSize, reference_capture: AlignmentReferenceCapture, misalignment: AlignmentMisalignment, reference_button_region: PixelRegion, thresholds: MisalignmentThresholds, exceeded_limits: tuple[str, ...], selection_preview: PixelRegion | None=None)
```

### `_marker_orientation_label`

```python
def _marker_orientation_label(marker) -> str
```

### `_draw_region_prompt`

```python
def _draw_region_prompt(frame, preview: PixelRegion | None)
```

### `main`

```python
def main(config: StandaloneShaftDetectionConfig=CONFIG) -> int
```

## `config.py`

Source: [scripts/paint_shaft_alignment/config.py](../../../scripts/paint_shaft_alignment/config.py).

Imports (including optional/function-local imports; not a startup dependency list): `dataclasses`.

Module declarations (expressions are shown without evaluating them):

```python
CONFIG = StandaloneShaftDetectionConfig()
```

### `StandaloneShaftDetectionConfig`

```python
@dataclass(frozen=True)
class StandaloneShaftDetectionConfig:
```

Editable settings for the standalone development runner.

Declared fields/defaults:

```python
marker_id: int = 0
minimum_area_px2: float = 0.0
active_work_area: str | None = 'paint'
raw_mode: bool = False
headless: bool = False
debug_draw_detected_markers: bool = True
debug_draw_detection_region: bool = True
debug_draw_robot_coordinates: bool = True
draw_initial_detection_region: bool = True
orientation_strategy: str = 'compare'
orientation_primary_strategy: str = 'corner_edge'
marker_size_mm: float = 11.0
calibration_pose: tuple[float, float, float, float, float, float] = (-29.075, 217.269, 200.076, -179.99, 0.0, 0.0)
capture_pose: tuple[float, float, float, float, float, float] = (257.75, 215.7, 400.1, -179.2, 0.0, 0.0)
reference_capture_samples: int = 30
misalignment_dx_threshold_mm: float = 1.0
misalignment_dy_threshold_mm: float = 1.0
misalignment_drz_threshold_deg: float = 1.0
misalignment_dw_threshold_mm: float = 0.5
misalignment_dh_threshold_mm: float = 0.5
base_region_width_px: int = 100
base_region_height_px: int = 700
tracking_region_padding_px: int = 50
tracking_region_minimum_width_px: int = 160
tracking_region_minimum_height_px: int = 160
tracking_recovery_expansion_px: int = 50
marker_misses_before_region_fallback: int = 10
detections_before_tracking: int = 1
acquisition_misses_before_reset: int = 3
tracking_position_filter_alpha: float = 0.5
tracking_prediction_gain: float = 0.5
tracking_maximum_center_jump_px: float = 100.0
tracking_maximum_area_ratio_change: float = 3.0
stability_required_samples: int = 5
stability_maximum_center_spread_px: float = 5.0
stability_maximum_orientation_spread_deg: float = 3.0
stability_misses_before_reset: int = 3
detection_interval_s: float = 0.1
run_duration_s: float = 0.0
verbose_logging: bool = False
window_title: str = 'Paint Shaft Marker Detection'
```

## `coordinate_mapper.py`

Source: [scripts/paint_shaft_alignment/coordinate_mapper.py](../../../scripts/paint_shaft_alignment/coordinate_mapper.py).

Imports (including optional/function-local imports; not a startup dependency list): `.models`, `__future__`, `dataclasses`, `math`, `typing`.

### `PixelToRobotTransformer`

```python
class PixelToRobotTransformer(Protocol):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def is_available(self) -> bool
```

```python
def transform(self, x: float, y: float) -> tuple[float, float]
```

### `CameraToTcpTransformer`

```python
class CameraToTcpTransformer(Protocol):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def is_available(self) -> bool
```

```python
def transform_to_tcp(self, x: float, y: float) -> tuple[float, float]
```

### `TcpCoordinateTransformer`

```python
class TcpCoordinateTransformer:
```

Expose camera-to-TCP conversion through the mapper's transform contract.

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, transformer: CameraToTcpTransformer) -> None
```

```python
def is_available(self) -> bool
```

```python
def transform(self, x: float, y: float) -> tuple[float, float]
```

### `CapturePoseCompensatedTransformer`

```python
class CapturePoseCompensatedTransformer:
```

Shift calibrated coordinates by the capture-pose translation.

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, transformer: PixelToRobotTransformer, calibration_pose: tuple[float, float, float, float, float, float], capture_pose: tuple[float, float, float, float, float, float]) -> None
```

```python
def set_capture_pose(self, capture_pose) -> None
```

```python
def clear_capture_pose(self) -> None
```

```python
@property
def translation_xy_mm(self) -> tuple[float, float]
```

```python
def is_available(self) -> bool
```

```python
def transform(self, x: float, y: float) -> tuple[float, float]
```

### `MarkerRobotPosition`

```python
@dataclass(frozen=True)
class MarkerRobotPosition:
```

Declared fields/defaults:

```python
available: bool
x_mm: float | None = None
y_mm: float | None = None
message: str = ''
```

### `MarkerPlanarSize`

```python
@dataclass(frozen=True)
class MarkerPlanarSize:
```

Declared fields/defaults:

```python
available: bool
real_size_mm: float
width_mm: float | None = None
height_mm: float | None = None
width_difference_mm: float | None = None
height_difference_mm: float | None = None
message: str = ''
```

### `MarkerCenterRobotMapper`

```python
class MarkerCenterRobotMapper:
```

Map a marker center through an injected robot-coordinate transform.

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, transformer: PixelToRobotTransformer) -> None
```

```python
def map(self, detection: MarkerDetection) -> MarkerRobotPosition
```

```python
def map_center(self, center_px: tuple[float, float]) -> MarkerRobotPosition
```

```python
def measure_planar_size(self, corners_px: tuple[tuple[float, float], ...], real_size_mm: float) -> MarkerPlanarSize
```

## `detector.py`

Source: [scripts/paint_shaft_alignment/detector.py](../../../scripts/paint_shaft_alignment/detector.py).

Imports (including optional/function-local imports; not a startup dependency list): `.models`, `.orientation`, `.region`, `__future__`, `logging`, `numpy`, `time`, `typing`.

### `VisionMarkerSource`

```python
class VisionMarkerSource(Protocol):
```

Small seam implemented by the platform's IVisionService.

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def get_latest_frame(self) -> np.ndarray
```

```python
def detect_aruco_markers(self, image: np.ndarray) -> tuple
```

### `ShaftMarkerDetector`

```python
class ShaftMarkerDetector:
```

Detect one configured shaft marker in a frame. This milestone intentionally reports image-space geometry only. Robot-frame pose estimation belongs in a later component once timestamped frame/robot pose synchronization is available.

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, vision: VisionMarkerSource, config: ShaftMarkerConfig, *, orientation_strategy: MarkerOrientationStrategy | None=None, clock: Callable[[], float]=time.monotonic, logger: logging.Logger | None=None) -> None
```

```python
def detect(self, frame: np.ndarray | None=None, detection_region: PixelRegion | None=None) -> MarkerDetection
```

## `models.py`

Source: [scripts/paint_shaft_alignment/models.py](../../../scripts/paint_shaft_alignment/models.py).

Imports (including optional/function-local imports; not a startup dependency list): `.region`, `__future__`, `dataclasses`, `enum`, `typing`.

Module declarations (expressions are shown without evaluating them):

```python
PixelPoint = Tuple[float, float]
```

### `MarkerDetectionStatus`

```python
class MarkerDetectionStatus(str, Enum):
```

Declared fields/defaults:

```python
DETECTED = 'detected'
FRAME_UNAVAILABLE = 'frame_unavailable'
DETECTION_FAILED = 'detection_failed'
MARKER_NOT_FOUND = 'marker_not_found'
DUPLICATE_MARKER_ID = 'duplicate_marker_id'
```

### `ShaftMarkerConfig`

```python
@dataclass(frozen=True)
class ShaftMarkerConfig:
```

Declared fields/defaults:

```python
marker_id: int
minimum_area_px2: float = 0.0
```

### `DetectedMarker`

```python
@dataclass(frozen=True)
class DetectedMarker:
```

Declared fields/defaults:

```python
marker_id: int
corners_px: Tuple[PixelPoint, ...]
center_px: PixelPoint
area_px2: float
orientation_deg: float
orientation_samples: Tuple[Tuple[str, float], ...] = ()
orientation_diagnostics: Tuple[Tuple[str, float], ...] = ()
```

### `MarkerDetection`

```python
@dataclass(frozen=True)
class MarkerDetection:
```

Declared fields/defaults:

```python
status: MarkerDetectionStatus
detected_at_monotonic_s: float
marker_id: int
detected_ids: Tuple[int, ...] = ()
detected_markers: Tuple[DetectedMarker, ...] = ()
detection_region: PixelRegion | None = None
corners_px: Tuple[PixelPoint, ...] = ()
center_px: PixelPoint | None = None
area_px2: float | None = None
orientation_deg: float | None = None
message: str = ''
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
@property
def detected(self) -> bool
```

## `orientation.py`

Source: [scripts/paint_shaft_alignment/orientation.py](../../../scripts/paint_shaft_alignment/orientation.py).

Imports (including optional/function-local imports; not a startup dependency list): `.models`, `__future__`, `cv2`, `dataclasses`, `math`, `numpy`, `typing`.

### `MarkerOrientationStrategy`

```python
class MarkerOrientationStrategy(Protocol):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def estimate(self, corners_px: Sequence[PixelPoint]) -> 'MarkerOrientationEstimate'
```

### `MarkerOrientationEstimate`

```python
@dataclass(frozen=True)
class MarkerOrientationEstimate:
```

Declared fields/defaults:

```python
primary_deg: float
samples: tuple[tuple[str, float], ...]
diagnostics: tuple[tuple[str, float], ...] = ()
```

### `CornerEdgeOrientationStrategy`

```python
class CornerEdgeOrientationStrategy:
```

Image-plane orientation averaged from all four canonical marker edges.

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def orientation_deg(self, corners_px: Sequence[PixelPoint]) -> float
```

```python
def estimate(self, corners_px: Sequence[PixelPoint]) -> MarkerOrientationEstimate
```

### `SolvePnPOrientationStrategy`

```python
class SolvePnPOrientationStrategy:
```

Camera-frame marker yaw from a square planar PnP solution.

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, *, marker_size_mm: float, camera_matrix: np.ndarray, distortion_coefficients: np.ndarray) -> None
```

```python
def orientation_deg(self, corners_px: Sequence[PixelPoint]) -> float
```

```python
def estimate(self, corners_px: Sequence[PixelPoint]) -> MarkerOrientationEstimate
```

### `ComparingOrientationStrategy`

```python
class ComparingOrientationStrategy:
```

Evaluate multiple strategies from the same corners and select one primary.

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, strategies: Sequence[MarkerOrientationStrategy], *, primary_name: str) -> None
```

```python
def estimate(self, corners_px: Sequence[PixelPoint]) -> MarkerOrientationEstimate
```

### `_normalize_angle_deg`

```python
def _normalize_angle_deg(angle: float) -> float
```

### `_rotation_matrix_to_euler_xyz_deg`

```python
def _rotation_matrix_to_euler_xyz_deg(rotation: np.ndarray) -> tuple[float, float, float]
```

## `orientation_factory.py`

Source: [scripts/paint_shaft_alignment/orientation_factory.py](../../../scripts/paint_shaft_alignment/orientation_factory.py).

Imports (including optional/function-local imports; not a startup dependency list): `.config`, `.orientation`, `__future__`, `cv2`, `numpy`, `os`.

### `build_orientation_strategy`

```python
def build_orientation_strategy(vision_service, config: StandaloneShaftDetectionConfig)
```

## `paint_vision_factory.py`

Source: [scripts/paint_shaft_alignment/paint_vision_factory.py](../../../scripts/paint_shaft_alignment/paint_vision_factory.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `os`, `src.engine.common_settings_ids`, `src.engine.repositories.settings_service_factory`, `src.engine.vision.homography_residual_transformer`, `src.engine.vision.implementation.VisionSystem.VisionSystem`, `src.engine.vision.implementation.VisionSystem.core.service.internal_service`, `src.engine.vision.vision_service`, `src.engine.work_areas.work_area_service`, `src.robot_systems.paint.paint_robot_system`.

### `build_paint_vision_service`

```python
def build_paint_vision_service(active_area: str | None=None) -> VisionService
```

Build vision exactly from the paint system's real specs and storage paths.

### `build_paint_base_transformer`

```python
def build_paint_base_transformer(vision_service: VisionService) -> HomographyResidualTransformer
```

Build the same base pixel-to-robot transformer used by paint targeting.

### `build_paint_tcp_transformer`

```python
def build_paint_tcp_transformer(vision_service: VisionService) -> HomographyResidualTransformer
```

Build pixel-to-TCP conversion using the paint robot's calibrated offsets.

## `region.py`

Source: [scripts/paint_shaft_alignment/region.py](../../../scripts/paint_shaft_alignment/region.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `dataclasses`, `typing`.

Module declarations (expressions are shown without evaluating them):

```python
PixelPoint = Tuple[float, float]
```

### `PixelRegion`

```python
@dataclass(frozen=True)
class PixelRegion:
```

Declared fields/defaults:

```python
x: int
y: int
width: int
height: int
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
@property
def right(self) -> int
```

```python
@property
def bottom(self) -> int
```

### `DetectionRegionProvider`

```python
class DetectionRegionProvider(Protocol):
```

Resolves the image region searched for the shaft marker.

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def resolve(self, image_width: int, image_height: int) -> PixelRegion
```

### `CenteredDetectionRegionProvider`

```python
@dataclass(frozen=True)
class CenteredDetectionRegionProvider:
```

Temporary provider until a paint-shaft work-area ROI is available.

Declared fields/defaults:

```python
width: int
height: int
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def resolve(self, image_width: int, image_height: int) -> PixelRegion
```

### `SelectableDetectionRegionProvider`

```python
class SelectableDetectionRegionProvider:
```

Uses a drawn ROI when present and otherwise delegates to a default provider.

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, default_provider: DetectionRegionProvider) -> None
```

```python
@property
def selected_region(self) -> PixelRegion | None
```

```python
def select(self, start: tuple[int, int], end: tuple[int, int]) -> bool
```

```python
def clear(self) -> None
```

```python
def resolve(self, image_width: int, image_height: int) -> PixelRegion
```

## `stabilizer.py`

Source: [scripts/paint_shaft_alignment/stabilizer.py](../../../scripts/paint_shaft_alignment/stabilizer.py).

Imports (including optional/function-local imports; not a startup dependency list): `.models`, `__future__`, `collections`, `dataclasses`, `math`, `statistics`.

### `StableMarkerEstimate`

```python
@dataclass(frozen=True)
class StableMarkerEstimate:
```

Declared fields/defaults:

```python
stable: bool
sample_count: int
required_samples: int
center_px: PixelPoint | None = None
orientation_deg: float | None = None
center_spread_px: float | None = None
orientation_spread_deg: float | None = None
message: str = ''
```

### `MarkerSampleStabilizer`

```python
class MarkerSampleStabilizer:
```

Produce a robust marker estimate from a rolling sample window.

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, *, required_samples: int, maximum_center_spread_px: float, maximum_orientation_spread_deg: float, misses_before_reset: int) -> None
```

```python
def record_detection(self, marker: DetectedMarker) -> StableMarkerEstimate
```

```python
def record_miss(self) -> StableMarkerEstimate
```

```python
def reset(self) -> None
```

```python
def estimate(self) -> StableMarkerEstimate
```

## `tracker.py`

Source: [scripts/paint_shaft_alignment/tracker.py](../../../scripts/paint_shaft_alignment/tracker.py).

Imports (including optional/function-local imports; not a startup dependency list): `.models`, `.region`, `__future__`, `enum`, `math`.

### `TrackingState`

```python
class TrackingState(str, Enum):
```

Declared fields/defaults:

```python
SEARCHING = 'searching'
TRACKING = 'tracking'
RECOVERING = 'recovering'
```

### `MarkerRegionTracker`

```python
class MarkerRegionTracker:
```

Stateful ROI tracker; independent from ArUco detection.

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, base_region_provider: DetectionRegionProvider, *, padding_px: int, minimum_width_px: int, minimum_height_px: int, recovery_expansion_px: int, misses_before_fallback: int, detections_before_tracking: int, acquisition_misses_before_reset: int, position_filter_alpha: float, prediction_gain: float, maximum_center_jump_px: float, maximum_area_ratio_change: float) -> None
```

```python
@property
def state(self) -> TrackingState
```

```python
@property
def consecutive_misses(self) -> int
```

```python
def region_for_frame(self, image_width: int, image_height: int) -> PixelRegion
```

```python
def record_detection(self, marker: DetectedMarker) -> bool
```

```python
def record_miss(self) -> None
```

```python
def reset(self) -> None
```
