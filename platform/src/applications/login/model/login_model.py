from src.applications.login.i_login_application_service import (
    AdminRecovery, AdminSetup, ILoginApplicationService, LoginFailure,
)


class LoginModel:
    def __init__(self, service: ILoginApplicationService) -> None:
        self._svc = service

    def get_connection_information(self) -> dict:
        return self._svc.get_connection_information()

    def is_first_run(self):
        return self._svc.is_first_run()

    def authenticate(self, user_id: str, password: str):
        return self._svc.authenticate(user_id.strip(), password)

    def poll_qr_login(self):
        result = self._svc.scan_qr()
        if isinstance(result, LoginFailure) or result.value is None:
            return result
        return self._svc.authenticate_qr(result.value)

    def move_to_login_pos(self) -> None:
        self._svc.move_to_login_pos()

    def create_and_login(self, command: AdminSetup):
        result = self._svc.create_first_admin(command)
        return result if isinstance(result, LoginFailure) else self.authenticate(command.login_id, command.password)

    def recover_admin(self, command: AdminRecovery):
        return self._svc.recover_admin(command)

    @staticmethod
    def validate_login_input(user_id: str, password: str) -> str | None:
        if not user_id.strip():
            return "User id is required."
        if not user_id.strip().isnumeric():
            return "User id must be numeric."
        if not password:
            return "Password is required."
        return None
