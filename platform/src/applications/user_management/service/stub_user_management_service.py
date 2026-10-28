"""In-memory application test double; never used by production wiring."""
from dataclasses import replace
from uuid import uuid4
import base64

from src.applications.user_management.service.i_user_management_service import (
    IUserManagementService, UserEntry, UserPage, UserSuccess, UserFailure, UserError,
    ScreenAccess, ControlAccess, SecretDisplay, QrDisplay, PermissionsPage,
)


class StubUserManagementService(IUserManagementService):
    def __init__(self):
        self._rows = {
            "demo-admin": UserEntry("demo-admin", "1", "Alice", "Admin", "Admin", "", True, 1, None, None, None, None),
            "demo-operator": UserEntry("demo-operator", "2", "Bob", "Operator", "Operator", "", True, 1, None, None, None, None),
            "demo-maker": UserEntry("demo-maker", "3", "Service", "Engineer", "Manufacturer", "", True, 1, None, None, None, None),
        }
        self._grants = (("demo", ("Manufacturer", "Admin", "Operator")),)
        self._permission_revision = 1

    def session_revision(self):
        return 1

    def load_users(self):
        return UserSuccess(UserPage(tuple(self._rows.values()), "demo-maker", "Manufacturer", 1))

    def access(self, target_id):
        target = self._rows.get(target_id)
        keys = ("add", "edit", "delete", "password", "reveal", "role", "qr", "history", "codes", "permissions")
        controls = tuple(ControlAccess(key, key != "codes", key != "codes",
                         (key in {"add", "permissions"}) or (target is not None and key != "codes"
                          and (key != "reveal" or target.role == "Operator"))) for key in keys)
        return UserSuccess(ScreenAccess(1, 1, controls, ("Manufacturer", "Admin", "Operator")))

    def create(self, command):
        if any(row.login_id == command.login_id for row in self._rows.values()):
            return UserFailure(UserError("already_exists"))
        row = UserEntry(uuid4().hex, command.login_id, command.first_name, command.last_name, command.role,
                        command.email, True, 1, None, "demo-maker", None, "demo-maker")
        self._rows[row.account_id] = row
        return UserSuccess(row)

    def _replace(self, identity, revision, **values):
        row = self._rows.get(identity)
        if row is None:
            return UserFailure(UserError("not_found"))
        if row.revision != revision:
            return UserFailure(UserError("conflict"))
        changed = replace(row, revision=row.revision + 1, **values)
        self._rows[identity] = changed
        return UserSuccess(changed)

    def edit(self, command):
        return self._replace(command.account_id, command.revision, first_name=command.first_name,
                             last_name=command.last_name, email=command.email)

    def change_password(self, command):
        return self._replace(command.account_id, command.revision)

    def change_role(self, command):
        return self._replace(command.account_id, command.revision, role=command.role)

    def delete(self, account_id, revision):
        result = self._replace(account_id, revision)
        if isinstance(result, UserFailure):
            return result
        del self._rows[account_id]
        return UserSuccess(None)

    def reveal(self, account_id):
        row = self._rows.get(account_id)
        if row is None or row.role != "Operator":
            return UserFailure(UserError("policy_violation"))
        return UserSuccess(SecretDisplay("DEMO ONLY"))

    def issue_qr(self, account_id, revision):
        return UserSuccess(QrDisplay(base64.b64decode(
            "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+aX1cAAAAASUVORK5CYII=")))

    def generate_recovery_codes(self, current_password):
        return UserSuccess(SecretDisplay("DEMO-CODE-NOT-VALID"))

    def history(self, account_id):
        return UserSuccess(())

    def permissions(self):
        return UserSuccess(PermissionsPage(self._permission_revision, ("Manufacturer", "Admin", "Operator"),
                                           self._grants, (("demo", "Manufacturer"),)))

    def set_permission(self, app_id, roles, revision):
        if revision != self._permission_revision:
            return UserFailure(UserError("conflict"))
        self._permission_revision += 1
        self._grants = ((app_id, roles),)
        return self.permissions()
