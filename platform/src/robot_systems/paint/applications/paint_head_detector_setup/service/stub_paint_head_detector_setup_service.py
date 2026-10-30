"""Faithful in-memory application service for tests and standalone development."""

from collections.abc import Callable
from dataclasses import replace
from hashlib import sha256
from time import monotonic
from typing import NoReturn

from src.robot_systems.paint.contracts.paint_head_calibration.errors import (
    CalibrationFailed,
    CalibrationFailure,
    CalibrationFailureCode,
    CalibrationResult,
    CalibrationSucceeded,
    PaintHeadCalibrationError,
)
from src.robot_systems.paint.contracts.paint_head_calibration.models import (
    AssetId,
    CalibrationCatalog,
    CalibrationChange,
    CalibrationDefinition,
    CalibrationDraft,
    CalibrationEvaluation,
    CalibrationProfile,
    CalibrationRevision,
    ImageFrame,
    ImagePixels,
    LandmarkEvidence,
    LandmarkRole,
    ProfileId,
    ReferenceAsset,
    ReferenceRole,
    References,
    RevisionRef,
)
from src.robot_systems.paint.contracts.paint_head_check.models import (
    PaintHeadObservationReason,
    PaintHeadState,
)

from .i_paint_head_detector_setup_service import IPaintHeadDetectorSetupService
from .stub_data import NOW, sample_catalog, sample_definition, sample_pixels


