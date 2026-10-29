"""Operator correction directions, without detection features or pose geometry."""

from dataclasses import dataclass
from enum import Enum, auto
from typing import NamedTuple


class HeadCorrectionDirection(NamedTuple):
    """Unit direction in normalized image axes: right is +X, down is +Y."""

    x: float
    y: float


class HeadRotationCorrection(Enum):
    NONE = auto()
    CLOCKWISE = auto()
    COUNTERCLOCKWISE = auto()


@dataclass(frozen=True, slots=True)
class PaintHeadCorrection:
    """Directions and bounded schematic extents for one valid inspection.

    Translation is normalized after dividing each axis by its frame dimension.
    The GUI can preserve direction across display aspect ratios without receiving
    a measured distance, pivot, landmark, or robot motion command. Frame size is
    retained only to associate the correction with a compatible camera frame.
    No translation direction and NONE rotation mean no correction is required.
    """

    image_width: int
    image_height: int
    translation_direction: HeadCorrectionDirection | None
    rotation_direction: HeadRotationCorrection
    translation_extent: float
    rotation_extent: float
