"""Editing state and service delegation; no Qt, image-library or platform service I/O."""

from threading import RLock
from typing import NoReturn

from src.applications.base.i_application_model import IApplicationModel
from src.robot_systems.paint.contracts.paint_head_calibration.errors import (
    CalibrationFailed,
    CalibrationFailure,
    CalibrationFailureCode,
    CalibrationResult,
    PaintHeadCalibrationError,
)
from src.robot_systems.paint.contracts.paint_head_calibration.models import (
    CalibrationCatalog,
    CalibrationChange,
    CalibrationDefinition,
    CalibrationEvaluation,
    ImageFrame,
    ImagePixels,
    ProfileId,
    ReferenceRole,
    RevisionRef,
)

from ..presentation import PreviewUpdate, SetupSnapshot
from ..service.i_paint_head_detector_setup_service import IPaintHeadDetectorSetupService


def _value[T](result: CalibrationResult[T]) -> T:
    if isinstance(result, CalibrationFailed):
        raise PaintHeadCalibrationError(result.failure)
    return result.value


class PaintHeadDetectorSetupModel(IApplicationModel):
    def __init__(self, service: IPaintHeadDetectorSetupService) -> None:
        self._service = service
        self._lock = RLock()
        self._catalog: CalibrationCatalog | None = None
        self._profile_id: ProfileId | None = None
        self._definition: CalibrationDefinition | None = None
        self._saved_definition: CalibrationDefinition | None = None
        self._base_revision: int | None = None
        self._generation = 1
        self._frozen = False
        self._live = False
        self._frame: ImageFrame | None = None
        self._evaluated_sequence: int | None = None
        self._in_use: tuple[RevisionRef, ...] = ()

    @property
    def snapshot(self) -> SetupSnapshot:
        with self._lock:
            return SetupSnapshot(
                self._catalog,
                self._profile_id,
                self._definition,
                self._base_revision,
                self._definition != self._saved_definition,
                self._generation,
                self._frozen,
                self._live,
                self._in_use,
            )

    @property
    def current_frame(self) -> ImageFrame | None:
        with self._lock:
            return self._frame

    def load(self) -> CalibrationCatalog:
        catalog = _value(self._service.load_catalog())
        in_use = _value(self._service.in_use_revisions())
        with self._lock:
            self._catalog = catalog
            self._in_use = in_use
            identity = (
                catalog.selected.profile_id
                if catalog.selected
                else (catalog.profiles[0].profile_id if catalog.profiles else None)
            )
            self._open_profile(identity)
        return catalog

    def select_profile(self, identity: ProfileId) -> None:
        with self._lock:
            if self._definition != self._saved_definition:
                raise PaintHeadCalibrationError(
                    CalibrationFailure(
                        CalibrationFailureCode.CONFLICT,
                        "Resolve unsaved changes before switching profiles",
                    )
                )
            self._require_catalog().profile(identity)
            self._open_profile(identity)

    def discard_local_changes(self) -> None:
        with self._lock:
            self._definition = self._saved_definition
            self._invalidate_evaluation()

    def update_definition(self, definition: CalibrationDefinition) -> None:
        with self._lock:
            if self._profile_id is None:
                self._no_profile()
            self._definition = definition
            self._invalidate_evaluation()

    def create_profile(self, name: str, description: str = "") -> CalibrationChange:
        version = self._catalog_version()
        change = _value(self._service.create_profile(version, name, description))
        with self._lock:
            self._catalog = change.catalog
            self._open_profile(change.catalog.profiles[-1].profile_id)
        return change

    def import_factory_profile(self, name: str) -> CalibrationChange:
        change = _value(self._service.import_factory_profile(self._catalog_version(), name))
        with self._lock:
            self._catalog = change.catalog
            self._open_profile(change.catalog.profiles[-1].profile_id)
        return change

    def save(self) -> None:
        self.save_draft()

    def save_draft(self) -> CalibrationChange:
        with self._lock:
            version, identity, definition = self._editing()
            base_revision = self._base_revision
        change = _value(self._service.save_draft(version, identity, definition, base_revision))
        with self._lock:
            self._catalog = change.catalog
            self._saved_definition = definition
        return change

    def save_revision(self, description: str = "") -> CalibrationChange:
        with self._lock:
            version, identity, definition = self._editing()
        change = _value(self._service.save_revision(version, identity, definition, description))
        with self._lock:
            self._catalog = change.catalog
            self._open_profile(identity)
        return change

    def edit_revision(self, reference: RevisionRef) -> CalibrationChange:
        change = _value(self._service.edit_revision(self._catalog_version(), reference))
        with self._lock:
            self._catalog = change.catalog
            self._open_profile(reference.profile_id)
        return change

    def select_revision(self, reference: RevisionRef) -> CalibrationChange:
        change = _value(self._service.select_revision(self._catalog_version(), reference))
        with self._lock:
            self._catalog = change.catalog
        return change

    def delete_revision(self, reference: RevisionRef) -> CalibrationChange:
        with self._lock:
            catalog = self._require_catalog()
            profile = catalog.profile(reference.profile_id)
            replaces_editor = (
                self._profile_id == reference.profile_id
                and self._base_revision == reference.number
                and profile.draft is None
            )
            if replaces_editor and self._definition != self._saved_definition:
                raise PaintHeadCalibrationError(
                    CalibrationFailure(
                        CalibrationFailureCode.CONFLICT,
                        "Save or discard the working draft before deleting its source revision",
                    )
                )
        change = _value(self._service.delete_revision(self._catalog_version(), reference))
        with self._lock:
            self._catalog = change.catalog
            if replaces_editor:
                self._open_profile(reference.profile_id)
        return change

    def delete_profile(self, identity: ProfileId) -> CalibrationChange:
        change = _value(self._service.delete_profile(self._catalog_version(), identity))
        with self._lock:
            self._catalog = change.catalog
            if self._profile_id == identity:
                self._open_profile(
                    change.catalog.profiles[0].profile_id if change.catalog.profiles else None
                )
        return change

    def discard_saved_draft(self) -> CalibrationChange:
        with self._lock:
            _, identity, _ = self._editing()
        change = _value(self._service.discard_draft(self._catalog_version(), identity))
        with self._lock:
            self._catalog = change.catalog
            self._open_profile(identity)
        return change

    def start_preview(self) -> None:
        _value(self._service.start_preview())

    def stop_preview(self) -> None:
        self._service.stop_preview()
        with self._lock:
            self._live = False
            self._invalidate_evaluation()

    def freeze(self, frozen: bool) -> None:
        with self._lock:
            self._frozen = frozen
            if frozen:
                self._live = False
            self._invalidate_evaluation()

    def set_live(self, enabled: bool) -> None:
        with self._lock:
            self._live = enabled
            if enabled:
                self._frozen = False
            self._invalidate_evaluation()

    def poll_preview(self) -> PreviewUpdate:
        in_use = _value(self._service.in_use_revisions())
        with self._lock:
            self._in_use = in_use
            generation, definition, frozen, live = (
                self._generation,
                self._definition,
                self._frozen,
                self._live,
            )
        if frozen:
            return PreviewUpdate(generation, None, None)
        result = self._service.latest_frame()
        if isinstance(result, CalibrationFailed):
            return PreviewUpdate(generation, None, None, result.failure)
        frame = result.value
        evaluation = None
        with self._lock:
            if generation != self._generation:
                return PreviewUpdate(generation, None, None)
            self._frame = frame
            self._in_use = in_use
            already_evaluated = self._evaluated_sequence == frame.sequence
        if live and definition is not None and not already_evaluated:
            evaluated = self._service.evaluate(definition, frame, generation)
            if isinstance(evaluated, CalibrationFailed):
                return PreviewUpdate(generation, frame, None, evaluated.failure)
            evaluation = evaluated.value
            with self._lock:
                if generation == self._generation:
                    self._evaluated_sequence = frame.sequence
        return PreviewUpdate(generation, frame, evaluation)

    def capture_snapshot(self) -> ImageFrame:
        with self._lock:
            frame = self._frame if self._frozen else None
        if frame is None:
            frame = _value(self._service.latest_frame())
        with self._lock:
            self._frame = frame
            self._frozen = True
            self._live = False
            self._invalidate_evaluation()
        return frame

    def confirm_reference(self, frame: ImageFrame, role: ReferenceRole) -> CalibrationDefinition:
        with self._lock:
            _, _, definition = self._editing()
        updated = _value(self._service.capture_reference(definition, frame, role))
        self.update_definition(updated)
        return updated

    def evaluate_once(self) -> CalibrationEvaluation:
        with self._lock:
            _, _, definition = self._editing()
            frame = self._frame if self._frozen else None
            self._live = False
            self._invalidate_evaluation()
            generation = self._generation
        if frame is None:
            frame = _value(self._service.latest_frame())
        evaluated = _value(self._service.evaluate(definition, frame, generation))
        with self._lock:
            if generation == self._generation:
                self._frame = frame
                self._frozen = True
        return evaluated

    def reference_preview(self, role: ReferenceRole) -> ImagePixels:
        with self._lock:
            _, _, definition = self._editing()
            reference = (
                definition.references.present
                if role is ReferenceRole.PRESENT
                else definition.references.missing
            )
        if reference is None:
            raise PaintHeadCalibrationError(
                CalibrationFailure(
                    CalibrationFailureCode.ASSET_NOT_FOUND, "Reference image has not been captured"
                )
            )
        return _value(self._service.reference_preview(reference))

    def end_session(self) -> None:
        self.stop_preview()
        self._service.end_session()

    def _open_profile(self, identity: ProfileId | None) -> None:
        self._profile_id = identity
        self._definition = None
        self._base_revision = None
        if identity is not None:
            profile = self._require_catalog().profile(identity)
            if profile.draft is not None:
                self._definition = profile.draft.definition
                self._base_revision = profile.draft.base_revision
            elif profile.revisions:
                latest = max(profile.revisions, key=lambda revision: revision.number)
                self._definition = latest.definition
                self._base_revision = latest.number
        self._saved_definition = self._definition
        self._invalidate_evaluation()

    def _editing(self) -> tuple[int, ProfileId, CalibrationDefinition]:
        if self._profile_id is None or self._definition is None:
            self._no_profile()
        return self._require_catalog().version, self._profile_id, self._definition

    def _catalog_version(self) -> int:
        with self._lock:
            return self._require_catalog().version

    def _require_catalog(self) -> CalibrationCatalog:
        if self._catalog is None:
            raise PaintHeadCalibrationError(
                CalibrationFailure(
                    CalibrationFailureCode.STORAGE_LOAD_FAILED, "Load the calibration library first"
                )
            )
        return self._catalog

    @staticmethod
    def _no_profile() -> NoReturn:
        raise PaintHeadCalibrationError(
            CalibrationFailure(
                CalibrationFailureCode.PROFILE_NOT_FOUND,
                "Select or create a calibration profile first",
            )
        )

    def _invalidate_evaluation(self) -> None:
        self._generation += 1
        self._evaluated_sequence = None
