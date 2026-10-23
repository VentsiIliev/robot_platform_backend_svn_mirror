"""Train from data/<slot>/{empty,occupied} full-frame images.

python calibrate_slots.py --config slots.json --data data --out slots_robust.json --model forest

Last 25% of each class in filename order is held out, also from reference
construction. Adjacent captures may still be correlated: evaluate a new session
before relying on the detector. Keep model/reference sidecars with output JSON.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import uuid
from pathlib import Path

import cv2
import numpy as np

from slot_detector import (
    DetectorConfig, _normalize_roi, feature_names,
    extract_features, forest_scores, inspection_mask, preprocess_slot,
)

IMG_EXT = {".png", ".jpg", ".jpeg", ".bmp"}


def load_images(folder: Path, exclude=()):
    """Read unique decoded frames; fail explicitly on unreadable inputs."""
    if not folder.is_dir():
        return []
    frames, seen = [], set()
    for path in sorted(folder.iterdir()):
        if path.suffix.lower() not in IMG_EXT or path.resolve() in exclude:
            continue
        frame = cv2.imread(str(path))
        if frame is None:
            raise ValueError(f"Cannot read {path}")
        digest = hashlib.sha256(frame.tobytes()).digest()
        if digest not in seen:
            frames.append(frame)
            seen.add(digest)
    return frames


def augment_frame(frame, rng):
    """Mild camera lighting/position variations, generated only for training."""
    h, w = frame.shape[:2]
    yy, xx = np.mgrid[-1:1:complex(h), -1:1:complex(w)]
    ramp = rng.uniform(-20, 20) * xx + rng.uniform(-20, 20) * yy
    value = frame.astype(np.float32) * rng.uniform(0.65, 1.35)
    value += rng.uniform(-25, 25) + ramp[..., None]
    value = np.clip(value, 0, 255).astype(np.uint8)
    transform = np.float32([[1, 0, rng.uniform(-2, 2)], [0, 1, rng.uniform(-2, 2)]])
    return cv2.warpAffine(value, transform, (w, h), borderMode=cv2.BORDER_REFLECT_101)


def sigmoid(z):
    return 1.0 / (1.0 + np.exp(-np.clip(z, -80, 80)))


def fit_logistic(X: np.ndarray, y: np.ndarray, l2: float = 1e-2, iters: int = 4000, lr: float = 0.1):
    """Standardized logistic baseline; fold normalization into stored weights."""
    mu, sd = X.mean(0), X.std(0) + 1e-6
    Z = (X - mu) / sd
    w = np.zeros(Z.shape[1])
    b = 0.0
    for _ in range(iters):
        p = sigmoid(Z @ w + b)
        w -= lr * (Z.T @ (p - y) / len(y) + l2 * w)
        b -= lr * float((p - y).mean())
    return w / sd, b - float(np.sum(w * mu / sd))


def fit_forest(X, y):
    """Depth-limited forest for modest per-slot datasets."""
    cv2.setRNGSeed(42)
    model = cv2.ml.RTrees_create()
    model.setMaxDepth(5)
    model.setMinSampleCount(2)
    model.setMaxCategories(2)
    model.setCalculateVarImportance(True)
    model.setTermCriteria((cv2.TERM_CRITERIA_MAX_ITER, 200, 0))
    if not model.train(np.asarray(X, np.float32), cv2.ml.ROW_SAMPLE, np.asarray(y, np.int32)):
        raise ValueError("Forest training failed")
    return model


def report_scores(label, scores, y, slot):
    empty, occupied = scores <= slot.t_empty, scores >= slot.t_occupied
    correct = ((empty & (y == 0)) | (occupied & (y == 1))).sum()
    wrong = ((empty & (y == 1)) | (occupied & (y == 0))).sum()
    unknown = (~(empty | occupied)).sum()
    print(f"  {label}: total={len(y)} correct={correct} unknown={unknown} wrong={wrong}")
    return {"total": len(y), "correct": int(correct), "unknown": int(unknown), "wrong": int(wrong)}


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--config", required=True)
    ap.add_argument("--data", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--model", choices=("logistic", "forest"), default="logistic")
    ap.add_argument("--features", type=int, choices=(1, 2),
                    help="feature schema (default: 2 for forest, 1 for logistic)")
    ap.add_argument("--margin", type=float,
                    help="UNKNOWN half-width (default: 0.4 forest, 0.2 logistic)")
    ap.add_argument("--validation-fraction", type=float, default=0.25)
    ap.add_argument("--augment", type=int, help="generated variants per training image (default: 12 forest, 0 logistic)")
    ap.add_argument("--refit-all", action="store_true",
                    help="after validation, refit the saved model on all non-excluded images")
    ap.add_argument("--exclude-image", action="append", default=[],
                    help="image path to exclude entirely, e.g. an external regression frame")
    args = ap.parse_args()
    if args.features is None:
        args.features = 2 if args.model == "forest" else 1
    if args.margin is None:
        args.margin = 0.4 if args.model == "forest" else 0.2
    if args.augment is None:
        args.augment = 12 if args.model == "forest" else 0
    if args.augment < 0:
        ap.error("augment must be nonnegative")
    if not 0 < args.margin < 0.5 or not 0 < args.validation_fraction < 0.5:
        ap.error("margin and validation-fraction must be between 0 and 0.5")

    cfg = DetectorConfig.load(args.config)
    data = Path(args.data)
    out = Path(args.out).resolve()
    out.parent.mkdir(parents=True, exist_ok=True)
    assets = out.parent / f"{out.stem}_assets_{uuid.uuid4().hex[:8]}"
    report = {}
    exclude = {Path(p).resolve() for p in args.exclude_image}
    rng = np.random.default_rng(42)

    for index, slot in enumerate(cfg.slots):
        sdir = data / slot.name
        empty, full = load_images(sdir / "empty", exclude), load_images(sdir / "occupied", exclude)
        if len(empty) < 5 or len(full) < 5:
            print(f"[{slot.name}] need >=5 unique frames per class; have {len(empty)} empty, {len(full)} occupied - skipped")
            continue
        empty_hashes = {hashlib.sha256(f.tobytes()).digest() for f in empty}
        if any(hashlib.sha256(f.tobytes()).digest() in empty_hashes for f in full):
            raise ValueError(f"{slot.name}: identical image has conflicting labels")
        shape = empty[0].shape
        if any(f.shape != shape for f in empty + full):
            raise ValueError(f"{slot.name}: training images must have the same resolution")
        ne = max(1, int(np.ceil(len(empty) * args.validation_fraction)))
        nf = max(1, int(np.ceil(len(full) * args.validation_fraction)))
        train_e, val_e = empty[:-ne], empty[-ne:]
        train_f, val_f = full[:-nf], full[-nf:]
        mask = inspection_mask(shape[:2], slot)
        if not (mask > 0).any():
            raise ValueError(f"{slot.name}: polygon is outside the training images")
        slot.feature_version = args.features

        def reference(frames):
            norms = [_normalize_roi(preprocess_slot(f, cfg, slot, mask), mask) for f in frames]
            return (np.median(np.stack(norms), axis=0).astype(np.uint8),
                    float(np.median([n[mask > 0].std() for n in norms])))

        ref, ref_std = reference(train_e)

        def one_feature(frame):
            return extract_features(preprocess_slot(frame, cfg, slot, mask), mask, slot, ref, ref_std)

        def feats(frames):
            return np.stack([one_feature(f) for f in frames])

        def training_features(e, o):
            features, labels = [], []
            for frames, label in ((e, 0), (o, 1)):
                for frame in frames:
                    features.append(one_feature(frame))
                    labels.append(label)
                    for _ in range(args.augment):
                        features.append(one_feature(augment_frame(frame, rng)))
                        labels.append(label)
            return np.stack(features), np.asarray(labels)

        X, y = training_features(train_e, train_f)
        Xv = np.vstack([feats(val_e), feats(val_f)])
        yv = np.r_[np.zeros(len(val_e)), np.ones(len(val_f))]
        slot.t_empty, slot.t_occupied = 0.5 - args.margin, 0.5 + args.margin
        assets.mkdir(exist_ok=True)
        prefix = assets / f"slot_{index}"
        if args.model == "forest":
            model = fit_forest(X, y)
            scores, validation = forest_scores(model, X), forest_scores(model, Xv)
            importance = model.getVarImportance().ravel()
            ranked = sorted(zip(feature_names(slot.feature_version), importance), key=lambda p: -p[1])[:5]
            print(f"\n[{slot.name}] forest: top features {ranked}")
        else:
            w, b = fit_logistic(X, y)
            slot.weights, slot.bias = w.tolist(), float(b)
            slot.model_path = None
            scores, validation = sigmoid(X @ w + b), sigmoid(Xv @ w + b)
            print(f"\n[{slot.name}] logistic, {X.shape[1]} features")
        if args.model == "logistic":
            # Preserve baseline thresholds. In-sample forest votes are too
            # optimistic to use for threshold tightening.
            slot.t_empty = float(min(slot.t_empty, np.percentile(scores[y == 0], 99) + 0.02))
            slot.t_occupied = float(max(slot.t_occupied, np.percentile(scores[y == 1], 1) - 0.02))
        report_scores("training (including generated variants)", scores, y, slot)
        report[slot.name] = report_scores("held-out (before optional refit)", validation, yv, slot)
        report[slot.name]["training_originals"] = len(train_e) + len(train_f)
        report[slot.name]["saved_training_originals"] = (
            len(empty) + len(full) if args.refit_all else len(train_e) + len(train_f)
        )
        if args.refit_all:
            ref, ref_std = reference(empty)
            X, y = training_features(empty, full)
            if args.model == "forest":
                model = fit_forest(X, y)
            else:
                w, b = fit_logistic(X, y)
                slot.weights, slot.bias = w.tolist(), float(b)
            print(f"  saved model refitted on {len(empty) + len(full)} originals")
        if args.model == "forest":
            model_path = prefix.with_suffix(".xml")
            model.save(str(model_path))
            slot.model_path = str(model_path)
        ref_path = prefix.with_suffix(".npz")
        np.savez_compressed(ref_path, norm=ref, std=ref_std, polygon=slot.polygon,
                            inspection_polygon=(slot.inspection_polygon if slot.inspection_polygon is not None else slot.polygon),
                            preprocessing=[cfg.clahe_clip, cfg.clahe_grid, cfg.blur_ksize,
                                           slot.diff_threshold, slot.canny_low, slot.canny_high]
                            + ([1] if slot.local_preprocessing else []))
        slot.reference_path = str(ref_path)

    if not report:
        raise ValueError("No slots trained; check the data directory and class counts")
    cfg.save(out)
    out.with_suffix(".report.json").write_text(json.dumps({
        "model": args.model, "features": args.features,
        "validation": "last frames of each class; references use training frames only",
        "refit_all": args.refit_all, "augmentation_variants": args.augment,
        "excluded_images": sorted(str(p) for p in exclude),
        "slots": report,
    }, indent=2))
    print(f"\nSaved {out} and model/reference assets in {assets}")


if __name__ == "__main__":
    main()
