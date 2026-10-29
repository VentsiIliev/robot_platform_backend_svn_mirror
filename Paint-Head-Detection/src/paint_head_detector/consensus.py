"""Vectorized association of distinct landmarks to a shared rigid pose."""

from __future__ import annotations

from collections.abc import Sequence

import numpy as np

from .configuration import MatchingConfig
from .geometry import _pixel_shift, _point
from .models import (
    FeatureDefinition,
    FeatureMatch,
    FloatImage,
    Image,
    PoseEstimate,
    PresentEvidence,
    Region,
)
from .templates import MatchCandidate, PreparedTemplate, TemplateKey, _candidate_matches


def _match_group(
    ref_edges: Image,
    current_edges: Image,
    features: tuple[FeatureDefinition, ...],
    margin: int,
    search_rect: Region | None = None,
    template_cache: dict[TemplateKey, PreparedTemplate] | None = None,
    current_proximity: FloatImage | None = None,
    *,
    settings: MatchingConfig,
) -> tuple[FeatureMatch, ...]:
    """Unrotated matches, retained for the missing-plate features."""
    matches = []
    for feature in features:
        candidates = _candidate_matches(
            ref_edges,
            current_edges,
            feature,
            margin,
            [0],
            1,
            search_rect,
            template_cache,
            current_proximity,
            settings=settings,
        )
        if candidates:
            best = candidates[0]
            shift = _pixel_shift(best.center - best.expected_center)
            position = (
                int(round(best.center[0] - feature.region.width / 2)),
                int(round(best.center[1] - feature.region.height / 2)),
            )
            score = best.score
        else:
            position = (int(feature.region.x), int(feature.region.y))
            shift = (0, 0)
            score = 0.0
        matches.append(
            FeatureMatch(
                feature=feature,
                score=score,
                position=position,
                passed=score >= float(feature.threshold),
                shift=shift,
                rotation_degrees=0.0,
                inlier=False,
                center=_point(best.center) if candidates else None,
            )
        )
    return tuple(matches)


