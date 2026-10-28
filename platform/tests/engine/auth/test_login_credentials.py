"""Bearer-card revocation and persistent authentication limits on real SQLite."""
from dataclasses import replace
import hashlib
import sqlite3
import unittest
from unittest.mock import patch

from src.engine.auth.account_login_service import AccountLoginService
from src.engine.auth.authentication_throttle import AuthenticationLimits, AuthenticationThrottle
from src.engine.auth.login_token_service import LoginTokenService
from src.engine.auth.sqlite_account_store import SQLiteAccountStore, SQLiteAccountTransaction
from src.shared_contracts.accounts.authentication import LoginCredentials
from src.shared_contracts.accounts.commands import ChangePassword, ChangeRole, DeleteAccount
from src.shared_contracts.accounts.login_tokens import IssueLoginToken
from src.shared_contracts.authorization.errors import AuditPersistenceError, ErrorCode
from src.shared_contracts.authorization.results import Failure, Success
import tests.engine.auth.test_account_service as fixtures


class LoginCredentialTests(unittest.TestCase):
    def setUp(self):
        self.fixture = fixtures.AccountServiceTests()
        self.fixture.setUp()
        self.addCleanup(self.fixture.doCleanups)
        self.now = 1000.0
        self.throttle = AuthenticationThrottle(AuthenticationLimits(3, 6, 60), clock=lambda: self.now)
        self.tokens = LoginTokenService(self.fixture.store, self.fixture.session, self.fixture.policy,
                                        throttle=self.throttle)
        self.passwords = AccountLoginService(self.fixture.store, self.fixture.credentials, throttle=self.throttle)

    def issue(self, account=None):
        account = account or self.fixture.operator
        result = self.tokens.issue(IssueLoginToken(account.summary.account_id, account.summary.revision))
        self.assertIsInstance(result, Success)
        return result.value.payload

    def test_card_has_opaque_random_proof_only_digest_persisted_and_audited(self):
        token = self.issue()
        self.assertNotIn("initial-secret", token)
        self.assertNotIn(self.fixture.operator.summary.account_id, token)
        with sqlite3.connect(self.fixture.path) as connection:
            row = connection.execute("SELECT digest, credential_version FROM login_tokens").fetchone()
            self.assertEqual(row, (hashlib.sha256(token.encode()).hexdigest(), 1))
        result = self.tokens.authenticate(token)
        self.assertEqual(result.value.account, self.fixture.operator.summary)
        self.assertNotIn(token, repr(result))
        events = self.fixture.history(self.fixture.operator.summary.account_id)
        self.assertEqual([e.action_id for e in events], ["users.login", "users.issue_login_token"])
        self.assertNotIn(token, repr(events))

    def test_card_replacement_revokes_previous_card(self):
        previous = self.issue()
        current = self.issue()
        self.assertNotEqual(previous, current)
        self.assertEqual(self.tokens.authenticate(previous).error.code, ErrorCode.INVALID_PROOF)
        self.assertIsInstance(self.tokens.authenticate(current), Success)

    def test_admin_can_issue_own_and_operator_cards_but_no_other_privileged_cards(self):
        self.issue(self.fixture.admin)
        self.issue(self.fixture.operator)
        for account in (self.fixture.other_admin, self.fixture.manufacturer):
            result = self.tokens.issue(IssueLoginToken(account.summary.account_id, 1))
            self.assertEqual(result.error.code, ErrorCode.ACCESS_DENIED)
        self.fixture.login(self.fixture.operator)
        result = self.tokens.issue(IssueLoginToken(self.fixture.operator.summary.account_id, 1))
        self.assertEqual(result.error.code, ErrorCode.ACCESS_DENIED)

    def test_manufacturer_can_issue_registered_account_cards(self):
        self.fixture.login(self.fixture.manufacturer)
        for account in (self.fixture.admin, self.fixture.operator, self.fixture.manufacturer):
            self.assertIsInstance(self.tokens.authenticate(self.issue(account)), Success)

    def test_password_change_revokes_existing_card(self):
        token = self.issue()
        account_id = self.fixture.operator.summary.account_id
        self.assertIsInstance(self.fixture.service.change_password(ChangePassword(account_id, 1, "new-password")), Success)
        self.assertEqual(self.tokens.authenticate(token).error.code, ErrorCode.INVALID_PROOF)
        updated = self.fixture.get(self.fixture.operator)
        self.assertIsInstance(self.tokens.authenticate(self.issue(updated)), Success)

    def test_role_change_revokes_existing_card(self):
        token = self.issue()
        self.fixture.login(self.fixture.manufacturer)
        result = self.fixture.service.change_role(ChangeRole(self.fixture.operator.summary.account_id, 1,
                                                              "Admin", "fresh-password"))
        self.assertIsInstance(result, Success)
        self.assertEqual(self.tokens.authenticate(token).error.code, ErrorCode.INVALID_PROOF)

    def test_disabled_account_card_cannot_log_in_or_be_reissued(self):
        token = self.issue()
        account = self.fixture.operator
        with self.fixture.store.transaction() as transaction:
            transaction.replace(replace(account, summary=replace(account.summary, enabled=False)))
        self.assertEqual(self.tokens.authenticate(token).error.code, ErrorCode.INVALID_PROOF)
        self.assertEqual(self.tokens.issue(IssueLoginToken(account.summary.account_id, 1)).error.code,
                         ErrorCode.POLICY_VIOLATION)

    def test_deleted_recreated_login_cannot_use_old_card(self):
        token = self.issue()
        self.fixture.service.delete_user(DeleteAccount(self.fixture.operator.summary.account_id, 1))
        self.fixture.seed(self.fixture.operator.summary.login_id, "Operator")
        self.assertEqual(self.tokens.authenticate(token).error.code, ErrorCode.INVALID_PROOF)

    def test_plaintext_password_qr_formats_are_rejected(self):
        for payload in ("id = 3\npassword = initial-secret", "3:initial-secret", "", None,
                        "robot-login-v1:initial-secret"):
            self.assertEqual(self.tokens.authenticate(payload).error.code, ErrorCode.INVALID_PROOF)

    def test_stale_card_request_does_not_revoke_current_card(self):
        token = self.issue()
        result = self.tokens.issue(IssueLoginToken(self.fixture.operator.summary.account_id, 999))
        self.assertEqual(result.error.code, ErrorCode.CONFLICT)
        self.assertIsInstance(self.tokens.authenticate(token), Success)

    def test_audit_failure_rolls_back_replacement_and_never_returns_card(self):
        token = self.issue()
        with patch.object(SQLiteAccountTransaction, "append_event", side_effect=AuditPersistenceError):
            with self.assertRaises(AuditPersistenceError):
                self.tokens.issue(IssueLoginToken(self.fixture.operator.summary.account_id, 1))
            with self.assertRaises(AuditPersistenceError):
                self.tokens.authenticate(token)
        self.assertIsInstance(self.tokens.authenticate(token), Success)

    def test_password_limit_persists_across_service_and_store_reopen_and_expires(self):
        for _ in range(3):
            self.assertEqual(self.passwords.login(LoginCredentials("1", "wrong")).error.code, ErrorCode.INVALID_PROOF)
        reopened = AccountLoginService(SQLiteAccountStore(self.fixture.path), self.fixture.credentials,
                                        throttle=self.throttle)
        self.assertEqual(reopened.login(LoginCredentials("1", "initial-secret")).error.code, ErrorCode.RATE_LIMITED)
        self.now += 60
        self.assertIsInstance(reopened.login(LoginCredentials("1", "initial-secret")), Success)

    def test_success_resets_identifier_counter_but_keeps_global_failure_budget(self):
        for _ in range(2):
            self.passwords.login(LoginCredentials("1", "wrong"))
        self.assertIsInstance(self.passwords.login(LoginCredentials("1", "initial-secret")), Success)
        for _ in range(2):
            self.passwords.login(LoginCredentials("1", "wrong"))
        self.assertIsInstance(self.passwords.login(LoginCredentials("1", "initial-secret")), Success)
        for login in ("unknown-1", "unknown-2"):
            self.passwords.login(LoginCredentials(login, "wrong"))
        self.assertEqual(self.passwords.login(LoginCredentials("1", "initial-secret")).error.code, ErrorCode.RATE_LIMITED)

    def test_random_identifiers_and_cards_share_global_failure_limit(self):
        for number in range(3):
            self.passwords.login(LoginCredentials(str(100 + number), "wrong"))
            self.tokens.authenticate("robot-login-v1:" + str(number) * 43)
        self.assertEqual(self.passwords.login(LoginCredentials("1", "initial-secret")).error.code, ErrorCode.RATE_LIMITED)
        self.assertEqual(self.tokens.authenticate(self.issue()).error.code, ErrorCode.RATE_LIMITED)

    def test_recovery_attempts_have_independent_limits(self):
        from src.engine.auth.account_store import RecoveryAttempts
        with self.fixture.store.transaction() as transaction:
            transaction.set_recovery_attempts("global", RecoveryAttempts(1000, self.now))
        self.assertIsInstance(self.passwords.login(LoginCredentials("1", "initial-secret")), Success)

    def test_repeated_invalid_card_is_throttled(self):
        token = "robot-login-v1:" + "x" * 43
        for _ in range(3):
            self.assertEqual(self.tokens.authenticate(token).error.code, ErrorCode.INVALID_PROOF)
        self.assertEqual(self.tokens.authenticate(token).error.code, ErrorCode.RATE_LIMITED)
