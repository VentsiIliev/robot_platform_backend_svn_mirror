from src.applications.base.i_application_model import IApplicationModel
from ..service.i_platform_settings_service import IPlatformSettingsService


class PlatformSettingsModel(IApplicationModel):
    def __init__(self, service: IPlatformSettingsService) -> None:
        self._service = service

    def load(self) -> None:
        pass

    def save(self) -> None:
        pass

    def is_virtual_keyboard_enabled(self) -> bool:
        return self._service.is_virtual_keyboard_enabled()

    def set_virtual_keyboard_enabled(self, enabled: bool) -> None:
        self._service.set_virtual_keyboard_enabled(enabled)
