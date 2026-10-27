from __future__ import annotations

import copy

import numpy as np
from scipy.optimize import least_squares
from scipy.spatial import cKDTree


class PaintCaptureContourPreparation:
    """Build editable prepared geometry without paint-contact projection or motion."""

    def __init__(self, path_preparation_service):
        self._preparation = path_preparation_service

    def __call__(self, workpiece: dict) -> dict:
        result = copy.deepcopy(workpiece)
        if result.get("paint_contour_prepared"):
            return result
        # A separate preparation service keeps capture work independent of the
        # execution runtime and its active plan. This plan stops before RTCP.
        plan = self._preparation.build_execution_plan(copy.deepcopy(workpiece), skip_debug_plot=True)
        paths = []
        for pixels, raw, prepared in zip(plan.raw_pixel_paths, plan.raw_paths, plan.prepared_paths):
            source_px = np.asarray(pixels, dtype=float)[:, :2]
            source_mm = np.asarray(raw, dtype=float)[:, :2]
            prepared_mm = np.asarray(prepared, dtype=float)[:, :2]
            paths.append(self._to_pixels(source_px, source_mm, prepared_mm, workpiece).tolist())
        if len(paths) != 1 or len(paths[0]) < 3:
            raise ValueError("Capture must produce one complete workpiece contour.")
        result.setdefault("matchingContour", copy.deepcopy(workpiece["contour"]))
        result["contour"] = paths[0]
        result["paint_contour_prepared"] = True
        # A complete Paint copy is a selection source, not an independently
        # drawn paint section. Keep it in sync with the editable boundary.
        for section in (result.get("sprayPattern") or {}).get("Contour", []):
            if (section.get("settings") or {}).get("paint_selection_source"):
                section["contour"] = copy.deepcopy(paths[0])
        return result

    def _to_pixels(self, source_px, source_mm, prepared_mm, settings):
        # Geometry-PPM conversion is affine about the contour's own anchor.
        # Recover its exact inverse from the paired points; a homography inverse
        # would lose the PPM scale, target offsets and height compensation.
        center = source_mm.mean(axis=0)
        design = np.column_stack((source_mm - center, np.ones(len(source_mm))))
        inverse, _, rank, _ = np.linalg.lstsq(design, source_px, rcond=None)
        if rank < 3:
            raise ValueError("Captured contour has no usable two-dimensional area.")
        if np.max(np.linalg.norm(design @ inverse - source_px, axis=1)) < 1e-6:
            return np.column_stack((prepared_mm - center, np.ones(len(prepared_mm)))) @ inverse

        # Residual calibration can be nonlinear. Invert the actual calibrated
        # converter locally, starting at the closest source point, rather than
        # drawing an approximate contour with the wrong calibration.
        tree = cKDTree(source_mm)
        _, indices = tree.query(prepared_mm)
        output = []
        for target, index in zip(prepared_mm, indices):
            def residual(pixel):
                converted = self._preparation.convert_contour_to_robot([pixel], settings)
                return np.asarray(converted["poses"][0][:2]) - target

            result = least_squares(residual, source_px[index], diff_step=1e-3, max_nfev=30)
            if not result.success or np.linalg.norm(result.fun) > 1e-4:
                raise ValueError("Could not map the processed contour back to the camera image.")
            output.append(result.x)
        return np.asarray(output, dtype=float)
