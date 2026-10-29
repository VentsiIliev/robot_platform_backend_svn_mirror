"""Reusable capture/evaluation runner built on the public detector API."""

import json
import time
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

from ..api import PaintHeadDetector
from ..errors import CameraError, ErrorReason
from ..preprocessing import ImageProcessor
from .application import prepare_configuration
from .artifacts import ArtifactWriter, write_json
from .camera_session import CameraSession
from .capture_results import (
    BenchmarkResult,
    CaptureLevelResult,
    CaptureOutcome,
    CaptureSessionResult,
)
from .exposure import ExposureController
from .options import DevelopmentOptions
from .renderer import OverlayRenderer
from .statistics import StreamStatistics
from .view import DevelopmentView, FrameRateMeter, ViewAction


@dataclass(frozen=True, slots=True)
class ExposureStep:
    name: str
    factor: float | None


class CaptureApplication:
    def __init__(self, options: DevelopmentOptions) -> None:
        self._options = options
        self._configuration = prepare_configuration(options)
        self._detector = PaintHeadDetector(self._configuration)
        self._renderer = OverlayRenderer(self._configuration, options.development.view)
        self._writer = ArtifactWriter(self._renderer)
        self._view = (
            None if options.headless else DevelopmentView(self._renderer, options.development.view)
        )
        processor = ImageProcessor(
            self._configuration.calibration,
            self._configuration.preprocessing,
            self._detector.reference_size,
            self._configuration.matching.edge_distance_sigma,
        )
        self._mask = processor.inspection_mask

    def benchmark(self) -> BenchmarkResult:
        image = self._detector.reference_images.present
        detector = self._detector
        detector.get_status(image)
        frames = self._options.development.runtime.benchmark_frames
        start = time.perf_counter()
        for _ in range(frames):
            detector.get_status(image)
        elapsed = time.perf_counter() - start
        return BenchmarkResult(frames, elapsed, frames / elapsed, 1000 * elapsed / frames)

    def _steps(self) -> tuple[ExposureStep, ...]:
        steps = [ExposureStep("original", None)]
        names = {0.5: "half_exposure", 1.0: "normal_exposure", 2.0: "double_exposure"}
        if self._options.exposure_sweep:
            steps.extend(
                ExposureStep(names.get(factor, f"exposure_{factor:g}x"), factor)
                for factor in self._options.development.runtime.exposure_factors
            )
        return tuple(steps)

    def _record(
        self, camera: CameraSession, step: ExposureStep, directory: Path
    ) -> CaptureLevelResult:
        self._detector.reset()
        runtime = self._options.development.runtime
        statistics = StreamStatistics(self._mask)
        meter = FrameRateMeter(self._options.development.view.fps_window)
        started = time.monotonic()
        last_saved = -float("inf")
        saved = 0
        outcome = CaptureOutcome.COMPLETE
        print(f"Evaluating {step.name}: exposure={camera.exposure}", flush=True)
        while statistics.frames == 0 or time.monotonic() - started < self._options.duration:
            read_start = time.perf_counter()
            image = camera.read()
            read_end = time.perf_counter()
            result = self._detector.get_status(image)
            detection_end = time.perf_counter()
            statistics.add(image, result, read_end - read_start, detection_end - read_end)
            fps = meter.update()
            now = time.monotonic()
            if now - last_saved >= runtime.capture_interval:
                artifacts = self._writer.save(directory, image, result, fps)
                print(
                    f"Saved {artifacts.raw_image}: {result.status.value} ({result.reason.value})",
                    flush=True,
                )
                saved += 1
                last_saved = now
            if self._view is not None:
                action = self._view.display(image, result, fps)
                if action is ViewAction.QUIT:
                    outcome = CaptureOutcome.INTERRUPTED
                    break
                if action is ViewAction.SAVE:
                    self._writer.save(directory, image, result, fps)
                    saved += 1
        return statistics.finish(
            step.name, outcome, saved, camera.exposure, time.monotonic() - started
        )

    def run(self) -> CaptureSessionResult:
        options = self._options
        runtime = options.development.runtime
        run_name = datetime.now(UTC).strftime("%Y%m%dT%H%M%S_%fZ")
        directory = options.capture_directory or runtime.output_directory / run_name
        levels: list[CaptureLevelResult] = []
        calibrated_exposure: float | None = None
        session_result: CaptureSessionResult
        try:
            with CameraSession(options.development.camera, self._detector.reference_size) as camera:
                controller = ExposureController(camera, options.development.camera, runtime)
                try:
                    camera.settled_frame(runtime.warmup_frames)
                    for step in self._steps():
                        if step.factor is not None:
                            if calibrated_exposure is None:
                                initial_brightness = levels[0].brightness_range
                                if initial_brightness is None:
                                    raise CameraError(
                                        ErrorReason.CAMERA_CONTROL_FAILED,
                                        "Initial capture has no brightness measurements",
                                    )
                                calibrated_exposure = controller.calibrate(
                                    sum(initial_brightness) / 2, self._mask
                                )
                            try:
                                controller.apply(calibrated_exposure * step.factor)
                            except CameraError as error:
                                if error.reason is not ErrorReason.CAMERA_CONTROL_FAILED:
                                    raise
                                level = CaptureLevelResult(
                                    step.name,
                                    CaptureOutcome.SKIPPED,
                                    error.message,
                                    0,
                                    0,
                                    camera.exposure,
                                    (),
                                    (),
                                    None,
                                    None,
                                    None,
                                    (),
                                    0.0,
                                )
                                levels.append(level)
                                print(json.dumps(level.to_json()), flush=True)
                                continue
                            camera.settled_frame(runtime.warmup_frames)
                        level = self._record(camera, step, directory / step.name)
                        levels.append(level)
                        print(json.dumps(level.to_json()), flush=True)
                        if level.outcome is CaptureOutcome.INTERRUPTED:
                            break
                finally:
                    restoration = controller.restore()
                    session_result = CaptureSessionResult(
                        directory / "summary.json",
                        tuple(levels),
                        controller.original_auto_exposure,
                        controller.original_exposure,
                        controller.measurements,
                        restoration,
                    )
                    write_json(session_result.report_path, session_result.to_json())
                    print(f"Evaluation summary: {session_result.report_path}", flush=True)
                if not restoration.restored:
                    raise CameraError(ErrorReason.CAMERA_CONTROL_FAILED, restoration.message)
        finally:
            if self._view is not None:
                self._view.close()
        return session_result
