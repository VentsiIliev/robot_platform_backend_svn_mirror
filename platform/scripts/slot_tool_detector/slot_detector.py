"""Robust slot-occupancy detection (Qt-free, usable from a ROS2 node).

Legacy configs compute three features inside a polygon mask:
  * edge_density : fraction of Canny edge pixels (flat plate -> few edges)
  * diff_frac    : fraction of pixels differing from an "empty" reference
  * std_ratio    : local contrast (std dev) relative to the empty reference

Features are combined into a score in [0, 1]. A hysteresis + majority-vote
filter turns per-frame scores into a stable state:
    EMPTY / OCCUPIED / UNKNOWN
UNKNOWN means "do not act on this slot, re-check".

Feature schema 2 adds gradient/texture statistics, reference correlation,
connected change area and a 3x3 spatial difference grid. Models may use a
linear classifier or a persisted OpenCV random forest. Forest scores are tree
vote fractions, not calibrated probabilities.
"""
from __future__ import annotations

import json
import os
from collections import deque
from dataclasses import asdict, dataclass, field
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Tuple

import cv2
import numpy as np

Point = Tuple[float, float]


class SlotState(str, Enum):
    EMPTY = "empty"
    OCCUPIED = "occupied"
    UNKNOWN = "unknown"


FEATURE_NAMES = ("edge_density", "diff_frac", "std_ratio")
ROBUST_FEATURE_NAMES = FEATURE_NAMES + (
    "diff_mean", "diff_p90", "largest_change", "gradient_mean",
    "gradient_std", "intensity_iqr", "entropy", "reference_correlation",
) + tuple(f"cell_diff_{i}" for i in range(9))


def feature_names(version: int) -> tuple:
    if version not in (1, 2):
        raise ValueError(f"Unsupported feature version: {version}")
    return FEATURE_NAMES if version == 1 else ROBUST_FEATURE_NAMES


# --------------------------------------------------------------------------- #
# Config
# --------------------------------------------------------------------------- #
@dataclass
class SlotConfig:
    name: str
    polygon: List[Point]                      # pixel coords in the full frame
    # Linear model on standardized features: score = sigmoid(w . x + b)
    weights: List[float] = field(default_factory=lambda: [6.0, 6.0, 1.5])
    bias: float = -3.5
    t_empty: float = 0.30                     # score below -> EMPTY
    t_occupied: float = 0.70                  # score above -> OCCUPIED
    diff_threshold: int = 35                  # per-pixel abs diff counted as "changed"
    canny_low: int = 40
    canny_high: int = 120
    feature_version: int = 1                 # legacy configs retain three features
    model_path: Optional[str] = None         # OpenCV RTrees; relative to config
    reference_path: Optional[str] = None     # matching empty reference (.npz)
    inspection_polygon: Optional[List[Point]] = None  # classify only this inner area
    local_preprocessing: bool = False         # exclude surrounding scene from CLAHE


@dataclass
class DetectorConfig:
    slots: List[SlotConfig] = field(default_factory=list)
    vote_window: int = 5                      # frames in the majority vote
    clahe_clip: float = 2.0
    clahe_grid: int = 4
    blur_ksize: int = 5

    def save(self, path: str | Path) -> None:
        data = {
            "vote_window": self.vote_window,
            "clahe_clip": self.clahe_clip,
            "clahe_grid": self.clahe_grid,
            "blur_ksize": self.blur_ksize,
            "slots": [asdict(s) for s in self.slots],
        }
        for slot in data["slots"]:
            for key in ("model_path", "reference_path"):
                if slot[key]:
                    slot[key] = os.path.relpath(self.resolve_path(slot[key]), Path(path).resolve().parent)
        Path(path).write_text(json.dumps(data, indent=2))

    def resolve_path(self, path: str) -> Path:
        return (getattr(self, "_base_dir", Path.cwd()) / path).resolve()

    @staticmethod
    def load(path: str | Path) -> "DetectorConfig":
        d = json.loads(Path(path).read_text())
        slots = [SlotConfig(**s) for s in d.pop("slots")]
        cfg = DetectorConfig(slots=slots, **d)
        cfg._base_dir = Path(path).resolve().parent
        return cfg


