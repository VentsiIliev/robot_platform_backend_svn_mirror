import logging
from copy import deepcopy
from threading import RLock
from enum import Enum
from typing import Any, Dict

from src.engine.repositories.interfaces.i_settings_service import ISettingsService
from src.engine.repositories.interfaces.settings_repository import (
    ISettingsRepository,
    SettingsLoadError,
)


class SettingsService(ISettingsService):

    def __init__(self, repos: Dict[Enum, ISettingsRepository]):
        self._lock = RLock()
        self._repos = repos
        self._cache: Dict[Enum, Any] = {}
        self._logger = logging.getLogger(self.__class__.__name__)

    def get(self, name: Enum) -> Any:
        with self._lock:
            if not isinstance(name, Enum):
                raise TypeError(
                    f"SettingsService: key must be an Enum value, got {type(name).__name__!r}: {name!r}. "
                )

            if name in self._cache:
                return deepcopy(self._cache[name])
            return self.reload(name)

    def get_repo(self, name: Enum) -> ISettingsRepository:
        if not isinstance(name, Enum):
            raise TypeError(
                f"SettingsService: key must be an Enum value, got {type(name).__name__!r}: {name!r}. "
            )

        self._require(name)
        return self._repos[name]

    def reload(self, name: Enum) -> Any:
        with self._lock:
            if not isinstance(name, Enum):
                raise TypeError(
                    f"SettingsService: key must be an Enum value, got {type(name).__name__!r}: {name!r}. "
                )

            self._require(name)
            self._logger.debug("Loading settings '%s'", name)
            self._cache.pop(name, None)
            value = self._repos[name].load()
            self._cache[name] = deepcopy(value)
            return deepcopy(value)

    def save(self, name: Enum, settings: Any) -> None:
        with self._lock:
            if not isinstance(name, Enum):
                raise TypeError(
                    f"SettingsService: key must be an Enum value, got {type(name).__name__!r}: {name!r}. "
                )

            self._require(name)
            self._logger.debug("Saving settings '%s'", name)
            self._cache.pop(name, None)
            self._repos[name].save(settings)
            self._cache[name] = deepcopy(settings)

    def _require(self, name: Enum) -> None:
        if not isinstance(name, Enum):
            raise TypeError(
                f"SettingsService: key must be an Enum value, got {type(name).__name__!r}: {name!r}. "
            )

        if name not in self._repos:
            raise KeyError(
                f"No settings repository registered for '{name}'. "
                f"Available: {list(self._repos.keys())}"
            )