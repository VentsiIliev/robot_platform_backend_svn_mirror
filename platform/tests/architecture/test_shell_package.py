"""Verify that the shell can be distributed without the platform checkout."""

import ast
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tarfile
import tempfile
import tomllib
import unittest
import zipfile


ROOT = Path(__file__).resolve().parents[2]
SHELL = ROOT / "pl_gui"


class TestShellBoundary(unittest.TestCase):
    def test_shell_has_no_platform_imports(self):
        # Optional legacy dashboard style fallback; tracked in the migration plan.
        legacy = {("dashboard/widgets/RobotTrajectoryWidget.py", "src.dashboard.resources.styles")}
        actual = set()
        for path in SHELL.rglob("*.py"):
            for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
                modules = []
                if isinstance(node, ast.Import):
                    modules = [alias.name for alias in node.names]
                elif isinstance(node, ast.ImportFrom) and not node.level:
                    modules = [node.module or ""]
                for module in modules:
                    if module == "src" or module.startswith("src."):
                        actual.add((path.relative_to(SHELL).as_posix(), module))
        self.assertEqual(actual, legacy)

    def test_metadata_covers_existing_subpackages(self):
        metadata = tomllib.loads((SHELL / "pyproject.toml").read_text())
        packages = {"pl_gui"}
        packages.update(
            "pl_gui." + ".".join(path.parent.relative_to(SHELL).parts)
            for path in SHELL.rglob("__init__.py") if path.parent != SHELL
        )
        self.assertEqual(set(metadata["tool"]["setuptools"]["packages"]), packages)


class TestShellDistribution(unittest.TestCase):
    def test_standalone_sdist_wheel_and_installed_shell(self):
        with tempfile.TemporaryDirectory(prefix="robot-shell-") as temporary:
            root = Path(temporary)
            source = root / "source"
            shutil.copytree(SHELL, source, ignore=shutil.ignore_patterns(
                "__pycache__", "*.egg-info", "build", "dist"))
            artifacts = root / "artifacts"
            artifacts.mkdir()
            self._run([sys.executable, "-c",
                       "from setuptools.build_meta import build_sdist; "
                       f"build_sdist({str(artifacts)!r})"], source)
            sdist = next(artifacts.glob("*.tar.gz"))
            unpacked = root / "unpacked"
            unpacked.mkdir()
            with tarfile.open(sdist) as archive:
                archive.extractall(unpacked, filter="data")
            sdist_source = next(unpacked.iterdir())
            self._run([sys.executable, "-c",
                       "from setuptools.build_meta import build_wheel; "
                       f"build_wheel({str(artifacts)!r})"], sdist_source)
            wheel = next(artifacts.glob("*.whl"))
            with zipfile.ZipFile(wheel) as archive:
                names = set(archive.namelist())
                expected = {"pl_gui/" + path.relative_to(SHELL).as_posix()
                            for path in SHELL.rglob("*.py")}
                self.assertTrue(expected <= names, sorted(expected - names))
                for resource in ("shell/resources/logo.ico", "dashboard/resources/logo.ico",
                                 "dashboard/resources/Background_&_Logo_white.png"):
                    self.assertIn("pl_gui/" + resource, names)
                self.assertFalse(any(name.startswith("src/") for name in names))
            installed = root / "installed"
            self._run([sys.executable, "-m", "pip", "install", "--no-deps", "--no-index",
                       "--target", str(installed), str(wheel)], root)
            smoke = '''
import importlib.abc
import importlib.resources
import sys
from pathlib import Path
sys.path.insert(0, sys.argv[1])
class BlockPlatform(importlib.abc.MetaPathFinder):
    def find_spec(self, fullname, path=None, target=None):
        if fullname == "src" or fullname.startswith("src."):
            raise AssertionError("Shell attempted a platform import: " + fullname)
sys.meta_path.insert(0, BlockPlatform())
from PyQt6.QtWidgets import QApplication, QWidget
from pl_gui.shell.AppShell import AppShell
from pl_gui.settings.settings_menu.settings_menu import SettingsNavigationWidget
from pl_gui.settings.app.basic_settings_app_widget import BasicSettingsAppWidget
from pl_gui.settings.settings_view import SettingsView
import pl_gui
assert Path(pl_gui.__file__).is_relative_to(Path(sys.argv[1]))
app = QApplication([])
def make_widget(name):
    return QWidget()
shell = AppShell([], make_widget)
settings = SettingsNavigationWidget([], {})
shell.show()
settings.show()
app.processEvents()
for resource in ("shell/resources/logo.ico", "dashboard/resources/logo.ico",
                 "dashboard/resources/Background_&_Logo_white.png"):
    assert importlib.resources.files("pl_gui").joinpath(resource).read_bytes()
shell.close()
settings.close()
app.processEvents()
'''
            self._run([sys.executable, "-I", "-c", smoke, str(installed)], root,
                      env={**os.environ, "QT_QPA_PLATFORM": "offscreen"})

    def _run(self, command, directory, env=None):
        result = subprocess.run(command, cwd=directory, env=env, text=True,
                                stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=60)
        self.assertEqual(result.returncode, 0, result.stdout)


if __name__ == "__main__":
    unittest.main()
