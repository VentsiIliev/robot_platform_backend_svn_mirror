"""Public image-in/result-out API. No camera, CLI, GUI, or artifact dependencies."""

import time
from collections.abc import Callable, Sequence
from dataclasses import dataclass, replace
from pathlib import Path
from threading import RLock

import cv2

from .calibration import CalibrationLoader, ImageValidator
from .configuration import (
    CalibrationConfig,
    ConfigurationRepository,
    ConfigurationUpdateResult,
    DetectorConfiguration,
    ReferenceSource,
)
from .decision import DecisionPolicy
from .errors import (
    CalibrationError,
    ConfigurationError,
    DetectionProcessingError,
    ErrorReason,
    InvalidImageError,
)
from .matching import FeatureMatcher
from .models import (
    DetectionDiagnostics,
    DetectionResult,
    FeatureDefinition,
    FrameEvidence,
    Image,
    ImageSize,
    ReferenceImages,
    Region,
)
from .preprocessing import ImageProcessor


@dataclass(frozen=True, slots=True)
class _DetectorRuntime:
    configuration: DetectorConfiguration
    references: ReferenceImages
    size: ImageSize
    validator: ImageValidator
    processor: ImageProcessor
    matcher: FeatureMatcher
    policy: DecisionPolicy


def _build_runtime(
    configuration: DetectorConfiguration, reference_images: ReferenceImages | None = None
) -> _DetectorRuntime:
    configuration.validate()
    calibration = CalibrationLoader().load(configuration, reference_images=reference_images)
    references = ReferenceImages(calibration.present_reference, calibration.missing_reference)
    if isinstance(configuration.calibration.references, ReferenceImages):
        configuration = replace(
            configuration, calibration=replace(configuration.calibration, references=references)
        )
    try:
        processor = ImageProcessor(
            configuration.calibration,
            configuration.preprocessing,
            calibration.size,
            configuration.matching.edge_distance_sigma,
        )
        matcher = FeatureMatcher(
            processor.extract_edges(references.present),
            processor.extract_edges(references.missing),
            configuration.calibration,
            configuration.matching,
        )
    except cv2.error as error:
        raise CalibrationError(
            ErrorReason.PROCESSING_FAILED, f"Could not prepare reference images: {error}"
        ) from error
    return _DetectorRuntime(
        configuration,
        references,
        calibration.size,
        ImageValidator(calibration.size),
        processor,
        matcher,
        DecisionPolicy(configuration.alignment),
    )


