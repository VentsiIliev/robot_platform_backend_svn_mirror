from .i_remote_support_service import IRemoteSupportService
import time


class StubRemoteSupportService(IRemoteSupportService):
    def __init__(self):
        self.enabled = False
        self.expires_at = 0
        self.duration_seconds = 900
        self._password = ""

    def get_remote_support_status(self) -> dict:
        if time.monotonic() >= self.expires_at:
            self.enabled = False
        return {"enabled": self.enabled, "active": self.enabled,
                "service_state": "active" if self.enabled else "inactive",
                "timed_access_supported": True, "duration_seconds": self.duration_seconds,
                "remaining_seconds": max(0, int(self.expires_at - time.monotonic())) if self.enabled else 0}

    def set_remote_support_enabled(self, enabled: bool, duration_seconds: int = 900) -> None:
        self.duration_seconds = duration_seconds
        self.expires_at = time.monotonic() + duration_seconds
        self.enabled = bool(enabled)

    def get_password_status(self) -> dict:
        return {"available": True, "configured": bool(self._password), "unattended_enabled": bool(self._password)}

    def set_unattended_password(self, admin_id: str, admin_password: str, password: str) -> None:
        self._verify_admin(admin_id, admin_password)
        if not 8 <= len(password) <= 64:
            raise ValueError("Use a password with 8 to 64 characters")
        self._password = password

    def remove_unattended_password(self, admin_id: str, admin_password: str) -> None:
        self._verify_admin(admin_id, admin_password)
        self._password = ""

    @staticmethod
    def _verify_admin(admin_id: str, admin_password: str) -> None:
        if admin_id != "admin" or admin_password != "admin":
            raise ValueError("Administrator credentials are invalid")
