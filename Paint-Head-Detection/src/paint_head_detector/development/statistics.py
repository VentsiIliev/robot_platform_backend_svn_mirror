"""Capture statistics with enum keys and vectorized feature-score reductions."""

from collections import Counter

import cv2
import numpy as np

from ..models import BoolMask, DetectionResult, HeadStatus, Image
from .capture_results import CaptureLevelResult, CaptureOutcome, FeatureScoreRange, StatusCount


class StreamStatistics:
    def __init__(self, mask: BoolMask) -> None:
        self._mask = mask
        self._observed: Counter[HeadStatus] = Counter()
        self._confirmed: Counter[HeadStatus] = Counter()
        self._scores: list[tuple[float, ...]] = []
        self._feature_names: tuple[str, ...] = ()
        self._brightness: list[float] = []
        self._read_ms: list[float] = []
        self._detection_ms: list[float] = []

    @property
    def frames(self) -> int:
        return len(self._brightness)

    def add(
        self, image: Image, result: DetectionResult, read_seconds: float, detection_seconds: float
    ) -> None:
        self._observed[result.observed_status] += 1
        self._confirmed[result.status] += 1
        matches = result.diagnostics.present.matches
        self._feature_names = tuple(match.feature.name for match in matches)
        self._scores.append(tuple(match.score for match in matches))
        self._brightness.append(
            float(np.median(cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)[self._mask]))
        )
        self._read_ms.append(1000 * read_seconds)
        self._detection_ms.append(1000 * detection_seconds)

    def finish(
        self, name: str, outcome: CaptureOutcome, saved: int, exposure: float, elapsed: float
    ) -> CaptureLevelResult:
        scores = np.array(self._scores)
        ranges = tuple(
            (
                FeatureScoreRange(name, float(low), float(high))
                for name, low, high in zip(
                    self._feature_names, scores.min(axis=0), scores.max(axis=0), strict=True
                )
            )
        )
        return CaptureLevelResult(
            name,
            outcome,
            "Capture completed"
            if outcome is CaptureOutcome.COMPLETE
            else "Capture interrupted by the operator",
            self.frames,
            saved,
            exposure,
            tuple((StatusCount(status, count) for status, count in self._observed.items())),
            tuple((StatusCount(status, count) for status, count in self._confirmed.items())),
            (min(self._brightness), max(self._brightness)),
            float(np.median(self._read_ms)),
            float(np.median(self._detection_ms)),
            ranges,
            self.frames / elapsed,
        )
