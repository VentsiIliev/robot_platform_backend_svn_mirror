"""Synthetic end-to-end test: generate frames, calibrate, evaluate on held-out frames."""
import subprocess
import sys
from pathlib import Path

import cv2
import numpy as np

from slot_detector import DetectorConfig, SlotConfig, SlotDetector, SlotState

W, H = 750, 345
SLOTS = {"slot_left": (125, 130), "slot_mid": (375, 130), "slot_right": (625, 130)}
R = 70
rng = np.random.default_rng(0)


def scene(occupied: dict, gain: float, offset: float, noise: float):
    img = np.full((H, W, 3), 175, np.uint8)
    # brushed-aluminium plate texture
    tex = rng.normal(0, 6, (H, W)).astype(np.float32)
    tex = cv2.GaussianBlur(tex, (1, 15), 0) * 3
    img = np.clip(img.astype(np.float32) + tex[..., None], 0, 255)
    # black U-clips (static, present in both states)
    for name, (cx, cy) in SLOTS.items():
        cv2.ellipse(img, (cx, cy), (R + 22, R + 22), 0, 0, 360, (20, 20, 20), 22)
        # cut-out so clip does not fully cover the slot interior
        cv2.circle(img, (cx, cy), R - 2, (185, 185, 185), -1)
        if occupied.get(name):
            disc = np.zeros((H, W), np.float32)
            cv2.circle(disc, (cx + rng.integers(-6, 7), cy + rng.integers(-6, 7)), R - 10, 1.0, -1)
            yy, xx = np.mgrid[0:H, 0:W]
            shade = 200 + 40 * np.cos((xx - cx) / 25.0) + 15 * np.sin((yy - cy) / 18.0)
            shade = np.clip(shade, 0, 255)
            for c in range(3):
                img[..., c] = img[..., c] * (1 - disc) + shade * disc
            cv2.circle(img, (cx - 20, cy - 20), 14, (255, 255, 255), -1)   # specular
            cv2.circle(img, (cx, cy), 30, (150, 150, 150), 2)               # inner ring edge
    img = img * gain + offset
    img = img + rng.normal(0, noise, img.shape)
    return np.clip(img, 0, 255).astype(np.uint8)


def poly(cx, cy):
    r = R - 12
    return [(cx - r, cy - r), (cx + r, cy - r), (cx + r, cy + r), (cx - r, cy + r)]


def main():
    out = Path("/tmp/claude-0/-home-claude/ce3b5241-99de-5c20-a6cb-4b58ddfb967a/scratchpad/slot_test"); out.mkdir(exist_ok=True, parents=True)
    cfg = DetectorConfig(slots=[SlotConfig(n, poly(*c)) for n, c in SLOTS.items()])
    cfg.save(out / "slots.json")

    def lighting():
        return rng.uniform(0.7, 1.3), rng.uniform(-25, 25), rng.uniform(2, 8)

    # training frames: each slot independently empty/occupied under varied lighting
    for i in range(40):
        occ = {n: bool(rng.integers(0, 2)) for n in SLOTS}
        # guarantee balanced classes by also forcing extremes
        if i < 10: occ = {n: False for n in SLOTS}
        elif i < 20: occ = {n: True for n in SLOTS}
        img = scene(occ, *lighting())
        for n in SLOTS:
            d = out / "data" / n / ("occupied" if occ[n] else "empty"); d.mkdir(parents=True, exist_ok=True)
            cv2.imwrite(str(d / f"{i}.png"), img)

    r = subprocess.run([sys.executable, "calibrate_slots.py", "--config", str(out / "slots.json"),
                        "--data", str(out / "data"), "--out", str(out / "slots_cal.json")],
                       capture_output=True, text=True)
    print(r.stdout[-2500:]); print(r.stderr[-1500:])

    # evaluation on held-out frames with a fresh detector + reference from an empty frame
    cfg2 = DetectorConfig.load(out / "slots_cal.json")
    det = SlotDetector(cfg2)
    det.set_reference(scene({}, 1.0, 0.0, 3.0))   # reference taken at nominal lighting only

    correct = total = unknown = 0
    errors = []
    for t in range(60):
        occ = {n: bool(rng.integers(0, 2)) for n in SLOTS}
        g, o, nz = lighting()
        det.reset_history()
        for k in range(cfg2.vote_window):          # temporal window with fresh noise each frame
            res = det.update(scene(occ, g, o, nz))
        for rr in res:
            total += 1
            truth = SlotState.OCCUPIED if occ[rr.name] else SlotState.EMPTY
            if rr.state == SlotState.UNKNOWN:
                unknown += 1
            elif rr.state == truth:
                correct += 1
            else:
                errors.append((t, rr.name, truth.value, rr.state.value, round(rr.score, 2)))
    print(f"held-out: {total} slot decisions | correct={correct} unknown={unknown} wrong={len(errors)}")
    print("errors:", errors[:10])
    assert not errors, "misclassifications on synthetic data"
    # widget module should at least import cleanly
    try:
        import slot_widget  # noqa: F401
        print("slot_widget import OK")
    except Exception as e:  # PyQt6 may be missing in the sandbox
        print("slot_widget import skipped:", repr(e))


if __name__ == "__main__":
    main()
