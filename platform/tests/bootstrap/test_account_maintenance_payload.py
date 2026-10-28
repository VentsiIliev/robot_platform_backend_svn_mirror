import importlib.util
import os
from pathlib import Path
import subprocess
import tempfile
import unittest
import zipfile

ROOT = Path(__file__).resolve().parents[2]


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


builder = _load("account_payload_builder", ROOT / "packaging/accounts/build_payload.py")
installer = _load("account_payload_installer", ROOT / "packaging/accounts/install.py")


class AccountMaintenancePayloadTests(unittest.TestCase):
    def setUp(self):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.root = Path(directory.name)
        self.payload = self.root / "payload"
        self.archive = builder.build_payload(self.payload)

    def test_archive_runs_under_isolated_system_python_without_project_or_third_party_imports(self):
        result = subprocess.run(["/usr/bin/python3", "-I", str(self.archive), "--help"],
                                cwd="/tmp", capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("reset-manufacturer", result.stdout)
        with zipfile.ZipFile(self.archive) as archive:
            self.assertFalse(any("cryptography" in name or "storage/" in name or "robot_systems/" in name
                                 or "applications/" in name for name in archive.namelist()))
            self.assertEqual(archive.read("src/engine/auth/__init__.py"), b"")

    def test_build_is_reproducible_and_contains_no_local_credentials(self):
        again = builder.build_payload(self.root / "again")
        self.assertEqual(self.archive.read_bytes(), again.read_bytes())
        with zipfile.ZipFile(self.archive) as archive:
            self.assertTrue(all(name.endswith(".py") for name in archive.namelist()))

    def stage(self):
        stage = self.root / "installation"
        stage.mkdir(exist_ok=True, mode=0o700)
        return stage, installer.install_payload(self.payload, stage, uid=os.getuid(), gid=os.getgid())

    def test_install_uses_fixed_isolated_wrapper_and_safe_permissions(self):
        stage, command = self.stage()
        text = command.read_text()
        self.assertTrue(text.startswith("#!/bin/sh\nexec /usr/bin/python3 -I /usr/local/lib/robot-platform/accounts/"))
        archive = next(stage.glob("usr/local/lib/robot-platform/accounts/*/*.pyz"))
        self.assertEqual(archive.stat().st_mode & 0o777, 0o444)
        self.assertEqual(command.stat().st_mode & 0o777, 0o755)
        self.assertFalse((stage / "etc/sudoers.d").exists())
        self.stage()  # idempotent installation

    def test_checksum_failure_publishes_nothing(self):
        self.archive.write_bytes(b"tampered")
        stage = self.root / "installation"
        stage.mkdir(mode=0o700)
        with self.assertRaisesRegex(ValueError, "checksum"):
            installer.install_payload(self.payload, stage, uid=os.getuid(), gid=os.getgid())
        self.assertFalse((stage / "usr").exists())

    def test_symlink_or_other_writable_installation_path_is_rejected(self):
        for symlink in (False, True):
            stage = self.root / ("symlink" if symlink else "writable")
            stage.mkdir(mode=0o700)
            if symlink:
                (stage / "usr").symlink_to(self.payload, target_is_directory=True)
            else:
                (stage / "usr").mkdir(mode=0o777)
                (stage / "usr").chmod(0o777)
            with self.assertRaises(ValueError):
                installer.install_payload(self.payload, stage, uid=os.getuid(), gid=os.getgid())
