from typing import Callable, TypeVar

from src.applications.login.connection_information_reader import ConnectionInformationReader
from src.applications.login.i_login_application_service import (
    AdminRecovery, AdminSetup, ILoginApplicationService, LoginError, LoginErrorCode,
    LoginFailure, LoginResult, LoginSuccess, LoginUser, RecoveryCodeDisplay,
)
from src.applications.login.i_qr_scanner import IQrScanner
from src.engine.auth.account_principal import AccountPrincipal
from src.engine.auth.i_account_login_service import IAccountLoginService
from src.engine.auth.i_admin_commissioning_service import IAdminCommissioningService
from src.engine.auth.i_login_token_service import ILoginTokenService
from src.engine.auth.i_recovery_service import IRecoveryService
from src.engine.robot.interfaces.i_robot_service import IRobotService
from src.shared_contracts.accounts.authentication import LoginCredentials
from src.shared_contracts.accounts.commissioning import CreateFirstAdmin
from src.shared_contracts.accounts.recovery import RecoverAdminAccount
from src.shared_contracts.authorization.errors import ErrorCode, ServiceException
from src.shared_contracts.authorization.results import Failure, Result

T = TypeVar("T")
U = TypeVar("U")


class LoginApplicationService(ILoginApplicationService):
    def __init__(self, *, login: IAccountLoginService, tokens: ILoginTokenService,
                 commissioning: IAdminCommissioningService, recovery: IRecoveryService,
                 robot_service: IRobotService | None = None, qr_scanner: IQrScanner | None = None,
                 login_position: list[float] | None = None) -> None:
        self._login, self._tokens = login, tokens
        self._commissioning, self._recovery = commissioning, recovery
        self._robot, self._scanner, self._login_pos = robot_service, qr_scanner, login_position
        self._connection_information = ConnectionInformationReader()

    def get_connection_information(self) -> dict:
        return self._connection_information.read()

    def authenticate(self, user_id: str, password: str) -> LoginResult[LoginUser]:
        return self._call(lambda: self._login.login(LoginCredentials(user_id, password)), self._principal)

    def authenticate_qr(self, payload: str) -> LoginResult[LoginUser]:
        return self._call(lambda: self._tokens.authenticate(payload), self._principal)

    def scan_qr(self) -> LoginResult[str | None]:
        if self._scanner is None:
            return LoginSuccess(None)
        try:
            return LoginSuccess(self._scanner.scan())
        except Exception:
            # Camera drivers need not implement the account exception hierarchy.
            return LoginFailure(LoginError(LoginErrorCode.UNAVAILABLE))

    def move_to_login_pos(self) -> None:
        if self._robot is not None and self._login_pos is not None:
            self._robot.move_ptp(self._login_pos, 0, 0, 20.0, 20.0)

    def is_first_run(self) -> LoginResult[bool]:
        try:
            return LoginSuccess(self._commissioning.status().required)
        except ServiceException as exc:
            return self._error(exc.error)

    def create_first_admin(self, command: AdminSetup) -> LoginResult[None]:
        if not isinstance(command.login_id, str) or not command.login_id.isnumeric():
            return LoginFailure(LoginError(LoginErrorCode.INVALID_INPUT))
        return self._call(lambda: self._commissioning.create_first_admin(CreateFirstAdmin(
            command.login_id, command.first_name, command.last_name, command.password)), lambda _account: None)

    def recover_admin(self, command: AdminRecovery) -> LoginResult[RecoveryCodeDisplay]:
        return self._call(lambda: self._recovery.recover_admin(RecoverAdminAccount(
            command.login_id, command.code, command.new_password)), lambda codes: RecoveryCodeDisplay(codes.codes))

    @staticmethod
    def _principal(identity):
        return AccountPrincipal(identity.account, identity.credential_version)

    @classmethod
    def _call(cls, operation: Callable[[], Result[T]], convert: Callable[[T], U]) -> LoginResult[U]:
        try:
            result = operation()
            if isinstance(result, Failure):
                return cls._error(result.error)
            return LoginSuccess(convert(result.value))
        except ServiceException as exc:
            return cls._error(exc.error)

    @staticmethod
    def _error(error) -> LoginFailure:
        codes = {
            ErrorCode.INVALID_INPUT: LoginErrorCode.INVALID_INPUT,
            ErrorCode.INVALID_PROOF: LoginErrorCode.INVALID_PROOF,
            ErrorCode.RATE_LIMITED: LoginErrorCode.RATE_LIMITED,
            ErrorCode.BUSY: LoginErrorCode.BUSY,
            ErrorCode.POLICY_VIOLATION: LoginErrorCode.SETUP_CLOSED,
            ErrorCode.ALREADY_EXISTS: LoginErrorCode.ALREADY_EXISTS,
        }
        return LoginFailure(LoginError(codes.get(error.code, LoginErrorCode.UNAVAILABLE), error.correlation_id))