def _consensus_present(
    ref_edges: Image,
    current_edges: Image,
    features: tuple[FeatureDefinition, ...],
    margin: int,
    angles: Sequence[float],
    tolerance: float,
    min_features: int,
    search_rect: Region | None = None,
    template_cache: dict[TemplateKey, PreparedTemplate] | None = None,
    current_proximity: FloatImage | None = None,
    *,
    settings: MatchingConfig,
) -> PresentEvidence:
    selected: list[MatchCandidate | None]
    "Find a rigid rotation+translation supported by multiple distinct features."
    all_candidates = [
        _candidate_matches(
            ref_edges,
            current_edges,
            f,
            margin,
            angles,
            search_rect=search_rect,
            template_cache=template_cache,
            current_proximity=current_proximity,
            settings=settings,
        )
        for f in features
    ]
    origin = np.mean(
        [[f.region.x + f.region.width / 2, f.region.y + f.region.height / 2] for f in features],
        axis=0,
    )
    flat = [candidate for options in all_candidates for candidate in options]
    if not flat:
        selected, angle, offset = ([None] * len(features), 0.0, np.zeros(2))
    else:
        centers = np.array([c.center for c in flat])
        expected = np.array([c.expected_center for c in flat])
        candidate_angles = np.array([c.angle_degrees for c in flat])
        scores = np.array([c.score for c in flat])
        thresholds = np.array([c.feature.threshold for c in flat], dtype=float)
        invariant = np.array([c.feature.orientation_invariant for c in flat])
        groups = np.repeat(np.arange(len(features)), [len(options) for options in all_candidates])
        anchor_expected, anchor_observed = (expected, centers)
        hypothesis_angles = candidate_angles
        first, second = np.triu_indices(len(flat), 1)
        ref_vectors = expected[second] - expected[first]
        seen_vectors = centers[second] - centers[first]
        ref_lengths = np.linalg.norm(ref_vectors, axis=1)
        seen_lengths = np.linalg.norm(seen_vectors, axis=1)
        pair_angles = np.rad2deg(
            np.arctan2(
                ref_vectors[:, 1] * seen_vectors[:, 0] - ref_vectors[:, 0] * seen_vectors[:, 1],
                np.sum(ref_vectors * seen_vectors, axis=1),
            )
        )
        pairs = (
            invariant[first]
            & invariant[second]
            & (groups[first] != groups[second])
            & (scores[first] >= thresholds[first])
            & (scores[second] >= thresholds[second])
            & (ref_lengths > settings.minimum_pair_baseline)
            & (np.abs(ref_lengths - seen_lengths) <= settings.pair_tolerance_multiplier * tolerance)
            & (np.abs(pair_angles) <= max(abs(a) for a in angles) + 1e-06)
        )
        if np.any(pairs):
            anchor_expected = np.concatenate((expected, expected[first[pairs]]))
            anchor_observed = np.concatenate((centers, centers[first[pairs]]))
            hypothesis_angles = np.concatenate((candidate_angles, pair_angles[pairs]))
        theta = np.deg2rad(hypothesis_angles)
        cosine, sine = (np.cos(theta), np.sin(theta))
        rotations = np.stack((cosine, sine, -sine, cosine), axis=1).reshape(-1, 2, 2)
        delta = expected[None, :, :] - anchor_expected[:, None, :]
        predicted = anchor_observed[:, None, :] + np.einsum("aij,acj->aci", rotations, delta)
        residuals = np.sqrt(np.sum((centers[None, :, :] - predicted) ** 2, axis=2))
        valid = (
            (
                (
                    np.abs(hypothesis_angles[:, None] - candidate_angles[None, :])
                    <= settings.angle_tolerance
                )
                | invariant[None, :]
            )
            & (residuals <= tolerance)
            & (scores[None, :] >= thresholds[None, :])
        )
        membership = groups[None, :] == np.arange(len(features))[:, None]
        utility = np.where(
            valid[:, None, :] & membership[None, :, :],
            scores[None, None, :] - settings.residual_weight * residuals[:, None, :],
            -np.inf,
        )
        choices = np.argmax(utility, axis=2)
        supported = np.isfinite(np.max(utility, axis=2))
        counts = supported.sum(axis=1)
        quality = np.where(supported, np.max(utility, axis=2), 0).sum(axis=1)
        offsets = anchor_observed - (
            origin + np.einsum("aij,aj->ai", rotations, anchor_expected - origin)
        )
        order = np.lexsort(
            (
                -np.arange(len(hypothesis_angles)),
                -np.linalg.norm(offsets, axis=1),
                -np.abs(hypothesis_angles),
                quality,
                counts,
            )
        )
        winner = order[-1]
        selected = [
            flat[index] if passed else None
            for index, passed in zip(choices[winner], supported[winner], strict=True)
        ]
        angle, offset = (hypothesis_angles[winner], offsets[winner])
    matches = []
    for feature, chosen, options in zip(features, selected, all_candidates, strict=True):
        display = chosen or (options[0] if options else None)
        if display:
            center = display.center
            pos = (
                int(round(center[0] - feature.region.width / 2)),
                int(round(center[1] - feature.region.height / 2)),
            )
            shift = _pixel_shift(center - display.expected_center)
            score = display.score
        else:
            pos = (int(feature.region.x), int(feature.region.y))
            shift = (0, 0)
            score = 0.0
        matches.append(
            FeatureMatch(
                feature=feature,
                score=score,
                position=pos,
                shift=shift,
                center=_point(display.center) if display else None,
                passed=chosen is not None,
                inlier=chosen is not None,
                rotation_degrees=angle if chosen else 0.0,
            )
        )
    count = sum(m.inlier for m in matches)
    required_passed = all(m.passed for m in matches if m.feature.required)
    return PresentEvidence(
        tuple(matches),
        count >= min_features and required_passed,
        PoseEstimate(float(angle), _point(offset)),
        count,
    )
