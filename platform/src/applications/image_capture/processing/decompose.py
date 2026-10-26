#!/usr/bin/env python3
"""
Contour -> lines + circular arcs decomposition (test harness).

Inspired by Nguyen & Debled-Rennesson (SCIA 2011): corner / dominant points
locate the primitive boundaries, then spans are classified as line or arc.
This version uses simple numpy/OpenCV pieces instead of blurred segments:

  1. threshold + findContours (all contour points)
  2. light smoothing + uniform resampling
  3. corner seeds (turning-angle peaks)  -> initial chunk boundaries
  4. bottom-up merge: adjacent chunks are merged while the union still fits
     a line or a circle within `tol` pixels
  5. tiny-segment cleanup, then boundary refinement
  6. report, JSON, overlay image, deviation stats

Usage:
  python decompose.py image.png [--invert] [--tol 1.5] [--out out_dir]
  python decompose.py --selftest [--out out_dir]
  python decompose.py --stress   [--out out_dir]   # camera-like noise/blur/lighting tests

All pixel parameters (--tol, --sigma, --min-len, --min-radius, ...) scale with image
resolution: shrink them if your features are fewer pixels across.
"""
import argparse
import json
import math
import os
from types import SimpleNamespace

import cv2
import numpy as np


# ----------------------------------------------------------------- contour --
def extract_contour(gray, invert=False, min_area=500):
    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    flag = cv2.THRESH_BINARY_INV if invert else cv2.THRESH_BINARY
    _, bw = cv2.threshold(blur, 0, 255, flag | cv2.THRESH_OTSU)
    bw = cv2.morphologyEx(bw, cv2.MORPH_CLOSE, np.ones((3, 3), np.uint8))
    cnts, _ = cv2.findContours(bw, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    cnts = [c for c in cnts if cv2.contourArea(c) >= min_area]
    h, w = gray.shape[:2]
    inside = []
    for c in cnts:  # drop blobs touching the image border (dark surroundings, frames)
        x, y, bw_, bh_ = cv2.boundingRect(c)
        if x > 1 and y > 1 and x + bw_ < w - 1 and y + bh_ < h - 1:
            inside.append(c)
    cnts = inside
    if not cnts:
        raise SystemExit("No contour found (try --invert, or lower --min-area; "
                         "objects touching the image border are ignored).")
    c = max(cnts, key=cv2.contourArea)
    return c[:, 0, :].astype(np.float64), bw


def smooth_closed(P, sigma):
    if sigma <= 0:
        return P.copy()
    r = int(3 * sigma) + 1
    x = np.arange(-r, r + 1)
    k = np.exp(-x ** 2 / (2 * sigma ** 2))
    k /= k.sum()
    Q = np.empty_like(P)
    for d in range(2):
        padded = np.concatenate([P[-r:, d], P[:, d], P[:r, d]])
        Q[:, d] = np.convolve(padded, k, mode="valid")
    return Q


def resample_closed(P, step):
    Q = np.vstack([P, P[:1]])
    seg = np.hypot(*np.diff(Q, axis=0).T)
    s = np.concatenate([[0.0], np.cumsum(seg)])
    L = s[-1]
    n = max(int(round(L / step)), 12)
    t = np.linspace(0, L, n, endpoint=False)
    return np.column_stack([np.interp(t, s, Q[:, 0]), np.interp(t, s, Q[:, 1])])


# ------------------------------------------------------------------ models --
def fit_line(pts):
    c = pts.mean(0)
    w, v = np.linalg.eigh(np.cov((pts - c).T))
    d = v[:, 1]
    nrm = np.array([-d[1], d[0]])
    return dict(type="line", c=c, d=d, res=np.abs((pts - c) @ nrm))


def fit_circle(pts, rmax=1e9):
    x, y = pts[:, 0], pts[:, 1]
    xm, ym = x.mean(), y.mean()
    u, v = x - xm, y - ym
    Suu, Svv, Suv = (u * u).sum(), (v * v).sum(), (u * v).sum()
    b = 0.5 * np.array([(u ** 3).sum() + (u * v * v).sum(),
                        (v ** 3).sum() + (v * u * u).sum()])
    A = np.array([[Suu, Suv], [Suv, Svv]])
    if abs(np.linalg.det(A)) < 1e-9:
        return None
    uc, vc = np.linalg.solve(A, b)
    cx, cy = xm + uc, ym + vc
    r = math.sqrt(((x - cx) ** 2 + (y - cy) ** 2).mean())
    if not np.isfinite(r) or r > rmax * 3:
        return None
    for _ in range(6):  # geometric Gauss-Newton refinement
        dx, dy = x - cx, y - cy
        d = np.hypot(dx, dy) + 1e-12
        J = np.column_stack([-dx / d, -dy / d, -np.ones_like(d)])
        delta = np.linalg.lstsq(J, -(d - r), rcond=None)[0]
        cx, cy, r = cx + delta[0], cy + delta[1], r + delta[2]
        if np.abs(delta).max() < 1e-6:
            break
    if not np.isfinite(r) or r <= 0 or r > rmax:
        return None
    res = np.abs(np.hypot(x - cx, y - cy) - r)
    return dict(type="arc", c=np.array([cx, cy]), r=r, res=res)


def arc_is_sane(ar, pts, p):
    """Reject circles that are really lines (tiny bow) or corner roundings (tiny radius)."""
    if ar is None or ar["r"] < p.min_radius:
        return False
    ang = np.unwrap(np.arctan2(pts[:, 1] - ar["c"][1], pts[:, 0] - ar["c"][0]))
    sweep = ang[-1] - ang[0]
    sgn = np.sign(sweep)
    if sgn == 0 or abs(sweep) > 2 * math.pi + 0.3:
        return False
    if (np.sign(np.diff(ang)) == sgn).mean() < 0.9:  # must progress around the circle
        return False
    if math.degrees(abs(sweep)) < p.min_sweep_deg:
        return False
    sagitta = ar["r"] * (1 - math.cos(min(abs(sweep), math.pi) / 2))
    return sagitta >= p.min_sagitta * p.tol  # bow must be distinguishable from a line


def classify(pts, p):
    """Return model dict (line/arc) if pts fit within tol, else None."""
    ln = fit_line(pts)
    if ln["res"].max() <= p.tol:
        return ln
    if len(pts) >= p.min_arc_pts:
        ar = fit_circle(pts, p.rmax)
        if ar is not None and ar["res"].max() <= p.tol and arc_is_sane(ar, pts, p):
            return ar
    # no valid arc: accept a slightly bowed/noisy line rather than a fake huge-radius arc
    if ln["res"].max() <= p.line_slack * p.tol:
        return ln
    return None


def best_effort(pts, p):
    """Best of line/circle by max residual, used when nothing fits within tol."""
    ln = fit_line(pts)
    ar = fit_circle(pts, p.rmax) if len(pts) >= p.min_arc_pts else None
    if ar is not None and arc_is_sane(ar, pts, p) and ar["res"].max() < ln["res"].max():
        return ar
    return ln


# ---------------------------------------------------------- segmentation ----
def span(a, b, n):
    return (b - a) % n or n


def seg_pts(P, a, length):
    return P[np.arange(a, a + length + 1) % len(P)]


def corner_seeds(P, k, thresh_deg):
    n = len(P)
    a = P - np.roll(P, k, axis=0)
    b = np.roll(P, -k, axis=0) - P
    mag = np.abs(np.arctan2(a[:, 0] * b[:, 1] - a[:, 1] * b[:, 0], (a * b).sum(1)))
    seeds = []
    for i in np.argsort(-mag):
        if mag[i] < math.radians(thresh_deg):
            break
        if mag[i] >= mag[np.arange(i - k, i + k + 1) % n].max() and \
                all(min((i - s) % n, (s - i) % n) > k for s in seeds):
            seeds.append(int(i))
    return sorted(seeds)


def initial_boundaries(n, seeds, chunk):
    B = set(seeds)
    for i in range(0, n, chunk):
        if all(min((i - s) % n, (s - i) % n) >= chunk // 2 for s in seeds):
            B.add(i)
    B = sorted(B)
    return B if len(B) >= 3 else list(range(0, n, max(n // 6, 1)))


def merge_chunks(P, B, p):
    n = len(P)
    cache = {}

    def cls(a, length):
        key = (a % n, length)
        if key not in cache:
            cache[key] = classify(seg_pts(P, a, length), p)
        return cache[key]

    while len(B) > 1:
        m = len(B)
        best = None
        for i in range(m):
            a, c = B[i], B[(i + 2) % m]
            length = span(a, c, n) if m > 2 else n
            model = cls(a, length)
            if model is None:
                continue
            cost = float(np.sqrt((model["res"] ** 2).mean()))
            if best is None or cost < best[0]:
                best = (cost, (i + 1) % m)
        if best is None:
            break
        del B[best[1]]
    return B


def absorb_tiny(P, B, p):
    n = len(P)
    while len(B) > 2:
        m = len(B)
        lens = [span(B[i], B[(i + 1) % m], n) for i in range(m)]
        i = int(np.argmin(lens))
        if lens[i] >= p.min_len:
            break
        prev_i = (i - 1) % m
        la = span(B[prev_i], B[(i + 1) % m], n)
        lb = span(B[i], B[(i + 2) % m], n)
        ea = best_effort(seg_pts(P, B[prev_i], la), p)["res"].max()
        eb = best_effort(seg_pts(P, B[i], lb), p)["res"].max()
        del B[i if ea <= eb else (i + 1) % m]
    return B


def sse(P, a, length, kind, p):
    pts = seg_pts(P, a, length)
    if len(pts) < 5:
        return 1e18
    mdl = fit_line(pts) if kind == "line" else fit_circle(pts, p.rmax)
    return 1e18 if mdl is None else float((mdl["res"] ** 2).sum())


def refine_boundaries(P, B, p, passes=2):
    n = len(P)
    for _ in range(passes):
        m = len(B)
        if m < 2:
            return B
        kinds = []
        for i in range(m):
            pts = seg_pts(P, B[i], span(B[i], B[(i + 1) % m], n))
            mdl = classify(pts, p) or best_effort(pts, p)
            kinds.append(mdl["type"])
        for j in range(m):
            prev, nxt = B[(j - 1) % m], B[(j + 1) % m]
            tot = span(prev, nxt, n)
            best = (None, None)
            for t in range(-p.refine_w, p.refine_w + 1):
                nb = (B[j] + t) % n
                d1, d2 = span(prev, nb, n), span(nb, nxt, n)
                if d1 + d2 != tot or d1 < 5 or d2 < 5:
                    continue
                score = sse(P, prev, d1, kinds[(j - 1) % m], p) + \
                    sse(P, nb, d2, kinds[j], p)
                if best[0] is None or score < best[0]:
                    best = (score, nb)
            if best[1] is not None:
                B[j] = best[1]
    return B


# ------------------------------------------------------------- primitives ---
def build_primitives(P, B, p):
    n, m = len(P), len(B)
    prims = []
    for i in range(m):
        a = B[i]
        length = span(a, B[(i + 1) % m], n) if m > 1 else n
        pts = seg_pts(P, a, length)
        mdl = classify(pts, p)
        ok = mdl is not None
        if mdl is None:
            mdl = best_effort(pts, p)
        if mdl["type"] == "line":
            c, d = mdl["c"], mdl["d"]
            p0 = c + d * ((pts[0] - c) @ d)
            p1 = c + d * ((pts[-1] - c) @ d)
            prims.append(dict(type="line", p0=p0.tolist(), p1=p1.tolist(),
                              length=float(np.linalg.norm(p1 - p0)),
                              max_err=float(mdl["res"].max()), within_tol=ok,
                              start_idx=int(a), n_pts=len(pts)))
        else:
            c, r = mdl["c"], mdl["r"]
            ang = np.unwrap(np.arctan2(pts[:, 1] - c[1], pts[:, 0] - c[0]))
            sweep = float(ang[-1] - ang[0])
            if m == 1:
                sweep = math.copysign(2 * math.pi, sweep or 1)
            prims.append(dict(type="arc", center=c.tolist(), radius=float(r),
                              start_deg=float(math.degrees(ang[0])),
                              sweep_deg=float(math.degrees(sweep)),
                              length=float(abs(sweep) * r),
                              max_err=float(mdl["res"].max()), within_tol=ok,
                              start_idx=int(a), n_pts=len(pts)))
    return prims


def sample_primitive(pr, step=0.25):
    if pr["type"] == "line":
        p0, p1 = np.array(pr["p0"]), np.array(pr["p1"])
        k = max(int(np.linalg.norm(p1 - p0) / step), 2)
        t = np.linspace(0, 1, k)[:, None]
        return p0 + (p1 - p0) * t
    c, r = np.array(pr["center"]), pr["radius"]
    a0 = math.radians(pr["start_deg"])
    sw = math.radians(pr["sweep_deg"])
    k = max(int(abs(sw) * r / step), 2)
    a = a0 + np.linspace(0, sw, k)
    return np.column_stack([c[0] + r * np.cos(a), c[1] + r * np.sin(a)])


def min_dist(A, B, chunk=256):
    out = np.empty(len(A))
    for i in range(0, len(A), chunk):
        d = np.linalg.norm(A[i:i + chunk, None, :] - B[None, :, :], axis=2)
        out[i:i + chunk] = d.min(1)
    return out


def deviation_stats(contour, prims):
    R = np.vstack([sample_primitive(pr) for pr in prims])
    d1 = min_dist(contour, R)
    d2 = min_dist(R[::4], contour)
    return dict(mean_err=float(d1.mean()), max_err=float(d1.max()),
                p95_err=float(np.percentile(d1, 95)),
                hausdorff=float(max(d1.max(), d2.max())))


# ----------------------------------------------------------------- driver ---
def decompose(gray, p):
    raw, bw = extract_contour(gray, p.invert, p.min_area)
    P = resample_closed(smooth_closed(raw, p.sigma), p.step)
    seeds = corner_seeds(P, p.corner_k, p.corner_deg)
    B = initial_boundaries(len(P), seeds, p.chunk)
    n_init = len(B)
    B = merge_chunks(P, B, p)
    B = absorb_tiny(P, B, p)
    B = refine_boundaries(P, B, p)
    # re-merge after refinement (boundaries moved), then drop tiny leftovers
    B = merge_chunks(P, B, p)
    B = absorb_tiny(P, B, p)
    prims = build_primitives(P, B, p)
    stats = deviation_stats(raw, prims)
    stats.update(n_contour_pts=len(raw), n_initial_chunks=n_init, n_seeds=len(seeds))
    return raw, P, prims, stats


def draw_overlay(gray, raw, prims, scale=2):
    img = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)
    img = cv2.resize(img, None, fx=scale, fy=scale, interpolation=cv2.INTER_NEAREST)
    img = (img * 0.35).astype(np.uint8)
    for q in raw:
        cv2.circle(img, (int(q[0] * scale + scale / 2), int(q[1] * scale + scale / 2)),
                   1, (150, 150, 150), -1)
    arc_cols = [(255, 120, 0), (0, 200, 0)]
    k = 0
    for pr in prims:
        pts = (sample_primitive(pr, 0.5) * scale + scale / 2).astype(np.int32)
        if pr["type"] == "line":
            col = (0, 0, 255)
        else:
            col = arc_cols[k % 2]
            k += 1
        cv2.polylines(img, [pts.reshape(-1, 1, 2)], False, col, 2, cv2.LINE_AA)
        for e in (pts[0], pts[-1]):
            cv2.circle(img, tuple(int(v) for v in e), 4, (0, 255, 255), -1, cv2.LINE_AA)
    return img


def print_report(prims, stats, p):
    print(f"  contour points: {stats['n_contour_pts']}   corner seeds: {stats['n_seeds']}   "
          f"initial chunks: {stats['n_initial_chunks']}   primitives: {len(prims)}")
    for i, pr in enumerate(prims):
        flag = "" if pr["within_tol"] else "   <-- exceeds tol"
        if pr["type"] == "line":
            print(f"  {i:2d} LINE  len={pr['length']:7.1f}  "
                  f"({pr['p0'][0]:6.1f},{pr['p0'][1]:6.1f}) -> ({pr['p1'][0]:6.1f},{pr['p1'][1]:6.1f})"
                  f"  err={pr['max_err']:.2f}{flag}")
        else:
            print(f"  {i:2d} ARC   len={pr['length']:7.1f}  "
                  f"r={pr['radius']:6.1f} c=({pr['center'][0]:6.1f},{pr['center'][1]:6.1f}) "
                  f"sweep={pr['sweep_deg']:7.1f}deg  err={pr['max_err']:.2f}{flag}")
    print(f"  deviation of contour from reconstruction [px]: mean={stats['mean_err']:.2f} "
          f"p95={stats['p95_err']:.2f} max={stats['max_err']:.2f} hausdorff={stats['hausdorff']:.2f}")


# --------------------------------------------------------------- self test --
def _path_points(ops, ss):
    pts = []
    for op in ops:
        if op[0] == "line":
            p0, p1 = np.array(op[1], float), np.array(op[2], float)
            k = max(int(np.linalg.norm(p1 - p0) * ss), 2)
            pts.append(p0 + (p1 - p0) * np.linspace(0, 1, k, endpoint=False)[:, None])
        else:
            c, r, a0, a1 = np.array(op[1], float), op[2], op[3], op[4]
            k = max(int(abs(math.radians(a1 - a0)) * r * ss), 2)
            a = np.radians(np.linspace(a0, a1, k, endpoint=False))
            pts.append(np.column_stack([c[0] + r * np.cos(a), c[1] + r * np.sin(a)]))
    return np.vstack(pts)


def synthetic_shapes():
    A = [("line", (140, 150), (360, 150)), ("arc", (360, 190), 40, -90, 0),
         ("line", (400, 190), (400, 310)), ("arc", (360, 310), 40, 0, 90),
         ("line", (360, 350), (140, 350)), ("arc", (140, 310), 40, 90, 180),
         ("line", (100, 310), (100, 190)), ("arc", (140, 190), 40, 180, 270)]
    O = (120, 380)
    B = [("line", O, (120, 130)), ("arc", O, 250, -90, 0), ("line", (370, 380), O)]
    C = [("arc", (250, 250), 120, 180, 360), ("line", (370, 250), (370, 380)),
         ("line", (370, 380), (310, 380)), ("line", (310, 380), (310, 250)),
         ("arc", (250, 250), 60, 360, 180), ("line", (190, 250), (190, 380)),
         ("line", (190, 380), (130, 380)), ("line", (130, 380), (130, 250))]
    # ops for C's inner arc run 360->180 (counter-direction), handled by linspace
    return {"A_rounded_rect": (A, 0.0), "B_sector": (B, 0.0),
            "C_arch_concentric": (C, 0.0), "D_rounded_rect_noisy": (A, 6.0)}


def render(ops, noise, size=500, ss=4):
    big = np.zeros((size * ss, size * ss), np.uint8)
    pts = _path_points(ops, ss) * ss
    cv2.fillPoly(big, [np.round(pts).astype(np.int32)], 255)
    img = cv2.resize(big, (size, size), interpolation=cv2.INTER_AREA)
    if noise > 0:
        rng = np.random.default_rng(1)
        img = cv2.GaussianBlur(img, (0, 0), 1.0).astype(np.float32)
        img += rng.normal(0, noise * 4, img.shape).astype(np.float32)
        img = np.clip(img, 0, 255).astype(np.uint8)
    return img


def truth_summary(ops):
    return [f"LINE {np.hypot(o[2][0]-o[1][0], o[2][1]-o[1][1]):.0f}px" if o[0] == "line"
            else f"ARC r={o[2]} sweep={abs(o[4]-o[3]):.0f}deg" for o in ops]


def selftest(p, out):
    os.makedirs(out, exist_ok=True)
    for name, (ops, noise) in synthetic_shapes().items():
        gray = render(ops, noise)
        cv2.imwrite(os.path.join(out, f"{name}_input.png"), gray)
        raw, P, prims, stats = decompose(gray, p)
        print(f"\n=== {name} ===")
        print("  truth:", ", ".join(truth_summary(ops)))
        print_report(prims, stats, p)
        cv2.imwrite(os.path.join(out, f"{name}_overlay.png"), draw_overlay(gray, raw, prims))
        with open(os.path.join(out, f"{name}.json"), "w") as f:
            json.dump(dict(primitives=prims, stats=stats), f, indent=1)


STRESS_CASES = [
    ("noise 25", dict(noise=25)),
    ("noise 50", dict(noise=50)),
    ("noise 80", dict(noise=80)),
    ("blur 3 + noise 25", dict(blur=3, noise=25)),
    ("light gradient + noise 25", dict(grad=True, noise=25)),
    ("salt/pepper 3% + noise 25", dict(sp=0.03, noise=25)),
    ("1/3 resolution + noise 25", dict(down=3, noise=25)),
]


def degrade(clean, rng, noise=0.0, blur=0.0, grad=False, sp=0.0, down=1):
    """Camera-like degradation of a clean synthetic image."""
    img = clean.astype(np.float32)
    if down > 1:
        img = cv2.resize(img, None, fx=1 / down, fy=1 / down, interpolation=cv2.INTER_AREA)
    if blur:
        img = cv2.GaussianBlur(img, (0, 0), blur)
    if grad:  # uneven illumination
        ramp = np.linspace(0.45, 1.0, img.shape[1])[None, :]
        img = img * ramp + 25 * (1 - ramp)
    img = img + rng.normal(0, noise, img.shape)
    if sp:
        m = rng.random(img.shape)
        img[m < sp / 2] = 0
        img[m > 1 - sp / 2] = 255
    return np.clip(img, 0, 255).astype(np.uint8)


def stress(p, out):
    """Run camera-like degradations on the synthetic shapes; compare to ground truth counts."""
    os.makedirs(out, exist_ok=True)
    shapes = synthetic_shapes()
    rng = np.random.default_rng(7)
    n_bad = n_all = 0
    for name in ("A_rounded_rect", "B_sector", "C_arch_concentric"):
        ops = shapes[name][0]
        truth = (sum(o[0] == "line" for o in ops), sum(o[0] == "arc" for o in ops))
        clean = render(ops, 0.0)
        print(f"\n##### {name}  (truth: {truth[0]} lines + {truth[1]} arcs)")
        for cname, kw in STRESS_CASES:
            gray = degrade(clean, rng, **kw)
            s = math.sqrt(kw.get("down", 1))  # fewer pixels per feature -> scale pixel params
            q = SimpleNamespace(**{**vars(p), "tol": p.tol / s, "sigma": p.sigma / s,
                                   "min_radius": p.min_radius / s,
                                   "min_len": max(8, round(p.min_len / s)),
                                   "min_arc_pts": max(8, round(p.min_arc_pts / s)),
                                   "min_area": p.min_area / kw.get("down", 1) ** 2})
            n_all += 1
            try:
                raw, P, prims, st = decompose(gray, q)
            except SystemExit as e:
                n_bad += 1
                print(f"BAD {cname:28s} FAILED: {e}")
                continue
            nl = sum(x["type"] == "line" for x in prims)
            na = len(prims) - nl
            over = sum(not x["within_tol"] for x in prims)
            good = (nl, na) == truth
            n_bad += not good
            print(f"{'OK ' if good else 'BAD'} {cname:28s} {nl}L+{na}A  "
                  f"max_dev={st['max_err']:.2f}px mean={st['mean_err']:.2f} exceed_tol={over}")
            if not good:
                slug = cname.replace(" ", "_").replace("/", "_").replace("+", "")
                cv2.imwrite(os.path.join(out, f"stress_{name}_{slug}_overlay.png"),
                            draw_overlay(gray, raw, prims))
    print(f"\n{n_all - n_bad}/{n_all} cases matched ground truth primitive counts")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("image", nargs="?")
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--stress", action="store_true",
                    help="camera-like noise/blur/lighting tests on synthetic shapes")
    ap.add_argument("--min-radius", type=float, default=None,
                    help="arcs below this radius (px) are treated as corners (default 3*sigma)")
    ap.add_argument("--min-sweep-deg", type=float, default=10.0,
                    help="arcs sweeping less than this are treated as lines")
    ap.add_argument("--min-sagitta", type=float, default=1.0,
                    help="arc bow must be >= this many tolerances to count as an arc")
    ap.add_argument("--line-slack", type=float, default=1.35,
                    help="a line may exceed tol by this factor if no valid arc fits")
    ap.add_argument("--out", default="decomp_out")
    ap.add_argument("--invert", action="store_true", help="dark object on light background")
    ap.add_argument("--tol", type=float, default=1.5, help="max fit deviation in px")
    ap.add_argument("--sigma", type=float, default=1.5, help="contour smoothing (px)")
    ap.add_argument("--step", type=float, default=1.0, help="resampling step (px)")
    ap.add_argument("--chunk", type=int, default=10, help="initial chunk length (pts)")
    ap.add_argument("--corner-k", type=int, default=4)
    ap.add_argument("--corner-deg", type=float, default=35.0)
    ap.add_argument("--min-len", type=int, default=16, help="min primitive length (pts)")
    ap.add_argument("--min-arc-pts", type=int, default=12)
    ap.add_argument("--rmax", type=float, default=5000.0)
    ap.add_argument("--refine-w", type=int, default=12)
    ap.add_argument("--min-area", type=float, default=500)
    a = ap.parse_args()
    p = SimpleNamespace(tol=a.tol, sigma=a.sigma, step=a.step, chunk=a.chunk,
                        corner_k=a.corner_k, corner_deg=a.corner_deg, min_len=a.min_len,
                        min_arc_pts=a.min_arc_pts, rmax=a.rmax, refine_w=a.refine_w,
                        invert=a.invert, min_area=a.min_area,
                        min_radius=a.min_radius if a.min_radius is not None else 3 * a.sigma,
                        min_sweep_deg=a.min_sweep_deg, min_sagitta=a.min_sagitta,
                        line_slack=a.line_slack)
    if a.stress:
        return stress(p, a.out)
    if a.selftest:
        return selftest(p, a.out)
    if not a.image:
        ap.error("give an image or --selftest")
    gray = cv2.imread(a.image, cv2.IMREAD_GRAYSCALE)
    if gray is None:
        raise SystemExit(f"cannot read {a.image}")
    os.makedirs(a.out, exist_ok=True)
    raw, P, prims, stats = decompose(gray, p)
    print_report(prims, stats, p)
    base = os.path.splitext(os.path.basename(a.image))[0]
    cv2.imwrite(os.path.join(a.out, f"{base}_overlay.png"), draw_overlay(gray, raw, prims))
    with open(os.path.join(a.out, f"{base}.json"), "w") as f:
        json.dump(dict(primitives=prims, stats=stats), f, indent=1)


if __name__ == "__main__":
    main()
