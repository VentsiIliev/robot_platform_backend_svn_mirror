# `src/engine/robot/path_preparation/` — Workpiece → Execution Plan

Turns a workpiece dict (pixel contours captured from the camera) into a
`WorkpieceExecutionPlan` — the fully prepared, robot-frame path data that the
paint process executors consume.

**Dependency direction:** this package is imported by
`src/robot_systems/<system>/processes/...` and by the robot system's
`application_wiring.py`. It is *consumed by* robot systems but belongs to the
engine because the pipeline is robot-system agnostic.

---

## Files

| File | Contents |
|------|----------|
| `__init__.py` | Public surface: `DefaultWorkpiecePathPreparationService`, `WorkpieceExecutionPlan`, `IWorkpiecePathPreparationService`, `PIXEL_TO_MM_MODE_GEOMETRY_PPM_ANCHOR`, `PIXEL_TO_MM_MODE_HOMOGRAPHY_RESIDUAL` |
| `i_workpiece_path_preparation_service.py` | `IWorkpiecePathPreparationService` — single method `build_execution_plan(workpiece, skip_debug_plot=False)` |
| `default_workpiece_path_preparation_service.py` | `DefaultWorkpiecePathPreparationService`, `WorkpieceExecutionPlan` (1188 lines) |
| `geometry.py` | Contour canonicalization, pickup-RZ selectors, pose rebuilding (520 lines) |
| `debug.py` | `_save_contour_canonicalization_steps_debug_plot`, `_save_contour_reordering_debug_plot` |
| `config.py` | Tuning constants and per-segment settings keys |
| `pixel_to_mm/` | Strategy family for pixel → robot-XY conversion |

---

## `WorkpieceExecutionPlan`

```python
@dataclass(frozen=True)
class WorkpieceExecutionPlan:
    workpiece: dict
    raw_paths: list[list[list[float]]]        # robot-frame, immediately post-transform
    prepared_paths: list[list[list[float]]]   # after the injected contour processor
    curve_paths: list[list[list[float]]]      # the fitted curve representation
    sampled_paths: list[list[list[float]]]    # the sampled execution points
    execution_jobs: list[dict]                # per-segment job specs
    total_spline_pts: int                     # counts execution path POINTS (legacy name)
    raw_pixel_paths: list[list[list[float]]] = []
    raw_homography_paths: list[list[list[float]]] = []

    def execution_paths(self) -> list[list[list[float]]]:
        # job["execution_path"] or job["path"] fallback
```

The docstring states the contract plainly: it *"stores the transformation chain:
raw pixel paths → prepared/curve/sampled poses → final execution paths, plus
per-job metadata (velocity, acceleration, pickup point, target offsets)."*

`total_spline_pts` is explicitly annotated as a **legacy field name** — it counts
final execution path points, not spline control points.

### Per-job keys in `execution_jobs`

| Key | Meaning |
|-----|---------|
| `path`, `execution_path` | Final robot poses `(X, Y, Z, RX, RY, RZ)` |
| `captured_path_px` | The source pixels before any processing |
| `source_prepared_path_px` | Pixels after the optional source-contour processor |
| `transformed_path_mm`, `prepared_path_mm`, `curve_path_mm` | Intermediate representations |
| `vel`, `acc` | From segment `settings.velocity` / `settings.acceleration` (defaults 60 / 30) |
| `pattern_type` | `"Workpiece"` or `"Contour"` / `"Fill"` |
| `use_workpiece_layer` | Which source branch produced this path |
| `workpiece_height_mm`, `pivot_offset_mm`, `edge_cleanup_z_offset_mm` | Per-segment geometry |
| `pickup_xy`, `pickup_rz`, `pickup_target_point_name`, `pickup_target_offset_x/y`, `pickup_reference_rz` | Pickup resolution |
| `execution_target_point_name`, `execution_target_offset_x/y`, `execution_reference_rz` | Execution target-point metadata |
| `process_selection_paths_mm` | Saved paint-selection segments (workpiece-layer branch only) |
| `paint_selection_cut_applied` | Whether the canonical contour start was cut to the saved selection |

