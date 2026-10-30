"""Portable tuning values; the detector adapter owns algorithm validation."""

from dataclasses import dataclass

from .validation import finite_number, integer


@dataclass(frozen=True, slots=True)
class MatchingTuning:
    search_margin: int
    relative_tolerance: float
    plate_threshold: float
    min_missing_features: int
    max_rotation: int
    rotation_step: int
    consensus_tolerance: float
    min_present_features: int
    top_candidates: int
    invariant_candidates: int
    peak_window: int
    candidate_score_ratio: float
    suppression_radius: int
    angle_tolerance: float
    residual_weight: float
    minimum_pair_baseline: float
    pair_tolerance_multiplier: float
    edge_distance_sigma: float
    default_feature_threshold: float

    def __post_init__(self) -> None:
        integer(self.search_margin, "search_margin")
        finite_number(self.relative_tolerance, "relative_tolerance")
        finite_number(self.plate_threshold, "plate_threshold")
        integer(self.min_missing_features, "min_missing_features")
        integer(self.max_rotation, "max_rotation")
        integer(self.rotation_step, "rotation_step")
        finite_number(self.consensus_tolerance, "consensus_tolerance")
        integer(self.min_present_features, "min_present_features")
        integer(self.top_candidates, "top_candidates")
        integer(self.invariant_candidates, "invariant_candidates")
        integer(self.peak_window, "peak_window")
        finite_number(self.candidate_score_ratio, "candidate_score_ratio")
        integer(self.suppression_radius, "suppression_radius")
        finite_number(self.angle_tolerance, "angle_tolerance")
        finite_number(self.residual_weight, "residual_weight")
        finite_number(self.minimum_pair_baseline, "minimum_pair_baseline")
        finite_number(self.pair_tolerance_multiplier, "pair_tolerance_multiplier")
        finite_number(self.edge_distance_sigma, "edge_distance_sigma")
        finite_number(self.default_feature_threshold, "default_feature_threshold")


@dataclass(frozen=True, slots=True)
class PreprocessingTuning:
    blur_kernel: int
    illumination_sigma: float
    illumination_floor: float
    low_percentile: float
    high_percentile: float
    minimum_normalization_range: float
    clahe_clip_limit: float
    clahe_tile_size: int
    gradient_percentile: float
    canny_high_floor: float
    canny_low_ratio: float
    quality_low_percentile: float
    quality_high_percentile: float
    dark_limit: float
    bright_limit: float
    minimum_contrast: float
    minimum_valid_pixels: int
    inpaint_radius: float

    def __post_init__(self) -> None:
        integer(self.blur_kernel, "blur_kernel")
        finite_number(self.illumination_sigma, "illumination_sigma")
        finite_number(self.illumination_floor, "illumination_floor")
        finite_number(self.low_percentile, "low_percentile")
        finite_number(self.high_percentile, "high_percentile")
        finite_number(self.minimum_normalization_range, "minimum_normalization_range")
        finite_number(self.clahe_clip_limit, "clahe_clip_limit")
        integer(self.clahe_tile_size, "clahe_tile_size")
        finite_number(self.gradient_percentile, "gradient_percentile")
        finite_number(self.canny_high_floor, "canny_high_floor")
        finite_number(self.canny_low_ratio, "canny_low_ratio")
        finite_number(self.quality_low_percentile, "quality_low_percentile")
        finite_number(self.quality_high_percentile, "quality_high_percentile")
        finite_number(self.dark_limit, "dark_limit")
        finite_number(self.bright_limit, "bright_limit")
        finite_number(self.minimum_contrast, "minimum_contrast")
        integer(self.minimum_valid_pixels, "minimum_valid_pixels")
        finite_number(self.inpaint_radius, "inpaint_radius")


@dataclass(frozen=True, slots=True)
class AlignmentTuning:
    max_translation_pixels: float
    max_rotation_degrees: float
    hysteresis_pixels: float
    hysteresis_degrees: float
    unknown_grace_frames: int
    unknown_grace_seconds: float
    stable_frames: int

    def __post_init__(self) -> None:
        finite_number(self.max_translation_pixels, "max_translation_pixels")
        finite_number(self.max_rotation_degrees, "max_rotation_degrees")
        finite_number(self.hysteresis_pixels, "hysteresis_pixels")
        finite_number(self.hysteresis_degrees, "hysteresis_degrees")
        integer(self.unknown_grace_frames, "unknown_grace_frames")
        finite_number(self.unknown_grace_seconds, "unknown_grace_seconds")
        integer(self.stable_frames, "stable_frames")


@dataclass(frozen=True, slots=True)
class DetectorTuning:
    matching: MatchingTuning
    preprocessing: PreprocessingTuning
    alignment: AlignmentTuning
