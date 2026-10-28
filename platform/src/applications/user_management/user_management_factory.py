from src.applications.base.application_factory import ApplicationFactory
from src.applications.user_management.controller.user_management_controller import UserManagementController
from src.applications.user_management.model.user_management_model import UserManagementModel
from src.applications.user_management.model.permissions_model import PermissionsModel
from src.applications.user_management.view.user_management_view import UserManagementView
from src.applications.user_management.domain.default_schema import DEFAULT_USER_SCHEMA


class UserManagementFactory(ApplicationFactory):
    def _create_model(self, service):
        return UserManagementModel(service, PermissionsModel(service))

    def _create_view(self):
        return UserManagementView(DEFAULT_USER_SCHEMA)

    def _create_controller(self, model, view):
        return UserManagementController(model, view)
