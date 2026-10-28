import unittest
from unittest.mock import MagicMock

from src.applications.login.i_login_application_service import (
    AdminSetup, AdminRecovery, LoginFailure, LoginErrorCode, LoginSuccess,
)
from src.applications.login.login_application_service import LoginApplicationService
from src.engine.auth.i_account_login_service import IAccountLoginService
from src.engine.auth.i_admin_commissioning_service import IAdminCommissioningService
from src.engine.auth.i_login_token_service import ILoginTokenService
from src.engine.auth.i_recovery_service import IRecoveryService
from src.shared_contracts.accounts.authentication import AccountIdentity, LoginCredentials
from src.shared_contracts.accounts.commissioning import AdminSetupStatus, CreateFirstAdmin
from src.shared_contracts.accounts.records import AccountSummary
from src.shared_contracts.accounts.recovery import RecoveryCodes, RecoverAdminAccount
from src.shared_contracts.authorization.errors import ErrorCode, ServiceError, StorageIntegrityError
from src.shared_contracts.authorization.results import Success, Failure


class LoginApplicationAdapterTests(unittest.TestCase):
    def setUp(self):
        self.login = MagicMock(spec=IAccountLoginService)
        self.tokens = MagicMock(spec=ILoginTokenService)
        self.setup = MagicMock(spec=IAdminCommissioningService)
        self.recovery = MagicMock(spec=IRecoveryService)
        self.service = LoginApplicationService(login=self.login, tokens=self.tokens,
                                               commissioning=self.setup, recovery=self.recovery)
        self.account = AccountSummary("uuid", "42", "First", "Admin", "Admin", "", True, 1, None, None, None, None)
        self.identity = AccountIdentity(self.account, 7)

    def test_login_maps_safe_identity_into_platform_principal(self):
        self.login.login.return_value = Success(self.identity)
        result = self.service.authenticate("42", " secret ")
        self.login.login.assert_called_once_with(LoginCredentials("42", " secret "))
        self.assertEqual((result.value.user_id, result.value.account_id, result.value.credential_version), ("42", "uuid", 7))
        self.assertEqual(result.value.record.password, "")
        self.assertNotIn(" secret ", repr(result))

    def test_qr_uses_only_token_service(self):
        self.tokens.authenticate.return_value = Success(self.identity)
        self.assertEqual(self.service.authenticate_qr("opaque-card").value.account_id, "uuid")
        self.tokens.authenticate.assert_called_once_with("opaque-card")
        self.login.login.assert_not_called()

    def test_attempt_limit_and_invalid_proof_remain_typed(self):
        for engine, local in ((ErrorCode.RATE_LIMITED, LoginErrorCode.RATE_LIMITED),
                              (ErrorCode.INVALID_PROOF, LoginErrorCode.INVALID_PROOF)):
            self.login.login.return_value = Failure(ServiceError(engine, "safe.key", "reference"))
            result = self.service.authenticate("42", "wrong")
            self.assertEqual((result.error.code, result.error.reference), (local, "reference"))

    def test_storage_failure_is_safe_and_does_not_become_first_run(self):
        self.setup.status.side_effect = StorageIntegrityError(correlation_id="reference")
        result = self.service.is_first_run()
        self.assertIsInstance(result, LoginFailure)
        self.assertEqual(result.error.code, LoginErrorCode.UNAVAILABLE)

    def test_setup_status_is_independent_of_account_count(self):
        self.setup.status.return_value = AdminSetupStatus(True)
        self.assertEqual(self.service.is_first_run(), LoginSuccess(True))

    def test_first_admin_uses_fixed_backend_setup_command(self):
        self.setup.create_first_admin.return_value = Success(self.account)
        result = self.service.create_first_admin(AdminSetup("42", "First", "Admin", "new-secret"))
        self.assertEqual(result, LoginSuccess(None))
        self.setup.create_first_admin.assert_called_once_with(CreateFirstAdmin("42", "First", "Admin", "new-secret"))

    def test_recovery_returns_redacted_replacement_codes_and_does_not_authenticate(self):
        self.recovery.recover_admin.return_value = Success(RecoveryCodes("uuid", ("one-time-secret",)))
        result = self.service.recover_admin(AdminRecovery("42", "old-code", "new-password"))
        self.recovery.recover_admin.assert_called_once_with(RecoverAdminAccount("42", "old-code", "new-password"))
        self.assertEqual(result.value.codes, ("one-time-secret",))
        self.assertNotIn("one-time-secret", repr(result))
        self.login.login.assert_not_called()

    def test_scanning_is_optional_and_never_decodes_passwords(self):
        self.assertEqual(self.service.scan_qr(), LoginSuccess(None))
        scanner = MagicMock()
        scanner.scan.return_value = "opaque:card"
        self.service._scanner = scanner
        self.assertEqual(self.service.scan_qr(), LoginSuccess("opaque:card"))
        scanner.scan.side_effect = RuntimeError("unsafe driver details")
        result = self.service.scan_qr()
        self.assertEqual(result.error.code, LoginErrorCode.UNAVAILABLE)
        self.assertNotIn("unsafe", repr(result))

    def test_optional_positioning_preserves_existing_motion_contract(self):
        self.assertIsNone(self.service.move_to_login_pos())
        robot = MagicMock()
        self.service._robot, self.service._login_pos = robot, [1, 2, 3, 4, 5, 6]
        self.service.move_to_login_pos()
        robot.move_ptp.assert_called_once_with([1, 2, 3, 4, 5, 6], 0, 0, 20.0, 20.0)
