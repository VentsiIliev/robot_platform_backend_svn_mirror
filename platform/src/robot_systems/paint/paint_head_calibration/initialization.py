"""Explicit one-time import of the previously bundled station calibration."""

from dataclasses import replace
from datetime import UTC, datetime
from functools import partial

from src.robot_systems.paint.contracts.paint_head_calibration.interfaces import (
    IReferenceAssetRepository,
)
from src.robot_systems.paint.contracts.paint_head_calibration.models import (
    CalibrationCatalog,
    CalibrationDraft,
    CalibrationProfile,
    CalibrationRevision,
    InspectionBinding,
    ProfileId,
    References,
    RevisionRef,
)

from .detector_adapter import CalibrationDetectorAdapter, encode_reference
from .repository import SettingsCalibrationCatalogRepository


def initialize_factory_calibration(
    repository: SettingsCalibrationCatalogRepository,
    assets: IReferenceAssetRepository,
    adapter: CalibrationDetectorAdapter,
    binding: InspectionBinding,
) -> CalibrationCatalog:
    return repository.initialize_if_missing(partial(_import, assets, adapter, binding))


def _import(
    assets: IReferenceAssetRepository,
    adapter: CalibrationDetectorAdapter,
    binding: InspectionBinding,
) -> CalibrationCatalog:
    definition, present, missing = adapter.bundled_template(binding)
    present_asset = assets.put_png(encode_reference(present), present.size)
    missing_asset = assets.put_png(encode_reference(missing), missing.size)
    definition = replace(definition, references=References(present_asset, missing_asset))
    adapter.validate(definition)
    identity = ProfileId.new()
    now = datetime.now(UTC)
    description = "Imported once from the bundled paint-head detector calibration."
    profile = CalibrationProfile(
        identity,
        "Imported factory calibration",
        description,
        CalibrationDraft(definition, 1, now),
        (CalibrationRevision(1, definition, now, description),),
        2,
    )
    return CalibrationCatalog(1, (profile,), RevisionRef(identity, 1))
