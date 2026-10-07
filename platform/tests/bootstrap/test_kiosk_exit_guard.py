import os
os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')
import unittest
from types import SimpleNamespace
from unittest.mock import Mock, patch
from PyQt6.QtWidgets import QApplication, QDialog
from PyQt6.QtGui import QCloseEvent
from pl_gui.shell.AppShell import AppShell
from src.bootstrap.kiosk_exit_guard import KioskExitGuard
from src.bootstrap.startup_config import _load_ui_startup_config

class TestKioskExit(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def test_config(self):
        self.assertFalse(_load_ui_startup_config({}).kiosk_mode)
        self.assertTrue(_load_ui_startup_config({'kiosk_mode': True}).kiosk_mode)
        with self.assertRaises(RuntimeError):
            _load_ui_startup_config({'kiosk_mode': 'false'})

    def test_credentials(self):
        auth = Mock()
        guard = KioskExitGuard(auth)
        auth.verify.return_value = False
        self.assertFalse(guard.verify('wrong'))
        auth.verify.return_value = True
        self.assertTrue(guard.verify('correct'))
        auth.verify.side_effect = RuntimeError('unavailable')
        with self.assertLogs('src.bootstrap.kiosk_exit_guard', level='ERROR'):
            self.assertFalse(guard.verify('secret'))

    def test_cancel(self):
        with patch.object(QDialog, 'exec', return_value=QDialog.DialogCode.Rejected):
            self.assertFalse(KioskExitGuard(Mock())())

    def test_close_gate(self):
        for guard, allowed in [(lambda: False, False), (lambda: True, True), (None, True)]:
            shell = AppShell([], lambda _: None, close_guard=guard)
            with patch.object(shell, 'cleanup') as cleanup:
                event = QCloseEvent()
                shell.closeEvent(event)
                self.assertEqual(event.isAccepted(), allowed)
                self.assertEqual(cleanup.call_count, int(allowed))
            shell.deleteLater()

    def test_reentrant_close(self):
        shell = AppShell([], lambda _: None)
        shell._close_in_progress = True
        event = QCloseEvent()
        shell.closeEvent(event)
        self.assertFalse(event.isAccepted())
        shell.deleteLater()
