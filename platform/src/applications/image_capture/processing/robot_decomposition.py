"""Fit converted robot XY contours, and render them using an equal-scale XY plot."""
import json

import cv2
import numpy as np

from .decompose_contour import default_params, decompose_points
from .decompose import sample_primitive
from .comparison import compare_conversion, compare_fit
from .connected_fit import connect_primitives, scale_primitives, refit_original_contour


def build_robot_result(contours, converter, work_area_id):
    params = default_params()
    entries = []
    for index, contour in enumerate(contours):
        converted = converter(contour)
        poses = np.asarray(converted.pop("poses"), dtype=float)
        if poses.shape != (len(contour), 6) or not np.isfinite(poses).all():
            raise ValueError("Robot-space conversion returned invalid poses.")
        points = poses[:, :2]
        entry = {"contour_index": index, "points": points.tolist(), "poses": poses.tolist(),
                 "conversion": converted, "conversion_comparison": compare_conversion(contour, points)}
        try:
            comparison = entry["conversion_comparison"]
            scale = comparison.get("similarity_scale_mm_per_pixel", 0.0)
            if not np.isfinite(scale) or scale <= 1e-9:
                raise ValueError("Cannot derive a physical parameter scale for this contour.")
            origin = points.mean(0)
            # Fit robot geometry in pixel-equivalent units. This scales ALL
            # length-based operations, including the wrapper's cleaning and
            # initial sampling. Sigma remains a number of samples.
            raw, processed, fitted, _ = decompose_points((points-origin)/scale, params)
            independent = scale_primitives(fitted, scale, origin)
            connected = connect_primitives(processed, fitted, params.tol)
            before_refinement = scale_primitives(connected, scale, origin)
            refined = refit_original_contour((points-origin)/scale, processed, fitted, params.tol)
            primitives = scale_primitives(refined, scale, origin)
            tolerance = params.tol*scale
            stats = compare_fit(points, primitives)
            json.dumps({"primitives": primitives, "stats": stats}, allow_nan=False)
            entry.update(status="ok", primitives=primitives, stats=stats,
                         independent_primitives=independent,
                         before_refinement_comparison=compare_fit(points, before_refinement),
                         acceptance_basis="maximum distance of assigned original vertices to finite primitives",
                         max_assigned_original_error_mm=max((p['max_err'] for p in primitives), default=0.0),
                         independent_fit_comparison=compare_fit(points, independent),
                         fit_comparison=stats,
                         tolerance_mm=tolerance,
                         parameter_scale_mm_per_pixel=scale,
                         sampling_step_mm=params.step*scale,
                         continuity="shared endpoints; tangency not constrained")
        except (ValueError, ArithmeticError, np.linalg.LinAlgError, cv2.error) as exc:
            entry.update(status="error", error=str(exc), primitives=[], stats={})
        entries.append(entry)
    document = {"schema_version": 1, "coordinate_space": "robot_xy_mm", "units": "mm",
                "work_area_id": work_area_id, "pixel_equivalent_params": vars(params),
                "experiment": "scaled parameters and original-vertex-validated adaptive refit",
                "height_mm": 0.0, "contours": entries,
                "stage": "detected contour converted before paint path smoothing"}
    return json.dumps(document, indent=2, allow_nan=False).encode(), render_robot_plot(entries)


def render_robot_plot(entries):
    canvas = np.full((700, 1000, 3), 248, np.uint8)
    paths = []
    for entry in entries:
        paths.append((np.asarray(entry['points']), (130, 130, 130), True))
        for primitive in entry['primitives']:
            paths.append((sample_primitive(primitive),
                          (0, 0, 220) if primitive['type'] == 'line' else (220, 110, 0), False))
    cv2.putText(canvas, 'Robot XY (mm): detected = gray, lines = red, arcs = blue',
                (30, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (35, 35, 35), 1, cv2.LINE_AA)
    failed = sum(e['status'] != 'ok' for e in entries)
    exceeded = sum(not p['within_tol'] for e in entries for p in e['primitives'])
    cv2.putText(canvas, f'Scaled pixel tolerance; outside tolerance: {exceeded}; failed contours: {failed}',
                (30, 58), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (35, 35, 35), 1, cv2.LINE_AA)
    if not paths:
        return canvas
    all_points = np.vstack([p for p, _, _ in paths])
    low, high = all_points.min(0), all_points.max(0)
    extent = np.maximum(high-low, 1e-6)
    scale = min(850/extent[0], 540/extent[1])
    center = (low+high)/2
    for points, color, closed in paths:
        display = (points-center)*[scale, -scale]+[520, 340]
        cv2.polylines(canvas, [np.rint(display).astype(np.int32).reshape(-1, 1, 2)],
                      closed, color, 2, cv2.LINE_AA)
    cv2.putText(canvas, f'X: {low[0]:.3f} .. {high[0]:.3f} mm   Y: {low[1]:.3f} .. {high[1]:.3f} mm',
                (30, 650), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (35, 35, 35), 1, cv2.LINE_AA)
    cv2.putText(canvas, 'Equal XY scale; +X right, +Y up', (30, 680),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (35, 35, 35), 1, cv2.LINE_AA)
    return canvas
