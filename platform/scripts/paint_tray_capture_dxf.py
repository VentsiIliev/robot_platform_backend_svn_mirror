#!/usr/bin/env python3
"""Standalone tray-dryer vision capture. No robot connection is started.

Run: .venv/bin/python scripts/paint_tray_capture_dxf.py
The default PyQt6 studio offers capture, reference calibration and explicit DXF
export. --demo previews the GUI without hardware. --opencv keeps the original
capture window, where Capture/Space automatically exports the largest contour. The rotated minimum rectangle is shown
only in the preview and dimension readout for scale verification.
Contours use the paint system's Bezier fitting and millimetre-space smoothing;
--raw-contour disables these stages for comparison.
DXF units are millimetres using the area's saved geometry PPM calibration.
Use --reference-size-mm WIDTH HEIGHT to calibrate scale from a known rectangle.
In the studio, click Measure reference and calibrate; in --opencv mode, the
first capture measures the raw minimum-area rectangle and saves a correction
beside the captures. Remove the reference, then capture parts normally. Saved
corrections apply only to the same area and nominal geometry calibration.
--scale-correction explicitly overrides a saved correction.
--mm-per-pixel can explicitly override the saved scale.
DXF coordinates have their origin at the contour's lower-left, with Y upwards.
"""
from __future__ import annotations

import argparse
import json
from concurrent.futures import ThreadPoolExecutor
from dataclasses import asdict
import hashlib
import os
import tempfile
from datetime import datetime
from pathlib import Path
import sys

_QT_CALLER_ENV = {key: os.environ.get(key) for key in ("QT_QPA_PLATFORM_PLUGIN_PATH", "QT_QPA_FONTDIR")}

import cv2
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.engine.geometry.contour_to_dxf import write_contour_dxf
from src.engine.geometry.rectangle_scale_calibration import calibrate_rectangle_scale

def load_geometry_scale(area, geometry_path=None):
    """Read the same geometry PPM used by the production ppm_anchor strategy."""
    if geometry_path is None:
        data = ROOT / "src/robot_systems/paint_tray_dry/storage/settings/vision/data"
        if area == "paint":
            geometry_path = data / "cameraToRobotMatrix_camera_center_geometry_scale.json"
        elif area == "magazine":
            geometry_path = data / "calibrations/magazine/camera_to_robot_geometry_scale.json"
        else:
            raise ValueError(f"No geometry calibration mapping for {area!r}; use --geometry-scale")
    path = Path(geometry_path)
    payload = json.loads(path.read_text(encoding="utf-8"))
    ppm = float(payload["ppm"])
    if not np.isfinite(ppm) or ppm <= 0:
        raise ValueError(f"Invalid geometry PPM in {path}: {ppm}")
    # ppm already includes the calibration's height correction; do not reapply ppm_scale.
    return 1.0 / ppm, path


def scale_calibration_context(area, mm_per_pixel, geometry_path):
    """Bind a script-local correction to its area and nominal calibration."""
    source = Path(geometry_path).resolve() if geometry_path is not None else None
    return {
        "area": area,
        "base_mm_per_pixel": mm_per_pixel,
        "geometry_source": str(source) if source is not None else None,
        "geometry_sha256": hashlib.sha256(source.read_bytes()).hexdigest() if source is not None else None,
    }


def load_scale_correction(path, context):
    if not path.is_file():
        return 1.0
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict) or payload.get("format") != 1 or payload.get("context") != context:
        raise ValueError("Saved scale calibration does not match this area/geometry; recalibrate or use --scale-correction")
    result = calibrate_rectangle_scale(payload["measured_size_mm"], payload["reference_size_mm"])
    if not np.isclose(float(payload["correction"]), result.correction, rtol=1e-12, atol=0):
        raise ValueError("Saved correction does not match its reference measurements")
    return result.correction


