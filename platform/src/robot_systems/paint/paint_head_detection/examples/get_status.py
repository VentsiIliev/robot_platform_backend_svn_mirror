"""Second integration: inspect saved images through the public API without a GUI.

Edit the adjacent settings.py. Run from the platform checkout with:
python -m src.robot_systems.paint.paint_head_detection.examples.get_status
Direct-file execution from an IDE or another directory also works.

Other components can construct HeadlessApplication with typed configuration and
optional external calibration, then call run() with saved image paths.
"""

from __future__ import annotations

import sys
from collections.abc import Sequence
from dataclasses import dataclass, replace
from pathlib import Path
from typing import cast

# Direct execution puts examples/ on sys.path; imports need the platform root.
if not __package__:
    sys.path.insert(0, str(Path(__file__).resolve().parents[5]))

import cv2  # noqa: E402

from src.robot_systems.paint.paint_head_detection import (  # noqa: E402
    CalibrationConfig,
    ConfigurationRepository,
    DetectionResult,
    DetectorConfiguration,
    ErrorReason,
    HeadStatus,
    Image,
    PaintHeadDetector,
    PaintHeadError,
)
from src.robot_systems.paint.paint_head_detection.examples.settings import SETTINGS, ExampleSettings  # noqa: E402


class InputImageError(PaintHeadError):
    """A saved input frame could not be read by this integration."""


def load_image(path: Path) -> Image:
    if not path.is_file():
        raise InputImageError(ErrorReason.IMAGE_UNREADABLE, f"Input image does not exist: {path}")
    try:
        image = cv2.imread(str(path), cv2.IMREAD_COLOR)
    except cv2.error as error:
        raise InputImageError(
            ErrorReason.IMAGE_UNREADABLE, f"Cannot decode input image {path}: {error}"
        ) from error
    if image is None:
        raise InputImageError(ErrorReason.IMAGE_UNREADABLE, f"Cannot decode input image: {path}")
    return cast(Image, image)


@dataclass(frozen=True, slots=True)
class InspectedImage:
    path: Path
    detection: DetectionResult


class HeadlessApplication:
    """A consumer of the same API as the development app, with saved-file input.

    Hosts can inject a complete typed calibration (arrays, ROI, ignored regions,
    and tracked features) without any calibration JSON files. A complete typed
    DetectorConfiguration also removes the need for algorithm configuration files.
    """

    def __init__(
        self,
        configuration: DetectorConfiguration,
        *,
        calibration: CalibrationConfig | None = None,
    ) -> None:
        self._detector = PaintHeadDetector(configuration, calibration=calibration)

    @property
    def detector(self) -> PaintHeadDetector:
        """Allow the host to update calibration through the public detector API."""
        return self._detector

    def run(
        self, paths: Sequence[Path], *, independent_images: bool = False
    ) -> tuple[InspectedImage, ...]:
        results: list[InspectedImage] = []
        for path in paths:
            image = load_image(path)
            if independent_images:
                self._detector.reset()
            results.append(InspectedImage(path, self._detector.get_status(image)))
        return tuple(results)


def show_result(image_path: Path, result: DetectionResult) -> None:
    print(
        f"{image_path.name}: {result.status.value} (configuration {result.configuration_revision})"
    )
    print(f"  observed={result.observed_status.value}, reason={result.reason.value}")
    print(f"  {result.message}")
    if result.alignment is not None:
        print(
            f"  shift={result.alignment.translation_pixels:.2f}px, "
            f"rotation={result.alignment.rotation_degrees:+.2f}deg"
        )
    # Consumers branch on the enum, never string keys or status text.
    if result.status is HeadStatus.HEAD_MISALIGNED:
        print("  Placement needs correction.")
    elif result.status is HeadStatus.HEAD_MISSING:
        print("  Empty mount verified.")
    elif result.status is HeadStatus.UNKNOWN:
        print("  No confirmed decision yet.")


def main(settings: ExampleSettings = SETTINGS) -> int:
    try:
        configuration = ConfigurationRepository(settings.config_directory).load(
            calibration=settings.calibration
        )
        if settings.independent_images:
            # This local immutable override does not edit any JSON file.
            configuration = replace(
                configuration, alignment=replace(configuration.alignment, stable_frames=1)
            )
        app = HeadlessApplication(configuration)
        for inspected in app.run(
            settings.image_paths, independent_images=settings.independent_images
        ):
            show_result(inspected.path, inspected.detection)
        return 0
    except PaintHeadError as error:
        print(f"{error.reason.value}: {error.message}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
