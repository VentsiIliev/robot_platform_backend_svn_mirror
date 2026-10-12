# Photo to DXF

Standalone PyQt6 capture, scale verification and DXF export. It uses the shared
platform palette and touch numeric fields, supports English/Bulgarian on initial
render and during language switching, and follows the application MVC blueprint.
It does not start the robot or register another shell screen.

```bash
# Existing tray-dryer camera and configured paint work area
.venv/bin/python scripts/paint_tray_capture_dxf.py
# Hardware-free preview
.venv/bin/python scripts/paint_tray_capture_dxf.py --demo
```

The two previews show live camera frames and the last processed contour.
The measurement cards report the rotated minimum rectangle sides and contour
point count. Green is the exported contour; yellow is the measurement overlay.
The rectangle itself is not exported. Capture and Export are separate actions.

For calibration, place a rectangular reference at the same height/plane as the
parts. Enter its known dimensions and permitted residual error, then click
**Measure reference and calibrate**. The measurement uses raw contour geometry,
matching short and long sides, and computes one uniform scale correction.
Accepted calibration is stored separately from production geometry settings.
A rejected reference or failed calibration save preserves the previous scale;
reference captures cannot be exported. Remove the reference before capturing
parts. Perspective distortion requires geometry calibration, not a scale factor.

Export creates a closed millimetre DXF with Y upwards and a lower-left origin.
Existing files are never overwritten. The destination appears in the footer.
The language preference is saved in `gui_language.json` beside the output files.
Demo calibration lasts only for the current session.

## Composition

`IContourDXFService` defines immutable frame, capture and session DTOs without Qt.
The model delegates to this contract. The controller uses `BackgroundWorker` for
camera lifecycle, preview, processing, calibration persistence and DXF writes.
The view owns Qt widgets and the refresh timer. ApplicationFactory retains the
controller and wires cleanup; shutdown stops refresh and releases the camera.
The standalone host blocks closure during an active capture/calibration/export.

`ContourDXFService` receives camera creation, processing and calibration storage
callbacks from the capture script. `StubContourDXFService` provides synthetic
frames for development. Robot-system composition can supply another adapter;
no paint-specific camera construction is embedded in the view or controller.

## Verification

```bash
QT_QPA_PLATFORM=offscreen .venv/bin/python -m unittest discover -s tests/applications/contour_dxf -v
.venv/bin/python -m unittest tests.engine.test_contour_to_dxf tests.scripts.test_paint_tray_capture_dxf -v
```

Tests exercise capture/calibration/export, rejection, overwrite protection,
initial and runtime translation, numeric editing, disconnect and camera release.
Camera accuracy and touch keyboard placement still need physical station checks.
