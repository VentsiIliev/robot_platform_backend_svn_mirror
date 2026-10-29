"""Development acquisition loop. The detector itself accepts only images."""

import time
from dataclasses import dataclass, replace
from pathlib import Path

from ..api import PaintHeadDetector
from ..calibration import CalibrationLoader
from ..configuration import DetectorConfiguration
from ..models import DetectionResult, FeatureRole
from .artifacts import ArtifactWriter, CaptureArtifacts
from .camera_session import CameraSession
from .options import DevelopmentOptions
from .renderer import OverlayRenderer
from .selection import FeatureSelector, SelectionOutcome
from .view import DevelopmentView, FrameRateMeter, ViewAction


@dataclass(frozen=True, slots=True)
class DevelopmentRunResult:
    frames: int
    elapsed_seconds: float
    last_detection: DetectionResult | None
    captures: tuple[CaptureArtifacts, ...]


def prepare_configuration(options: DevelopmentOptions) -> DetectorConfiguration:
    configuration = options.configuration
    selector = FeatureSelector()
    threshold = configuration.matching.default_feature_threshold
    references = (
        CalibrationLoader().load_references(configuration.calibration.references)
        if options.select_present or options.select_missing
        else None
    )
    if options.select_present:
        assert references is not None
        selection = selector.select(
            references.present,
            options.config_directory / "present_features.json",
            FeatureRole.PRESENT,
            threshold,
        )
        print(f"Feature selection {selection.outcome.value}: {selection.path}")
        if selection.outcome is SelectionOutcome.SAVED:
            configuration = replace(
                configuration,
                calibration=replace(configuration.calibration, present_features=selection.features),
            )
    if options.select_missing:
        assert references is not None
        selection = selector.select(
            references.missing,
            options.config_directory / "missing_features.json",
            FeatureRole.MISSING,
            threshold,
        )
        print(f"Feature selection {selection.outcome.value}: {selection.path}")
        if selection.outcome is SelectionOutcome.SAVED:
            configuration = replace(
                configuration,
                calibration=replace(configuration.calibration, missing_features=selection.features),
            )
    if options.select_present or options.select_missing:
        configuration.validate()
    return configuration


class DetectorDevelopmentApplication:
    def __init__(self, options: DevelopmentOptions) -> None:
        self._options = options

    def run(self) -> DevelopmentRunResult:
        options = self._options
        configuration = prepare_configuration(options)
        detector = PaintHeadDetector(configuration)
        renderer = OverlayRenderer(configuration, options.development.view)
        writer = ArtifactWriter(renderer)
        view = None if options.headless else DevelopmentView(renderer, options.development.view)
        meter = FrameRateMeter(options.development.view.fps_window)
        captures: list[CaptureArtifacts] = []
        last_result = None
        frames = 0
        started = time.monotonic()
        last_capture = -float("inf")
        print("Press Q to quit, S to save a raw frame and typed diagnostics", flush=True)
        try:
            with CameraSession(options.development.camera, detector.reference_size) as camera:
                while True:
                    image = camera.read()
                    last_result = detector.get_status(image)
                    fps = meter.update()
                    frames += 1
                    now = time.monotonic()
                    if (
                        options.capture_directory is not None
                        and now - last_capture >= options.development.runtime.capture_interval
                    ):
                        artifacts = writer.save(options.capture_directory, image, last_result, fps)
                        captures.append(artifacts)
                        print(f"Saved {artifacts.raw_image}", flush=True)
                        last_capture = now
                    if view is not None:
                        action = view.display(image, last_result, fps)
                        if action is ViewAction.QUIT:
                            break
                        if action is ViewAction.SAVE:
                            directory = (
                                options.capture_directory
                                or options.development.runtime.output_directory / "manual"
                            )
                            artifacts = writer.save(Path(directory), image, last_result, fps)
                            captures.append(artifacts)
                            print(f"Saved {artifacts.raw_image}", flush=True)
                    if options.duration and now - started >= options.duration:
                        break
        finally:
            if view is not None:
                view.close()
        return DevelopmentRunResult(
            frames, time.monotonic() - started, last_result, tuple(captures)
        )
