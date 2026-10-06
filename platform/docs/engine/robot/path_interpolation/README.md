# `src/engine/robot/path_interpolation/` — Path Interpolation

Utility code for densifying, smoothing and reshaping robot / vision paths. Used when a coarse list of waypoints (or a raw vision contour) needs to be converted into a finer trajectory for smoother robot motion.

> `__init__.py`: *"Active interpolation package. Only the new interpolation pipeline is used by production execution code. Legacy modules live under `path_interpolation.deprecated`."*

---

## Structure

```
path_interpolation/
├── __init__.py                    ← package docstring only (no exports)
├── new_interpolation/             ← ACTIVE — used by production execution code
│   ├── interpolation_pipeline.py  ← ContourPathPipeline + contour/curve helpers
│   ├── debug_plotting.py          ← matplotlib/OpenCV debug + shape-comparison reports
│   └── simple_interpolation_pyqt6.py ← standalone PyQt6 tuning/dev tool (not imported by runtime)
└── deprecated/                    ← LEGACY — kept for reference, not imported by src/ or tests/
    ├── linear_interpolation.py        ← interpolate_path_linear()
    ├── spline_interpolation.py        ← interpolate_path_spline_with_lambda()
    ├── combined_interpolation.py      ← interpolate_path_two_stage() + corner blending
    ├── points_interpolation_example.py
    ├── simple_interpolation_viewer.py
    ├── test_trajectory_interpolation.py
    └── ttest_trajectory_interpolation.py
```

---

## `new_interpolation/interpolation_pipeline.py` — Active Pipeline

Clean contour→path pipeline for vision contours.

### Config dataclasses

```python
@dataclass(slots=True)
class PreprocessConfig:
    close_tol: float = 5.0               # append first point if contour is nearly closed
    min_spacing: float = 1.0             # drop points closer than this
    max_segment_length: float = 0.0      # 0 = off; else densify so no segment exceeds it
    use_approx_poly_dp: bool = False
    approx_epsilon_factor: float = 0.01
    noise_method: NoiseMethod = "none"   # "none" | "moving_average" | "savgol"
    noise_strength: float = 5.0

@dataclass(slots=True)
class InterpolationConfig:
    method: CurveMethod = "pchip"        # "linear" | "pchip"
    output_spacing: float = 10.0         # final arc-length spacing
    dense_sampling_factor: float = 0.25

@dataclass(slots=True)
class PipelineResult:
    raw: np.ndarray       # after duplicate removal / close
    prepared: np.ndarray  # after approx / densify / simplify / smooth
    curve: np.ndarray     # fitted dense curve
    sampled: np.ndarray   # final uniform arc-length resample
```

### `ContourPathPipeline`

```python
ContourPathPipeline(preprocess: PreprocessConfig | None = None,
                    interpolation: InterpolationConfig | None = None)

prepare(points) -> (raw, prepared)   # normalize + preprocess only — no curve fit
run(points)     -> PipelineResult    # prepare → fit_curve → arc_length_resample
```

### Module helpers

| Function | Docstring |
|---|---|
| `contour_to_xy(contour)` | Convert a contour from OpenCV-style or Nx2 format to float Nx2 |
| `normalize_contours(contours)` | Normalize a list of contours into float Nx2 arrays |
| `contour_area_xy(contour)` | Compute absolute contour area in XY space |
| `select_contour(contours, mode, index)` | Select one contour (`largest_area` / `index`) |
| `remove_duplicate_consecutive` | Drop consecutive duplicates or near-duplicates |
| `close_if_needed` | Append the first point if the contour is almost closed |
| `simplify_min_spacing` | Keep points separated by at least `min_spacing` |
| `densify_max_spacing` | Insert linear support points so no segment exceeds `max_segment_length` |
| `approx_polyline` | Simplify using OpenCV `approxPolyDP` with perimeter-scaled epsilon |
| `smooth_points` | Apply optional light denoising in XY space |
| `path_lengths` | Cumulative arc length along a polyline |
| `pchip_curve` | Fit and sample a PCHIP curve using arc length as parameter |
| `fit_curve` | Create a dense geometric curve from prepared contour points |
| `arc_length_resample` | Resample a polyline at nearly uniform arc-length spacing |

Dependencies: `numpy`, `scipy.interpolate.PchipInterpolator`, `scipy.signal.savgol_filter`, `cv2`.

---

## `new_interpolation/debug_plotting.py` — Debug & Reports

| Function | Docstring |
|---|---|
| `plot_pixel_to_mm_debug` | Plot robot-mm paths immediately after pixel-to-mm conversion |
| `plot_pixel_to_mm_strategy_comparison` | Plot side-by-side pixel-to-mm strategy results with min-rect dimensions |
| `write_path_shape_comparison_debug` | Persist metrics and an overlay comparing pixel-to-mm output to move-prep paths |
| `plot_trajectory_debug` / `plot_pivot_path_debug` | Trajectory / pivot-path debug views |
| `plot_workpiece_alignment_debug` | Workpiece alignment debug view |

All consumers import it **lazily inside the function** so matplotlib/OpenCV figure code never loads at module import time:

| Consumer | Import site |
|---|---|
| Paint diagnostics | `src/robot_systems/paint/processes/paint/execute/diagnostics.py:515` |
| Paint dashboard | `src/robot_systems/paint/applications/dashboard/service/paint_dashboard_service.py:610` |
| Path preparation | `src/engine/robot/path_preparation/default_workpiece_path_preparation_service.py:905` |
| Workpiece editor | `src/applications/workpiece_editor/controller/workpiece_editor_controller.py:440,746,860` |

