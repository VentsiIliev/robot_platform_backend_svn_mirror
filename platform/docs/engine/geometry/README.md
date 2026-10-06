# `src/engine/geometry/` — Planar Geometry Helpers

Dependency-free 2-D math shared by the robot stack. Stdlib only (`math`) — no
NumPy, no OpenCV, no Qt.

---

## Files

| File | Contents |
|------|----------|
| `planar.py` | Angle and XY helpers (58 lines) |

---

## `planar.py`

### `rotate_xy(x, y, angle_degrees) -> (x', y')`

Rotation about the origin. `angle_degrees` is converted with `math.radians`.

### `rotate_xy_about(point_xy, angle_degrees, pivot_xy) -> (x', y')`

Rotate `point_xy` around `pivot_xy`: translate to the pivot, `rotate_xy`, then
translate back. Accepts any 2-sequence; values are coerced with `float()`.

### `unwrap_degrees(previous, current) -> float`

Shift `current` by whole turns until it lies within ±180° of `previous`:

```python
while value - prev > 180.0:  value -= 360.0
while value - prev < -180.0: value += 360.0
```

Used to make consecutive headings comparable without wrap-around jumps.

### `normalize_degrees(angle) -> float`

Map any angle into `(-180, 180]`. Note the asymmetry: `> 180` subtracts, while
`<= -180` adds — so `-180` becomes `180`.

### `nearest_axis_equivalent_degrees(reference, axis_angle) -> float`

> Return the 180-degree-equivalent axis angle nearest to `reference`.

Considers the candidates `axis_angle`, `axis_angle + 180`, `axis_angle - 180`,
unwraps each against `reference`, and returns the one with the smallest absolute
distance to `reference`.

An *axis* is bidirectional, so a 180° flip is the same physical orientation.
This is the helper that resolves that ambiguity in favour of whichever
representation is closest to a known reference frame.

### `axis_equivalent_shift_degrees(reference, current) -> float`

> Return the constant 180-degree shift that puts `current` nearest `reference`.

Convenience wrapper: `nearest_axis_equivalent_degrees(reference, current) -
current`. Returns `0.0`, `+180.0`, or `-180.0` (after unwrap).

---

## Consumers

| Consumer | Uses |
|----------|------|
| `src/engine/robot/path_preparation/geometry.py` | `nearest_axis_equivalent_degrees`, `normalize_degrees`, `unwrap_degrees` |
| `src/engine/robot/path_preparation/default_workpiece_path_preparation_service.py` | `nearest_axis_equivalent_degrees`, `unwrap_degrees` (pickup-RZ normalization) |
| `src/engine/robot/targeting/target_point_geometry.py` | planar helpers |
| `src/robot_systems/paint/processes/paint/plan/*` | heading/pose math |
| `src/robot_systems/paint/processes/paint/execute/*` | rotation and unwrap |
| `src/robot_systems/paint/processes/paint/motion/pose_comparison.py` | angle comparison |

---

## Design Notes

- **Pure functions, no classes, no state.** Everything is importable and
  unit-testable without any fixture.
- **180° is a special case throughout.** `nearest_axis_equivalent_degrees` and
  `axis_equivalent_shift_degrees` exist specifically because tool/workpiece axes
  are undirected — a plain `normalize_degrees` is not enough for pickup
  orientation selection.
- **Degrees in, degrees out.** Conversion to radians happens only inside
  `rotate_xy`.
