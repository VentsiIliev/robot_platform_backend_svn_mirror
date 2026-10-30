"""Translate portable calibration profiles to the unchanged image-only detector."""

from dataclasses import asdict

import cv2
import numpy as np
from numpy.typing import NDArray

from src.robot_systems.paint.component_ids import CameraRoleID, MovementGroupID
from src.robot_systems.paint.contracts.paint_head_calibration.errors import (
    CalibrationFailure,
    CalibrationFailureCode,
    PaintHeadCalibrationError,
)
from src.robot_systems.paint.contracts.paint_head_calibration.interfaces import (
    ICalibrationDefinitionValidator,
    IReferenceAssetRepository,
)
from src.robot_systems.paint.contracts.paint_head_calibration.models import (
    CalibrationDefinition,
    CalibrationEvaluation,
    ExcludedRegion,
    ImageFrame,
    ImagePixels,
    ImageSize,
    InspectionBinding,
    Landmark,
    LandmarkEvidence,
    LandmarkRole,
    LandmarkSupport,
    ObjectId,
    ReferenceAsset,
    References,
    Region,
)
from src.robot_systems.paint.contracts.paint_head_calibration.tuning import (
    AlignmentTuning,
    DetectorTuning,
    MatchingTuning,
    PreprocessingTuning,
)
from src.robot_systems.paint.contracts.paint_head_check.models import (
    PaintHeadObservationReason,
    PaintHeadState,
)
from src.robot_systems.paint.paint_head_detection import (
    AlignmentConfig,
    CalibrationConfig,
    ConfigurationRepository,
    DetectionReason,
    DetectorConfiguration,
    FeatureDefinition,
    FeatureRole,
    FeatureSupport,
    HeadStatus,
    MatchingConfig,
    PaintHeadDetector,
    PaintHeadError,
    PreprocessingConfig,
    ReferenceImages,
)
from src.robot_systems.paint.paint_head_detection import (
    Region as DetectorRegion,
)

_ROLES = {
    LandmarkRole.PRESENT: FeatureRole.PRESENT,
    LandmarkRole.MISSING: FeatureRole.MISSING,
    LandmarkRole.EMPTY_MOUNT: FeatureRole.EMPTY_MOUNT,
}
_SUPPORTS = {
    LandmarkSupport.CIRCLE: FeatureSupport.CIRCLE,
    LandmarkSupport.RECTANGLE: FeatureSupport.RECTANGLE,
}
_STATES = {
    HeadStatus.HEAD_PRESENT: PaintHeadState.PRESENT,
    HeadStatus.HEAD_MISSING: PaintHeadState.MISSING,
    HeadStatus.HEAD_MISALIGNED: PaintHeadState.MISALIGNED,
    HeadStatus.UNKNOWN: PaintHeadState.UNKNOWN,
}
_REASONS = {
    DetectionReason.ALIGNED: PaintHeadObservationReason.ALIGNED,
    DetectionReason.MISALIGNED: PaintHeadObservationReason.MISALIGNED,
    DetectionReason.EMPTY_MOUNT: PaintHeadObservationReason.EMPTY_MOUNT,
    DetectionReason.INSUFFICIENT_EVIDENCE: PaintHeadObservationReason.INSUFFICIENT_EVIDENCE,
    DetectionReason.CONFLICTING_EVIDENCE: PaintHeadObservationReason.CONFLICTING_EVIDENCE,
    DetectionReason.POSE_UNDETERMINED: PaintHeadObservationReason.POSE_UNDETERMINED,
    DetectionReason.TOO_DARK: PaintHeadObservationReason.TOO_DARK,
    DetectionReason.OVEREXPOSED: PaintHeadObservationReason.OVEREXPOSED,
    DetectionReason.LOW_CONTRAST: PaintHeadObservationReason.LOW_CONTRAST,
    DetectionReason.CONFIRMING_STATUS: PaintHeadObservationReason.CONFIRMING_STATUS,
    DetectionReason.RECHECKING_POSITION: PaintHeadObservationReason.RECHECKING_POSITION,
}


def _invalid(detail: str) -> PaintHeadCalibrationError:
    return PaintHeadCalibrationError(
        CalibrationFailure(CalibrationFailureCode.INVALID_CALIBRATION, detail)
    )


def image_array(image: ImagePixels) -> NDArray[np.uint8]:
    return np.frombuffer(image.bgr, dtype=np.uint8).reshape(image.size.height, image.size.width, 3)


def image_pixels(image: NDArray[np.uint8]) -> ImagePixels:
    if image.dtype != np.uint8 or image.ndim != 3 or image.shape[2] != 3:
        raise PaintHeadCalibrationError(
            CalibrationFailure(
                CalibrationFailureCode.FRAME_INVALID, "Camera image must be BGR uint8"
            )
        )
    return ImagePixels(ImageSize(int(image.shape[1]), int(image.shape[0])), image.tobytes())


