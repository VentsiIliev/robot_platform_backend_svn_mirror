from pathlib import Path
import tempfile
import unittest

from src.engine.auth.account_runtime_lock import AccountRuntimeLock
from src.engine.auth.sqlite_account_store import SQLiteAccountStore
from src.shared_contracts.authorization.errors import AccountRuntimeInUseError, ServiceUnavailableError


class AccountRuntimeOwnershipTests(unittest.TestCase):
    def setUp(self):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.root = Path(directory.name)
        self.database = self.root / "accounts.sqlite3"
        SQLiteAccountStore.initialize(self.database)

    def test_runtime_and_offline_writer_cannot_hold_the_same_database(self):
        with AccountRuntimeLock.acquire(self.database):
            with self.assertRaises(AccountRuntimeInUseError):
                AccountRuntimeLock.acquire(self.database)
        with AccountRuntimeLock.acquire(self.database):
            self.assertTrue(self.database.is_file())

    def test_symlink_database_alias_uses_the_same_ownership_lock(self):
        alias = self.root / "alias.sqlite3"
        alias.symlink_to(self.database)
        with AccountRuntimeLock.acquire(self.database):
            with self.assertRaises(AccountRuntimeInUseError):
                AccountRuntimeLock.acquire(alias)

    def test_lock_symlink_is_rejected_without_touching_its_destination(self):
        victim = self.root / "unrelated.txt"
        victim.write_text("unchanged")
        (self.root / "accounts.sqlite3.runtime.lock").symlink_to(victim)
        with self.assertRaises(ServiceUnavailableError):
            AccountRuntimeLock.acquire(self.database)
        self.assertEqual(victim.read_text(), "unchanged")

    def test_close_is_idempotent_and_lock_file_is_private(self):
        ownership = AccountRuntimeLock.acquire(self.database)
        self.assertEqual((self.root / "accounts.sqlite3.runtime.lock").stat().st_mode & 0o777, 0o600)
        ownership.close()
        ownership.close()
        with AccountRuntimeLock.acquire(self.database):
            pass
