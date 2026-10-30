"""Calibration persistence and lifecycle tests without Qt, cameras or robot hardware."""

from concurrent.futures import ThreadPoolExecutor
from dataclasses import asdict, replace
from datetime import UTC, datetime
from pathlib import Path
from struct import pack
from tempfile import TemporaryDirectory
from unittest import TestCase
from unittest.mock import patch
from zlib import compress, crc32

from src.engine.repositories.json.base_json_settings_repository import BaseJsonSettingsRepository
from src.engine.repositories.settings_service import SettingsService
from src.robot_systems.paint.component_ids import CameraRoleID, MovementGroupID, SettingsID
from src.robot_systems.paint.contracts.paint_head_calibration.errors import (
    CalibrationConflictError, CalibrationFailure, CalibrationFailureCode,
    CalibrationPersistenceError, CalibrationValidationError, PaintHeadCalibrationError,
)
from src.robot_systems.paint.contracts.paint_head_calibration.interfaces import ICalibrationDefinitionValidator
from src.robot_systems.paint.contracts.paint_head_calibration.models import (
    AssetId, CalibrationCatalog, CalibrationDefinition, ExcludedRegion, ImageSize,
    InspectionBinding, Landmark, LandmarkRole, LandmarkSupport, ObjectId, ProfileId,
    References, Region, RevisionRef,
)
from src.robot_systems.paint.contracts.paint_head_calibration.tuning import (
    AlignmentTuning, DetectorTuning, MatchingTuning, PreprocessingTuning,
)
from src.robot_systems.paint.paint_head_calibration.assets import FileReferenceAssetRepository
from src.robot_systems.paint.paint_head_calibration.library import PaintHeadCalibrationLibrary
from src.robot_systems.paint.paint_head_calibration.repository import SettingsCalibrationCatalogRepository
from src.robot_systems.paint.paint_head_calibration.serializer import CalibrationCatalogSerializer
from src.robot_systems.paint.paint_head_detection.configuration import ConfigurationRepository

_NOW = datetime(2026, 10, 30, tzinfo=UTC)


def png(value=80):
    def chunk(kind, payload):
        return pack(">I", len(payload)) + kind + payload + pack(">I", crc32(kind + payload))
    return (
        b"\x89PNG\r\n\x1a\n"
        + chunk(b"IHDR", pack(">IIBBBBB", 8, 8, 8, 2, 0, 0, 0))
        + chunk(b"IDAT", compress((b"\0" + bytes((value, value, value)) * 8) * 8))
        + chunk(b"IEND", b"")
    )


def definition(references=None):
    config = ConfigurationRepository().load()
    return CalibrationDefinition(
        InspectionBinding(CameraRoleID.PRIMARY_VISION, MovementGroupID.VERTICAL_SHAFT_ALIGNMENT),
        references or References(None, None), Region(0, 0, 8, 8), Region(0, 0, 8, 8),
        (ExcludedRegion(ObjectId.new(), "Excluded cable", Region(0, 0, 2, 2)),),
        (Landmark(ObjectId.new(), "Fastener", Region(3, 3, 2, 2), .72,
                  LandmarkRole.PRESENT, False, True, LandmarkSupport.CIRCLE, None),),
        DetectorTuning(
            MatchingTuning(**asdict(config.matching)),
            PreprocessingTuning(**asdict(config.preprocessing)),
            AlignmentTuning(**asdict(config.alignment)),
        ),
    )


class _Validator(ICalibrationDefinitionValidator):
    def __init__(self):
        self.calls = 0
        self.reject = False

    def validate(self, definition):
        self.calls += 1
        if self.reject:
            raise PaintHeadCalibrationError(CalibrationFailure(
                CalibrationFailureCode.INVALID_CALIBRATION, "References are incompatible"
            ))


