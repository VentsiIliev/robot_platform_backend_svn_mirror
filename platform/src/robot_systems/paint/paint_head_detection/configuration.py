"""Immutable configuration and validation at the JSON boundary."""

from __future__ import annotations

import json
import math
from dataclasses import dataclass, replace
from pathlib import Path
from typing import cast

from .errors import ConfigurationError, ErrorReason
from .models import (
    FeatureDefinition,
    FeatureRole,
    FeatureSupport,
    ImageSize,
    ReferenceImages,
    Region,
)

DEFAULT_CONFIG_DIRECTORY = Path(__file__).resolve().parent / "config"


@dataclass(frozen=True, slots=True)
class MatchingConfig:
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


@dataclass(frozen=True, slots=True)
class PreprocessingConfig:
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


@dataclass(frozen=True, slots=True)
class AlignmentConfig:
    max_translation_pixels: float
    max_rotation_degrees: float
    hysteresis_pixels: float
    hysteresis_degrees: float
    unknown_grace_frames: int
    unknown_grace_seconds: float
    stable_frames: int

    @property
    def recovery_pixels(self) -> float:
        return max(0.0, self.max_translation_pixels - self.hysteresis_pixels)

    @property
    def recovery_degrees(self) -> float:
        return max(0.0, self.max_rotation_degrees - self.hysteresis_degrees)


@dataclass(frozen=True, slots=True)
class ReferencePaths:
    present: Path
    missing: Path


type ReferenceSource = ReferencePaths | ReferenceImages


@dataclass(frozen=True, slots=True)
class CalibrationConfig:
    references: ReferenceSource
    inspection_region: Region
    empty_mount_region: Region
    ignored_regions: tuple[Region, ...]
    present_features: tuple[FeatureDefinition, ...]
    missing_features: tuple[FeatureDefinition, ...]


