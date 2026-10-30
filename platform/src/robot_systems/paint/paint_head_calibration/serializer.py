"""Explicit JSON boundary for the system-owned calibration catalog."""

from dataclasses import asdict
from datetime import datetime
from math import isfinite

from src.engine.repositories.interfaces.settings_serializer import ISettingsSerializer
from src.robot_systems.paint.component_ids import CameraRoleID, MovementGroupID
from src.robot_systems.paint.contracts.paint_head_calibration.errors import (
    CalibrationValidationError,
)
from src.robot_systems.paint.contracts.paint_head_calibration.models import (
    AssetId,
    CalibrationCatalog,
    CalibrationDefinition,
    CalibrationDraft,
    CalibrationProfile,
    CalibrationRevision,
    ExcludedRegion,
    ImageSize,
    InspectionBinding,
    Landmark,
    LandmarkRole,
    LandmarkSupport,
    ObjectId,
    ProfileId,
    ReferenceAsset,
    References,
    Region,
    RevisionRef,
)
from src.robot_systems.paint.contracts.paint_head_calibration.tuning import (
    AlignmentTuning,
    DetectorTuning,
    MatchingTuning,
    PreprocessingTuning,
)


class _Object:
    def __init__(self, value: object, keys: tuple[str, ...]) -> None:
        if not isinstance(value, dict) or any(not isinstance(key, str) for key in value):
            raise CalibrationValidationError("Calibration JSON value must be an object")
        if set(value) != set(keys):
            raise CalibrationValidationError(
                f"Calibration JSON keys differ: expected {keys}, received {tuple(value)}"
            )
        self._value = value

    def value(self, key: str) -> object:
        return self._value[key]

    def text(self, key: str) -> str:
        value = self.value(key)
        if not isinstance(value, str):
            raise CalibrationValidationError(f"{key} must be text")
        return value

    def integer(self, key: str) -> int:
        value = self.value(key)
        if type(value) is not int:
            raise CalibrationValidationError(f"{key} must be an integer")
        return value

    def number(self, key: str) -> float:
        value = self.value(key)
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise CalibrationValidationError(f"{key} must be numeric")
        try:
            valid = isfinite(value)
        except OverflowError:
            valid = False
        if not valid:
            raise CalibrationValidationError(f"{key} must be a finite number")
        return float(value)

    def boolean(self, key: str) -> bool:
        value = self.value(key)
        if type(value) is not bool:
            raise CalibrationValidationError(f"{key} must be boolean")
        return value

    def sequence(self, key: str) -> list[object]:
        value = self.value(key)
        if not isinstance(value, list):
            raise CalibrationValidationError(f"{key} must be an array")
        return value


def _region(value: object) -> Region | None:
    if value is None:
        return None
    r = _Object(value, ("x", "y", "width", "height"))
    return Region(r.integer("x"), r.integer("y"), r.integer("width"), r.integer("height"))


def _required_region(value: object) -> Region:
    region = _region(value)
    if region is None:
        raise CalibrationValidationError("An editor object requires a region")
    return region


def _asset(value: object) -> ReferenceAsset | None:
    if value is None:
        return None
    r = _Object(value, ("asset_id", "width", "height"))
    return ReferenceAsset(
        AssetId(r.text("asset_id")), ImageSize(r.integer("width"), r.integer("height"))
    )


def _asset_dict(asset: ReferenceAsset | None) -> object:
    if asset is None:
        return None
    return {
        "asset_id": asset.asset_id.value,
        "width": asset.size.width,
        "height": asset.size.height,
    }


def _excluded(value: object) -> ExcludedRegion:
    r = _Object(value, ("object_id", "name", "region"))
    return ExcludedRegion(
        ObjectId(r.text("object_id")), r.text("name"), _required_region(r.value("region"))
    )


def _landmark(value: object) -> Landmark:
    r = _Object(
        value,
        (
            "object_id",
            "name",
            "region",
            "threshold",
            "role",
            "required",
            "orientation_invariant",
            "support",
            "max_template_rotation",
        ),
    )
    return Landmark(
        ObjectId(r.text("object_id")),
        r.text("name"),
        _required_region(r.value("region")),
        r.number("threshold"),
        LandmarkRole(r.text("role")),
        r.boolean("required"),
        r.boolean("orientation_invariant"),
        LandmarkSupport(r.text("support")),
        None if r.value("max_template_rotation") is None else r.number("max_template_rotation"),
    )


