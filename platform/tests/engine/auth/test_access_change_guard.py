from contextlib import contextmanager
import unittest
from unittest.mock import MagicMock, patch

from src.engine.auth.access_change_guard import SystemAccessChangeGuard
from src.engine.auth.account_service import AccountService
from src.engine.auth.permission_service import PermissionService
from src.engine.auth.recovery_service import RecoveryService
from src.engine.auth.sqlite_account_store import SQLiteAccountTransaction
from src.engine.system.system_manager import SystemManager
from src.shared_contracts.accounts.commands import ChangePassword, ChangeRole, DeleteAccount, EditProfile
from src.shared_contracts.accounts.recovery import GenerateRecoveryCodes, RecoverAdminAccount
from src.shared_contracts.authorization.permissions import UpdateAppPermissions
from src.shared_contracts.authorization.errors import AuditPersistenceError, ErrorCode, ServiceUnavailableError
from src.shared_contracts.authorization.results import Success
import tests.engine.auth.test_account_service as fixtures


class ActiveSessionChangeTests(unittest.TestCase):
    def setUp(self):
        self.fixture = fixtures.AccountServiceTests()
        self.fixture.setUp()
        self.addCleanup(self.fixture.doCleanups)
        self.manager = SystemManager(MagicMock())
        self.reason = None
        self.guard = SystemAccessChangeGuard(self.fixture.session, self.manager, self.block_reason)
        self.accounts = AccountService(self.fixture.store, self.fixture.session, self.fixture.policy,
                                        self.fixture.credentials, activity_guard=self.guard)

    def block_reason(self):
        return self.reason

    def test_own_password_change_is_rejected_while_process_retains_control(self):
        self.manager.acquire("production")
        result = self.accounts.change_password(ChangePassword(self.fixture.admin.summary.account_id, 1,
                                                               "replacement", "initial-secret"))
        self.assertEqual(result.error.code, ErrorCode.BUSY)
        self.assertEqual(self.fixture.get(self.fixture.admin), self.fixture.admin)
        self.assertEqual(self.manager.active_process_id, "production")
        self.assertEqual(self.fixture.history(self.fixture.admin.summary.account_id), ())

    def test_other_operator_reset_and_profile_edit_do_not_revoke_the_active_session(self):
        self.manager.acquire("production")
        result = self.accounts.change_password(ChangePassword(self.fixture.operator.summary.account_id, 1, "replacement"))
        self.assertIsInstance(result, Success)
        result = self.accounts.edit_profile(EditProfile(self.fixture.admin.summary.account_id, 1, "Changed", "Last", ""))
        self.assertIsInstance(result, Success)
        self.assertEqual(self.manager.active_process_id, "production")

    def test_own_role_change_and_deletion_are_rejected_while_busy(self):
        self.fixture.login(self.fixture.manufacturer)
        self.manager.acquire("production")
        identity = self.fixture.manufacturer.summary.account_id
        self.assertEqual(self.accounts.change_role(ChangeRole(identity, 1, "Admin")).error.code, ErrorCode.BUSY)
        self.assertEqual(self.accounts.delete_user(DeleteAccount(identity, 1)).error.code, ErrorCode.BUSY)

    def test_idle_reservation_is_retained_until_after_database_commit(self):
        observed = []
        original_transaction = self.fixture.store.transaction
        @contextmanager
        def transaction():
            with original_transaction() as value:
                yield value
            observed.append(self.manager.active_process_id)
        original_hash = self.fixture.credentials.hash_password
        def hash_while_attempting_start(password):
            self.assertFalse(self.manager.acquire("production"))
            return original_hash(password)
        with patch.object(self.fixture.store, "transaction", transaction), \
                patch.object(self.fixture.credentials, "hash_password", side_effect=hash_while_attempting_start):
            result = self.accounts.change_password(ChangePassword(self.fixture.admin.summary.account_id, 1,
                                                                   "replacement", "initial-secret"))
        self.assertIsInstance(result, Success)
        self.assertTrue(observed[-1].startswith("account_access_change:"))
        self.assertIsNone(self.manager.active_process_id)
        self.assertTrue(self.manager.acquire("production"))

    def test_activity_starting_during_crypto_rolls_back_credentials_and_history(self):
        original_hash = self.fixture.credentials.hash_password
        def hash_then_activity(password):
            self.reason = "robot_moving"
            return original_hash(password)
        with patch.object(self.fixture.credentials, "hash_password", side_effect=hash_then_activity):
            result = self.accounts.change_password(ChangePassword(self.fixture.admin.summary.account_id, 1,
                                                                   "replacement", "initial-secret"))
        self.assertEqual(result.error.code, ErrorCode.BUSY)
        self.assertEqual(self.fixture.get(self.fixture.admin), self.fixture.admin)
        self.assertEqual(self.fixture.history(self.fixture.admin.summary.account_id), ())
        self.assertIsNone(self.manager.active_process_id)

    def test_audit_failure_releases_reservation_and_rolls_back(self):
        with patch.object(SQLiteAccountTransaction, "append_event", side_effect=AuditPersistenceError):
            with self.assertRaises(AuditPersistenceError):
                self.accounts.change_password(ChangePassword(self.fixture.admin.summary.account_id, 1,
                                                               "replacement", "initial-secret"))
        self.assertIsNone(self.manager.active_process_id)
        self.assertEqual(self.fixture.get(self.fixture.admin), self.fixture.admin)

    def test_permission_reads_work_while_writes_wait_for_idle(self):
        self.fixture.login(self.fixture.manufacturer)
        service = PermissionService(self.fixture.store, self.fixture.session, self.fixture.policy,
                                    app_ids=frozenset({"dashboard"}), activity_guard=self.guard)
        before = service.read_permissions().value
        self.manager.acquire("production")
        self.assertIsInstance(service.read_permissions(), Success)
        result = service.update_permissions(UpdateAppPermissions("dashboard", ("Operator",), before.revision))
        self.assertEqual(result.error.code, ErrorCode.BUSY)
        self.assertEqual(service.read_permissions().value, before)

    def test_busy_recovery_preserves_code_until_a_safe_retry(self):
        service = RecoveryService(self.fixture.store, self.fixture.session, self.fixture.policy,
                                   self.fixture.credentials, activity_guard=self.guard)
        code = service.generate_codes(GenerateRecoveryCodes("initial-secret")).value.codes[0]
        self.manager.acquire("production")
        command = RecoverAdminAccount("1", code, "replacement")
        self.assertEqual(service.recover_admin(command).error.code, ErrorCode.BUSY)
        self.assertEqual(self.fixture.get(self.fixture.admin), self.fixture.admin)
        self.assertEqual(service.recover_admin(RecoverAdminAccount("1", "wrong-code", "replacement")).error.code,
                         ErrorCode.INVALID_PROOF)
        self.manager.release("production")
        self.assertIsInstance(service.recover_admin(command), Success)

    def test_activity_query_failure_is_not_treated_as_idle(self):
        guard = SystemAccessChangeGuard(self.fixture.session, self.manager,
                                       MagicMock(side_effect=RuntimeError("unavailable")))
        accounts = AccountService(self.fixture.store, self.fixture.session, self.fixture.policy,
                                    self.fixture.credentials, activity_guard=guard)
        with self.assertRaises(ServiceUnavailableError):
            accounts.change_password(ChangePassword(self.fixture.admin.summary.account_id, 1,
                                                      "replacement", "initial-secret"))
        self.assertEqual(self.fixture.get(self.fixture.admin), self.fixture.admin)
