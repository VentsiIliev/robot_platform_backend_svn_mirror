# Paint-head detector

The integration API is `PaintHeadDetector.get_status(image)`. It accepts a BGR
`uint8` NumPy image and returns an immutable, typed `DetectionResult`. Camera
acquisition, windows, drawing, CLI parsing, and artifact writing are development
utilities; importing or constructing the detector does not import the camera or UI.

## Integration

Python 3.12 or newer is required. Install this checkout into the consuming environment:

```sh
python -m pip install -e /path/to/Paint-Head-Detection
```

```python
from pathlib import Path

from paint_head_detector import HeadStatus, PaintHeadDetector, PaintHeadError

paint_head_detector = PaintHeadDetector(
    config_directory=Path('/path/to/Paint-Head-Detection/config')
)

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
headless [`examples/get_status.py`](examples/get_status.py). Its
`HeadlessApplication` accepts typed configuration and optional externally supplied
calibration, returning typed `InspectedImage` results for saved frames. It uses
the same public API and demonstrates image loading, status/placement access,
enum comparisons, and exception handling:

```sh
.venv/bin/python examples/get_status.py
.venv/bin/python -m examples.get_status
```

Direct file execution also works from an IDE or another working directory.

Edit [`examples/settings.py`](examples/settings.py) to set input image paths,
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
from paint_head_detector import ConfigurationRepository, PaintHeadDetector

configuration = ConfigurationRepository(Path('/path/to/config')).load()
configuration = replace(
    configuration,
    alignment=replace(configuration.alignment, max_rotation_degrees=3.0),
)
paint_head_detector = PaintHeadDetector(configuration)
```

The no-argument constructor uses this checkout's `config/`. Deployments should
pass an explicit configuration directory and provide their own reference images;
calibration assets are intentionally not bundled into the Python package.

External components can supply full-frame reference arrays, ROI, ignored
regions, and feature definitions without writing calibration JSON:

```python
from paint_head_detector import (
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

All active configuration lives in `config/`. Paths in configuration files are
resolved relative to that directory. Settings are validated on construction and
on each API update. Editing files alone does not change a running instance;
load a new typed configuration and pass it to `configure()` to apply it.

| File | Responsibility |
| --- | --- |
| `references.json` | Present/missing reference image paths |
| `roi.json` | Inspection boundary, ignored camera area, empty-mount region |
| `present_features.json` | Present-head landmarks, roles, support masks, thresholds |
| `missing_features.json` | Empty-mount landmarks and thresholds |
| `matching.json` | Search ranges, geometry, scoring, candidate extraction |
| `preprocessing.json` | Illumination normalization, edge extraction, quality gates |
| `alignment.json` | Placement limits, hysteresis, temporal confirmation/dropout grace |
| `development.json` | Development camera, UI, FPS, capture, and exposure-test settings |

The migrated configuration preserves the operator's settings, including the
2-degree placement limit. The previous JSON files beside the reference images
were preserved in `output/refactor_backup/legacy_configuration/` and are no
longer read. Reference images remain in
`src/paint_head_dataset/references/` unless `references.json` points elsewhere.

Production configuration uses frozen dataclasses and enums. JSON is decoded at
the repository boundary; the vision and decision code use attributes rather than
string-keyed result dictionaries or reflective attribute access.

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
.venv/bin/python src/detect.py
.venv/bin/python tools/capture.py
.venv/bin/python tools/capture.py --show --duration 10
.venv/bin/python tools/capture.py --exposure-sweep --duration 4
.venv/bin/python tools/capture.py --benchmark
```

`src/detect.py` is only the development entry point. Other components import the
package instead. Both development acquisition paths use the typed `src/Camera.py`
wrapper. Camera properties and capture/exposure operations return typed values;
failures carry explicit error reasons. The camera wrapper's property result is
now `CameraProperties`, accessed as `.width`, `.height`, `.fps`, and so on.

The main view shows a rolling actual FPS label, cyan dashed expected positions,
solid detected positions, and displacement arrows. A separate `Detection Edges`
window shows the exact binary mask passed to matching. Use `--no-show-expected`
or `--no-show-edges` to hide these views. Press `Q` to quit and `S` to save.

CLI arguments are optional development overrides; file values remain the source
of defaults. Existing matching/alignment flags are supported, along with
`--config-dir` for an alternative configuration directory. For example:

```sh
.venv/bin/python src/detect.py --alignment-pixels 8 --alignment-degrees 3
```

Captures contain raw PNGs, overlays, and JSON-serialized typed results under
`output/captures/<UTC timestamp>/`. The capture API itself returns
`CaptureSessionResult`; JSON serialization happens only when writing artifacts.
Summaries separate acquisition and detection time. Exposure sweeps calibrate a
manual baseline against initial automatic-mode brightness, skip unsupported
settings, and restore original controls; restoration failures are reported.

## Verification

```sh
.venv/bin/python -m unittest discover -s tests -v
.venv/bin/python -m mypy
.venv/bin/python -m ruff check src tests tools examples
.venv/bin/python -m ruff format --check src tests tools examples
```

The tests cover the typed API contract, specific errors and reset behavior,
image immutability, absence of camera/UI side effects, ROI/camera exclusion,
lighting changes, left/right rotations, placement limits, temporal behavior,
artifacts, camera control/cleanup with a fake driver, external calibration,
atomic updates, and the headless second integration. Image regressions use
the local calibration references and skip when those images are unavailable.
Passing these checks does not establish field accuracy; validate independently
labelled captures from the real installation before operational use.