def definition_to_dict(definition: CalibrationDefinition) -> dict[str, object]:
    return {
        "binding": {
            "camera_role": definition.binding.camera_role.value,
            "movement_group": definition.binding.movement_group.value,
        },
        "references": {
            "present": _asset_dict(definition.references.present),
            "missing": _asset_dict(definition.references.missing),
        },
        "inspection_region": None
        if definition.inspection_region is None
        else asdict(definition.inspection_region),
        "empty_mount_region": None
        if definition.empty_mount_region is None
        else asdict(definition.empty_mount_region),
        "excluded_regions": [
            {"object_id": item.object_id.value, "name": item.name, "region": asdict(item.region)}
            for item in definition.excluded_regions
        ],
        "landmarks": [
            {
                "object_id": item.object_id.value,
                "name": item.name,
                "region": asdict(item.region),
                "threshold": item.threshold,
                "role": item.role.value,
                "required": item.required,
                "orientation_invariant": item.orientation_invariant,
                "support": item.support.value,
                "max_template_rotation": item.max_template_rotation,
            }
            for item in definition.landmarks
        ],
        "tuning": asdict(definition.tuning),
    }


def definition_from_dict(value: object) -> CalibrationDefinition:
    r = _Object(
        value,
        (
            "binding",
            "references",
            "inspection_region",
            "empty_mount_region",
            "excluded_regions",
            "landmarks",
            "tuning",
        ),
    )
    binding = _Object(r.value("binding"), ("camera_role", "movement_group"))
    refs = _Object(r.value("references"), ("present", "missing"))
    return CalibrationDefinition(
        InspectionBinding(
            CameraRoleID(binding.text("camera_role")),
            MovementGroupID(binding.text("movement_group")),
        ),
        References(_asset(refs.value("present")), _asset(refs.value("missing"))),
        _region(r.value("inspection_region")),
        _region(r.value("empty_mount_region")),
        tuple(_excluded(item) for item in r.sequence("excluded_regions")),
        tuple(_landmark(item) for item in r.sequence("landmarks")),
        _tuning(r.value("tuning")),
    )


def _reference(value: object) -> RevisionRef | None:
    if value is None:
        return None
    r = _Object(value, ("profile_id", "number"))
    return RevisionRef(ProfileId(r.text("profile_id")), r.integer("number"))


def _timestamp(value: str) -> datetime:
    try:
        return datetime.fromisoformat(value)
    except ValueError as error:
        raise CalibrationValidationError("Invalid calibration timestamp") from error


def _draft(value: object) -> CalibrationDraft | None:
    if value is None:
        return None
    r = _Object(value, ("definition", "base_revision", "saved_at"))
    return CalibrationDraft(
        definition_from_dict(r.value("definition")),
        None if r.value("base_revision") is None else r.integer("base_revision"),
        _timestamp(r.text("saved_at")),
    )


def _revision(value: object) -> CalibrationRevision:
    r = _Object(value, ("number", "definition", "created_at", "description"))
    return CalibrationRevision(
        r.integer("number"),
        definition_from_dict(r.value("definition")),
        _timestamp(r.text("created_at")),
        r.text("description"),
    )


def _profile(value: object) -> CalibrationProfile:
    r = _Object(value, ("profile_id", "name", "description", "draft", "revisions", "next_revision"))
    return CalibrationProfile(
        ProfileId(r.text("profile_id")),
        r.text("name"),
        r.text("description"),
        _draft(r.value("draft")),
        tuple(_revision(item) for item in r.sequence("revisions")),
        r.integer("next_revision"),
    )


class CalibrationCatalogSerializer(ISettingsSerializer[CalibrationCatalog]):
    @property
    def settings_type(self) -> str:
        return "paint_head_detector_calibration"

    def get_default(self) -> CalibrationCatalog:
        return CalibrationCatalog(0, (), None)

    def to_dict(self, settings: CalibrationCatalog) -> dict[str, object]:
        return {
            "schema_version": 1,
            "version": settings.version,
            "selected": None
            if settings.selected is None
            else {
                "profile_id": settings.selected.profile_id.value,
                "number": settings.selected.number,
            },
            "profiles": [
                {
                    "profile_id": profile.profile_id.value,
                    "name": profile.name,
                    "description": profile.description,
                    "next_revision": profile.next_revision,
                    "draft": None
                    if profile.draft is None
                    else {
                        "definition": definition_to_dict(profile.draft.definition),
                        "base_revision": profile.draft.base_revision,
                        "saved_at": profile.draft.saved_at.isoformat(),
                    },
                    "revisions": [
                        {
                            "number": revision.number,
                            "definition": definition_to_dict(revision.definition),
                            "created_at": revision.created_at.isoformat(),
                            "description": revision.description,
                        }
                        for revision in profile.revisions
                    ],
                }
                for profile in settings.profiles
            ],
        }

    def from_dict(self, data: dict[str, object]) -> CalibrationCatalog:
        r = _Object(data, ("schema_version", "version", "selected", "profiles"))
        if r.integer("schema_version") != 1:
            raise CalibrationValidationError("Unsupported paint-head calibration schema version")
        try:
            return CalibrationCatalog(
                r.integer("version"),
                tuple(_profile(item) for item in r.sequence("profiles")),
                _reference(r.value("selected")),
            )
        except (TypeError, ValueError) as error:
            raise CalibrationValidationError(f"Invalid calibration catalog: {error}") from error


