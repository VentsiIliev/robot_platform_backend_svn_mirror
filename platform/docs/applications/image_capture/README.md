# Image Capture

Open **Tests → ImageCapture** in Paint Tray Dry, or **Service → ImageCapture**
in Paint and Glue. Select **Capture** to freeze a calibrated camera image and run
contour detection on that exact image. The preview shows contour outlines and
the status shows the number found. **Save capture** saves the clean PNG and contour
JSON with matching basenames in a new capture folder under the wired system's
`storage/captures` directory. The completed folder path appears below the preview.
Capture does not move the robot; capture, detection, and saving run off the GUI thread.

Each JSON contains `schema_version`, `image_file`, `captured_at`, image dimensions,
and `contours` (objects containing `points` and `closed`). Points are floating-point
`[x, y]` pairs in calibrated-image pixels: origin at top left, x right, y down.
All found contours are saved; no detections produces an empty list and count zero.
The files are written in a temporary folder and published together by renaming it
only after all writes succeed. Repeated saves create separate pairs. Failed
recapture/detection clears the old capture so it cannot be saved accidentally.

Calibration means intrinsic lens correction through the wired vision system's
`correctImage` implementation. The saved PNG has camera orientation applied but no
contour overlays, robot-coordinate conversion, or perspective warping. The camera
must be running with a non-stale frame and calibration loaded.

Detection calls the same `ContourDetectionService.detect()` used by Paint,
including threshold, morphology, approximation, smoothing, subpixel refinement,
area limits, and active work-area filtering. It operates on the captured corrected
image without applying calibration twice. It does not call Paint's
`CaptureSnapshotService` or `compute_contours_for_latest_frame()`: those also handle
robot/work-area verification, cached results, and automatic brightness. Thus this
screen shares the detector but is not an exact reproduction of Paint's full
capture pipeline. No camera settings or vision lifecycle state are changed.

## Wiring another robot system

The application accepts only `IImageCaptureService`. Compose its platform adapter
in the robot system's `application_wiring.py`:

```python
from src.applications.image_capture import ImageCaptureApplication
from src.applications.image_capture.service.image_capture_application_service import (
    ImageCaptureApplicationService,
)
from src.engine.common_service_ids import CommonServiceID


def _build_image_capture_application(robot_system):
    return ImageCaptureApplication(ImageCaptureApplicationService(
        vision_service=robot_system.get_optional_service(CommonServiceID.VISION),
        output_directory=robot_system.storage_path("captures"),
    ))
```

Register this factory in an `ApplicationSpec` in that system's Service folder.
Paint exposes `IMAGE_CAPTURE_APP` in `paint_system_config.py` to enable the screen.
A custom vision implementation must implement `IVisionService.capture_corrected_image()`
and `detect_contours_for_image(image)`:
return an owned, fresh calibrated image without overlays, and detect contours on
the supplied image without acquiring another frame or modifying it. Raise if unavailable.
The default implementation preserves compatibility with other vision providers
by reporting that capture is unsupported until they implement this method.

## Standalone and checks

```bash
.venv/bin/python src/applications/image_capture/example_usage.py
QT_QPA_PLATFORM=offscreen .venv/bin/python -m unittest discover -s tests/applications/image_capture -v
```

The standalone runner uses a synthetic image and simulated saving. Hardware
verification: capture a known scene, save it, check the displayed file, then test
capture with the camera unavailable. English and Bulgarian UI catalogs are
provided beside the application.

## Line and arc decomposition

Capture also runs the supplied `decompose_contour.py` and `decompose.py`, now
bundled under `src/applications/image_capture/processing`. The original Downloads
files are retained. The application imports the algorithm directly in its capture
worker, with no subprocess or temporary export needed. Each detected contour is
processed independently, preserving its index in the detected-contour JSON.

