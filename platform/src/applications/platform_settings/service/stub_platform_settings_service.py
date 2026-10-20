from .i_platform_settings_service import IPlatformSettingsService
from pl_gui.theme.palette import DEFAULT_COLORS, THEME_PRESETS, ThemePreview, validate_colors


class StubPlatformSettingsService(IPlatformSettingsService):
    def __init__(self, enabled: bool = True) -> None:
        self._enabled = enabled
        self._colors = dict(DEFAULT_COLORS)
        self._language = "en"
        self._color_preview = ThemePreview()

    def preview_colors(self, colors: dict[str, str]) -> None:
        self._color_preview.update(colors)

    def discard_color_preview(self) -> None:
        self._color_preview.discard()

    def available_languages(self) -> list[tuple[str, str]]:
        return [("en", "English"), ("bg", "Български")]

    def get_language(self) -> str:
        return self._language

    def set_language(self, code: str) -> None:
        if code not in dict(self.available_languages()):
            raise ValueError("Unsupported language")
        self._language = code

    def get_colors(self) -> dict[str, str]:
        return dict(self._colors)

    def get_default_colors(self) -> dict[str, str]:
        return dict(DEFAULT_COLORS)

    def get_color_presets(self) -> dict[str, dict[str, str]]:
        return {name: dict(colors) for name, colors in THEME_PRESETS.items()}

    def set_colors(self, colors: dict[str, str]) -> None:
        self._colors = validate_colors(colors)
        self._color_preview.accept(self._colors)

    def is_virtual_keyboard_enabled(self) -> bool:
        return self._enabled

    def set_virtual_keyboard_enabled(self, enabled: bool) -> None:
        self._enabled = bool(enabled)