class CalibrationStorageTests(TestCase):
    def setUp(self):
        self.temp = TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.serializer = CalibrationCatalogSerializer()
        self.base = BaseJsonSettingsRepository(
            self.serializer, str(self.root / "settings/head_detector.json"), required=False
        )
        self.settings = SettingsService({SettingsID.PAINT_HEAD_CALIBRATION: self.base})
        self.repository = SettingsCalibrationCatalogRepository(self.settings, self.root / "catalog-transaction")
        self.assets = FileReferenceAssetRepository(self.root / "calibration/references")
        self.validator = _Validator()
        self.idle = True
        self.library = PaintHeadCalibrationLibrary(
            self.repository, self.assets, self.validator,
            selection_allowed=self.selection_allowed, clock=self.clock,
        )

    def selection_allowed(self):
        return self.idle

    def clock(self):
        return _NOW

    def create(self, payload=None, name="Standard"):
        catalog = self.library.load()
        changed = self.library.create_profile(catalog.version, name, "", payload or definition())
        return changed.catalog, changed.catalog.profiles[-1].profile_id

    def publish(self, identity, payload=None):
        catalog = self.library.load()
        return self.library.save_revision(
            catalog.version, identity, payload or catalog.profile(identity).draft.definition, ""
        ).catalog

    def test_optional_missing_catalog_is_empty_without_writing_defaults(self):
        self.assertEqual(self.library.load(), CalibrationCatalog(0, (), None))
        self.assertFalse(Path(self.base.file_path).exists())

    def test_draft_round_trip_preserves_all_properties_and_can_be_incomplete(self):
        payload = replace(definition(), inspection_region=None)
        catalog, identity = self.create(payload)
        loaded = self.library.load()
        self.assertEqual(loaded, catalog)
        self.assertEqual(loaded.profile(identity).draft.definition, payload)
        self.assertEqual(self.validator.calls, 0)
        self.assertIsNone(loaded.selected)

    def test_revision_save_and_runtime_selection_are_separate(self):
        catalog, identity = self.create()
        catalog = self.publish(identity)
        self.assertEqual(len(catalog.profile(identity).revisions), 1)
        self.assertIsNone(catalog.selected)
        chosen = self.library.select_revision(catalog.version, RevisionRef(identity, 1)).catalog
        self.assertEqual(chosen.selected, RevisionRef(identity, 1))
        self.assertEqual(self.validator.calls, 2)

    def test_invalid_revision_does_not_replace_draft_or_selection(self):
        catalog, identity = self.create()
        self.validator.reject = True
        with self.assertRaises(PaintHeadCalibrationError):
            self.publish(identity)
        self.assertEqual(self.library.load(), catalog)

    def test_catalog_conflict_preserves_another_profile(self):
        first = self.library.load()
        catalog, _ = self.create(name="Other writer")
        with self.assertRaises(CalibrationConflictError):
            self.library.create_profile(first.version, "Stale editor", "", definition())
        self.assertEqual(self.library.load(), catalog)

    def test_two_repository_instances_cannot_both_commit_same_catalog_version(self):
        second = SettingsCalibrationCatalogRepository(
            SettingsService({SettingsID.PAINT_HEAD_CALIBRATION: self.base}),
            self.root / "catalog-transaction",
        )
        def update(repository):
            try:
                return repository.update(0, lambda catalog: catalog).version
            except CalibrationConflictError:
                return "conflict"
        with ThreadPoolExecutor(max_workers=2) as executor:
            results = list(executor.map(update, (self.repository, second)))
        self.assertCountEqual(results, [1, "conflict"])

    def test_failed_save_preserves_existing_catalog(self):
        catalog, identity = self.create()
        with patch.object(self.base, "_write_file", side_effect=OSError("disk full")):
            with self.assertRaises(CalibrationPersistenceError) as raised:
                self.library.discard_draft(catalog.version, identity)
        self.assertEqual(raised.exception.failure.code, CalibrationFailureCode.STORAGE_SAVE_FAILED)
        self.assertFalse(raised.exception.failure.published)
        self.assertEqual(self.library.load(), catalog)

    def test_corrupt_catalog_is_not_overwritten_with_defaults(self):
        destination = Path(self.base.file_path)
        destination.parent.mkdir(parents=True)
        destination.write_text('{"schema_version":999}')
        before = destination.read_bytes()
        with self.assertRaises(CalibrationPersistenceError):
            self.library.load()
        self.assertEqual(destination.read_bytes(), before)

    def test_invalid_json_scalar_and_unknown_fields_are_rejected(self):
        base = self.serializer.to_dict(CalibrationCatalog(0, (), None))
        for changed in ({**base, "version": True}, {**base, "extra": 1}, {**base, "schema_version": 99}):
            with self.subTest(changed=changed):
                with self.assertRaises(CalibrationValidationError):
                    self.serializer.from_dict(changed)

    def test_revisions_are_not_renumbered_or_reused_after_deletion(self):
        catalog, identity = self.create()
        catalog = self.publish(identity)
        catalog = self.publish(identity)
        catalog = self.library.delete_revision(catalog.version, RevisionRef(identity, 2)).catalog
        catalog = self.publish(identity)
        self.assertEqual([r.number for r in catalog.profile(identity).revisions], [1, 3])
        self.assertEqual(catalog.profile(identity).next_revision, 4)

    def test_selected_revision_and_profile_cannot_be_deleted(self):
        catalog, identity = self.create()
        catalog = self.publish(identity)
        catalog = self.library.select_revision(catalog.version, RevisionRef(identity, 1)).catalog
        for operation in (
            lambda: self.library.delete_revision(catalog.version, RevisionRef(identity, 1)),
            lambda: self.library.delete_profile(catalog.version, identity),
        ):
            with self.assertRaises(PaintHeadCalibrationError) as raised:
                operation()
            self.assertEqual(raised.exception.failure.code, CalibrationFailureCode.REVISION_SELECTED)
        self.assertEqual(self.library.load(), catalog)

    def test_selection_guard_is_enforced_below_the_ui(self):
        catalog, identity = self.create()
        catalog = self.publish(identity)
        self.idle = False
        with self.assertRaises(PaintHeadCalibrationError) as raised:
            self.library.select_revision(catalog.version, RevisionRef(identity, 1))
        self.assertEqual(raised.exception.failure.code, CalibrationFailureCode.PROCESS_ACTIVE)
        self.assertIsNone(self.library.load().selected)

    def test_in_use_revision_cannot_be_deleted_and_release_is_idempotent(self):
        catalog, identity = self.create()
        catalog = self.publish(identity)
        lease = self.library.acquire_revision(RevisionRef(identity, 1))
        with self.assertRaises(PaintHeadCalibrationError) as raised:
            self.library.delete_revision(catalog.version, RevisionRef(identity, 1))
        self.assertEqual(raised.exception.failure.code, CalibrationFailureCode.REVISION_IN_USE)
        lease.close()
        lease.close()
        catalog = self.library.delete_revision(catalog.version, RevisionRef(identity, 1)).catalog
        self.assertEqual(catalog.profile(identity).revisions, ())

    def test_selection_missing_has_a_typed_failure(self):
        with self.assertRaises(PaintHeadCalibrationError) as raised:
            self.library.acquire_selected()
        self.assertEqual(raised.exception.failure.code, CalibrationFailureCode.SELECTION_MISSING)

    def test_shared_assets_survive_until_last_draft_and_revision_release(self):
        asset = self.assets.put_png(png(), ImageSize(8, 8))
        payload = definition(References(asset, asset))
        catalog, identity = self.create(payload)
        catalog = self.publish(identity)
        catalog, other = self.create(payload, name="Other profile")
        catalog = self.library.delete_profile(catalog.version, identity).catalog
        self.assertEqual(self.assets.read_png(asset), png())
        self.library.delete_profile(catalog.version, other)
        with self.assertRaises(CalibrationPersistenceError) as raised:
            self.assets.read_png(asset)
        self.assertEqual(raised.exception.failure.code, CalibrationFailureCode.ASSET_NOT_FOUND)

    def test_editor_pin_defers_asset_cleanup_and_closing_lease_does_no_io(self):
        asset = self.assets.put_png(png(), ImageSize(8, 8))
        payload = definition(References(asset, None))
        catalog, identity = self.create(payload)
        lease = self.library.pin_definition(payload)
        self.library.delete_profile(catalog.version, identity)
        self.assertEqual(self.assets.read_png(asset), png())
        with patch.object(self.assets, "delete") as delete:
            lease.close()
            delete.assert_not_called()
        self.assertEqual(self.library.cleanup_pending_assets(), ())
        with self.assertRaises(CalibrationPersistenceError):
            self.assets.read_png(asset)

    def test_cleanup_failure_is_a_warning_after_catalog_publication(self):
        asset = self.assets.put_png(png(), ImageSize(8, 8))
        catalog, identity = self.create(definition(References(asset, None)))
        error = CalibrationPersistenceError(CalibrationFailure(
            CalibrationFailureCode.ASSET_CLEANUP_FAILED, "read-only directory", True
        ))
        with patch.object(self.assets, "delete", side_effect=error):
            changed = self.library.delete_profile(catalog.version, identity)
        self.assertEqual(changed.catalog.profiles, ())
        self.assertEqual(changed.warnings, (error.failure,))
        self.assertEqual(self.assets.read_png(asset), png())
        self.assertEqual(self.library.cleanup_pending_assets(), ())

    def test_edit_revision_copies_content_without_changing_the_revision(self):
        catalog, identity = self.create()
        catalog = self.publish(identity)
        revision = catalog.profile(identity).revision(1)
        catalog = self.library.edit_revision(catalog.version, RevisionRef(identity, 1)).catalog
        changed = replace(catalog.profile(identity).draft.definition, inspection_region=None)
        catalog = self.library.save_draft(catalog.version, identity, changed, 1).catalog
        self.assertEqual(catalog.profile(identity).revision(1), revision)
        self.assertIsNone(catalog.profile(identity).draft.definition.inspection_region)

    def test_asset_content_is_addressed_once_and_verified_on_read(self):
        first = self.assets.put_png(png(), ImageSize(8, 8))
        second = self.assets.put_png(png(), ImageSize(8, 8))
        self.assertEqual(first, second)
        self.assertEqual(len(list((self.root / "calibration/references").glob("*.png"))), 1)
        path = self.root / "calibration/references" / (first.asset_id.value + ".png")
        path.write_bytes(png(90))
        with self.assertRaises(PaintHeadCalibrationError) as raised:
            self.assets.read_png(first)
        self.assertEqual(raised.exception.failure.code, CalibrationFailureCode.ASSET_INVALID)

    def test_reference_dimensions_and_identities_cannot_escape_storage(self):
        with self.assertRaises(PaintHeadCalibrationError):
            self.assets.put_png(png(), ImageSize(16, 8))
        for identity in ("../../settings", "A" * 64, "0" * 63):
            with self.subTest(identity=identity):
                with self.assertRaises(CalibrationValidationError):
                    AssetId(identity)
        with self.assertRaises(CalibrationValidationError):
            ProfileId("../profile")
