"""Concrete application adapter; the only MVC layer that knows runtime dependencies."""

from collections.abc import Callable
from dataclasses import replace
from functools import partial
from threading import RLock

from src.robot_systems.paint.contracts.paint_head_calibration.errors import (
    CalibrationFailed,
    CalibrationFailure,
    CalibrationFailureCode,
    CalibrationResult,
    CalibrationSucceeded,
    PaintHeadCalibrationError,
)
from src.robot_systems.paint.contracts.paint_head_calibration.interfaces import (
    ICalibrationEditorEvaluator,
    ICalibrationLease,
    ICalibrationLibrary,
    ISetupFrameSource,
)
from src.robot_systems.paint.contracts.paint_head_calibration.models import (
    CalibrationCatalog,
    CalibrationChange,
    CalibrationDefinition,
    CalibrationEvaluation,
    ImageFrame,
    ImagePixels,
    InspectionBinding,
    ProfileId,
    ReferenceAsset,
    ReferenceRole,
    References,
    RevisionRef,
)

from .i_paint_head_detector_setup_service import IPaintHeadDetectorSetupService


def _result[T](operation: Callable[[], T]) -> CalibrationResult[T]:
    try:
        return CalibrationSucceeded(operation())
    except PaintHeadCalibrationError as error:
        return CalibrationFailed(error.failure)


class PaintHeadDetectorSetupApplicationService(IPaintHeadDetectorSetupService):
    def __init__(
        self,
        library: ICalibrationLibrary,
        evaluator: ICalibrationEditorEvaluator,
        frames: ISetupFrameSource,
        binding: InspectionBinding,
    ) -> None:
        self._library = library
        self._evaluator = evaluator
        self._frames = frames
        self._binding = binding
        self._lock = RLock()
        self._reference_leases: list[ICalibrationLease] = []

    def load_catalog(self) -> CalibrationResult[CalibrationCatalog]:
        return _result(self._library.load)

    def in_use_revisions(self) -> CalibrationResult[tuple[RevisionRef, ...]]:
        return _result(self._library.in_use_revisions)

    def create_profile(
        self, version: int, name: str, description: str
    ) -> CalibrationResult[CalibrationChange]:
        return _result(partial(self._create_profile, version, name, description))

    def _create_profile(self, version: int, name: str, description: str) -> CalibrationChange:
        definition = self._evaluator.empty_template(self._binding)
        return self._library.create_profile(version, name, description, definition)

    def import_factory_profile(
        self, version: int, name: str
    ) -> CalibrationResult[CalibrationChange]:
        return _result(partial(self._import_factory_profile, version, name))

    def _import_factory_profile(self, version: int, name: str) -> CalibrationChange:
        definition, present, missing = self._evaluator.bundled_template(self._binding)
        present_asset, first = self._library.store_reference(
            self._evaluator.encode_reference(present), present.size
        )
        try:
            missing_asset, second = self._library.store_reference(
                self._evaluator.encode_reference(missing), missing.size
            )
            try:
                return self._library.import_profile(
                    version,
                    name,
                    replace(definition, references=References(present_asset, missing_asset)),
                )
            finally:
                second.close()
        finally:
            first.close()

    def save_draft(
        self,
        version: int,
        profile_id: ProfileId,
        definition: CalibrationDefinition,
        base_revision: int | None,
    ) -> CalibrationResult[CalibrationChange]:
        return _result(
            partial(self._library.save_draft, version, profile_id, definition, base_revision)
        )

    def save_revision(
        self,
        version: int,
        profile_id: ProfileId,
        definition: CalibrationDefinition,
        description: str,
    ) -> CalibrationResult[CalibrationChange]:
        return _result(
            partial(self._library.save_revision, version, profile_id, definition, description)
        )

    def edit_revision(
        self, version: int, reference: RevisionRef
    ) -> CalibrationResult[CalibrationChange]:
        return _result(partial(self._library.edit_revision, version, reference))

    def select_revision(
        self, version: int, reference: RevisionRef
    ) -> CalibrationResult[CalibrationChange]:
        return _result(partial(self._library.select_revision, version, reference))

    def delete_revision(
        self, version: int, reference: RevisionRef
    ) -> CalibrationResult[CalibrationChange]:
        return _result(partial(self._library.delete_revision, version, reference))

    def delete_profile(
        self, version: int, profile_id: ProfileId
    ) -> CalibrationResult[CalibrationChange]:
        return _result(partial(self._library.delete_profile, version, profile_id))

    def discard_draft(
        self, version: int, profile_id: ProfileId
    ) -> CalibrationResult[CalibrationChange]:
        return _result(partial(self._library.discard_draft, version, profile_id))

    def start_preview(self) -> CalibrationResult[None]:
        try:
            self._frames.start()
        except PaintHeadCalibrationError as error:
            return CalibrationFailed(error.failure)
        except (OSError, RuntimeError) as error:
            return CalibrationFailed(
                CalibrationFailure(CalibrationFailureCode.CAMERA_UNAVAILABLE, str(error))
            )
        return CalibrationSucceeded(None)

    def stop_preview(self) -> None:
        self._frames.stop()

    def latest_frame(self) -> CalibrationResult[ImageFrame]:
        return _result(self._frames.latest)

    def reference_preview(self, asset: ReferenceAsset) -> CalibrationResult[ImagePixels]:
        return _result(partial(self._evaluator.reference_preview, asset))

    def capture_reference(
        self, definition: CalibrationDefinition, frame: ImageFrame, role: ReferenceRole
    ) -> CalibrationResult[CalibrationDefinition]:
        return _result(partial(self._capture_reference, definition, frame, role))

    def _capture_reference(
        self, definition: CalibrationDefinition, frame: ImageFrame, role: ReferenceRole
    ) -> CalibrationDefinition:
        if not isinstance(role, ReferenceRole):
            raise PaintHeadCalibrationError(
                CalibrationFailure(
                    CalibrationFailureCode.INVALID_DATA, "Reference role must be typed"
                )
            )
        asset, lease = self._library.store_reference(
            self._evaluator.encode_reference(frame.image), frame.image.size
        )
        with self._lock:
            self._reference_leases.append(lease)
        match role:
            case ReferenceRole.PRESENT:
                references = replace(definition.references, present=asset)
            case ReferenceRole.MISSING:
                references = replace(definition.references, missing=asset)
            case _:
                raise PaintHeadCalibrationError(
                    CalibrationFailure(
                        CalibrationFailureCode.INVALID_DATA, "Reference role must be typed"
                    )
                )
        return replace(definition, references=references)

    def evaluate(
        self, definition: CalibrationDefinition, frame: ImageFrame, generation: int
    ) -> CalibrationResult[CalibrationEvaluation]:
        return _result(partial(self._evaluate, definition, frame, generation))

    def _evaluate(
        self, definition: CalibrationDefinition, frame: ImageFrame, generation: int
    ) -> CalibrationEvaluation:
        lease = self._library.pin_definition(definition)
        try:
            with self._lock:
                return self._evaluator.evaluate(definition, frame, generation)
        finally:
            lease.close()

    def end_session(self) -> None:
        self._frames.stop()
        with self._lock:
            self._evaluator.reset()
            for lease in self._reference_leases:
                lease.close()
            self._reference_leases.clear()
