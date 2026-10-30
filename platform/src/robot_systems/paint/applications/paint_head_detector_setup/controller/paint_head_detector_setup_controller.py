"""MVC coordination and queued worker delivery; no settings, camera or robot services."""

import logging
from collections.abc import Callable
from dataclasses import dataclass, replace
from functools import partial

from PyQt6.QtCore import QTimer

from src.applications.base.background_worker import BackgroundWorker
from src.applications.base.i_application_controller import IApplicationController
from src.robot_systems.paint.contracts.paint_head_calibration.errors import (
    CalibrationFailed,
    CalibrationFailure,
    CalibrationFailureCode,
    CalibrationSucceeded,
    PaintHeadCalibrationError,
)
from src.robot_systems.paint.contracts.paint_head_calibration.models import (
    CalibrationChange,
    CalibrationEvaluation,
    ImageFrame,
    ImagePixels,
    ProfileId,
    ReferenceRole,
    Region,
    RevisionRef,
)

from ..editor_contracts import (
    EditorKind,
    EditorTarget,
    GeometryEdit,
    ObjectPropertiesEdit,
    UnsavedDecision,
)
from ..model import editing
from ..model.paint_head_detector_setup_model import PaintHeadDetectorSetupModel
from ..presentation import PreviewUpdate
from ..tuning_fields import TUNING_PARAMETERS, TuningParameterId, parameter
from ..view.paint_head_detector_setup_view import PaintHeadDetectorSetupView
from ..view.widgets.forms import translate

_LOG = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True)
class _Task:
    operation: Callable[[], object]
    complete: Callable[[object], None]
    finite: bool