class StubPaintHeadDetectorSetupService(IPaintHeadDetectorSetupService):
    def __init__(self) -> None:
        self._catalog = sample_catalog()
        self._preview = False
        self._sequence = 0
        self._failure: CalibrationFailure | None = None
        self._in_use: set[RevisionRef] = set()
        self._selection_allowed = True
        self._state = PaintHeadState.PRESENT
        self.preview_starts = 0
        self.preview_stops = 0

    def fail_next(self, failure: CalibrationFailure) -> None:
        self._failure = failure

    def set_revision_in_use(self, reference: RevisionRef, used: bool) -> None:
        if used:
            self._in_use.add(reference)
        else:
            self._in_use.discard(reference)

    def set_selection_allowed(self, allowed: bool) -> None:
        self._selection_allowed = allowed

    def set_detected_state(self, state: PaintHeadState) -> None:
        self._state = state

    def _result[T](self, operation: Callable[[], T]) -> CalibrationResult[T]:
        if self._failure is not None:
            failure, self._failure = self._failure, None
            return CalibrationFailed(failure)
        try:
            return CalibrationSucceeded(operation())
        except PaintHeadCalibrationError as error:
            return CalibrationFailed(error.failure)

    def _mutate(
        self, version: int, operation: Callable[[CalibrationCatalog], CalibrationCatalog]
    ) -> CalibrationResult[CalibrationChange]:
        def mutate() -> CalibrationChange:
            if version != self._catalog.version:
                self._raise(CalibrationFailureCode.CONFLICT, "Catalog changed; reload")
            self._catalog = replace(operation(self._catalog), version=version + 1)
            return CalibrationChange(self._catalog)

        return self._result(mutate)

    @staticmethod
    def _raise(code: CalibrationFailureCode, detail: str) -> NoReturn:
        raise PaintHeadCalibrationError(CalibrationFailure(code, detail))

    @staticmethod
    def _replace(catalog: CalibrationCatalog, profile: CalibrationProfile) -> CalibrationCatalog:
        return replace(
            catalog,
            profiles=tuple(
                profile if current.profile_id == profile.profile_id else current
                for current in catalog.profiles
            ),
        )

    @staticmethod
    def _validate(definition: CalibrationDefinition) -> None:
        if (
            definition.references.present is None
            or definition.references.missing is None
            or definition.inspection_region is None
            or definition.empty_mount_region is None
            or len([item for item in definition.landmarks if item.role is LandmarkRole.PRESENT]) < 2
        ):
            StubPaintHeadDetectorSetupService._raise(
                CalibrationFailureCode.INVALID_CALIBRATION,
                "Complete reference images, regions and landmarks first",
            )

    def load_catalog(self) -> CalibrationResult[CalibrationCatalog]:
        return self._result(lambda: self._catalog)

    def in_use_revisions(self) -> CalibrationResult[tuple[RevisionRef, ...]]:
        return CalibrationSucceeded(tuple(self._in_use))

    def create_profile(
        self, version: int, name: str, description: str
    ) -> CalibrationResult[CalibrationChange]:
        def create(catalog: CalibrationCatalog) -> CalibrationCatalog:
            template = replace(
                sample_definition(),
                references=References(None, None),
                inspection_region=None,
                empty_mount_region=None,
                excluded_regions=(),
                landmarks=(),
            )
            profile = CalibrationProfile(
                ProfileId.new(),
                name,
                description,
                CalibrationDraft(template, None, NOW),
                (),
                1,
            )
            return replace(catalog, profiles=(*catalog.profiles, profile))

        return self._mutate(version, create)

    def import_factory_profile(
        self, version: int, name: str
    ) -> CalibrationResult[CalibrationChange]:
        def create(catalog: CalibrationCatalog) -> CalibrationCatalog:
            definition = sample_definition()
            profile = CalibrationProfile(
                ProfileId.new(),
                name,
                "",
                CalibrationDraft(definition, 1, NOW),
                (CalibrationRevision(1, definition, NOW, ""),),
                2,
            )
            return replace(catalog, profiles=(*catalog.profiles, profile))

        return self._mutate(version, create)

    def save_draft(
        self,
        version: int,
        profile_id: ProfileId,
        definition: CalibrationDefinition,
        base_revision: int | None,
    ) -> CalibrationResult[CalibrationChange]:
        return self._mutate(
            version,
            lambda catalog: self._replace(
                catalog,
                replace(
                    catalog.profile(profile_id),
                    draft=CalibrationDraft(definition, base_revision, NOW),
                ),
            ),
        )

    def save_revision(
        self,
        version: int,
        profile_id: ProfileId,
        definition: CalibrationDefinition,
        description: str,
    ) -> CalibrationResult[CalibrationChange]:
        def save(catalog: CalibrationCatalog) -> CalibrationCatalog:
            self._validate(definition)
            profile = catalog.profile(profile_id)
            number = profile.next_revision
            return self._replace(
                catalog,
                replace(
                    profile,
                    revisions=(
                        *profile.revisions,
                        CalibrationRevision(number, definition, NOW, description),
                    ),
                    next_revision=number + 1,
                    draft=CalibrationDraft(definition, number, NOW),
                ),
            )

        return self._mutate(version, save)

    def edit_revision(
        self, version: int, reference: RevisionRef
    ) -> CalibrationResult[CalibrationChange]:
        def edit(catalog: CalibrationCatalog) -> CalibrationCatalog:
            profile = catalog.profile(reference.profile_id)
            definition = profile.revision(reference.number).definition
            return self._replace(
                catalog, replace(profile, draft=CalibrationDraft(definition, reference.number, NOW))
            )

        return self._mutate(version, edit)

    def select_revision(
        self, version: int, reference: RevisionRef
    ) -> CalibrationResult[CalibrationChange]:
        def select(catalog: CalibrationCatalog) -> CalibrationCatalog:
            if not self._selection_allowed:
                self._raise(
                    CalibrationFailureCode.PROCESS_ACTIVE, "Runtime selection cannot change now"
                )
            self._validate(
                catalog.profile(reference.profile_id).revision(reference.number).definition
            )
            return replace(catalog, selected=reference)

        return self._mutate(version, select)

    def delete_revision(
        self, version: int, reference: RevisionRef
    ) -> CalibrationResult[CalibrationChange]:
        def delete(catalog: CalibrationCatalog) -> CalibrationCatalog:
            self._deletable(catalog, reference)
            profile = catalog.profile(reference.profile_id)
            profile.revision(reference.number)
            return self._replace(
                catalog,
                replace(
                    profile,
                    revisions=tuple(
                        item for item in profile.revisions if item.number != reference.number
                    ),
                ),
            )

        return self._mutate(version, delete)

    def _deletable(self, catalog: CalibrationCatalog, reference: RevisionRef) -> None:
        if reference == catalog.selected:
            self._raise(
                CalibrationFailureCode.REVISION_SELECTED, "Select another runtime revision first"
            )
        if reference in self._in_use:
            self._raise(CalibrationFailureCode.REVISION_IN_USE, "Revision is currently in use")

    def delete_profile(
        self, version: int, profile_id: ProfileId
    ) -> CalibrationResult[CalibrationChange]:
        def delete(catalog: CalibrationCatalog) -> CalibrationCatalog:
            for item in catalog.profile(profile_id).revisions:
                self._deletable(catalog, RevisionRef(profile_id, item.number))
            return replace(
                catalog,
                profiles=tuple(item for item in catalog.profiles if item.profile_id != profile_id),
            )

        return self._mutate(version, delete)

    def discard_draft(
        self, version: int, profile_id: ProfileId
    ) -> CalibrationResult[CalibrationChange]:
        return self._mutate(
            version,
            lambda catalog: self._replace(
                catalog, replace(catalog.profile(profile_id), draft=None)
            ),
        )

    def start_preview(self) -> CalibrationResult[None]:
        self._preview = True
        self.preview_starts += 1
        return CalibrationSucceeded(None)

    def stop_preview(self) -> None:
        if self._preview:
            self.preview_stops += 1
        self._preview = False

    def latest_frame(self) -> CalibrationResult[ImageFrame]:
        def latest() -> ImageFrame:
            if not self._preview:
                self._raise(CalibrationFailureCode.CAMERA_UNAVAILABLE, "Preview is stopped")
            self._sequence += 1
            return ImageFrame(sample_pixels(), self._sequence, monotonic())

        return self._result(latest)

    def reference_preview(self, asset: ReferenceAsset) -> CalibrationResult[ImagePixels]:
        return self._result(sample_pixels)

    def capture_reference(
        self, definition: CalibrationDefinition, frame: ImageFrame, role: ReferenceRole
    ) -> CalibrationResult[CalibrationDefinition]:
        identity = AssetId(sha256(frame.image.bgr + role.value.encode()).hexdigest())
        asset = ReferenceAsset(identity, frame.image.size)
        refs = (
            replace(definition.references, present=asset)
            if role is ReferenceRole.PRESENT
            else replace(definition.references, missing=asset)
        )
        return self._result(lambda: replace(definition, references=refs))

    def evaluate(
        self, definition: CalibrationDefinition, frame: ImageFrame, generation: int
    ) -> CalibrationResult[CalibrationEvaluation]:
        def evaluate() -> CalibrationEvaluation:
            self._validate(definition)
            measured = self._state in (PaintHeadState.PRESENT, PaintHeadState.MISALIGNED)
            reasons = {
                PaintHeadState.PRESENT: PaintHeadObservationReason.ALIGNED,
                PaintHeadState.MISSING: PaintHeadObservationReason.EMPTY_MOUNT,
                PaintHeadState.MISALIGNED: PaintHeadObservationReason.MISALIGNED,
                PaintHeadState.UNKNOWN: PaintHeadObservationReason.INSUFFICIENT_EVIDENCE,
            }
            return CalibrationEvaluation(
                self._state,
                self._state,
                reasons[self._state],
                False,
                True,
                frame.sequence,
                generation,
                1.8 if measured else None,
                1.5 if measured else None,
                0.9 if measured else None,
                0.3 if measured else None,
                tuple(
                    LandmarkEvidence(item.object_id, item.name, 0.87, True, True, item.region, 1, 1)
                    for item in definition.landmarks
                ),
            )

        return self._result(evaluate)

    def end_session(self) -> None:
        self.stop_preview()
