#!/usr/bin/env python3
"""
Run the lines/arcs decomposition (decompose.py, unchanged) on contours exported
as JSON: {"contours": [{"points": [[x, y], ...], "closed": true}], ...}

Your exported points are irregular (integer pixels mixed with subpixel clusters,
exact and near duplicates, small back-and-forth jitter), so they are cleaned
and resampled to a uniform spacing before the normal pipeline runs.

Usage:
  python decompose_contour.py capture.json [--image frame.png] [--out out_dir]
         [--tol 1.5] [--sigma 1.5] [--contour-index N]
Units follow the JSON (here: calibrated image pixels). If you give mm, scale
--tol / --sigma / --min-len / --min-radius to mm as well.
"""
import argparse
import json
import os
from types import SimpleNamespace

import cv2
import numpy as np

from . import decompose as D


# ------------------------------------------------------------------ loading --
def load_contour(path, index=None):
    with open(path) as f:
        data = json.load(f)
    cs = data.get("contours") or []
    if not cs:
        raise SystemExit(f"{path}: no contours")
    if index is None:  # default: the largest contour by area
        areas = [abs(cv2.contourArea(np.array(c["points"], np.float32))) for c in cs]
        index = int(np.argmax(areas))
    return np.array(cs[index]["points"], np.float64), data


def clean_points(pts, min_gap=0.25, short=2.5, max_iter=10):
    """Drop duplicates and tiny back-and-forth spikes (both neighbouring steps short)."""
    out = [pts[0]]
    for q in pts[1:]:
        if np.hypot(*(q - out[-1])) >= min_gap:
            out.append(q)
    P = np.array(out)
    if len(P) > 1 and np.hypot(*(P[0] - P[-1])) < min_gap:
        P = P[:-1]
    removed = 0
    for _ in range(max_iter):
        a = P - np.roll(P, 1, axis=0)       # step into point i
        b = np.roll(P, -1, axis=0) - P      # step out of point i
        la, lb = np.hypot(*a.T), np.hypot(*b.T)
        reversal = (a * b).sum(1) < 0
        bad = reversal & (la < short) & (lb < short)
        if not bad.any():
            break
        # remove non-adjacent offenders per pass to stay stable
        idx = np.where(bad)[0]
        keep = np.ones(len(P), bool)
        last = -10
        for i in idx:
            if i - last > 1:
                keep[i] = False
                last = i
        removed += int((~keep).sum())
        P = P[keep]
    return P, removed


# ------------------------------------------------------------- decomposition --
def default_params(**kw):
    p = dict(tol=1.5, sigma=1.5, step=1.0, chunk=10, corner_k=4, corner_deg=35.0,
             min_len=16, min_arc_pts=12, rmax=5000.0, refine_w=12, invert=False,
             min_area=500, min_sweep_deg=10.0, min_sagitta=1.0, line_slack=1.35,
             min_radius=None)
    p.update({k: v for k, v in kw.items() if v is not None})
    if p["min_radius"] is None:
        p["min_radius"] = 3 * p["sigma"]
    return SimpleNamespace(**p)


def decompose_points(pts, p):
    """Same steps as decompose.decompose(), starting from an exported point list."""
    pts = np.asarray(pts, dtype=np.float64).reshape(-1, 2)
    if len(pts) < 3 or not np.isfinite(pts).all():
        raise ValueError("Contour requires at least three finite points.")
    clean, removed = clean_points(pts)
    if len(clean) < 3 or abs(cv2.contourArea(clean.astype(np.float32))) <= 1e-9:
        raise ValueError("Contour is degenerate after cleaning.")
    raw = D.resample_closed(clean, 1.0)                       # uniform ~1 unit spacing
    P = D.resample_closed(D.smooth_closed(raw, p.sigma), p.step)
    seeds = D.corner_seeds(P, p.corner_k, p.corner_deg)
    B = D.initial_boundaries(len(P), seeds, p.chunk)
    n_init = len(B)
    B = D.merge_chunks(P, B, p)
    B = D.absorb_tiny(P, B, p)
    B = D.refine_boundaries(P, B, p)
    B = D.merge_chunks(P, B, p)
    B = D.absorb_tiny(P, B, p)
    prims = D.build_primitives(P, B, p)
    stats = D.deviation_stats(raw, prims)
    stats.update(n_contour_pts=len(pts), n_clean_pts=len(clean), n_removed_spikes=removed,
                 n_initial_chunks=n_init, n_seeds=len(seeds))
    return raw, P, prims, stats


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("json_file")
    ap.add_argument("--image", help="frame to draw the overlay on (optional)")
    ap.add_argument("--out", default="contour_out")
    ap.add_argument("--contour-index", type=int, default=None)
    ap.add_argument("--tol", type=float, default=None)
    ap.add_argument("--sigma", type=float, default=None)
    ap.add_argument("--step", type=float, default=None)
    ap.add_argument("--min-len", type=int, default=None)
    ap.add_argument("--min-radius", type=float, default=None)
    a = ap.parse_args()

    p = default_params(tol=a.tol, sigma=a.sigma, step=a.step, min_len=a.min_len,
                       min_radius=a.min_radius)
    pts, data = load_contour(a.json_file, a.contour_index)
    raw, P, prims, st = decompose_points(pts, p)

    print(f"  input points: {st['n_contour_pts']}  after cleaning: {st['n_clean_pts']} "
          f"(spike points removed: {st['n_removed_spikes']})")
    D.print_report(prims, st, p)

    os.makedirs(a.out, exist_ok=True)
    base = os.path.splitext(os.path.basename(a.json_file))[0][:40]
    if a.image:
        gray = cv2.imread(a.image, cv2.IMREAD_GRAYSCALE)
    else:
        gray = np.zeros((int(data.get("height", 720)), int(data.get("width", 1280))), np.uint8)
    ov = D.draw_overlay(gray, raw, prims, scale=2)
    x0, y0 = np.floor(raw.min(0) - 40).astype(int)
    x1, y1 = np.ceil(raw.max(0) + 40).astype(int)
    x0, y0 = max(x0, 0), max(y0, 0)
    cv2.imwrite(os.path.join(a.out, f"{base}_overlay.png"), ov[2 * y0:2 * y1, 2 * x0:2 * x1])
    with open(os.path.join(a.out, f"{base}.json"), "w") as f:
        json.dump(dict(source=os.path.basename(a.json_file), params=vars(p),
                       primitives=prims, stats=st), f, indent=1)


if __name__ == "__main__":
    main()
