"""Typed outcomes for capture, exposure calibration, and benchmarking."""

from dataclasses import dataclass
from enum import Enum
from pathlib import Path

from ..models import HeadStatus


class CaptureOutcome(Enum):
    COMPLETE = "complete"
    SKIPPED = "skipped"
    INTERRUPTED = "interrupted"


@dataclass(frozen=True, slots=True)
class StatusCount:
    status: HeadStatus
    count: int


@dataclass(frozen=True, slots=True)
class FeatureScoreRange:
    name: str
    minimum: float
    maximum: float


@dataclass(frozen=True, slots=True)
class ExposureMeasurement:
    exposure: float
    median_brightness: float


@dataclass(frozen=True, slots=True)
class CameraRestoreResult:
    restored: bool
    message: str


@dataclass(frozen=True, slots=True)
class CaptureLevelResult:
    name: str
    outcome: CaptureOutcome
    message: str
    frames: int
    saved: int
    exposure: float
    observed_counts: tuple[StatusCount, ...]
    confirmed_counts: tuple[StatusCount, ...]
    brightness_range: tuple[float, float] | None
    median_read_ms: float | None
    median_detection_ms: float | None
    feature_ranges: tuple[FeatureScoreRange, ...]
    frames_per_second: float

    def to_json(self) -> dict[str, object]:
        return {
            "level": self.name,
            "outcome": self.outcome.value,
            "message": self.message,
            "frames": self.frames,
            "saved": self.saved,
            "exposure": self.exposure,
            "raw_states": {item.status.value: item.count for item in self.observed_counts},
            "stable_states": {item.status.value: item.count for item in self.confirmed_counts},
            "median_brightness_range": self.brightness_range,
            "median_read_ms": self.median_read_ms,
            "median_detection_ms": self.median_detection_ms,
            "feature_score_ranges": {
                item.name: [item.minimum, item.maximum] for item in self.feature_ranges
            },
            "frames_per_second": self.frames_per_second,
        }


@dataclass(frozen=True, slots=True)
class CaptureSessionResult:
    report_path: Path
    levels: tuple[CaptureLevelResult, ...]
    original_auto_exposure: float
    original_exposure: float
    calibration: tuple[ExposureMeasurement, ...]
    restoration: CameraRestoreResult

    def to_json(self) -> dict[str, object]:
        return {
            "description": "Live detector results; no automatic ground-truth labels assigned",
            "original_auto_exposure": self.original_auto_exposure,
            "original_exposure": self.original_exposure,
            "exposure_calibration": [
                {"exposure": item.exposure, "median_brightness": item.median_brightness}
                for item in self.calibration
            ],
            "controls_restored": self.restoration.restored,
            "restoration_message": self.restoration.message,
            "levels": [level.to_json() for level in self.levels],
        }


@dataclass(frozen=True, slots=True)
class BenchmarkResult:
    frames: int
    elapsed_seconds: float
    processing_fps: float
    milliseconds_per_frame: float
