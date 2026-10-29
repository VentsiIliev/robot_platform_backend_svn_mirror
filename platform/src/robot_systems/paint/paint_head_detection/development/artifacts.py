"""Explicit serialization at the development artifact boundary."""

import json
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

import cv2

from ..errors import ArtifactError, ErrorReason
from ..models import AlignmentMeasurement, DetectionResult, Image
from .renderer import OverlayRenderer


@dataclass(frozen=True, slots=True)
class CaptureArtifacts:
    raw_image: Path
    overlay_image: Path
    metadata: Path


def alignment_json(alignment: AlignmentMeasurement | None) -> dict[str, object] | None:
    if alignment is None:
        return None
    return {
        "aligned": alignment.aligned,
        "translation_pixels": alignment.translation_pixels,
        "rotation_degrees": alignment.rotation_degrees,
        "max_translation_pixels": alignment.max_translation_pixels,
        "max_rotation_degrees": alignment.max_rotation_degrees,
        "recovery_pixel_limit": alignment.recovery_pixel_limit,
        "recovery_degree_limit": alignment.recovery_degree_limit,
        "recovering": alignment.recovering,
    }


def result_json(result: DetectionResult, fps: float | None = None) -> dict[str, object]:
    diagnostics = result.diagnostics
    return {
        "state": result.status.value,
        "configuration_revision": result.configuration_revision,
        "raw_state": result.observed_status.value,
        "reason": result.reason.value,
        "message": result.message,
        "fps": fps,
        "plate": diagnostics.missing.plate_similarity,
        "quality_issue": None
        if diagnostics.quality.issue is None
        else diagnostics.quality.issue.value,
        "inliers": diagnostics.present.inlier_count,
        "rotation": diagnostics.pose.rotation_degrees,
        "offset": list(diagnostics.pose.offset),
        "alignment": alignment_json(result.alignment),
        "held_warning": result.held_warning,
        "features": [
            {
                "name": match.feature.name,
                "score": match.score,
                "passed": match.passed,
                "position": list(match.position),
            }
            for match in diagnostics.present.matches
        ],
    }


def write_json(path: Path, payload: object) -> None:
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    except (OSError, TypeError, ValueError) as error:
        raise ArtifactError(
            ErrorReason.ARTIFACT_WRITE_FAILED, f"Cannot write report {path}: {error}"
        ) from error


class ArtifactWriter:
    def __init__(self, renderer: OverlayRenderer) -> None:
        self._renderer = renderer

    def save(
        self, directory: Path, image: Image, result: DetectionResult, fps: float | None = None
    ) -> CaptureArtifacts:
        name = datetime.now(UTC).strftime("%Y%m%dT%H%M%S_%fZ")
        artifacts = CaptureArtifacts(
            directory / f"{name}.png", directory / f"{name}_overlay.png", directory / f"{name}.json"
        )
        try:
            directory.mkdir(parents=True, exist_ok=True)
            if not cv2.imwrite(str(artifacts.raw_image), image):
                raise OSError("raw image writer returned failure")
            if not cv2.imwrite(
                str(artifacts.overlay_image), self._renderer.draw(image, result, fps=fps)
            ):
                raise OSError("overlay writer returned failure")
            write_json(artifacts.metadata, result_json(result, fps))
        except (OSError, cv2.error) as error:
            raise ArtifactError(
                ErrorReason.ARTIFACT_WRITE_FAILED, f"Cannot save capture to {directory}: {error}"
            ) from error
        return artifacts
