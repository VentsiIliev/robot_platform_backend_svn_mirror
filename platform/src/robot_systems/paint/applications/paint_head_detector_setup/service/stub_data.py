"""Deterministic portable fixtures for the standalone screen; no files or hardware."""

from datetime import UTC, datetime
from functools import lru_cache
from math import hypot

from src.robot_systems.paint.component_ids import CameraRoleID, MovementGroupID
from src.robot_systems.paint.contracts.paint_head_calibration.models import (
    AssetId,
    CalibrationCatalog,
    CalibrationDefinition,
    CalibrationDraft,
    CalibrationProfile,
    CalibrationRevision,
    ExcludedRegion,
    ImagePixels,
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

PROFILE_ID = ProfileId("00000000000000000000000000000001")
NOW = datetime(2026, 10, 30, 12, 0, tzinfo=UTC)
SIZE = ImageSize(640, 480)


def sample_definition() -> CalibrationDefinition:
    landmarks = tuple(
        Landmark(
            ObjectId(f"{index + 1:032x}"),
            name,
            Region(x, y, 24, 24),
            0.72,
            role,
            False,
            True,
            LandmarkSupport.CIRCLE,
            None,
        )
        for index, (name, x, y, role) in enumerate(
            (
                ("Upper fastener", 308, 155, LandmarkRole.PRESENT),
                ("Lower fastener", 308, 295, LandmarkRole.PRESENT),
                ("Upper left bolt", 210, 180, LandmarkRole.MISSING),
                ("Upper right bolt", 400, 180, LandmarkRole.MISSING),
                ("Lower left bolt", 210, 315, LandmarkRole.MISSING),
                ("Lower right bolt", 400, 315, LandmarkRole.MISSING),
            )
        )
    )
    return CalibrationDefinition(
        InspectionBinding(CameraRoleID.PRIMARY_VISION, MovementGroupID.VERTICAL_SHAFT_ALIGNMENT),
        References(
            ReferenceAsset(AssetId("a" * 64), SIZE), ReferenceAsset(AssetId("b" * 64), SIZE)
        ),
        Region(160, 60, 320, 370),
        Region(190, 130, 260, 250),
        (ExcludedRegion(ObjectId("f" * 32), "Cable", Region(175, 75, 65, 55)),),
        landmarks,
        sample_tuning(),
    )


def sample_catalog() -> CalibrationCatalog:
    definition = sample_definition()
    profile = CalibrationProfile(
        PROFILE_ID,
        "Standard",
        "Standalone sample",
        CalibrationDraft(definition, 1, NOW),
        (CalibrationRevision(1, definition, NOW, ""),),
        2,
    )
    return CalibrationCatalog(1, (profile,), RevisionRef(PROFILE_ID, 1))


@lru_cache(maxsize=1)
def sample_pixels() -> ImagePixels:
    pixels = bytearray()
    for y in range(SIZE.height):
        for x in range(SIZE.width):
            value = 205
            if 155 <= x <= 485 and 55 <= y <= 435:
                value = 125
            radius = hypot(x - 320, y - 265)
            if radius < 130:
                value = 48 if radius < 119 else 90
            if 300 <= x <= 340 and 110 <= y <= 370:
                value = 75
            if hypot(x - 320, y - 165) < 13 or hypot(x - 320, y - 305) < 9:
                value = 220
            pixels.extend((value, value, value))
    return ImagePixels(SIZE, bytes(pixels))


def sample_tuning() -> DetectorTuning:
    return DetectorTuning(
        MatchingTuning(
            search_margin=65,
            relative_tolerance=15.0,
            plate_threshold=0.65,
            min_missing_features=2,
            max_rotation=180,
            rotation_step=5,
            consensus_tolerance=14.0,
            min_present_features=2,
            top_candidates=3,
            invariant_candidates=48,
            peak_window=15,
            candidate_score_ratio=0.65,
            suppression_radius=7,
            angle_tolerance=5.01,
            residual_weight=0.01,
            minimum_pair_baseline=1.0,
            pair_tolerance_multiplier=2.0,
            edge_distance_sigma=2.0,
            default_feature_threshold=0.7,
        ),
        PreprocessingTuning(
            blur_kernel=7,
            illumination_sigma=15.0,
            illumination_floor=16.0,
            low_percentile=2.0,
            high_percentile=98.0,
            minimum_normalization_range=0.05,
            clahe_clip_limit=2.0,
            clahe_tile_size=8,
            gradient_percentile=85.0,
            canny_high_floor=40.0,
            canny_low_ratio=0.4,
            quality_low_percentile=5.0,
            quality_high_percentile=95.0,
            dark_limit=8.0,
            bright_limit=247.0,
            minimum_contrast=12.0,
            minimum_valid_pixels=100,
            inpaint_radius=3.0,
        ),
        AlignmentTuning(
            max_translation_pixels=10.0,
            max_rotation_degrees=2.0,
            hysteresis_pixels=2.0,
            hysteresis_degrees=1.0,
            unknown_grace_frames=3,
            unknown_grace_seconds=0.35,
            stable_frames=3,
        ),
    )
