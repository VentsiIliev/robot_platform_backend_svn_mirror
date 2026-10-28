"""Qt-free permission state; writes use the exact revision displayed to the user."""
from src.applications.user_management.service.i_user_management_service import IUserManagementService


class PermissionsModel:
    def __init__(self, service: IUserManagementService):
        self._service = service
        self.page = None

    def load(self):
        return self._service.permissions()

    def session_revision(self):
        return self._service.session_revision()

    def set_permission(self, app_id, role, allowed):
        if self.page is None:
            raise RuntimeError("Load permissions before editing")
        grants = dict(self.page.grants)
        roles = set(grants[app_id])
        if allowed:
            roles.add(role)
        else:
            roles.discard(role)
        return self._service.set_permission(app_id, tuple(sorted(roles)), self.page.revision)
