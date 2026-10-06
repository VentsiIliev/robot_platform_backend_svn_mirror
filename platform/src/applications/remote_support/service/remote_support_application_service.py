import sys

from src.engine.remote_support.client import RemoteSupportClient
from src.engine.remote_support.password_client import RustDeskPasswordClient
from src.engine.auth.i_authentication_service import IAuthenticationService
from .i_remote_support_service import IRemoteSupportService


class RemoteSupportApplicationService(IRemoteSupportService):
    def __init__(self, client=None, platform: str | None = None, *,
                 password_client=None, authentication_service: IAuthenticationService | None = None,
                 admin_role_value: str = "Admin"):
        self._client = client or RemoteSupportClient()
        self._platform = platform or sys.platform
        self._password_client = password_client or RustDeskPasswordClient()
        self._authentication = authentication_service
        self._admin_role_value = admin_role_value

    def _require_linux(self) -> None:
        if not self._platform.startswith("linux"):
            raise RuntimeError("Remote support service control is available on Linux")

    def get_remote_support_status(self) -> dict:
        self._require_linux()
        return self._client.status()

    def set_remote_support_enabled(self, enabled: bool, duration_seconds: int = 900) -> None:
        self._require_linux()
        if enabled:
            if type(duration_seconds) is not int or duration_seconds not in (900, 7200, 18000):
                raise ValueError("Unsupported remote support duration")
            # Fail closed on an old controller: never enable unbounded access.
            if self._client.status().get("timed_access_supported") is not True:
                raise RuntimeError("Install the updated remote support controller to use timed access")
            self._client.set_enabled(True, duration_seconds=duration_seconds)
        else:
            self._client.set_enabled(False)

    def get_password_status(self) -> dict:
        self._require_linux()
        if not self._password_management_available():
            return {"available": False, "configured": None, "unattended_enabled": None}
        return {"available": True, **self._password_client.get_password_status()}

    def _password_management_available(self) -> bool:
        status = self._client.status()
        return (status.get("enabled") is True and status.get("active") is True
                and status.get("timed_access_supported") is True)

    def _require_password_management(self) -> None:
        if not self._password_management_available():
            raise ValueError("Enable timed support before managing unattended access")

    def _verify_admin(self, admin_id: str, admin_password: str) -> None:
        self._require_linux()
        if self._authentication is None:
            raise RuntimeError("Platform administrator authentication is not configured")
        user = self._authentication.authenticate(admin_id, admin_password)
        if user is None or str(getattr(user.role, "value", user.role)) != self._admin_role_value:
            raise ValueError("Administrator credentials are invalid")

    def set_unattended_password(self, admin_id: str, admin_password: str, password: str) -> None:
        self._verify_admin(admin_id, admin_password)
        if not isinstance(password, str) or not 8 <= len(password) <= 64 or password.isspace():
            raise ValueError("Use a password with 8 to 64 characters")
        self._require_password_management()
        self._password_client.set_password(password)

    def remove_unattended_password(self, admin_id: str, admin_password: str) -> None:
        self._verify_admin(admin_id, admin_password)
        self._require_password_management()
        self._password_client.remove_password()