def encode_reference(image: ImagePixels) -> bytes:
    try:
        encoded, png = cv2.imencode(".png", image_array(image))
    except cv2.error as error:
        raise _invalid(f"Reference encoding failed: {error}") from error
    if not encoded:
        raise _invalid("Reference encoding failed")
    return png.tobytes()


def _region(region: Region) -> DetectorRegion:
    return DetectorRegion(region.x, region.y, region.width, region.height)


def _feature(landmark: Landmark) -> FeatureDefinition:
    return FeatureDefinition(
        landmark.name,
        _region(landmark.region),
        landmark.threshold,
        _ROLES[landmark.role],
        landmark.required,
        landmark.orientation_invariant,
        _SUPPORTS[landmark.support],
        landmark.max_template_rotation,
    )


class CalibrationDetectorAdapter(ICalibrationDefinitionValidator):
    def __init__(self, assets: IReferenceAssetRepository) -> None:
        self._assets = assets

    def reference_preview(self, asset: ReferenceAsset) -> ImagePixels:
        data = self._assets.read_png(asset)
        try:
            decoded = cv2.imdecode(np.frombuffer(data, dtype=np.uint8), cv2.IMREAD_COLOR)
        except cv2.error as error:
            raise _invalid(f"Reference image cannot be decoded: {error}") from error
        if decoded is None:
            raise _invalid("Reference image cannot be decoded")
        image = image_pixels(decoded)
        if image.size != asset.size:
            raise _invalid("Reference dimensions differ from saved metadata")
        return image

    def create_detector(self, definition: CalibrationDefinition) -> PaintHeadDetector:
        if (
            definition.binding.camera_role is not CameraRoleID.PRIMARY_VISION
            or definition.binding.movement_group is not MovementGroupID.VERTICAL_SHAFT_ALIGNMENT
        ):
            raise _invalid(
                "This inspection supports Primary vision and Vertical Shaft Alignment only"
            )
        refs = definition.references
        inspection, empty = definition.inspection_region, definition.empty_mount_region
        if refs.present is None or refs.missing is None:
            raise _invalid("Both present and missing reference images are required")
        if inspection is None or empty is None:
            raise _invalid("Inspection and empty-mount regions are required")
        present, missing = (
            self.reference_preview(refs.present),
            self.reference_preview(refs.missing),
        )
        if present.size != missing.size:
            raise _invalid("Present and missing reference images must have the same dimensions")
        landmarks = tuple(_feature(item) for item in definition.landmarks)
        tuning = definition.tuning
        configuration = DetectorConfiguration(
            MatchingConfig(**asdict(tuning.matching)),
            PreprocessingConfig(**asdict(tuning.preprocessing)),
            AlignmentConfig(**asdict(tuning.alignment)),
            CalibrationConfig(
                ReferenceImages(image_array(present), image_array(missing)),
                _region(inspection),
                _region(empty),
                tuple(_region(item.region) for item in definition.excluded_regions),
                tuple(item for item in landmarks if item.role is FeatureRole.PRESENT),
                tuple(item for item in landmarks if item.role is not FeatureRole.PRESENT),
            ),
        )
        try:
            return PaintHeadDetector(configuration)
        except PaintHeadError as error:
            raise _invalid(error.message) from error

    def validate(self, definition: CalibrationDefinition) -> None:
        self.create_detector(definition)

    @staticmethod
    def empty_template(binding: InspectionBinding) -> CalibrationDefinition:
        try:
            configuration = ConfigurationRepository().load()
        except PaintHeadError as error:
            raise _invalid(error.message) from error
        return CalibrationDefinition(
            binding,
            References(None, None),
            None,
            None,
            (),
            (),
            DetectorTuning(
                MatchingTuning(**asdict(configuration.matching)),
                PreprocessingTuning(**asdict(configuration.preprocessing)),
                AlignmentTuning(**asdict(configuration.alignment)),
            ),
        )

    def bundled_template(
        self,
        binding: InspectionBinding,
    ) -> tuple[CalibrationDefinition, ImagePixels, ImagePixels]:
        """Read factory calibration for an explicit import; never activate or write it."""
        try:
            detector = PaintHeadDetector()
        except PaintHeadError as error:
            raise _invalid(error.message) from error
        configuration = detector.configuration
        calibration = configuration.calibration

        def region(value: DetectorRegion) -> Region:
            return Region(value.x, value.y, value.width, value.height)

        inverse_roles = {value: key for key, value in _ROLES.items()}
        inverse_support = {value: key for key, value in _SUPPORTS.items()}
        definition = CalibrationDefinition(
            binding,
            References(None, None),
            region(calibration.inspection_region),
            region(calibration.empty_mount_region),
            tuple(
                ExcludedRegion(ObjectId.new(), f"Excluded region {index + 1}", region(value))
                for index, value in enumerate(calibration.ignored_regions)
            ),
            tuple(
                Landmark(
                    ObjectId.new(),
                    feature.name,
                    region(feature.region),
                    feature.threshold,
                    inverse_roles[feature.role],
                    feature.required,
                    feature.orientation_invariant,
                    inverse_support[feature.support],
                    feature.max_template_rotation,
                )
                for feature in (*calibration.present_features, *calibration.missing_features)
            ),
            DetectorTuning(
                MatchingTuning(**asdict(configuration.matching)),
                PreprocessingTuning(**asdict(configuration.preprocessing)),
                AlignmentTuning(**asdict(configuration.alignment)),
            ),
        )
        references = detector.reference_images
        return definition, image_pixels(references.present), image_pixels(references.missing)


