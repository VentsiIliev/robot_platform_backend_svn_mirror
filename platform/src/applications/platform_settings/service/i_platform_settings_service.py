"""Platform-independent contract for shared platform UI preferences."""

from abc import ABC, abstractmethod


class IPlatformSettingsService(ABC):
    @abstractmethod
    def is_virtual_keyboard_enabled(self) -> bool: ...

    @abstractmethod
    def set_virtual_keyboard_enabled(self, enabled: bool) -> None: ...
