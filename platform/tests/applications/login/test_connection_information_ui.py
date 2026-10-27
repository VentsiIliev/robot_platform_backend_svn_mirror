"""Verify pre-login access, background refresh, teardown and live translation."""

import json
import os
import threading
import time
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PyQt6.QtCore import QCoreApplication, QEvent, QPoint, Qt, pyqtSignal
from PyQt6.QtTest import QTest
from PyQt6.QtGui import QColor, QPainter
from PyQt6.QtWidgets import QApplication, QScrollArea, QWidget

from src.applications.login.login_factory import LoginFactory
from src.applications.login.stub_login_application_service import StubLoginApplicationService
from src.applications.login.view.connection_information_dialog import ConnectionInformationDialog
from src.engine.localization.dict_translator import DictTranslator
from src.shared_contracts.events.vision_events import VisionTopics
from src.applications.base.config.virtual_keyboard_config import (
    is_custom_virtual_keyboard_enabled, set_custom_virtual_keyboard_enabled,
)
from src.applications.base.widgets.custom_virtual_keyboard import KeyboardLineEdit


class _WebBackground(QWidget):
    """Keep these tests focused on native login controls, without starting Chromium."""

    loadFinished = pyqtSignal(bool)

    def load(self, _url):
        pass


class _PaintedWebBackground(_WebBackground):
    COLOR = QColor(31, 119, 78)

    def paintEvent(self, _event):
        painter = QPainter(self)
        painter.fillRect(self.rect(), self.COLOR)


