"""Typed domain values shared by the detector and its consumers."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import NamedTuple

import numpy as np
from numpy.typing import NDArray

type Image = NDArray[np.uint8]
type FloatImage = NDArray[np.float32]
type Vector = NDArray[np.float64]
type BoolMask = NDArray[np.bool_]
type PixelPoint = tuple[int, int]


@dataclass(frozen=True, slots=True, eq=False)
class ReferenceImages:
    """Caller-supplied full-frame BGR uint8 calibration images.

    The detector snapshots these arrays; it never changes the caller's buffers.
    """

    present: Image = field(repr=False)
    missing: Image = field(repr=False)


class HeadStatus(Enum):
    HEAD_PRESENT = "HEAD_PRESENT"
    HEAD_MISALIGNED = "HEAD_MISALIGNED"
    HEAD_MISSING = "HEAD_MISSING"
    UNKNOWN = "UNKNOWN"


class DetectionReason(Enum):
    ALIGNED = "aligned"
    MISALIGNED = "misaligned"
    EMPTY_MOUNT = "empty_mount"
    INSUFFICIENT_EVIDENCE = "insufficient_evidence"
    CONFLICTING_EVIDENCE = "conflicting_evidence"
    POSE_UNDETERMINED = "pose_undetermined"
    TOO_DARK = "too_dark"
    OVEREXPOSED = "overexposed"
    LOW_CONTRAST = "low_contrast"
    CONFIRMING_STATUS = "confirming_status"
    RECHECKING_POSITION = "rechecking_position"


class FeatureRole(Enum):
    PRESENT = "present"
    MISSING = "missing"
    EMPTY_MOUNT = "empty_mount"


class FeatureSupport(Enum):
    RECTANGLE = "rectangle"
    CIRCLE = "circle"


class Point2D(NamedTuple):
    x: float
    y: float


@dataclass(frozen=True, slots=True)
class ImageSize:
    width: int
    height: int


@dataclass(frozen=True, slots=True)
class Region:
    x: int
    y: int
    width: int
    height: int

    @property
    def center(self) -> Point2D:
        return Point2D(self.x + self.width / 2, self.y + self.height / 2)

    @property
    def slices(self) -> tuple[slice, slice]:
        return slice(self.y, self.y + self.height), slice(self.x, self.x + self.width)

    @property
    def coordinates(self) -> tuple[int, int, int, int]:
        return self.x, self.y, self.width, self.height

    def contains(self, other: Region) -> bool:
        return (
            other.x >= self.x
            and other.y >= self.y
            and other.x + other.width <= self.x + self.width
            and other.y + other.height <= self.y + self.height
        )

    def intersection(self, other: Region) -> Region:
        x, y = max(self.x, other.x), max(self.y, other.y)
        return Region(
            x,
            y,
            min(self.x + self.width, other.x + other.width) - x,
            min(self.y + self.height, other.y + other.height) - y,
        )


@dataclass(frozen=True, slots=True)
class FeatureDefinition:
    name: str
    region: Region
    threshold: float
    role: FeatureRole
    required: bool = False
    orientation_invariant: bool = False
    support: FeatureSupport = FeatureSupport.RECTANGLE
    max_template_rotation: float | None = None


@dataclass(frozen=True, slots=True)
class FeatureMatch:
    feature: FeatureDefinition
    score: float
    position: PixelPoint
    shift: PixelPoint
    center: Point2D | None
    passed: bool
    inlier: bool
    rotation_degrees: float


@dataclass(frozen=True, slots=True)
class PoseEstimate:
    rotation_degrees: float
    offset: Point2D

    @property
    def translation_pixels(self) -> float:
        return float(np.hypot(self.offset.x, self.offset.y))


@dataclass(frozen=True, slots=True)
class AlignmentMeasurement:
    aligned: bool
    translation_pixels: float
    rotation_degrees: float
    max_translation_pixels: float
    max_rotation_degrees: float
    recovery_pixel_limit: float
    recovery_degree_limit: float
    recovering: bool


@dataclass(frozen=True, slots=True)
class ImageQuality:
    issue: DetectionReason | None

    @property
    def usable(self) -> bool:
        return self.issue is None


@dataclass(frozen=True, slots=True)
class PresentEvidence:
    matches: tuple[FeatureMatch, ...]
    verified: bool
    pose: PoseEstimate
    inlier_count: int


@dataclass(frozen=True, slots=True)
class MissingEvidence:
    matches: tuple[FeatureMatch, ...]
    verified: bool
    plate_similarity: float
    landmark_count: int
    geometry_consistent: bool | None


@dataclass(frozen=True, slots=True)
class FrameEvidence:
    present: PresentEvidence
    missing: MissingEvidence
    quality: ImageQuality
    edges: Image = field(repr=False, compare=False)


@dataclass(frozen=True, slots=True)
class DetectionDiagnostics:
    present: PresentEvidence
    missing: MissingEvidence
    quality: ImageQuality
    pose: PoseEstimate
    edges: Image = field(repr=False, compare=False)


@dataclass(frozen=True, slots=True)
class DetectionResult:
    """One ordered stream observation; UNKNOWN is a valid detection outcome.

    `status` includes confirmation/hysteresis. `observed_status` describes the
    current image before temporal filtering. Diagnostics never mutate the input.
    """

    status: HeadStatus
    observed_status: HeadStatus
    reason: DetectionReason
    message: str
    alignment: AlignmentMeasurement | None
    held_warning: bool
    timestamp: float
    configuration_revision: int
    diagnostics: DetectionDiagnostics
