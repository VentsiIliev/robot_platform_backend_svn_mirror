import os
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import json
import time
import unittest
from pathlib import Path
from unittest.mock import Mock

from PyQt6.QtCore import QCoreApplication, QEvent, QTranslator
from PyQt6.QtWidgets import QApplication

from pl_gui.shell.ui.Header import Header
from src.bootstrap.shell_remote_support_controller import ShellRemoteSupportController, _Worker


class _Translator(QTranslator):
    def isEmpty(self):
        return False

    def translate(self, context, source, disambiguation=None, n=-1):
        path = Path("src/applications/localization/bg.json")
        return json.loads(path.read_text()).get(context, {}).get(source, source)


class ShellRemoteSupportTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def test_worker_distinguishes_service_from_sessions_and_failures(self):
        for enabled, active, count, expected in (
            (False, False, 0, "disabled"), (True, False, 0, "unavailable"),
            (True, True, 0, "ready"), (True, True, 1, "connected"),
            (False, True, 2, "connected"), (True, True, None, "unavailable"),
        ):
            with self.subTest(expected=expected, count=count):
                support, sessions = Mock(), Mock()
                support.status.return_value = {"enabled": enabled, "active": active}
                sessions.get_session_count.return_value = count
                if count is None:
                    sessions.get_session_count.side_effect = OSError("offline")
                worker = _Worker(support, sessions, 0)
                states = []
                def capture(state):
                    states.append(state)
                    worker.stopped.set()
                worker.status_updated.connect(capture)
                worker.run()
                self.assertEqual(states, [expected])
                if not active:
                    sessions.get_session_count.assert_not_called()

    def test_background_monitor_updates_header_and_stops(self):
        header = Header(1280, 900, None, None)
        support, sessions = Mock(), Mock()
        support.status.return_value = {"enabled": True, "active": True}
        sessions.get_session_count.return_value = 1
        monitor = ShellRemoteSupportController(header, support, sessions, .01)
        try:
            monitor.start()
            deadline = time.monotonic() + 2
            while header._remote_support_state != "connected" and time.monotonic() < deadline:
                self.app.processEvents()
                time.sleep(.005)
            self.assertEqual(header._remote_support_state, "connected")
            sessions.get_session_count.return_value = 0
            deadline = time.monotonic() + 2
            while header._remote_support_state != "ready" and time.monotonic() < deadline:
                self.app.processEvents()
                time.sleep(.005)
            self.assertEqual(header._remote_support_state, "ready")
        finally:
            monitor.stop()
            monitor.stop()
            self.assertFalse(monitor._thread.isRunning())
            header.close()

    def test_badge_visibility_and_initial_and_runtime_translation(self):
        header = Header(1280, 900, None, None)
        translator = _Translator()
        try:
            header.set_remote_support_state("connected")
            self.assertFalse(header.remote_support_badge.isHidden())
            self.assertEqual(header.remote_support_badge.text(), "")
            self.assertFalse(header.remote_support_badge.pixmap().isNull())
            self.assertIn("Remote session active", header.remote_support_badge.toolTip())
            QCoreApplication.installTranslator(translator)
            initially_translated = Header(1280, 900, None, None)
            initially_translated.set_remote_support_state("connected")
            self.assertIn("Активна отдалечена сесия", initially_translated.remote_support_badge.toolTip())
            initially_translated.close()
            QApplication.sendEvent(header, QEvent(QEvent.Type.LanguageChange))
            self.assertIn("Активна отдалечена сесия", header.remote_support_badge.toolTip())
            for state in ("ready", "unavailable", "disabled"):
                header.set_remote_support_state(state)
                self.assertTrue(header.remote_support_badge.isHidden())
        finally:
            QCoreApplication.removeTranslator(translator)
            header.close()
