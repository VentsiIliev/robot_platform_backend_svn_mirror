"""Numerical comparison of conversion and fitting, without changing either."""
import numpy as np
from .decompose import sample_primitive


def compare_conversion(pixel_points, robot_points):
    """Measure departure from a best-fit similarity (reflection allowed).

    A nonzero residual can be legitimate calibration distortion, not an error.
    Corresponding points must be in their original order.
    """
    source = np.asarray(pixel_points, float)
    target = np.asarray(robot_points, float)
    a, b = source-source.mean(0), target-target.mean(0)
    denominator = float(np.sum(a*a))
    if denominator <= 1e-12:
        return {"status": "degenerate"}
    u, singular, vt = np.linalg.svd(a.T @ b)
    rotation = u @ vt
    scale = float(singular.sum()/denominator)
    residual = np.linalg.norm(a @ rotation * scale-b, axis=1)
    return {"similarity_scale_mm_per_pixel": scale,
            "reflection": bool(np.linalg.det(rotation) < 0),
            "similarity_rms_residual_mm": float(np.sqrt(np.mean(residual**2))),
            "similarity_max_residual_mm": float(residual.max())}


def compare_fit(points, primitives):
    """Distances to sampled finite primitive segments, plus cyclic join gaps."""
    if not primitives:
        return {}
    points = np.asarray(points, float)
    sampled = [sample_primitive(p, step=0.1) for p in primitives]
    starts = np.vstack([p[:-1] for p in sampled])
    ends = np.vstack([p[1:] for p in sampled])
    vectors = ends-starts
    squared = np.maximum(np.sum(vectors*vectors, axis=1), 1e-20)
    distances = []
    for start in range(0, len(points), 64):
        delta = points[start:start+64, None, :]-starts
        t = np.clip(np.sum(delta*vectors, axis=2)/squared, 0, 1)
        distances.extend(np.sqrt(np.min(np.sum((delta-t[..., None]*vectors)**2, axis=2), axis=1)))
    gaps = [float(np.linalg.norm(p[-1]-sampled[(i+1)%len(sampled)][0]))
            for i,p in enumerate(sampled)]
    return {"original_to_fit_mean_mm": float(np.mean(distances)),
            "original_to_fit_max_mm": float(np.max(distances)),
            "original_to_fit_p95_mm": float(np.percentile(distances, 95)),
            "join_gaps_mm": gaps, "max_join_gap_mm": max(gaps),
            "distance_method": "point to primitive polyline segments sampled at 0.1 mm"}