# --------------------------------------------------------------------------- #
# Image helpers
# --------------------------------------------------------------------------- #
def polygon_mask(shape: Tuple[int, int], polygon: Sequence[Point]) -> np.ndarray:
    mask = np.zeros(shape[:2], np.uint8)
    cv2.fillPoly(mask, [np.round(np.array(polygon)).astype(np.int32)], 255)
    return mask


def inspection_mask(shape: Tuple[int, int], slot: SlotConfig) -> np.ndarray:
    mask = polygon_mask(shape, slot.polygon)
    if slot.inspection_polygon is not None:
        mask = cv2.bitwise_and(mask, polygon_mask(shape, slot.inspection_polygon))
    return mask


def preprocess(frame: np.ndarray, cfg: DetectorConfig) -> np.ndarray:
    """Gray -> blur -> CLAHE. CLAHE + per-ROI normalization tame lighting drift."""
    gray = frame if frame.ndim == 2 else cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    k = cfg.blur_ksize | 1
    gray = cv2.GaussianBlur(gray, (k, k), 0)
    clahe = cv2.createCLAHE(cfg.clahe_clip, (cfg.clahe_grid, cfg.clahe_grid))
    return clahe.apply(gray)


def preprocess_slot(frame: np.ndarray, cfg: DetectorConfig, slot: SlotConfig, mask: np.ndarray) -> np.ndarray:
    """Optionally isolate the inspection pixels before blur/contrast processing.

    Masking only after full-frame CLAHE still lets floor lighting affect the
    inspected pixels through neighboring tiles. This path removes that coupling.
    """
    if not slot.local_preprocessing:
        return preprocess(frame, cfg)
    if not mask.any():
        return np.zeros(frame.shape[:2], np.uint8)
    x, y, w, h = cv2.boundingRect(mask)
    crop = frame[y:y + h, x:x + w]
    gray = crop.copy() if crop.ndim == 2 else cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY)
    inside = mask[y:y + h, x:x + w] > 0
    median = int(np.median(gray[inside]))
    gray[~inside] = median
    prepared = preprocess(gray, cfg)
    out = np.full(frame.shape[:2], median, np.uint8)
    out[y:y + h, x:x + w] = prepared
    return out


def _normalize_roi(img: np.ndarray, mask: np.ndarray) -> np.ndarray:
    """Shift/scale so the ROI median is 128 -> robust to global brightness change."""
    vals = img[mask > 0]
    if vals.size == 0:
        return img
    med = float(np.median(vals))
    out = img.astype(np.float32) - med + 128.0
    return np.clip(out, 0, 255).astype(np.uint8)


