from functools import partial
from PyQt6.QtCore import QCoreApplication, QTimer
from src.applications.base.background_worker import BackgroundWorker
from src.applications.base.i_application_controller import IApplicationController


class RemoteSupportController(IApplicationController, BackgroundWorker):
    def __init__(self, model, view):
        BackgroundWorker.__init__(self)
        self._model = model
        self._view = view
        self._stopped = False
        self._status_source = ""
        self._error_source = ""
        self._error_kind = ""
        self._busy = {"remote": False, "password": False}
        self._remote_timer = QTimer(view)
        self._remote_timer.setInterval(3000)
        self._remote_timer.timeout.connect(self._refresh_remote_if_visible)
        view.remote_support_requested.connect(self._set_remote_support)
        view.remote_support_refresh_requested.connect(self._refresh_all)
        view.password_change_requested.connect(self._change_password)
        view.password_remove_requested.connect(self._remove_password)
        view.language_changed.connect(self._retranslate)

    def load(self) -> None:
        QTimer.singleShot(0, self._refresh_all)
        self._remote_timer.start()

    def stop(self) -> None:
        self._stopped = True
        self._remote_timer.stop()
        self._view.clear_password_fields()
        self._stop_threads()

    def _refresh_remote_if_visible(self) -> None:
        if self._view.is_remote_support_visible():
            self._refresh_all()

    def _refresh_all(self) -> None:
        self._refresh_remote_support()
        self._refresh_password_status()

    @staticmethod
    def _t(source: str) -> str:
        return QCoreApplication.translate("RemoteSupportController", source) or source

    def _refresh_remote_support(self) -> None:
        if self._stopped or self._busy["remote"]:
            return
        self._set_busy("remote", True)
        self._run_in_thread(
            self._model.get_remote_support_status,
            self._remote_support_loaded,
            partial(self._on_error, "remote"),
        )

    def _remote_support_loaded(self, status: dict) -> None:
        if self._stopped:
            return
        self._view.set_remote_support_status(status)
        if self._error_kind == "remote":
            self._error_source = ""
        self._set_busy("remote", False)

    def _set_remote_support(self, enabled: bool) -> None:
        if self._stopped or any(self._busy.values()):
            return
        self._set_busy("remote", True)
        self._set_status("Starting remote support…" if enabled else "Stopping remote support…")
        duration = self._view.get_access_duration()
        self._run_in_thread(
            partial(self._model.set_remote_support_enabled, enabled, duration),
            self._remote_support_changed,
            self._on_remote_change_error,
        )

    def _on_remote_change_error(self, message: str) -> None:
        self._on_error("remote", message)
        self._refresh_remote_support()

    def _remote_support_changed(self, _result) -> None:
        if self._stopped:
            return
        self._set_busy("remote", False)
        self._refresh_remote_support()
        self._set_status("Remote support service updated")

    def _refresh_password_status(self) -> None:
        if self._stopped or self._busy["password"]:
            return
        self._set_busy("password", True)
        self._run_in_thread(self._model.get_password_status, self._password_loaded,
                            partial(self._on_error, "password"))

    def _password_loaded(self, status: dict) -> None:
        if self._stopped:
            return
        self._view.set_password_status(status)
        if self._error_kind == "password":
            self._error_source = ""
        self._set_busy("password", False)

    def _run_password_operation(self, fn) -> None:
        if self._stopped or any(self._busy.values()):
            return
        self._view.set_password_operation_busy(True)
        self._set_busy("password", True)
        self._set_status("Updating unattended access…")
        self._run_in_thread(fn, self._password_changed, self._password_operation_failed)

    def _password_operation_failed(self, message: str) -> None:
        if self._stopped:
            return
        self._view.set_password_operation_busy(False)
        self._on_error("password", message)

    def _change_password(self, admin_id: str, admin_password: str, password: str, confirmation: str) -> None:
        self._run_password_operation(partial(
            self._model.set_unattended_password, admin_id, admin_password, password, confirmation,
        ))

    def _remove_password(self, admin_id: str, admin_password: str) -> None:
        self._run_password_operation(partial(self._model.remove_unattended_password, admin_id, admin_password))

    def _password_changed(self, _result) -> None:
        if self._stopped:
            return
        self._view.set_password_operation_busy(False)
        self._set_busy("password", False)
        self._refresh_password_status()
        self._set_status("Unattended access updated")

    def _set_status(self, source: str) -> None:
        self._error_source = ""
        self._status_source = source
        self._retranslate()

    def _retranslate(self) -> None:
        if self._error_source and not self._stopped:
            translated = self._t(self._error_source)
            if self._error_kind == "remote":
                self._view.set_remote_support_error(translated)
            else:
                self._view.set_password_error(translated)
            self._view.set_error(translated)
            return
        if self._status_source and not self._stopped:
            self._view.set_status(self._t(self._status_source))

    def _set_busy(self, kind: str, busy: bool) -> None:
        self._busy[kind] = busy
        self._view.set_busy(kind, busy)

    def _on_error(self, kind: str, message: str) -> None:
        if self._stopped:
            return
        self._set_busy(kind, False)
        self._status_source = ""
        self._error_source = message
        self._error_kind = kind
        self._retranslate()
