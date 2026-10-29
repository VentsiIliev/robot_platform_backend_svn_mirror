# Paint-head detector

The integration API is `PaintHeadDetector.get_status(image)`. It accepts a BGR
`uint8` NumPy image and returns an immutable, typed `DetectionResult`. Camera
acquisition, windows, drawing, CLI parsing, and artifact writing are development
utilities; importing or constructing the detector does not import the camera or UI.

For a detailed Bulgarian walkthrough with real images, intermediate processing
stages, matching scores, geometry, and final decisions, see the
[illustrated technical manual](paint_head_detection_pipeline_bg.docx).

## Integration

Python 3.12 or newer is required. This module is part of the robot platform.
Run commands below from the platform root using its `.venv`; dependencies are
declared in the platform's `requirements.txt`. No separate editable installation
or detector virtual environment is required.

## Platform layout

- Source/API: `src/robot_systems/paint/paint_head_detection/`.
- Development UI: `src/robot_systems/paint/paint_head_detection/detect.py`.
- Headless integration: `src/robot_systems/paint/paint_head_detection/examples/get_status.py`.
- Capture tool: `src/robot_systems/paint/paint_head_detection/tools/capture.py`.
- Development calibration: `src/robot_systems/paint/paint_head_detection/config/` and adjacent `references/`.
- Tests: `tests/robot_systems/paint/paint_head_detection/`.
- Documentation: `docs/robot_systems/paint/paint_head_detection/`.
- Local captures and historical evaluation evidence: `output/paint_head_detection/` (ignored).

The bundled calibration is the existing camera installation's development
snapshot. Production consumers must supply their station calibration through
the typed API or an explicit configuration directory. Registration with platform
settings, camera streams, dashboard, and production checks is a subsequent
integration task; moving the code does not enable production gating.

The Bulgarian manual is preserved unchanged as the algorithm walkthrough. Its
original project paths and dependency versions describe the documented snapshot;
use this README for current imports, commands, and asset locations.


```python
from pathlib import Path

from src.robot_systems.paint.paint_head_detection import HeadStatus, PaintHeadDetector, PaintHeadError

paint_head_detector = PaintHeadDetector()

try:
    result = paint_head_detector.get_status(image)
except PaintHeadError as error:
    # error.reason is an ErrorReason enum; error.message explains the failure.
    raise

if result.status is HeadStatus.HEAD_MISALIGNED:
    # React to the confirmed misalignment warning.
    pass

if result.alignment is not None:
    shift_pixels = result.alignment.translation_pixels
    angle_degrees = result.alignment.rotation_degrees
```

Reuse one instance for each ordered image stream. References, configuration, and
rotated templates are reused. `get_status` preserves temporal confirmation and
placement hysteresis: the initial confirmed status is `UNKNOWN` until enough
observations arrive. `result.observed_status` is the current image's classification
before temporal filtering. Call `reset()` before an independent stream, or when
replaying unrelated individual images. Do not recreate the detector per frame.

`result.reason` is a `DetectionReason` enum, and `result.message` explains the
outcome. `result.diagnostics` contains typed feature matches, positive empty-mount
evidence, image quality, pose, and the read-only edge mask. The input image is
never modified. Calls on one detector instance are serialized; use separate
instances for different cameras/calibrations.

The development app is the first integration. The second is the runnable,
headless [`src/robot_systems/paint/paint_head_detection/examples/get_status.py`](../../../../src/robot_systems/paint/paint_head_detection/examples/get_status.py). Its
`HeadlessApplication` accepts typed configuration and optional externally supplied
calibration, returning typed `InspectedImage` results for saved frames. It uses
the same public API and demonstrates image loading, status/placement access,
enum comparisons, and exception handling:

```sh
.venv/bin/python src/robot_systems/paint/paint_head_detection/examples/get_status.py
.venv/bin/python -m src.robot_systems.paint.paint_head_detection.examples.get_status
```

Direct file execution also works from an IDE or another working directory.

Edit [`src/robot_systems/paint/paint_head_detection/examples/settings.py`](../../../../src/robot_systems/paint/paint_head_detection/examples/settings.py) to set input image paths,
the detector configuration directory, and whether frames are independent.
`independent_images=True` uses a local one-frame confirmation override and resets
between snapshots. Set it to `False` for ordered frames with the configured
temporal behavior. Neither mode opens a camera or development window. The default
settings inspect both local reference images.

The example accepts a typed `ExampleSettings` object directly through
`main(settings)`. Its optional `calibration` field accepts externally supplied
reference arrays or paths, ROI, ignored regions, and tracked features; omitted
calibration comes from the dedicated detector configuration files. Other
components can use `HeadlessApplication(configuration, calibration=...)` and
`run(image_paths)` directly. Feature coordinates use the full reference image,
and all features and the empty-mount region must fit within the inspection ROI.

The input must have shape `(reference_height, reference_width, 3)` and dtype
`numpy.uint8`. Invalid type, dtype, channels, or size raises `InvalidImageError`
with a specific `ErrorReason`. Invalid settings raise `ConfigurationError`;
unreadable or inconsistent references raise `CalibrationError`; vision backend
failures raise `DetectionProcessingError`, preserving the original exception as
its cause. A failed image operation clears temporal state. Poor visibility and
insufficient visual evidence are valid `UNKNOWN` results, not exceptions.

Typed configuration can also be provided directly:

```python
from dataclasses import replace
from src.robot_systems.paint.paint_head_detection import ConfigurationRepository, PaintHeadDetector

configuration = ConfigurationRepository(Path('/path/to/station/paint_head_detection/config')).load()
configuration = replace(
    configuration,
    alignment=replace(configuration.alignment, max_rotation_degrees=3.0),
)
paint_head_detector = PaintHeadDetector(configuration)
```

The no-argument constructor uses this module's `config/` and bundled development
reference images. Deployments should pass station-specific configuration and
reference images; the checked-in calibration describes one installation.

External components can supply full-frame reference arrays, ROI, ignored
regions, and feature definitions without writing calibration JSON:

```python
from src.robot_systems.paint.paint_head_detection import (
    CalibrationConfig, PaintHeadDetector, ReferenceImages,
)

# roi/empty_mount/ignored_regions are Region objects; feature groups contain
# FeatureDefinition objects (with FeatureRole and FeatureSupport enums).
calibration = CalibrationConfig(
    references=ReferenceImages(present_reference_image, missing_reference_image),
    inspection_region=roi,
    empty_mount_region=empty_mount,
    ignored_regions=tuple(ignored_regions),
    present_features=tuple(present_features),
    missing_features=tuple(missing_features),
)
paint_head_detector = PaintHeadDetector(configuration, calibration=calibration)
```

