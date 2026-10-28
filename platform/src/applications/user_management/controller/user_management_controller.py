from functools import partial

from PyQt6.QtCore import QCoreApplication, QTimer

from src.applications.base.i_application_controller import IApplicationController
from src.applications.base.background_worker import BackgroundWorker
from src.applications.base.access.access_binding import AccessBinding
from src.applications.base.access.contracts import AccessRequirement, AccessVersion, ControlState, PresentationAccess
from src.applications.base.styled_message_box import ask_yes_no, show_warning
from src.applications.user_management.service.i_user_management_service import (
    NewUser, EditUser, PasswordChange, RoleChange, UserFailure,
)
from src.applications.user_management.controller.permissions_controller import PermissionsController
from src.shared_contracts.authorization.actions import UserAction, RecoveryAction, AuditAction
from src.shared_contracts.authorization.features import UserFeature


_ACTIONS = {
    "add": UserAction.CREATE, "edit": UserAction.EDIT_PROFILE, "delete": UserAction.DELETE,
    "password": UserAction.CHANGE_PASSWORD, "reveal": UserAction.REVEAL_PASSWORD,
    "role": UserAction.CHANGE_ROLE, "qr": UserAction.ISSUE_LOGIN_TOKEN,
    "history": AuditAction.VIEW, "codes": RecoveryAction.ISSUE,
}
_PROFILE_FIELDS = (("first_name", "First Name", False), ("last_name", "Last Name", False),
                   ("email", "Email", False))
_PASSWORD_FIELDS = (("new_password", "New password", True), ("confirm", "Confirm password", True))


