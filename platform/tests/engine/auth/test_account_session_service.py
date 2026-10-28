from dataclasses import replace
import unittest
from unittest.mock import patch

from src.engine.auth.account_access_context import AccountAccessContext
from src.engine.auth.account_session_service import AccountSessionService
from src.shared_contracts.accounts.commands import ChangePassword, DeleteAccount
from src.shared_contracts.authorization.errors import ErrorCode
import tests.engine.auth.test_account_service as fixtures


class AccountSessionValidationTests(unittest.TestCase):
    def setUp(self):
        self.fixture = fixtures.AccountServiceTests()
        self.fixture.setUp()
        self.addCleanup(self.fixture.doCleanups)
        self.contexts = AccountAccessContext(self.fixture.store, self.fixture.session)
        self.service = AccountSessionService(self.contexts, self.fixture.session)

    def test_current_claims_validate_without_editing_metadata_or_writing_audit(self):
        result = self.service.status().value
        self.assertTrue(result.authenticated)
        self.assertEqual(result.session_revision, self.fixture.session.snapshot().revision)
        self.assertEqual(self.fixture.get(self.fixture.admin), self.fixture.admin)
        self.assertEqual(self.fixture.history(self.fixture.admin.summary.account_id), ())

    def test_password_change_invalidates_claims_without_needing_explicit_logout(self):
        self.fixture.service.change_password(ChangePassword(self.fixture.admin.summary.account_id, 1,
                                                            "replacement", "initial-secret"))
        self.assertTrue(self.fixture.session.is_authenticated())
        self.assertFalse(self.service.status().value.authenticated)

    def test_deleted_recreated_login_does_not_validate_old_technical_identity(self):
        with self.fixture.store.transaction() as transaction:
            transaction.delete(self.fixture.admin.summary.account_id)
        self.fixture.seed(self.fixture.admin.summary.login_id, "Admin")
        self.assertFalse(self.service.status().value.authenticated)

    def test_disabled_or_role_changed_account_invalidates_displayed_claims(self):
        for change in ({"enabled": False}, {"role": "Operator"}):
            with self.subTest(change=change):
                with self.fixture.store.transaction() as transaction:
                    transaction.replace(replace(self.fixture.admin, summary=replace(self.fixture.admin.summary, **change)))
                self.assertFalse(self.service.status().value.authenticated)

    def test_session_change_during_validation_returns_conflict(self):
        original = self.contexts.capture
        def capture_then_switch():
            result = original()
            self.fixture.session.logout()
            return result
        with patch.object(self.contexts, "capture", side_effect=capture_then_switch):
            self.assertEqual(self.service.status().error.code, ErrorCode.CONFLICT)

    def test_logged_out_status_is_safe_and_unauthenticated(self):
        self.fixture.session.logout()
        self.assertFalse(self.service.status().value.authenticated)
