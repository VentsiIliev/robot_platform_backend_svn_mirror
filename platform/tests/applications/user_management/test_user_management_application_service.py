import unittest
from unittest.mock import MagicMock

from src.applications.user_management.service.user_management_application_service import UserManagementApplicationService
from src.applications.user_management.service.i_user_management_service import (
    NewUser, EditUser, PasswordChange, RoleChange, UserFailure,
)
from src.engine.auth.account_principal import AccountPrincipal
from src.engine.auth.user_session import UserSession
from src.shared_contracts.accounts.records import AccountSummary, AccountChange
from src.shared_contracts.accounts.commands import CreateAccount, EditProfile, ChangePassword, ChangeRole, DeleteAccount, RevealedPassword
from src.shared_contracts.accounts.recovery import RecoveryCodes
from src.shared_contracts.authorization.access import AccessSnapshot, AccessDecision, DenialReason
from src.shared_contracts.authorization.errors import StorageIntegrityError, ErrorCode, ServiceError
from src.shared_contracts.authorization.results import Success, Failure
from src.shared_contracts.authorization.permissions import PermissionSnapshot, ApplicationGrant, UpdateAppPermissions


class UserManagementAdapterTests(unittest.TestCase):
    def setUp(self):
        self.accounts, self.access = MagicMock(), MagicMock()
        self.tokens, self.recovery, self.permissions, self.history = (MagicMock() for _ in range(4))
        self.session = UserSession()
        self.admin = AccountSummary("admin-id", "1", "First", "Admin", "Admin", "", True, 1, None, None, None, None)
        self.operator = AccountSummary("operator-id", "2", "First", "Operator", "Operator", "", True, 1, None, None, None, None)
        self.session.login(AccountPrincipal(self.admin, 1))
        self.accounts.list_users.return_value = Success((self.admin, self.operator))
        self.service = UserManagementApplicationService(accounts=self.accounts, access=self.access,
            tokens=self.tokens, recovery=self.recovery, permissions=self.permissions, history=self.history,
            session=self.session)

    def test_user_page_contains_safe_summaries_and_trusted_actor(self):
        page = self.service.load_users().value
        self.assertEqual((page.actor_id, page.actor_role), ("admin-id", "Admin"))
        self.assertEqual(page.session_revision, self.session.snapshot().revision)
        self.assertTrue(all(not hasattr(row, "password") for row in page.users))

    def test_user_page_cannot_cross_session_change(self):
        def read_then_logout():
            self.session.logout()
            return Success((self.admin, self.operator))
        self.accounts.list_users.side_effect = read_then_logout
        self.assertEqual(self.service.load_users().error.code, "conflict")

    def test_create_profile_password_role_and_delete_use_separate_commands(self):
        self.accounts.create_user.return_value = Success(self.operator)
        self.service.create(NewUser("2", "First", "Operator", "Operator", "secret"))
        self.accounts.create_user.assert_called_once_with(CreateAccount("2", "First", "Operator", "Operator", "secret", ""))
        self.accounts.edit_profile.return_value = Success(AccountChange(self.operator, True))
        self.service.edit(EditUser("operator-id", 1, "Changed", "Operator", ""))
        self.accounts.edit_profile.assert_called_once_with(EditProfile("operator-id", 1, "Changed", "Operator", ""))
        self.accounts.change_password.return_value = Success(self.operator)
        self.service.change_password(PasswordChange("operator-id", 1, "new-secret", "current"))
        self.accounts.change_password.assert_called_once_with(ChangePassword("operator-id", 1, "new-secret", "current"))
        self.accounts.change_role.return_value = Success(AccountChange(self.operator, True))
        self.service.change_role(RoleChange("operator-id", 1, "Admin", "fresh-secret"))
        self.accounts.change_role.assert_called_once_with(ChangeRole("operator-id", 1, "Admin", "fresh-secret"))
        self.accounts.delete_user.return_value = Success(None)
        self.service.delete("operator-id", 1)
        self.accounts.delete_user.assert_called_once_with(DeleteAccount("operator-id", 1))

    def test_expected_failure_preserves_code_and_reference(self):
        self.accounts.list_users.return_value = Failure(ServiceError(ErrorCode.ACCESS_DENIED, "safe", "reference"))
        result = self.service.load_users()
        self.assertEqual((result.error.code, result.error.reference), ("access_denied", "reference"))

    def test_storage_failure_has_no_exception_details(self):
        self.accounts.list_users.side_effect = StorageIntegrityError(correlation_id="reference")
        result = self.service.load_users()
        self.assertEqual((result.error.code, result.error.reference), ("integrity", "reference"))

    def test_revealed_and_recovery_values_have_redacted_representations(self):
        self.accounts.reveal_operator_password.return_value = Success(RevealedPassword("operator-secret"))
        self.recovery.generate_codes.return_value = Success(RecoveryCodes("admin-id", ("code-one", "code-two")))
        reveal = self.service.reveal("operator-id")
        codes = self.service.generate_recovery_codes("current")
        self.assertEqual(reveal.value.text, "operator-secret")
        self.assertNotIn("operator-secret", repr(reveal))
        self.assertEqual(codes.value.text, "code-one\ncode-two")
        self.assertNotIn("code-one", repr(codes))

    def test_presentation_never_offers_privileged_password_reveal_even_with_global_grant(self):
        def allow_all(requests):
            return Success(AccessSnapshot(self.session.snapshot().revision, 1, requests,
                tuple(AccessDecision(True, True, DenialReason.ALLOWED) for _ in requests)))
        self.access.evaluate.side_effect = allow_all
        for target, allowed in (("admin-id", False), ("operator-id", True)):
            controls = {control.key: control for control in self.service.access(target).value.controls}
            self.assertEqual(controls["reveal"].allowed, allowed)

    def test_permissions_editor_keeps_exact_revision_and_immutable_grants(self):
        snapshot = PermissionSnapshot(7, (ApplicationGrant("demo", ("Admin", "Manufacturer"), ("Admin", "Operator")),))
        self.permissions.read_permissions.return_value = Success(snapshot)
        self.permissions.update_permissions.return_value = Success(snapshot)
        page = self.service.permissions().value
        self.assertEqual(page.locked, (("demo", "Manufacturer"),))
        self.service.set_permission("demo", ("Manufacturer",), page.revision)
        self.permissions.update_permissions.assert_called_once_with(UpdateAppPermissions("demo", ("Manufacturer",), 7))

    def test_plaintext_package_api_is_removed(self):
        self.assertFalse(hasattr(self.service, "send_access_package"))
        self.assertFalse(hasattr(self.service, "generate_qr"))