---

## `DefaultWorkpiecePathPreparationService`

### Construction

All inputs are keyword-only:

| Parameter | Role |
|-----------|------|
| `logger`, `segment_config` | Required. `segment_config.schema.get_defaults()` supplies default `spraying_height` / `rz_angle` |
| `transformer` / `transformer_getter` | Pixel→robot transformer, injected directly **or resolved lazily** via a callable |
| `resolver` / `resolver_getter` | Calibration resolver, same lazy-or-direct pair |
| `calibration_frame_name` / `calibration_frame_name_getter` | Active target frame, lazy-or-direct |
| `z_min`, `rz_mode` | Base Z floor; `"constant"` (segment `rz_angle`) or `"path_tangent"` |
| `execute_from_workpiece_layer` | `True` → use the workpiece contour instead of `sprayPattern` |
| `target_point_name`, `pickup_target_point_name` | Resolver target points (lower-cased on store; pickup falls back to execution) |
| `pixel_height_compensation_fn(height_mm) -> (dx_px, dy_px)` | Optional height-dependent pixel shift |
| `base_position_provider() -> [X, Y, Z, RX, RY, RZ] \| None` | Base pose for RX/RY and base Z |
| `pickup_axis_alignment_sign` | `+1.0` or `-1.0` (anything negative collapses to `-1.0`) |
| `pixel_to_mm_mode` | One of `config._PIXEL_TO_MM_MODES`; anything else raises `ValueError` at construction |
| `debug_plot_dir` | Enables background debug plots (empty/`None` disables all plotting) |
| `source_contour_processor` | Runs on **pixel** points before conversion |
| `contour_processor` | Runs on **robot mm** points after conversion |

The lazy getters each swallow exceptions with `logger.debug(..., exc_info=True)`
and fall back to the directly injected object, so a calibration rebuild in the
robot system does not break a running plan build.

### `build_execution_plan(workpiece, skip_debug_plot=False)`

The docstring names the five stages:

```
1. Select source      — workpiece layer contour, or sprayPattern Contour/Fill paths
2. Pixel→robot        — calibration resolver (strategy) or fallback transformer
3. Contour processor  — injected by the robot system for smoothing/resampling
4. Heading            — constant RZ, or path-tangent aligned
5. Pickup resolution  — first-segment pickup XY and RZ
```

**Source selection**

- `execute_from_workpiece_layer=True` **and** a valid `workpiece["contour"]`
  → workpiece-layer branch; `sprayPattern` is ignored for execution but its
  `Contour` entries are still read as *paint selections* and transformed into
  `process_selection_paths_mm`
- otherwise → iterate `sprayPattern["Contour"]` then `["Fill"]`
- neither present → two warnings (the hard `raise` is commented out); no paths
  at all → `ValueError("No executable paths after transformation")`

**Workpiece-layer preparation** (guarded by `config._CANONICALIZE_WORKPIECE_LAYER_CONTOUR`):

```
raw pixels
  → canonicalize_closed_contour_points()        stable winding + start point
  → _cut_closed_contour_at_saved_selection_start()  anchor start to first saved paint point
  → _process_source_contour()                   optional injected pixel processor
  → _transform_to_robot()
```

Both canonicalization steps queue debug plots (`contour_canonicalization_steps`,
`contour_reordering`) unless `skip_debug_plot`.

**Per-path stage:** `raw_paths` / `raw_pixel_paths` are appended, then
`raw_homography_paths` is filled by `HomographyOnlyPreviewStrategy` — an
**extra, independent conversion used only for debug comparison**, and an empty
list when `skip_debug_plot`.

If a `contour_processor` is configured and returns a dict, its
`prepared_xy` / `curve_xy` / `method` are used; otherwise the transformed path is
used as-is with `method="raw"`. Failures in the processor are caught with
`logger.exception` and the unprocessed path is used.

