from src.applications.base.i_application_model import IApplicationModel
from ..service.i_platform_settings_service import IPlatformSettingsService


class PlatformSettingsModel(IApplicationModel):
    def __init__(self, service: IPlatformSettingsService) -> None:
        self._service = service
        self._draft_colors = None

    def load(self) -> None:
        pass

    def save(self) -> None:
        pass

    def get_colors(self) -> dict[str, str]:
        colors = self._service.get_colors()
        self._draft_colors = dict(colors)
        return colors

    def preview_color(self, role: str, color: str) -> None:
        colors = dict(self._draft_colors or self.get_default_colors())
        colors[role] = color
        self.preview_colors(colors)

    def preview_colors(self, colors: dict[str, str]) -> None:
        self._service.preview_colors(colors)
        self._draft_colors = dict(colors)

    def discard_color_preview(self) -> None:
        self._service.discard_color_preview()

    def available_languages(self) -> list[tuple[str, str]]:
        return self._service.available_languages()

    def get_language(self) -> str:
        return self._service.get_language()

    def set_language(self, code: str) -> None:
        self._service.set_language(code)

    def set_colors(self, colors: dict[str, str]) -> None:
        self._service.set_colors(colors)

    def get_default_colors(self) -> dict[str, str]:
        return self._service.get_default_colors()

    def get_preset_colors(self, preset: str) -> dict[str, str]:
        presets = self._service.get_color_presets()
        if preset not in presets:
            raise ValueError("Unknown theme preset")
        return dict(presets[preset])

    def get_selected_theme(self, colors: dict[str, str] | None = None) -> str:
        selected = colors if colors is not None else self._draft_colors
        for name, preset_colors in self._service.get_color_presets().items():
            if preset_colors == selected:
                return name
        return "custom"

    def is_virtual_keyboard_enabled(self) -> bool:
        return self._service.is_virtual_keyboard_enabled()

    def set_virtual_keyboard_enabled(self, enabled: bool) -> None:
        self._service.set_virtual_keyboard_enabled(enabled)
