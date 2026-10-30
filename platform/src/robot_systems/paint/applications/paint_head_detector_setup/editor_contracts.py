"""Typed interaction values shared by MVC components; no Qt or services."""

from dataclasses import dataclass
from enum import Enum, auto

from src.robot_systems.paint.contracts.paint_head_calibration.models import (
    LandmarkRole,
    LandmarkSupport,
    ObjectId,
    Region,
)


class SetupPage(Enum):
    PROFILES = auto()
    CAMERA = auto()
    REGIONS = auto()
    TEST = auto()
    SETTINGS = auto()


class EditorKind(Enum):
    INSPECTION = auto()
    EMPTY_MOUNT = auto()
    EXCLUDED = auto()
    LANDMARK = auto()


class EditorTool(Enum):
    SELECT = auto()
    PAN = auto()
    INSPECTION = auto()
    EMPTY_MOUNT = auto()
    EXCLUDED = auto()
    RECTANGLE_LANDMARK = auto()
    CIRCLE_LANDMARK = auto()


class UnsavedDecision(Enum):
    SAVE = auto()
    DISCARD = auto()
    CANCEL = auto()


@dataclass(frozen=True, slots=True)
class EditorTarget:
    kind: EditorKind
    object_id: ObjectId | None


@dataclass(frozen=True, slots=True)
class EditorObject:
    target: EditorTarget
    name: str
    region: Region
    support: LandmarkSupport
    role: LandmarkRole | None = None


@dataclass(frozen=True, slots=True)
class GeometryEdit:
    target: EditorTarget
    region: Region
    support: LandmarkSupport
    role: LandmarkRole


@dataclass(frozen=True, slots=True)
class ObjectPropertiesEdit:
    target: EditorTarget
    name: str
    x: int
    y: int
    width: int
    height: int
    threshold: float
    role: LandmarkRole
    required: bool
    orientation_invariant: bool
    support: LandmarkSupport
    max_template_rotation: float | None
