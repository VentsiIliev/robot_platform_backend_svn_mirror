"""Isolated, read-only workpiece-index experiment; no robot runtime is started.

Run with .venv/bin/python scripts/workpiece_index_probe.py
or add --root /path/to/workpieces --queries 3 for a real-library smoke test.
Use --save-library PATH with --generated-count to prepare a persistent library;
later use --root PATH to reuse its JSON files and completed index.
Coordinates retain their original units; no millimetre calibration is assumed.
"""
from __future__ import annotations

import argparse
import json
import random
import shutil
import sqlite3
import sys
import tempfile
from pathlib import Path
from time import perf_counter

import cv2
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.engine.vision.implementation.VisionSystem.features.contour_matching.matching.strategies.geometric_matching_strategy import GeometricMatchingStrategy


def progress(message):
    """Keep progress visible immediately while leaving stdout for JSON results."""
    print(message, file=sys.stderr, flush=True)


def read_contour(path):
    raw = json.loads(path.read_text(encoding="utf-8"))
    points = raw.get("matchingContour")
    if points is None:
        points = raw.get("contour", [])
    if isinstance(points, dict):
        points = points.get("contour", [])
    contour = np.asarray(points, dtype=np.float32).reshape(-1, 1, 2)
    if len(contour) < 3 or not np.isfinite(contour).all():
        raise ValueError("Contour must contain at least three finite points")
    if cv2.contourArea(contour) <= 0:
        raise ValueError("Contour area must be positive")
    return contour


def build_index(connection, paths):
    connection.executescript("""
        CREATE TABLE features(path TEXT PRIMARY KEY, area REAL, short_side REAL, long_side REAL,
                              perimeter REAL, solidity REAL, vertices INTEGER);
        CREATE INDEX by_area ON features(area);
        PRAGMA user_version = 2;
    """)
    for index, path in enumerate(paths, 1):
        contour = read_contour(path)
        short, long = sorted(cv2.minAreaRect(contour)[1])
        area = cv2.contourArea(contour)
        perimeter = cv2.arcLength(contour, True)
        hull_area = cv2.contourArea(cv2.convexHull(contour))
        vertices = len(cv2.approxPolyDP(contour, 0.02 * perimeter, True))
        connection.execute("INSERT INTO features VALUES (?, ?, ?, ?, ?, ?, ?)",
                           (str(path), area, short, long, perimeter, area / hull_area, vertices))
        if index % 10000 == 0:
            progress(f"Indexed {index:,}/{len(paths):,}")
    connection.commit()


def candidate_paths(connection, query, filter_name):
    """Experimental gates; full-scan comparison measures their recall, not proof."""
    area = cv2.contourArea(query)
    bounds = [area * 0.80 - area * 1e-6, area / 0.80 + area * 1e-6]
    where = "area BETWEEN ? AND ?"
    area_count = connection.execute(f"SELECT COUNT(*) FROM features WHERE {where}", bounds).fetchone()[0]
    if filter_name == "geometry":
        short, long = sorted(cv2.minAreaRect(query)[1])
        perimeter = cv2.arcLength(query, True)
        solidity = area / cv2.contourArea(cv2.convexHull(query))
        vertices = len(cv2.approxPolyDP(query, 0.02 * perimeter, True))
        # Dimension/perimeter ratios and solidity are empirical hypotheses.
        # Vertex ratio mirrors the existing matcher's gate (with roundoff slack).
        for column, value, ratio in [("short_side", short, 0.75),
                                     ("long_side", long, 0.75),
                                     ("perimeter", perimeter, 0.80),
                                     ("vertices", vertices, 0.70)]:
            where += f" AND {column} BETWEEN ? AND ?"
            bounds.extend([value * ratio - 1e-5, value / ratio + 1e-5])
        where += " AND solidity BETWEEN ? AND ?"
        bounds.extend([solidity - 0.12, solidity + 0.12])
    rows = connection.execute(f"SELECT path FROM features WHERE {where} ORDER BY path", bounds).fetchall()
    return [Path(row[0]) for row in rows], area_count


def synthetic_library(root):
    # Different sizes and aspect ratios, with intermediate vertices to satisfy
    # the current matcher's minimum contour length.
    paths = []
    for index in range(16):
        width, height = 35 + index * 14, 55 + index * 9
        points = [[0, 0], [width / 2, 0], [width, 0], [width, height / 2],
                  [width, height], [width / 2, height], [0, height], [0, height / 2]]
        path = root / f"{index}_workpiece.json"
        path.write_text(json.dumps({"matchingContour": points}), encoding="utf-8")
        paths.append(path)
    return paths


