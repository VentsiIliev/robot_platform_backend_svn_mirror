from src.applications.base.application_factory import ApplicationFactory
from .controller.platform_settings_controller import PlatformSettingsController
from .model.platform_settings_model import PlatformSettingsModel
from .view.platform_settings_view import PlatformSettingsView


class PlatformSettingsFactory(ApplicationFactory):
    def _create_model(self, service):
        return PlatformSettingsModel(service)

    def _create_view(self):
        from PyQt6.QtWidgets import QApplication
        from pl_gui.theme.runtime import install_theme
        install_theme(QApplication.instance())
        return PlatformSettingsView()

    def _create_controller(self, model, view):
        return PlatformSettingsController(model, view)