class PaintHeadDetector:
    """Classify one ordered image stream using an immutable calibration snapshot.

    Calls and configuration updates are serialized. Updates validate and build a
    complete replacement before applying it, then reset temporal confirmation.
    Failed updates preserve the existing configuration, caches, and stream state.
    """

    def __init__(
        self,
        configuration: DetectorConfiguration | None = None,
        *,
        config_directory: Path | None = None,
        calibration: CalibrationConfig | None = None,
        clock: Callable[[], float] = time.monotonic,
    ) -> None:
        if configuration is not None and config_directory is not None:
            raise ConfigurationError(
                ErrorReason.CONFIGURATION_INVALID,
                "Pass either a typed configuration or a configuration directory, not both",
            )
        if configuration is None:
            repository = (
                ConfigurationRepository()
                if config_directory is None
                else ConfigurationRepository(config_directory)
            )
            configuration = repository.load(calibration=calibration)
        elif calibration is not None:
            configuration = replace(configuration, calibration=calibration)
        self._lock = RLock()
        self._clock = clock
        self._runtime = _build_runtime(configuration)
        self._revision = 1

    @property
    def configuration(self) -> DetectorConfiguration:
        with self._lock:
            return self._runtime.configuration

    @property
    def reference_size(self) -> ImageSize:
        with self._lock:
            return self._runtime.size

    @property
    def reference_images(self) -> ReferenceImages:
        """Read-only reference snapshots owned by this detector."""
        with self._lock:
            return self._runtime.references

    @property
    def configuration_revision(self) -> int:
        with self._lock:
            return self._revision

    def _apply_configuration(
        self, configuration: DetectorConfiguration, references: ReferenceImages | None = None
    ) -> ConfigurationUpdateResult:
        runtime = _build_runtime(configuration, references)
        self._runtime = runtime
        self._revision += 1
        return ConfigurationUpdateResult(
            self._revision,
            runtime.configuration,
            runtime.size,
            len(runtime.configuration.calibration.present_features),
            len(runtime.configuration.calibration.missing_features),
        )

    def configure(self, configuration: DetectorConfiguration) -> ConfigurationUpdateResult:
        """Replace all settings together, including references, ROI, and features.

        File references are reloaded. Use this when changing related settings
        together, such as moving an ROI and all of its landmark selections.
        """
        with self._lock:
            return self._apply_configuration(configuration)

    def set_roi(
        self,
        roi: Region,
        *,
        empty_mount_region: Region | None = None,
        ignored_regions: Sequence[Region] | None = None,
    ) -> ConfigurationUpdateResult:
        """Update inspection bounds; omitted regions and features are preserved.

        Existing features and the empty-mount region must still fit inside roi.
        This reuses reference snapshots without reading their files again.
        """
        with self._lock:
            current = self._runtime.configuration
            calibration = replace(
                current.calibration,
                inspection_region=roi,
                empty_mount_region=(
                    current.calibration.empty_mount_region
                    if empty_mount_region is None
                    else empty_mount_region
                ),
                ignored_regions=(
                    current.calibration.ignored_regions
                    if ignored_regions is None
                    else tuple(ignored_regions)
                ),
            )
            return self._apply_configuration(
                replace(current, calibration=calibration), self._runtime.references
            )

    def set_reference_images(self, references: ReferenceSource) -> ConfigurationUpdateResult:
        """Replace references from file paths or caller-provided BGR uint8 arrays."""
        with self._lock:
            current = self._runtime.configuration
            return self._apply_configuration(
                replace(current, calibration=replace(current.calibration, references=references))
            )

    def set_features(
        self,
        present: Sequence[FeatureDefinition],
        *,
        missing: Sequence[FeatureDefinition] | None = None,
    ) -> ConfigurationUpdateResult:
        """Replace tracked present features and optionally empty-mount features."""
        with self._lock:
            current = self._runtime.configuration
            calibration = replace(
                current.calibration,
                present_features=tuple(present),
                missing_features=(
                    current.calibration.missing_features if missing is None else tuple(missing)
                ),
            )
            return self._apply_configuration(
                replace(current, calibration=calibration), self._runtime.references
            )

    def reset(self) -> None:
        """Discard confirmations and hysteresis before starting a new stream."""
        with self._lock:
            self._runtime.policy.reset()

    def get_status(self, image: Image) -> DetectionResult:
        """Return typed status, reason, placement measurements, and diagnostics.

        Invalid images raise InvalidImageError; vision backend failures raise
        DetectionProcessingError. Errors clear temporal state. Insufficient
        evidence returns HeadStatus.UNKNOWN. Results identify their configuration
        revision so consumers can associate a decision with its calibration.
        """
        with self._lock:
            runtime = self._runtime
            try:
                runtime.validator.validate(image)
                processed = runtime.processor.process(image)
                present = runtime.matcher.match_present(processed.edges, processed.proximity)
                missing = runtime.matcher.match_missing(processed.edges, processed.proximity)
                timestamp = self._clock()
                evidence = FrameEvidence(present, missing, processed.quality, processed.edges)
                decision = runtime.policy.evaluate(evidence, timestamp)
            except InvalidImageError:
                runtime.policy.reset()
                raise
            except cv2.error as error:
                runtime.policy.reset()
                raise DetectionProcessingError(
                    ErrorReason.PROCESSING_FAILED, f"OpenCV could not process the image: {error}"
                ) from error
            processed.edges.setflags(write=False)
            diagnostics = DetectionDiagnostics(
                present, missing, processed.quality, decision.pose, processed.edges
            )
            return DetectionResult(
                decision.status,
                decision.observed_status,
                decision.reason,
                decision.message,
                decision.alignment,
                decision.held_warning,
                timestamp,
                self._revision,
                diagnostics,
            )
