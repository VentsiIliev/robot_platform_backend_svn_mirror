"""Prepare a schematic operator compass without exposing detector geometry."""

from dataclasses import dataclass, replace
from enum import Enum, auto
from math import hypot, isfinite
from typing import NamedTuple

from src.robot_systems.paint.contracts.paint_head_check.guidance import (
    HeadRotationCorrection,
    PaintHeadCorrection,
)


class GuidePoint(NamedTuple):
    x: float
    y: float


class GuideRotation(Enum):
    NONE = auto()
    CLOCKWISE = auto()
    COUNTERCLOCKWISE = auto()


class GuideAvailability(Enum):
    AVAILABLE = auto()
    UNAVAILABLE = auto()


@dataclass(frozen=True, slots=True)
class HeadAlignmentGuideData:
    """Directions only; marker displacement and tilt are schematic UI choices."""

    translation_direction: GuidePoint | None
    rotation_direction: GuideRotation
    aligned: bool
    translation_extent: float
    rotation_extent: float
    availability: GuideAvailability = GuideAvailability.AVAILABLE
    show_head_reference: bool = True


def unavailable_head_alignment_guide(
    previous: HeadAlignmentGuideData | None,
    *,
    show_head_reference: bool = True,
) -> HeadAlignmentGuideData:
    """Keep a grey historical marker; it must never render as actionable or aligned."""
    if previous is not None:
        return replace(
            previous,
            aligned=False,
            availability=GuideAvailability.UNAVAILABLE,
            show_head_reference=show_head_reference,
        )
    return HeadAlignmentGuideData(
        None,
        GuideRotation.NONE,
        False,
        0.0,
        0.0,
        GuideAvailability.UNAVAILABLE,
        show_head_reference,
    )


def build_head_alignment_guide(
    correction: PaintHeadCorrection,
    *,
    confirmed_present: bool = False,
) -> HeadAlignmentGuideData | None:
    """Validate directions; green alignment also requires a confirmed present state."""
    if correction.image_width <= 0 or correction.image_height <= 0:
        return None
    if not all(
        isfinite(value) and 0.0 <= value <= 1.0
        for value in (
            correction.translation_extent,
            correction.rotation_extent,
        )
    ):
        return None
    direction = None
    if correction.translation_direction is not None:
        x, y = correction.translation_direction
        # Resolve normalized image axes here so the widget has no camera dependency.
        x, y = x * correction.image_width, y * correction.image_height
        length = hypot(x, y)
        if not isfinite(length) or length <= 1e-12:
            return None
        direction = GuidePoint(x / length, y / length)
    rotations = {
        HeadRotationCorrection.NONE: GuideRotation.NONE,
        HeadRotationCorrection.CLOCKWISE: GuideRotation.CLOCKWISE,
        HeadRotationCorrection.COUNTERCLOCKWISE: GuideRotation.COUNTERCLOCKWISE,
    }
    rotation = rotations[correction.rotation_direction]
    return HeadAlignmentGuideData(
        translation_direction=direction,
        rotation_direction=rotation,
        aligned=confirmed_present and direction is None and rotation is GuideRotation.NONE,
        translation_extent=correction.translation_extent if direction is not None else 0.0,
        rotation_extent=correction.rotation_extent if rotation is not GuideRotation.NONE else 0.0,
    )


@dataclass(frozen=True, slots=True)
class HeadAlignmentFeedback:
    """One complete translated popup update; independent of detector and Qt."""

    guide: HeadAlignmentGuideData
    status_text: str
    notice: str
    attention: bool
