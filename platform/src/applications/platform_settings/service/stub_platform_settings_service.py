from .i_platform_settings_service import IPlatformSettingsService


class StubPlatformSettingsService(IPlatformSettingsService):
    def __init__(self, enabled: bool = True) -> None:
        self._enabled = enabled

    def is_virtual_keyboard_enabled(self) -> bool:
        return self._enabled

    def set_virtual_keyboard_enabled(self, enabled: bool) -> None:
        self._enabled = bool(enabled)
