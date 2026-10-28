import unittest
from unittest.mock import MagicMock

from src.applications.login.i_login_application_service import (
    AdminSetup, AdminRecovery, ILoginApplicationService, LoginSuccess, LoginFailure, LoginError, LoginErrorCode,
)
from src.applications.login.model.login_model import LoginModel
from src.applications.login.stub_login_application_service import StubLoginApplicationService


class LoginModelTests(unittest.TestCase):
    def setUp(self):
        self.service = MagicMock(spec=ILoginApplicationService)
        self.model = LoginModel(self.service)

    def test_password_whitespace_is_preserved_and_identifier_is_trimmed(self):
        expected = LoginSuccess(object())
        self.service.authenticate.return_value = expected
        self.assertIs(self.model.authenticate(" 42 ", " secret "), expected)
        self.service.authenticate.assert_called_once_with("42", " secret ")

    def test_validation_rejects_empty_id_non_numeric_id_and_empty_password(self):
        for uid, password in (("", "secret"), ("  ", "secret"), ("name", "secret"), ("42", "")):
            self.assertIsNotNone(self.model.validate_login_input(uid, password))
        self.assertIsNone(self.model.validate_login_input(" 42 ", " secret "))

    def test_no_card_scan_does_not_attempt_authentication(self):
        self.service.scan_qr.return_value = LoginSuccess(None)
        self.assertEqual(self.model.poll_qr_login(), LoginSuccess(None))
        self.service.authenticate_qr.assert_not_called()

    def test_scanned_card_uses_token_authentication_without_password_parsing(self):
        self.service.scan_qr.return_value = LoginSuccess("opaque:payload")
        self.service.authenticate_qr.return_value = LoginSuccess(object())
        self.model.poll_qr_login()
        self.service.authenticate_qr.assert_called_once_with("opaque:payload")
        self.service.authenticate.assert_not_called()

    def test_scanner_failure_is_not_converted_into_a_login_attempt(self):
        failure = LoginFailure(LoginError(LoginErrorCode.UNAVAILABLE))
        self.service.scan_qr.return_value = failure
        self.assertIs(self.model.poll_qr_login(), failure)
        self.service.authenticate_qr.assert_not_called()

    def test_successful_commissioning_authenticates_through_normal_login(self):
        command = AdminSetup("42", "First", "Admin", "secret")
        self.service.create_first_admin.return_value = LoginSuccess(None)
        result = LoginSuccess(object())
        self.service.authenticate.return_value = result
        self.assertIs(self.model.create_and_login(command), result)
        self.service.create_first_admin.assert_called_once_with(command)
        self.service.authenticate.assert_called_once_with("42", "secret")

    def test_closed_commissioning_never_attempts_login(self):
        failure = LoginFailure(LoginError(LoginErrorCode.SETUP_CLOSED))
        self.service.create_first_admin.return_value = failure
        self.assertIs(self.model.create_and_login(AdminSetup("42", "F", "L", "secret")), failure)
        self.service.authenticate.assert_not_called()

    def test_recovery_returns_codes_without_logging_in(self):
        command = AdminRecovery("42", "saved-code", "replacement")
        result = LoginSuccess(object())
        self.service.recover_admin.return_value = result
        self.assertIs(self.model.recover_admin(command), result)
        self.service.authenticate.assert_not_called()

    def test_stub_honours_typed_contract(self):
        stub = StubLoginApplicationService()
        self.assertIsInstance(stub.authenticate("1", "demo"), LoginSuccess)
        self.assertFalse(stub.is_first_run().value)
        self.assertIsNone(stub.scan_qr().value)
