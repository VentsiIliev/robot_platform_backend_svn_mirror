"""Immutable calibration values; no detector, image library, Qt or filesystem I/O."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum, auto
from uuid import UUID, uuid4

from src.robot_systems.paint.component_ids import CameraRoleID, MovementGroupID
from src.robot_systems.paint.contracts.paint_head_check.models import (
    PaintHeadObservationReason,
    PaintHeadState,
)

from .errors import (
    CalibrationFailure,
    CalibrationFailureCode,
    CalibrationValidationError,
    PaintHeadCalibrationError,
)
from .tuning import DetectorTuning
from .validation import finite_number, integer, text


@dataclass(frozen=True, slots=True)
class ProfileId:
    value: str

    def __post_init__(self) -> None:
        try:
            valid = isinstance(self.value, str) and UUID(self.value).hex == self.value
        except (ValueError, AttributeError):
            valid = False
        if not valid:
            raise CalibrationValidationError("Profile identity must be a canonical UUID hex value")

    @classmethod
    def new(cls) -> ProfileId:
        return cls(uuid4().hex)


@dataclass(frozen=True, slots=True)
class ObjectId:
    value: str

    def __post_init__(self) -> None:
        try:
            valid = isinstance(self.value, str) and UUID(self.value).hex == self.value
        except (ValueError, AttributeError):
            valid = False
        if not valid:
            raise CalibrationValidationError("Calibration-object identity must be a UUID hex value")

    @classmethod
    def new(cls) -> ObjectId:
        return cls(uuid4().hex)


@dataclass(frozen=True, slots=True)
class AssetId:
    value: str

    def __post_init__(self) -> None:
        if (
            not isinstance(self.value, str)
            or len(self.value) != 64
            or any(character not in "0123456789abcdef" for character in self.value)
        ):
            raise CalibrationValidationError("Reference identity must be a SHA-256 hex digest")


@dataclass(frozen=True, slots=True)
class RevisionRef:
    profile_id: ProfileId
    number: int

    def __post_init__(self) -> None:
        if not isinstance(self.profile_id, ProfileId):
            raise CalibrationValidationError("Revision requires a typed profile identity")
        integer(self.number, "Revision number", minimum=1)


@dataclass(frozen=True, slots=True)
class ImageSize:
    width: int
    height: int

    def __post_init__(self) -> None:
        integer(self.width, "Image width", minimum=2)
        integer(self.height, "Image height", minimum=2)


@dataclass(frozen=True, slots=True)
class ImagePixels:
    size: ImageSize
    bgr: bytes

    def __post_init__(self) -> None:
        if (
            not isinstance(self.bgr, bytes)
            or len(self.bgr) != self.size.width * self.size.height * 3
        ):
            raise CalibrationValidationError("Image must contain owned full-frame BGR bytes")


@dataclass(frozen=True, slots=True)
class ImageFrame:
    """Owned capture pixels and identity; reference previews do not invent frame metadata."""

    image: ImagePixels
    sequence: int
    captured_at_monotonic: float

    def __post_init__(self) -> None:
        integer(self.sequence, "Frame sequence", minimum=1)
        finite_number(self.captured_at_monotonic, "Frame capture time")


@dataclass(frozen=True, slots=True)
class LandmarkEvidence:
    object_id: ObjectId
    name: str
    score: float
    passed: bool
    inlier: bool
    reference_region: Region
    shift_x: int
    shift_y: int


@dataclass(frozen=True, slots=True)
class CalibrationEvaluation:
    state: PaintHeadState
    observed_state: PaintHeadState
    reason: PaintHeadObservationReason
    held_warning: bool
    image_usable: bool
    frame_sequence: int
    generation: int
    translation_pixels: float | None
    offset_x_pixels: float | None
    offset_y_pixels: float | None
    rotation_degrees: float | None
    evidence: tuple[LandmarkEvidence, ...]


@dataclass(frozen=True, slots=True)
class ReferenceAsset:
    asset_id: AssetId
    size: ImageSize


class ReferenceRole(StrEnum):
    PRESENT = auto()
    MISSING = auto()


@dataclass(frozen=True, slots=True)
class References:
    present: ReferenceAsset | None
    missing: ReferenceAsset | None

    def assets(self) -> tuple[ReferenceAsset, ...]:
        return tuple(asset for asset in (self.present, self.missing) if asset is not None)


@dataclass(frozen=True, slots=True)
class InspectionBinding:
    camera_role: CameraRoleID
    movement_group: MovementGroupID

    def __post_init__(self) -> None:
        if not isinstance(self.camera_role, CameraRoleID) or not isinstance(
            self.movement_group, MovementGroupID
        ):
            raise CalibrationValidationError(
                "Inspection requires typed camera and movement-group IDs"
            )


@dataclass(frozen=True, slots=True)
class Region:
    x: int
    y: int
    width: int
    height: int

    def __post_init__(self) -> None:
        integer(self.x, "Region x")
        integer(self.y, "Region y")
        integer(self.width, "Region width", minimum=2)
        integer(self.height, "Region height", minimum=2)

    def fits(self, size: ImageSize) -> bool:
        return self.x + self.width <= size.width and self.y + self.height <= size.height


@dataclass(frozen=True, slots=True)
class ExcludedRegion:
    object_id: ObjectId
    name: str
    region: Region

    def __post_init__(self) -> None:
        text(self.name, "Excluded region name")


class LandmarkRole(StrEnum):
    PRESENT = auto()
    MISSING = auto()
    EMPTY_MOUNT = auto()


class LandmarkSupport(StrEnum):
    RECTANGLE = auto()
    CIRCLE = auto()


@dataclass(frozen=True, slots=True)
class Landmark:
    object_id: ObjectId
    name: str
    region: Region
    threshold: float
    role: LandmarkRole
    required: bool
    orientation_invariant: bool
    support: LandmarkSupport
    max_template_rotation: float | None

    def __post_init__(self) -> None:
        text(self.name, "Landmark name")
        finite_number(self.threshold, "Landmark threshold")
        if self.threshold > 1:
            raise CalibrationValidationError("Landmark threshold must not exceed 1")
        if self.max_template_rotation is not None:
            finite_number(self.max_template_rotation, "Template rotation limit")
            if self.max_template_rotation > 180:
                raise CalibrationValidationError(
                    "Template rotation limit must not exceed 180 degrees"
                )
        if type(self.required) is not bool or type(self.orientation_invariant) is not bool:
            raise CalibrationValidationError("Landmark switches must be boolean values")
        if not isinstance(self.role, LandmarkRole) or not isinstance(self.support, LandmarkSupport):
            raise CalibrationValidationError("Landmark role/support must use typed identities")


@dataclass(frozen=True, slots=True)
class CalibrationDefinition:
    """Structurally valid draft data; full detector validation happens before publication."""

    binding: InspectionBinding
    references: References
    inspection_region: Region | None
    empty_mount_region: Region | None
    excluded_regions: tuple[ExcludedRegion, ...]
    landmarks: tuple[Landmark, ...]
    tuning: DetectorTuning

    def __post_init__(self) -> None:
        identities = [item.object_id for item in self.excluded_regions]
        identities.extend(item.object_id for item in self.landmarks)
        if len(set(identities)) != len(identities):
            raise CalibrationValidationError("Region and landmark identities must be unique")
        names = [item.name for item in self.landmarks]
        if len(set(names)) != len(names):
            raise CalibrationValidationError("Landmark names must be unique")


@dataclass(frozen=True, slots=True)
class CalibrationDraft:
    definition: CalibrationDefinition
    base_revision: int | None
    saved_at: datetime

    def __post_init__(self) -> None:
        if self.base_revision is not None:
            integer(self.base_revision, "Draft base revision", minimum=1)
        _timestamp(self.saved_at)


@dataclass(frozen=True, slots=True)
class CalibrationRevision:
    number: int
    definition: CalibrationDefinition
    created_at: datetime
    description: str

    def __post_init__(self) -> None:
        integer(self.number, "Revision number", minimum=1)
        _timestamp(self.created_at)
        if not isinstance(self.description, str):
            raise CalibrationValidationError("Revision description must be text")


@dataclass(frozen=True, slots=True)
class CalibrationProfile:
    profile_id: ProfileId
    name: str
    description: str
    draft: CalibrationDraft | None
    revisions: tuple[CalibrationRevision, ...]
    next_revision: int

    def __post_init__(self) -> None:
        text(self.name, "Profile name")
        integer(self.next_revision, "Next revision", minimum=1)
        numbers = [revision.number for revision in self.revisions]
        if len(set(numbers)) != len(numbers) or any(
            number >= self.next_revision for number in numbers
        ):
            raise CalibrationValidationError(
                "Revision numbers must be unique and below next_revision"
            )
        if not isinstance(self.description, str):
            raise CalibrationValidationError("Profile description must be text")

    def revision(self, number: int) -> CalibrationRevision:
        for revision in self.revisions:
            if revision.number == number:
                return revision
        raise PaintHeadCalibrationError(
            CalibrationFailure(
                CalibrationFailureCode.REVISION_NOT_FOUND, f"Revision {number} not found"
            )
        )


@dataclass(frozen=True, slots=True)
class CalibrationCatalog:
    version: int
    profiles: tuple[CalibrationProfile, ...]
    selected: RevisionRef | None

    def __post_init__(self) -> None:
        integer(self.version, "Catalog version")
        identities = [profile.profile_id for profile in self.profiles]
        if len(set(identities)) != len(identities):
            raise CalibrationValidationError("Profile identities must be unique")
        if self.selected is not None:
            self.profile(self.selected.profile_id).revision(self.selected.number)

    def profile(self, identity: ProfileId) -> CalibrationProfile:
        for profile in self.profiles:
            if profile.profile_id == identity:
                return profile
        raise PaintHeadCalibrationError(
            CalibrationFailure(
                CalibrationFailureCode.PROFILE_NOT_FOUND, "Calibration profile not found"
            )
        )

    def referenced_assets(self) -> frozenset[AssetId]:
        identities: set[AssetId] = set()
        for profile in self.profiles:
            definitions = [revision.definition for revision in profile.revisions]
            if profile.draft is not None:
                definitions.append(profile.draft.definition)
            for definition in definitions:
                identities.update(asset.asset_id for asset in definition.references.assets())
        return frozenset(identities)


@dataclass(frozen=True, slots=True)
class CalibrationChange:
    catalog: CalibrationCatalog
    warnings: tuple[CalibrationFailure, ...] = ()


def _timestamp(value: datetime) -> None:
    if not isinstance(value, datetime) or value.tzinfo is None or value.utcoffset() is None:
        raise CalibrationValidationError("Calibration timestamps must be timezone-aware")
