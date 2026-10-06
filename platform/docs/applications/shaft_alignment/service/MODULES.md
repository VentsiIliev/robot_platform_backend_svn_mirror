# Module reference: `src/applications/shaft_alignment/service`

[Package guide](README.md) · [Complete source index](../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [i_shaft_alignment_service.py](#i_shaft_alignment_servicepy)
- [paint_vision_shaft_alignment_service.py](#paint_vision_shaft_alignment_servicepy)
- [shaft_alignment_application_service.py](#shaft_alignment_application_servicepy)
- [stub_shaft_alignment_service.py](#stub_shaft_alignment_servicepy)

## `__init__.py`

Source: [src/applications/shaft_alignment/service/__init__.py](../../../../src/applications/shaft_alignment/service/__init__.py).

Imports (including optional/function-local imports; not a startup dependency list): `src.applications.shaft_alignment.service.i_shaft_alignment_service`.

Package-level import/export surface:

```python
from src.applications.shaft_alignment.service.i_shaft_alignment_service import AlignmentSnapshot, AlignmentThresholds, IShaftAlignmentService
```

Module declarations (expressions are shown without evaluating them):

```python
__all__ = ['AlignmentSnapshot', 'AlignmentThresholds', 'IShaftAlignmentService']
```

## `i_shaft_alignment_service.py`

Source: [src/applications/shaft_alignment/service/i_shaft_alignment_service.py](../../../../src/applications/shaft_alignment/service/i_shaft_alignment_service.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `abc`, `dataclasses`, `src.applications.shaft_alignment.settings.shaft_alignment_settings`.

### `AlignmentThresholds`

```python
@dataclass(frozen=True)
class AlignmentThresholds:
```

Declared fields/defaults:

```python
dx_mm: float = 1.0
dy_mm: float = 1.0
drz_deg: float = 1.0
dw_mm: float = 0.5
dh_mm: float = 0.5
```

### `AlignmentSnapshot`

```python
@dataclass(frozen=True)
class AlignmentSnapshot:
```

Declared fields/defaults:

```python
frame: object | None = None
running: bool = False
detected: bool = False
marker_id: int | None = None
marker_corners_normalized: tuple[tuple[float, float], ...] = ()
point_of_interest_normalized: tuple[float, float] | None = None
reference_marker_corners_normalized: tuple[tuple[float, float], ...] = ()
detection_region_normalized: tuple[float, float, float, float] | None = None
configuration_warning: bool = False
tcp_x_mm: float | None = None
tcp_y_mm: float | None = None
orientation_deg: float | None = None
marker_width_mm: float | None = None
marker_height_mm: float | None = None
reference_tcp_x_mm: float | None = None
reference_tcp_y_mm: float | None = None
reference_orientation_deg: float | None = None
reference_marker_width_mm: float | None = None
reference_marker_height_mm: float | None = None
dx_mm: float | None = None
dy_mm: float | None = None
drz_deg: float | None = None
dw_mm: float | None = None
dh_mm: float | None = None
reference_capturing: bool = False
reference_samples: int = 0
reference_samples_required: int = 0
reference_available: bool = False
misaligned: bool = False
exceeded_limits: tuple[str, ...] = ()
message: str = ''
```

### `IShaftAlignmentService`

```python
class IShaftAlignmentService(ABC):
```

Platform boundary for shaft-alignment acquisition and calculations.

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
@abstractmethod
def start(self) -> None
```

```python
@abstractmethod
def stop(self) -> None
```

```python
@abstractmethod
def get_snapshot(self) -> AlignmentSnapshot
```

```python
@abstractmethod
def capture_reference(self, sample_count: int) -> None
```

```python
@abstractmethod
def set_thresholds(self, thresholds: AlignmentThresholds) -> None
```

```python
@abstractmethod
def get_settings(self) -> ShaftAlignmentSettings
```

```python
@abstractmethod
def save_settings(self, settings: ShaftAlignmentSettings) -> None
```

```python
@abstractmethod
def check_alignment(self) -> bool
```

Return True only when the latest complete comparison is aligned.

## `paint_vision_shaft_alignment_service.py`

Source: [src/applications/shaft_alignment/service/paint_vision_shaft_alignment_service.py](../../../../src/applications/shaft_alignment/service/paint_vision_shaft_alignment_service.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `collections`, `dataclasses`, `json`, `logging`, `numpy`, `os`, `pathlib`, `scripts.paint_shaft_alignment.alignment_reference`, `scripts.paint_shaft_alignment.coordinate_mapper`, `scripts.paint_shaft_alignment.detector`, `scripts.paint_shaft_alignment.models`, `scripts.paint_shaft_alignment.orientation_factory`, `scripts.paint_shaft_alignment.paint_vision_factory`, `scripts.paint_shaft_alignment.region`, `scripts.paint_shaft_alignment.stabilizer`, `scripts.paint_shaft_alignment.tracker`, `src.applications.shaft_alignment.service.i_shaft_alignment_service`, `src.applications.shaft_alignment.settings.shaft_alignment_settings`, `statistics`, `threading`, `time`, `typing`.

### `_NormalizedRegionProvider`

```python
class _NormalizedRegionProvider:
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, fallback) -> None
```

```python
def set(self, left: float, top: float, right: float, bottom: float) -> None
```

```python
def clear(self) -> None
```

```python
@property
def normalized(self) -> tuple[float, float, float, float] | None
```

```python
def resolve(self, image_width: int, image_height: int) -> PixelRegion
```

### `PaintVisionShaftAlignmentService`

```python
class PaintVisionShaftAlignmentService(IShaftAlignmentService):
```

Real example backend composed from the same Paint vision stack as the CLI.

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, settings_path: str | os.PathLike | None=None, *, vision_service=None, robot_pose_provider: Callable[[], list[float] | tuple[float, ...] | None] | None=None, work_area_region_provider: Callable[[str], object] | None=None) -> None
```

```python
def start(self) -> None
```

```python
def stop(self) -> None
```

```python
def get_snapshot(self) -> AlignmentSnapshot
```

```python
def capture_reference(self, sample_count: int) -> None
```

```python
def set_thresholds(self, thresholds: AlignmentThresholds) -> None
```

```python
def get_settings(self) -> ShaftAlignmentSettings
```

```python
def save_settings(self, settings: ShaftAlignmentSettings) -> None
```

```python
def check_alignment(self) -> bool
```

## `shaft_alignment_application_service.py`

Source: [src/applications/shaft_alignment/service/shaft_alignment_application_service.py](../../../../src/applications/shaft_alignment/service/shaft_alignment_application_service.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `src.applications.shaft_alignment.service.i_shaft_alignment_service`, `src.applications.shaft_alignment.settings.shaft_alignment_settings`.

### `ShaftAlignmentApplicationService`

```python
class ShaftAlignmentApplicationService(IShaftAlignmentService):
```

Adapt an injected alignment backend without coupling the app to a robot system.

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, backend: IShaftAlignmentService) -> None
```

```python
def start(self) -> None
```

```python
def stop(self) -> None
```

```python
def get_snapshot(self) -> AlignmentSnapshot
```

```python
def capture_reference(self, sample_count: int) -> None
```

```python
def set_thresholds(self, thresholds: AlignmentThresholds) -> None
```

```python
def get_settings(self) -> ShaftAlignmentSettings
```

```python
def save_settings(self, settings: ShaftAlignmentSettings) -> None
```

```python
def check_alignment(self) -> bool
```

## `stub_shaft_alignment_service.py`

Source: [src/applications/shaft_alignment/service/stub_shaft_alignment_service.py](../../../../src/applications/shaft_alignment/service/stub_shaft_alignment_service.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `dataclasses`, `math`, `numpy`, `src.applications.shaft_alignment.service.i_shaft_alignment_service`, `src.applications.shaft_alignment.settings.shaft_alignment_settings`, `time`.

### `StubShaftAlignmentService`

```python
class StubShaftAlignmentService(IShaftAlignmentService):
```

Animated standalone backend for developing the application without hardware.

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self) -> None
```

```python
def start(self) -> None
```

```python
def stop(self) -> None
```

```python
def capture_reference(self, sample_count: int) -> None
```

```python
def set_thresholds(self, thresholds: AlignmentThresholds) -> None
```

```python
def get_settings(self) -> ShaftAlignmentSettings
```

```python
def save_settings(self, settings: ShaftAlignmentSettings) -> None
```

```python
def check_alignment(self) -> bool
```

```python
def get_snapshot(self) -> AlignmentSnapshot
```
