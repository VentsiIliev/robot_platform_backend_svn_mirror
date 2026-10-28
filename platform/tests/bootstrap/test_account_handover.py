"""Disposable commissioning/recovery/restore acceptance with real scrypt and Fernet."""
from pathlib import Path
import shutil
import sqlite3
import tempfile
import unittest

from src.engine.auth.account_installation import AccountInstallation, AccountInstallationPaths
from src.engine.auth.account_maintenance_service import AccountMaintenanceService
from src.engine.auth.account_principal import AccountPrincipal
from src.engine.auth.account_runtime import AccountRuntime
from src.engine.auth.i_maintenance_authority import IMaintenanceAuthority
from src.engine.auth.password_hasher import ScryptPasswordHasher
from src.engine.auth.user_session import UserSession
from src.shared_contracts.accounts.authentication import LoginCredentials
from src.shared_contracts.accounts.commands import ChangePassword, CreateAccount, RevealPassword
from src.shared_contracts.accounts.commissioning import CreateFirstAdmin
from src.shared_contracts.accounts.events import HistoryQuery
from src.shared_contracts.accounts.maintenance import CreateManufacturer, OperatingSystemActor, ResetManufacturerPassword
from src.shared_contracts.accounts.recovery import GenerateRecoveryCodes, RecoverAdminAccount
from src.shared_contracts.authorization.results import Failure, Success


class _TestOsAuthority(IMaintenanceAuthority):
    def current_actor(self):
        # Injected authority double, never invokes sudo or changes OS identity.
        return Success(OperatingSystemActor(0, "root"))


class AccountHandoverTests(unittest.TestCase):
    def test_empty_setup_recovery_fallback_and_separate_key_backup_restore(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            paths = AccountInstallationPaths(root / "live/accounts.sqlite3", root / "live/state.json",
                                             root / "live-private/operator.key")
            prepared = AccountInstallation(paths).initialize_new().value
            with prepared.store.transaction() as transaction:
                self.assertEqual(transaction.list_accounts(), ())
            session = UserSession()
            runtime = AccountRuntime(prepared, session, ())
            maintenance = AccountMaintenanceService(prepared.store, _TestOsAuthority(), ScryptPasswordHasher())
            manufacturer = maintenance.create_manufacturer(CreateManufacturer(
                "900", "Factory", "Service", "test-manufacturer-original")).value
            self.assertTrue(runtime.commissioning.status().required)
            admin = runtime.commissioning.create_first_admin(CreateFirstAdmin(
                "1", "Customer", "Admin", "test-admin-original")).value
            self.assertFalse(runtime.commissioning.status().required)
            self.login(runtime, "1", "test-admin-original")
            operator = runtime.accounts.create_user(CreateAccount(
                "2", "Production", "Operator", "Operator", "test-operator-original")).value
            code = runtime.recovery.generate_codes(GenerateRecoveryCodes("test-admin-original")).value.codes[0]
            session.logout()
            recovered = runtime.recovery.recover_admin(RecoverAdminAccount("1", code, "test-admin-recovered"))
            self.assertIsInstance(recovered, Success)
            self.assertFalse(session.is_authenticated())
            self.assertIsInstance(runtime.login.login(LoginCredentials("1", "test-admin-original")), Failure)
            self.login(runtime, "900", "test-manufacturer-original")
            current_admin = next(row for row in runtime.accounts.list_users().value if row.account_id == admin.account_id)
            self.assertIsInstance(runtime.accounts.change_password(ChangePassword(
                admin.account_id, current_admin.revision, "test-admin-fallback")), Success)
            self.assertIsInstance(runtime.recovery.recover_admin(RecoverAdminAccount(
                "1", recovered.value.codes[0], "not-applied")), Failure)
            session.logout()
            self.assertIsInstance(maintenance.reset_manufacturer_password(ResetManufacturerPassword(
                manufacturer.account_id, manufacturer.revision, "test-manufacturer-os-reset")), Success)
            self.assertIsInstance(runtime.login.login(LoginCredentials("900", "test-manufacturer-original")), Failure)
            self.login(runtime, "900", "test-manufacturer-os-reset")
            self.assertEqual(runtime.accounts.reveal_operator_password(RevealPassword(operator.account_id)).value.password,
                             "test-operator-original")
            session.logout()

            # An offline, consistent SQLite snapshot plus the matching marker.
            backup = root / "backup"
            backup.mkdir(mode=0o700)
            with sqlite3.connect(paths.database) as source, sqlite3.connect(backup / "accounts.sqlite3") as target:
                source.backup(target)
            shutil.copy2(paths.state, backup / "state.json")
            key_backup = root / "separate-key-backup"
            key_backup.mkdir(mode=0o700)
            shutil.copy2(paths.operator_key, key_backup / "operator.key")

            restored_paths = AccountInstallationPaths(root / "restored/accounts.sqlite3",
                root / "restored/state.json", root / "restored-private/operator.key")
            restored_paths.database.parent.mkdir(mode=0o700)
            restored_paths.operator_key.parent.mkdir(mode=0o700)
            shutil.copy2(backup / "accounts.sqlite3", restored_paths.database)
            restored_paths.database.chmod(0o600)
            shutil.copy2(backup / "state.json", restored_paths.state)
            shutil.copy2(key_backup / "operator.key", restored_paths.operator_key)
            restored = AccountInstallation(restored_paths).open_existing()
            self.assertEqual(restored.installation_id, prepared.installation_id)
            restored_runtime = AccountRuntime(restored, UserSession(), ())
            self.login(restored_runtime, "1", "test-admin-fallback")
            self.assertEqual(restored_runtime.accounts.reveal_operator_password(RevealPassword(operator.account_id)).value.password,
                             "test-operator-original")
            self.login(restored_runtime, "900", "test-manufacturer-os-reset")
            with restored.store.transaction() as transaction:
                events = transaction.history(HistoryQuery(manufacturer.account_id))
            self.assertTrue(any(event.action_id == "maintenance.manufacturer_password_reset" for event in events))
            self.assertNotIn("test-manufacturer-os-reset", repr(events))
            self.assertNotIn(b"test-operator-original", restored_paths.database.read_bytes())

    def login(self, runtime, login_id, password):
        result = runtime.login.login(LoginCredentials(login_id, password))
        self.assertIsInstance(result, Success)
        runtime.session.login(AccountPrincipal(result.value.account, result.value.credential_version))
