"""Rank a saved test library by contour descriptors, then verify top-K results.

Example (read-only library, reusable descriptor cache in /tmp):
  .venv/bin/python scripts/workpiece_descriptor_probe.py \
    --root "$HOME/Downloads/workpiece-benchmark-100000" \
    --cache /tmp/workpiece-descriptors-100000.npz --query-indices 0

Preparation and cache loading are timed separately from steady-state queries.
"""
from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path
from time import perf_counter

import cv2
import numpy as np

from workpiece_index_probe import GeometricMatchingStrategy, progress, read_contour


def descriptor(contour):
    """Arc-length-sampled centroid radii; FFT magnitudes ignore start and direction.

    A rotation preserves radii, a reflection reverses their order, and a change
    of contour starting point shifts them. Fourier magnitudes suppress these
    differences. Sampling makes the representation approximate, not a recall bound.
    """
    points = np.asarray(contour, dtype=np.float64).reshape(-1, 2)
    following = np.roll(points, -1, axis=0)
    lengths = np.linalg.norm(following - points, axis=1)
    keep = lengths > 1e-9
    points, following, lengths = points[keep], following[keep], lengths[keep]
    cumulative = np.concatenate([[0], np.cumsum(lengths)])
    positions = np.arange(256) * cumulative[-1] / 256
    edges = np.minimum(np.searchsorted(cumulative, positions, side="right") - 1, len(points) - 1)
    fractions = (positions - cumulative[edges]) / lengths[edges]
    sampled = points[edges] + (following[edges] - points[edges]) * fractions[:, None]
    moments = cv2.moments(contour)
    center = np.array([moments["m10"], moments["m01"]]) / moments["m00"]
    radii = np.linalg.norm(sampled - center, axis=1)
    spectrum = np.abs(np.fft.rfft(radii)) / radii.sum()
    return spectrum[1:25].astype(np.float32)


def load_library(root, cache):
    started = perf_counter()
    if cache.exists():
        with np.load(cache, allow_pickle=False) as saved:
            if int(saved["version"]) != 1 or str(saved["root"]) != str(root):
                raise ValueError("Descriptor cache belongs to another library/version; choose a new --cache")
            paths = saved["paths"].tolist()
            areas = saved["areas"]
            vectors = saved["vectors"]
        progress(f"Loaded {len(paths):,} cached descriptors in {perf_counter() - started:.2f}s")
        return paths, areas, vectors, 0.0, perf_counter() - started
    if (root / ".probe-incomplete").exists():
        raise ValueError("Library preparation is incomplete")
    paths = sorted(str(path) for path in root.rglob("*_workpiece.json")
                   if not any(part.startswith(".") for part in path.relative_to(root).parts)
                   and not (path.parent / ".incomplete").exists())
    if not paths:
        raise ValueError("No published workpieces found")
    areas = np.empty(len(paths), dtype=np.float64)
    vectors = np.empty((len(paths), 24), dtype=np.float32)
    for index, path in enumerate(paths):
        contour = read_contour(Path(path))
        areas[index] = cv2.contourArea(contour)
        vectors[index] = descriptor(contour)
        if (index + 1) % 10000 == 0:
            progress(f"Prepared {index + 1:,}/{len(paths):,} descriptors in {perf_counter() - started:.1f}s")
    with tempfile.TemporaryDirectory(prefix=".descriptor-build-", dir=cache.parent) as staging:
        target = Path(staging) / "descriptors.npz"
        np.savez(target, version=1, root=str(root), paths=np.asarray(paths), areas=areas, vectors=vectors)
        target.replace(cache)
    elapsed = perf_counter() - started
    progress(f"Saved descriptor cache: {cache} ({elapsed:.2f}s)")
    return paths, areas, vectors, elapsed, 0.0


def rank(areas, vectors, query, limit):
    area = cv2.contourArea(query)
    eligible = np.flatnonzero((areas >= area * 0.80 - area * 1e-6) &
                             (areas <= area / 0.80 + area * 1e-6))
    shape_distance = np.linalg.norm(vectors[eligible] - descriptor(query), axis=1)
    # Approximate both the size agreement and normalized shape overlap used by
    # the expensive matcher. This weight is experimental and must be validated.
    distance = np.maximum(np.abs(np.log(areas[eligible] / area)), 4 * shape_distance)
    order = np.argsort(distance, kind="stable")[:limit]
    return eligible[order], len(eligible)


def exact_scores(paths, indices, query, matcher):
    scores = {}
    for offset, index in enumerate(sorted(indices), 1):
        scores[int(index)] = matcher._getSimilarity(read_contour(Path(paths[index])), query)
        if offset % 10000 == 0:
            progress(f"  Full baseline scored {offset:,}/{len(indices):,}")
    return scores


