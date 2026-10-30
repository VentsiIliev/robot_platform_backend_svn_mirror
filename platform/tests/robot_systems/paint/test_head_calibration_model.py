"""MVC model tests through the standalone in-memory service."""

from dataclasses import replace
from unittest import TestCase

from src.robot_systems.paint.applications.paint_head_detector_setup.model.paint_head_detector_setup_model import (
    PaintHeadDetectorSetupModel,
)
from src.robot_systems.paint.applications.paint_head_detector_setup.service.stub_data import PROFILE_ID
from src.robot_systems.paint.applications.paint_head_detector_setup.service.stub_paint_head_detector_setup_service import (
    StubPaintHeadDetectorSetupService,
)
from src.robot_systems.paint.contracts.paint_head_calibration.errors import (
    CalibrationFailure, CalibrationFailureCode, PaintHeadCalibrationError,
)
from src.robot_systems.paint.contracts.paint_head_calibration.models import ReferenceRole, Region, RevisionRef
from src.robot_systems.paint.contracts.paint_head_check.models import PaintHeadState


class CalibrationModelTests(TestCase):
    def setUp(self):
        self.service = StubPaintHeadDetectorSetupService()
        self.model = PaintHeadDetectorSetupModel(self.service)
        self.model.load()

    def change_region(self):
        current = self.model.snapshot.definition
        self.model.update_definition(replace(current, inspection_region=Region(150, 50, 340, 380)))

    def test_load_restores_saved_draft_and_selected_runtime_revision(self):
        snapshot = self.model.snapshot
        self.assertEqual(snapshot.profile_id, PROFILE_ID)
        self.assertEqual(snapshot.base_revision, 1)
        self.assertEqual(snapshot.catalog.selected, RevisionRef(PROFILE_ID, 1))
        self.assertFalse(snapshot.dirty)

    def test_save_draft_does_not_modify_a_saved_revision_or_runtime(self):
        old = self.model.snapshot.catalog.profile(PROFILE_ID).revision(1)
        self.change_region()
        self.assertTrue(self.model.snapshot.dirty)
        self.model.save_draft()
        snapshot = self.model.snapshot
        self.assertFalse(snapshot.dirty)
        self.assertEqual(snapshot.catalog.profile(PROFILE_ID).revision(1), old)
        self.assertEqual(snapshot.catalog.selected, RevisionRef(PROFILE_ID, 1))

    def test_save_calibration_and_runtime_selection_are_distinct_operations(self):
        self.change_region()
        self.model.save_revision("New calibration")
        self.assertEqual(self.model.snapshot.base_revision, 2)
        self.assertEqual(self.model.snapshot.catalog.selected.number, 1)
        self.model.select_revision(RevisionRef(PROFILE_ID, 2))
        self.assertEqual(self.model.snapshot.catalog.selected.number, 2)

    def test_failed_save_keeps_the_working_draft_and_loaded_catalog(self):
        self.change_region()
        before = self.model.snapshot
        failure = CalibrationFailure(CalibrationFailureCode.STORAGE_SAVE_FAILED, "disk full")
        self.service.fail_next(failure)
        with self.assertRaises(PaintHeadCalibrationError) as raised:
            self.model.save_draft()
        after = self.model.snapshot
        self.assertEqual(raised.exception.failure, failure)
        self.assertEqual(after.definition, before.definition)
        self.assertEqual(after.catalog, before.catalog)
        self.assertTrue(after.dirty)

    def test_incomplete_draft_can_be_saved_but_not_published(self):
        self.model.update_definition(replace(self.model.snapshot.definition, inspection_region=None))
        self.model.save_draft()
        with self.assertRaises(PaintHeadCalibrationError) as raised:
            self.model.save_revision()
        self.assertEqual(raised.exception.failure.code, CalibrationFailureCode.INVALID_CALIBRATION)
        self.assertIsNone(self.model.snapshot.definition.inspection_region)
        self.assertEqual(len(self.model.snapshot.catalog.profile(PROFILE_ID).revisions), 1)

    def test_unsaved_changes_cannot_be_silently_lost_on_profile_switch(self):
        self.change_region()
        with self.assertRaises(PaintHeadCalibrationError):
            self.model.select_profile(PROFILE_ID)
        self.assertTrue(self.model.snapshot.dirty)
        self.model.discard_local_changes()
        self.model.select_profile(PROFILE_ID)
        self.assertFalse(self.model.snapshot.dirty)

    def test_new_profile_is_a_persisted_incomplete_draft(self):
        self.model.create_profile("New head")
        snapshot = self.model.snapshot
        self.assertEqual(snapshot.catalog.profile(snapshot.profile_id).name, "New head")
        self.assertIsNone(snapshot.definition.references.present)
        self.assertIsNone(snapshot.base_revision)
        self.assertFalse(snapshot.dirty)
        self.assertEqual(snapshot.catalog.selected, RevisionRef(PROFILE_ID, 1))

    def test_import_is_explicit_and_does_not_change_runtime_selection(self):
        self.model.import_factory_profile("Factory import")
        profile = self.model.snapshot.catalog.profile(self.model.snapshot.profile_id)
        self.assertEqual(len(profile.revisions), 1)
        self.assertEqual(self.model.snapshot.catalog.selected, RevisionRef(PROFILE_ID, 1))

    def test_selected_revision_deletion_is_rejected_through_the_service(self):
        before = self.model.snapshot
        with self.assertRaises(PaintHeadCalibrationError) as raised:
            self.model.delete_revision(RevisionRef(PROFILE_ID, 1))
        self.assertEqual(raised.exception.failure.code, CalibrationFailureCode.REVISION_SELECTED)
        self.assertEqual(self.model.snapshot, before)

    def test_capturing_reference_changes_only_the_working_draft(self):
        self.model.start_preview()
        frame = self.model.capture_snapshot()
        original = self.model.snapshot
        self.model.confirm_reference(frame, ReferenceRole.PRESENT)
        snapshot = self.model.snapshot
        self.assertTrue(snapshot.dirty)
        self.assertEqual(snapshot.catalog, original.catalog)
        self.assertNotEqual(snapshot.definition.references.present, original.definition.references.present)

    def test_frozen_capture_is_not_overwritten_by_preview_polls(self):
        self.model.start_preview()
        self.model.poll_preview()
        frame = self.model.capture_snapshot()
        self.assertTrue(self.model.snapshot.frozen)
        self.assertIsNone(self.model.poll_preview().frame)
        self.assertEqual(self.model.evaluate_once().frame_sequence, frame.sequence)

    def test_live_and_single_frame_evaluation_use_different_confirmation_generations(self):
        self.model.start_preview()
        self.model.set_live(True)
        first = self.model.poll_preview()
        second = self.model.poll_preview()
        self.assertEqual(first.evaluation.generation, second.evaluation.generation)
        self.assertGreater(second.frame.sequence, first.frame.sequence)
        once = self.model.evaluate_once()
        self.assertGreater(once.generation, second.evaluation.generation)
        self.assertFalse(self.model.snapshot.live)

    def test_editing_invalidates_the_previous_evaluation_generation(self):
        self.model.start_preview()
        self.model.set_live(True)
        before = self.model.poll_preview()
        self.change_region()
        self.assertGreater(self.model.snapshot.generation, before.generation)

    def test_missing_has_no_fabricated_alignment_measurements(self):
        self.model.start_preview()
        self.service.set_detected_state(PaintHeadState.MISSING)
        result = self.model.evaluate_once()
        self.assertEqual(result.state, PaintHeadState.MISSING)
        self.assertIsNone(result.translation_pixels)
        self.assertIsNone(result.rotation_degrees)

    def test_camera_failure_is_preserved_as_typed_preview_feedback(self):
        self.model.start_preview()
        failure = CalibrationFailure(CalibrationFailureCode.FRAME_STALE, "stale capture")
        self.service.fail_next(failure)
        result = self.model.poll_preview()
        self.assertIsNone(result.frame)
        self.assertEqual(result.failure, failure)

    def test_stop_releases_preview_and_invalidates_late_result_generation(self):
        self.model.start_preview()
        self.model.set_live(True)
        generation = self.model.snapshot.generation
        self.model.end_session()
        self.assertEqual(self.service.preview_starts, 1)
        self.assertEqual(self.service.preview_stops, 1)
        self.assertFalse(self.model.snapshot.live)
        self.assertGreater(self.model.snapshot.generation, generation)

    def test_runtime_selection_keeps_unrelated_unsaved_edits(self):
        self.model.save_revision()
        self.change_region()
        before = self.model.snapshot.definition
        self.model.select_revision(RevisionRef(PROFILE_ID, 2))
        self.assertEqual(self.model.snapshot.definition, before)
        self.assertTrue(self.model.snapshot.dirty)

    def test_deleting_displayed_revision_without_a_persisted_draft_reopens_remaining_revision(self):
        self.model.save_revision("Second")
        second = RevisionRef(PROFILE_ID, 2)
        self.model.discard_saved_draft()
        self.assertEqual(self.model.snapshot.base_revision, 2)
        self.model.delete_revision(second)
        self.assertEqual(self.model.snapshot.base_revision, 1)
        self.assertEqual(self.model.snapshot.definition, self.model.snapshot.catalog.profile(PROFILE_ID).revision(1).definition)

    def test_deleting_source_revision_with_unsaved_edits_requires_draft_resolution(self):
        self.model.save_revision("Second")
        self.model.discard_saved_draft()
        self.change_region()
        before = self.model.snapshot
        with self.assertRaises(PaintHeadCalibrationError) as raised:
            self.model.delete_revision(RevisionRef(PROFILE_ID, 2))
        self.assertEqual(raised.exception.failure.code, CalibrationFailureCode.CONFLICT)
        self.assertEqual(self.model.snapshot, before)