def _tuning(value: object) -> DetectorTuning:
    r = _Object(value, ("matching", "preprocessing", "alignment"))
    return DetectorTuning(
        _matching(r.value("matching")),
        _preprocessing(r.value("preprocessing")),
        _alignment(r.value("alignment")),
    )


def _matching(value: object) -> MatchingTuning:
    r = _Object(
        value,
        (
            "search_margin",
            "relative_tolerance",
            "plate_threshold",
            "min_missing_features",
            "max_rotation",
            "rotation_step",
            "consensus_tolerance",
            "min_present_features",
            "top_candidates",
            "invariant_candidates",
            "peak_window",
            "candidate_score_ratio",
            "suppression_radius",
            "angle_tolerance",
            "residual_weight",
            "minimum_pair_baseline",
            "pair_tolerance_multiplier",
            "edge_distance_sigma",
            "default_feature_threshold",
        ),
    )
    return MatchingTuning(
        r.integer("search_margin"),
        r.number("relative_tolerance"),
        r.number("plate_threshold"),
        r.integer("min_missing_features"),
        r.integer("max_rotation"),
        r.integer("rotation_step"),
        r.number("consensus_tolerance"),
        r.integer("min_present_features"),
        r.integer("top_candidates"),
        r.integer("invariant_candidates"),
        r.integer("peak_window"),
        r.number("candidate_score_ratio"),
        r.integer("suppression_radius"),
        r.number("angle_tolerance"),
        r.number("residual_weight"),
        r.number("minimum_pair_baseline"),
        r.number("pair_tolerance_multiplier"),
        r.number("edge_distance_sigma"),
        r.number("default_feature_threshold"),
    )


def _preprocessing(value: object) -> PreprocessingTuning:
    r = _Object(
        value,
        (
            "blur_kernel",
            "illumination_sigma",
            "illumination_floor",
            "low_percentile",
            "high_percentile",
            "minimum_normalization_range",
            "clahe_clip_limit",
            "clahe_tile_size",
            "gradient_percentile",
            "canny_high_floor",
            "canny_low_ratio",
            "quality_low_percentile",
            "quality_high_percentile",
            "dark_limit",
            "bright_limit",
            "minimum_contrast",
            "minimum_valid_pixels",
            "inpaint_radius",
        ),
    )
    return PreprocessingTuning(
        r.integer("blur_kernel"),
        r.number("illumination_sigma"),
        r.number("illumination_floor"),
        r.number("low_percentile"),
        r.number("high_percentile"),
        r.number("minimum_normalization_range"),
        r.number("clahe_clip_limit"),
        r.integer("clahe_tile_size"),
        r.number("gradient_percentile"),
        r.number("canny_high_floor"),
        r.number("canny_low_ratio"),
        r.number("quality_low_percentile"),
        r.number("quality_high_percentile"),
        r.number("dark_limit"),
        r.number("bright_limit"),
        r.number("minimum_contrast"),
        r.integer("minimum_valid_pixels"),
        r.number("inpaint_radius"),
    )


def _alignment(value: object) -> AlignmentTuning:
    r = _Object(
        value,
        (
            "max_translation_pixels",
            "max_rotation_degrees",
            "hysteresis_pixels",
            "hysteresis_degrees",
            "unknown_grace_frames",
            "unknown_grace_seconds",
            "stable_frames",
        ),
    )
    return AlignmentTuning(
        r.number("max_translation_pixels"),
        r.number("max_rotation_degrees"),
        r.number("hysteresis_pixels"),
        r.number("hysteresis_degrees"),
        r.integer("unknown_grace_frames"),
        r.number("unknown_grace_seconds"),
        r.integer("stable_frames"),
    )
