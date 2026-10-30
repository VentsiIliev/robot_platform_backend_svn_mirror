"""Controller behavior against a stub service and offscreen widgets, without hardware."""

from dataclasses import replace
from threading import Event, Timer
from time import monotonic
from unittest import TestCase

from PyQt6.QtCore import QEvent, QPoint, Qt
from PyQt6.QtTest import QTest
from PyQt6.QtWidgets import QApplication, QComboBox, QLabel, QListWidget, QPushButton

from src.applications.base.config.virtual_keyboard_config import (
    is_custom_virtual_keyboard_enabled, set_custom_virtual_keyboard_enabled,
)
from src.applications.base.widgets.keyboard_number_field import KeyboardNumberField
from src.robot_systems.paint.applications.paint_head_detector_setup.controller.paint_head_detector_setup_controller import (
    PaintHeadDetectorSetupController,
)
from src.robot_systems.paint.applications.paint_head_detector_setup.editor_contracts import (
    EditorKind, EditorTarget, EditorTool, GeometryEdit, SetupPage, UnsavedDecision,
)
from src.robot_systems.paint.applications.paint_head_detector_setup.tuning_fields import TuningParameterId
from src.robot_systems.paint.applications.paint_head_detector_setup.view.widgets.forms import TuningField
from src.robot_systems.paint.applications.paint_head_detector_setup.model.paint_head_detector_setup_model import (
    PaintHeadDetectorSetupModel,
)
from src.robot_systems.paint.applications.paint_head_detector_setup.service.stub_data import PROFILE_ID, sample_pixels
from src.robot_systems.paint.applications.paint_head_detector_setup.service.stub_paint_head_detector_setup_service import (
    StubPaintHeadDetectorSetupService,
)
from src.robot_systems.paint.applications.paint_head_detector_setup.view.paint_head_detector_setup_view import (
    PaintHeadDetectorSetupView,
)
from src.robot_systems.paint.applications.paint_head_detector_setup.view.widgets.calibration_canvas import CalibrationCanvas
from src.robot_systems.paint.contracts.paint_head_calibration.errors import (
    CalibrationFailed, CalibrationFailure, CalibrationFailureCode,
)
from src.robot_systems.paint.contracts.paint_head_calibration.models import (
    LandmarkRole, LandmarkSupport, ProfileId, ReferenceRole, Region, RevisionRef,
)

_APP = QApplication.instance() or QApplication(["paint-head-controller-tests"])


class _Stub(StubPaintHeadDetectorSetupService):
    def __init__(self):
        super().__init__()
        self.evaluation_entered = Event()
        self.evaluation_release = Event()
        self.delay_evaluation = False
        self.save_failure = None
        self.evaluation_failure = None
        self.evaluated_definitions = []

    def evaluate(self, definition, frame, generation):
        self.evaluated_definitions.append(definition)
        if self.evaluation_failure is not None:
            return CalibrationFailed(self.evaluation_failure)
        if self.delay_evaluation:
            self.delay_evaluation = False
            self.evaluation_entered.set()
            self.evaluation_release.wait(2)
        return super().evaluate(definition, frame, generation)

    def save_draft(self, version, profile_id, definition, base_revision):
        if self.save_failure is not None:
            failure, self.save_failure = self.save_failure, None
            return CalibrationFailed(failure)
        return super().save_draft(version, profile_id, definition, base_revision)


class _View(PaintHeadDetectorSetupView):
    def __init__(self):
        self.failures = []
        self.reports = []
        self.frames = []
        self.capture_previews = []
        self.accept_capture = True
        self.unsaved_decision = UnsavedDecision.CANCEL
        self.replace_draft = False
        self.replace_prompts = 0
        super().__init__()

    def show_failure(self, failure):
        self.failures.append(failure)
        self.set_notice(failure.detail, error=True)

    def set_frame(self, frame):
        self.frames.append(frame)
        super().set_frame(frame)

    def set_evaluation(self, report):
        self.reports.append(report)
        super().set_evaluation(report)

    def confirm_capture(self, frame, role):
        self.capture_previews.append((frame, role))
        return role if self.accept_capture else None

    def ask_unsaved(self):
        return self.unsaved_decision

    def confirm_replace_draft(self):
        self.replace_prompts += 1
        return self.replace_draft


