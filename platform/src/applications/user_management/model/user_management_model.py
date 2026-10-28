from dataclasses import replace

from src.applications.base.i_application_model import IApplicationModel
from src.applications.user_management.service.i_user_management_service import IUserManagementService, UserSuccess


class UserManagementModel(IApplicationModel):
    def __init__(self, service: IUserManagementService, permissions_model):
        self._service = service
        self.permissions = permissions_model
        self.page = None

    def load(self):
        return self._service.load_users()

    def session_revision(self):
        return self._service.session_revision()

    def access(self, target_id):
        return self._service.access(target_id)

    def create(self, command):
        return self._service.create(command)

    def edit(self, command):
        return self._service.edit(command)

    def change_password(self, command):
        return self._service.change_password(command)

    def change_role(self, command):
        return self._service.change_role(command)

    def delete(self, account_id, revision):
        return self._service.delete(account_id, revision)

    def reveal(self, account_id):
        return self._service.reveal(account_id)

    def issue_qr(self, account_id, revision):
        return self._service.issue_qr(account_id, revision)

    def generate_recovery_codes(self, current_password):
        return self._service.generate_recovery_codes(current_password)

    def history(self, account_id):
        result = self._service.history(account_id)
        if isinstance(result, UserSuccess) and self.page is not None:
            actors = {row.account_id: self._actor_label(row) for row in self.page.users}
            return UserSuccess(tuple(replace(event, actor=actors.get(event.actor, event.actor))
                                     for event in result.value))
        return result

    def save(self, *args, **kwargs):
        raise NotImplementedError("Use the explicit account commands")

    def filtered_users(self, key: str, value: str):
        rows = self.page.users if self.page is not None else ()
        # Resolve stable actor IDs against the full authorized page before filtering.
        # Keep raw IDs and the accepted service snapshot unchanged for commands/audit.
        actors = {row.account_id: self._actor_label(row) for row in rows}
        rows = tuple(replace(row,
            created_by_label=actors.get(row.created_by, "—"),
            updated_by_label=actors.get(row.updated_by, "—")) for row in rows)
        if not value:
            return rows
        return tuple(row for row in rows if value.casefold() in str(row.get(key)).casefold())

    @staticmethod
    def _actor_label(row):
        name = " ".join(part.strip() for part in (row.first_name, row.last_name) if part.strip())
        return f"{name} ({row.login_id})" if name else row.login_id