**Heading:** `rebuild_pose_path_from_xy(..., rz_mode, tangent_lookahead_distance_mm,
tangent_heading_deadband_deg)` rebuilds full poses from XY. With
`skip_debug_plot=True` the cheaper `_pose_path_from_xy()` is used instead.

**Pickup resolution** (runs once, on the first path) — see the `[PICKUP_RZ]` log
tags:

| Priority | Selector |
|----------|----------|
| workpiece layer **and** saved paint selections exist | `compute_pickup_rz_from_initial_paint_segment` |
| workpiece layer, ≥3 points | `compute_pickup_rz_from_min_rect_long_axis` |
| otherwise | `compute_pickup_rz_from_robot_path` (path tangent) |

The raw result is then axis-normalized relative to `pickup_reference_rz`:

```python
measured_delta = unwrap_degrees(reference_rz, raw_pickup_rz) - reference_rz
signed_pickup_axis = reference_rz + pickup_axis_alignment_sign * measured_delta
# workpiece layer → unwrap_degrees(reference, signed)
# spray pattern    → nearest_axis_equivalent_degrees(reference, signed)
```

Logged as `[PICKUP_RZ] axis_equivalent_normalized raw=… reference=… sign=… selected=…`.

Finally `pickup_xy` is resolved with `_transform_single_pixel_to_robot(...,
rz_override=pickup_rz)` using the *pickup* target point.

### `_transform_to_robot(pts_px, settings)`

Docstring:

> Two modes (controlled by *pixel_to_mm_mode*):
> - `geometry_ppm_anchor`: resolve a single anchor through the calibration
>   resolver, then offset all other points via a homography-derived direction
>   basis + geometry PPM scale.
> - `homography_residual`: resolve every point individually through the resolver.
>
> Falls back to a simple Transformer (or raw pixel coords) when no resolver is
> available.

Before conversion:

1. `spray_height` and `rz_angle` come from segment `settings`, falling back to
   `segment_config.schema.get_defaults()`; non-numeric →
   `ValueError("Invalid segment settings: spraying_height and rz_angle must be numbers")`
2. `base_z = base_position[2] + spray_height`, or `z_min + spray_height` with no
   base position
3. `rx, ry = _base_orientation_xy(base_position)`
4. **Pixel height compensation** — if `pixel_height_compensation_fn` is set and
   `height_mm != 0`, points are shifted by the returned `(dx_px, dy_px)`;
   exceptions are logged and the unshifted points are kept

After conversion, `rz` is either the segment `rz_offset` (`"constant"`) or
`compute_path_aligned_rz_degrees(...)`. When a resolver returned per-point seeds,
each seed's `z` is used; otherwise every point gets `base_z`.

### Pickup pixel — `_extract_pickup_pixel(merged)`

1. Explicit `merged["pickupPoint"]` — string `"x,y"`, list `[x, y]`, or
   `{"x": …, "y": …}`
2. Contour image-moment centroid (`cv2.moments`)
3. Contour XY mean
4. `None` when no contour exists

### Debug plots

All plotting goes through `_queue_debug_plot` → `_submit_debug_plot`, a module
level **single background worker** (`_ensure_debug_plot_worker`,
`_debug_plot_worker_loop`) fed by a bounded `Queue`. Matplotlib is imported
lazily with `MPLCONFIGDIR` defaulted and `Agg` backend forced, so plotting never
touches Qt and never blocks plan building. Everything is a no-op when
`debug_plot_dir` is empty.

Plots produced: `contour_canonicalization_steps`, `contour_reordering`,
`contour_pipeline_<pattern>` (3-panel before-Bézier / after-Bézier /
after-conversion), `interpolated_path` (multi-panel raw vs prepared vs curve vs
sampled vs execution, with heading markers).

---

## `pixel_to_mm/` — Conversion Strategies

Shared inputs live in one frozen dataclass:

```python
@dataclass(frozen=True)
class PixelToMmContext:
    base_z, rz_offset, rx, ry
    target_point_name, calibration_frame_name, mode_name
    logger: Logger
    geometry_scale_cache: GeometryScaleCache   # mutable, shared

@dataclass
class GeometryScaleCache:
    entry: tuple[str, float] | None = None     # one cached PPM artifact
```

| Strategy | Class | Behaviour |
|----------|-------|-----------|
| `geometry_ppm_anchor` | `GeometryPpmAnchorStrategy` | Loads a geometry pixels-per-mm artifact (`derive_calibration_artifact_paths`), computes a pixel anchor, derives a **direction basis from the homography**, resolves **one** `VisionPoseRequest` at the anchor, then offsets every other point: `anchor_xy + (Δpx · mm_per_px · x_axis) + (Δpx · mm_per_px · y_axis)`. Returns `None` (<2 points, missing PPM, or no homography basis) so the caller can fall through |
| `homography_residual` | `HomographyResidualStrategy` | Resolves **every** point individually through `resolver.resolve(VisionPoseRequest, target_point, frame=…)`, returning the seeded results **and** the XY list. Never fails |
| *(debug only)* | `HomographyOnlyPreviewStrategy` | Reads the raw homography matrix out of `resolver._base._model.homography_matrix` and converts without the full resolver model. Returns `[]` whenever anything is unavailable — it is a comparison baseline, not a production path |

The selected mode is validated in the service constructor against
`config._PIXEL_TO_MM_MODES`; `HomographyOnlyPreviewStrategy` is instantiated
unconditionally but only *called* for the debug preview.

---

## `geometry.py`

| Function | Contract |
|----------|----------|
| `has_valid_contour(contour)` | Shape/size check for a contour payload |
| `canonicalize_closed_contour_points(points)` | Normalize winding + start point. Docstring warns: *"canonicalization must not invent new boundary adjacency"* — only cyclic shift and optional reversal are allowed; nearest-neighbour rebuilding *"can create broken shapes for otherwise valid captures"* |
| `_orient_contour_like_original(candidate, original)` | Pick the loop direction by comparing candidate start neighbours against the original's predecessor/successor |
| `fast_inverse_preview_points(transformer, robot_xy)` | Inverse-mapped preview points |
| `compute_path_aligned_rz_degrees(path, base_rz_offset_degrees)` | Per-point tangent headings with lookahead distance and deadband |
| `compute_pickup_rz_from_robot_path(path, near)` | Local tangent heading near a point |
| `compute_pickup_rz_from_stable_paint_segment(path, reference)` | Scans the execution contour and *"favors segments that are locally straight and require the smallest axis-equivalent rotation from the pickup reference"* — for when a whole-shape axis is misleading |
| `compute_pickup_rz_from_initial_paint_segment(path, reference)` | Same idea but anchored to the **first** stable run: *"pickup RZ must follow the initial directed segment instead of whichever later segment happens to be closest to zero rotation"* |
| `compute_pickup_rz_from_min_rect_long_axis(points, reference)` | `cv2.minAreaRect` long axis |
| `compute_pickup_rz_from_robot_contour(points)` | Central moments — better for centroid pickup, since *"the centroid is inside the shape and does not have a meaningful boundary tangent"* |
| `compute_pickup_rz_from_robot_contour_with_direction(points, path)` | Moments, then the 180° ambiguity resolved by path ordering |
| `rebuild_pose_path_from_xy(xy, reference_path, rz_mode, …)` | Reattach Z/RX/RY (and RZ per mode) to a plain XY list |

Angle helpers are imported from `src.engine.geometry.planar`.

---

## `config.py` — Tuning Constants

