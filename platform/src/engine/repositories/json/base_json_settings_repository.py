import logging
import os
from pathlib import Path
from typing import Optional, TypeVar, Generic

from src.engine.core.durable_files import atomic_write_json, store_lock
from .json_store import JsonStoreError, LoadResult, StoreStatus, read_json_object
from ..interfaces.settings_repository import ISettingsRepository, SettingsLoadError, SettingsSaveError
from ..interfaces.settings_serializer import ISettingsSerializer

T = TypeVar('T')


class BaseJsonSettingsRepository(ISettingsRepository[T], Generic[T]):
    def __init__(self, serializer: ISettingsSerializer[T], file_path: Optional[str] = None,
                 *, required: bool = True):
        super().__init__(file_path)
        self._serializer = serializer
        self.required = required
        self.logger = logging.getLogger(self.__class__.__name__)

    def load_result(self) -> LoadResult[T]:
        if not self.file_path:
            return LoadResult(StoreStatus.MISSING, detail='No settings path configured')
        try:
            data = read_json_object(Path(self.file_path))
        except JsonStoreError as exc:
            return LoadResult(exc.status, detail=str(exc))
        try:
            return LoadResult(StoreStatus.OK, self._serializer.from_dict(data))
        except Exception as exc:
            return LoadResult(StoreStatus.CORRUPT, detail=f'Serializer validation failed: {exc}')

    def load(self) -> T:
        result = self.load_result()
        if result.status is StoreStatus.OK:
            return result.value
        if not self.required and result.status is StoreStatus.MISSING:
            self.logger.warning('Optional settings missing at %s; using in-memory defaults', self.file_path)
            return self._serializer.get_default()
        error = SettingsLoadError(f'{self.file_path}: {result.status.value}: {result.detail}')
        error.status = result.status
        raise error

    def save(self, settings: T) -> None:
        if not self.file_path:
            raise SettingsSaveError('No settings path configured')
        try:
            data = self._serializer.to_dict(settings)
            if not isinstance(data, dict):
                raise ValueError('Settings serializer must produce a JSON object')
            self._serializer.from_dict(data)
            with store_lock(Path(self.file_path)):
                self._write_file(data)
        except Exception as exc:
            error = SettingsSaveError(f"Failed to save '{self.file_path}': {exc}")
            error.published = bool(getattr(exc, 'published', False))
            raise error from exc

    def exists(self) -> bool:
        return bool(self.file_path) and os.path.exists(self.file_path)

    def _write_file(self, data: dict) -> None:
        atomic_write_json(Path(self.file_path), data)
