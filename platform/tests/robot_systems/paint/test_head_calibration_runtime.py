"""One selected revision per run, including independently owned stopped guidance."""

import logging
from dataclasses import replace
from threading import Event, Thread
from unittest import TestCase
from unittest.mock import MagicMock, patch

from src.robot_systems.paint.applications.paint_head_detector_setup.service.stub_data import sample_definition
from src.robot_systems.paint.contracts.paint_head_calibration.errors import (
    CalibrationFailureCode, PaintHeadCalibrationError,
)
from src.robot_systems.paint.contracts.paint_head_calibration.models import CalibrationCatalog, RevisionRef
from src.robot_systems.paint.contracts.paint_head_check.errors import PaintHeadCalibrationError as HeadCalibrationError
from src.robot_systems.paint.contracts.paint_head_check.models import HeadCheckOperatingMode, PaintHeadState
from src.robot_systems.paint.contracts.paint_head_check.results import HeadCheckSkipped, HeadCheckStopped, ObservationReceived
from src.robot_systems.paint.paint_head_calibration.library import PaintHeadCalibrationLibrary
from src.robot_systems.paint.paint_head_calibration.runtime import CalibratedHeadCheckRunFactory
from src.robot_systems.paint.paint_head_check.configuration import default_head_check_configuration
from src.robot_systems.paint.paint_head_check.live_guidance import PaintHeadLiveGuidance
from tests.robot_systems.paint.test_head_check_live_guidance import LiveInspector, LiveObserver, observation
from tests.robot_systems.paint.test_head_check_run import FakeControl, FakeInspector, FakeMotion, FakeTargetProvider, RecordingObserver


class _Repository:
    def __init__(self):
        self.catalog = CalibrationCatalog(0, (), None)
        self.before_update = None

    def load(self):
        return self.catalog

    def update(self, version, mutation):
        if self.before_update is not None:
            self.before_update()
        assert version == self.catalog.version
        self.catalog = replace(mutation(self.catalog), version=version + 1)
        return self.catalog


class _MisalignedInspector(FakeInspector):
    def next_observation(self, window, control):
        return ObservationReceived(replace(
            observation(PaintHeadState.MISALIGNED),
            frame_captured_at=window.started_at,
            frame_received_at=window.started_at,
            evaluated_at=window.started_at,
        ))