@dataclass(frozen=True, slots=True)
class DetectorConfiguration:
    matching: MatchingConfig
    preprocessing: PreprocessingConfig
    alignment: AlignmentConfig
    calibration: CalibrationConfig

    def validate(self) -> None:
        m, p, a = self.matching, self.preprocessing, self.alignment
        numbers = (
            m.relative_tolerance,
            m.plate_threshold,
            m.consensus_tolerance,
            m.candidate_score_ratio,
            m.angle_tolerance,
            m.residual_weight,
            m.minimum_pair_baseline,
            m.pair_tolerance_multiplier,
            m.edge_distance_sigma,
            m.default_feature_threshold,
            a.max_translation_pixels,
            a.max_rotation_degrees,
            a.hysteresis_pixels,
            a.hysteresis_degrees,
            a.unknown_grace_seconds,
            p.illumination_sigma,
            p.illumination_floor,
            p.low_percentile,
            p.high_percentile,
            p.minimum_normalization_range,
            p.clahe_clip_limit,
            p.gradient_percentile,
            p.canny_high_floor,
            p.canny_low_ratio,
            p.quality_low_percentile,
            p.quality_high_percentile,
            p.dark_limit,
            p.bright_limit,
            p.minimum_contrast,
            p.inpaint_radius,
        )
        if any(not math.isfinite(n) or n < 0 for n in numbers):
            self._invalid("Configuration numbers must be finite and non-negative")
        integers = (
            m.search_margin,
            m.min_missing_features,
            m.max_rotation,
            m.rotation_step,
            m.min_present_features,
            m.top_candidates,
            m.invariant_candidates,
            m.peak_window,
            m.suppression_radius,
            a.unknown_grace_frames,
            a.stable_frames,
            p.blur_kernel,
            p.clahe_tile_size,
            p.minimum_valid_pixels,
        )
        if any(isinstance(n, bool) or not isinstance(n, int) or n < 0 for n in integers):
            self._invalid(
                "Frame counts, kernel sizes, and search limits must be non-negative integers"
            )
        if (
            m.rotation_step < 1
            or m.top_candidates < 1
            or m.invariant_candidates < 1
            or m.min_present_features < 2
            or m.min_missing_features < 2
            or a.stable_frames < 1
        ):
            self._invalid(
                "Rotation step, candidate counts, and stable frames must be positive; minimum feature counts must be >= 2"
            )
        if (
            m.max_rotation > 180
            or not 0 <= m.plate_threshold <= 1
            or not 0 <= m.default_feature_threshold <= 1
        ):
            self._invalid(
                "Rotation must be <= 180 degrees and similarity thresholds must be between 0 and 1"
            )
        if m.min_present_features > len(self.calibration.present_features):
            self._invalid("Minimum present features exceeds the number of calibrated features")
        if (
            p.blur_kernel < 1
            or p.blur_kernel % 2 == 0
            or m.peak_window < 1
            or m.peak_window % 2 == 0
            or p.clahe_tile_size < 1
            or p.minimum_valid_pixels < 1
        ):
            self._invalid(
                "Blur/peak kernels must be positive odd integers; tile size and valid-pixel count must be positive"
            )
        if (
            min(
                p.illumination_sigma,
                p.illumination_floor,
                p.minimum_normalization_range,
                p.clahe_clip_limit,
                m.edge_distance_sigma,
                m.pair_tolerance_multiplier,
            )
            <= 0
        ):
            self._invalid(
                "Normalization scales, contrast limits, and edge distance sigma must be positive"
            )
        if not (
            0 <= p.low_percentile < p.high_percentile <= 100
            and 0 <= p.quality_low_percentile < p.quality_high_percentile <= 100
            and 0 <= p.gradient_percentile <= 100
            and 0 < p.canny_low_ratio <= 1
        ):
            self._invalid("Percentile ranges or Canny threshold ratio are invalid")
        if not self.calibration.inspection_region.contains(self.calibration.empty_mount_region):
            self._invalid("Empty-mount region must lie inside the inspection region")
        regions = (
            self.calibration.inspection_region,
            self.calibration.empty_mount_region,
            *self.calibration.ignored_regions,
            *(feature.region for feature in self.calibration.present_features),
            *(feature.region for feature in self.calibration.missing_features),
        )
        if any(
            any(isinstance(n, bool) or not isinstance(n, int) for n in region.coordinates)
            or region.x < 0
            or region.y < 0
            or region.width < 2
            or region.height < 2
            for region in regions
        ):
            self._invalid("Regions require integer coordinates >= 0 and dimensions >= 2")
        present = self.calibration.present_features
        missing = self.calibration.missing_features
        if any(feature.role is not FeatureRole.PRESENT for feature in present):
            self._invalid("Present features must have the PRESENT role")
        if any(
            feature.role not in (FeatureRole.MISSING, FeatureRole.EMPTY_MOUNT)
            for feature in missing
        ):
            self._invalid("Missing features must have the MISSING or EMPTY_MOUNT role")
        for features in (present, missing):
            if len({feature.name for feature in features}) != len(features):
                self._invalid("Feature names must be unique within each group")
            for feature in features:
                if not isinstance(feature.support, FeatureSupport):
                    self._invalid(f"Feature {feature.name!r} requires a FeatureSupport enum")
                if feature.max_template_rotation is not None and (
                    not math.isfinite(feature.max_template_rotation)
                    or not 0 <= feature.max_template_rotation <= 180
                ):
                    self._invalid(
                        f"Feature {feature.name!r}: maximum template rotation must be between 0 and 180"
                    )
                if (
                    not feature.name.strip()
                    or not math.isfinite(feature.threshold)
                    or not 0 <= feature.threshold <= 1
                ):
                    self._invalid(
                        "Feature names must be non-empty and thresholds must be finite values between 0 and 1"
                    )
                if not self.calibration.inspection_region.contains(feature.region):
                    self._invalid(f"Feature {feature.name!r} exceeds the inspection region")
        if (
            missing
            and sum(feature.role is FeatureRole.MISSING for feature in missing)
            < m.min_missing_features
        ):
            self._invalid(
                "Minimum missing features exceeds the number of calibrated missing landmarks"
            )

    @staticmethod
    def _invalid(message: str) -> None:
        raise ConfigurationError(ErrorReason.CONFIGURATION_INVALID, message)


@dataclass(frozen=True, slots=True)
class ConfigurationUpdateResult:
    """A successful atomic update; invalid updates raise ConfigurationError/CalibrationError."""

    revision: int
    configuration: DetectorConfiguration
    reference_size: ImageSize
    present_feature_count: int
    missing_feature_count: int


