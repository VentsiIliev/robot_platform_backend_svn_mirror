"""System-level construction; mutable roots come from the concrete robot system."""

import logging
from collections.abc import Callable
from dataclasses import dataclass
from functools import partial
from pathlib import Path

from src.engine.repositories.interfaces.i_settings_service import ISettingsService
from src.engine.system.i_system_manager import ISystemManager
from src.robot_systems.paint.contracts.paint_head_calibration.models import InspectionBinding

from .assets import FileReferenceAssetRepository
from .detector_adapter import CalibrationDetectorAdapter
from .initialization import initialize_factory_calibration
from .library import PaintHeadCalibrationLibrary
from .repository import SettingsCalibrationCatalogRepository
from .selection import CalibrationSelectionReservation

_LOG = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True)
class CalibrationServices:
    library: PaintHeadCalibrationLibrary
    detector: CalibrationDetectorAdapter

    def close(self) -> None:
        for warning in self.library.cleanup_pending_assets():
            _LOG.warning("Reference-image cleanup: %s", warning.detail)


def build_calibration_services(
    settings: ISettingsService,
    *,
    reference_root: Path,
    transaction_path: Path,
    binding: InspectionBinding,
    selection_allowed: Callable[[], bool],
    system_manager: ISystemManager,
) -> CalibrationServices:
    assets = FileReferenceAssetRepository(reference_root)
    detector = CalibrationDetectorAdapter(assets)
    repository = SettingsCalibrationCatalogRepository(settings, transaction_path)
    library = PaintHeadCalibrationLibrary(
        repository,
        assets,
        detector,
        selection_allowed=selection_allowed,
        selection_reservation=CalibrationSelectionReservation(system_manager).hold,
        initialize=partial(initialize_factory_calibration, repository, assets, detector, binding),
    )
    return CalibrationServices(library, detector)