class CalibrationRuntimeTests(TestCase):
    def setUp(self):
        self.repository = _Repository()
        self.validator = MagicMock()
        self.library = PaintHeadCalibrationLibrary(
            self.repository, MagicMock(), self.validator, selection_allowed=lambda: True,
        )
        changed = self.library.create_profile(0, 'Test', '', sample_definition())
        self.identity = changed.catalog.profiles[0].profile_id
        self.one = RevisionRef(self.identity, 1)
        self.two = RevisionRef(self.identity, 2)
        self.library.save_revision(1, self.identity, sample_definition(), '')
        changed_definition = replace(sample_definition(), inspection_region=None)
        self.library.save_revision(2, self.identity, changed_definition, '')
        self.select(self.one)
        self.definitions = []
        self.inspectors = []
        self.inspector_type = FakeInspector
        self.guidance = None
        self.configuration = replace(default_head_check_configuration(), enabled=True)

    def select(self, reference):
        self.library.select_revision(self.repository.catalog.version, reference)

    def inspector(self, definition):
        self.definitions.append(definition)
        inspector = self.inspector_type()
        self.inspectors.append(inspector)
        return inspector

    def factory(self):
        return CalibratedHeadCheckRunFactory(
            self.library, self.inspector, FakeTargetProvider(), FakeMotion(),
            RecordingObserver(), guidance=self.guidance,
        )

    def new_run(self, configuration=None, mode=HeadCheckOperatingMode.PRODUCTION):
        return self.factory().create_run(configuration or self.configuration, mode)

    def live_guidance(self):
        guard = MagicMock()
        guard.check.return_value = None
        self.guidance = PaintHeadLiveGuidance(
            None, guard, LiveObserver(), lambda: True, logger=logging.getLogger(__name__),
        )
        self.addCleanup(self.guidance.close)

    def test_run_keeps_original_revision_and_next_start_uses_new_selection(self):
        first = self.new_run()
        self.addCleanup(first.close)
        self.select(self.two)
        second = self.new_run()
        self.addCleanup(second.close)
        self.assertEqual(self.definitions[0], sample_definition())
        self.assertIsNone(self.definitions[1].inspection_region)
        self.assertEqual(set(self.library.in_use_revisions()), {self.one, self.two})
        first.close()
        first.close()
        self.assertEqual(self.library.in_use_revisions(), (self.two,))
        self.assertEqual(self.inspectors[0].end_count, 1)

    def test_disabled_and_pickup_only_do_not_load_calibration_or_inspector(self):
        with patch.object(self.library, 'acquire_selected', side_effect=AssertionError('No calibration I/O')):
            for config, mode in (
                (default_head_check_configuration(), HeadCheckOperatingMode.PRODUCTION),
                (self.configuration, HeadCheckOperatingMode.PICKUP_ONLY),
            ):
                run = self.new_run(config, mode)
                self.assertIsInstance(run.check_before_cycle(FakeControl()), HeadCheckSkipped)
                run.close()
        self.assertEqual(self.definitions, [])

    def test_missing_selection_becomes_typed_runtime_configuration_failure(self):
        self.repository.catalog = replace(self.repository.catalog, selected=None)
        with self.assertRaises(HeadCalibrationError):
            self.new_run()
        self.assertEqual(self.library.in_use_revisions(), ())

    def test_inspector_preparation_failure_releases_revision(self):
        factory = self.factory()
        with patch.object(factory, '_inspector_factory', side_effect=RuntimeError('decoder failed')):
            with self.assertRaisesRegex(RuntimeError, 'decoder failed'):
                factory.create_run(self.configuration, HeadCheckOperatingMode.PRODUCTION)
        self.assertEqual(self.library.in_use_revisions(), ())

    def offer_guidance(self):
        self.live_guidance()
        self.inspector_type = _MisalignedInspector
        run = self.new_run()
        self.addCleanup(run.close)
        self.assertIsInstance(run.check_before_cycle(FakeControl()), HeadCheckStopped)
        run.close()
        self.select(self.two)
        return run

    def test_pending_guidance_protects_original_revision_after_run_closes(self):
        self.offer_guidance()
        self.assertEqual(self.library.in_use_revisions(), (self.one,))
        with self.assertRaises(PaintHeadCalibrationError) as raised:
            self.library.delete_revision(self.repository.catalog.version, self.one)
        self.assertEqual(raised.exception.failure.code, CalibrationFailureCode.REVISION_IN_USE)
        self.guidance.cancel()
        self.assertEqual(self.library.in_use_revisions(), ())
        self.library.delete_revision(self.repository.catalog.version, self.one)

    def test_active_guidance_keeps_its_snapshot_until_worker_exits(self):
        self.offer_guidance()
        live = LiveInspector()
        # The offer captured the bound method, so replace the factory used by that method.
        self.inspector_type = lambda: live
        self.guidance.start_pending()
        self.assertTrue(live.started.wait(1))
        self.assertEqual(self.definitions[-1], sample_definition())
        self.assertEqual(self.library.in_use_revisions(), (self.one,))
        self.guidance.close()
        self.assertTrue(live.ended.is_set())
        self.assertEqual(self.library.in_use_revisions(), ())

    def test_failed_or_closed_guidance_releases_transferred_ownership(self):
        self.offer_guidance()
        entered = Event()
        def fail():
            entered.set()
            raise RuntimeError('reference decoder failed')
        self.inspector_type = fail
        with self.assertLogs(__name__, level='ERROR'):
            self.guidance.start_pending()
            self.assertTrue(entered.wait(1))
            self.guidance.close()
        self.assertEqual(self.library.in_use_revisions(), ())
        release = MagicMock()
        self.guidance.offer_with_inspector(FakeTargetProvider().resolve(), 1, FakeInspector,
                                          on_finished=release)
        release.assert_called_once_with()
        self.assertEqual(self.library.in_use_revisions(), ())

    def test_clone_and_close_do_not_wait_for_repository_io_and_closed_lease_cannot_clone(self):
        lease = self.library.acquire_selected()
        entered, release = Event(), Event()
        def block():
            entered.set()
            if not release.wait(2):
                raise AssertionError('Test did not release storage')
        self.repository.before_update = block
        writer = Thread(target=self.library.save_draft, args=(
            self.repository.catalog.version, self.identity, sample_definition(), 1,
        ))
        writer.start()
        self.addCleanup(writer.join, 3)
        self.addCleanup(release.set)
        self.assertTrue(entered.wait(1))
        done = Event()
        def close():
            clone = lease.clone()
            lease.close()
            clone.close()
            done.set()
        closer = Thread(target=close)
        closer.start()
        self.assertTrue(done.wait(.5), 'Lease lifecycle waited for disk I/O')
        closer.join(1)
        self.assertEqual(self.library.in_use_revisions(), ())
        with self.assertRaises(PaintHeadCalibrationError):
            lease.clone()
        release.set()
        writer.join(1)
