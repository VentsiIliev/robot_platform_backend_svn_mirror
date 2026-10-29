"""Interactive calibration is confined to development tools."""

from dataclasses import dataclass
from enum import Enum
from pathlib import Path

import cv2

from ..models import FeatureDefinition, FeatureRole, Image, Region
from .artifacts import write_json


class SelectionOutcome(Enum):
    SAVED = "saved"
    CANCELLED = "cancelled"


@dataclass(frozen=True, slots=True)
class FeatureSelectionResult:
    outcome: SelectionOutcome
    path: Path
    features: tuple[FeatureDefinition, ...]


class FeatureSelector:
    def select(
        self, image: Image, path: Path, role: FeatureRole, default_threshold: float
    ) -> FeatureSelectionResult:
        features: list[FeatureDefinition] = []
        print(
            "Select a feature and press ENTER; cancel to finish. Existing settings are preserved on cancellation."
        )
        while True:
            title = f"{role.value}: feature {len(features) + 1}"
            x, y, width, height = cv2.selectROI(title, image, showCrosshair=True, fromCenter=False)
            cv2.destroyWindow(title)
            if width == 0 or height == 0:
                break
            name = (
                input(f"Feature name [feature_{len(features) + 1}]: ").strip()
                or f"feature_{len(features) + 1}"
            )
            if any(feature.name == name for feature in features):
                print("Feature names must be unique")
                continue
            raw = input(f"Threshold [{default_threshold:g}]: ").strip()
            try:
                threshold = float(raw) if raw else default_threshold
            except ValueError:
                print("Threshold must be a number between 0 and 1")
                continue
            if not 0 <= threshold <= 1:
                print("Threshold must be between 0 and 1")
                continue
            features.append(FeatureDefinition(name, Region(x, y, width, height), threshold, role))
        if not features:
            return FeatureSelectionResult(SelectionOutcome.CANCELLED, path, ())
        write_json(
            path,
            {
                "features": [
                    {
                        "name": f.name,
                        "x": f.region.x,
                        "y": f.region.y,
                        "width": f.region.width,
                        "height": f.region.height,
                        "threshold": f.threshold,
                    }
                    for f in features
                ]
            },
        )
        return FeatureSelectionResult(SelectionOutcome.SAVED, path, tuple(features))
