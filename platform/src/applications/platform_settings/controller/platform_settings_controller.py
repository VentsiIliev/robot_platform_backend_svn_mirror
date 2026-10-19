from PyQt6.QtCore import QCoreApplication

from src.applications.base.i_application_controller import IApplicationController


class PlatformSettingsController(IApplicationController):
    def __init__(self, model, view) -> None:
        self._model = model
        self._view = view
        self._view.virtual_keyboard_changed.connect(self._save_virtual_keyboard)

    def load(self) -> None:
        self._view.set_virtual_keyboard_enabled(
            self._model.is_virtual_keyboard_enabled()
        )

    def stop(self) -> None:
        pass

    def _save_virtual_keyboard(self, enabled: bool) -> None:
        try:
            self._model.set_virtual_keyboard_enabled(enabled)
        except (OSError, ValueError) as exc:
            self._view.set_virtual_keyboard_enabled(
                self._model.is_virtual_keyboard_enabled()
            )
            self._view.set_error(str(exc))
            return
        self._view.set_status(self._t("Saved. The change is active now."))

    @staticmethod
    def _t(source: str) -> str:
        return QCoreApplication.translate("PlatformSettingsController", source) or source
