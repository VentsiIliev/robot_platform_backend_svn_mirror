# Module reference: `src/robot_systems/paint/processes/paint/plan/paint_contact_motion`

[Package guide](README.md) · [Complete source index](../../../../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [core.py](#corepy)
- [source_plan.py](#source_planpy)

## `__init__.py`

Source: [src/robot_systems/paint/processes/paint/plan/paint_contact_motion/__init__.py](../../../../../../../src/robot_systems/paint/processes/paint/plan/paint_contact_motion/__init__.py).

Imports (including optional/function-local imports; not a startup dependency list): `.core`, `.source_plan`.

Package-level import/export surface:

```python
from .core import project_paint_contact_motion_continuous, project_paint_motion_geometry_continuous, rebase_contact_motion_path_to_zero_start_rotation, rebase_projected_paint_path_to_zero_start_rz
from .source_plan import build_paint_contact_source_plan, prepare_pivot_source_plan
```

No top-level functions, classes or public value declarations; inspect the source for imports or entry-point statements.

## `core.py`

Source: [src/robot_systems/paint/processes/paint/plan/paint_contact_motion/core.py](../../../../../../../src/robot_systems/paint/processes/paint/plan/paint_contact_motion/core.py).

Paint contact-motion projection helpers. This module converts a prepared workpiece contour into robot poses that keep a chosen contour point touching the fixed paint contact axis. The calculation is done in the active 2D motion plane from ``PaintSimulationConfig``. The shape is rotated and translated so each sampled point contacts the paint axis in turn; it is not orbiting around the axis. * ``xy_z_rz`` uses X/Y as the contact plane and RZ as the active rotation. * ``xz_y_ry`` uses X/Z as the contact plane and RY as the active rotation. Performance notes: * Point rotations are vectorized with NumPy instead of per-point Python loops. * Projection snapshots are disabled by default to avoid O(n^2) memory copying on dense contours. If you need old debug snapshots, set either ``config.save_projection_snapshots = True`` or ``PAINT_PROJECTION_TUNING.save_projection_snapshots = True``.

Imports (including optional/function-local imports; not a startup dependency list): `logging`, `numpy`, `src.engine.geometry.planar`, `src.robot_systems.paint.processes.paint.config`.

Module declarations (expressions are shown without evaluating them):

```python
project_paint_motion_geometry_continuous = project_paint_contact_motion_continuous
rebase_projected_paint_path_to_zero_start_rz = rebase_contact_motion_path_to_zero_start_rotation
```

### `rebase_contact_motion_path_to_zero_start_rotation`

```python
def rebase_contact_motion_path_to_zero_start_rotation(path: list[list[float]], config: PaintSimulationConfig) -> list[list[float]]
```

Shift a paint contact-motion path so its active rotation starts at zero.

### `_rotate_points_about`

```python
def _rotate_points_about(points, angle_deg: float, pivot) -> np.ndarray
```

Vectorized 2D rotation around ``pivot``. Accepts either an ``(N, 2)`` array or one ``(2,)`` point. Returns the same dimensionality as the input.

### `_save_projection_snapshots`

```python
def _save_projection_snapshots(config: PaintSimulationConfig) -> bool
```

Return whether expensive full-shape debug snapshots should be stored.

### `project_paint_contact_motion_continuous`

```python
def project_paint_contact_motion_continuous(path: list[list[float]], paint_axis_pose: list[float], config: PaintSimulationConfig, anchor_xy: tuple[float, float] | None=None, source_rotation_deg: float=0.0, enforce_open_path_side: bool=False) -> tuple[list[list[float]], list[np.ndarray], list[dict[str, float | int]]]
```

Project a dense contour into paint-axis contact motion. The input path is expected to be the prepared paint source contour. The algorithm mirrors the legacy KAREL RTCP loop: the current contour point is the paint-axis contact, the remaining workpiece is rotated around that point, then translated along the contact axis so the next contour point becomes the new contact. The geometry rotation is kept separate from the robot command rotation sign.

### `_extend_closed_path_by_overlap`

```python
def _extend_closed_path_by_overlap(points: np.ndarray, overlap_mm: float) -> np.ndarray
```

Append an exact arc-length prefix after a closed contour's seam.

### `_compose_pose`

```python
def _compose_pose(*, reference_pose: list[float], planar_i: int, planar_j: int, planar_a: float, planar_b: float, orthogonal_index: int, orthogonal_value: float, rotation_index: int, rotation_value: float, rx: float, ry: float, rz: float) -> list[float]
```

Build a full 6D pose from a projected 2D point and the active motion plane.

### `_segment_heading_deg`

```python
def _segment_heading_deg(point_a: np.ndarray, point_b: np.ndarray) -> float
```

Return the heading of the segment from ``point_a`` to ``point_b``. The heading is measured in the XY plane relative to the positive X-axis, with positive angles rotating counter-clockwise. The result is in the range [-180°, 180°]. Examples: (0, 0) → (1, 0) -> 0° (0, 0) → (0, 1) -> 90° (0, 0) → (-1, 0) -> 180° (0, 0) → (0, -1) -> -90°

### `_angle_error_deg`

```python
def _angle_error_deg(a: float, b: float) -> float
```

Return the smallest angular error between two angles in degrees. The comparison accounts for axis-equivalent rotations (e.g. 0° ≡ 360°, -180° ≡ 180°) by first unwrapping ``b`` into the revolution closest to ``a`` before computing the absolute difference. Examples: _angle_error_deg(10, 370) -> 0.0 _angle_error_deg(179, -181) -> 0.0 _angle_error_deg(10, 20) -> 10.0

### `_canonicalize_closed_source_path`

```python
def _canonicalize_closed_source_path(points: np.ndarray, *, pivot_xy: tuple[float, float], start_reference_xy: tuple[float, float] | None=None, translation_heading: float, side_reference_heading: float, contact_segment_heading: float, side_sign: float) -> np.ndarray
```

Give closed contours a pivot-aware start point and traversal direction.

### `_orient_open_source_path_for_contact_side`

```python
def _orient_open_source_path_for_contact_side(points: np.ndarray, *, pivot_xy: tuple[float, float], side_reference_heading: float, contact_segment_heading: float, side_sign: float) -> tuple[np.ndarray, bool]
```

Choose the open-path direction that places the workpiece on the configured side.

## `source_plan.py`

Source: [src/robot_systems/paint/processes/paint/plan/paint_contact_motion/source_plan.py](../../../../../../../src/robot_systems/paint/processes/paint/plan/paint_contact_motion/source_plan.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `logging`, `numpy`, `src.engine.robot.path_preparation`, `src.robot_systems.paint.processes.paint.config`.

Module declarations (expressions are shown without evaluating them):

```python
prepare_pivot_source_plan = build_paint_contact_source_plan
```

### `build_paint_contact_source_plan`

```python
def build_paint_contact_source_plan(plan: WorkpieceExecutionPlan, contact_config: PaintSimulationConfig) -> WorkpieceExecutionPlan
```

Attach the final paint contact source contour to each execution job. Path preparation owns pixel-to-mm conversion, contour smoothing, and final sampling. Paint contact planning consumes that final execution path directly as contact source geometry; it does not resample or simplify the contour. Compatibility keys using the old pivot terminology are kept until all downstream readers are migrated.

### `_planar_spacing_stats`

```python
def _planar_spacing_stats(path: list[list[float]], planar_indices: tuple[int, int]) -> tuple[float, float, float]
```

Return min/mean/max spacing in the active source plane.

### `_trim_and_profile_selected_interval`

```python
def _trim_and_profile_selected_interval(source_path: list[list[float]], selection_paths: list[list[list[float]]], *, cut_moved_outside_selection: bool=False) -> tuple[list[list[float]], list[float]]
```

Trim after the last selected span and add clearance through internal gaps.

### `_points_near_polyline`

```python
def _points_near_polyline(points: np.ndarray, polyline: np.ndarray, *, tolerance_mm: float) -> np.ndarray
```

### `_cumulative_distances`

```python
def _cumulative_distances(points: np.ndarray) -> np.ndarray
```
