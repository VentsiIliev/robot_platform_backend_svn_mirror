# Module reference: `src/robot_systems/paint/processes/paint/tray_dry`

[Package guide](README.md) · [Complete source index](../../../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [errors.py](#errorspy)
- [plate_layout.py](#plate_layoutpy)

## `__init__.py`

Source: [src/robot_systems/paint/processes/paint/tray_dry/__init__.py](../../../../../../src/robot_systems/paint/processes/paint/tray_dry/__init__.py).

No top-level functions, classes or public value declarations; inspect the source for imports or entry-point statements.

## `errors.py`

Source: [src/robot_systems/paint/processes/paint/tray_dry/errors.py](../../../../../../src/robot_systems/paint/processes/paint/tray_dry/errors.py).

Actionable tray failures shared by production and dashboard boundaries.

Imports (including optional/function-local imports; not a startup dependency list): `dataclasses`, `enum`.

### `TrayErrorCode`

```python
class TrayErrorCode(StrEnum):
```

Declared fields/defaults:

```python
CONFIRMATION_REQUIRED = 'tray_confirmation_required'
BUSY = 'tray_busy'
LAYOUT_CHANGED = 'tray_layout_changed'
UNAVAILABLE = 'tray_unavailable'
```

### `TrayFailure`

```python
@dataclass(frozen=True)
class TrayFailure:
```

Declared fields/defaults:

```python
code: TrayErrorCode
message: str
```

### `TrayError`

```python
class TrayError(RuntimeError):
```

Declared fields/defaults:

```python
code: TrayErrorCode
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def as_failure(self) -> TrayFailure
```

### `TrayConfirmationRequiredError`

```python
class TrayConfirmationRequiredError(TrayError):
```

Declared fields/defaults:

```python
code = TrayErrorCode.CONFIRMATION_REQUIRED
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self) -> None
```

### `TrayBusyError`

```python
class TrayBusyError(TrayError):
```

Declared fields/defaults:

```python
code = TrayErrorCode.BUSY
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self) -> None
```

### `TrayLayoutChangedError`

```python
class TrayLayoutChangedError(TrayError):
```

Declared fields/defaults:

```python
code = TrayErrorCode.LAYOUT_CHANGED
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self) -> None
```

### `TrayUnavailableError`

```python
class TrayUnavailableError(TrayError):
```

Declared fields/defaults:

```python
code = TrayErrorCode.UNAVAILABLE
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self) -> None
```

## `plate_layout.py`

Source: [src/robot_systems/paint/processes/paint/tray_dry/plate_layout.py](../../../../../../src/robot_systems/paint/processes/paint/tray_dry/plate_layout.py).

Imports (including optional/function-local imports; not a startup dependency list): `.errors`, `__future__`, `dataclasses`, `datetime`, `enum`, `math`, `src.robot_systems.paint.processes.paint.configuration.models`, `src.robot_systems.paint.processes.paint.results`, `threading`, `typing`.

### `TrayReadiness`

```python
class TrayReadiness(StrEnum):
```

Declared fields/defaults:

```python
UNKNOWN = 'unknown'
READY = 'ready'
```

### `PlateDropoffReservation`

```python
@dataclass(frozen=True)
class PlateDropoffReservation:
```

Declared fields/defaults:

```python
release_pose: list[float]
approach_pose: list[float]
transit_pose: list[float]
has_space_for_same_footprint: bool
width_mm: float
height_mm: float
placement_id: int = 0
left_mm: float = 0.0
bottom_mm: float = 0.0
outlines_mm: tuple[tuple[tuple[float, float], ...], ...] = ()
paint_passes: tuple[dict[str, float | int], ...] = ()
```

### `PlatePlacement`

```python
@dataclass(frozen=True)
class PlatePlacement:
```

Declared fields/defaults:

```python
placement_id: int
left_mm: float
bottom_mm: float
width_mm: float
height_mm: float
outlines_mm: tuple[tuple[tuple[float, float], ...], ...] = ()
painted_at: str = ''
paint_passes: tuple[dict[str, float | int], ...] = ()
```

### `PlateLayoutService`

```python
class PlateLayoutService:
```

Validate a taught plate and reserve deterministic shelf placements.

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, clock: Callable[[], datetime] | None=None) -> None
```

```python
@property
def readiness(self) -> TrayReadiness
```

```python
def ensure_ready(self, config: PaintDropoffConfig | None=None) -> None
```

Reject unknown occupancy or changed geometry without discarding it.

```python
@property
def pending(self) -> PlateDropoffReservation | None
```

```python
def snapshot(self, config) -> dict[str, object]
```

Return an immutable dashboard-friendly view of the physical plate.

```python
def clear(self) -> None
```

Confirm a physically empty tray; callers must obtain operator approval.

```python
def remove(self, placement_id: int) -> bool
```

```python
def reserve(self, config, *, width_mm: float, height_mm: float, calibration_pose: list[float], workpiece_rz_at_calibration_deg: float, pose_calculator, outlines_mm=(), paint_passes=()) -> tuple[PlateDropoffReservation | None, str]
```

```python
def reserve_result(self, config, *, width_mm: float, height_mm: float, calibration_pose: list[float], workpiece_rz_at_calibration_deg: float, pose_calculator, outlines_mm=(), paint_passes=()) -> Ready[PlateDropoffReservation] | PaintOperationResult
```

```python
def commit(self, config) -> None
```

```python
def cancel(self) -> None
```

### `validate_plate_corners`

```python
def validate_plate_corners(raw_corners) -> tuple[list[list[float]], str]
```

### `validate_plate_passage_gate`

```python
def validate_plate_passage_gate(raw_pose) -> tuple[list[float], str]
```

### `_average_edge_length`

```python
def _average_edge_length(a, b, c, d) -> float
```

### `_map_plate_point`

```python
def _map_plate_point(corners, width, height, x, y) -> tuple[float, float, float]
```

### `_layout_signature`

```python
def _layout_signature(config, corners) -> tuple
```

### `_rectangles_overlap`

```python
def _rectangles_overlap(candidate: tuple[float, float, float, float], item: PlatePlacement, *, spacing_x: float=0.0, spacing_y: float=0.0) -> bool
```