class CalibrationEvaluationSession:
    """One development stream; production detectors and confirmation stay independent."""

    def __init__(self, adapter: CalibrationDetectorAdapter) -> None:
        self._adapter = adapter
        self._definition: CalibrationDefinition | None = None
        self._generation: int | None = None
        self._detector: PaintHeadDetector | None = None
        self._last_sequence: int | None = None

    def reset(self) -> None:
        self._definition = None
        self._generation = None
        self._detector = None
        self._last_sequence = None

    def evaluate(
        self,
        definition: CalibrationDefinition,
        frame: ImageFrame,
        generation: int,
    ) -> CalibrationEvaluation:
        if self._definition != definition or self._generation != generation:
            detector = self._adapter.create_detector(definition)
            self._detector = detector
            self._definition, self._generation, self._last_sequence = definition, generation, None
        detector = self._detector
        if detector is None:
            raise _invalid("Evaluation session has no prepared detector")
        if self._last_sequence is not None and frame.sequence <= self._last_sequence:
            raise PaintHeadCalibrationError(
                CalibrationFailure(
                    CalibrationFailureCode.FRAME_STALE,
                    "A live session requires distinct ordered captures",
                )
            )
        try:
            result = detector.get_status(image_array(frame.image))
        except PaintHeadError as error:
            raise PaintHeadCalibrationError(
                CalibrationFailure(CalibrationFailureCode.EVALUATION_FAILED, error.message)
            ) from error
        self._last_sequence = frame.sequence
        identities = {item.name: item.object_id for item in definition.landmarks}
        matches = (*result.diagnostics.present.matches, *result.diagnostics.missing.matches)
        measured = result.alignment
        pose = result.diagnostics.pose
        return CalibrationEvaluation(
            _STATES[result.status],
            _STATES[result.observed_status],
            _REASONS[result.reason],
            result.held_warning,
            result.diagnostics.quality.usable,
            frame.sequence,
            generation,
            None if measured is None else measured.translation_pixels,
            None if measured is None else float(pose.offset.x),
            None if measured is None else float(pose.offset.y),
            None if measured is None else measured.rotation_degrees,
            tuple(
                LandmarkEvidence(
                    identities[match.feature.name],
                    match.feature.name,
                    match.score,
                    match.passed,
                    match.inlier,
                    Region(
                        match.feature.region.x,
                        match.feature.region.y,
                        match.feature.region.width,
                        match.feature.region.height,
                    ),
                    int(match.shift[0]),
                    int(match.shift[1]),
                )
                for match in matches
            ),
        )


class CalibrationEditorEvaluator:
    """A narrow development port combining preparation, previews and stream evaluation."""

    def __init__(self, adapter: CalibrationDetectorAdapter) -> None:
        self._adapter = adapter
        self._session = CalibrationEvaluationSession(adapter)

    def empty_template(self, binding: InspectionBinding) -> CalibrationDefinition:
        return self._adapter.empty_template(binding)

    def bundled_template(
        self, binding: InspectionBinding
    ) -> tuple[CalibrationDefinition, ImagePixels, ImagePixels]:
        return self._adapter.bundled_template(binding)

    def reference_preview(self, asset: ReferenceAsset) -> ImagePixels:
        return self._adapter.reference_preview(asset)

    def encode_reference(self, image: ImagePixels) -> bytes:
        return encode_reference(image)

    def evaluate(
        self, definition: CalibrationDefinition, frame: ImageFrame, generation: int
    ) -> CalibrationEvaluation:
        return self._session.evaluate(definition, frame, generation)

    def reset(self) -> None:
        self._session.reset()
