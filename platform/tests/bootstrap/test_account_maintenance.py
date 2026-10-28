from contextlib import redirect_stderr, redirect_stdout
import getpass
import io
import unittest
from unittest.mock import patch
import warnings

from src.bootstrap import account_maintenance
from src.engine.auth.account_runtime_lock import AccountRuntimeLock
from src.shared_contracts.accounts.maintenance import OperatingSystemActor
from src.shared_contracts.authorization.results import Success
import tests.engine.auth.test_account_service as fixtures


class AccountMaintenanceCLITests(unittest.TestCase):
    def setUp(self):
        self.fixture = fixtures.AccountServiceTests()
        self.fixture.setUp()
        self.addCleanup(self.fixture.doCleanups)

    def run_command(self, action, password=None):
        output, errors = io.StringIO(), io.StringIO()
        with patch("src.engine.auth.unix_maintenance_authority.UnixMaintenanceAuthority.current_actor",
                   return_value=Success(OperatingSystemActor(0, "root"))), \
                patch("src.engine.auth.password_hasher.ScryptPasswordHasher", return_value=self.fixture.credentials), \
                patch.object(account_maintenance, "_read_password", return_value=password), \
                redirect_stdout(output), redirect_stderr(errors):
            code = account_maintenance.main(["--database", str(self.fixture.path), *action])
        return code, output.getvalue(), errors.getvalue()

    def test_reset_uses_interactive_secret_and_never_prints_it(self):
        code, output, errors = self.run_command(["reset-manufacturer", "--login-id", "4"], "new-secret")
        self.assertEqual(code, 0)
        self.assertNotIn("new-secret", output + errors)
        self.assertTrue(self.fixture.credentials.verify_password("new-secret", self.fixture.get(self.fixture.manufacturer).password_hash))

    def test_inspect_never_requests_a_password_or_exposes_hashes(self):
        code, output, errors = self.run_command(["inspect-manufacturer", "--login-id", "4"])
        self.assertEqual(code, 0)
        self.assertNotIn(self.fixture.manufacturer.password_hash, output)

    def test_nonroot_is_refused_before_opening_database_or_prompting(self):
        with patch("os.geteuid", return_value=1000), \
                patch("src.engine.auth.sqlite_account_store.SQLiteAccountStore") as store, \
                patch.object(account_maintenance, "_read_password") as prompt, redirect_stderr(io.StringIO()):
            code = account_maintenance.main(["--database", str(self.fixture.path), "reset-manufacturer", "--login-id", "4"])
        self.assertEqual(code, 3)
        store.assert_not_called()
        prompt.assert_not_called()

    def test_password_input_rejects_pipes_and_echo_fallback(self):
        with patch.object(account_maintenance.sys.stdin, "isatty", return_value=False):
            with self.assertRaises(ValueError):
                account_maintenance._read_password()
        def unsafe_getpass(prompt):
            warnings.warn("Cannot control echo", getpass.GetPassWarning)
            return "secret"
        with patch.object(account_maintenance.sys.stdin, "isatty", return_value=True), \
                patch.object(account_maintenance.sys.stdout, "isatty", return_value=True), \
                patch.object(account_maintenance.getpass, "getpass", side_effect=unsafe_getpass):
            with self.assertRaises(getpass.GetPassWarning):
                account_maintenance._read_password()

    def test_password_input_requires_matching_nonempty_confirmation(self):
        with patch.object(account_maintenance.sys.stdin, "isatty", return_value=True), \
                patch.object(account_maintenance.sys.stdout, "isatty", return_value=True), \
                patch.object(account_maintenance.getpass, "getpass", side_effect=["one", "two"]):
            with self.assertRaises(ValueError):
                account_maintenance._read_password()

    def test_create_and_missing_database_behavior(self):
        code, output, errors = self.run_command(["create-manufacturer", "--login-id", "5",
                                                "--first-name", "Service", "--last-name", "Engineer"], "secret")
        self.assertEqual(code, 0)
        with self.fixture.store.transaction() as transaction:
            self.assertEqual(transaction.get_by_login("5").summary.role, "Manufacturer")
        missing = self.fixture.path.parent / "missing.sqlite3"
        with patch("src.engine.auth.unix_maintenance_authority.UnixMaintenanceAuthority.current_actor",
                   return_value=Success(OperatingSystemActor(0, "root"))), redirect_stderr(io.StringIO()):
            code = account_maintenance.main(["--database", str(missing), "reset-manufacturer", "--login-id", "4"])
        self.assertEqual(code, 2)
        self.assertFalse(missing.exists())

    def test_creation_rejects_login_id_that_current_platform_form_cannot_accept(self):
        with redirect_stderr(io.StringIO()), self.assertRaises(SystemExit) as stopped:
            account_maintenance.main(["--database", str(self.fixture.path), "create-manufacturer",
                                      "--login-id", "service", "--first-name", "Service", "--last-name", "Engineer"])
        self.assertEqual(stopped.exception.code, 2)

    def test_offline_reset_is_refused_while_platform_owns_the_database(self):
        with AccountRuntimeLock.acquire(self.fixture.path):
            code, output, errors = self.run_command(["reset-manufacturer", "--login-id", "4"], "replacement")
        self.assertEqual(code, 2)
        self.assertIn("busy", errors)
        self.assertEqual(self.fixture.get(self.fixture.manufacturer), self.fixture.manufacturer)

    def test_read_only_inspection_does_not_revoke_running_access(self):
        with AccountRuntimeLock.acquire(self.fixture.path):
            code, output, errors = self.run_command(["inspect-manufacturer", "--login-id", "4"])
        self.assertEqual(code, 0, errors)


if __name__ == "__main__":
    unittest.main()