Reference arrays must be BGR `uint8` and have matching full-frame dimensions.
The detector owns immutable snapshots; changing the caller's arrays afterward
does not change calibration. `ReferencePaths(present=..., missing=...)` is also
accepted. `PaintHeadDetector(config_directory=..., calibration=calibration)`
reads only `matching.json`, `preprocessing.json`, and `alignment.json` from that
directory. Passing a complete `DetectorConfiguration` requires no files.

Runtime changes use typed methods and return `ConfigurationUpdateResult`:

```python
update = paint_head_detector.set_roi(
    roi, empty_mount_region=empty_mount, ignored_regions=ignored_regions,
)
update = paint_head_detector.set_reference_images(
    ReferenceImages(new_present_image, new_missing_image),
)
update = paint_head_detector.set_features(present_features, missing=missing_features)

# Replace all settings together when ROI, references, and features depend on one another.
update = paint_head_detector.configure(new_configuration)
revision = update.revision
```

Omitted optional fields in the convenience setters preserve their current
values; an empty sequence explicitly clears ignored regions or missing features.
Present features must still meet the configured minimum count. ROI and feature
setters reuse loaded reference snapshots. `configure()` reloads file references.
All updates are serialized with detection and validate before replacing the
working model. Invalid updates raise `ConfigurationError` or `CalibrationError`
and preserve its configuration, revision, and temporal state. Successful updates
reset confirmation, so status may return to `UNKNOWN` while new evidence arrives.
Each `DetectionResult.configuration_revision` identifies the settings used.

## Configuration

All active detector settings live in [`config/`](../../../../src/robot_systems/paint/paint_head_detection/config/). Relative file paths
are resolved against that directory, regardless of the process's working
directory. The checked-in values describe the current camera installation; use
them as a starting point for a new installation, then validate on its images.
The JSON files are the authority if their values differ from the examples below.