# --------------------------------------------------------------------------- #
# Feature extraction
# --------------------------------------------------------------------------- #
def extract_features(
    prep: np.ndarray,
    mask: np.ndarray,
    slot: SlotConfig,
    ref_norm: Optional[np.ndarray],
    ref_std: Optional[float],
) -> np.ndarray:
    """Return [edge_density, diff_frac, std_ratio] for one slot."""
    inside = mask > 0
    if not inside.any():
        return np.zeros(len(feature_names(slot.feature_version)), np.float32)

    if slot.feature_version == 2:
        # Keep expensive operations local to the slot, with a derivative halo.
        x, y, w, h = cv2.boundingRect(mask)
        roi = np.s_[max(0, y - 2):y + h + 2, max(0, x - 2):x + w + 2]
        prep, mask = prep[roi], mask[roi]
        ref_norm = ref_norm[roi] if ref_norm is not None else None
        inside = mask > 0

    norm = _normalize_roi(prep, mask)

    edges = cv2.Canny(prep, slot.canny_low, slot.canny_high)
    edge_density = float((edges[inside] > 0).mean())

    if ref_norm is not None:
        diff = cv2.absdiff(norm, ref_norm)
        diff_frac = float((diff[inside] > slot.diff_threshold).mean())
    else:
        diff_frac = 0.0

    std = float(norm[inside].std())
    std_ratio = std / ref_std if ref_std and ref_std > 1e-6 else 1.0

    feats = [edge_density, diff_frac, std_ratio]
    if slot.feature_version == 1:
        return np.array(feats, np.float32)
    feature_names(slot.feature_version)  # reject unsupported schemas
    diff = cv2.absdiff(norm, ref_norm) if ref_norm is not None else np.zeros_like(norm)
    changed = ((diff > slot.diff_threshold) & inside).astype(np.uint8)
    _, _, stats, _ = cv2.connectedComponentsWithStats(changed, connectivity=8)
    largest = float(stats[1:, cv2.CC_STAT_AREA].max()) / inside.sum() if len(stats) > 1 else 0.0
    gx = cv2.Sobel(norm, cv2.CV_32F, 1, 0, ksize=3)
    gy = cv2.Sobel(norm, cv2.CV_32F, 0, 1, ksize=3)
    grad = cv2.magnitude(gx, gy)[inside] / 1020.0
    vals = norm[inside].astype(np.float32)
    hist = np.histogram(vals, bins=16, range=(0, 256))[0].astype(float)
    probs = hist[hist > 0] / vals.size
    corr = 0.0
    if ref_norm is not None:
        a = vals - vals.mean()
        b = ref_norm[inside].astype(np.float32)
        b -= b.mean()
        denom = float(np.linalg.norm(a) * np.linalg.norm(b))
        corr = float(np.dot(a, b) / denom) if denom > 1e-6 else float(np.array_equal(norm[inside], ref_norm[inside]))
    feats.extend([float(diff[inside].mean()) / 255, float(np.percentile(diff[inside], 90)) / 255,
                  largest, float(grad.mean()), float(grad.std()),
                  float(np.percentile(vals, 75) - np.percentile(vals, 25)) / 255,
                  float(-(probs * np.log2(probs)).sum()) / 4, corr])
    ys, xs = np.where(inside)
    # Spatial cells preserve where changes occur without resizing the polygon.
    for rows in np.array_split(np.arange(ys.min(), ys.max() + 1), 3):
        for cols in np.array_split(np.arange(xs.min(), xs.max() + 1), 3):
            cell = np.ix_(rows, cols)
            valid = inside[cell]
            feats.append(float(diff[cell][valid].mean()) / 255 if valid.any() else 0.0)
    return np.array(feats, np.float32)


def score_from_features(feats: np.ndarray, slot: SlotConfig) -> float:
    z = float(np.dot(slot.weights, feats) + slot.bias)
    return float(1.0 / (1.0 + np.exp(-np.clip(z, -80, 80))))


def forest_scores(model, features: np.ndarray) -> np.ndarray:
    """Occupied tree-vote fraction, not a calibrated probability."""
    votes = model.getVotes(np.ascontiguousarray(features, dtype=np.float32), 0)
    occupied = np.flatnonzero(votes[0] == 1)
    if len(occupied) != 1 or set(votes[0]) != {0, 1}:
        raise ValueError("Expected a binary empty/occupied forest")
    return votes[1:, occupied[0]] / votes[1:].sum(axis=1)


def state_from_score(score: float, slot: SlotConfig) -> SlotState:
    if score <= slot.t_empty:
        return SlotState.EMPTY
    if score >= slot.t_occupied:
        return SlotState.OCCUPIED
    return SlotState.UNKNOWN


# --------------------------------------------------------------------------- #
# Detector
# --------------------------------------------------------------------------- #
@dataclass
class SlotResult:
    name: str
    score: float
    raw_state: SlotState
    state: SlotState                          # after temporal filtering
    features: np.ndarray


