from PyQt6.QtCore import QCoreApplication

from src.applications.base.i_application_controller import IApplicationController


class PlatformSettingsController(IApplicationController):
    def __init__(self, model, view) -> None:
        self._model = model
        self._view = view
        self._status_source = None
        self._preview_active = False
        self._stopped = False
        self._view.virtual_keyboard_changed.connect(self._save_virtual_keyboard)
        self._view.colors_changed.connect(self._save_colors)
        self._view.color_preview_requested.connect(self._preview_color)
        self._view.color_preview_cancel_requested.connect(self._discard_preview)
        self._view.default_colors_requested.connect(self._restore_colors)
        self._view.theme_preview_requested.connect(self._preview_theme)
        self._view.selected_language_changed.connect(self._save_language)
        self._view.language_changed.connect(self._sync_language)
        self._view.destroyed.connect(self.stop)

    def load(self) -> None:
        self._view.set_virtual_keyboard_enabled(
            self._model.is_virtual_keyboard_enabled()
        )
        try:
            self._show_colors(self._model.get_colors())
        except (OSError, ValueError) as exc:
            self._show_colors(self._model.get_default_colors())
            self._show_error(exc)
        self._view.set_languages(self._model.available_languages(), self._model.get_language())

    def _sync_language(self) -> None:
        self._view.set_selected_language(self._model.get_language())
        if self._status_source:
            self._set_status(self._status_source)

    def _set_status(self, source: str) -> None:
        self._status_source = source
        self._view.set_status(self._t(source))

    def _show_error(self, error: Exception) -> None:
        self._status_source = None
        self._view.set_error(str(error))

    def _show_saved_status(self) -> None:
        if self._preview_active:
            self._show_preview_status()
        else:
            self._set_status("Saved. The change is active now.")

    def _show_preview_status(self) -> None:
        self._set_status("Preview only. Apply colors to keep these changes.")

    def _show_colors(self, colors: dict[str, str]) -> None:
        self._view.set_colors(colors)
        self._view.set_selected_theme(self._model.get_selected_theme(colors))

    def _preview_theme(self, preset: str) -> None:
        if self._stopped:
            return
        try:
            colors = self._model.get_preset_colors(preset)
            self._model.preview_colors(colors)
        except ValueError as exc:
            self._show_error(exc)
            return
        self._preview_active = True
        self._show_colors(colors)
        self._show_preview_status()

    def _preview_color(self, role: str, color: str) -> None:
        if self._stopped:
            return
        try:
            self._model.preview_color(role, color)
        except ValueError as exc:
            self._show_error(exc)
            return
        self._preview_active = True
        self._view.set_selected_theme(self._model.get_selected_theme())
        self._show_preview_status()

    def _discard_preview(self) -> None:
        if self._stopped or not self._preview_active:
            return
        self._preview_active = False
        self._model.discard_color_preview()
        try:
            self._show_colors(self._model.get_colors())
        except (OSError, ValueError) as exc:
            self._show_colors(self._model.get_default_colors())
            self._show_error(exc)
            return
        self._set_status("Unsaved color changes discarded.")

    def _save_language(self, code: str) -> None:
        try:
            self._model.set_language(code)
        except (OSError, ValueError) as exc:
            self._sync_language()
            self._show_error(exc)
            return
        self._sync_language()
        self._show_saved_status()

    def _save_colors(self, colors: dict) -> None:
        try:
            self._model.set_colors(colors)
        except (OSError, ValueError) as exc:
            self._show_error(exc)
            return
        self._preview_active = False
        self._show_colors(self._model.get_colors())
        self._show_saved_status()

    def _restore_colors(self) -> None:
        colors = self._model.get_default_colors()
        self._model.preview_colors(colors)
        self._preview_active = True
        self._show_colors(colors)
        self._show_preview_status()

    def stop(self) -> None:
        if self._stopped:
            return
        self._stopped = True
        self._model.discard_color_preview()
        self._preview_active = False

    def _save_virtual_keyboard(self, enabled: bool) -> None:
        try:
            self._model.set_virtual_keyboard_enabled(enabled)
        except (OSError, ValueError) as exc:
            self._view.set_virtual_keyboard_enabled(
                self._model.is_virtual_keyboard_enabled()
            )
            self._show_error(exc)
            return
        self._show_saved_status()

    @staticmethod
    def _t(source: str) -> str:
        return QCoreApplication.translate("PlatformSettingsController", source) or source