| File | Responsibility | Guide |
| --- | --- | --- |
| [`references.json`](../../../../src/robot_systems/paint/paint_head_detection/config/references.json) | Correctly seated and empty-mount reference images | [Reference images](#reference-images) |
| [`roi.json`](../../../../src/robot_systems/paint/paint_head_detection/config/roi.json) | Inspection box, ignored camera area, empty-mount comparison area | [Regions and coordinates](#regions-and-coordinates) |
| [`present_features.json`](../../../../src/robot_systems/paint/paint_head_detection/config/present_features.json) | Landmarks on the installed head | [Tracked features](#tracked-features) |
| [`missing_features.json`](../../../../src/robot_systems/paint/paint_head_detection/config/missing_features.json) | Landmarks on the empty mounting face | [Tracked features](#tracked-features) |
| [`alignment.json`](../../../../src/robot_systems/paint/paint_head_detection/config/alignment.json) | Acceptable placement, hysteresis, confirmation | [Placement and temporal behavior](#placement-and-temporal-behavior) |
| [`matching.json`](../../../../src/robot_systems/paint/paint_head_detection/config/matching.json) | Candidate search, structural scores, geometric agreement | [Matching parameters](#matching-parameters) |
| [`preprocessing.json`](../../../../src/robot_systems/paint/paint_head_detection/config/preprocessing.json) | Lighting normalization, edges, image-quality checks | [Lighting and edge extraction](#lighting-and-edge-extraction) |
| [`development.json`](../../../../src/robot_systems/paint/paint_head_detection/config/development.json) | Development camera, windows, capture, exposure experiments | [Development settings](#development-settings) |
| [`src/robot_systems/paint/paint_head_detection/examples/settings.py`](../../../../src/robot_systems/paint/paint_head_detection/examples/settings.py) | Inputs and configuration for the headless integration | [Headless example settings](#headless-example-settings) |

Settings are validated when constructing a detector and on every API update.
Editing a file alone does not update a running instance: restart the development
app, or load the configuration and call `detector.configure(configuration)`.
A successful API update resets temporal confirmation and increments
`configuration_revision`. An invalid update raises a typed error and preserves
the working detector. Production configuration uses frozen dataclasses and enums;
JSON key access is confined to the configuration boundary.

Keep the documented keys when editing a file; most scalar settings are required,
and missing keys do not automatically restore their checked-in values. JSON uses
`true`, `false`, and `null`; the typed Python example uses `True`, `False`, and
`None`. Numeric settings must be finite and obey the constraints described below.

### Calibrate a new installation

1. **Fix the camera position and image size.** Choose a resolution that keeps the
   two fasteners recognizable. Reference images and incoming frames must have
   identical full-frame dimensions, BGR channels, and `uint8` data. The current
   installation uses 1280 × 720 frames. Moving the camera, changing its zoom, or
   resizing/cropping frames changes the coordinate system and requires checking
   the references, regions, features, and placement limits again.
2. **Save two raw reference images.** Capture the head seated in its correct
   position, then the mounting face with the head removed. Save full-resolution
   images without drawn boxes, text, or display scaling, and update
   `references.json`. For the first calibration, use your acquisition component
   or camera software to save these images. `src/robot_systems/paint/paint_head_detection/tools/capture.py` constructs a
   detector and therefore needs valid references and configuration already.
3. **Draw the inspection and exclusion regions.** In `roi.json`, include the
   correctly seated head and its expected displaced/rotated positions, in both
   directions. Include the empty mounting face too. Exclude the changing camera
   next to the knob through `ignore_regions`. Select an `empty_mount` rectangle
   whose appearance identifies the exposed mounting face. Leave sufficient room
   for entire feature patches to remain inside the inspection box during motion.
4. **Select stable landmarks.** Configure at least two distinct present-head
   features. The current round fasteners use `support: "circle"` and
   `orientation_invariant: true`; the knob provides supplementary evidence.
   Select tight patches with recognizable edges and substantial separation.
   Keep changing cables, the adjacent camera, reflections, and unrelated
   background out of these patches. Add at least two identifiable empty-mount
   landmarks with `role: "missing"` in the missing-feature file.
5. **Check edge quality before adjusting scores.** Run
   `.venv/bin/python src/robot_systems/paint/paint_head_detection/detect.py` and inspect the `Detection Edges` window.
   Fastener contours should survive normal lighting changes without the mask
   filling with noise. Check `result.reason` for exposure/contrast failures.
   Tune preprocessing only after the regions and references are correct.
6. **Tune recognition using labelled images.** Collect correctly seated,
   translated, rotated-left, rotated-right, empty-mount, and partially obscured
   examples under the lighting conditions the installation will encounter.
   Inspect feature scores and geometric agreement. Set feature thresholds to
   separate real landmarks from competing matches. Keep some captures aside for
   validation after tuning. A feature score is structural similarity, not a
   probability that the head is present.
7. **Set acceptable placement separately.** Choose the permitted pixel shift and
   rotation in `alignment.json` from the installation's requirements. Keep the
   search range broad enough to recognize a head outside those limits, so it can
   report `HEAD_MISALIGNED`. Set hysteresis margins smaller than the corresponding
   limits unless recovery is intentionally required to reach zero error.
8. **Validate sequences and performance.** Use ordered images or the live feed to
   check confirmation, brief occlusion, and recovery. The headless example's
   `independent_images=True` setting changes confirmation to one observation, so
   set it to `False` when checking temporal behavior. Use the FPS overlay, capture
   summaries, and camera-free benchmark to assess cost. Recheck all labelled
   cases after each tuning change, then retain the matching references and JSON
   files together as that installation's calibration.

The development tools also provide rectangle selection:

```sh
.venv/bin/python src/robot_systems/paint/paint_head_detection/detect.py --select-features
.venv/bin/python src/robot_systems/paint/paint_head_detection/detect.py --select-missing-features
```

They load and validate the existing configuration first, so a new installation
needs valid seed feature files or manual JSON setup before using these commands.
The selector writes a replacement `features` list containing names, rectangles,
and thresholds. **After selection, edit advanced fields such as `support`,
`orientation_invariant`, `required`, `role`, and `max_template_rotation` in the
JSON files.** The selector does not preserve those advanced fields. Cancelling
without selecting any feature preserves the existing file.

### Reference images

[`references.json`](../../../../src/robot_systems/paint/paint_head_detection/config/references.json) has two required path values:

```json
{
  "present": "../references/head_present.png",
  "missing": "../references/head_missing.png"
}
```

| Field | What to supply |
| --- | --- |
| `present` | A full-frame raw image of the correctly seated head. Its selected feature centers define the expected placement. A misplaced head in this reference becomes the expected pose. |
| `missing` | A full-frame raw image of the actual empty mounting face, taken with the same camera position and image dimensions. This supplies the plate comparison and empty-mount landmarks. |

Both files must exist and decode successfully. The detector loads path references
as BGR images and requires equal dimensions. Externally supplied `ReferenceImages`
must already be three-channel BGR `uint8` arrays. The detector snapshots reference
arrays and reuses its prepared edges/templates. ROI and feature setters reuse
that snapshot; `set_reference_images()` replaces it, and `configure()` reloads
file references.

The two development reference images are included under the module's `references/`
directory and explicitly allowed by the platform Git ignore rules. Captures stay
local and ignored. Each installation must supply its own calibration and point
this file to its references. Similar lighting in the two references helps isolate
the physical difference; avoid glare that erases landmark edges.

### Regions and coordinates

All rectangles use **full-frame pixel coordinates**, including feature boxes and
ignored regions. The origin is the image's top-left corner, `x` increases right,
and `y` increases down. A rectangle selects `image[y:y+height, x:x+width]`.
Display-window resizing does not change these coordinates.

| Rectangle field | Current inspection-box value | Meaning and constraints |
| --- | --- | --- |
| `x` | `470` px | Left edge; non-negative integer. |
| `y` | `215` px | Top edge; non-negative integer. |
| `width` | `450` px | Horizontal extent; integer ≥ 2. The right edge is `x + width`, excluded from the slice. |
| `height` | `505` px | Vertical extent; integer ≥ 2. The bottom edge is `y + height`, excluded from the slice. |

These four fields define the inspection box at the root of `roi.json`; the same
schema applies to every nested rectangle. With the current values, processing
uses rows 215–719 and columns 470–919. Pixels outside the box do not contribute
to feature matching, normalization statistics, or image-quality statistics.

| Additional field | Current value | Meaning and setup |
| --- | --- | --- |
| `empty_mount` | `{ "x": 517, "y": 225, "width": 277, "height": 352 }` | Fixed-position patch compared with the missing reference. Must lie inside the inspection box. Choose the mounting face exposed by removal; avoid background that can change independently. If omitted, it defaults to the entire inspection box. |
| `ignore_regions` | One rectangle: `{ "name": "changeable_camera", "x": 525, "y": 225, "width": 100, "height": 90 }` | Array of rectangles excluded before edge/statistical processing. Add regions for changeable objects; `[]` or omission means no exclusions. Each rectangle must fit in the image. Prefer exclusions within the inspection box. |
| `name` | `"changeable_camera"` | Optional human-readable label on an ignored region. The detector uses its coordinates, not this label. |

The inspection box, empty-mount box, ignored boxes, and feature boxes must fit in
the reference image. Present-feature rectangles must also avoid ignored pixels
entirely, including rectangle corners outside a circular support mask. Missing
landmarks should avoid exclusions as well. The unmasked inspection area must
contain at least `minimum_valid_pixels` pixels.

Enlarging the ROI can make rotated features visible and searchable, but also
admits more clutter and costs more processing time. Enlarge it to cover the
actual motion envelope and exclude changing content inside it. A landmark beyond
the image boundary cannot be recovered by increasing any search setting.

### Tracked features

Both feature files contain a `features` array. Present features come from the
present reference; missing features come from the missing reference. Each entry
has the following fields:

| Field | Values / fallback when omitted | Meaning and tuning |
| --- | --- | --- |
| `name` | Non-empty text; required | Identifier shown in diagnostics. Must be unique within its feature group. Use names identifying the physical landmark. |
| `x`, `y`, `width`, `height` | Required; rectangle rules above | Tight reference-image patch around the landmark. Smaller patches reduce unrelated texture; overly small patches lose distinguishing shape. Separate landmark centers improve pose measurement. |
| `threshold` | `0`–`1`; otherwise `matching.default_feature_threshold` | Minimum structural match score to support detection. Higher is stricter and can reject real features under blur/glare; lower admits more competing shapes. Tune using both true and false matches, not the reference's near-perfect self-match. |
| `role` | `"present"` in the present file; `"missing"` in the missing file | Present entries must use `"present"`. Missing entries can use `"missing"` for counted landmarks or `"empty_mount"` for an auxiliary patch excluded from the missing-landmark count. |
| `required` | Boolean; `false` | For present features, `true` requires this feature to be a geometric inlier even when enough others agree. Use only for a landmark that must always be visible. This flag is not enforced by the missing-feature matcher. |
| `orientation_invariant` | Boolean; `false` | Uses one unrotated patch and searches the full inspection box. Intended for round landmarks whose centers identify pose while their local appearance stays recognizable. Two such landmarks can propose head rotation from their relative positions. Does not make an arbitrary textured patch rotation invariant. |
| `support` | `"rectangle"` or `"circle"`; `"rectangle"` | Rectangle uses the whole patch. Circle uses its centered inscribed disk to omit surrounding bracket/background edges; use a tight, roughly square box centered on a round fastener. This controls score support, not the search region. |
| `max_template_rotation` | `null` or finite `0`–`180` degrees; `null` | Caps the global rotation grid for a non-invariant present feature. `null` uses the whole grid; `0` uses only its zero-angle entry. Ignored for invariant features. Missing features always use unrotated templates, so this setting does not enable rotated empty-mount matching. |

For example, this is **one entry** inside a present `features` array, not a
complete feature file:

```json
{
  "name": "upper_bracket_fastener",
  "x": 653,
  "y": 334,
  "width": 52,
  "height": 57,
  "threshold": 0.72,
  "role": "present",
  "required": false,
  "orientation_invariant": true,
  "support": "circle",
  "max_template_rotation": null
}
```

The checked-in calibration uses:

| Present feature | Reference box `(x, y, width, height)` | Score threshold | Settings and purpose |
| --- | --- | --- | --- |
| `adjustment_knob` | `(627, 253, 124, 59)` | `0.72` | Rectangle, non-invariant, template rotation capped at 35°. Supplementary; `required=false` lets the fastener pair establish presence when the knob is clipped. |
| `upper_bracket_fastener` | `(653, 334, 52, 57)` | `0.72` | Circle, invariant; tracks the upper fastener center. |
| `lower_bracket_fastener` | `(667, 515, 46, 41)` | `0.72` | Circle, invariant; tracks the lower fastener center. |

The missing file has `paint_head_empty_spot` with role `empty_mount` and threshold
`0.7`, plus `top_left_bolt`, `top_right_bolt`, `bottom_left_bolt`, and
`bottom_right_bolt` with role `missing` and threshold `0.7`. The auxiliary
`paint_head_empty_spot` feature is separate from `roi.empty_mount`: the latter
controls the plate comparison used by `plate_threshold`. Changing the auxiliary
feature's threshold does not change that plate threshold.

At least `min_present_features` present features must agree on one rigid pose,
and all required present features must agree. For missing verification, the
fixed plate comparison must pass and, when the missing list is populated, at
least `min_missing_features` counted landmarks must pass with consistent shifts.
An empty missing `features` array enables plate-only verification; keeping
independent missing landmarks provides additional evidence against false matches.

The file loader clips feature selections to the inspection ROI and rejects
selections with less than a 2 × 2 overlap. Define boxes fully inside the ROI so
you know exactly which patch is being used. Typed API feature definitions are
validated as supplied and are rejected if they extend outside it.

To choose a threshold, compare each landmark's scores across real positive and
competing negative examples. For illustration, if usable true matches score
0.80–0.95 and competing shapes score at most 0.60, a threshold of 0.72 leaves
separation on both sides. These illustrative ranges are not measurements of this
installation. If the two groups overlap substantially, improve the selected
patch, lighting, or geometric evidence; a threshold alone cannot separate them.
Include misplaced heads among positive examples for **head recognition**, then
use alignment limits to distinguish their placement. Tune the plate threshold
separately using empty-mount positives and installed-head/other-scene negatives.

Read the typed diagnostics when evaluating those captures:

```python
print(result.reason.value, result.message)
for match in result.diagnostics.present.matches:
    print(match.feature.name, match.score, match.passed, match.inlier)
print("plate score:", result.diagnostics.missing.plate_similarity)
print("missing landmarks:", result.diagnostics.missing.landmark_count)
```

### Placement and temporal behavior

[`alignment.json`](../../../../src/robot_systems/paint/paint_head_detection/config/alignment.json) controls acceptable placement after the
head has been recognized. These limits do not expand the search or increase
recognition confidence.

| Field | Current value | Meaning and tuning |
| --- | --- | --- |
| `max_translation_pixels` | `10.0` px | Maximum Euclidean displacement of the configured feature-centroid origin after the fitted rigid transform. Both axis offsets contribute: `(8, 8)` is about 11.3 px and exceeds a 10 px limit. Choose from the allowed image-plane installation error at the calibrated resolution. |
| `max_rotation_degrees` | `2.0`° | Maximum absolute fitted rotation relative to the correctly seated reference, in either direction. A recognized head beyond this or the translation limit is misaligned. This is independent of `matching.max_rotation`. |
| `hysteresis_pixels` | `2.0` px | Subtracted from the translation limit while recovering from observed misalignment. The current recovery limit is 8 px. Increase to reduce boundary oscillation, at the cost of requiring better repositioning. |
| `hysteresis_degrees` | `1.0`° | Subtracted from the rotation limit during recovery. The current recovery limit is 1°. Keep below the acceptance limit unless zero-error recovery is intended. |
| `stable_frames` | `3` observations | Confirmation count, integer ≥ 1. Present/missing require a full run of matching observations; misalignment evidence can accumulate across allowed brief partial-evidence gaps. Larger values slow confirmation. Use actual processed-frame rate when evaluating response time. |
| `unknown_grace_frames` | `3` observations | Maximum consecutive weak `UNKNOWN` observations that can bridge existing misalignment evidence when some head evidence remains. `0` disables such frame gaps. This never holds a green result. |
| `unknown_grace_seconds` | `0.35` s | Maximum elapsed time since the last misaligned observation for the same bridge. Both the frame and time limits must pass. Does not protect against unusable images, conflicting evidence, or loss of all head inliers. |

Both translation and absolute rotation must be within their active limits to be
aligned. Recovery limits are `max(0, limit - hysteresis)`. A placement just above
2° can latch misalignment; returning to 1.5° still fails the current 1° recovery
limit. Reach ≤ 1° **and** ≤ 8 px and obtain the configured confirmation before
expecting a green result. The latch can start from observed misalignment before
the outward status has finished confirming.

Rotation is fitted from landmark centers, so its reported precision is not
restricted to the `rotation_step` grid. Pixel limits are specific to the image
scale; they are not millimetres or proof of seating depth. Do not widen placement
limits to compensate for incorrect references or camera movement.

### Matching parameters

[`matching.json`](../../../../src/robot_systems/paint/paint_head_detection/config/matching.json) controls where matches are sought and how
independent landmarks agree. Distinguish these three kinds of tolerance:

- `edge_distance_sigma`: how much edge contours may drift locally.
- `consensus_tolerance`: how far a landmark may deviate from a proposed rigid pose.
- `max_translation_pixels` / `max_rotation_degrees`: acceptable physical placement
  in the calibrated image, configured in `alignment.json`.

#### Search and score selection

| Field | Current value | Meaning and tuning |
| --- | --- | --- |
| `search_margin` | `65` px | Center-search margin around the reference location for ordinary features, clipped to the inspection box. Larger values cover more translation and rotation-induced movement but add clutter and work. Invariant features override this and search the full inspection box. |
| `max_rotation` | `180`° | Maximum absolute angle used to generate present-head pose hypotheses and the ordinary-feature rotation grid; integer from 0 to 180. Keep broad enough to recognize the incorrect placements you want to label misaligned. A narrow range can leave them `UNKNOWN`. |
| `rotation_step` | `5`° | Positive integer spacing of ordinary-feature template rotations. Smaller steps increase search cost; larger steps may miss orientation-sensitive matches. Zero-angle matching is always included. Invariant landmarks use only their unrotated patch and derive head rotation from geometry. |
| `top_candidates` | `3` | Positive count of spatial alternatives retained **per template angle** for ordinary present features. Increasing it can preserve a true match behind a stronger false match, but creates more pose hypotheses. Ordinary missing features retain their single best candidate. |
| `invariant_candidates` | `48` | Invariant landmarks retain up to `max(top_k, invariant_candidates)` spatial peaks; for present matching `top_k` starts as `top_candidates`. Higher values help recover matching fasteners among similar circles, but can substantially increase pose-association cost. |
| `peak_window` | `15` px | Positive odd width/height of the local-maximum filter for invariant peaks. Larger windows suppress nearby competing peaks; overly large windows can hide useful close alternatives. |
| `candidate_score_ratio` | `0.65` | Candidate-generation cutoff as a fraction of the feature threshold. A feature threshold of 0.72 currently admits candidates starting at 0.468, but final support still needs 0.72 and geometric agreement. Use a fraction in `[0, 1]`; decreasing it retains more weak alternatives and work. |
| `suppression_radius` | `7` px | Radius suppressed after selecting an ordinary-feature score maximum. Increase to avoid several candidates representing nearly the same location; decrease when useful alternatives are close together. |
| `edge_distance_sigma` | `2.0` px | Positive scale of the Gaussian edge-proximity score, `exp(-distance² / (2 × sigma²))`. Larger values tolerate more lighting-induced edge drift but also reward nearby unrelated contours. This changes feature and plate similarity scores, so recheck their thresholds after changing it. |
| `default_feature_threshold` | `0.7` | Fallback score threshold in `[0, 1]` when an entry omits `threshold`; also the selector's suggested threshold. Existing explicit feature thresholds override it. |
| `plate_threshold` | `0.65` | Required score in `[0, 1]` for the current `roi.empty_mount` patch against the missing reference at the **same coordinates**. Higher is stricter about declaring an empty mount. This comparison does not search for a moved mounting face. |

Keep `angle_tolerance` compatible with the chosen rotation-grid spacing and
observed local orientation variation. Keep a cap such as the knob's
`max_template_rotation: 35` when broad head-pose coverage does not require rotating
that patch through the entire global grid. The current knob uses 15 angles,
while each invariant fastener uses one patch.

#### Geometric agreement

| Field | Current value | Meaning and tuning |
| --- | --- | --- |
| `min_present_features` | `2` | Minimum number of distinct present-feature inliers; integer ≥ 2 and no larger than the configured present group. Raising it requires more simultaneous visible landmarks; keep the expected occlusion cases in mind. |
| `consensus_tolerance` | `14.0` px | Maximum landmark-center residual from a present-head rigid-pose hypothesis. Increase only when valid matches demonstrably need more geometric slack. Too much slack lets unrelated matches agree. This is not the allowed placement shift. |
| `angle_tolerance` | `5.01`° | Maximum difference between a pose hypothesis and a non-invariant candidate's template angle. Invariant candidates bypass this local-angle check. Too small rejects useful grid matches; too large weakens orientation consistency. |
| `residual_weight` | `0.01` score/px | Within candidate selection, utility is `score - residual_weight × residual`. More supported feature groups take priority; within comparable support, increasing the weight favors tighter geometry over a slightly higher image score. |
| `minimum_pair_baseline` | `1.0` px | An invariant landmark pair must have reference-center separation **greater than** this value before proposing a rotation. Choose well-separated landmarks in the image; this guard alone does not ensure a useful calibration baseline. |
| `pair_tolerance_multiplier` | `2.0` | Positive multiplier on `consensus_tolerance` for the allowed difference between observed and reference pair lengths when generating invariant-pair hypotheses. The current difference limit is 28 px. Individual inliers still have to meet the 14 px residual limit. |
| `min_missing_features` | `2` | Minimum passed landmarks with role `missing` when the missing-feature list is populated. Integer ≥ 2; auxiliary `empty_mount` entries do not count. Must not exceed the number of counted landmarks. |
| `relative_tolerance` | `15.0` px | For passed missing landmarks, the spread of their x shifts and the spread of their y shifts must each be no larger than this value. Smaller values require a more consistent empty-mount match. This check is not used for present-head rigid-pose consensus. |

### Lighting and edge extraction

[`preprocessing.json`](../../../../src/robot_systems/paint/paint_head_detection/config/preprocessing.json) controls this sequence within
the inspection ROI: exclude/inpaint ignored pixels → blur → divide by estimated
illumination → percentile normalization → local contrast enhancement → adaptive
Canny edges. Image quality is checked separately on the **raw grayscale** values
of unmasked ROI pixels. Increasing normalized contrast cannot rescue a raw frame
that fails the quality gate.

#### Normalization and edges

| Field | Current value | Meaning and tuning |
| --- | --- | --- |
| `blur_kernel` | `7` px | Positive odd Gaussian kernel size. Larger values suppress fine noise but can erase small landmark contours. `1` leaves this blur stage effectively unchanged. |
| `illumination_sigma` | `15.0` px | Positive Gaussian scale used to estimate slowly varying brightness for division normalization. Adjust to the scale of the illumination changes while checking that landmark structure survives. Larger values estimate broader lighting variation. |
| `illumination_floor` | `16.0` grayscale levels | Positive lower bound on the estimated illumination divisor. Raising it limits gain in dark areas; lowering it can amplify shadow noise. |
| `low_percentile` | `2.0`% | Lower percentile of the illumination-normalized ratios used as the normalization black point. Increasing it clips more of the darkest ratios. |
| `high_percentile` | `98.0`% | Upper percentile used as the normalization white point. Decreasing it clips more of the brightest ratios. Require `0 ≤ low_percentile < high_percentile ≤ 100`. |
| `minimum_normalization_range` | `0.05` ratio units | Positive floor for the difference between normalization white/black points. Raising it reduces amplification of nearly uniform patches; lowering it can turn small fluctuations into strong edges. |
| `clahe_clip_limit` | `2.0` | Positive contrast limit for local histogram equalization. Increasing it allows stronger local contrast and may reveal weak edges or amplify texture/noise. |
| `clahe_tile_size` | `8` | Positive number of tiles **per axis**, giving an 8 × 8 grid, not 8-pixel tiles. Larger values make enhancement more local. Check the edge mask after changing this or the clip limit. |
| `gradient_percentile` | `85.0`% | Percentile of normalized-image gradient strength used for the upper Canny threshold. Higher generally retains only stronger gradients; lower can recover faint contours but adds clutter. Range `[0, 100]`. |
| `canny_high_floor` | `40.0` gradient units | Minimum upper Canny threshold. The actual upper threshold is the larger of this floor and the gradient percentile. Raising it suppresses weak/noisy edges even in low-gradient frames. |
| `canny_low_ratio` | `0.4` | Lower Canny threshold divided by the upper threshold; require `0 < ratio ≤ 1`. Lower values admit more weak edges connected to stronger contours. |
| `inpaint_radius` | `3.0` px | Neighborhood radius for filling ignored pixels before filtering. Their final edges and statistics remain excluded. Adjust only if exclusion-boundary artifacts affect nearby useful contours. |

#### Raw-image quality gate

| Field | Current value | Meaning and tuning |
| --- | --- | --- |
| `quality_low_percentile` | `5.0`% | Raw grayscale percentile called `low` in the checks below. |
| `quality_high_percentile` | `95.0`% | Raw grayscale percentile called `high`. Require `0 ≤ quality_low_percentile < quality_high_percentile ≤ 100`. These percentiles are separate from normalization percentiles. |
| `dark_limit` | `8.0` grayscale levels | `high ≤ dark_limit` produces `TOO_DARK`. Raising it rejects more dim frames. Choose within the raw grayscale range 0–255. |
| `bright_limit` | `247.0` grayscale levels | `low ≥ bright_limit` produces `OVEREXPOSED`. Lowering it rejects more very bright frames. Choose within 0–255. |
| `minimum_contrast` | `12.0` grayscale levels | `high - low < minimum_contrast` produces `LOW_CONTRAST`. Raising it rejects more flat images. Confirm that rejected images actually lack useful landmark detail before lowering this value. |
| `minimum_valid_pixels` | `100` pixels | Minimum unmasked inspection area; positive integer. A smaller usable region fails configuration during construction rather than returning a frame status. |

Quality checks run in the order dark, overexposed, then low contrast. Failure
returns an observed `UNKNOWN` and clears confirmation, including a held warning.
For ordinary light changes, first verify the mask and exposure, then compare edge
masks under representative lighting. Tune normalization/edges for recognizable
contours and validate scores afterward. Changing score thresholds alone cannot
restore contours lost to glare, darkness, or blur.

### Development settings

[`development.json`](../../../../src/robot_systems/paint/paint_head_detection/config/development.json) affects the development apps and
`Camera.py`; the core `PaintHeadDetector` does not read it. A host integrating the
API owns its acquisition, threading, display, and persistence choices.

#### Camera settings

Fields below are under the `camera` object.

| Field | Current value | Meaning and setup |
| --- | --- | --- |
| `camera.device` | `0` | Integer camera index, device-path string such as `/dev/video0`, or supported stream URL. Use the device actually connected to this installation. |
| `camera.width` | `1280` px | Requested width for standalone camera use/preview. Detector development/capture sessions replace this with the reference-image width. |
| `camera.height` | `720` px | Requested height for standalone camera use/preview. Detector sessions use the reference-image height. Changing only these two fields does not rescale detector calibration. |
| `camera.fourcc` | `"MJPG"` | Four-character requested camera format. Use a format the device supports at the required resolution/FPS; inspect the reported stream properties. The camera can negotiate a different format. |
| `camera.fps` | `30.0` frames/s | Positive requested acquisition rate. Actual camera rate, end-to-end FPS, and processing-only benchmark FPS can differ. Raising the request does not increase detector compute throughput. |
| `camera.backend` | `"AUTO"` | One of `AUTO`, `ANY`, `V4L2`, `DSHOW`, `FFMPEG`. `AUTO` selects V4L2 on Linux, DSHOW on Windows, otherwise ANY. HTTP(S) device URLs use FFMPEG. |
| `camera.open_timeout` | `5.0` s | Positive retry window for opening the camera. A backend's individual blocking open call is not forcibly interrupted by this timer. |
| `camera.retries` | `3` attempts | Positive maximum number of read attempts per capture call, also bounded by `read_timeout`. Does not count camera-open attempts. |
| `camera.read_timeout` | `1.0` s | Positive elapsed-time budget checked after failed read attempts. A blocking backend read can exceed this wrapper budget. |
| `camera.retry_delay` | `0.1` s | Delay between failed camera-open attempts. Increase when a device needs time to become available. |
| `camera.configuration_settle_delay` | `0.05` s | Delay after applying stream format, resolution, buffer, and FPS requests. |
| `camera.control_settle_delay` | `0.02` s | Delay after changing an exposure property before reading back/continuing. Increase if readback is stale on this driver. |
| `camera.stream_release_delay` | `0.2` s | Delay between releasing and reopening the stream when switching automatic exposure. |
| `camera.automatic_exposure_values` | `[3.0, 1.0, 0.75, 0.25]` | Driver mode codes tried in order when enabling automatic exposure. These are mode identifiers, not exposure times. Set for the actual backend/device. |
| `camera.manual_exposure_values` | `[1.0, 0.25, 0.0, 0.75]` | Driver mode codes tried in order when disabling automatic exposure. The first accepted property write ends the attempt sequence. |
| `camera.automatic_exposure_modes` | `[3.0, 0.75]` | Readback mode codes recognized as automatic by the exposure controller and preview toggle. Keep consistent with what the driver reports. |
| `camera.manual_exposure_modes` | `[1.0, 0.25]` | Readback mode codes accepted as manual before the exposure sweep writes exposure values. A successful property write with an unrecognized readback can still fail the sweep. |
| `camera.exposure_absolute_tolerance` | `2.0` driver units | Absolute allowance between requested and reported exposure. Used with relative tolerance as described below. |
| `camera.exposure_relative_tolerance` | `0.1` | Fraction of the requested exposure allowed as readback error. With a positive request, acceptance uses the larger of this fraction and the absolute allowance. |

Use non-negative delay/tolerance values. The exposure candidate lists and mode
lists must be non-empty arrays of finite numbers. They are consulted when
changing exposure mode; listing them does not automatically impose a particular
exposure at normal detector startup. Driver exposure units are not assumed to be
milliseconds. The current sweep calibration requires positive exposure values
and rounds requests to integers, as used by the supported V4L2 setup; a device
using negative logarithmic exposure values needs different integration logic.

#### Runtime and capture settings

Fields below are under the `runtime` object.

| Field | Current value | Meaning and tuning |
| --- | --- | --- |
| `runtime.opencv_threads` | `1` | Positive OpenCV thread count applied by the detector and capture entry points. Benchmark on the target CPU before increasing it. The core API does not change a host's process-wide thread setting. |
| `runtime.headless` | `false` | Default window behavior for `src/robot_systems/paint/paint_head_detection/detect.py`. Headless detector runs also require a positive duration. `src/robot_systems/paint/paint_head_detection/tools/capture.py` defaults to headless independently; `--show` enables its windows, and an explicit `--headless`/`--no-headless` takes precedence. |
| `runtime.duration` | `0.0` s | Main development-run duration. Zero means interactive operation until `Q`; use a positive value for timed/headless operation. |
| `runtime.capture_duration` | `12.0` s | Recording duration **per level** in the capture tool. Exposure calibration and warmup add time to the full session. Must be positive. |
| `runtime.capture_interval` | `1.0` s | Positive interval between automatic saved frame/overlay/metadata sets. Smaller values increase disk activity and can affect live FPS. In the main dev app, automatic saving also requires `--capture-dir`. |
| `runtime.output_directory` | `"../../../../../output/paint_head_detection/captures"` | Capture root, relative to the configuration directory. The capture tool creates timestamped session/level subdirectories unless a capture directory is supplied. |
| `runtime.benchmark_frames` | `30` observations | Positive number of timed `get_status` calls on the present reference for `--benchmark`. One untimed call prepares the reusable caches first. No camera acquisition or window rendering is timed. |
| `runtime.warmup_frames` | `12` frames | Positive number of camera frames read/discarded to settle acquisition before capture and after exposure changes/calibration requests. Separate from detector confirmation and benchmark warmup. |
| `runtime.exposure_calibration_attempts` | `6` attempts | Positive maximum number of adjustments to match the original capture's brightness in manual exposure mode. Failure stops calibration with a camera-control error. |
| `runtime.exposure_brightness_tolerance` | `0.15` | Allowed fractional difference from target median ROI brightness during manual-baseline calibration. Current value permits 15%, subject to the absolute floor below. |
| `runtime.exposure_brightness_floor` | `5.0` grayscale levels | Absolute brightness allowance; calibration accepts error ≤ `max(floor, tolerance × target_brightness)`. Helps avoid demanding an unrealistically tiny error at low target brightness. |
| `runtime.exposure_ratio_min` | `0.4` | Lower bound on the multiplicative exposure adjustment per calibration attempt. Use a positive value no greater than `exposure_ratio_max`. |
| `runtime.exposure_ratio_max` | `4.0` | Upper bound on that adjustment. The next request scales by the target/measured brightness ratio clipped between these two bounds. Bounds spanning 1 allow adjustments in both directions. |
| `runtime.exposure_factors` | `[0.5, 1.0, 2.0]` | Positive multipliers of the calibrated manual exposure for `--exposure-sweep`. The original capture runs first, followed by these levels. These multiply requested driver exposure values, not guaranteed image brightness. |

A normal capture does not require an exposure sweep. Unsupported individual
factor requests are reported as skipped levels; failure to establish the manual
baseline can stop the session. The controller attempts to restore original
exposure controls afterward and reports restoration failures. Use the original
scene/camera configuration while evaluating light sensitivity.

#### View settings

Fields below are under the `view` object. Sizes affect development windows and
overlays, not input image dimensions or detector coordinates.

| Field | Current value | Meaning and setup |
| --- | --- | --- |
| `view.show_edges` | `true` | Show the exact binary mask used for matching in a separate window. Useful for lighting/feature setup. |
| `view.show_expected` | `true` | Draw expected feature positions and displacement guides on the overlay. |
| `view.main_width` | `960` px | Initial main-window width; positive integer. |
| `view.main_height` | `540` px | Initial main-window height; positive integer. |
| `view.edges_width` | `640` px | Initial edge-window width; positive integer. |
| `view.edges_height` | `360` px | Initial edge-window height; positive integer. |
| `view.main_title` | `"Paint Head Detection"` | Non-empty main-window title. |
| `view.edges_title` | `"Detection Edges"` | Non-empty edge-window title. |
| `view.fps_window` | `30` observations | Rolling timestamp-window length for measured display FPS; integer ≥ 2. Larger values smooth the label but react more slowly to changes. |
| `view.dash_period` | `12` px | Distance between expected-box dash starts. Positive integer. |
| `view.dash_length` | `6` px | Length of each expected-box dash. Positive integer; keep ≤ `dash_period` for visible gaps. |
| `view.present_color` | `[0, 255, 0]` | Green present-status overlay color; also used for passed feature matches. |
| `view.misaligned_color` | `[0, 165, 255]` | Orange misalignment overlay color. |
| `view.missing_color` | `[0, 0, 255]` | Red empty-mount overlay color. |
| `view.unknown_color` | `[0, 255, 255]` | Yellow uncertain/unconfirmed overlay color. |
| `view.expected_color` | `[255, 255, 0]` | Cyan expected-position guides. |
| `view.ignored_color` | `[160, 160, 160]` | Gray ignored-area overlay. |

Colors are OpenCV **BGR**, with three integer channels from 0 to 255; they are not
RGB arrays. Visual settings do not change scores or decisions.

### Headless example settings

[`src/robot_systems/paint/paint_head_detection/examples/settings.py`](../../../../src/robot_systems/paint/paint_head_detection/examples/settings.py) contains a typed `SETTINGS` object,
so the headless integration needs no argument parser.

| Field | Checked-in example value | Meaning and setup |
| --- | --- | --- |
| `config_directory` | Module's `config/` directory | Directory for detector JSON files. It is resolved from the example file's location, so direct execution from another working directory works. |
| `image_paths` | Tuple containing local present/missing reference paths | Input images in processing order. Replace with captured-frame paths for evaluation. Python `Path` values supplied by a host can be absolute; relative paths follow that host's working directory. |
| `independent_images` | `True` in `SETTINGS` | Resets between images and locally uses `stable_frames=1`. Set to `False` for an ordered stream and the configured confirmation behavior. Does not edit `alignment.json`. |
| `calibration` | `None` | Optional `CalibrationConfig` supplying reference paths/arrays, inspection/empty-mount/ignored regions, and feature tuples. When supplied, only matching/preprocessing/alignment JSON files are needed. Otherwise calibration comes from the configuration directory. |

Run `.venv/bin/python src/robot_systems/paint/paint_head_detection/examples/get_status.py`, or instantiate
`HeadlessApplication` directly as described in [Integration](#integration).

### Diagnose and tune by symptom

| Symptom | Check first | Configuration to adjust after checking evidence |
| --- | --- | --- |
| Rotated head becomes `UNKNOWN` | Are both fasteners fully inside the image/ROI, and do their edge patches still match? Is an optional knob incorrectly required? | ROI coverage, feature `support`/`orientation_invariant`/`required`, `max_rotation`, then candidate budgets and geometric tolerances. Widening acceptance limits cannot recover missing evidence. |
| High feature score but feature is rejected | Present support also needs agreement with the common pose; inspect inlier counts and the other landmarks. | Patch selection, `consensus_tolerance`, and `angle_tolerance`; a threshold alone does not establish geometric agreement. |
| Usable images alternate with exposure-related `UNKNOWN` | Read `result.reason`; inspect raw brightness and the edge mask at the failing lighting condition. | Exposure/mask setup, normalization, then quality thresholds only when their rejection is demonstrably inappropriate. |
| `UNKNOWN` appears only at startup or after reconfiguration | Is `observed_status` already correct while reason is `CONFIRMING_STATUS`? | `stable_frames` and actual processing cadence; use a sequence when testing confirmation. |
| Misalignment alternates with `UNKNOWN` during occlusion | Does at least some consistent head evidence remain, and is the image usable? | Landmark visibility/search first; then bounded `unknown_grace_frames` and `unknown_grace_seconds` for brief partial-evidence gaps. |
| Head remains misaligned after moving back | Inspect fitted displacement/rotation and the stricter active recovery limits. | Reference correctness, then acceptance limits and hysteresis margins. With current settings, recovery needs ≤ 8 px and ≤ 1°, followed by confirmation. |
| Wrong object/empty mount matches head features | Examine competing landmarks and whether several similar patches can form a plausible pose. | More distinctive/separated features, thresholds, required landmarks where visibility permits, and tighter geometric agreement. |
| Empty mount does not verify | Check the fixed `empty_mount` patch, plate score, counted missing landmarks, and their shifts. | `plate_threshold`, missing-feature thresholds, `min_missing_features`, `relative_tolerance`, and empty-mount ROI selection. |
| FPS drops | Separate camera read time, detector time, display, and saving time using the capture summary and benchmark. | ROI area, ordinary-feature `search_margin`, rotation grid/caps, candidate counts, capture interval, camera format, and measured thread count. Increasing candidate budgets can grow association work rapidly. |

Change one parameter group at a time and keep the same labelled comparison set.
Use the camera-free benchmark for processing cost and the live FPS label for the
whole acquisition/display loop. Reusing one detector preserves caches; the first
frame after construction/reconfiguration can cost more than subsequent frames.

The previous JSON files beside the reference images were retained locally in
`output/paint_head_detection/refactor_backup/legacy_configuration/`; runtime no longer reads them.

## Status behavior

- `HEAD_PRESENT`: verified head within the allowed reference-relative pose.
- `HEAD_MISALIGNED`: verified head outside the placement limits.
- `HEAD_MISSING`: positive evidence of the empty mounting face.
- `UNKNOWN`: insufficient, conflicting, or unusable evidence, or pending confirmation.

Pixel displacement is the Euclidean shift of the reference feature centroid.
Rotation is signed; the limit applies to its absolute value. Both fasteners must
remain recognizable inside the inspection ROI for landmark-pair verification.
The search supports both rotation directions, including large rotations. The
knob is supplementary; a clipped knob does not veto a verified fastener pair.

Only pixels inside the configured inspection box contribute. The ignored camera
area is removed before preprocessing and statistics. The empty-mount check uses
its separate region. Circular support masks omit surrounding bracket texture;
landmark geometry determines head rotation independently of local fastener angle.

Green clears immediately when verification is lost. A confirmed misalignment
warning bridges only short partial-evidence gaps, bounded by both the configured
frame count and elapsed time. Invalid images, contradictory evidence, or loss of
all head evidence immediately clear the warning. Recovery requires returning
inside the limits minus the configured hysteresis margins, then confirming the
aligned pose. Glare, severe blur, occlusion, and landmarks outside the image can
still produce `UNKNOWN`. This checks image-plane placement; hidden latch
engagement or seating depth requires additional evidence.

## Development tools

```sh
.venv/bin/python src/robot_systems/paint/paint_head_detection/detect.py
.venv/bin/python src/robot_systems/paint/paint_head_detection/tools/capture.py
.venv/bin/python src/robot_systems/paint/paint_head_detection/tools/capture.py --show --duration 10
.venv/bin/python src/robot_systems/paint/paint_head_detection/tools/capture.py --exposure-sweep --duration 4
.venv/bin/python src/robot_systems/paint/paint_head_detection/tools/capture.py --benchmark
```

`src/robot_systems/paint/paint_head_detection/detect.py` is only the development entry point. Other components import the
package instead. Both development acquisition paths use the shared engine
[`Camera`](../../../../src/engine/vision/implementation/plvision/PLVision/Camera.py)
through the typed `development/camera_session.py` adapter. The adapter supplies
the configured device, format, timing, retry limits, and exposure candidates;
properties are `CameraProperties` values accessed through `.width`, `.height`,
`.fps`, and so on. Engine failures are translated to `CameraError` with explicit
reasons. There is no detector-local camera implementation.

The development application owns its camera while running. Close it before
starting another application that owns the same physical device. Production
integration should consume frames from the platform's camera owner.

The main view shows a rolling actual FPS label, cyan dashed expected positions,
solid detected positions, and displacement arrows. A separate `Detection Edges`
window shows the exact binary mask passed to matching. Use `--no-show-expected`
or `--no-show-edges` to hide these views. Press `Q` to quit and `S` to save.

CLI arguments are optional development overrides; file values remain the source
of defaults. Existing matching/alignment flags are supported, along with
`--config-dir` for an alternative configuration directory. For example:

```sh
.venv/bin/python src/robot_systems/paint/paint_head_detection/detect.py --alignment-pixels 8 --alignment-degrees 3
```

Captures contain raw PNGs, overlays, and JSON-serialized typed results under
`output/paint_head_detection/captures/<UTC timestamp>/`. The capture API itself returns
`CaptureSessionResult`; JSON serialization happens only when writing artifacts.
Summaries separate acquisition and detection time. Exposure sweeps calibrate a
manual baseline against initial automatic-mode brightness, skip unsupported
settings, and restore original controls; restoration failures are reported.

## Verification

Run tests using the platform environment. To enable the optional static checks,
install `src/robot_systems/paint/paint_head_detection/requirements-dev.txt` into
that environment. No detector-specific environment is required.

The platform-root `pyproject.toml` owns the mypy and Ruff settings. Their initial
check scope covers the detector module and, for Ruff, its tests; it does not
apply these checks to the rest of the platform.

```sh
.venv/bin/python -m unittest discover -s tests/robot_systems/paint/paint_head_detection -t . -v
.venv/bin/python -m mypy --config-file pyproject.toml
.venv/bin/python -m ruff check --config pyproject.toml
.venv/bin/python -m ruff format --check --config pyproject.toml
```

The tests cover the typed API contract, specific errors and reset behavior,
image immutability, absence of camera/UI side effects, ROI/camera exclusion,
lighting changes, left/right rotations, placement limits, temporal behavior,
artifacts, camera control/cleanup with a fake driver, external calibration,
atomic updates, and the headless second integration. Image regressions use
the bundled calibration references. The reference images are included in this module.
Passing these checks does not establish field accuracy; validate independently
labelled captures from the real installation before operational use.
