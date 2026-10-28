"""Account/login adapter integration on temporary SQLite, without hardware or real users."""
import unittest

from src.applications.login.i_login_application_service import AdminRecovery, LoginFailure
from src.applications.login.login_application_service import LoginApplicationService
from src.applications.user_management.service.i_user_management_service import (
    NewUser, EditUser, PasswordChange, UserFailure,
)
from src.applications.user_management.service.user_management_application_service import UserManagementApplicationService
from src.engine.auth.account_installation import PreparedAccountInstallation
from src.engine.auth.account_runtime import AccountRuntime
from src.shared_contracts.accounts.authentication import LoginCredentials
from src.shared_contracts.authorization.results import Success
import tests.engine.auth.test_account_service as fixtures
from tests.engine.auth.test_account_runtime import APPLICATIONS


class AccountApplicationFlowTests(unittest.TestCase):
    def setUp(self):
        self.fixture = fixtures.AccountServiceTests()
        self.fixture.setUp()
        self.addCleanup(self.fixture.doCleanups)
        self.runtime = AccountRuntime(PreparedAccountInstallation("fixture", self.fixture.store, self.fixture.credentials),
                                      self.fixture.session, APPLICATIONS)
        r = self.runtime
        self.login = LoginApplicationService(login=r.login, tokens=r.login_tokens, commissioning=r.commissioning,
                                             recovery=r.recovery)
        self.users = UserManagementApplicationService(accounts=r.accounts, access=r.access, tokens=r.login_tokens,
            recovery=r.recovery, permissions=r.permissions, history=r.history, session=r.session)

    def test_login_and_account_management_use_same_verified_identity(self):
        self.fixture.session.logout()
        self.assertIsInstance(self.users.load_users(), UserFailure)
        authenticated = self.login.authenticate("1", "initial-secret")
        self.fixture.session.login(authenticated.value)
        page = self.users.load_users().value
        created = self.users.create(NewUser("5", "New", "Operator", "Operator", "new-secret")).value
        self.assertEqual(created.created_by, page.actor_id)
        self.assertNotIn("new-secret", repr(self.users.load_users()))
        edited = self.users.edit(EditUser(created.account_id, created.revision, "Changed", "Operator", "")).value
        self.assertEqual((edited.updated_by, edited.revision), (page.actor_id, created.revision + 1))

    def test_admin_cannot_bypass_ui_to_manage_other_admin_or_permissions(self):
        other = self.fixture.other_admin.summary
        self.assertIsInstance(self.users.change_password(PasswordChange(other.account_id, 1, "replacement")), UserFailure)
        self.assertIsInstance(self.users.permissions(), UserFailure)
        self.assertIsInstance(self.users.set_permission("dashboard", ("Operator",), 1), UserFailure)
        self.assertIsInstance(self.users.reveal(other.account_id), UserFailure)

    def test_manufacturer_permission_changes_take_effect_in_runtime_navigation(self):
        self.fixture.login(self.fixture.manufacturer)
        page = self.users.permissions().value
        result = self.users.set_permission("dashboard", ("Admin",), page.revision)
        self.assertNotIsInstance(result, UserFailure)
        self.fixture.login(self.fixture.operator)
        self.assertFalse(self.runtime.authorization.can_access(self.fixture.session.current_user, "dashboard"))
        self.assertIsInstance(self.users.load_users(), UserFailure)

    def test_one_time_recovery_flow_returns_replacements_and_rejects_old_password_and_code(self):
        code = self.users.generate_recovery_codes("initial-secret").value.text.splitlines()[0]
        self.fixture.session.logout()
        recovered = self.login.recover_admin(AdminRecovery("1", code, "replacement-secret"))
        self.assertEqual(len(recovered.value.codes), 8)
        self.assertNotIn(recovered.value.codes[0], repr(recovered))
        self.assertFalse(self.fixture.session.is_authenticated())
        self.assertIsInstance(self.login.authenticate("1", "initial-secret"), LoginFailure)
        self.assertNotIsInstance(self.login.authenticate("1", "replacement-secret"), LoginFailure)
        self.assertIsInstance(self.login.recover_admin(AdminRecovery("1", code, "another-secret")), LoginFailure)

    def test_generated_qr_contains_token_and_is_usable_without_plaintext_password(self):
        import cv2
        import numpy as np
        target = self.fixture.operator.summary
        png = self.users.issue_qr(target.account_id, target.revision).value.png
        image = cv2.imdecode(np.frombuffer(png, dtype=np.uint8), cv2.IMREAD_GRAYSCALE)
        token, _points, _straight = cv2.QRCodeDetector().detectAndDecode(image)
        self.assertTrue(token.startswith("robot-login-v1:"))
        self.assertNotIn("initial-secret", token)
        self.assertEqual(self.login.authenticate_qr(token).value.account_id, target.account_id)
        self.users.change_password(PasswordChange(target.account_id, target.revision, "new-secret"))
        self.assertIsInstance(self.login.authenticate_qr(token), LoginFailure)

    def test_admin_can_read_own_and_operator_history_but_not_other_privileged_accounts(self):
        target = self.fixture.operator.summary
        self.users.change_password(PasswordChange(target.account_id, 1, "operator-secret"))
        self.assertTrue(any(row.password_changed for row in self.users.history(target.account_id).value))
        self.assertNotIsInstance(self.users.history(self.fixture.admin.summary.account_id), UserFailure)
        for account in (self.fixture.other_admin, self.fixture.manufacturer):
            with self.subTest(target=account.summary.role):
                self.assertIsInstance(self.users.history(account.summary.account_id), UserFailure)
        self.fixture.login(self.fixture.manufacturer)
        history = self.users.history(target.account_id).value
        self.assertTrue(any(row.password_changed for row in history))
        self.assertNotIn("operator-secret", repr(history))

    def test_history_button_access_matches_target_scope(self):
        for target, permitted in ((None, False), (self.fixture.admin, True), (self.fixture.operator, True),
                                  (self.fixture.other_admin, False), (self.fixture.manufacturer, False)):
            identity = target.summary.account_id if target else None
            with self.subTest(target=identity):
                controls = {control.key: control for control in self.users.access(identity).value.controls}
                self.assertTrue(controls["history"].role_eligible)
                self.assertEqual(controls["history"].allowed, permitted)
        self.fixture.login(self.fixture.operator)
        self.assertIsInstance(self.users.history(self.fixture.operator.summary.account_id), UserFailure)