class TestConnectionInformationUi(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def wait_until(self, predicate):
        deadline = time.monotonic() + 3
        while not predicate() and time.monotonic() < deadline:
            self.app.processEvents()
            time.sleep(.005)
        self.assertTrue(predicate())

    def make_login(self, service=None, messaging=None, *, background=_WebBackground):
        with patch("src.applications.login.view.login_view.QWebEngineView", background):
            view = LoginFactory.build(service or StubLoginApplicationService(), messaging)
        self.addCleanup(view.deleteLater)
        self.addCleanup(view._controller.stop)
        view.set_connection_information_guard(Mock(return_value=True))
        return view

    def test_information_is_accessible_on_setup_first_admin_and_login_pages(self):
        view = self.make_login()
        view.show()
        panel = view._connection_dialog
        for navigate in (view.show_setup, view.show_first_run, view.show_login):
            navigate()
            self.assertTrue(view._connection_info_btn.isVisible())
            view._connection_info_btn.click()
            self.wait_until(lambda: panel._hostname.text() == "robot-demo" and panel._refresh.isEnabled())
            self.assertTrue(panel.isVisible())
            self.assertEqual(panel._rustdesk.text(), "123456789")
            self.assertEqual("192.168.222.20", panel._addresses.text())
            self.assertEqual("operator", panel._username.text())
            panel._close.click()
            self.assertFalse(panel.isVisible())
            self.assertIsNone(view.result_user())

    def test_login_scroll_viewport_does_not_cover_fluid_background(self):
        view = self.make_login(background=_PaintedWebBackground)
        view.resize(1280, 800)
        view.show()
        view.show_login()
        self.app.processEvents()
        scroll = view.findChild(QScrollArea)
        point = scroll.viewport().mapTo(view, QPoint(4, scroll.viewport().height() - 4))
        rendered = view.grab().toImage()
        self.assertEqual(_PaintedWebBackground.COLOR, rendered.pixelColor(point))

    def test_refresh_runs_off_gui_thread_and_rejects_overlapping_requests(self):
        service = StubLoginApplicationService()
        release = threading.Event()
        threads = []

        def read():
            threads.append(threading.get_ident())
            release.wait(2)
            return {"hostname": "refreshed", "addresses": [], "rustdesk_id": None}

        service.get_connection_information = Mock(side_effect=read)
        view = self.make_login(service)
        self.addCleanup(release.set)
        view._connection_info_btn.click()
        self.wait_until(lambda: bool(threads))
        self.assertNotEqual(threads[0], threading.get_ident())
        self.assertFalse(view._connection_dialog._refresh.isEnabled())
        view.connection_information_requested.emit()
        self.assertEqual(service.get_connection_information.call_count, 1)
        release.set()
        self.wait_until(lambda: view._connection_dialog._refresh.isEnabled())
        self.assertEqual(view._connection_dialog._hostname.text(), "refreshed")
        self.assertEqual(view._connection_dialog._addresses.text(), "No IP addresses assigned.")
        self.assertEqual(view._connection_dialog._rustdesk.text(), "Unavailable")

    def test_failed_refresh_can_be_retried_without_exposing_raw_errors(self):
        service = StubLoginApplicationService()
        service.get_connection_information = Mock(side_effect=[
            RuntimeError("private system diagnostic"),
            {"hostname": "plp", "addresses": [], "rustdesk_id": "987654321"},
        ])
        view = self.make_login(service)
        view._connection_info_btn.click()
        panel = view._connection_dialog
        self.wait_until(lambda: panel._refresh.isEnabled())
        self.assertIn("Please try again", panel._status.text())
        self.assertNotIn("private", panel._status.text())
        panel._refresh.click()
        self.wait_until(lambda: panel._hostname.text() == "plp" and panel._refresh.isEnabled())
        self.assertEqual(panel._status.text(), "")

    def test_login_completion_stops_queries_and_unsubscribes(self):
        messaging = Mock()
        view = self.make_login(messaging=messaging)
        view._connection_info_btn.click()
        view.accept_login(object())
        self.assertTrue(view._controller._stopped)
        self.assertFalse(view._controller.has_running_workers())
        messaging.unsubscribe.assert_called_once_with(
            VisionTopics.LATEST_IMAGE, view._controller._on_camera_frame_raw,
        )
        # Results already queued when login succeeded must not touch the view.
        view._controller._connection_information_loaded({"hostname": "stale"})
        self.assertNotEqual(view._connection_dialog._hostname.text(), "stale")

    def test_bulgarian_initial_render_and_runtime_switch_preserve_identifiers(self):
        catalog = Path("src/applications/login/localization/bg.json")
        translator = DictTranslator(json.loads(catalog.read_text(encoding="utf-8")))
        self.app.installTranslator(translator)
        panel = ConnectionInformationDialog()
        self.addCleanup(panel.deleteLater)
        try:
            self.assertEqual(panel.windowTitle(), "Информация за връзката")
            self.assertEqual(panel._hostname_label.text(), "Име на компютъра:")
            panel.set_information({"hostname": "plp", "username": "pl_user", "addresses": [], "rustdesk_id": "123456789"})
            self.assertEqual(panel._username_label.text(), "PC потребител:")
            self.assertEqual(panel._username.text(), "pl_user")
            self.assertEqual(panel._addresses.text(), "Няма зададени IP адреси.")
            self.app.removeTranslator(translator)
            panel.changeEvent(QEvent(QEvent.Type.LanguageChange))
            self.assertEqual(panel._title.text(), "Connection information")
            self.assertEqual(panel._addresses.text(), "No IP addresses assigned.")
            self.assertEqual(panel._hostname.text(), "plp")
            self.assertEqual(panel._rustdesk.text(), "123456789")
            self.app.installTranslator(translator)
            panel.changeEvent(QEvent(QEvent.Type.LanguageChange))
            self.assertEqual(panel._refresh.text(), "Обнови")
            panel.set_busy(True)
            self.assertEqual(panel._status.text(), "Зареждане на информацията за връзката…")
        finally:
            self.app.removeTranslator(translator)

    def test_missing_or_denied_password_guard_cannot_open_or_refresh_information(self):
        for guard in (None, Mock(return_value=False)):
            service = StubLoginApplicationService()
            service.get_connection_information = Mock()
            view = self.make_login(service)
            view.set_connection_information_guard(guard)
            view._connection_info_btn.click()
            view.connection_information_requested.emit()
            service.get_connection_information.assert_not_called()
            self.assertFalse(view._connection_dialog.isVisible())

    def test_each_open_requires_password_and_close_clears_details_and_late_results(self):
        view = self.make_login()
        guard = Mock(return_value=True)
        view.set_connection_information_guard(guard)
        for _ in range(2):
            view._connection_info_btn.click()
            self.wait_until(lambda: view._connection_dialog._hostname.text() == "robot-demo")
            view._connection_dialog.reject()
            self.assertFalse(view.is_connection_information_authorized())
            self.assertEqual("Unavailable", view._connection_dialog._hostname.text())
            view.set_connection_information({"hostname": "late secret"})
            self.assertEqual("Unavailable", view._connection_dialog._hostname.text())
            self.wait_until(lambda: not view._controller.has_running_workers())
        self.assertEqual(2, guard.call_count)

    def test_login_and_first_admin_fields_use_shared_keyboard_and_stay_above_it(self):
        original = is_custom_virtual_keyboard_enabled()
        self.addCleanup(set_custom_virtual_keyboard_enabled, original)
        set_custom_virtual_keyboard_enabled(True)
        view = self.make_login()
        view.resize(1280, 900)
        view.show()
        for navigate, names in (
            (view.show_login, ("_uid_input", "_pw_input")),
            (view.show_first_run, ("_fa_uid", "_fa_pw")),
        ):
            navigate()
            self.app.processEvents()
            for name in names:
                field = getattr(view, name)
                self.assertIsInstance(field, KeyboardLineEdit)
                QTest.mouseClick(field, Qt.MouseButton.LeftButton)
                self.wait_until(lambda: field._keyboard_dialog is not None and field._keyboard_dialog.isVisible())
                QTest.qWait(80)
                keyboard = field._keyboard_dialog
                self.assertLess(field.mapToGlobal(QPoint(0, field.height())).y(), keyboard.keyboard_rect_global().top())
                field.clear()
                keyboard._append("test")
                self.assertEqual("test", field.text())
                keyboard.hide()
        set_custom_virtual_keyboard_enabled(False)
        QTest.mouseClick(view._fa_pw, Qt.MouseButton.LeftButton)
        self.assertFalse(view._fa_pw._keyboard_dialog.isVisible())


if __name__ == "__main__":
    unittest.main()