class PaintHeadDetectorSetupController(IApplicationController, BackgroundWorker):
    def __init__(
        self, model: PaintHeadDetectorSetupModel, view: PaintHeadDetectorSetupView
    ) -> None:
        BackgroundWorker.__init__(self)
        self._model = model
        self._view = view
        self._stopped = False
        self._visible = True
        self._loaded = False
        self._preview_needed = False
        self._current: _Task | None = None
        self._pending: _Task | None = None
        self._after_save: Callable[[], None] | None = None
        self._selected: EditorTarget | None = None
        self._last_generation = -1
        self._last_usage: tuple[RevisionRef, ...] = ()
        self._capture_role = ReferenceRole.PRESENT
        self._was_frozen = False
        self._timer = QTimer()
        self._timer.setInterval(100)
        self._timer.timeout.connect(self._poll)
        self._connections = (
            (view.profile_selected, self._on_profile),
            (view.create_requested, self._on_create),
            (view.import_requested, self._on_import),
            (view.save_draft_requested, self._on_save_draft),
            (view.save_revision_requested, self._on_save_revision),
            (view.edit_revision_requested, self._on_edit_revision),
            (view.select_revision_requested, self._on_select_revision),
            (view.delete_revision_requested, self._on_delete_revision),
            (view.delete_profile_requested, self._on_delete_profile),
            (view.discard_local_requested, self._on_discard_local),
            (view.discard_saved_draft_requested, self._on_discard_saved),
            (view.capture_requested, self._on_capture),
            (view.reference_preview_requested, self._on_reference_preview),
            (view.freeze_requested, self._on_freeze),
            (view.live_requested, self._on_live),
            (view.test_requested, self._on_test),
            (view.geometry_edited, self._on_geometry),
            (view.object_selected, self._on_selection),
            (view.properties_edited, self._on_properties),
            (view.object_removed, self._on_remove),
            (view.tuning_edited, self._on_tuning),
            (view.screen_shown, self._on_shown),
            (view.screen_hidden, self._on_hidden),
            (view.language_changed, self._refresh),
        )
        for signal, callback in self._connections:
            signal.connect(callback)

    def load(self) -> None:
        self._submit(self._model.load, self._on_loaded)

    def has_active_operations(self) -> bool:
        return bool(
            (self._current and self._current.finite) or (self._pending and self._pending.finite)
        )

    def has_running_workers(self) -> bool:
        # The factory navigation guard must exclude continuous preview/evaluation.
        return self.has_active_operations()

    def stop(self) -> None:
        if self._stopped:
            return
        self._stopped = True
        self._timer.stop()
        self._pending = None
        self._preview_needed = False
        self._model.stop_preview()
        self._stop_threads()
        self._model.end_session()
        for signal, callback in self._connections:
            try:
                signal.disconnect(callback)
            except (TypeError, RuntimeError):
                pass
        self._current = None

    def _submit(
        self,
        operation: Callable[[], object],
        complete: Callable[[object], None],
        *,
        finite: bool = True,
    ) -> None:
        if self._stopped:
            return
        task = _Task(operation, complete, finite)
        if self._current is not None:
            if finite and self._pending is None:
                self._pending = task
                self._view.set_busy(True)
            return
        self._current = task
        if finite:
            self._view.set_busy(True)
        self._run_in_thread(self._perform, self._on_completed, self._on_worker_failure)

    def _perform(self) -> object:
        task = self._current
        if task is None:
            return CalibrationFailed(
                CalibrationFailure(CalibrationFailureCode.CANCELLED, "Operation cancelled")
            )
        try:
            return CalibrationSucceeded(task.operation())
        except PaintHeadCalibrationError as error:
            return CalibrationFailed(error.failure)
        except Exception as error:
            _LOG.exception("Paint-head setup operation failed")
            return CalibrationFailed(
                CalibrationFailure(CalibrationFailureCode.EVALUATION_FAILED, str(error))
            )

    def _on_completed(self, result: object) -> None:
        if self._stopped:
            return
        task, self._current = self._current, None
        if not self._visible:
            # A queued preview activation can finish after hideEvent cancelled
            # its previous subscription. Revoke any late activation as well.
            self._model.stop_preview()
        if self._visible and task is not None:
            self._view.set_busy(False)
            if isinstance(result, CalibrationFailed):
                self._after_save = None
                if task.finite:
                    self._view.show_failure(result.failure)
                else:
                    self._view.set_preview_failure(result.failure)
            elif isinstance(result, CalibrationSucceeded):
                task.complete(result.value)
        if self._current is None and self._pending is not None:
            pending, self._pending = self._pending, None
            self._submit(pending.operation, pending.complete, finite=pending.finite)
        self._ensure_preview()

    def _on_worker_failure(self, detail: str) -> None:
        self._on_completed(
            CalibrationFailed(CalibrationFailure(CalibrationFailureCode.EVALUATION_FAILED, detail))
        )

    def _on_loaded(self, _: object) -> None:
        self._loaded = True
        self._refresh()
        if self._visible:
            self._preview_needed = True
            self._ensure_preview()

    def _ensure_preview(self) -> None:
        if self._preview_needed and self._visible and self._loaded and self._current is None:
            self._preview_needed = False
            self._submit(self._model.start_preview, self._on_preview_started, finite=False)

    def _on_preview_started(self, _: object) -> None:
        if self._visible and not self._stopped:
            self._timer.start()

    def _on_shown(self) -> None:
        if self._stopped:
            return
        self._visible = True
        if self._model.snapshot.catalog is not None:
            self._loaded = True
        if self._loaded:
            self._refresh()
            self._preview_needed = True
            self._ensure_preview()

    def _on_hidden(self) -> None:
        self._visible = False
        self._timer.stop()
        self._pending = None
        self._preview_needed = False
        self._model.stop_preview()

    def _poll(self) -> None:
        if not self._visible or self._stopped or self._current is not None:
            return
        self._submit(self._model.poll_preview, self._on_preview, finite=False)

    def _on_preview(self, update: object) -> None:
        if (
            not isinstance(update, PreviewUpdate)
            or update.generation != self._model.snapshot.generation
        ):
            return
        if self._model.snapshot.in_use_revisions != self._last_usage:
            self._refresh()
        if update.frame is not None:
            self._view.set_frame(update.frame)
        if update.failure is not None:
            self._view.set_preview_failure(update.failure)
        elif update.evaluation is not None:
            self._view.set_evaluation(update.evaluation)

    def _refresh(self) -> None:
        if self._stopped:
            return
        snapshot = self._model.snapshot
        self._last_usage = snapshot.in_use_revisions
        values = () if snapshot.definition is None else editing.objects(snapshot.definition)
        translated = tuple(
            replace(
                item,
                name=translate(
                    "Inspection region"
                    if item.target.kind is EditorKind.INSPECTION
                    else "Empty-mount region"
                ),
            )
            if not item.name
            else item
            for item in values
        )
        if self._selected is not None and not any(item.target == self._selected for item in values):
            self._selected = None
        landmark = None
        if snapshot.definition is not None and self._selected is not None:
            landmark = next(
                (
                    item
                    for item in snapshot.definition.landmarks
                    if item.object_id == self._selected.object_id
                ),
                None,
            )
        self._view.set_snapshot(snapshot, translated, self._selected, landmark)
        if snapshot.definition is not None:
            self._view.set_tuning_values(
                {item.identity: item.read(snapshot.definition.tuning) for item in TUNING_PARAMETERS}
            )
        if snapshot.generation != self._last_generation:
            self._view.clear_evaluation()
            self._last_generation = snapshot.generation

    def _on_changed(self, result: object) -> None:
        self._refresh()
        if isinstance(result, CalibrationChange) and result.warnings:
            self._view.set_notice("\n".join(item.detail for item in result.warnings), error=True)
        else:
            self._view.set_notice(
                translate("Saved. Runtime selection changes only when explicitly selected.")
            )

    def _resolve_draft(self, continuation: Callable[[], None]) -> None:
        if not self._model.snapshot.dirty:
            continuation()
            return
        decision = self._view.ask_unsaved()
        if decision is UnsavedDecision.SAVE:
            self._after_save = continuation
            self._submit(self._model.save_draft, self._on_draft_saved)
        elif decision is UnsavedDecision.DISCARD:
            self._model.discard_local_changes()
            continuation()
        else:
            self._refresh()

    def _on_profile(self, identity: object) -> None:
        if not isinstance(identity, ProfileId) or identity == self._model.snapshot.profile_id:
            return
        self._resolve_draft(partial(self._select_profile, identity))

    def _select_profile(self, identity: ProfileId) -> None:
        self._model.select_profile(identity)
        self._selected = None
        self._refresh()

    def _on_create(self, name: str, description: str) -> None:
        self._resolve_draft(partial(self._create, name, description))

    def _create(self, name: str, description: str) -> None:
        self._submit(partial(self._model.create_profile, name, description), self._on_changed)

    def _on_import(self, name: str) -> None:
        self._resolve_draft(partial(self._import, name))

    def _import(self, name: str) -> None:
        self._submit(partial(self._model.import_factory_profile, name), self._on_changed)

    def _on_save_draft(self) -> None:
        self._submit(self._model.save_draft, self._on_draft_saved)

    def _on_draft_saved(self, result: object) -> None:
        self._on_changed(result)
        continuation, self._after_save = self._after_save, None
        if continuation is not None:
            continuation()

    def _on_save_revision(self, description: str) -> None:
        self._submit(partial(self._model.save_revision, description), self._on_changed)

    def _on_edit_revision(self, reference: object) -> None:
        if isinstance(reference, RevisionRef):
            self._resolve_draft(partial(self._edit_revision, reference))

    def _edit_revision(self, reference: RevisionRef) -> None:
        catalog = self._model.snapshot.catalog
        if catalog is None:
            return
        profile = catalog.profile(reference.profile_id)
        if (
            profile.draft is not None
            and profile.draft.definition != profile.revision(reference.number).definition
            and not self._view.confirm_replace_draft()
        ):
            return
        self._submit(partial(self._model.edit_revision, reference), self._on_changed)

    def _on_select_revision(self, reference: object) -> None:
        if isinstance(reference, RevisionRef):
            self._submit(partial(self._model.select_revision, reference), self._on_changed)

    def _on_delete_revision(self, reference: object) -> None:
        if isinstance(reference, RevisionRef):
            self._submit(partial(self._model.delete_revision, reference), self._on_changed)

    def _on_delete_profile(self, identity: object) -> None:
        if isinstance(identity, ProfileId):
            self._submit(partial(self._model.delete_profile, identity), self._on_changed)

    def _on_discard_local(self) -> None:
        self._model.discard_local_changes()
        self._refresh()

    def _on_discard_saved(self) -> None:
        self._submit(self._model.discard_saved_draft, self._on_changed)

    def _on_capture(self, role: object) -> None:
        if not isinstance(role, ReferenceRole):
            return
        self._capture_role = role
        self._was_frozen = self._model.snapshot.frozen
        self._submit(self._model.capture_snapshot, self._on_snapshot_captured)

    def _on_snapshot_captured(self, result: object) -> None:
        if not isinstance(result, ImageFrame):
            return
        self._refresh()
        self._view.set_frame(result)
        chosen = self._view.confirm_capture(result, self._capture_role)
        if chosen is not None:
            self._submit(
                partial(self._model.confirm_reference, result, chosen), self._on_reference_confirmed
            )
        else:
            self._model.freeze(self._was_frozen)
            self._refresh()

    def _on_reference_confirmed(self, _: object) -> None:
        self._refresh()
        self._view.set_notice(
            translate("Reference added to draft. Save the draft or create a calibration revision.")
        )

    def _on_reference_preview(self, role: object) -> None:
        if isinstance(role, ReferenceRole):
            self._submit(partial(self._model.reference_preview, role), self._on_reference_image)

    def _on_reference_image(self, result: object) -> None:
        if isinstance(result, ImagePixels):
            self._view.show_reference(result)

    def _on_freeze(self, frozen: bool) -> None:
        self._model.freeze(frozen)
        self._refresh()

    def _on_live(self, enabled: bool) -> None:
        self._model.set_live(enabled)
        self._refresh()

    def _on_test(self) -> None:
        self._submit(self._model.evaluate_once, self._on_evaluated)

    def _on_evaluated(self, result: object) -> None:
        self._refresh()
        if (
            isinstance(result, CalibrationEvaluation)
            and result.generation == self._model.snapshot.generation
        ):
            frame = self._model.current_frame
            if frame is not None:
                self._view.set_frame(frame)
            self._view.set_evaluation(result)

    def _on_selection(self, target: object) -> None:
        self._selected = target if isinstance(target, EditorTarget) else None
        self._refresh()

    def _on_geometry(self, edit: object) -> None:
        definition = self._model.snapshot.definition
        if isinstance(edit, GeometryEdit) and definition is not None:
            try:
                updated, self._selected = editing.change_geometry(definition, edit)
                self._model.update_definition(updated)
                self._refresh()
            except PaintHeadCalibrationError as error:
                self._view.set_notice(error.failure.detail, error=True)

    def _on_properties(self, edit: object) -> None:
        definition = self._model.snapshot.definition
        if not isinstance(edit, ObjectPropertiesEdit) or definition is None:
            return
        try:
            region = Region(edit.x, edit.y, edit.width, edit.height)
            updated, self._selected = editing.change_geometry(
                definition,
                GeometryEdit(
                    edit.target,
                    region,
                    edit.support,
                    edit.role,
                ),
            )
            if edit.target.kind is EditorKind.LANDMARK:
                current = next(
                    item for item in updated.landmarks if item.object_id == edit.target.object_id
                )
                updated = editing.replace_landmark(
                    updated,
                    replace(
                        current,
                        name=edit.name,
                        threshold=edit.threshold,
                        role=edit.role,
                        support=edit.support,
                        required=edit.required,
                        orientation_invariant=edit.orientation_invariant,
                        max_template_rotation=edit.max_template_rotation,
                    ),
                )
            elif edit.target.kind is EditorKind.EXCLUDED:
                updated = replace(
                    updated,
                    excluded_regions=tuple(
                        replace(item, name=edit.name)
                        if item.object_id == edit.target.object_id
                        else item
                        for item in updated.excluded_regions
                    ),
                )
            self._model.update_definition(updated)
            self._refresh()
        except PaintHeadCalibrationError as error:
            self._view.set_notice(error.failure.detail, error=True)

    def _on_remove(self, target: object) -> None:
        definition = self._model.snapshot.definition
        if isinstance(target, EditorTarget) and definition is not None:
            self._model.update_definition(editing.remove_object(definition, target))
            self._selected = None
            self._refresh()

    def _on_tuning(self, identity: object, value: object) -> None:
        definition = self._model.snapshot.definition
        if (
            isinstance(identity, TuningParameterId)
            and type(value) in (int, float)
            and definition is not None
        ):
            try:
                self._model.update_definition(
                    replace(definition, tuning=parameter(identity).write(definition.tuning, value))
                )
                self._refresh()
            except PaintHeadCalibrationError as error:
                self._view.set_notice(error.failure.detail, error=True)
