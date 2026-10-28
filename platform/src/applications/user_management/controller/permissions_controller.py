from functools import partial
from PyQt6.QtCore import QCoreApplication
from src.applications.base.background_worker import BackgroundWorker
from src.applications.user_management.service.i_user_management_service import UserErrorCode, UserFailure


class PermissionsController(BackgroundWorker):
    def __init__(self, model, view):
        super().__init__()
        self._model, self._view = model, view
        self._stopped, self._busy = False, False
        self._connected = False

    def load(self):
        self._view.permission_toggled.connect(self._on_permission_toggled)
        self._view.language_changed.connect(self._retranslate)
        self._connected = True
        self.refresh()

    def refresh(self):
        if not self._busy and not self._stopped:
            self._start(self._model.load)

    def _start(self, operation):
        self._busy = True
        self._session_revision = self._model.session_revision()
        self._view.setEnabled(False)
        self._run_in_thread(operation, self._loaded, self._failed)

    def _loaded(self, result):
        if self._stopped:
            return
        self._busy = False
        if self._session_revision != self._model.session_revision():
            self._view.clear_permissions()
            return
        if isinstance(result, UserFailure):
            self._model.page = None
            self._view.clear_permissions()
            self._notice("Wait until the active operation is idle before changing access."
                         if result.error.code == UserErrorCode.BUSY
                         else "Permissions could not be loaded. Refresh and try again.")
            return
        self._model.page = result.value
        page = result.value
        self._view.set_permissions([app for app, _ in page.grants], list(page.roles),
                                   {app: list(roles) for app, roles in page.grants}, page.locked)
        self._view.setEnabled(True)
        self._notice("Changes apply immediately. Protected role grants cannot be edited.")

    def _on_permission_toggled(self, app_id, role, allowed):
        if not self._busy and not self._stopped and self._model.page is not None:
            self._start(partial(self._model.set_permission, app_id, role, allowed))

    def _failed(self, _message):
        if not self._stopped:
            self._busy = False
            self._model.page = None
            self._view.clear_permissions()
            self._notice("Permissions could not be loaded. Refresh and try again.")

    def _notice(self, source):
        self._notice_source = source
        self._view.set_notice(self._t(source))

    def _retranslate(self):
        if not self._stopped and hasattr(self, "_notice_source"):
            self._view.set_notice(self._t(self._notice_source))

    def stop(self):
        if self._stopped:
            return
        self._stopped = True
        if self._connected:
            try:
                self._view.permission_toggled.disconnect(self._on_permission_toggled)
                self._view.language_changed.disconnect(self._retranslate)
            except (RuntimeError, TypeError):
                pass
            self._connected = False
        self._stop_threads()
        self._model.page = None
        self._view.clear_permissions()

    @staticmethod
    def _t(text):
        return QCoreApplication.translate("UserManagement", text) or text
