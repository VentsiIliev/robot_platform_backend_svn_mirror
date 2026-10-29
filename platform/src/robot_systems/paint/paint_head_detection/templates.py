"""Reference templates, structural scoring, and spatial candidate extraction."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from typing import NamedTuple, cast

import cv2
import numpy as np

from .configuration import MatchingConfig
from .models import FeatureDefinition, FeatureSupport, FloatImage, Image, Point2D, Region, Vector
from .preprocessing import edge_proximity


@dataclass(frozen=True, slots=True)
class MatchCandidate:
    feature: FeatureDefinition
    score: float
    center: Vector
    angle_degrees: float
    expected_center: Vector


class TemplateData(NamedTuple):
    expected: FloatImage
    proximity: FloatImage
    edge_count: float
    support: FloatImage | None


class PreparedTemplate(NamedTuple):
    image: Image
    data: TemplateData


type TemplateKey = tuple[int, FeatureDefinition, float]


def _rotated_template(
    reference: Image, feature: FeatureDefinition, angle: float
) -> tuple[Image, Point2D]:
    """Rotate only the selected feature, without importing its surroundings."""
    x, y, w, h = feature.region.coordinates
    center = feature.region.center
    patch = reference[y : y + h, x : x + w]
    if angle == 0:
        return (patch, center)
    matrix = cast(Vector, cv2.getRotationMatrix2D((w / 2, h / 2), angle, 1.0))
    tw = int(np.ceil(w * abs(matrix[0, 0]) + h * abs(matrix[0, 1])))
    th = int(np.ceil(h * abs(matrix[0, 0]) + w * abs(matrix[0, 1])))
    matrix[:, 2] += np.array([(tw - w) / 2, (th - h) / 2], dtype=np.float64)
    rotated = cast(
        Image,
        cv2.warpAffine(
            patch,
            matrix,
            (tw, th),
            flags=cv2.INTER_NEAREST,
            borderMode=cv2.BORDER_CONSTANT,
            borderValue=0,
        ),
    )
    return (rotated, center)


def _shape_scores(
    search: Image,
    template: Image,
    target_near: FloatImage | None = None,
    template_data: TemplateData | None = None,
    *,
    settings: MatchingConfig,
) -> FloatImage:
    """Symmetric soft edge overlap, allowing roughly two pixels of edge drift.

    Recall rewards the expected contour; precision penalizes unrelated clutter.
    Unlike exact binary correlation this tolerates small lighting-induced shifts.
    Scores are structural similarity, not calibrated probabilities.
    """
    target = (search > 0).astype(np.float32)
    if template_data is None:
        expected = (template > 0).astype(np.float32)
        expected_near = edge_proximity(template, settings.edge_distance_sigma)
        expected_count = float(expected.sum())
        support = None
    else:
        expected, expected_near, expected_count, support = template_data
    shape = (search.shape[0] - template.shape[0] + 1, search.shape[1] - template.shape[1] + 1)
    if not np.any(target) or expected_count == 0:
        return np.zeros(shape, dtype=np.float32)
    if target_near is None:
        target_near = edge_proximity(search, settings.edge_distance_sigma)
    recall = cv2.matchTemplate(target_near, expected, cv2.TM_CCORR) / expected_count
    if support is None:
        integral = cv2.integral(target)
        th, tw = template.shape
        counts = (
            integral[th:, tw:] - integral[:-th, tw:] - integral[th:, :-tw] + integral[:-th, :-tw]
        ).astype(np.float32)
    else:
        counts = cast(FloatImage, cv2.matchTemplate(target, support, cv2.TM_CCORR))
    precision = cv2.matchTemplate(target, expected_near, cv2.TM_CCORR) / np.maximum(counts, 1)
    scores = 2 * precision * recall / np.maximum(precision + recall, 1e-06)
    return cast(FloatImage, np.clip(scores, 0, 1))


def _candidate_matches(
    ref_edges: Image,
    current_edges: Image,
    feature: FeatureDefinition,
    margin: int,
    angles: Sequence[float],
    top_k: int | None = None,
    search_rect: Region | None = None,
    template_cache: dict[TemplateKey, PreparedTemplate] | None = None,
    current_proximity: FloatImage | None = None,
    *,
    settings: MatchingConfig,
) -> list[MatchCandidate]:
    """Generate multiple plausible matches instead of taking only one maximum."""
    x, y, w, h = feature.region.coordinates
    expected = np.array([x + w / 2, y + h / 2], dtype=float)
    top_k = settings.top_candidates if top_k is None else top_k
    bx, by, bw, bh = (
        search_rect.coordinates
        if search_rect is not None
        else (0, 0, ref_edges.shape[1], ref_edges.shape[0])
    )
    if feature.orientation_invariant:
        angles = [0]
        margin = max(bw, bh)
        top_k = max(top_k, settings.invariant_candidates)
    elif feature.max_template_rotation is not None:
        angles = [a for a in angles if abs(a) <= feature.max_template_rotation]
    candidates: list[MatchCandidate] = []
    for angle in angles:
        key = (id(ref_edges), feature, angle)
        cached = template_cache.get(key) if template_cache is not None else None
        if cached is None:
            template, _ = _rotated_template(ref_edges, feature, angle)
            expected_edges = (template > 0).astype(np.float32)
            support = None
            if feature.support == FeatureSupport.CIRCLE:
                th, tw = template.shape
                yy, xx = np.ogrid[:th, :tw]
                support = (
                    (xx - (tw - 1) / 2) ** 2 + (yy - (th - 1) / 2) ** 2 < (min(th, tw) / 2 - 1) ** 2
                ).astype(np.float32)
                expected_edges *= support
            expected_near = edge_proximity(expected_edges, settings.edge_distance_sigma)
            if support is not None:
                expected_near *= support
            cached = PreparedTemplate(
                template,
                TemplateData(expected_edges, expected_near, float(expected_edges.sum()), support),
            )
            if template_cache is not None:
                template_cache[key] = cached
        template, template_data = cached
        th, tw = template.shape
        sx = max(bx, int(expected[0] - margin - tw / 2))
        sy = max(by, int(expected[1] - margin - th / 2))
        ex = min(bx + bw, int(np.ceil(expected[0] + margin + tw / 2)))
        ey = min(by + bh, int(np.ceil(expected[1] + margin + th / 2)))
        search = current_edges[sy:ey, sx:ex]
        if search.shape[0] < th or search.shape[1] < tw or template_data.edge_count == 0:
            continue
        near = current_proximity[sy:ey, sx:ex] if current_proximity is not None else None
        scores = _shape_scores(search, template, near, template_data, settings=settings)
        scores = np.nan_to_num(scores, nan=-1, posinf=-1, neginf=-1)
        if feature.orientation_invariant:
            peaks = (scores >= float(feature.threshold) * settings.candidate_score_ratio) & (
                scores
                == cv2.dilate(
                    scores, np.ones((settings.peak_window, settings.peak_window), np.uint8)
                )
            )
            py, px = np.nonzero(peaks)
            peak_scores = scores[py, px]
            order = np.argsort(-peak_scores, kind="stable")[:top_k]
            centers = np.column_stack((sx + px[order] + tw / 2, sy + py[order] + th / 2))
            candidates.extend(
                (
                    MatchCandidate(
                        feature=feature,
                        score=float(score),
                        center=center,
                        angle_degrees=float(angle),
                        expected_center=expected,
                    )
                    for score, center in zip(peak_scores[order], centers, strict=True)
                )
            )
            continue
        for _ in range(top_k):
            _, score, _, pos = cv2.minMaxLoc(scores)
            if score < float(feature.threshold) * settings.candidate_score_ratio:
                break
            observed = np.array([sx + pos[0] + tw / 2, sy + pos[1] + th / 2])
            candidates.append(
                MatchCandidate(
                    feature=feature,
                    score=float(score),
                    center=observed,
                    angle_degrees=float(angle),
                    expected_center=expected,
                )
            )
            cv2.circle(scores, pos, settings.suppression_radius, -1, -1)
    return sorted(candidates, key=lambda c: c.score, reverse=True)
