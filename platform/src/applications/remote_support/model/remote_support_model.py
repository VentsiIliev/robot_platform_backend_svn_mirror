from src.applications.base.i_application_model import IApplicationModel
from src.applications.remote_support.service.i_remote_support_service import IRemoteSupportService


class RemoteSupportModel(IApplicationModel):
    def __init__(self, service: IRemoteSupportService):
        self._service = service

    def load(self) -> dict:
        return self._service.get_remote_support_status()

    def save(self, enabled: bool, duration_seconds: int = 900) -> None:
        self._service.set_remote_support_enabled(enabled, duration_seconds)

    def get_remote_support_status(self) -> dict:
        return self.load()

    def set_remote_support_enabled(self, enabled: bool, duration_seconds: int = 900) -> None:
        self.save(enabled, duration_seconds)

    def get_password_status(self) -> dict:
        return self._service.get_password_status()

    def set_unattended_password(self, admin_id: str, admin_password: str, password: str, confirmation: str) -> None:
        if password != confirmation:
            raise ValueError("Passwords do not match")
        self._service.set_unattended_password(admin_id, admin_password, password)

    def remove_unattended_password(self, admin_id: str, admin_password: str) -> None:
        self._service.remove_unattended_password(admin_id, admin_password)
