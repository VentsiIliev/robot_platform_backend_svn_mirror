# Contour export and reference-scale calibration

`write_contour_dxf()` accepts an image contour as `Nx2` XY or OpenCV `Nx1x2`.
It writes a closed R2000 `LWPOLYLINE` on the green `CONTOUR` layer, translates
the contour to a lower-left origin, and flips image Y into upward CAD Y.
It does not change the input or overwrite existing files. Empty, nonfinite,
degenerate contours and invalid scales are rejected before writing.

```python
from src.engine.geometry.contour_to_dxf import write_contour_dxf

write_contour_dxf("part.dxf", detected_contour, mm_per_pixel=0.25)
```

Supplying a scale declares millimetres (`$INSUNITS=4`). Omitting it preserves
pixel distances with unitless coordinates. The module does not fit/smooth
contours, choose a work area, load calibration or connect a camera/robot.

## Standalone tray capture

[paint_tray_capture_dxf.py](../../../scripts/paint_tray_capture_dxf.py) retains the
tray-dryer detection pipeline, largest-contour selection, optional paint Bezier
processing/smoothing and live preview. The yellow rectangle is a measurement
overlay; only the green contour is exported. No robot connection is started.

To calibrate, use a rectangle with independently known physical dimensions:

```bash
.venv/bin/python scripts/paint_tray_capture_dxf.py --reference-size-mm 120 100
```

1. Place the 120 x 100 mm reference alone in the configured ROI, at the same
   capture height and plane as subsequent parts. Keep camera setup unchanged.
2. In the PyQt6 studio, click **Measure reference and calibrate**. This uses
   the raw contour and measures its minimum-area rectangle with the nominal
   saved geometry PPM. The command-line dimensions prefill the reference fields.
3. Inspect the green contour/yellow rectangle and displayed measurement errors.
   The rectangle axes are matched short-side/long-side, so rotation does not
   swap the known dimensions incorrectly.
4. On success, the correction is saved to
   `captures/paint_tray_dry/scale_calibration_paint.json`. The reference capture
   calibrates only; it does not create a DXF.
5. Remove the reference, click **Capture contour**, inspect the result, then
   **Export DXF…** to select a destination. The corrected scale is used; paint
   smoothing is enabled unless `--raw-contour` is set or unchecked in the GUI.

The PyQt6 studio reuses the saved correction, including when reference fields
are prefilled. `--demo` opens synthetic camera frames without hardware and keeps
calibration in memory; demo files default to `captures/contour_dxf_demo`.
`--opencv` retains the legacy interface: Capture/Space automatically writes DXF,
and with `--reference-size-mm` its first capture calibrates instead.

Later runs without `--reference-size-mm` reuse the saved correction. It is bound
to the area, nominal mm/pixel, geometry file path and its SHA-256 fingerprint.
Changing those rejects the saved correction; recalibrate or explicitly override
it. With no saved correction, the nominal scale is used. The former hardcoded
120 x 100 mm reference correction has been removed.

`--scale-calibration PATH` chooses another capture-tool calibration file;
`--scale-correction FACTOR` explicitly bypasses saved correction and cannot be
combined with reference calibration. `--mm-per-pixel` overrides the nominal
scale, and `--geometry-scale` selects another saved geometry PPM file. The
capture tool never rewrites that nominal geometry file or production settings.

## Correction and residuals

The shared `calibrate_rectangle_scale(measured_size_mm, reference_size_mm)`
computes one least-squares factor for both sides:

```text
correction = dot(measured, reference) / dot(measured, measured)
corrected_mm_per_pixel = nominal_mm_per_pixel * correction
```

Its result exposes corrected dimensions and residuals in mm and percent.
The script rejects a reference if either corrected side differs by more than
2% from its known dimension; `--max-calibration-error-percent` changes that
tolerance explicitly. A rejected capture leaves an existing calibration intact
and disables reference export. Calibration can be retried after fixing placement
or detection.

A single factor corrects uniform scale only. Perspective, a wrong height/plane,
unequal axis scaling or detecting the wrong contour require geometry/detection
correction rather than assuming the reference fit solved them. Verify the
exported dimensions independently against the actual part.

## Verification

```bash
.venv/bin/python -B -m unittest tests.engine.test_contour_to_dxf tests.scripts.test_paint_tray_capture_dxf -q
```

Tests read/audit generated DXFs, check units/coordinates/closure and preservation
of input/existing files, validate scale fitting and axis swapping, reject stale
calibration, and exercise reference capture followed by part export without
camera or robot hardware. Physical camera accuracy still needs station testing.
