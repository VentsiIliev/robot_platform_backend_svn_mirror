"""Compose reference matching and positive evidence for head presence/absence."""

from __future__ import annotations

import numpy as np

from .configuration import CalibrationConfig, MatchingConfig
from .consensus import _consensus_present, _match_group
from .geometry import _relative_geometry
from .models import (
    FeatureDefinition,
    FeatureRole,
    FloatImage,
    Image,
    MissingEvidence,
    PresentEvidence,
)
from .templates import (
    MatchCandidate,
    PreparedTemplate,
    TemplateKey,
    _candidate_matches,
    _shape_scores,
)


def _same_position_similarity(
    template: Image, candidate: Image, *, settings: MatchingConfig
) -> float:
    if np.std(template) < 1e-06 or np.std(candidate) < 1e-06:
        return 0.0
    score = float(_shape_scores(candidate, template, settings=settings)[0, 0])
    return score if np.isfinite(score) else 0.0


class FeatureMatcher:
    """Owns immutable references and the reusable rotated-template cache."""

    def __init__(
        self,
        present_edges: Image,
        missing_edges: Image,
        calibration: CalibrationConfig,
        settings: MatchingConfig,
    ) -> None:
        self._present_edges = present_edges
        self._missing_edges = missing_edges
        self._calibration = calibration
        self._settings = settings
        self._cache: dict[TemplateKey, PreparedTemplate] = {}
        angles = list(
            range(-settings.max_rotation, settings.max_rotation + 1, settings.rotation_step)
        )
        if 0 not in angles:
            angles.append(0)
        self._angles = tuple(angles)
        self._plate_template = missing_edges[calibration.empty_mount_region.slices]

    @property
    def rotation_angles(self) -> tuple[int, ...]:
        return self._angles

    def match_present(self, edges: Image, proximity: FloatImage) -> PresentEvidence:
        c, s = (self._calibration, self._settings)
        return _consensus_present(
            self._present_edges,
            edges,
            c.present_features,
            s.search_margin,
            self._angles,
            s.consensus_tolerance,
            s.min_present_features,
            c.inspection_region,
            self._cache,
            proximity,
            settings=s,
        )

    def match_missing(self, edges: Image, proximity: FloatImage) -> MissingEvidence:
        c, s = (self._calibration, self._settings)
        matches = _match_group(
            self._missing_edges,
            edges,
            c.missing_features,
            s.search_margin,
            c.inspection_region,
            self._cache,
            proximity,
            settings=s,
        )
        plate = _same_position_similarity(
            self._plate_template, edges[c.empty_mount_region.slices], settings=s
        )
        landmarks = tuple(m for m in matches if m.feature.role is not FeatureRole.EMPTY_MOUNT)
        count = sum(m.passed for m in landmarks)
        geometry = (
            _relative_geometry(landmarks, s.relative_tolerance) if c.missing_features else None
        )
        verified = plate >= s.plate_threshold
        if c.missing_features:
            verified = verified and count >= s.min_missing_features and (geometry is True)
        return MissingEvidence(matches, bool(verified), plate, count, geometry)

    def candidates(
        self, edges: Image, proximity: FloatImage, feature: FeatureDefinition
    ) -> tuple[MatchCandidate, ...]:
        return tuple(
            _candidate_matches(
                self._present_edges,
                edges,
                feature,
                self._settings.search_margin,
                self._angles,
                self._settings.top_candidates,
                self._calibration.inspection_region,
                self._cache,
                proximity,
                settings=self._settings,
            )
        )