class JsonReader:
    """The only place where untrusted JSON keys become typed domain values."""

    def __init__(self, data: dict[str, object], source: Path) -> None:
        self._data = data
        self.source = source

    @classmethod
    def read(cls, path: Path) -> JsonReader:
        try:
            value: object = json.loads(path.read_text(encoding="utf-8"))
        except FileNotFoundError as error:
            raise ConfigurationError(
                ErrorReason.CONFIGURATION_NOT_FOUND, f"Configuration file does not exist: {path}"
            ) from error
        except (OSError, UnicodeError, json.JSONDecodeError) as error:
            raise ConfigurationError(
                ErrorReason.CONFIGURATION_INVALID, f"Cannot read configuration {path}: {error}"
            ) from error
        return cls(cls.as_object(value, path), path)

    @staticmethod
    def as_object(value: object, source: Path) -> dict[str, object]:
        if not isinstance(value, dict) or not all(isinstance(k, str) for k in value):
            raise ConfigurationError(
                ErrorReason.CONFIGURATION_INVALID, f"Expected a JSON object in {source}"
            )
        return cast(dict[str, object], value)

    def value(self, key: str) -> object:
        if key not in self._data:
            self.fail(key, "required value is missing")
        return self._data[key]

    def optional(self, key: str, default: object) -> object:
        return self._data.get(key, default)

    def number(self, key: str, default: float | None = None) -> float:
        value = self.value(key) if default is None else self.optional(key, default)
        if (
            isinstance(value, bool)
            or not isinstance(value, (int, float))
            or not math.isfinite(value)
        ):
            self.fail(key, "expected a finite number")
        return float(cast(int | float, value))

    def integer(self, key: str) -> int:
        value = self.value(key)
        if isinstance(value, bool) or not isinstance(value, int):
            self.fail(key, "expected an integer")
        return cast(int, value)

    def boolean(self, key: str, default: bool | None = None) -> bool:
        value = self.value(key) if default is None else self.optional(key, default)
        if not isinstance(value, bool):
            self.fail(key, "expected a boolean")
        return cast(bool, value)

    def text(self, key: str, default: str | None = None) -> str:
        value = self.value(key) if default is None else self.optional(key, default)
        if not isinstance(value, str) or not value.strip():
            self.fail(key, "expected non-empty text")
        return cast(str, value)

    def child(self, key: str) -> JsonReader:
        return JsonReader(self.as_object(self.value(key), self.source), self.source)

    def sequence(self, key: str) -> list[object]:
        value = self.value(key)
        if not isinstance(value, list):
            self.fail(key, "expected an array")
        return cast(list[object], value)

    def region(self) -> Region:
        region = Region(
            self.integer("x"), self.integer("y"), self.integer("width"), self.integer("height")
        )
        if region.x < 0 or region.y < 0 or region.width < 2 or region.height < 2:
            self.fail("region", "coordinates must be non-negative and dimensions must be >= 2")
        return region

    def region_or_child(self, key: str) -> Region:
        value = self.optional(key, None)
        return (
            self.region()
            if value is None
            else JsonReader(self.as_object(value, self.source), self.source).region()
        )

    def optional_sequence(self, key: str) -> list[object]:
        value = self.optional(key, [])
        if not isinstance(value, list):
            self.fail(key, "expected an array")
        return cast(list[object], value)

    def fail(self, key: str, message: str) -> None:
        raise ConfigurationError(
            ErrorReason.CONFIGURATION_INVALID, f"{self.source}: {key}: {message}"
        )


