"""The MVC service uses robot-owned repositories and production's calibration library."""

import os
from dataclasses import replace
from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace
from unittest import TestCase
from unittest.mock import MagicMock, patch

from src.bootstrap.account_runtime import application_catalog
from src.engine.repositories.json.base_json_settings_repository import BaseJsonSettingsRepository
from src.engine.repositories.settings_service import SettingsService
from src.engine.system.system_manager import SystemManager
from src.robot_systems.paint.component_ids import SettingsID
from src.robot_systems.paint.contracts.paint_head_calibration.errors import CalibrationFailureCode, PaintHeadCalibrationError
from src.robot_systems.paint.contracts.paint_head_calibration.models import ImageFrame, ReferenceRole, Region, RevisionRef
from src.robot_systems.paint.applications.paint_head_detector_setup.model.paint_head_detector_setup_model import PaintHeadDetectorSetupModel
from src.robot_systems.paint.applications.paint_head_detector_setup.service.paint_head_detector_setup_application_service import PaintHeadDetectorSetupApplicationService
from src.robot_systems.paint.paint_head_calibration.composition import build_calibration_services
from src.robot_systems.paint.paint_head_calibration.detector_adapter import CalibrationEditorEvaluator
from src.robot_systems.paint.paint_head_calibration.serializer import CalibrationCatalogSerializer
from src.robot_systems.paint.paint_robot_system import PaintRobotSystem
from src.robot_systems.paint_auto_dry.paint_robot_system import AutomaticDryerPaintRobotSystem
from src.robot_systems.paint_tray_dry.paint_robot_system import TrayDryerPaintRobotSystem
from src.shared_contracts.events.process_events import ProcessState


class CalibrationApplicationIntegrationTests(TestCase):
    def setUp(self):
        self.temporary = TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.binding = PaintRobotSystem.head_detector_inspection_binding()
        self.repository = BaseJsonSettingsRepository(
            CalibrationCatalogSerializer(), str(self.root / 'settings/paint/head_detector.json'), required=False,
        )
        self.settings = SettingsService({SettingsID.PAINT_HEAD_CALIBRATION: self.repository})
        self.stopped = True
        self.manager = SystemManager(MagicMock())
        self.bundle = self.build_bundle()
        self.addCleanup(self.bundle.close)
        self.frames = MagicMock()
        self.service = self.build_service()
        self.model = PaintHeadDetectorSetupModel(self.service)
        self.addCleanup(self.model.end_session)

    def build_bundle(self):
        return build_calibration_services(
            self.settings, reference_root=self.root / 'calibration/paint_head/references',
            transaction_path=self.root / 'settings/paint/head_detector.transaction',
            binding=self.binding, selection_allowed=lambda: self.stopped,
            system_manager=self.manager,
        )

    def build_service(self):
        return PaintHeadDetectorSetupApplicationService(
            self.bundle.library, CalibrationEditorEvaluator(self.bundle.detector), self.frames, self.binding,
        )

    def test_composition_does_no_calibration_io_until_first_use_and_imports_only_once(self):
        self.assertFalse(self.root.joinpath('calibration').exists())
        self.assertFalse(Path(self.repository.file_path).exists())
        self.model.load()
        first = self.model.snapshot.catalog
        self.assertEqual(first.selected.number, 1)
        for asset in first.profiles[0].revision(1).definition.references.assets():
            self.assertTrue(self.root.joinpath('calibration/paint_head/references', asset.asset_id.value + '.png').is_file())
        second = self.build_bundle()
        self.addCleanup(second.close)
        self.assertEqual(second.library.load(), first)

    def test_capture_save_reopen_evaluate_and_select_use_the_same_system_library(self):
        unrelated = self.root / 'settings/unrelated.json'
        unrelated.parent.mkdir(parents=True)
        unrelated.write_bytes(b'{"preserve": "unchanged"}\n')
        self.model.load()
        identity = self.model.snapshot.profile_id
        first_selection = self.model.snapshot.catalog.selected
        original_revision = self.model.snapshot.catalog.profile(identity).revision(1)
        present = self.model.reference_preview(ReferenceRole.PRESENT)
        missing = self.model.reference_preview(ReferenceRole.MISSING)
        for index, (role, pixels) in enumerate(((ReferenceRole.PRESENT, present), (ReferenceRole.MISSING, missing)), 1):
            self.model.freeze(False)
            self.frames.latest.return_value = ImageFrame(pixels, index, float(index))
            frame = self.model.capture_snapshot()
            self.assertEqual(frame.image, pixels)
            self.model.confirm_reference(frame, role)
        definition = self.model.snapshot.definition
        region = definition.inspection_region
        self.model.update_definition(replace(definition, inspection_region=Region(region.x+1, region.y, region.width-1, region.height)))
        self.model.save_draft()
        reopened = PaintHeadDetectorSetupModel(self.build_service())
        self.addCleanup(reopened.end_session)
        reopened.load()
        self.assertEqual(reopened.snapshot.definition, self.model.snapshot.definition)
        self.assertEqual(reopened.reference_preview(ReferenceRole.PRESENT), present)
        self.assertEqual(reopened.reference_preview(ReferenceRole.MISSING), missing)
        reopened.start_preview()
        self.frames.latest.return_value = ImageFrame(present, 3, 3.0)
        result = reopened.evaluate_once()
        self.assertEqual(result.frame_sequence, 3)
        self.assertTrue(result.evidence)
        reopened.save_revision('Verified on station')
        self.assertEqual(reopened.snapshot.catalog.selected, first_selection)
        self.assertEqual(reopened.snapshot.catalog.profile(identity).revision(1), original_revision)
        chosen = RevisionRef(identity, 2)
        reopened.select_revision(chosen)
        lease = self.bundle.library.acquire_selected()
        self.addCleanup(lease.close)
        self.assertEqual(lease.reference, chosen)
        self.assertEqual(lease.definition, reopened.snapshot.definition)
        self.assertEqual(unrelated.read_bytes(), b'{"preserve": "unchanged"}\n')

    def test_active_process_cannot_change_selection_through_application_service(self):
        self.model.load()
        self.model.save_revision('New revision')
        chosen = self.model.snapshot.catalog.selected
        self.stopped = False
        with self.assertRaises(PaintHeadCalibrationError) as raised:
            self.model.select_revision(RevisionRef(chosen.profile_id, 2))
        self.assertEqual(raised.exception.failure.code, CalibrationFailureCode.PROCESS_ACTIVE)
        self.assertEqual(self.bundle.library.load().selected, chosen)


