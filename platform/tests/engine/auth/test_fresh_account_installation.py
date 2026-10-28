from concurrent.futures import ThreadPoolExecutor
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from src.engine.auth.account_installation import AccountInstallation, AccountInstallationPaths
from src.engine.auth.admin_commissioning_service import AdminCommissioningService
from src.engine.auth.account_login_service import AccountLoginService
from src.shared_contracts.accounts.authentication import LoginCredentials
from src.shared_contracts.accounts.commissioning import CreateFirstAdmin
from src.shared_contracts.accounts.events import HistoryQuery
from src.shared_contracts.authorization.errors import AuditPersistenceError, KeyUnavailableError, ServiceUnavailableError, StorageIntegrityError
from src.shared_contracts.authorization.results import Failure, Success


class FreshAccountInstallationTests(unittest.TestCase):
    def setUp(self):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.root = Path(directory.name)
        self.paths = AccountInstallationPaths(self.root / "data" / "accounts.sqlite3",
                                              self.root / "data" / "installation.json",
                                              self.root / "private" / "operator.key")
        self.installation = AccountInstallation(self.paths)

    def initialize(self):
        result = self.installation.initialize_new()
        self.assertIsInstance(result, Success)
        return result.value

    def test_fresh_setup_needs_no_legacy_sources_and_has_no_default_accounts(self):
        prepared = self.initialize()
        with prepared.store.transaction() as transaction:
            self.assertEqual(transaction.list_accounts(), ())
            self.assertEqual(transaction.read_permissions(), {})
            self.assertEqual(transaction.metadata("commissioned"), "0")
            self.assertEqual(transaction.metadata("fresh_setup"), "1")
            self.assertIsNone(transaction.metadata("legacy_migration"))
            events = transaction.history(HistoryQuery(prepared.installation_id))
            self.assertEqual([event.action_id for event in events], ["installation.created"])
        self.assertEqual(json.loads(self.paths.state.read_text())["setup_mode"], "fresh")

    def test_fresh_setup_ignores_old_account_and_permission_files(self):
        source = self.root / "old-users.csv"
        source.write_text("old plaintext credentials")
        (self.root / "permissions.json").write_text('{"admin": ["Developer"]}')
        result = self.installation.initialize_new()
        self.assertIsInstance(result, Success)
        with result.value.store.transaction() as transaction:
            self.assertEqual(transaction.list_accounts(), ())
            self.assertEqual(transaction.read_permissions(), {})
        self.assertEqual(source.read_text(), "old plaintext credentials")

    def test_repeated_setup_preserves_new_admin_and_only_one_install_event(self):
        prepared = self.initialize()
        service = AdminCommissioningService(prepared.store, prepared.credentials)
        admin = service.create_first_admin(CreateFirstAdmin("1", "First", "Admin", "fresh-secret"))
        self.assertIsInstance(admin, Success)
        reopened = self.initialize()
        with reopened.store.transaction() as transaction:
            self.assertEqual([a.summary for a in transaction.list_accounts()], [admin.value])
            self.assertEqual(len(transaction.history(HistoryQuery(prepared.installation_id))), 1)
        self.assertFalse(service.status().required)

    def test_interruption_after_setup_commit_resumes_without_duplicate_audit(self):
        original = self.installation._write_state
        def fail_activation(state):
            if state["stage"] == "active":
                raise ServiceUnavailableError()
            original(state)
        with patch.object(self.installation, "_write_state", side_effect=fail_activation):
            with self.assertRaises(ServiceUnavailableError):
                self.installation.initialize_new()
        prepared = self.initialize()
        with prepared.store.transaction() as transaction:
            self.assertEqual(len(transaction.history(HistoryQuery(prepared.installation_id))), 1)

    def test_lost_established_database_cannot_reopen_fresh_setup(self):
        self.initialize()
        self.paths.database.unlink()
        with self.assertRaises(StorageIntegrityError):
            self.installation.initialize_new()
        self.assertFalse(self.paths.database.exists())

    def test_audit_failure_cannot_activate_installation(self):
        with patch("src.engine.auth.sqlite_account_store.SQLiteAccountTransaction.append_event",
                   side_effect=AuditPersistenceError):
            with self.assertRaises(AuditPersistenceError):
                self.installation.initialize_new()
        self.assertEqual(json.loads(self.paths.state.read_text())["stage"], "key_ready")
        with self.assertRaises(StorageIntegrityError):
            self.installation.open_existing()
        prepared = self.initialize()
        with prepared.store.transaction() as transaction:
            self.assertEqual(len(transaction.history(HistoryQuery(prepared.installation_id))), 1)

    def test_missing_state_cannot_replace_existing_material(self):
        self.initialize()
        key = self.paths.operator_key.read_bytes()
        self.paths.state.unlink()
        self.assertIsInstance(self.installation.initialize_new(), Failure)
        self.assertEqual(self.paths.operator_key.read_bytes(), key)
        self.assertFalse(self.paths.state.exists())

    def test_unsupported_setup_mode_is_an_integrity_error(self):
        self.initialize()
        state = json.loads(self.paths.state.read_text())
        state.update(setup_mode="legacy", stage="key_ready")
        self.paths.state.write_text(json.dumps(state))
        with self.assertRaises(StorageIntegrityError):
            self.installation.initialize_new()
        self.assertEqual(json.loads(self.paths.state.read_text())["stage"], "key_ready")

    def test_key_loss_does_not_block_admin_authentication_or_recreate_key(self):
        prepared = self.initialize()
        AdminCommissioningService(prepared.store, prepared.credentials).create_first_admin(
            CreateFirstAdmin("1", "First", "Admin", "fresh-secret"))
        self.paths.operator_key.unlink()
        reopened = self.installation.open_existing()
        result = AccountLoginService(reopened.store, reopened.credentials).login(LoginCredentials("1", "fresh-secret"))
        self.assertIsInstance(result, Success)
        self.assertIsInstance(self.installation.initialize_new(), Success)
        self.assertFalse(self.paths.operator_key.exists())
        with self.assertRaises(KeyUnavailableError):
            reopened.credentials.encrypt_operator_password("secret")

    def test_interrupted_key_binding_cannot_silently_generate_another_key(self):
        original = self.installation._write_state
        def fail_after_binding(state):
            if state["stage"] == "key_ready":
                raise ServiceUnavailableError()
            original(state)
        with patch.object(self.installation, "_write_state", side_effect=fail_after_binding):
            with self.assertRaises(ServiceUnavailableError):
                self.installation.initialize_new()
        self.paths.operator_key.unlink()
        with self.assertRaises(KeyUnavailableError):
            self.installation.initialize_new()
        self.assertFalse(self.paths.operator_key.exists())

    def test_corrupt_state_cannot_reopen_setup(self):
        self.initialize()
        self.paths.state.write_text("{}")
        with self.assertRaises(StorageIntegrityError):
            self.installation.open_existing()
        with self.assertRaises(StorageIntegrityError):
            self.installation.initialize_new()

    def test_concurrent_setup_produces_one_identity_and_one_event(self):
        with ThreadPoolExecutor(max_workers=2) as pool:
            results = list(pool.map(lambda _: AccountInstallation(self.paths).initialize_new(), range(2)))
        self.assertTrue(all(isinstance(result, Success) for result in results))
        first = results[0].value
        self.assertEqual(first.installation_id, results[1].value.installation_id)
        with first.store.transaction() as transaction:
            self.assertEqual(len(transaction.history(HistoryQuery(first.installation_id))), 1)