def generated_library(root, count):
    """Stream the existing generator's shapes into sharded benchmark JSON files.

    Avoid its all-in-memory manifest when preparing very large libraries.
    The completion marker is written only after every JSON file is published.
    """
    from dataclasses import replace
    from src.robot_systems.paint.scripts.generate_dry_run_dataset import (
        build_config, _choose_dimensions, _generate_item, _validate_config,
    )

    config = replace(build_config(), output_root=root / "datasets",
                     dataset_id="index-benchmark", workpiece_count=count,
                     generate_previews=False, overwrite_existing_dataset=False)
    _validate_config(config)
    progress(f"Generating and saving {count:,} workpieces to {root} (no previews)...")
    started = perf_counter()
    rng = random.Random(config.random_seed)
    library = root / "library"
    library.mkdir()
    paths = []
    payload_bytes = 0
    for index in range(count):
        shape = config.shape_types[index % len(config.shape_types)]
        width, height = _choose_dimensions(shape, config, rng)
        item = _generate_item(index, shape, width, height)
        points = np.asarray(item["contour_normalized"], dtype=np.float32)
        points *= [item["width_mm"], item["height_mm"]]
        shard = library / f"{index // 1000:06d}"
        if index % 1000 == 0:
            shard.mkdir()
        path = shard / f"{item['id']}_workpiece.json"
        payload = json.dumps({"workpieceId": item["id"],
                              "matchingContour": points.tolist()}, separators=(",", ":"))
        path.write_text(payload, encoding="utf-8")
        payload_bytes += len(payload.encode("utf-8"))
        paths.append(path)
        if (index + 1) % 1000 == 0:
            progress(f"Saved {index + 1:,}/{count:,} in {perf_counter() - started:.1f}s")
    metadata = {"schema_version": 1, "count": count, "seed": config.random_seed,
                "payload_bytes": payload_bytes,
                "generation_seconds": round(perf_counter() - started, 3),
                "immutable_benchmark_library": True}
    (root / "probe-library.json").write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    progress(f"Library saved: {count:,} records, {payload_bytes / 1024**2:.1f} MiB JSON payload")
    return sorted(paths)


def score(paths, query, matcher):
    started = perf_counter()
    scores = {}
    for index, path in enumerate(paths, 1):
        scores[str(path)] = matcher._getSimilarity(read_contour(path), query)
        if index % 1000 == 0:
            progress(f"  Scored {index:,}/{len(paths):,} in {perf_counter() - started:.1f}s")
    accepted = {path for path, value in scores.items()
                if value > matcher.similarity_threshold * 100}
    best = max(scores, key=scores.get) if accepted else None
    return accepted, best, perf_counter() - started