def save_scale_correction(path, context, result):
    """Atomically replace only the standalone capture tool's calibration file."""
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {"format": 1, "context": context,
               "created_at": datetime.now().astimezone().isoformat(), **asdict(result)}
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=path.parent,
                                         prefix=path.name + ".", delete=False) as stream:
            temporary = Path(stream.name)
            json.dump(payload, stream, indent=2)
            stream.write("\n")
        os.replace(temporary, path)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def build_vision(area):
    """Reuse the tray-dryer settings, calibration, ROI and detection pipeline."""
    from src.engine.common_settings_ids import CommonSettingsID
    from src.engine.repositories.settings_service_factory import build_from_specs
    from src.engine.vision.implementation.VisionSystem.VisionSystem import VisionSystem
    from src.engine.vision.implementation.VisionSystem.core.service.internal_service import Service
    from src.engine.vision.vision_service import VisionService
    from src.engine.work_areas.work_area_service import WorkAreaService
    from src.robot_systems.paint_tray_dry.paint_robot_system import TrayDryerPaintRobotSystem

    system = TrayDryerPaintRobotSystem
    settings = build_from_specs(system.settings_specs, system.metadata.settings_root, system)
    areas = WorkAreaService(settings_service=settings, definitions=system.work_areas,
                            default_active_area_id=system.default_active_work_area_id)
    areas.set_active_area_id(area)
    data = system.storage_path("settings", "vision", "data")
    repo = settings.get_repo(CommonSettingsID.VISION_CAMERA_SETTINGS)
    internal = Service(data_storage_path=data, settings_file_path=repo.file_path)
    vision = VisionSystem(storage_path=data, messaging_service=None,
                          service=internal, work_area_service=areas)
    return VisionService(vision, work_area_service=areas)


def smooth_paint_contour(contour, mm_per_pixel):
    """Apply paint's pixel and mm processing stages, returning float pixel XY."""
    from src.robot_systems.paint.processes.paint.plan.paint_contour_interpolation import (
        PaintContourInterpolation,
        PaintContourInterpolationConfig,
        remove_local_hairpin_reversals_xy,
        resample_contour_xy,
        smooth_contour_xy_bounded,
    )

    if not np.isfinite(mm_per_pixel) or mm_per_pixel <= 0:
        raise ValueError("Scale must be finite and positive")
    xy = np.asarray(contour, dtype=float).reshape(-1, 2)
    poses = np.column_stack((xy, np.zeros((len(xy), 4)))).tolist()
    # Match _paint_source_contour_processor in paint/application_wiring.py.
    fitted = PaintContourInterpolation(PaintContourInterpolationConfig(
        units="px", fit_sample_spacing=1.0, output_spacing=1.0,
    )).build(poses, include_debug_paths=False)
    mm_xy = np.asarray(fitted.execution_path, dtype=float)[:, :2] * mm_per_pixel
    # Match _paint_mm_contour_processor; distance parameters here are in mm.
    mm_xy = resample_contour_xy(mm_xy, spacing=1.0, closed=True)
    mm_xy = remove_local_hairpin_reversals_xy(mm_xy, spacing=1.0, closed=True)
    mm_xy = smooth_contour_xy_bounded(
        mm_xy, max_deviation_mm=0.50, corner_threshold_deg=45.0, passes=20,
    )
    if len(mm_xy) < 3 or not np.isfinite(mm_xy).all():
        raise ValueError("Paint interpolation produced an invalid contour")
    return mm_xy / mm_per_pixel


def capture_geometry(vision, mm_per_pixel, smooth=True):
    """Capture, optionally smooth, then measure and preview the exported contour."""
    frame, contours = vision.compute_contours_for_latest_frame()
    if frame is None:
        raise ValueError("No camera frame available")
    valid = [np.asarray(c, dtype=np.float32).reshape(-1, 1, 2) for c in contours
             if np.asarray(c).size >= 6]
    valid = [c for c in valid if np.isfinite(c).all() and cv2.contourArea(c) > 0]
    if not valid:
        raise ValueError("No contour detected in the configured ROI")
    contour = max(valid, key=cv2.contourArea)
    if smooth:
        contour = smooth_paint_contour(contour, mm_per_pixel)
    contour = np.asarray(contour, dtype=np.float32).reshape(-1, 1, 2)
    if cv2.contourArea(contour) <= 0:
        raise ValueError("Processed contour has no area")
    rect = cv2.minAreaRect(contour)
    box = cv2.boxPoints(rect)
    preview = frame.copy()
    cv2.drawContours(preview, [np.rint(contour).astype(np.int32)], -1, (0, 220, 0), 2)
    cv2.polylines(preview, [np.rint(box).astype(np.int32)], True, (0, 200, 255), 2)
    return preview, contour.reshape(-1, 2), box, rect[1]


