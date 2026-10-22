from __future__ import annotations

from pathlib import Path

from src.engine.auth.i_permissions_repository import IPermissionsRepository
from src.engine.core.durable_files import atomic_write_json, store_lock
from src.engine.repositories.json.json_store import JsonStoreError, StoreStatus, read_json_object


class JsonPermissionsRepository(IPermissionsRepository):
    """Strict permissions store; mutations reread under a cross-process lock."""

    def __init__(self, file_path: str, default_role_values: list[str] | None = None) -> None:
        self._path = file_path
        self._default_role_values = list(default_role_values or [])
        self._load()  # Fail construction if an established permissions file is unavailable.

    def get_allowed_role_values(self, app_id: str) -> list[str]:
        return list(self._load().get(app_id, self._default_role_values))

    def set_allowed_role_values(self, app_id: str, role_values: list[str]) -> None:
        with store_lock(Path(self._path)):
            data = self._load()
            data[app_id] = list(role_values)
            self._validate(data)
            atomic_write_json(Path(self._path), data, mode=0o600)

    def get_all(self) -> dict[str, list[str]]:
        return self._load()

    def _validate(self, data: dict) -> None:
        if any(not isinstance(key, str) or not key or not isinstance(roles, list)
               or any(not isinstance(role, str) or not role for role in roles)
               for key, roles in data.items()):
            raise JsonStoreError(self._path, StoreStatus.CORRUPT,
                                 'Permissions must map application IDs to lists of role strings')

    def _load(self) -> dict[str, list[str]]:
        data = read_json_object(Path(self._path))
        self._validate(data)
        return data
