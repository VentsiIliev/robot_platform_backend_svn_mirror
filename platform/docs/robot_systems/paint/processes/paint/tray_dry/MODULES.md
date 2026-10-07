# Module reference: `src/robot_systems/paint/processes/paint/tray_dry`

[Package guide](README.md) · [Complete source index](../../../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [plate_layout.py](#plate_layoutpy)
- [errors.py](../../../../../../src/robot_systems/paint/processes/paint/tray_dry/errors.py) — typed tray failure codes, records and actionable exceptions.

## `__init__.py`

Source: [src/robot_systems/paint/processes/paint/tray_dry/__init__.py](../../../../../../src/robot_systems/paint/processes/paint/tray_dry/__init__.py).

No top-level functions, classes or public value declarations; inspect the source for imports or entry-point statements.

## `plate_layout.py`

Source: [src/robot_systems/paint/processes/paint/tray_dry/plate_layout.py](../../../../../../src/robot_systems/paint/processes/paint/tray_dry/plate_layout.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `dataclasses`, `datetime`, `math`, `threading`, `typing`.

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
def pending(self) -> PlateDropoffReservation | None
```

```python
def snapshot(self, config) -> dict[str, object]
```

Return an immutable dashboard-friendly view of the physical plate.

```python
def clear(self) -> None
```

```python
def remove(self, placement_id: int) -> bool
```

```python
def reserve(self, config, *, width_mm: float, height_mm: float, calibration_pose: list[float], workpiece_rz_at_calibration_deg: float, pose_calculator, outlines_mm=(), paint_passes=()) -> tuple[PlateDropoffReservation | None, str]
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

Readiness additions: `TrayReadiness.UNKNOWN` / `READY`, `PlateLayoutService.readiness`, and `ensure_ready(config=None)`. `clear()` records an explicit empty-tray confirmation and rejects pending reservations. See the package guide for the confirmation workflow.
