from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from src.engine.auth.admin_commissioning_service import AdminCommissioningService
from src.engine.auth.account_maintenance_service import AccountMaintenanceService
from src.engine.auth.sqlite_account_store import SQLiteAccountStore, SQLiteAccountTransaction
from src.shared_contracts.accounts.commissioning import CreateFirstAdmin
from src.shared_contracts.accounts.events import HistoryQuery
from src.shared_contracts.accounts.maintenance import CreateManufacturer
from src.shared_contracts.authorization.errors import AuditPersistenceError, ErrorCode, StorageIntegrityError
from src.shared_contracts.authorization.results import Failure, Success
from tests.engine.auth.test_account_service import FakeCredentials
from tests.engine.auth.test_account_maintenance import FakeAuthority


class AdminCommissioningTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.store = SQLiteAccountStore.initialize(Path(self.directory.name) / "accounts.sqlite3")
        self.passwords = FakeCredentials()
        self.service = AdminCommissioningService(self.store, self.passwords)
        self.command = CreateFirstAdmin("1", "Customer", "Admin", "secret")

    def test_manufacturer_provisioning_does_not_skip_customer_admin_setup(self):
        maintenance = AccountMaintenanceService(self.store, FakeAuthority(), self.passwords)
        maintenance.create_manufacturer(CreateManufacturer("900", "Service", "Engineer", "manufacturer-secret"))
        self.assertTrue(self.service.status().required)
        created = self.service.create_first_admin(self.command)
        self.assertIsInstance(created, Success)
        self.assertEqual(created.value.role, "Admin")
        self.assertFalse(self.service.status().required)
        with self.store.transaction() as transaction:
            self.assertEqual(len(transaction.list_accounts()), 2)
            event = transaction.history(HistoryQuery(created.value.account_id))[0]
        self.assertEqual(event.actor_method, "commissioning")
        self.assertIsNone(event.actor_id)

    def test_completed_setup_cannot_be_reopened_for_another_admin(self):
        self.service.create_first_admin(self.command)
        again = self.service.create_first_admin(CreateFirstAdmin("2", "Another", "Admin", "secret"))
        self.assertEqual(again.error.code, ErrorCode.POLICY_VIOLATION)

    def test_missing_commissioning_state_is_not_initial_setup(self):
        with patch.object(SQLiteAccountTransaction, "metadata", return_value=None):
            with self.assertRaises(StorageIntegrityError):
                self.service.status()
            with self.assertRaises(StorageIntegrityError):
                self.service.create_first_admin(self.command)

    def test_audit_failure_does_not_close_setup_or_leave_partial_account(self):
        with patch.object(SQLiteAccountTransaction, "append_event", side_effect=AuditPersistenceError):
            with self.assertRaises(AuditPersistenceError):
                self.service.create_first_admin(self.command)
        self.assertTrue(self.service.status().required)
        with self.store.transaction() as transaction:
            self.assertEqual(transaction.list_accounts(), ())

    def test_concurrent_initial_creation_has_only_one_winner(self):
        commands = (self.command, CreateFirstAdmin("2", "Another", "Admin", "secret"))
        with ThreadPoolExecutor(max_workers=2) as pool:
            results = list(pool.map(self.service.create_first_admin, commands))
        self.assertEqual(sum(isinstance(result, Success) for result in results), 1)
        self.assertEqual(sum(isinstance(result, Failure) for result in results), 1)


if __name__ == "__main__":
    unittest.main()
