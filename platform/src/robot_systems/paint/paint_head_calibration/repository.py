"""Calibration mutations through the existing settings service and JSON repository."""

from collections.abc import Callable
from dataclasses import replace
from pathlib import Path

from src.engine.core.durable_files import DurabilityError, store_lock
from src.engine.repositories.interfaces.i_settings_service import ISettingsService
from src.engine.repositories.interfaces.settings_repository import (
    SettingsLoadError,
    SettingsSaveError,
)
from src.robot_systems.paint.component_ids import SettingsID
from src.robot_systems.paint.contracts.paint_head_calibration.errors import (
    CalibrationConflictError,
    CalibrationFailure,
    CalibrationFailureCode,
    CalibrationPersistenceError,
)
from src.robot_systems.paint.contracts.paint_head_calibration.interfaces import (
    ICalibrationCatalogRepository,
)
from src.robot_systems.paint.contracts.paint_head_calibration.models import CalibrationCatalog


class SettingsCalibrationCatalogRepository(ICalibrationCatalogRepository):
    def __init__(self, settings: ISettingsService, transaction_path: Path) -> None:
        self._settings = settings
        # Separate from BaseJsonSettingsRepository's file lock: nested acquisition
        # of that same flock would deadlock. This lock covers reload + mutation + save.
        self._transaction_path = transaction_path

    def load(self) -> CalibrationCatalog:
        try:
            value = self._settings.reload(SettingsID.PAINT_HEAD_CALIBRATION)
        except (SettingsLoadError, OSError, KeyError) as error:
            raise CalibrationPersistenceError(
                CalibrationFailure(CalibrationFailureCode.STORAGE_LOAD_FAILED, str(error))
            ) from error
        if not isinstance(value, CalibrationCatalog):
            raise CalibrationPersistenceError(
                CalibrationFailure(
                    CalibrationFailureCode.STORAGE_LOAD_FAILED, "Invalid calibration catalog type"
                )
            )
        return value

    def initialize_if_missing(
        self, factory: Callable[[], CalibrationCatalog]
    ) -> CalibrationCatalog:
        """One startup migration; existing, empty or corrupt files are never overwritten."""
        try:
            with store_lock(self._transaction_path):
                if self._settings.get_repo(SettingsID.PAINT_HEAD_CALIBRATION).exists():
                    return self.load()
                catalog = factory()
                self._settings.save(SettingsID.PAINT_HEAD_CALIBRATION, catalog)
                return catalog
        except SettingsSaveError as error:
            raise CalibrationPersistenceError(
                CalibrationFailure(
                    CalibrationFailureCode.STORAGE_SAVE_FAILED,
                    str(error),
                    published=isinstance(error.__cause__, DurabilityError),
                )
            ) from error
        except OSError as error:
            raise CalibrationPersistenceError(
                CalibrationFailure(CalibrationFailureCode.STORAGE_SAVE_FAILED, str(error))
            ) from error

    def update(
        self,
        expected_version: int,
        mutation: Callable[[CalibrationCatalog], CalibrationCatalog],
    ) -> CalibrationCatalog:
        try:
            with store_lock(self._transaction_path):
                current = self.load()
                if current.version != expected_version:
                    raise CalibrationConflictError(
                        "Calibration changed since it was loaded; reload before saving"
                    )
                updated = replace(mutation(current), version=current.version + 1)
                self._settings.save(SettingsID.PAINT_HEAD_CALIBRATION, updated)
                return updated
        except SettingsSaveError as error:
            raise CalibrationPersistenceError(
                CalibrationFailure(
                    CalibrationFailureCode.STORAGE_SAVE_FAILED,
                    str(error),
                    published=isinstance(error.__cause__, DurabilityError),
                )
            ) from error
        except OSError as error:
            raise CalibrationPersistenceError(
                CalibrationFailure(CalibrationFailureCode.STORAGE_SAVE_FAILED, str(error))
            ) from error