The **Detected contours** and **Lines and arcs** tabs show the detection and fitted
result. Decomposition uses the supplied defaults (tolerance 1.5 px, smoothing sigma
1.5, resampling step 1.0 px). Red lines, blue/green arcs and yellow endpoints follow
the script's overlay convention. The summary reports primitive counts, fits outside
tolerance, and failed contours. Degenerate contours are recorded as errors while
preserving the original capture for inspection. This does not alter Paint execution.

Each capture directory now contains four matching files:

- `<capture>.png`: original calibrated image.
- `<capture>.json`: detected pixel contours and links to decomposition files.
- `<capture>_decomposition.json`: parameters, per-contour primitives and deviation
  statistics, source indices, and summary. Coordinates and radii remain pixels.
- `<capture>_decomposition.png`: full-image overlay at the original image size.

The bundle is published only when all four files have been written successfully.
The original standalone algorithm is retained; the point-list wrapper uses a
package-relative import and validates finite/nondegenerate points before fitting.

## Robot-space experiment (Paint and Paint Tray Dry)

Capture additionally converts each detected contour using a separate instance of
Paint's configured path-preparation service. The new read-only
`convert_contour_to_robot()` entry point calls the existing `_transform_to_robot()`
routine, so conversion mode, calibration resolver, target offsets and frame selection
follow Paint wiring. Missing calibration raises an error; pixels are never exported
as millimetres. An active work-area change during capture also rejects the result.
No execution plan is built and no motion is commanded. Paint's execution behavior
is unchanged. Glue retains pixel-only capture until a converter is wired for it.

The **Robot XY (mm)** tab shows converted detected points in gray and fitted lines
and arcs in red/blue on an equal-scale XY plot. Conversion happens **before** fitting
in mm, rather than transforming pixel-space circles as if they remained circles.
This comparison uses raw detected contours, not matched stored contours or Paint's
additional pixel-space preparation and robot-space smoothing.

Experiment assumptions: workpiece height 0 mm, default segment spraying height and
orientation, with the same configured base-position provider as Paint. Captures of
nonzero-height workpieces or custom segment settings are not exact execution-path
comparisons. The mm fit currently uses tolerance 0.5 mm, sigma 0.5, step 1.0 mm and
minimum radius 1.5 mm; remaining supplied script defaults apply (including its
point cleaning). These are diagnostic defaults, not production acceptance limits.

Paint captures add two files to the existing four-file bundle:

- `<capture>_robot_mm.json`: original converted XY points, six-component poses,
  frame/target/configured conversion mode/settings, work-area ID, fit parameters,
  per-contour primitives, deviation statistics and any decomposition errors.
- `<capture>_robot_mm.png`: equal-scale robot XY comparison plot.

The main contour JSON links these files. All six files are published together.

## Sampled tangent-continuous experiment

Paint capture wiring injects the existing `resample_contour_xy` function. After
robot-space decomposition, a new capture-only stage interpolates a closed,
periodic cubic spline through dense primitive samples, then passes its dense
polyline to Paint's sampler with `spacing=1.0, closed=True`. The resulting
**Sampled path (mm)** tab shows the sampled points and connecting segments.
The existing line/arc tab remains unchanged. This does not modify Paint execution.

The underlying periodic spline is C2, including at closure. The discretized
polyline itself is not tangent-continuous, and small-radius transitions can still
produce large heading changes between 1 mm samples. This is not tangent-constrained
line/arc fitting. The final closure segment may be shorter than 1 mm, following
Paint's existing sampler behavior.

New `_sampled_mm.json` and `_sampled_mm.png` files are saved with the complete bundle
(eight files for Paint). JSON records sampled XY points, reconstructible spline
knots/coefficients, sample counts, segment lengths, maximum discrete heading change,
minimum evaluated spline speed, and numerical deviation checks in both directions.
Results that fail tolerance checks remain available with `outside_tolerance` status;
algorithm failures are recorded per contour. Checks use a dense 0.05 mm parameter
grid and are diagnostic estimates, not a continuous geometric or motion guarantee.
