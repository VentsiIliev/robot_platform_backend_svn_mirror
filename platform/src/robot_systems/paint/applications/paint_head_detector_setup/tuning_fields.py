"""Explicit tuning bindings; immutable replacement, without reflective attribute access."""

from collections.abc import Callable
from dataclasses import dataclass, replace
from enum import Enum, StrEnum, auto

from src.robot_systems.paint.contracts.paint_head_calibration.errors import (
    CalibrationValidationError,
)
from src.robot_systems.paint.contracts.paint_head_calibration.tuning import DetectorTuning


class TuningSection(Enum):
    ALIGNMENT = auto()
    MATCHING = auto()
    PREPROCESSING = auto()


class TuningParameterId(StrEnum):
    ALIGNMENT_MAX_TRANSLATION_PIXELS = "alignment.max_translation_pixels"
    ALIGNMENT_MAX_ROTATION_DEGREES = "alignment.max_rotation_degrees"
    ALIGNMENT_HYSTERESIS_PIXELS = "alignment.hysteresis_pixels"
    ALIGNMENT_HYSTERESIS_DEGREES = "alignment.hysteresis_degrees"
    ALIGNMENT_UNKNOWN_GRACE_FRAMES = "alignment.unknown_grace_frames"
    ALIGNMENT_UNKNOWN_GRACE_SECONDS = "alignment.unknown_grace_seconds"
    ALIGNMENT_STABLE_FRAMES = "alignment.stable_frames"
    MATCHING_SEARCH_MARGIN = "matching.search_margin"
    MATCHING_RELATIVE_TOLERANCE = "matching.relative_tolerance"
    MATCHING_PLATE_THRESHOLD = "matching.plate_threshold"
    MATCHING_MIN_MISSING_FEATURES = "matching.min_missing_features"
    MATCHING_MAX_ROTATION = "matching.max_rotation"
    MATCHING_ROTATION_STEP = "matching.rotation_step"
    MATCHING_CONSENSUS_TOLERANCE = "matching.consensus_tolerance"
    MATCHING_MIN_PRESENT_FEATURES = "matching.min_present_features"
    MATCHING_TOP_CANDIDATES = "matching.top_candidates"
    MATCHING_INVARIANT_CANDIDATES = "matching.invariant_candidates"
    MATCHING_PEAK_WINDOW = "matching.peak_window"
    MATCHING_CANDIDATE_SCORE_RATIO = "matching.candidate_score_ratio"
    MATCHING_SUPPRESSION_RADIUS = "matching.suppression_radius"
    MATCHING_ANGLE_TOLERANCE = "matching.angle_tolerance"
    MATCHING_RESIDUAL_WEIGHT = "matching.residual_weight"
    MATCHING_MINIMUM_PAIR_BASELINE = "matching.minimum_pair_baseline"
    MATCHING_PAIR_TOLERANCE_MULTIPLIER = "matching.pair_tolerance_multiplier"
    MATCHING_EDGE_DISTANCE_SIGMA = "matching.edge_distance_sigma"
    MATCHING_DEFAULT_FEATURE_THRESHOLD = "matching.default_feature_threshold"
    PREPROCESSING_BLUR_KERNEL = "preprocessing.blur_kernel"
    PREPROCESSING_ILLUMINATION_SIGMA = "preprocessing.illumination_sigma"
    PREPROCESSING_ILLUMINATION_FLOOR = "preprocessing.illumination_floor"
    PREPROCESSING_LOW_PERCENTILE = "preprocessing.low_percentile"
    PREPROCESSING_HIGH_PERCENTILE = "preprocessing.high_percentile"
    PREPROCESSING_MINIMUM_NORMALIZATION_RANGE = "preprocessing.minimum_normalization_range"
    PREPROCESSING_CLAHE_CLIP_LIMIT = "preprocessing.clahe_clip_limit"
    PREPROCESSING_CLAHE_TILE_SIZE = "preprocessing.clahe_tile_size"
    PREPROCESSING_GRADIENT_PERCENTILE = "preprocessing.gradient_percentile"
    PREPROCESSING_CANNY_HIGH_FLOOR = "preprocessing.canny_high_floor"
    PREPROCESSING_CANNY_LOW_RATIO = "preprocessing.canny_low_ratio"
    PREPROCESSING_QUALITY_LOW_PERCENTILE = "preprocessing.quality_low_percentile"
    PREPROCESSING_QUALITY_HIGH_PERCENTILE = "preprocessing.quality_high_percentile"
    PREPROCESSING_DARK_LIMIT = "preprocessing.dark_limit"
    PREPROCESSING_BRIGHT_LIMIT = "preprocessing.bright_limit"
    PREPROCESSING_MINIMUM_CONTRAST = "preprocessing.minimum_contrast"
    PREPROCESSING_MINIMUM_VALID_PIXELS = "preprocessing.minimum_valid_pixels"
    PREPROCESSING_INPAINT_RADIUS = "preprocessing.inpaint_radius"