def best_result(scores, threshold):
    accepted = {index: value for index, value in scores.items() if value > threshold}
    best = max(accepted, key=accepted.get) if accepted else None
    return best, accepted.get(best, 0.0), set(accepted)


def run(args):
    startup = perf_counter()
    root, cache = args.root.resolve(), args.cache.resolve()
    paths, areas, vectors, build_seconds, load_seconds = load_library(root, cache)
    if max(args.query_indices) >= len(paths):
        raise ValueError("Query index exceeds library size")
    startup_seconds = perf_counter() - startup
    matcher = GeometricMatchingStrategy()
    threshold = matcher.similarity_threshold * 100
    reports = []
    for source in args.query_indices:
        original = read_contour(Path(paths[source])).reshape(-1, 2)
        for label, angle, reflection, scale in [
            ("rotated", 37, 1, 1), ("reflected", 123, -1, 1),
            ("scaled_5_percent", 71, 1, 1.05),
        ]:
            if label not in args.variants:
                continue
            radians = np.deg2rad(angle)
            rotation = np.array([[np.cos(radians), -np.sin(radians)],
                                 [np.sin(radians), np.cos(radians)]])
            query = ((original * [reflection, 1]) @ rotation.T * scale + [200, 350]).astype(np.float32).reshape(-1, 1, 2)
            progress(f"{Path(paths[source]).name} / {label}: ranking and scoring top {args.top_k}")
            # Measure complete independent top-K query paths BEFORE the baseline;
            # each includes descriptor extraction, ranking, JSON reads, and scoring.
            ranked_results = []
            for limit in args.top_k:
                started = perf_counter()
                indices, eligible = rank(areas, vectors, query, limit)
                ranking_seconds = perf_counter() - started
                scores = exact_scores(paths, indices, query, matcher)
                elapsed = perf_counter() - started
                best, confidence, accepted = best_result(scores, threshold)
                ranked_results.append((limit, indices, best, confidence, accepted, ranking_seconds, elapsed))
                progress(f"  Top {limit}: {elapsed:.3f}s including ranking ({ranking_seconds:.3f}s)")
            full, full_seconds = {}, None
            if not args.query_only:
                progress(f"  Computing full-scan reference for {len(paths):,} workpieces...")
                started = perf_counter()
                full = exact_scores(paths, range(len(paths)), query, matcher)
                full_seconds = perf_counter() - started
            full_best, full_confidence, full_accepted = best_result(full, threshold)
            for limit, indices, best, confidence, accepted, ranking_seconds, elapsed in ranked_results:
                result = {"source": Path(paths[source]).name, "variant": label,
                          "total": len(paths), "area_candidates": eligible, "top_k": limit,
                          "scored_candidates": len(indices), "ranking_seconds": round(ranking_seconds, 5),
                          "query_seconds": round(elapsed, 5),
                          "full_seconds": round(full_seconds, 5) if full_seconds is not None else None,
                          "reference_checked": not args.query_only,
                          "same_best": best == full_best if not args.query_only else None,
                          "same_best_score": abs(confidence - full_confidence) < 1e-6 if not args.query_only else None,
                          "full_best_retained": (full_best is None or full_best in indices) if not args.query_only else None,
                          "full_best": Path(paths[full_best]).name if full_best is not None else None,
                          "ranked_best": Path(paths[best]).name if best is not None else None,
                          "full_best_score": full_confidence if not args.query_only else None,
                          "ranked_best_score": confidence,
                          "full_accepted_matches": len(full_accepted) if not args.query_only else None,
                          "accepted_matches_outside_top_k": len(full_accepted - accepted) if not args.query_only else None}
                reports.append(result)
                if not args.query_only:
                    progress(f"  Top {limit}: same best={result['same_best']}, "
                             f"score gap={full_confidence - confidence:.5f}")
    print(json.dumps({"cache": str(cache), "build_seconds": build_seconds,
                      "cache_load_seconds": load_seconds, "startup_seconds": startup_seconds,
                      "results": reports}, indent=2))
    return 1 if any(result["same_best"] is False for result in reports) else 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, required=True, help="Immutable saved workpiece library (read only)")
    parser.add_argument("--cache", type=Path, required=True, help="Reusable descriptor NPZ file; parent must exist")
    parser.add_argument("--query-indices", nargs="+", type=int, default=list(range(9)), help="Zero-based sorted library records")
    parser.add_argument("--top-k", nargs="+", type=int, default=[20, 50])
    parser.add_argument("--query-only", action="store_true", help="Skip slow full-scan validation; report correctness as unverified")
    parser.add_argument("--variants", nargs="+", choices=("rotated", "reflected", "scaled_5_percent"),
                        default=["rotated", "reflected", "scaled_5_percent"])
    arguments = parser.parse_args()
    if min(arguments.top_k) < 1 or min(arguments.query_indices) < 0:
        parser.error("Top-K must be positive and query indices nonnegative")
    raise SystemExit(run(arguments))
