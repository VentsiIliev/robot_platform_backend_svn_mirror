from enum import Enum
from src.applications.login.i_login_application_service import (
    ILoginApplicationService, LoginSuccess, RecoveryCodeDisplay,
)


class _StubUser:
    @property
    def user_id(self) -> str:
        return "0"

    @property
    def role(self) -> Enum:
        class _R(Enum):
            ADMIN = "Admin"
        return _R.ADMIN


class StubLoginApplicationService(ILoginApplicationService):
    """Always authenticates successfully. Used in tests and standalone runners."""

    def get_connection_information(self) -> dict:
        return {
            "hostname": "robot-demo",
            "username": "operator",
            "addresses": [{"interface": "eth0", "address": "192.168.222.20"}],
            "rustdesk_id": "123456789",
        }

    def authenticate(self, user_id: str, password: str):
        return LoginSuccess(_StubUser())

    def authenticate_qr(self, qr_payload: str):
        return LoginSuccess(_StubUser())

    def scan_qr(self):
        return LoginSuccess(None)

    def move_to_login_pos(self) -> None:
        pass

    def is_first_run(self):
        return LoginSuccess(False)

    def create_first_admin(self, command):
        return LoginSuccess(None)

    def recover_admin(self, command):
        return LoginSuccess(RecoveryCodeDisplay(("DEMO-CODE-NOT-VALID",)))
