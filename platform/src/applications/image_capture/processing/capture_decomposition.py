"""Run the supplied decomposition on captured points, with no files or GUI calls."""
import json

import cv2
import numpy as np

from . import decompose
from .decompose_contour import default_params, decompose_points


def decompose_capture(frame, contours):
    """Return JSON bytes, overlay pixels and counts for all contours in source order.

    Keep per-contour errors in the result so the original image/contour pair can
    still be saved for investigating a contour the supplied algorithm rejects.
    """
    params = default_params()
    results, raw_paths, primitives = [], [], []
    failed = 0
    for index, contour in enumerate(contours):
        try:
            raw, _processed, fitted, stats = decompose_points(contour, params)
            result = {"contour_index": index, "status": "ok", "primitives": fitted, "stats": stats}
            # Reject non-finite numerical fits before displaying/saving them.
            json.dumps(result, allow_nan=False)
            results.append(result)
            raw_paths.append(raw)
            primitives.extend(fitted)
        except (ValueError, ArithmeticError, np.linalg.LinAlgError, cv2.error) as exc:
            failed += 1
            results.append({"contour_index": index, "status": "error", "error": str(exc),
                            "primitives": [], "stats": {}})
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    raw = np.vstack(raw_paths) if raw_paths else np.empty((0, 2))
    overlay = decompose.draw_overlay(gray, raw, primitives, scale=1)
    counts = {
        "lines": sum(p["type"] == "line" for p in primitives),
        "arcs": sum(p["type"] == "arc" for p in primitives),
        "exceeds_tolerance": sum(not p["within_tol"] for p in primitives),
        "failed_contours": failed,
    }
    document = {
        "schema_version": 1,
        "coordinate_space": "calibrated_image_pixels",
        "params": vars(params),
        "contours": results,
        "summary": counts,
    }
    return json.dumps(document, indent=2, allow_nan=False).encode("utf-8"), overlay, counts
