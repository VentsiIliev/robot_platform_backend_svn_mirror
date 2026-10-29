"""Typed geometry estimates and landmark consistency checks."""

from __future__ import annotations

import numpy as np

from .models import FeatureMatch, Point2D, PoseEstimate, Vector


def _point(vector: Vector) -> Point2D:
    return Point2D(float(vector[0]), float(vector[1]))


def _pixel_shift(vector: Vector) -> tuple[int, int]:
    return (int(round(vector[0])), int(round(vector[1])))


def fitted_pose(matches: tuple[FeatureMatch, ...]) -> PoseEstimate | None:
    """Fit image-plane rotation and centroid displacement from agreed features.

    Numerical fitting uses array operations; the coarse template rotation grid
    is only for finding correspondences, not for measuring installation error.
    """
    inliers = [match for match in matches if match.inlier]
    if len(inliers) < 2:
        return None
    expected = np.array(
        [
            [
                m.feature.region.x + m.feature.region.width / 2,
                m.feature.region.y + m.feature.region.height / 2,
            ]
            for m in inliers
        ]
    )
    observed = np.array([m.center for m in inliers])
    source_mean, target_mean = (expected.mean(axis=0), observed.mean(axis=0))
    source, target = (expected - source_mean, observed - target_mean)
    if np.sum(source**2) < 1e-06:
        return None
    dot: np.float64 = np.sum(source * target)
    cross: np.float64 = np.sum(source[:, 1] * target[:, 0] - source[:, 0] * target[:, 1])
    angle = np.arctan2(cross, dot)
    rotation = np.array([[np.cos(angle), np.sin(angle)], [-np.sin(angle), np.cos(angle)]])
    origin = np.mean(
        [
            [
                m.feature.region.x + m.feature.region.width / 2,
                m.feature.region.y + m.feature.region.height / 2,
            ]
            for m in matches
        ],
        axis=0,
    )
    offset = target_mean - (origin + rotation @ (source_mean - origin))
    return PoseEstimate(float(np.rad2deg(angle)), _point(offset))


def _relative_geometry(matches: tuple[FeatureMatch, ...], tolerance: float) -> bool | None:
    passed = [m for m in matches if m.passed]
    if len(passed) < 2:
        return None
    xs = [m.shift[0] for m in passed]
    ys = [m.shift[1] for m in passed]
    return max(xs) - min(xs) <= tolerance and max(ys) - min(ys) <= tolerance