class ConfigurationRepository:
    def __init__(self, directory: Path = DEFAULT_CONFIG_DIRECTORY) -> None:
        self.directory = directory.resolve()

    def load(self, *, calibration: CalibrationConfig | None = None) -> DetectorConfiguration:
        m = JsonReader.read(self.directory / "matching.json")
        matching = MatchingConfig(
            m.integer("search_margin"),
            m.number("relative_tolerance"),
            m.number("plate_threshold"),
            m.integer("min_missing_features"),
            m.integer("max_rotation"),
            m.integer("rotation_step"),
            m.number("consensus_tolerance"),
            m.integer("min_present_features"),
            m.integer("top_candidates"),
            m.integer("invariant_candidates"),
            m.integer("peak_window"),
            m.number("candidate_score_ratio"),
            m.integer("suppression_radius"),
            m.number("angle_tolerance"),
            m.number("residual_weight"),
            m.number("minimum_pair_baseline"),
            m.number("pair_tolerance_multiplier"),
            m.number("edge_distance_sigma"),
            m.number("default_feature_threshold"),
        )
        p = JsonReader.read(self.directory / "preprocessing.json")
        preprocessing = PreprocessingConfig(
            p.integer("blur_kernel"),
            p.number("illumination_sigma"),
            p.number("illumination_floor"),
            p.number("low_percentile"),
            p.number("high_percentile"),
            p.number("minimum_normalization_range"),
            p.number("clahe_clip_limit"),
            p.integer("clahe_tile_size"),
            p.number("gradient_percentile"),
            p.number("canny_high_floor"),
            p.number("canny_low_ratio"),
            p.number("quality_low_percentile"),
            p.number("quality_high_percentile"),
            p.number("dark_limit"),
            p.number("bright_limit"),
            p.number("minimum_contrast"),
            p.integer("minimum_valid_pixels"),
            p.number("inpaint_radius"),
        )
        a = JsonReader.read(self.directory / "alignment.json")
        alignment = AlignmentConfig(
            a.number("max_translation_pixels"),
            a.number("max_rotation_degrees"),
            a.number("hysteresis_pixels"),
            a.number("hysteresis_degrees"),
            a.integer("unknown_grace_frames"),
            a.number("unknown_grace_seconds"),
            a.integer("stable_frames"),
        )
        config = DetectorConfiguration(
            matching,
            preprocessing,
            alignment,
            self._load_calibration(matching) if calibration is None else calibration,
        )
        config.validate()
        return config

    def _load_calibration(self, matching: MatchingConfig) -> CalibrationConfig:
        refs = JsonReader.read(self.directory / "references.json")
        references = ReferencePaths(
            (self.directory / refs.text("present")).resolve(),
            (self.directory / refs.text("missing")).resolve(),
        )
        roi = JsonReader.read(self.directory / "roi.json")
        inspection = roi.region()
        empty = roi.region_or_child("empty_mount")
        ignored = tuple(
            JsonReader(JsonReader.as_object(v, roi.source), roi.source).region()
            for v in roi.optional_sequence("ignore_regions")
        )
        present = self._features(
            "present_features.json",
            FeatureRole.PRESENT,
            matching.default_feature_threshold,
            inspection,
        )
        missing = self._features(
            "missing_features.json",
            FeatureRole.MISSING,
            matching.default_feature_threshold,
            inspection,
        )
        return CalibrationConfig(references, inspection, empty, ignored, present, missing)

    def _features(
        self, filename: str, role: FeatureRole, threshold: float, inspection: Region
    ) -> tuple[FeatureDefinition, ...]:
        reader = JsonReader.read(self.directory / filename)
        features: list[FeatureDefinition] = []
        for value in reader.sequence("features"):
            item = JsonReader(JsonReader.as_object(value, reader.source), reader.source)
            name = item.text("name")
            try:
                support = FeatureSupport(item.text("support", FeatureSupport.RECTANGLE.value))
                feature_role = FeatureRole(item.text("role", role.value))
            except ValueError as error:
                raise ConfigurationError(
                    ErrorReason.CONFIGURATION_INVALID,
                    f"{reader.source}: invalid support or role for feature {name}",
                ) from error
            if feature_role is not role and not (
                role is FeatureRole.MISSING and feature_role is FeatureRole.EMPTY_MOUNT
            ):
                item.fail(name, f"role {feature_role.value} does not belong in this feature group")
            feature = FeatureDefinition(
                name,
                item.region(),
                item.number("threshold", threshold),
                feature_role,
                item.boolean("required", False),
                item.boolean("orientation_invariant", False),
                support,
                None
                if item.optional("max_template_rotation", None) is None
                else item.number("max_template_rotation"),
            )
            clipped = feature.region.intersection(inspection)
            if clipped.width < 2 or clipped.height < 2:
                item.fail(name, "feature does not overlap the inspection region")
            if not 0 <= feature.threshold <= 1:
                item.fail(name, "threshold must be between 0 and 1")
            if (
                feature.max_template_rotation is not None
                and not 0 <= feature.max_template_rotation <= 180
            ):
                item.fail(name, "maximum template rotation must be between 0 and 180")
            features.append(replace(feature, region=clipped))
        if role is FeatureRole.PRESENT and not features:
            reader.fail("features", "at least one present feature is required")
        if len({f.name for f in features}) != len(features):
            reader.fail("features", "feature names must be unique")
        return tuple(features)
