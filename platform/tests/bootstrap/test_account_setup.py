from contextlib import redirect_stderr, redirect_stdout
import io
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from src.bootstrap.account_setup import main
from src.engine.auth.account_installation import AccountInstallation, AccountInstallationPaths
from src.shared_contracts.authorization.errors import StorageIntegrityError


class AccountSetupCLITests(unittest.TestCase):
    def setUp(self):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.root = Path(directory.name)
        self.paths = AccountInstallationPaths(self.root / "data" / "accounts.sqlite3",
                                              self.root / "data" / "installation.json",
                                              self.root / "secrets" / "operator.key")

    def arguments(self):
        return ["--database", str(self.paths.database), "--state", str(self.paths.state),
                "--operator-key", str(self.paths.operator_key)]

    def run_command(self, arguments=None):
        output, errors = io.StringIO(), io.StringIO()
        with redirect_stdout(output), redirect_stderr(errors):
            code = main(self.arguments() if arguments is None else arguments)
        return code, output.getvalue(), errors.getvalue()

    def test_creates_empty_installation_with_provisioning_instructions(self):
        code, output, errors = self.run_command()
        self.assertEqual(code, 0, errors)
        self.assertIn("first-Admin", output)
        self.assertNotIn(self.paths.operator_key.read_text().strip(), output + errors)
        prepared = AccountInstallation(self.paths).open_existing()
        with prepared.store.transaction() as transaction:
            self.assertEqual(transaction.list_accounts(), ())

    def test_refuses_relative_paths_without_creating_material(self):
        arguments = self.arguments()
        arguments[1] = "accounts.sqlite3"
        code, output, errors = self.run_command(arguments)
        self.assertEqual(code, 2)
        self.assertFalse(self.paths.state.exists())

    def test_direct_entry_point_works_with_isolated_interpreter(self):
        command = Path(__file__).resolve().parents[2] / "src" / "bootstrap" / "account_setup.py"
        result = subprocess.run([sys.executable, "-I", str(command), *self.arguments()],
                                cwd=self.root, capture_output=True, text=True, timeout=20)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue(self.paths.database.is_file())
        self.assertTrue(self.paths.operator_key.is_file())

    def test_refuses_existing_unbound_database_without_touching_it(self):
        self.paths.database.parent.mkdir()
        self.paths.database.write_bytes(b"existing unbound data")
        code, output, errors = self.run_command()
        self.assertEqual(code, 2)
        self.assertEqual(self.paths.database.read_bytes(), b"existing unbound data")
        self.assertFalse(self.paths.operator_key.exists())

    def test_same_directory_for_key_and_database_is_rejected(self):
        arguments = self.arguments()
        arguments[-1] = str(self.paths.database.parent / "operator.key")
        self.assertEqual(self.run_command(arguments)[0], 2)
        self.assertFalse(self.paths.database.exists())

    def test_structured_error_does_not_expose_exception_details(self):
        with patch("src.engine.auth.account_installation.AccountInstallation.initialize_new",
                   side_effect=StorageIntegrityError()) as operation:
            code, output, errors = self.run_command()
        self.assertEqual(code, 4)
        self.assertIn("reference", errors)
        self.assertNotIn("Traceback", errors)
        operation.assert_called_once()
