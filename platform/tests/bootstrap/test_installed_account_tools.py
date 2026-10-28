from contextlib import redirect_stdout
import importlib.util
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from src.bootstrap.account_locations import deployment_record, installed_account_paths
from src.bootstrap.account_runtime import account_installation_paths
from src.engine.auth.account_installation import AccountInstallation

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location("account_tools_entry", ROOT / "packaging/platform/platform_entrypoint.py")
entry = importlib.util.module_from_spec(spec)
spec.loader.exec_module(entry)


class InstalledAccountToolTests(unittest.TestCase):
    def test_frozen_self_test_checks_real_credentials_without_hardware(self):
        entry.check_account_backend()

    def test_frozen_configuration_and_model_dependencies_are_available(self):
        entry.check_configuration_dependencies()

    def test_frozen_self_test_constructs_account_and_recovery_screens(self):
        # WebEngine needs a program name and one QApplication per process.
        # Other UI tests intentionally use QApplication([]), so isolate the
        # rendering check just like the actual frozen executable.
        script = '''
import importlib.util
from pathlib import Path
from src.bootstrap.qt_application import prepare_qt_application
prepare_qt_application()
from PyQt6.QtWidgets import QApplication
app = QApplication(['account-widget-self-test'])
spec = importlib.util.spec_from_file_location('account_entry', Path('packaging/platform/platform_entrypoint.py'))
entry = importlib.util.module_from_spec(spec)
spec.loader.exec_module(entry)
entry.check_account_widgets(app)
'''
        result = subprocess.run([sys.executable, '-B', '-c', script], cwd=ROOT,
            env={**os.environ, 'QT_QPA_PLATFORM': 'offscreen', 'QTWEBENGINE_DISABLE_SANDBOX': '1'},
            capture_output=True, text=True, timeout=30)
        self.assertEqual(result.returncode, 0, result.stderr)

    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.environment = patch.dict("os.environ", {"ROBOT_PLATFORM_DATA_ROOT": str(self.root / "data"),
                                                     "XDG_STATE_HOME": str(self.root / "private-state")})
        self.environment.start()
        self.addCleanup(self.environment.stop)
        self.target = {"robot_system": "paint_tray_dry"}

    def run_tool(self, flag):
        output = io.StringIO()
        with patch.object(entry.sys, "argv", ["platform", flag]), redirect_stdout(output):
            self.assertTrue(entry.dispatch_account_tool(self.target))
        return output.getvalue()

    def test_setup_is_explicit_empty_and_does_not_create_default_accounts(self):
        paths = installed_account_paths(self.root / "data", self.target)
        initial = json.loads(self.run_tool("--account-locations"))
        self.assertIsNone(initial["installation_id"])
        self.assertFalse(paths.database.exists())
        self.run_tool("--account-setup")
        installation = AccountInstallation(paths).open_existing()
        with installation.store.transaction() as transaction:
            self.assertEqual(transaction.list_accounts(), ())
        record = json.loads(self.run_tool("--account-locations"))
        self.assertEqual(record["installation_id"], installation.installation_id)
        self.assertEqual(record["operator_key"], str(paths.operator_key))
        self.run_tool("--account-setup")  # safe retry

    def test_runtime_and_installed_tools_resolve_identical_profile_paths(self):
        from src.robot_systems.paint_tray_dry.paint_robot_system import TrayDryerPaintRobotSystem
        self.assertEqual(account_installation_paths(TrayDryerPaintRobotSystem),
                         installed_account_paths(self.root / "data", self.target))

    def test_record_names_backup_location_without_exposing_key_or_password_material(self):
        paths = installed_account_paths(self.root / "data", self.target)
        self.run_tool("--account-setup")
        record = deployment_record(paths, self.root / "external-backup")
        self.assertEqual(record["backup_location"], str(self.root / "external-backup"))
        self.assertNotIn(paths.operator_key.read_text().strip(), json.dumps(record))

    def test_missing_established_store_cannot_be_reported_as_fresh(self):
        paths = installed_account_paths(self.root / "data", self.target)
        self.run_tool("--account-setup")
        paths.database.unlink()
        with self.assertRaises(SystemExit) as refused:
            self.run_tool("--account-locations")
        self.assertEqual(refused.exception.code, 4)
        self.assertFalse(paths.database.exists())

    def test_tool_mode_exits_before_factory_seeding_or_gui_backend_startup(self):
        resources = self.root / "resources/config"
        resources.mkdir(parents=True)
        (resources / "release-target.json").write_text(json.dumps({**self.target, "product": "test-product"}))
        with (patch.object(entry.sys, "argv", ["platform", "--account-setup"]),
              patch.object(entry.sys, "_MEIPASS", str(resources.parent), create=True),
              patch.object(entry, "default_config_path", return_value=self.root / "absent-update-config"),
              patch.object(entry, "default_install_root", return_value=self.root),
              patch("src.engine.updates.factory_defaults.seed_factory_defaults") as seed,
              patch("src.bootstrap.run_main.main") as start,
              redirect_stdout(io.StringIO())):
            entry.main()
            seed.assert_not_called()
            start.assert_not_called()

    def test_interrupted_update_refuses_setup_without_creating_account_material(self):
        resources = self.root / "resources/config"
        resources.mkdir(parents=True)
        (resources / "release-target.json").write_text(json.dumps({**self.target, "product": "test-product"}))
        transaction = self.root / "update-state/transaction.json"
        transaction.parent.mkdir(parents=True)
        transaction.write_text("{}")
        paths = installed_account_paths(self.root / "data", self.target)
        with (patch.object(entry.sys, "argv", ["platform", "--account-setup"]),
              patch.object(entry.sys, "_MEIPASS", str(resources.parent), create=True),
              patch.object(entry, "default_config_path", return_value=self.root / "absent-update-config"),
              patch.object(entry, "default_install_root", return_value=self.root),
              patch("src.bootstrap.account_setup.main") as setup):
            with self.assertRaisesRegex(RuntimeError, "Interrupted update"):
                entry.main()
            setup.assert_not_called()
        self.assertFalse(paths.database.exists())
        self.assertFalse(paths.state.exists())
        self.assertFalse(paths.operator_key.exists())

    def test_exclusive_update_lease_prevents_account_setup(self):
        from src.engine.updates.files import lock
        resources = self.root / "resources/config"
        resources.mkdir(parents=True)
        (resources / "release-target.json").write_text(json.dumps({**self.target, "product": "test-product"}))
        paths = installed_account_paths(self.root / "data", self.target)
        with (lock(self.root / "update-state/runtime.lock"),
              patch.object(entry.sys, "argv", ["platform", "--account-setup"]),
              patch.object(entry.sys, "_MEIPASS", str(resources.parent), create=True),
              patch.object(entry, "default_config_path", return_value=self.root / "absent-update-config"),
              patch.object(entry, "default_install_root", return_value=self.root),
              patch("src.bootstrap.account_setup.main") as setup):
            with self.assertRaisesRegex(RuntimeError, "another update"):
                entry.main()
            setup.assert_not_called()
        self.assertFalse(paths.database.exists())
        self.assertFalse(paths.operator_key.exists())