class SlotDetector:
    def __init__(self, cfg: DetectorConfig):
        if cfg.vote_window < 1:
            raise ValueError("vote_window must be positive")
        self.cfg = cfg
        self._masks: Dict[str, np.ndarray] = {}
        self._mask_shape: Optional[Tuple[int, int]] = None
        self._ref_norm: Dict[str, np.ndarray] = {}
        self._ref_std: Dict[str, float] = {}
        self._history: Dict[str, deque] = {
            s.name: deque(maxlen=cfg.vote_window) for s in cfg.slots
        }
        self._stable: Dict[str, SlotState] = {s.name: SlotState.UNKNOWN for s in cfg.slots}
        self._models = {}
        for s in cfg.slots:
            count = len(feature_names(s.feature_version))
            if s.model_path:
                model = cv2.ml.RTrees_load(str(cfg.resolve_path(s.model_path)))
                if not model.isTrained() or model.getVarCount() != count:
                    raise ValueError(f"{s.name}: model/feature schema mismatch")
                self._models[s.name] = model
            elif len(s.weights) != count:
                raise ValueError(f"{s.name}: weights/feature schema mismatch")
            if s.reference_path:
                with np.load(cfg.resolve_path(s.reference_path), allow_pickle=False) as ref:
                    if not np.array_equal(ref["polygon"], np.asarray(s.polygon)):
                        raise ValueError(f"{s.name}: polygon changed; retrain the model")
                    inspection = s.inspection_polygon if s.inspection_polygon is not None else s.polygon
                    saved_inspection = ref["inspection_polygon"] if "inspection_polygon" in ref else ref["polygon"]
                    if not np.array_equal(saved_inspection, np.asarray(inspection)):
                        raise ValueError(f"{s.name}: inspection polygon changed; retrain the model")
                    settings = [cfg.clahe_clip, cfg.clahe_grid, cfg.blur_ksize,
                                s.diff_threshold, s.canny_low, s.canny_high]
                    if s.local_preprocessing:
                        settings.append(1)
                    if not np.array_equal(ref["preprocessing"], settings):
                        raise ValueError(f"{s.name}: preprocessing changed; retrain the model")
                    self._ref_norm[s.name] = ref["norm"]
                    self._ref_std[s.name] = float(ref["std"])

    # -- masks ---------------------------------------------------------------
    def _ensure_masks(self, shape: Tuple[int, int]) -> None:
        if self._mask_shape == shape[:2] and self._masks:
            return
        self._masks = {s.name: inspection_mask(shape, s) for s in self.cfg.slots}
        self._mask_shape = shape[:2]

    def invalidate_masks(self) -> None:
        """Call after editing a polygon."""
        self._masks.clear()
        self._mask_shape = None
        self._ref_norm.clear()
        self._ref_std.clear()
        self.reset_history()

    # -- reference -------------------------------------------------------------
    def set_reference(self, frame: np.ndarray, slot_names: Optional[Sequence[str]] = None) -> None:
        """Store the current frame as the 'empty' reference for the given slots.

        Only call when you KNOW the slots are empty.
        """
        self._ensure_masks(frame.shape[:2])
        self.reset_history()
        shared_prep = preprocess(frame, self.cfg) if any(not s.local_preprocessing for s in self.cfg.slots) else None
        for s in self.cfg.slots:
            if slot_names is not None and s.name not in slot_names:
                continue
            m = self._masks[s.name]
            if not (m > 0).any():
                raise ValueError(f"{s.name}: polygon is outside the reference image")
            prep = preprocess_slot(frame, self.cfg, s, m) if s.local_preprocessing else shared_prep
            norm = _normalize_roi(prep, m)
            self._ref_norm[s.name] = norm
            self._ref_std[s.name] = float(norm[m > 0].std())

    def has_reference(self, name: str) -> bool:
        return name in self._ref_norm

    # -- inference -------------------------------------------------------------
    def features(self, frame: np.ndarray) -> Dict[str, np.ndarray]:
        self._ensure_masks(frame.shape[:2])
        if any(ref.shape != frame.shape[:2] for ref in self._ref_norm.values()):
            raise ValueError("Frame resolution differs from the empty reference; recalibrate at this resolution")
        shared_prep = preprocess(frame, self.cfg) if any(not s.local_preprocessing for s in self.cfg.slots) else None
        return {
            s.name: extract_features(
                (preprocess_slot(frame, self.cfg, s, self._masks[s.name]) if s.local_preprocessing else shared_prep),
                self._masks[s.name], s,
                self._ref_norm.get(s.name), self._ref_std.get(s.name),
            )
            for s in self.cfg.slots
        }

    def update(self, frame: np.ndarray) -> List[SlotResult]:
        feats = self.features(frame)
        results: List[SlotResult] = []
        for s in self.cfg.slots:
            f = feats[s.name]
            model = self._models.get(s.name)
            score = float(forest_scores(model, f[None, :])[0]) if model is not None else score_from_features(f, s)
            raw = state_from_score(score, s)
            if not self._masks[s.name].any() or (s.feature_version == 2 and not self.has_reference(s.name)):
                score, raw = 0.5, SlotState.UNKNOWN
            hist = self._history[s.name]
            hist.append(raw)
            state = self._vote(s.name, hist)
            results.append(SlotResult(s.name, score, raw, state, f))
        return results

    def _vote(self, name: str, hist: deque) -> SlotState:
        """Majority vote with hysteresis: switching state needs a clear majority;
        otherwise keep the previous stable state. Starts as UNKNOWN until the
        window fills so the robot never acts on a single frame."""
        if len(hist) < hist.maxlen:
            return SlotState.UNKNOWN
        n = len(hist)
        occ = sum(1 for h in hist if h == SlotState.OCCUPIED)
        emp = sum(1 for h in hist if h == SlotState.EMPTY)
        need = n // 2 + 1
        prev = self._stable[name]
        if occ >= need:
            new = SlotState.OCCUPIED
        elif emp >= need:
            new = SlotState.EMPTY
        else:
            new = SlotState.UNKNOWN
        # hysteresis: do not flip directly between certain states on a thin margin
        if prev in (SlotState.EMPTY, SlotState.OCCUPIED) and new not in (prev, SlotState.UNKNOWN):
            strong = need + 1 if n >= 5 else need
            if (occ if new == SlotState.OCCUPIED else emp) < strong:
                new = prev
        self._stable[name] = new
        return new

    def reset_history(self) -> None:
        for h in self._history.values():
            h.clear()
        for k in self._stable:
            self._stable[k] = SlotState.UNKNOWN