@dataclass(frozen=True, slots=True)
class TuningParameter:
    identity: TuningParameterId
    label: str
    section: TuningSection
    integer: bool
    read: Callable[[DetectorTuning], int | float]
    write: Callable[[DetectorTuning, int | float], DetectorTuning]


def _integer(value: int | float) -> int:
    if isinstance(value, bool) or int(value) != value:
        raise CalibrationValidationError("This tuning value requires an integer")
    return int(value)


TUNING_PARAMETERS: tuple[TuningParameter, ...] = (
    TuningParameter(
        TuningParameterId.ALIGNMENT_MAX_TRANSLATION_PIXELS,
        "Allowed translation (px)",
        TuningSection.ALIGNMENT,
        False,
        lambda tuning: tuning.alignment.max_translation_pixels,
        lambda tuning, value: replace(
            tuning, alignment=replace(tuning.alignment, max_translation_pixels=float(value))
        ),
    ),
    TuningParameter(
        TuningParameterId.ALIGNMENT_MAX_ROTATION_DEGREES,
        "Allowed rotation (degrees)",
        TuningSection.ALIGNMENT,
        False,
        lambda tuning: tuning.alignment.max_rotation_degrees,
        lambda tuning, value: replace(
            tuning, alignment=replace(tuning.alignment, max_rotation_degrees=float(value))
        ),
    ),
    TuningParameter(
        TuningParameterId.ALIGNMENT_HYSTERESIS_PIXELS,
        "Translation hysteresis (px)",
        TuningSection.ALIGNMENT,
        False,
        lambda tuning: tuning.alignment.hysteresis_pixels,
        lambda tuning, value: replace(
            tuning, alignment=replace(tuning.alignment, hysteresis_pixels=float(value))
        ),
    ),
    TuningParameter(
        TuningParameterId.ALIGNMENT_HYSTERESIS_DEGREES,
        "Rotation hysteresis (degrees)",
        TuningSection.ALIGNMENT,
        False,
        lambda tuning: tuning.alignment.hysteresis_degrees,
        lambda tuning, value: replace(
            tuning, alignment=replace(tuning.alignment, hysteresis_degrees=float(value))
        ),
    ),
    TuningParameter(
        TuningParameterId.ALIGNMENT_UNKNOWN_GRACE_FRAMES,
        "Unknown grace (frames)",
        TuningSection.ALIGNMENT,
        True,
        lambda tuning: tuning.alignment.unknown_grace_frames,
        lambda tuning, value: replace(
            tuning, alignment=replace(tuning.alignment, unknown_grace_frames=_integer(value))
        ),
    ),
    TuningParameter(
        TuningParameterId.ALIGNMENT_UNKNOWN_GRACE_SECONDS,
        "Unknown grace (seconds)",
        TuningSection.ALIGNMENT,
        False,
        lambda tuning: tuning.alignment.unknown_grace_seconds,
        lambda tuning, value: replace(
            tuning, alignment=replace(tuning.alignment, unknown_grace_seconds=float(value))
        ),
    ),
    TuningParameter(
        TuningParameterId.ALIGNMENT_STABLE_FRAMES,
        "Confirmation frames",
        TuningSection.ALIGNMENT,
        True,
        lambda tuning: tuning.alignment.stable_frames,
        lambda tuning, value: replace(
            tuning, alignment=replace(tuning.alignment, stable_frames=_integer(value))
        ),
    ),
    TuningParameter(
        TuningParameterId.MATCHING_SEARCH_MARGIN,
        "Search margin",
        TuningSection.MATCHING,
        True,
        lambda tuning: tuning.matching.search_margin,
        lambda tuning, value: replace(
            tuning, matching=replace(tuning.matching, search_margin=_integer(value))
        ),
    ),
    TuningParameter(
        TuningParameterId.MATCHING_RELATIVE_TOLERANCE,
        "Relative tolerance",
        TuningSection.MATCHING,
        False,
        lambda tuning: tuning.matching.relative_tolerance,
        lambda tuning, value: replace(
            tuning, matching=replace(tuning.matching, relative_tolerance=float(value))
        ),
    ),
    TuningParameter(
        TuningParameterId.MATCHING_PLATE_THRESHOLD,
        "Plate threshold",
        TuningSection.MATCHING,
        False,
        lambda tuning: tuning.matching.plate_threshold,
        lambda tuning, value: replace(
            tuning, matching=replace(tuning.matching, plate_threshold=float(value))
        ),
    ),
    TuningParameter(
        TuningParameterId.MATCHING_MIN_MISSING_FEATURES,
        "Min missing features",
        TuningSection.MATCHING,
        True,
        lambda tuning: tuning.matching.min_missing_features,
        lambda tuning, value: replace(
            tuning, matching=replace(tuning.matching, min_missing_features=_integer(value))
        ),
    ),
    TuningParameter(
        TuningParameterId.MATCHING_MAX_ROTATION,
        "Maximum search rotation (degrees)",
        TuningSection.MATCHING,
        True,
        lambda tuning: tuning.matching.max_rotation,
        lambda tuning, value: replace(
            tuning, matching=replace(tuning.matching, max_rotation=_integer(value))
        ),
    ),
    TuningParameter(
        TuningParameterId.MATCHING_ROTATION_STEP,
        "Search rotation step (degrees)",
        TuningSection.MATCHING,
        True,
        lambda tuning: tuning.matching.rotation_step,
        lambda tuning, value: replace(
            tuning, matching=replace(tuning.matching, rotation_step=_integer(value))
        ),
    ),
    TuningParameter(
        TuningParameterId.MATCHING_CONSENSUS_TOLERANCE,
        "Consensus tolerance",
        TuningSection.MATCHING,
        False,
        lambda tuning: tuning.matching.consensus_tolerance,
        lambda tuning, value: replace(
            tuning, matching=replace(tuning.matching, consensus_tolerance=float(value))
        ),
    ),
    TuningParameter(
        TuningParameterId.MATCHING_MIN_PRESENT_FEATURES,
        "Min present features",
        TuningSection.MATCHING,
        True,
        lambda tuning: tuning.matching.min_present_features,
        lambda tuning, value: replace(
            tuning, matching=replace(tuning.matching, min_present_features=_integer(value))
        ),
    ),
    TuningParameter(
        TuningParameterId.MATCHING_TOP_CANDIDATES,
        "Top candidates",
        TuningSection.MATCHING,
        True,
        lambda tuning: tuning.matching.top_candidates,
        lambda tuning, value: replace(
            tuning, matching=replace(tuning.matching, top_candidates=_integer(value))
        ),
    ),
    TuningParameter(
        TuningParameterId.MATCHING_INVARIANT_CANDIDATES,
        "Invariant candidates",
        TuningSection.MATCHING,
        True,
        lambda tuning: tuning.matching.invariant_candidates,
        lambda tuning, value: replace(
            tuning, matching=replace(tuning.matching, invariant_candidates=_integer(value))
        ),
    ),
    TuningParameter(
        TuningParameterId.MATCHING_PEAK_WINDOW,
        "Peak window",
        TuningSection.MATCHING,
        True,
        lambda tuning: tuning.matching.peak_window,
        lambda tuning, value: replace(
            tuning, matching=replace(tuning.matching, peak_window=_integer(value))
        ),
    ),
    TuningParameter(
        TuningParameterId.MATCHING_CANDIDATE_SCORE_RATIO,
        "Candidate score ratio",
        TuningSection.MATCHING,
        False,
        lambda tuning: tuning.matching.candidate_score_ratio,
        lambda tuning, value: replace(
            tuning, matching=replace(tuning.matching, candidate_score_ratio=float(value))
        ),
    ),
    TuningParameter(
        TuningParameterId.MATCHING_SUPPRESSION_RADIUS,
        "Suppression radius",
        TuningSection.MATCHING,
        True,
        lambda tuning: tuning.matching.suppression_radius,
        lambda tuning, value: replace(
            tuning, matching=replace(tuning.matching, suppression_radius=_integer(value))
        ),
    ),
    TuningParameter(
        TuningParameterId.MATCHING_ANGLE_TOLERANCE,
        "Angle tolerance",
        TuningSection.MATCHING,
        False,
        lambda tuning: tuning.matching.angle_tolerance,
        lambda tuning, value: replace(
            tuning, matching=replace(tuning.matching, angle_tolerance=float(value))
        ),
    ),
    TuningParameter(
        TuningParameterId.MATCHING_RESIDUAL_WEIGHT,
        "Residual weight",
        TuningSection.MATCHING,
        False,
        lambda tuning: tuning.matching.residual_weight,
        lambda tuning, value: replace(
            tuning, matching=replace(tuning.matching, residual_weight=float(value))
        ),
    ),
    TuningParameter(
        TuningParameterId.MATCHING_MINIMUM_PAIR_BASELINE,
        "Minimum pair baseline",
        TuningSection.MATCHING,
        False,
        lambda tuning: tuning.matching.minimum_pair_baseline,
        lambda tuning, value: replace(
            tuning, matching=replace(tuning.matching, minimum_pair_baseline=float(value))
        ),
    ),
    TuningParameter(
        TuningParameterId.MATCHING_PAIR_TOLERANCE_MULTIPLIER,
        "Pair tolerance multiplier",
        TuningSection.MATCHING,
        False,
        lambda tuning: tuning.matching.pair_tolerance_multiplier,
        lambda tuning, value: replace(
            tuning, matching=replace(tuning.matching, pair_tolerance_multiplier=float(value))
        ),
    ),
    TuningParameter(
        TuningParameterId.MATCHING_EDGE_DISTANCE_SIGMA,
        "Edge distance sigma",
        TuningSection.MATCHING,
        False,
        lambda tuning: tuning.matching.edge_distance_sigma,
        lambda tuning, value: replace(
            tuning, matching=replace(tuning.matching, edge_distance_sigma=float(value))
        ),
    ),
    TuningParameter(
        TuningParameterId.MATCHING_DEFAULT_FEATURE_THRESHOLD,
        "Default feature threshold",
        TuningSection.MATCHING,
        False,
        lambda tuning: tuning.matching.default_feature_threshold,
        lambda tuning, value: replace(
            tuning, matching=replace(tuning.matching, default_feature_threshold=float(value))
        ),
    ),
    TuningParameter(
        TuningParameterId.PREPROCESSING_BLUR_KERNEL,
        "Blur kernel",
        TuningSection.PREPROCESSING,
        True,
        lambda tuning: tuning.preprocessing.blur_kernel,
        lambda tuning, value: replace(
            tuning, preprocessing=replace(tuning.preprocessing, blur_kernel=_integer(value))
        ),
    ),
    TuningParameter(
        TuningParameterId.PREPROCESSING_ILLUMINATION_SIGMA,
        "Illumination sigma",
        TuningSection.PREPROCESSING,
        False,
        lambda tuning: tuning.preprocessing.illumination_sigma,
        lambda tuning, value: replace(
            tuning, preprocessing=replace(tuning.preprocessing, illumination_sigma=float(value))
        ),
    ),
    TuningParameter(
        TuningParameterId.PREPROCESSING_ILLUMINATION_FLOOR,
        "Illumination floor",
        TuningSection.PREPROCESSING,
        False,
        lambda tuning: tuning.preprocessing.illumination_floor,
        lambda tuning, value: replace(
            tuning, preprocessing=replace(tuning.preprocessing, illumination_floor=float(value))
        ),
    ),
    TuningParameter(
        TuningParameterId.PREPROCESSING_LOW_PERCENTILE,
        "Low percentile",
        TuningSection.PREPROCESSING,
        False,
        lambda tuning: tuning.preprocessing.low_percentile,
        lambda tuning, value: replace(
            tuning, preprocessing=replace(tuning.preprocessing, low_percentile=float(value))
        ),
    ),
    TuningParameter(
        TuningParameterId.PREPROCESSING_HIGH_PERCENTILE,
        "High percentile",
        TuningSection.PREPROCESSING,
        False,
        lambda tuning: tuning.preprocessing.high_percentile,
        lambda tuning, value: replace(
            tuning, preprocessing=replace(tuning.preprocessing, high_percentile=float(value))
        ),
    ),
    TuningParameter(
        TuningParameterId.PREPROCESSING_MINIMUM_NORMALIZATION_RANGE,
        "Minimum normalization range",
        TuningSection.PREPROCESSING,
        False,
        lambda tuning: tuning.preprocessing.minimum_normalization_range,
        lambda tuning, value: replace(
            tuning,
            preprocessing=replace(tuning.preprocessing, minimum_normalization_range=float(value)),
        ),
    ),
    TuningParameter(
        TuningParameterId.PREPROCESSING_CLAHE_CLIP_LIMIT,
        "CLAHE clip limit",
        TuningSection.PREPROCESSING,
        False,
        lambda tuning: tuning.preprocessing.clahe_clip_limit,
        lambda tuning, value: replace(
            tuning, preprocessing=replace(tuning.preprocessing, clahe_clip_limit=float(value))
        ),
    ),
    TuningParameter(
        TuningParameterId.PREPROCESSING_CLAHE_TILE_SIZE,
        "CLAHE tile size",
        TuningSection.PREPROCESSING,
        True,
        lambda tuning: tuning.preprocessing.clahe_tile_size,
        lambda tuning, value: replace(
            tuning, preprocessing=replace(tuning.preprocessing, clahe_tile_size=_integer(value))
        ),
    ),
    TuningParameter(
        TuningParameterId.PREPROCESSING_GRADIENT_PERCENTILE,
        "Gradient percentile",
        TuningSection.PREPROCESSING,
        False,
        lambda tuning: tuning.preprocessing.gradient_percentile,
        lambda tuning, value: replace(
            tuning, preprocessing=replace(tuning.preprocessing, gradient_percentile=float(value))
        ),
    ),
    TuningParameter(
        TuningParameterId.PREPROCESSING_CANNY_HIGH_FLOOR,
        "Canny high floor",
        TuningSection.PREPROCESSING,
        False,
        lambda tuning: tuning.preprocessing.canny_high_floor,
        lambda tuning, value: replace(
            tuning, preprocessing=replace(tuning.preprocessing, canny_high_floor=float(value))
        ),
    ),
    TuningParameter(
        TuningParameterId.PREPROCESSING_CANNY_LOW_RATIO,
        "Canny low ratio",
        TuningSection.PREPROCESSING,
        False,
        lambda tuning: tuning.preprocessing.canny_low_ratio,
        lambda tuning, value: replace(
            tuning, preprocessing=replace(tuning.preprocessing, canny_low_ratio=float(value))
        ),
    ),
    TuningParameter(
        TuningParameterId.PREPROCESSING_QUALITY_LOW_PERCENTILE,
        "Quality low percentile",
        TuningSection.PREPROCESSING,
        False,
        lambda tuning: tuning.preprocessing.quality_low_percentile,
        lambda tuning, value: replace(
            tuning, preprocessing=replace(tuning.preprocessing, quality_low_percentile=float(value))
        ),
    ),
    TuningParameter(
        TuningParameterId.PREPROCESSING_QUALITY_HIGH_PERCENTILE,
        "Quality high percentile",
        TuningSection.PREPROCESSING,
        False,
        lambda tuning: tuning.preprocessing.quality_high_percentile,
        lambda tuning, value: replace(
            tuning,
            preprocessing=replace(tuning.preprocessing, quality_high_percentile=float(value)),
        ),
    ),
    TuningParameter(
        TuningParameterId.PREPROCESSING_DARK_LIMIT,
        "Dark limit",
        TuningSection.PREPROCESSING,
        False,
        lambda tuning: tuning.preprocessing.dark_limit,
        lambda tuning, value: replace(
            tuning, preprocessing=replace(tuning.preprocessing, dark_limit=float(value))
        ),
    ),
    TuningParameter(
        TuningParameterId.PREPROCESSING_BRIGHT_LIMIT,
        "Bright limit",
        TuningSection.PREPROCESSING,
        False,
        lambda tuning: tuning.preprocessing.bright_limit,
        lambda tuning, value: replace(
            tuning, preprocessing=replace(tuning.preprocessing, bright_limit=float(value))
        ),
    ),
    TuningParameter(
        TuningParameterId.PREPROCESSING_MINIMUM_CONTRAST,
        "Minimum contrast",
        TuningSection.PREPROCESSING,
        False,
        lambda tuning: tuning.preprocessing.minimum_contrast,
        lambda tuning, value: replace(
            tuning, preprocessing=replace(tuning.preprocessing, minimum_contrast=float(value))
        ),
    ),
    TuningParameter(
        TuningParameterId.PREPROCESSING_MINIMUM_VALID_PIXELS,
        "Minimum valid pixels",
        TuningSection.PREPROCESSING,
        True,
        lambda tuning: tuning.preprocessing.minimum_valid_pixels,
        lambda tuning, value: replace(
            tuning,
            preprocessing=replace(tuning.preprocessing, minimum_valid_pixels=_integer(value)),
        ),
    ),
    TuningParameter(
        TuningParameterId.PREPROCESSING_INPAINT_RADIUS,
        "Inpaint radius",
        TuningSection.PREPROCESSING,
        False,
        lambda tuning: tuning.preprocessing.inpaint_radius,
        lambda tuning, value: replace(
            tuning, preprocessing=replace(tuning.preprocessing, inpaint_radius=float(value))
        ),
    ),
)


def parameter(identity: TuningParameterId) -> TuningParameter:
    for item in TUNING_PARAMETERS:
        if item.identity is identity:
            return item
    raise CalibrationValidationError("Unknown typed tuning parameter")