class CaptureWindow:
    """Small OpenCV GUI: live feed, frozen result and clickable capture button."""

    name = "Paint tray dry - contour to DXF"

    def __init__(self):
        self.requested = False

    def mouse(self, event, x, y, flags, userdata):
        if event == cv2.EVENT_LBUTTONUP and 10 <= x <= 190 and 10 <= y <= 55:
            self.requested = True

    @staticmethod
    def panel(frame):
        canvas = np.zeros((450, 640, 3), np.uint8)
        if frame is not None:
            h, w = frame.shape[:2]
            factor = min(640 / w, 450 / h)
            resized = cv2.resize(frame, (max(1, round(w * factor)), max(1, round(h * factor))))
            if resized.ndim == 2:
                resized = cv2.cvtColor(resized, cv2.COLOR_GRAY2BGR)
            rh, rw = resized.shape[:2]
            canvas[:rh, :rw] = resized
        return canvas

    def draw(self, live, captured, status, busy):
        from pl_gui.settings.settings_view.styles import PRIMARY

        canvas = np.zeros((555, 1280, 3), np.uint8)
        accent = tuple(int(PRIMARY.lstrip("#")[i:i + 2], 16) for i in (4, 2, 0))
        cv2.rectangle(canvas, (10, 10), (190, 55), accent, -1)
        cv2.putText(canvas, "Working..." if busy else "Capture [Space]", (20, 40),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
        cv2.putText(canvas, "LIVE                      CAPTURE: green contour / yellow rectangle",
                    (210, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
        canvas[65:515, :640] = self.panel(live)
        canvas[65:515, 640:] = self.panel(captured)
        cv2.putText(canvas, status[:145], (10, 542), cv2.FONT_HERSHEY_SIMPLEX,
                    0.5, (255, 255, 255), 1)
        cv2.imshow(self.name, canvas)


def prepare_gui_environment():
    """Restore the caller's Qt 6 plugin settings after OpenCV imports Qt 5."""
    for key, value in _QT_CALLER_ENV.items():
        if value is None:
            os.environ.pop(key, None)
        else:
            os.environ[key] = value


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--area", default="paint", help="Configured work area (default: paint)")
    parser.add_argument("--output-dir", type=Path)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--opencv", action="store_true", help="Use the original OpenCV capture window")
    mode.add_argument("--demo", action="store_true", help="Preview the PyQt6 studio without camera or robot")
    parser.add_argument("--raw-contour", action="store_true", help="Skip paint interpolation and smoothing")
    scale_options = parser.add_mutually_exclusive_group()
    scale_options.add_argument("--mm-per-pixel", type=float, help="Override the saved geometry scale")
    scale_options.add_argument("--geometry-scale", type=Path, help="Override the area's geometry-scale JSON path")
    parser.add_argument("--scale-correction", type=float, help="Explicit correction, overriding saved calibration")
    parser.add_argument("--reference-size-mm", type=float, nargs=2, metavar=("WIDTH", "HEIGHT"),
                        help="Prefill reference dimensions (first capture calibrates in --opencv mode)")
    parser.add_argument("--scale-calibration", type=Path, help="Script-local calibration JSON (default: beside captures)")
    parser.add_argument("--max-calibration-error-percent", type=float, default=2.0,
                        help="Maximum residual per reference side after uniform correction (default: 2%%)")
    args = parser.parse_args()
    args.output_dir = args.output_dir or ROOT / "captures" / ("contour_dxf_demo" if args.demo else "paint_tray_dry")
    if not np.isfinite(args.max_calibration_error_percent) or args.max_calibration_error_percent <= 0:
        parser.error("--max-calibration-error-percent must be finite and positive")
    if args.mm_per_pixel is not None and (not np.isfinite(args.mm_per_pixel) or args.mm_per_pixel <= 0):
        parser.error("--mm-per-pixel must be finite and positive")
    if args.scale_correction is not None and (not np.isfinite(args.scale_correction) or args.scale_correction <= 0):
        parser.error("--scale-correction must be finite and positive")
    if args.reference_size_mm is not None:
        if args.scale_correction is not None:
            parser.error("Reference calibration cannot be combined with --scale-correction")
        if any(not np.isfinite(value) or value <= 0 for value in args.reference_size_mm):
            parser.error("Reference dimensions must be finite and positive")
    if args.demo:
        prepare_gui_environment()
        from src.applications.contour_dxf.service.stub_contour_dxf_service import StubContourDXFService
        from src.applications.contour_dxf.standalone import run_standalone
        return run_standalone(StubContourDXFService(args.output_dir),
                              args.reference_size_mm or (120, 100), args.max_calibration_error_percent, not args.raw_contour)
    try:
        if args.mm_per_pixel is None:
            scale, source = load_geometry_scale(args.area, args.geometry_scale)
            print(f"Geometry PPM: {1 / scale:.9f} px/mm ({scale:.9f} mm/px) | {source}", flush=True)
        else:
            source = None
            scale = args.mm_per_pixel
            print(f"Manual scale: {scale:.9f} mm/px", flush=True)
    except (OSError, ValueError, KeyError, TypeError) as exc:
        parser.error(f"Cannot load geometry scale: {exc}")
    base_scale = scale
    calibration_path = args.scale_calibration or args.output_dir / f"scale_calibration_{args.area}.json"
    if source is not None and calibration_path.resolve() == Path(source).resolve():
        parser.error("Capture correction file must differ from the saved geometry calibration")
    reference_pending = args.reference_size_mm is not None
    try:
        context = scale_calibration_context(args.area, base_scale, source)
        correction = (1.0 if reference_pending and args.opencv else args.scale_correction
                      if args.scale_correction is not None else load_scale_correction(calibration_path, context))
    except (OSError, ValueError, KeyError, TypeError) as exc:
        parser.error(f"Cannot load script scale calibration: {exc}")
    scale *= correction
    print(f"Script correction: {correction:.9f} | Effective PPM: {1 / scale:.9f} px/mm", flush=True)
    if reference_pending:
        print(f"Place the {args.reference_size_mm[0]:g} x {args.reference_size_mm[1]:g} mm reference at the capture height, then measure the reference to calibrate.", flush=True)
    print("Contour: " + ("raw" if args.raw_contour else "paint Bezier + 1 mm resampling + bounded smoothing"), flush=True)
    if not args.opencv:
        prepare_gui_environment()
        from functools import partial
        from src.applications.contour_dxf.service.contour_dxf_service import ContourDXFService
        from src.applications.contour_dxf.standalone import run_standalone
        service = ContourDXFService(
            partial(build_vision, args.area), capture_geometry, partial(save_scale_correction, calibration_path, context),
            source=f"paint_tray_dry / {args.area}", base_scale=base_scale, correction=correction,
            output_dir=args.output_dir, calibration_path=calibration_path)
        return run_standalone(service, args.reference_size_mm or (120, 100),
                              args.max_calibration_error_percent, not args.raw_contour)
    vision = build_vision(args.area)
    window = CaptureWindow()
    captured = pending = None
    status = ("Place the known rectangle and Capture to calibrate scale." if reference_pending else
              "Waiting for camera. Capture saves DXF automatically. Esc/Q closes.")
    try:
        vision.start()
        cv2.namedWindow(window.name, cv2.WINDOW_AUTOSIZE)
        cv2.setMouseCallback(window.name, window.mouse)
        with ThreadPoolExecutor(max_workers=1) as worker:
            while True:
                if pending is not None and pending.done():
                    try:
                        captured, contour, box, size = pending.result()
                        if reference_pending:
                            measured = (float(size[0]) * base_scale, float(size[1]) * base_scale)
                            result = calibrate_rectangle_scale(measured, args.reference_size_mm)
                            if max(abs(error) for error in result.residual_percent) > args.max_calibration_error_percent:
                                raise ValueError(f"Reference sides disagree after uniform correction: {result.residual_percent}%; check reference/geometry")
                            save_scale_correction(calibration_path, context, result)
                            scale = base_scale * result.correction
                            reference_pending = False
                            residual = result.residual_mm
                            status = (f"Calibrated x{result.correction:.6f}; errors {residual[0]:+.2f}/{residual[1]:+.2f} mm. "
                                      "Remove reference, then Capture parts.")
                            print(f"{status}\nMeasured: {result.measured_size_mm} mm; reference: {result.reference_size_mm} mm\n{calibration_path}", flush=True)
                        else:
                            path = args.output_dir / (datetime.now().strftime("capture_%Y%m%d_%H%M%S_%f") + ".dxf")
                            write_contour_dxf(path, contour, scale)
                            status = f"{size[0] * scale:.2f} x {size[1] * scale:.2f} mm | Saved {path.name}"
                            print(f"{status}\n{path}", flush=True)
                    except Exception as exc:
                        status = f"Capture/export failed: {exc}"
                        print(status, file=sys.stderr, flush=True)
                    pending = None
                if window.requested:
                    window.requested = False
                    if pending is None:
                        pending = worker.submit(capture_geometry, vision, scale, not args.raw_contour and not reference_pending)
                        status = ("Measuring raw reference rectangle..." if reference_pending else
                                  "Detecting contour..." if args.raw_contour else "Detecting and smoothing contour...")
                window.draw(vision.get_latest_frame(), captured, status, pending is not None)
                key = cv2.waitKey(30) & 0xFF
                if key in (27, ord("q")) or cv2.getWindowProperty(window.name, cv2.WND_PROP_VISIBLE) < 1:
                    break
                if key in (32, ord("c")):
                    window.requested = True
    finally:
        vision.stop()
        cv2.destroyAllWindows()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