class CalibrationRegistrationTests(TestCase):
    def test_manufacturer_only_development_registration_and_storage_are_inherited_by_variants(self):
        roots = []
        with patch.dict(os.environ, {'ROBOT_PLATFORM_DATA_ROOT': '/tmp/paint-head-registration-test'}):
            for system in (PaintRobotSystem, TrayDryerPaintRobotSystem, AutomaticDryerPaintRobotSystem):
                with self.subTest(system=system.__name__):
                    specification = next(spec for spec in system.shell.applications if spec.name == 'PaintHeadDetectorSetup')
                    folder = next(item for item in system.shell.folders if item.folder_id == specification.folder_id)
                    self.assertEqual(folder.name, 'DEVELOPMENT')
                    policy = next(item for item in application_catalog(system) if item.app_id == specification.app_id)
                    self.assertEqual(policy.protected_roles, frozenset({'Manufacturer'}))
                    self.assertEqual(policy.denied_roles, frozenset({'Admin', 'Operator'}))
                    settings = next(spec for spec in system.settings_specs if spec.name == SettingsID.PAINT_HEAD_CALIBRATION)
                    self.assertEqual(settings.storage_key, 'paint/head_detector.json')
                    self.assertFalse(settings.required)
                    roots.append(system.storage_path('calibration', 'paint_head', 'references'))
        self.assertEqual(len(set(roots)), 3)

    def test_runtime_selection_guard_requires_stopped_and_finished_cleanup(self):
        system = PaintRobotSystem.__new__(PaintRobotSystem)
        for state in ProcessState:
            for stopping in (False, True):
                system._main_process = SimpleNamespace(state=state, is_stopping=stopping)
                self.assertEqual(system._head_calibration_selection_allowed(),
                                 state in (ProcessState.IDLE, ProcessState.STOPPED) and not stopping)


class CalibrationSelectionReservationTests(TestCase):
    def setUp(self):
        from src.robot_systems.paint.paint_head_calibration.selection import CalibrationSelectionReservation
        self.manager = SystemManager(MagicMock())
        self.reservation = CalibrationSelectionReservation(self.manager)

    def test_selection_reservation_excludes_start_and_overlapping_selection(self):
        from src.robot_systems.paint.component_ids import ProcessID
        with self.reservation.hold() as accepted:
            self.assertTrue(accepted)
            self.assertFalse(self.manager.acquire(ProcessID.MAIN_PROCESS))
            with self.reservation.hold() as overlapping:
                self.assertFalse(overlapping)
            self.assertTrue(self.manager.is_busy)
        self.assertFalse(self.manager.is_busy)
        self.assertTrue(self.manager.acquire(ProcessID.MAIN_PROCESS))
        self.manager.release(ProcessID.MAIN_PROCESS)

    def test_active_process_denies_selection_without_releasing_process_ownership(self):
        from src.robot_systems.paint.component_ids import ProcessID
        self.manager.acquire(ProcessID.MAIN_PROCESS)
        with self.reservation.hold() as accepted:
            self.assertFalse(accepted)
        self.assertEqual(self.manager.active_process_id, ProcessID.MAIN_PROCESS)

    def test_failed_publication_releases_selection_reservation(self):
        with self.assertRaises(OSError):
            with self.reservation.hold() as accepted:
                self.assertTrue(accepted)
                raise OSError('disk full')
        self.assertFalse(self.manager.is_busy)