class UserManagementController(IApplicationController, BackgroundWorker):
    def __init__(self, model, view):
        BackgroundWorker.__init__(self)
        self._model, self._view = model, view
        self._binding = AccessBinding()
        self._binding_version = None
        self._busy = self._access_busy = self._stopped = False
        self._selected, self._screen, self._permissions = None, None, None
        self._epoch = 0
        self._filter = ("", "")
        self._session_revision = model.session_revision()
        self._timer = QTimer(view)
        self._timer.setInterval(1000)
        self._timer.timeout.connect(self._poll_access)

    def load(self):
        for key, adapter in self._view.access_adapters().items():
            requirement = (AccessRequirement(feature=UserFeature.APP_PERMISSIONS) if key == "permissions"
                           else AccessRequirement(action=_ACTIONS[key], hide_when_target_denied=key in {"reveal", "history"}))
            self._binding.register(key, adapter, requirement, operational=ControlState(True, False))
        for signal, callback in (
            (self._view.add_requested, self._on_add), (self._view.edit_requested, self._on_edit),
            (self._view.delete_requested, self._on_delete), (self._view.qr_requested, self._on_qr),
            (self._view.password_requested, self._on_password), (self._view.reveal_requested, self._on_reveal),
            (self._view.role_requested, self._on_role), (self._view.history_requested, self._on_history),
            (self._view.codes_requested, self._on_codes), (self._view.selection_changed, self._selection_changed),
            (self._view.refresh_requested, self._refresh), (self._view.filter_changed, self._on_filter),
            (self._view.language_changed, self._retranslate),
        ):
            signal.connect(callback)
        self._timer.start()
        self._refresh()

    def stop(self):
        if self._stopped:
            return
        self._stopped = True
        self._timer.stop()
        self._binding.close()
        if self._permissions is not None:
            self._permissions.stop()
        self._stop_threads()
        self._model.page = None

    def has_active_operations(self):
        return self._busy or (self._permissions is not None and self._permissions.has_running_workers())

    def _refresh(self):
        if self._busy or self._stopped:
            return
        if self._permissions is not None:
            self._permissions.refresh()
        self._invalidate()
        self._execute(self._model.load, self._users_loaded)

    def _users_loaded(self, result):
        if self._failure(result):
            self._model.page = None
            self._view.set_users([])
            self._request_access()
            return
        if result.value.session_revision != self._model.session_revision():
            self._model.page = None
            self._view.set_users([])
            self._invalidate()
            return
        self._model.page = result.value
        self._session_revision = result.value.session_revision
        self._view.set_users(self._model.filtered_users(*self._filter))
        self._status("{n} users loaded", n=len(result.value.users))
        self._request_access()

    def _selection_changed(self, selected):
        self._selected = selected
        self._invalidate()
        self._request_access()

    def _invalidate(self):
        self._epoch += 1
        self._screen = None
        self._binding_version = AccessVersion(self._session_revision, 0, self._epoch)
        self._binding.invalidate(self._binding_version)
        self._operational()

    def _operational(self):
        for key in self._binding.requirements():
            selected = key in {"add", "codes", "permissions"} or self._selected is not None
            self._binding.set_operational_state(key, ControlState(True, selected and not self._busy))

    def _poll_access(self):
        if self._stopped:
            return
        revision = self._model.session_revision()
        if revision != self._session_revision:
            self._session_revision = revision
            self._model.page = None
            self._view.clear_private_displays()
            self._view.set_users([])
            self._invalidate()
        self._request_access()

    def _request_access(self):
        if self._stopped or self._busy or self._access_busy:
            return
        self._access_busy = True
        target_id = self._selected.account_id if self._selected else None
        self._run_in_thread(partial(self._model.access, target_id),
                            partial(self._access_loaded, self._epoch), self._access_failed)

    def _access_loaded(self, epoch, result):
        if self._stopped:
            return
        self._access_busy = False
        if epoch != self._epoch:
            self._request_access()
            return
        if isinstance(result, UserFailure):
            self._access_lost()
            return
        screen = result.value
        if screen.session_revision != self._model.session_revision():
            self._invalidate()
            return
        self._screen = screen
        if not any(control.role_eligible for control in screen.controls):
            self._view.clear_private_displays()
            if self._model.page is not None:
                self._model.page = None
                self._view.set_users([])
                return
        version = AccessVersion(screen.session_revision, screen.policy_revision, epoch)
        accepted = self._binding.replace_access(self._binding_version, version, {
            control.key: PresentationAccess(control.visible and control.allowed, control.role_eligible, control.allowed)
            for control in screen.controls
        })
        if not accepted:
            self._invalidate()
            return
        self._binding_version = version
        self._operational()
        permitted = next(control.allowed for control in screen.controls if control.key == "permissions")
        if permitted and self._permissions is None:
            view = self._view.ensure_permissions_view()
            self._permissions = PermissionsController(self._model.permissions, view)
            self._permissions.load()
        elif not permitted and self._permissions is not None:
            self._permissions.stop()
            self._permissions = None

    def _access_failed(self, _message):
        if not self._stopped:
            self._access_busy = False
            self._access_lost()

    def _access_lost(self):
        self._invalidate()
        self._view.clear_private_displays()
        if self._permissions is not None:
            self._permissions.stop()
            self._permissions = None
        if self._model.page is not None:
            self._model.page = None
            self._view.set_users([])

    def _permitted(self, key, record=None):
        if self._stopped or self._busy or self._screen is None:
            return False
        if self._screen.session_revision != self._model.session_revision():
            self._invalidate()
            return False
        if record is not None and (self._selected is None or record.account_id != self._selected.account_id):
            return False
        return any(control.key == key and control.visible and control.allowed for control in self._screen.controls)

    def _execute(self, operation, callback):
        if self._busy or self._stopped:
            return
        self._busy = True
        self._view.set_busy(True)
        self._operational()
        revision = self._model.session_revision()
        self._run_in_thread(operation, partial(self._delivered, callback, revision), self._failed)

    def _delivered(self, callback, revision, result):
        if self._stopped:
            return
        self._busy = False
        self._view.set_busy(False)
        if revision != self._model.session_revision():
            self._model.page = None
            self._view.clear_private_displays()
            self._view.set_users([])
            self._invalidate()
            return
        self._operational()
        callback(result)

    def _failed(self, _message):
        if not self._stopped:
            self._busy = False
            self._view.set_busy(False)
            self._invalidate()
            self._status("The account service is unavailable. Contact service support.")

    def _failure(self, result):
        if not isinstance(result, UserFailure):
            return False
        messages = {
            "access_denied": "Access denied.",
            "authentication_required": "Your session expired. Log in again.",
            "invalid_input": "Check the entered values.",
            "invalid_proof": "The current password is incorrect.",
            "already_exists": "This user ID is already in use.",
            "not_found": "The account no longer exists.",
            "conflict": "The data changed. Refresh and try again.",
            "rate_limited": "Too many attempts. Try again later.",
            "busy": "Wait until the active operation is idle before changing access.",
            "policy_violation": "This change is not permitted by the account policy.",
            "credential_storage": "Credential storage needs service attention.",
        }
        self._status(messages.get(result.error.code,
                     "The account service is unavailable. Contact service support."))
        return True

    def _changed(self, result):
        if self._failure(result):
            self._invalidate()
            self._request_access()
            return
        self._refresh()

    def _on_add(self):
        if not self._permitted("add"):
            return
        roles = self._screen.create_roles
        fields = (("login_id", "ID", False),) + _PROFILE_FIELDS + (
            ("role", "Role", False), ("password", "Password", True), ("confirm", "Confirm password", True))
        values = self._view.ask_form("Add User", fields, choices={"role": roles})
        if values is None or not self._matching_password(values, "password"):
            return
        command = NewUser(values["login_id"].strip(), values["first_name"].strip(), values["last_name"].strip(),
                          values["role"], values["password"], values["email"].strip())
        self._execute(partial(self._model.create, command), self._changed)

    def _on_edit(self, record):
        if not self._permitted("edit", record):
            return
        values = self._view.ask_form("Edit User", _PROFILE_FIELDS,
                                    {key: getattr(record, key) for key, _label, _secret in _PROFILE_FIELDS})
        if values is not None:
            command = EditUser(record.account_id, record.revision, values["first_name"].strip(),
                               values["last_name"].strip(), values["email"].strip())
            self._execute(partial(self._model.edit, command), self._changed)

    def _on_delete(self, record):
        if self._permitted("delete", record) and ask_yes_no(
                self._view, self._t("Confirm Delete"), self._t("Delete user '{uid}'?").format(uid=record.login_id)):
            self._execute(partial(self._model.delete, record.account_id, record.revision), self._changed)

    def _on_password(self, record):
        if not self._permitted("password", record):
            return
        own = self._model.page is not None and record.account_id == self._model.page.actor_id
        fields = ((("current_password", "Current password", True),) if own else ()) + _PASSWORD_FIELDS
        values = self._view.ask_form("Change password", fields)
        if values is not None and self._matching_password(values, "new_password"):
            command = PasswordChange(record.account_id, record.revision, values["new_password"],
                                     values.get("current_password", ""))
            self._execute(partial(self._model.change_password, command), self._changed)

    def _on_role(self, record):
        if not self._permitted("role", record):
            return
        fields = (("role", "Role", False),) + _PASSWORD_FIELDS
        values = self._view.ask_form("Change role", fields, {"role": record.role},
                                    {"role": self._screen.create_roles})
        if values is not None and self._matching_password(values, "new_password"):
            command = RoleChange(record.account_id, record.revision, values["role"], values["new_password"])
            self._execute(partial(self._model.change_role, command), self._changed)

    def _matching_password(self, values, key):
        if values[key] and values[key] == values["confirm"]:
            return True
        show_warning(self._view, self._t("Invalid Input"), self._t("Enter matching nonempty passwords."))
        return False

    def _on_reveal(self, record):
        if self._permitted("reveal", record):
            self._execute(partial(self._model.reveal, record.account_id), self._revealed)

    def _revealed(self, result):
        if not self._failure(result):
            self._view.display_secret("Operator password", "Keep this password private.", result.value.text)

    def _on_qr(self, record):
        if self._permitted("qr", record):
            self._execute(partial(self._model.issue_qr, record.account_id, record.revision), self._qr_ready)

    def _qr_ready(self, result):
        if not self._failure(result):
            self._view.display_qr(result.value.png)

    def _on_codes(self):
        if not self._permitted("codes"):
            return
        values = self._view.ask_form("Generate recovery codes", (("password", "Current password", True),))
        if values is not None:
            self._execute(partial(self._model.generate_recovery_codes, values["password"]), self._codes_ready)

    def _codes_ready(self, result):
        if not self._failure(result):
            self._view.display_secret("Save recovery codes",
                                      "Save these codes privately now. They are shown once. All previous codes are invalid.",
                                      result.value.text)

    def _on_history(self, record):
        if self._permitted("history", record):
            self._execute(partial(self._model.history, record.account_id), self._history_ready)

    def _history_ready(self, result):
        if not self._failure(result):
            self._view.display_history(result.value)

    def _on_filter(self, key, value):
        self._filter = (key, value)
        self._view.set_users(self._model.filtered_users(key, value))
        if self._model.page is not None:
            self._status("{n} of {total} users", n=len(self._model.filtered_users(key, value)),
                         total=len(self._model.page.users))

    def _retranslate(self):
        if not self._stopped:
            self._view.retranslateUi()
            if hasattr(self, "_status_source"):
                self._view.set_status(self._t(self._status_source).format(**self._status_values))

    def _status(self, source, **values):
        self._status_source, self._status_values = source, values
        self._view.set_status(self._t(source).format(**values))

    @staticmethod
    def _t(text):
        return QCoreApplication.translate("UserManagement", text) or text