| Constant | Value | Meaning |
|----------|-------|---------|
| `_EXECUTION_INTERPOLATION_SPACING_MM` | `10.0` | Interpolation spacing |
| `_EXECUTION_MIN_PREPROCESS_SPACING_MM` | `2.5` | Floor for pre-processing spacing |
| `_EXECUTION_DENSE_SAMPLING_FACTOR` | `0.25` | Dense-sampling factor |
| `_EXECUTION_OUTPUT_SPACING_SCALE` | `0.75` | Output spacing scale |
| `_EXECUTION_MIN_OUTPUT_SPACING_MM` | `6.0` | Output spacing floor |
| `_EXECUTION_DEFAULT_OUTPUT_SPACING_MM` | `max(6.0, 10.0 × 0.75)` = `7.5` | Derived default |
| `_HEADING_SUPPORT_SPACING_MM` | `1.0` | Heading support spacing |
| `_SHARP_TANGENT_BOUNDARY_DEG` | `45.0` | Sharp-tangent boundary |
| `_AUTO_DENSIFY_TRIGGER_RATIO` / `_TARGET_RATIO` | `2.5` / `1.25` | Auto-densify trigger and target |
| `_DEFAULT_WORKPIECE_HEIGHT_MM` | `0.0` | Fallback when `height_mm` missing |

Per-segment settings keys (each segment may override the global defaults):

```
preprocess_min_spacing_mm, interpolation_spacing_mm, dense_sampling_factor,
execution_spacing_mm, path_tangent_lookahead_mm, path_tangent_deadband_deg
```

Feature flags: `_CANONICALIZE_WORKPIECE_LAYER_CONTOUR = True`,
`_TEMPORARILY_SKIP_CONTOUR_INTERPOLATION = False`.

Public mode constants: `PIXEL_TO_MM_MODE_GEOMETRY_PPM_ANCHOR =
"geometry_ppm_anchor"`, `PIXEL_TO_MM_MODE_HOMOGRAPHY_RESIDUAL =
"homography_residual"`.

---

## `debug.py`

| Function | Output |
|----------|--------|
| `_save_contour_canonicalization_steps_debug_plot(...)` | One image per canonicalization step, used before pixel-to-mm |
| `_save_contour_reordering_debug_plot(...)` | Overlay of original vs canonicalized ordering |

Both accept `debug_dir` and return silently when it is empty.

---

## Consumers

| Consumer | Import |
|----------|--------|
| `src/robot_systems/paint/processes/paint/execute/workpiece_path_executor.py` | `IWorkpiecePathPreparationService`, `WorkpieceExecutionPlan` |
| `src/robot_systems/paint/processes/paint/execution_machine/handlers/workflow/plan_handler.py` | calls `service._path_preparation_service.build_execution_plan(...)` |
| `src/robot_systems/paint/processes/paint/plan/*` | `WorkpieceExecutionPlan`; `geometry.rebuild_pose_path_from_xy` |
| `src/robot_systems/paint/processes/paint/magazine_load_service.py` | `geometry.compute_pickup_rz_from_min_rect_long_axis` |
| `src/robot_systems/paint/applications/dashboard/service/paint_dashboard_service.py` | `config`, `pixel_to_mm` mode constants |
| `src/robot_systems/paint/processes/paint/config.py` | mode constants |
| `src/robot_systems/{glue,paint}/application_wiring.py` | construct `DefaultWorkpiecePathPreparationService` |
| `src/robot_systems/paint/processes/paint/execute/{pickup,dropoff,edge_cleanup,paint_contact}_executor.py`, `projection_preview.py`, `diagnostics.py` | `WorkpieceExecutionPlan` |

---

## Design Notes

- **One method, one contract.** `IWorkpiecePathPreparationService` exposes only
  `build_execution_plan` — callers never reach into stages.
- **Strategy selection is constructor-validated**, not per-call: an unknown
  `pixel_to_mm_mode` fails immediately at wiring time.
- **Lazy getters over stored references** so calibration can be rebuilt at
  runtime without re-injecting the service.
- **Every failure in an injected hook is non-fatal.** `source_contour_processor`,
  `contour_processor`, and all three getters catch and log, then fall back —
  a plan build never dies because an optional processor misbehaved.
- **Debug output is off the hot path.** A single background worker plus a bounded
  queue keeps plotting from blocking motion planning.