---

## `new_interpolation/simple_interpolation_pyqt6.py` — Dev Tool

Standalone PyQt6 window for tuning pipeline parameters against live contours (camera preview, contour capture, per-tab plots). It is **not part of the runtime**: `tests/architecture/test_import_boundaries.py:66` whitelists it precisely because it may import application/vision modules that runtime code may not.

---

## `deprecated/` — Legacy Interpolation

Kept for reference; **no production or test module imports these** (the only remaining importers are inside the package itself). Import paths must include `.deprecated`:

```python
# ✗ stale (pre-refactor) path — module no longer exists here:
from src.engine.robot.path_interpolation.combined_interpolation import interpolate_path_two_stage

# ✓ correct legacy path:
from src.engine.robot.path_interpolation.deprecated.combined_interpolation import interpolate_path_two_stage
```

### `interpolate_path_linear()` — `deprecated/linear_interpolation.py`

```python
def interpolate_path_linear(
    path: list[list[float]],
    target_spacing_mm: float,
    debug: bool = False,
) -> list[list[float]]:
```

Inserts linearly interpolated intermediate points between consecutive vertices so output has approximately `target_spacing_mm` spacing.

**Segment skip rule** — a segment is only interpolated if its length is at least `2 × target_spacing_mm`. Shorter segments are left as-is to avoid uneven spacing (e.g. a 70 mm segment with 50 mm spacing would produce 50+20 mm — worse than skipping).

Input/output: each point is `[x, y, z, rx, ry, rz, ...]`; distance uses XYZ only.

### `interpolate_path_spline_with_lambda()` — `deprecated/spline_interpolation.py`

```python
def interpolate_path_spline_with_lambda(
    path: list[list[float]],
    target_spacing_mm: float = 5.0,
    k: int = 3,
    smoothing_lambda: float = 0.0,
) -> list[list[float]]:
```

Fits an independent `scipy.interpolate.UnivariateSpline` per coordinate dimension and re-samples at evenly spaced arc-length intervals.

| Parameter | Effect |
|---|---|
| `k` | Spline degree: 1=linear, 2=quadratic, **3=cubic** (default) |
| `smoothing_lambda` | `s=` for `UnivariateSpline`. `0.0` = exact interpolation; larger = smoother, may deviate |

- **Arc-length parameterisation** — parameterised by cumulative XYZ distance rather than point index, preventing distortion on uneven segments.
- **Coincident-point handling** — deduplicates via `np.unique` (duplicate arc-length values crash `UnivariateSpline(s=0)`).
- **Fallback** — a numerically failing dimension falls back to `np.interp` so the pipeline never crashes.
- Extra internals: `_compute_vertex_turn_weights`, `_build_adaptive_t_samples` (denser sampling near turns).

### `interpolate_path_two_stage()` — `deprecated/combined_interpolation.py`

```python
def interpolate_path_two_stage(
    path: list[list[float]],
    adaptive_spacing_mm: float,
    spline_density_multiplier: float = 2.0,
    smoothing_lambda: float = 0.0,
    debug: bool = False,
) -> tuple[list[list[float]], list[list[float]]]:
```

Returns `(dense_linear, smoothed)`:

1. **Stage 1** — `interpolate_path_linear(path, adaptive_spacing_mm)` — densifies so stage 2 has data
2. **Stage 2** — spline smoothing at `adaptive_spacing_mm / spline_density_multiplier`; skipped if the densified path has fewer than 4 points (cubic minimum)

This legacy module also contains the original corner-handling code: `simplify_path_for_interpolation`, `pre_smooth_path_for_interpolation`, `blend_corners_with_radius`, `_inject_corner_support_points`, `_resample_polyline_with_intervals`.

### Legacy examples / viewers

`points_interpolation_example.py`, `simple_interpolation_viewer.py`, `test_trajectory_interpolation.py`, `ttest_trajectory_interpolation.py` — ad-hoc scripts and old tests kept alongside the legacy implementation.

---

## Usage Example (active pipeline)

```python
from src.engine.robot.path_interpolation.new_interpolation.interpolation_pipeline import (
    ContourPathPipeline, PreprocessConfig, InterpolationConfig,
)

pipeline = ContourPathPipeline(
    preprocess=PreprocessConfig(min_spacing=1.0, noise_method="savgol", noise_strength=5.0),
    interpolation=InterpolationConfig(method="pchip", output_spacing=10.0),
)
result = pipeline.run(contour_points)   # PipelineResult(raw, prepared, curve, sampled)
path = result.sampled.tolist()
```

---

## Design Notes

- **Two generations coexist on purpose**: `new_interpolation` is what runtime code imports; `deprecated` documents the earlier three-stage approach (linear densify → spline → corner blend) that it replaced. Do not import from `deprecated/` in new code.
- **XYZ-only distance (legacy)** — all spacing decisions in the legacy functions use only the first three coordinates; orientation dimensions are interpolated algebraically.
- **Input never mutated** — both legacy functions always return new lists.
- **`debug=True` (legacy)** prints stage summaries to stdout; the active package uses `debug_plotting` instead.
- **Lazy debug imports** — matplotlib/OpenCV figure helpers are imported inside call sites to keep module import cost and side effects out of the hot path.
