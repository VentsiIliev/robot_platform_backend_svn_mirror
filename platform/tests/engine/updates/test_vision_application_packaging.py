"""Paint-only bundles must be able to construct their lazy vision screens."""
import os
from pathlib import Path
import subprocess
import sys
import textwrap
import unittest


ROOT = Path(__file__).resolve().parents[3]


class TestVisionApplicationPackaging(unittest.TestCase):
    def test_vision_screens_build_with_other_robot_systems_excluded(self):
        code = textwrap.dedent("""
            import importlib.abc
            import importlib.util
            import sys

            class PaintOnlyImports(importlib.abc.MetaPathFinder):
                def find_spec(self, fullname, path=None, target=None):
                    if fullname.startswith(("src.robot_systems.glue", "src.robot_systems.welding")):
                        raise ModuleNotFoundError("Excluded robot system: " + fullname)

            sys.meta_path.insert(0, PaintOnlyImports())
            from PyQt6.QtWidgets import QApplication
            app = QApplication([])
            spec = importlib.util.spec_from_file_location(
                "platform_entrypoint", "packaging/platform/platform_entrypoint.py")
            entrypoint = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(entrypoint)
            entrypoint.check_vision_application_widgets(app)
            print("Vision application checks passed")
        """)
        result = subprocess.run(
            [sys.executable, "-c", code], cwd=ROOT,
            env={**os.environ, "QT_QPA_PLATFORM": "offscreen"},
            capture_output=True, text=True, timeout=60,
        )
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        self.assertIn("Vision application checks passed", result.stdout)
