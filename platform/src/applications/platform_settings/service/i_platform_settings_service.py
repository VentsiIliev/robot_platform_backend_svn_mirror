"""Platform-independent contract for shared platform UI preferences."""

from abc import ABC, abstractmethod


class IPlatformSettingsService(ABC):
    @abstractmethod
    def available_languages(self) -> list[tuple[str, str]]: ...

    @abstractmethod
    def get_language(self) -> str: ...

    @abstractmethod
    def set_language(self, code: str) -> None: ...

    @abstractmethod
    def get_colors(self) -> dict[str, str]: ...

    @abstractmethod
    def set_colors(self, colors: dict[str, str]) -> None: ...

    @abstractmethod
    def preview_colors(self, colors: dict[str, str]) -> None:
        """Apply a validated runtime preview without writing preferences."""

    @abstractmethod
    def discard_color_preview(self) -> None:
        """Restore the palette from before the first unsaved preview."""

    @abstractmethod
    def get_default_colors(self) -> dict[str, str]: ...

    @abstractmethod
    def get_color_presets(self) -> dict[str, dict[str, str]]:
        """Return available preset IDs and their complete color palettes."""

    @abstractmethod
    def is_virtual_keyboard_enabled(self) -> bool: ...

    @abstractmethod
    def set_virtual_keyboard_enabled(self, enabled: bool) -> None: ...
