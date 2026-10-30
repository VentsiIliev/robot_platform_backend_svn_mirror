"""Startup migration is one-time, lossless and isolated by robot-system storage."""

from dataclasses import replace
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase
from unittest.mock import patch

from src.engine.repositories.json.base_json_settings_repository import BaseJsonSettingsRepository
from src.engine.repositories.settings_service import SettingsService
from src.robot_systems.paint.component_ids import CameraRoleID, MovementGroupID, SettingsID
from src.robot_systems.paint.contracts.paint_head_calibration.errors import CalibrationPersistenceError
from src.robot_systems.paint.contracts.paint_head_calibration.models import CalibrationCatalog, InspectionBinding
from src.robot_systems.paint.paint_head_calibration.assets import FileReferenceAssetRepository
from src.robot_systems.paint.paint_head_calibration.detector_adapter import CalibrationDetectorAdapter
from src.robot_systems.paint.paint_head_calibration.initialization import initialize_factory_calibration
from src.robot_systems.paint.paint_head_calibration.repository import SettingsCalibrationCatalogRepository
from src.robot_systems.paint.paint_head_calibration.serializer import CalibrationCatalogSerializer


class CalibrationInitializationTests(TestCase):
    def setUp(self):
        self.temp = TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.binding = InspectionBinding(
            CameraRoleID.PRIMARY_VISION, MovementGroupID.VERTICAL_SHAFT_ALIGNMENT
        )
        self.assets = FileReferenceAssetRepository(self.root / "calibration/paint_head/references")
        self.adapter = CalibrationDetectorAdapter(self.assets)
        self.base = BaseJsonSettingsRepository(
            CalibrationCatalogSerializer(), str(self.root / "settings/paint/head_detector.json"), required=False,
        )
        self.settings = SettingsService({SettingsID.PAINT_HEAD_CALIBRATION: self.base})
        self.repository = SettingsCalibrationCatalogRepository(self.settings, self.root / "head_detector.transaction")

    def initialize(self):
        return initialize_factory_calibration(self.repository, self.assets, self.adapter, self.binding)

    def test_missing_catalog_is_imported_with_explicit_runtime_selection(self):
        catalog = self.initialize()
        self.assertEqual(len(catalog.profiles), 1)
        self.assertEqual(catalog.selected.profile_id, catalog.profiles[0].profile_id)
        self.assertEqual(catalog.selected.number, 1)
        profile = catalog.profiles[0]
        self.assertEqual(profile.name, "Imported factory calibration")
        self.assertEqual(profile.next_revision, 2)
        revision = profile.revision(1)
        self.assertEqual(revision.definition.binding, self.binding)
        preview = self.adapter.reference_preview(revision.definition.references.present)
        detector = self.adapter.create_detector(revision.definition)
        self.assertEqual((preview.size.width, preview.size.height),
                         (detector.reference_size.width, detector.reference_size.height))
        self.assertTrue(Path(self.base.file_path).is_file())
        self.assertEqual(self.repository.load(), catalog)

    def test_existing_catalog_is_never_reseeded_from_bundled_files(self):
        catalog = self.initialize()
        changed = replace(catalog, profiles=(replace(catalog.profiles[0], name="Station calibration"),))
        self.base.save(changed)
        with patch.object(self.adapter, "bundled_template", side_effect=AssertionError("must not read factory data")):
            self.assertEqual(self.initialize(), changed)

    def test_intentionally_empty_catalog_is_not_repopulated(self):
        empty = CalibrationCatalog(0, (), None)
        self.base.save(empty)
        with patch.object(self.adapter, "bundled_template", side_effect=AssertionError("must not import")):
            self.assertEqual(self.initialize(), empty)

    def test_corrupt_existing_catalog_is_preserved_and_fails_clearly(self):
        path = Path(self.base.file_path)
        path.parent.mkdir(parents=True)
        path.write_text("{broken")
        with self.assertRaises(CalibrationPersistenceError):
            self.initialize()
        self.assertEqual(path.read_text(), "{broken")

    def test_catalog_write_failure_cannot_publish_a_dangling_selection(self):
        with patch.object(self.base, "_write_file", side_effect=OSError("disk full")):
            with self.assertRaises(CalibrationPersistenceError):
                self.initialize()
        self.assertFalse(Path(self.base.file_path).exists())
        catalog = self.initialize()
        revision = catalog.profile(catalog.selected.profile_id).revision(catalog.selected.number)
        self.adapter.validate(revision.definition)
        self.assertEqual(len(catalog.profiles), 1)
