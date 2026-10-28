from pathlib import Path
import os
import subprocess
import sys
import unittest


class QtApplicationStartupTests(unittest.TestCase):
    def test_login_web_view_can_be_imported_lazily_after_application_construction(self):
        script = '''
from src.bootstrap.qt_application import prepare_qt_application
from PyQt6.QtCore import QCoreApplication, Qt
from PyQt6.QtWidgets import QApplication
prepare_qt_application()
app = QApplication([])
assert QCoreApplication.testAttribute(Qt.ApplicationAttribute.AA_ShareOpenGLContexts)
from src.applications.login.view.login_view import LoginView
assert LoginView is not None
'''
        result = subprocess.run([sys.executable, "-B", "-c", script],
            cwd=Path(__file__).resolve().parents[2],
            env={**os.environ, "QT_QPA_PLATFORM": "offscreen", "QTWEBENGINE_DISABLE_SANDBOX": "1"},
            capture_output=True, text=True, timeout=30)
        self.assertEqual(result.returncode, 0, result.stderr)