def run(args):
    matcher = GeometricMatchingStrategy()
    with tempfile.TemporaryDirectory(prefix="workpiece-index-probe-") as temporary:
        root = Path(temporary)
        if args.save_library:
            root = args.save_library.resolve()
            root.mkdir(parents=True, exist_ok=False)
            (root / ".probe-incomplete").touch()
        if args.root:
            library_root = args.root.resolve()
            if (library_root / ".probe-incomplete").exists():
                raise ValueError("Benchmark library preparation was interrupted; use a new output directory")
            paths = sorted(library_root.rglob("*_workpiece.json"))
            if (library_root / "probe-library.json").exists():
                metadata = json.loads((library_root / "probe-library.json").read_text())
                if metadata.get("schema_version") != 1 or len(paths) != metadata["count"]:
                    raise ValueError("Benchmark library does not match its completion metadata")
                root = library_root
        elif args.generated_count:
            paths = generated_library(root, args.generated_count)
        else:
            paths = sorted(synthetic_library(root))
        paths = [path for path in paths
                 if not any(part.startswith(".") for part in path.relative_to(
                     args.root.resolve() if args.root else root).parts)
                 and not (path.parent / ".incomplete").exists()]
        if not paths:
            raise ValueError("No published workpiece JSON files found")
        # Keep the original area-only index intact; the richer schema is separate.
        index_path = args.index_path.resolve() if args.index_path else root / "index-geometry-v2.db"
        build_seconds = 0.0
        if index_path.exists():
            with sqlite3.connect(index_path) as connection:
                if connection.execute("PRAGMA user_version").fetchone()[0] != 2:
                    raise ValueError("Unsupported probe index version; choose a new --index-path")
                indexed_paths = [row[0] for row in connection.execute("SELECT path FROM features ORDER BY path")]
                if indexed_paths != [str(path) for path in paths]:
                    raise ValueError("Index belongs to a different library; choose a new --index-path")
            progress(f"Reusing saved index: {index_path}; benchmark datasets must remain unchanged")
        else:
            progress(f"Building index for {len(paths):,} JSON files...")
            started = perf_counter()
            with tempfile.TemporaryDirectory(prefix=".workpiece-index-build-", dir=index_path.parent) as staging:
                staging_index = Path(staging) / "index.db"
                with sqlite3.connect(staging_index) as connection:
                    build_index(connection, paths)
                staging_index.replace(index_path)
            build_seconds = perf_counter() - started
            progress(f"Index built in {build_seconds:.2f}s")
        if args.save_library:
            (root / ".probe-incomplete").unlink()
        if args.prepare_only:
            allocated = sum(path.stat().st_blocks * 512 for path in paths) + index_path.stat().st_blocks * 512
            print(json.dumps({"library": str(root), "count": len(paths),
                              "allocated_file_mib": round(allocated / 1024**2, 1),
                              "free_disk_gib": round(shutil.disk_usage(root).free / 1024**3, 2),
                              "build_seconds": round(build_seconds, 4)}, indent=2))
            return 0
        with sqlite3.connect(index_path) as connection:
            reports = []
            for source in paths[:args.queries]:
                original = read_contour(source).reshape(-1, 2)
                for label, angle, reflection, scale in [
                    ("rotated", 37, 1, 1),
                    ("reflected", 123, -1, 1),
                    ("scaled_5_percent", 71, 1, 1.05),
                ]:
                    if label not in args.variants:
                        continue
                    radians = np.deg2rad(angle)
                    rotation = np.array([[np.cos(radians), -np.sin(radians)],
                                         [np.sin(radians), np.cos(radians)]])
                    query = ((original * [reflection, 1]) @ rotation.T * scale + [200, 350]).astype(np.float32).reshape(-1, 1, 2)
                    started = perf_counter()
                    shortlisted, area_count = candidate_paths(connection, query, args.filter)
                    query_seconds = perf_counter() - started
                    progress(f"{source.name} / {label}: {area_count:,} area candidates -> "
                             f"{len(shortlisted):,} {args.filter} candidates; full scan ({len(paths):,} records)...")
                    accepted, best, full_seconds = score(paths, query, matcher)
                    progress(f"  Full scan: {full_seconds:.2f}s; shortlist scan ({len(shortlisted):,} records)...")
                    indexed, indexed_best, indexed_seconds = score(shortlisted, query, matcher)
                    progress(f"  Shortlist scan: {indexed_seconds:.2f}s; missed matches: {len(accepted - indexed)}")
                    for missed in sorted(accepted - indexed):
                        progress(f"  EXCLUDED VALID MATCH: {Path(missed).name}; saved features="
                                 f"{connection.execute('SELECT area, short_side, long_side, perimeter, solidity, vertices FROM features WHERE path=?', (missed,)).fetchone()}; "
                                 f"query rectangle={sorted(cv2.minAreaRect(query)[1])}, "
                                 f"perimeter={cv2.arcLength(query, True):.3f}, "
                                 f"solidity={cv2.contourArea(query) / cv2.contourArea(cv2.convexHull(query)):.3f}")
                    reports.append({"source": source.name, "variant": label, "filter": args.filter,
                                    "area_only_candidates": area_count,
                                    "candidates": len(shortlisted), "total": len(paths),
                                    "query_seconds": round(query_seconds, 4),
                                    "full_seconds": round(full_seconds, 4),
                                    "indexed_seconds": round(query_seconds + indexed_seconds, 4),
                                    "speedup": round(full_seconds / (query_seconds + indexed_seconds), 3),
                                    "missed_valid_matches": len(accepted - indexed),
                                    "valid_matches": len(accepted),
                                    "same_best": best == indexed_best})
            print(json.dumps({"mode": "real-library" if args.root else "dry-run-generator" if args.generated_count else "synthetic",
                              "build_seconds": round(build_seconds, 4), "results": reports}, indent=2))
            return 1 if any(item["missed_valid_matches"] or not item["same_best"] for item in reports) else 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    source = parser.add_mutually_exclusive_group()
    source.add_argument("--root", type=Path, help="Read-only workpiece library; omit for synthetic fixtures")
    source.add_argument("--generated-count", type=int, help="Use the existing dry-run generator for this many workpieces")
    parser.add_argument("--queries", type=int, default=2, help="Number of stored contours to transform (three variants each)")
    parser.add_argument("--save-library", type=Path, help="Create a new persistent benchmark directory; never overwrite")
    parser.add_argument("--prepare-only", action="store_true", help="Prepare library/index without running matching")
    parser.add_argument("--filter", choices=("area", "geometry"), default="geometry", help="Candidate gates; geometry is experimental")
    parser.add_argument("--index-path", type=Path, help="Alternate reusable v2 index location (e.g. /tmp/library-geometry.db)")
    parser.add_argument("--variants", nargs="+", choices=("rotated", "reflected", "scaled_5_percent"),
                        default=["rotated", "reflected", "scaled_5_percent"], help="Transformations to benchmark")
    arguments = parser.parse_args()
    if arguments.queries < 1:
        parser.error("--queries must be positive")
    if arguments.generated_count is not None and arguments.generated_count < 1:
        parser.error("--generated-count must be positive")
    if arguments.save_library and not arguments.generated_count:
        parser.error("--save-library requires --generated-count")
    if arguments.prepare_only and not (arguments.save_library or arguments.root):
        parser.error("--prepare-only requires --save-library or --root")
    raise SystemExit(run(arguments))