# --------------------------------------------------------------------------- #
# Overlay (handy for debugging / the Qt widget)
# --------------------------------------------------------------------------- #
STATE_COLORS = {
    SlotState.EMPTY: (80, 200, 80),
    SlotState.OCCUPIED: (60, 60, 230),
    SlotState.UNKNOWN: (0, 200, 255),
}


def draw_overlay(frame: np.ndarray, cfg: DetectorConfig, results: Sequence[SlotResult]) -> np.ndarray:
    out = frame.copy() if frame.ndim == 3 else cv2.cvtColor(frame, cv2.COLOR_GRAY2BGR)
    by_name = {r.name: r for r in results}
    for s in cfg.slots:
        r = by_name.get(s.name)
        color = STATE_COLORS[r.state] if r else (200, 200, 200)
        pts = np.round(np.array(s.polygon)).astype(np.int32)
        cv2.polylines(out, [pts], True, color, 2)
        if s.inspection_polygon is not None:
            core = np.round(np.array(s.inspection_polygon)).astype(np.int32)
            cv2.polylines(out, [core], True, color, 1)
        label = f"{s.name}: {r.state.value} ({r.score:.2f})" if r else s.name
        x, y = pts.min(axis=0)
        cv2.putText(out, label, (int(x), int(y) - 6), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
    return out