class CalibrationControllerTests(TestCase):
    def setUp(self):
        self.keyboard = is_custom_virtual_keyboard_enabled()
        set_custom_virtual_keyboard_enabled(False)
        self.addCleanup(set_custom_virtual_keyboard_enabled, self.keyboard)
        self.service = _Stub()
        self.model = PaintHeadDetectorSetupModel(self.service)
        self.view = _View()
        self.controller = PaintHeadDetectorSetupController(self.model, self.view)
        self.addCleanup(self.close)
        self.controller.load()
        self.view.resize(1400, 900)
        self.view.show()
        self.wait_for(lambda: bool(self.view.frames))

    def close(self):
        self.service.evaluation_release.set()
        self.controller.stop()
        self.view.close()
        self.view.deleteLater()
        _APP.processEvents()

    def wait_for(self, predicate, timeout=3):
        deadline = monotonic() + timeout
        while monotonic() < deadline:
            _APP.processEvents()
            if predicate():
                return
            QTest.qWait(5)
        self.fail("Timed out waiting for controller operation")

    def edit(self):
        self.view.geometry_edited.emit(GeometryEdit(
            EditorTarget(EditorKind.INSPECTION, None), Region(150, 50, 340, 380),
            LandmarkSupport.RECTANGLE, LandmarkRole.PRESENT,
        ))

    def test_preview_does_not_block_navigation_as_a_finite_operation(self):
        self.assertFalse(self.controller.has_active_operations())
        self.assertFalse(self.controller.has_running_workers())
        self.assertTrue(self.view.can_close())

    def test_profile_picker_matches_persisted_id_by_value_not_qt_object_identity(self):
        identity = ProfileId(PROFILE_ID.value)
        self.assertEqual(identity, PROFILE_ID)
        self.assertIsNot(identity, PROFILE_ID)
        self.view.set_snapshot(replace(self.model.snapshot, profile_id=identity), ())
        picker = self.view.findChild(QComboBox, 'calibrationProfilePicker')
        self.assertEqual(picker.currentText(), 'Standard')
        self.assertEqual(picker.currentData(), PROFILE_ID)

    def open_settings_preview(self):
        navigation = self.view.findChild(QListWidget, 'calibrationNavigation')
        navigation.setCurrentRow(4)
        button = self.view.findChild(QPushButton, 'calibrationSettingsLivePreview')
        self.assertTrue(button.isChecked(), 'Opening Settings must start live evaluation')
        return navigation, button

    def test_settings_selected_before_async_load_still_starts_live_evaluation(self):
        model = PaintHeadDetectorSetupModel(_Stub())
        view = _View()
        view.findChild(QListWidget, 'calibrationNavigation').setCurrentRow(4)
        controller = PaintHeadDetectorSetupController(model, view)
        self.addCleanup(view.close)
        self.addCleanup(controller.stop)
        controller.load()
        self.wait_for(lambda: model.snapshot.live)
        self.assertTrue(view.findChild(QPushButton, 'calibrationSettingsLivePreview').isChecked())

    def test_settings_edits_update_visible_live_result_from_unsaved_draft(self):
        catalog = self.model.snapshot.catalog
        navigation, button = self.open_settings_preview()
        self.wait_for(lambda: bool(self.view.reports))
        before = self.view.reports[-1].generation
        field = self.view.findChild(TuningField, 'calibrationTuning_' + TuningParameterId.ALIGNMENT_MAX_TRANSLATION_PIXELS.value)
        field.findChild(KeyboardNumberField).setValue(12.3)
        self.wait_for(lambda: self.view.reports[-1].generation > before)
        self.assertEqual(navigation.currentRow(), 4)
        self.assertTrue(button.isChecked())
        self.assertTrue(self.model.snapshot.live)
        self.assertTrue(self.model.snapshot.dirty)
        self.assertEqual(self.model.snapshot.catalog, catalog)
        self.assertEqual(self.service.evaluated_definitions[-1].tuning.alignment.max_translation_pixels, 12.3)
        status = self.view.findChild(QLabel, 'calibrationSettingsResultStatus')
        self.assertEqual(status.text(), 'Head present')
        self.assertTrue(status.isVisible())
        canvas = self.view._canvases[SetupPage.SETTINGS]
        self.assertTrue(canvas.isVisible())
        self.assertFalse(canvas.findChild(QLabel, 'calibrationImageResult').isHidden())

    def test_settings_invalid_draft_shows_evaluation_error_and_recovers_live(self):
        self.service.evaluation_failure = CalibrationFailure(CalibrationFailureCode.INVALID_CALIBRATION, 'Search rotation step must be positive')
        self.open_settings_preview()
        status = self.view.findChild(QLabel, 'calibrationSettingsResultStatus')
        self.wait_for(lambda: status.text() == 'Evaluation unavailable')
        self.assertIsNotNone(self.model.current_frame)
        self.assertNotEqual(status.text(), 'Camera frame unavailable')
        self.service.evaluation_failure = None
        self.wait_for(lambda: status.text() == 'Head present')
        details = self.view.findChild(QLabel, 'calibrationSettingsResultDetails')
        self.assertIn('Translation', details.text())
        self.assertEqual(details.textFormat(), Qt.TextFormat.RichText)

    def test_settings_pause_and_test_tab_use_the_same_evaluation_mode(self):
        navigation, button = self.open_settings_preview()
        self.wait_for(lambda: bool(self.view.reports))
        button.click()
        self.assertFalse(self.model.snapshot.live)
        self.assertFalse(button.isChecked())
        navigation.setCurrentRow(3)
        self.assertFalse(self.view._live.isChecked())
        navigation.setCurrentRow(4)
        self.assertTrue(button.isChecked())
        self.assertTrue(self.model.snapshot.live)

    def test_save_signal_persists_draft_without_changing_runtime_or_revision(self):
        original = self.model.snapshot.catalog.profile(PROFILE_ID).revision(1)
        self.edit()
        self.assertTrue(self.model.snapshot.dirty)
        self.view.save_draft_requested.emit()
        self.wait_for(lambda: not self.model.snapshot.dirty)
        self.assertEqual(self.model.snapshot.catalog.profile(PROFILE_ID).revision(1), original)
        self.assertEqual(self.model.snapshot.catalog.selected, RevisionRef(PROFILE_ID, 1))

    def test_capture_requires_preview_confirmation_before_changing_the_draft(self):
        original = self.model.snapshot.definition
        self.view.accept_capture = False
        self.view.capture_requested.emit(ReferenceRole.PRESENT)
        self.wait_for(lambda: len(self.view.capture_previews) == 1)
        self.assertEqual(self.model.snapshot.definition, original)
        self.assertFalse(self.model.snapshot.dirty)
        self.view.accept_capture = True
        self.view.capture_requested.emit(ReferenceRole.PRESENT)
        self.wait_for(lambda: self.model.snapshot.dirty)
        self.assertEqual(len(self.view.capture_previews), 2)

    def test_save_error_keeps_dirty_edits_and_is_reported_as_typed_failure(self):
        self.edit()
        failure = CalibrationFailure(CalibrationFailureCode.STORAGE_SAVE_FAILED, "disk full")
        self.service.save_failure = failure
        self.view.save_draft_requested.emit()
        self.wait_for(lambda: bool(self.view.failures))
        self.assertEqual(self.view.failures[-1], failure)
        self.assertTrue(self.model.snapshot.dirty)

    def test_new_revision_is_not_automatically_selected_for_runtime(self):
        self.view.save_revision_requested.emit("Verified")
        self.wait_for(lambda: self.model.snapshot.base_revision == 2)
        self.assertEqual(self.model.snapshot.catalog.selected, RevisionRef(PROFILE_ID, 1))
        self.view.select_revision_requested.emit(RevisionRef(PROFILE_ID, 2))
        self.wait_for(lambda: self.model.snapshot.catalog.selected.number == 2)

    def test_selected_revision_deletion_is_blocked_even_if_signal_is_called_directly(self):
        self.view.delete_revision_requested.emit(RevisionRef(PROFILE_ID, 1))
        self.wait_for(lambda: bool(self.view.failures))
        self.assertEqual(self.view.failures[-1].code, CalibrationFailureCode.REVISION_SELECTED)

    def test_usage_display_updates_while_frozen_and_prevents_deletion(self):
        reference = RevisionRef(PROFILE_ID, 1)
        self.model.freeze(True)
        self.service.set_revision_in_use(reference, True)
        self.wait_for(lambda: reference in self.model.snapshot.in_use_revisions)
        self.wait_for(lambda: 'In use' in self.view._revision_table.item(0, 2).text())
        self.assertFalse(self.view._delete_revision.isEnabled())
        self.assertFalse(self.view._delete_profile.isEnabled())

    def test_single_frame_test_displays_and_freezes_the_evaluated_image(self):
        self.view.test_requested.emit()
        self.wait_for(lambda: bool(self.view.reports))
        self.assertTrue(self.model.snapshot.frozen)
        self.assertEqual(self.view.reports[-1].frame_sequence, self.view.frames[-1].sequence)

    def test_editing_revision_confirms_before_replacing_a_different_saved_draft(self):
        self.edit()
        self.view.save_draft_requested.emit()
        self.wait_for(lambda: not self.model.snapshot.dirty)
        saved = self.model.snapshot.definition
        self.view.edit_revision_requested.emit(RevisionRef(PROFILE_ID, 1))
        self.assertEqual(self.view.replace_prompts, 1)
        self.assertEqual(self.model.snapshot.definition, saved)
        self.view.replace_draft = True
        self.view.edit_revision_requested.emit(RevisionRef(PROFILE_ID, 1))
        self.wait_for(lambda: self.model.snapshot.definition != saved)

    def test_result_is_overlaid_and_camera_failure_replaces_it_until_recovery(self):
        from src.robot_systems.paint.applications.paint_head_detector_setup.editor_contracts import SetupPage
        self.view.test_requested.emit()
        self.wait_for(lambda: bool(self.view.reports))
        canvas = self.view._canvases[SetupPage.TEST]
        badge = canvas.findChild(QLabel, 'calibrationImageResult')
        self.assertFalse(badge.isHidden())
        self.view.set_preview_failure(CalibrationFailure(CalibrationFailureCode.FRAME_STALE, 'stale'))
        self.assertEqual(badge.text(), 'Camera frame unavailable')
        self.view.set_frame(self.view.frames[-1])
        self.assertTrue(badge.isHidden())
        self.assertEqual(self.view.findChild(QLabel, 'calibrationNotice').text(), '')

    def test_live_evaluation_ignores_late_results_after_an_edit(self):
        self.service.delay_evaluation = True
        self.open_settings_preview()
        self.wait_for(self.service.evaluation_entered.is_set)
        old_generation = self.model.snapshot.generation
        self.edit()
        self.view.live_requested.emit(False)
        self.service.evaluation_release.set()
        QTest.qWait(150)
        _APP.processEvents()
        self.assertGreater(self.model.snapshot.generation, old_generation)
        self.assertEqual(self.view.reports, [])

    def test_hide_releases_preview_and_show_restarts_it(self):
        starts = self.service.preview_starts
        self.view.hide()
        self.wait_for(lambda: self.service.preview_stops > 0)
        self.assertFalse(self.model.snapshot.live)
        self.view.show()
        self.wait_for(lambda: self.service.preview_starts > starts)
        count = len(self.view.frames)
        self.wait_for(lambda: len(self.view.frames) > count)

    def test_stop_prevents_late_worker_updates_to_the_view(self):
        self.service.delay_evaluation = True
        self.view.live_requested.emit(True)
        self.wait_for(self.service.evaluation_entered.is_set)
        Timer(.03, self.service.evaluation_release.set).start()
        self.controller.stop()
        count = len(self.view.reports)
        QTest.qWait(50)
        _APP.processEvents()
        self.assertEqual(len(self.view.reports), count)
        self.assertEqual(self.service.preview_stops, 1)

    def test_language_change_does_not_lose_dirty_edits(self):
        self.edit()
        before = self.model.snapshot.definition
        _APP.sendEvent(self.view, QEvent(QEvent.Type.LanguageChange))
        self.assertEqual(self.model.snapshot.definition, before)
        self.assertTrue(self.model.snapshot.dirty)


class CalibrationCanvasTests(TestCase):
    def test_drawn_regions_remain_in_original_pixels_after_zoom(self):
        canvas = CalibrationCanvas()
        self.addCleanup(canvas.close)
        canvas.resize(900, 650)
        canvas.set_image(sample_pixels())
        canvas.show()
        QTest.qWait(20)
        canvas.zoom_in()
        canvas.set_tool(EditorTool.INSPECTION)
        edits = []
        canvas.geometry_edited.connect(edits.append)
        start = canvas.mapFromScene(180, 100)
        finish = canvas.mapFromScene(400, 300)
        QTest.mousePress(canvas.viewport(), Qt.MouseButton.LeftButton, pos=start)
        QTest.mouseMove(canvas.viewport(), finish)
        QTest.mouseRelease(canvas.viewport(), Qt.MouseButton.LeftButton, pos=finish)
        self.assertEqual(len(edits), 1)
        self.assertLessEqual(abs(edits[0].region.x - 180), 2)
        self.assertLessEqual(abs(edits[0].region.y - 100), 2)
        self.assertLessEqual(abs(edits[0].region.width - 220), 2)
        self.assertLessEqual(abs(edits[0].region.height - 200), 2)
