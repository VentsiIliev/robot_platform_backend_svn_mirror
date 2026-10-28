from typing import Optional
from functools import partial

from PyQt6.QtCore import QObject, pyqtSignal, QCoreApplication

from src.applications.base.background_worker import BackgroundWorker
from src.applications.login.model.login_model import LoginModel
from src.applications.login.i_login_application_service import (
    AdminRecovery, AdminSetup, LoginErrorCode, LoginFailure,
)
from src.engine.core.i_messaging_service import IMessagingService
from src.shared_contracts.events.vision_events import VisionTopics


class _Bridge(QObject):
    """Safely delivers camera frames from the broker thread to the Qt thread."""
    camera_frame = pyqtSignal(object)


class LoginController(BackgroundWorker):

    def __init__(
        self,
        model: LoginModel,
        view,
        messaging: Optional[IMessagingService] = None,
    ) -> None:
        BackgroundWorker.__init__(self)
        self._model     = model
        self._view      = view
        self._messaging = messaging
        self._bridge    = _Bridge()
        self._bridge.camera_frame.connect(self._on_camera_frame)
        self._stopped = False
        self._connection_information_busy = False
        self._busy = False
        self._error_source = None

    def load(self) -> None:
        self._view.setup_confirmed.connect(self._on_setup_confirmed)
        self._view.login_submitted.connect(self._on_login_submitted)
        self._view.qr_scan_requested.connect(self._on_qr_scan_requested)
        self._view.qr_tab_activated.connect(self._on_qr_tab_activated)
        self._view.first_admin_submitted.connect(self._on_first_admin_submitted)
        self._view.recovery_submitted.connect(self._on_recovery_submitted)
        self._view.language_changed.connect(self._retranslate_error)
        self._view.connection_information_requested.connect(self._refresh_connection_information)

        if self._messaging:
            self._messaging.subscribe(
                VisionTopics.LATEST_IMAGE, self._on_camera_frame_raw
            )

        self._view.show_setup()

    def stop(self) -> None:
        """Stop background queries and release subscriptions before view deletion."""
        if self._stopped:
            return
        self._stopped = True
        if self._messaging:
            self._messaging.unsubscribe(VisionTopics.LATEST_IMAGE, self._on_camera_frame_raw)
        self._stop_threads()

    def _refresh_connection_information(self) -> None:
        if (self._stopped or self._connection_information_busy or
                not self._view.is_connection_information_authorized()):
            return
        self._connection_information_busy = True
        self._view.set_connection_information_busy(True)
        self._run_in_thread(
            self._model.get_connection_information,
            self._connection_information_loaded,
            self._connection_information_failed,
        )

    def _connection_information_loaded(self, information: dict) -> None:
        if self._stopped:
            return
        self._connection_information_busy = False
        self._view.set_connection_information(information)
        self._view.set_connection_information_busy(False)

    def _connection_information_failed(self, _message: str) -> None:
        if self._stopped:
            return
        self._connection_information_busy = False
        self._view.show_connection_information_error()
        self._view.set_connection_information_busy(False)

    # ── Camera frame delivery ────────────────────────────────────────────────

    @staticmethod
    def _t(text: str) -> str:
        translated = QCoreApplication.translate("Login", text)
        return translated or text

    def _on_camera_frame_raw(self, msg) -> None:
        """Broker thread — must not touch Qt. Forward via bridge signal."""
        frame = msg.get("image") if isinstance(msg, dict) else msg
        if frame is not None:
            self._bridge.camera_frame.emit(frame)

    def _on_camera_frame(self, frame) -> None:
        """Qt thread — safe to update the view."""
        if not self._stopped:
            self._view.update_camera_frame(frame)

    # ── Navigation slots ─────────────────────────────────────────────────────

    def _on_setup_confirmed(self) -> None:
        self._start(self._model.is_first_run, self._setup_loaded)

    def _setup_loaded(self, result) -> None:
        if self._show_failure(result):
            return
        if result.value:
            self._view.show_first_run()
        else:
            self._view.show_login()

    # ── Login slots ──────────────────────────────────────────────────────────

    def _on_login_submitted(self, user_id: str, password: str) -> None:
        error = self._model.validate_login_input(user_id, password)
        if error:
            self._display_error(error)
            return
        self._start(partial(self._model.authenticate, user_id, password), self._authenticated)

    def _on_qr_tab_activated(self) -> None:
        self._start(self._model.move_to_login_pos, self._positioned)

    def _positioned(self, _result) -> None:
        pass

    def _on_qr_scan_requested(self) -> None:
        self._start(self._model.poll_qr_login, self._authenticated)

    def _authenticated(self, result) -> None:
        if not self._show_failure(result) and result.value is not None:
            self._view.stop_qr_scanning()
            self._view.accept_login(result.value)

    def _on_first_admin_submitted(
        self, user_id: str, first_name: str, last_name: str, password: str
    ) -> None:
        error = self._model.validate_login_input(user_id, password)
        if error:
            self._display_error(error)
            return
        self._start(partial(self._model.create_and_login,
                            AdminSetup(user_id.strip(), first_name, last_name, password)), self._authenticated)

    def _on_recovery_submitted(self, user_id: str, code: str, password: str) -> None:
        self._start(partial(self._model.recover_admin, AdminRecovery(user_id.strip(), code, password)),
                    self._recovered)

    def _recovered(self, result) -> None:
        if not self._show_failure(result):
            self._view.show_replacement_codes(result.value.codes)
            self._view.show_login()

    def _start(self, operation, callback) -> None:
        if self._stopped or self._busy:
            return
        self._busy = True
        self._error_source = None
        self._view.clear_error()
        self._view.set_authentication_busy(True)
        self._run_in_thread(operation, partial(self._delivered, callback), self._operation_failed)

    def _delivered(self, callback, result) -> None:
        if self._stopped:
            return
        self._busy = False
        self._view.set_authentication_busy(False)
        callback(result)

    def _operation_failed(self, _unsafe_message: str) -> None:
        if self._stopped:
            return
        self._busy = False
        self._view.set_authentication_busy(False)
        self._display_error("The account service is unavailable. Contact service support.")

    def _show_failure(self, result) -> bool:
        if not isinstance(result, LoginFailure):
            return False
        messages = {
            LoginErrorCode.INVALID_INPUT: "Check the entered account details.",
            LoginErrorCode.INVALID_PROOF: "Invalid credentials or recovery code. Please try again.",
            LoginErrorCode.RATE_LIMITED: "Too many attempts. Wait before trying again.",
            LoginErrorCode.BUSY: "Wait until the active operation is idle before changing access.",
            LoginErrorCode.SETUP_CLOSED: "Initial Admin setup is already complete. Log in normally.",
            LoginErrorCode.ALREADY_EXISTS: "This user ID is already in use.",
            LoginErrorCode.UNAVAILABLE: "The account service is unavailable. Contact service support.",
        }
        self._display_error(messages[result.error.code])
        return True

    def _display_error(self, source):
        self._error_source = source
        self._view.show_error(self._t(source))

    def _retranslate_error(self):
        if not self._stopped and self._error_source is not None:
            self._view.show_error(self._t(self._error_source))
