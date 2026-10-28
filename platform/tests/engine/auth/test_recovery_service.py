from concurrent.futures import ThreadPoolExecutor
from dataclasses import replace
from pathlib import Path
import unittest
from unittest.mock import patch

from src.engine.auth.recovery_service import RecoveryLimits, RecoveryService
from src.engine.auth.sqlite_account_store import SQLiteAccountStore, SQLiteAccountTransaction
from src.shared_contracts.accounts.commands import ChangePassword
from src.shared_contracts.accounts.recovery import GenerateRecoveryCodes, RecoverAdminAccount
from src.shared_contracts.authorization.errors import AuditPersistenceError, ErrorCode
from src.shared_contracts.authorization.results import Failure, Success
import tests.engine.auth.test_account_service as fixtures


class RecoveryServiceTests(unittest.TestCase):
    def setUp(self):
        self.fixture = fixtures.AccountServiceTests()
        self.fixture.setUp()
        self.addCleanup(self.fixture.doCleanups)
        self.time = [1000.0]
        self.service = self.make_service(self.fixture.store)

    def make_service(self, store):
        return RecoveryService(store, self.fixture.session, self.fixture.policy, self.fixture.credentials,
                               limits=RecoveryLimits(failures_per_account=3, window_seconds=10),
                               clock=lambda: self.time[0])

    def issue(self):
        result = self.service.generate_codes(GenerateRecoveryCodes("initial-secret"))
        self.assertIsInstance(result, Success)
        return result.value

    def test_codes_are_returned_once_and_only_verification_digests_are_persisted(self):
        codes = self.issue()
        self.assertEqual(len(codes.codes), 8)
        self.assertEqual(len(set(codes.codes)), 8)
        for code in codes.codes:
            self.assertNotIn(code, repr(codes))
            self.assertNotIn(code.encode(), self.fixture.path.read_bytes())
            self.assertNotIn(code, repr(self.fixture.history(codes.account_id)))
        self.assertEqual(self.fixture.get(self.fixture.admin), self.fixture.admin)

    def test_issuance_requires_owner_admin_and_current_password(self):
        invalid = self.service.generate_codes(GenerateRecoveryCodes("wrong"))
        self.assertEqual(invalid.error.code, ErrorCode.INVALID_PROOF)
        for account in (self.fixture.operator, self.fixture.manufacturer):
            self.fixture.login(account)
            result = self.service.generate_codes(GenerateRecoveryCodes("initial-secret"))
            self.assertEqual(result.error.code, ErrorCode.ACCESS_DENIED)

    def test_success_consumes_all_old_codes_and_returns_replacements_without_logging_in(self):
        codes = self.issue()
        self.fixture.session.logout()
        command = RecoverAdminAccount("1", codes.codes[0], "replacement-secret")
        result = self.service.recover_admin(command)
        self.assertIsInstance(result, Success)
        self.assertIsNone(self.fixture.session.current_user)
        stored = self.fixture.get(self.fixture.admin)
        self.assertEqual(stored.credential_version, 2)
        self.assertEqual(stored.summary.updated_by, stored.summary.account_id)
        self.assertTrue(self.fixture.credentials.verify_password("replacement-secret", stored.password_hash))
        for old in codes.codes[:2]:
            self.assertEqual(self.service.recover_admin(RecoverAdminAccount("1", old, "again")).error.code,
                             ErrorCode.INVALID_PROOF)
        self.assertIsInstance(self.service.recover_admin(RecoverAdminAccount("1", result.value.codes[0], "again")), Success)

    def test_regenerating_codes_revokes_the_previous_set(self):
        first, second = self.issue(), self.issue()
        self.assertIsInstance(self.service.recover_admin(RecoverAdminAccount("1", first.codes[0], "replacement")), Failure)
        self.assertIsInstance(self.service.recover_admin(RecoverAdminAccount("1", second.codes[0], "replacement")), Success)

    def test_codes_do_not_work_for_another_admin(self):
        codes = self.issue()
        self.fixture.login(self.fixture.other_admin)
        self.issue()
        result = self.service.recover_admin(RecoverAdminAccount("2", codes.codes[0], "replacement"))
        self.assertEqual(result.error.code, ErrorCode.INVALID_PROOF)

    def test_code_verifiers_cannot_be_transplanted_into_another_installation(self):
        codes = self.issue()
        second = SQLiteAccountStore.initialize(Path(self.fixture.directory.name) / "second.sqlite3")
        with self.fixture.store.transaction() as transaction:
            verifiers = transaction.recovery_verifiers(self.fixture.admin.summary.account_id)
        with second.transaction() as transaction:
            transaction.insert(self.fixture.admin)
            transaction.replace_recovery_verifiers(self.fixture.admin.summary.account_id, verifiers)
        result = self.make_service(second).recover_admin(RecoverAdminAccount("1", codes.codes[0], "replacement"))
        self.assertEqual(result.error.code, ErrorCode.INVALID_PROOF)

    def test_recovery_requires_account_to_still_be_an_enabled_admin(self):
        codes = self.issue()
        with self.fixture.store.transaction() as transaction:
            transaction.replace(replace(self.fixture.admin, summary=replace(self.fixture.admin.summary, role="Manufacturer")))
        result = self.service.recover_admin(RecoverAdminAccount("1", codes.codes[0], "replacement"))
        self.assertEqual(result.error.code, ErrorCode.INVALID_PROOF)

    def test_manufacturer_reset_is_audited_and_invalidates_old_admin_recovery_codes(self):
        codes = self.issue()
        self.fixture.login(self.fixture.manufacturer)
        result = self.fixture.service.change_password(ChangePassword(self.fixture.admin.summary.account_id, 1,
                                                                      "manufacturer-reset"))
        self.assertIsInstance(result, Success)
        event = self.fixture.history(self.fixture.admin.summary.account_id)[0]
        self.assertEqual(event.actor_id, self.fixture.manufacturer.summary.account_id)
        self.assertTrue(event.password_changed)
        rejected = self.service.recover_admin(RecoverAdminAccount("1", codes.codes[0], "replacement"))
        self.assertEqual(rejected.error.code, ErrorCode.INVALID_PROOF)

    def test_failed_attempt_limits_survive_service_and_database_reopening(self):
        codes = self.issue()
        for _ in range(3):
            self.assertEqual(self.service.recover_admin(RecoverAdminAccount("1", "wrong", "replacement")).error.code,
                             ErrorCode.INVALID_PROOF)
        restarted = self.make_service(SQLiteAccountStore(self.fixture.path))
        blocked = restarted.recover_admin(RecoverAdminAccount("1", codes.codes[0], "replacement"))
        self.assertEqual(blocked.error.code, ErrorCode.RATE_LIMITED)
        self.time[0] += 11
        self.assertIsInstance(restarted.recover_admin(RecoverAdminAccount("1", codes.codes[0], "replacement")), Success)

    def test_audit_failure_rolls_back_password_and_code_consumption(self):
        codes = self.issue()
        command = RecoverAdminAccount("1", codes.codes[0], "replacement")
        with patch.object(SQLiteAccountTransaction, "append_event", side_effect=AuditPersistenceError):
            with self.assertRaises(AuditPersistenceError):
                self.service.recover_admin(command)
        self.assertEqual(self.fixture.get(self.fixture.admin), self.fixture.admin)
        self.assertIsInstance(self.service.recover_admin(command), Success)

    def test_concurrent_recovery_allows_at_most_one_redemption(self):
        codes = self.issue()
        command = RecoverAdminAccount("1", codes.codes[0], "replacement")
        with ThreadPoolExecutor(max_workers=2) as pool:
            results = list(pool.map(self.service.recover_admin, (command, command)))
        self.assertEqual(sum(isinstance(result, Success) for result in results), 1)
        self.assertEqual(sum(isinstance(result, Failure) for result in results), 1)


if __name__ == "__main__":
    unittest.main()
