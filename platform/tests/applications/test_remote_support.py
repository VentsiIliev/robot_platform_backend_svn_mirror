import json
import time
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch
from types import SimpleNamespace

from PyQt6.QtCore import QCoreApplication, QEvent, QPoint
from PyQt6.QtWidgets import QApplication, QLineEdit, QMainWindow
from PyQt6.QtTest import QTest

from src.applications.remote_support.remote_support_application_factory import RemoteSupportApplicationFactory
from src.applications.remote_support.service.remote_support_application_service import RemoteSupportApplicationService
from src.applications.remote_support.service.stub_remote_support_service import StubRemoteSupportService
from src.applications.remote_support.view.remote_support_view import RemoteSupportView
from src.engine.localization.dict_translator import DictTranslator
from src.robot_systems.paint.paint_robot_system import PaintRobotSystem
from src.robot_systems.paint import application_wiring


class RemoteSupportTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def wait_for(self, predicate):
        deadline = time.monotonic() + 2
        while not predicate() and time.monotonic() < deadline:
            self.app.processEvents()
            time.sleep(.005)
        self.assertTrue(predicate())

    def test_service_uses_existing_socket_client(self):
        client = MagicMock()
        client.status.return_value = {"enabled": False, "active": False, "timed_access_supported": True}
        service = RemoteSupportApplicationService(client, platform="linux")
        self.assertEqual(service.get_remote_support_status(), client.status.return_value)
        self.assertIsNone(service.set_remote_support_enabled(True))
        client.set_enabled.assert_called_once_with(True, duration_seconds=900)
        unsupported = RemoteSupportApplicationService(client, platform="win32")
        with self.assertRaisesRegex(RuntimeError, "Linux"):
            unsupported.set_remote_support_enabled(True)

    def test_switch_waits_for_confirmed_state_and_reports_mismatch_and_failure(self):
        view = RemoteSupportView()
        try:
            self.assertFalse(view._remote_switch.isEnabled())
            view.set_remote_support_status({"enabled": False, "active": False})
            requested = []
            view.remote_support_requested.connect(requested.append)
            view._remote_switch.click()
            self.assertEqual(requested, [True])
            self.assertFalse(view._remote_switch.isChecked())
            view.set_busy("remote", True)
            self.assertFalse(view._remote_switch.isEnabled())
            view.set_remote_support_status({"enabled": False, "active": True})
            self.assertIn("action needed", view._remote_state.text())
            view.set_remote_support_error("Controller unavailable")
            self.assertFalse(view._remote_switch.isEnabled())
            view.set_busy("remote", False)
            view.set_remote_support_status({"enabled": True, "active": True})
            self.assertTrue(view._remote_switch.isEnabled())
            self.assertTrue(view._remote_switch.isChecked())
        finally:
            view.close()

    def test_real_workers_enable_and_disable_without_blocking(self):
        stub = StubRemoteSupportService()
        view = RemoteSupportApplicationFactory().build(stub)
        try:
            self.wait_for(lambda: view._remote_switch.isEnabled())
            view._remote_switch.click()
            self.wait_for(lambda: view._remote_switch.isEnabled() and view._remote_switch.isChecked())
            self.assertTrue(stub.enabled)
            view._remote_switch.click()
            self.wait_for(lambda: view._remote_switch.isEnabled() and not view._remote_switch.isChecked())
            self.assertFalse(stub.enabled)
        finally:
            view._controller.stop()
            self.assertFalse(view._controller._remote_timer.isActive())
            view.close()

    def test_initial_and_runtime_bulgarian_translation(self):
        data = json.loads(Path('src/applications/remote_support/localization/bg.json').read_text())
        translator = DictTranslator(data)
        view = RemoteSupportApplicationFactory().build(StubRemoteSupportService())
        initially_translated = None
        try:
            view._controller._set_status("Starting remote support…")
            QCoreApplication.installTranslator(translator)
            QApplication.sendEvent(view, QEvent(QEvent.Type.LanguageChange))
            self.assertEqual(view._title.text(), data['RemoteSupportView']['Remote Support'])
            self.assertEqual(view._status.text(), data['RemoteSupportController']['Starting remote support…'])
            initially_translated = RemoteSupportView()
            self.assertEqual(initially_translated._title.text(), data['RemoteSupportView']['Remote Support'])
        finally:
            view._controller.stop()
            QCoreApplication.removeTranslator(translator)
            view.close()
            if initially_translated is not None:
                initially_translated.close()

    def test_paint_moves_control_to_administration_and_does_not_poll_it_in_network(self):
        specs = {spec.name: spec for spec in PaintRobotSystem.shell.applications}
        self.assertEqual(specs['RemoteSupport'].folder_id, 3)
        self.assertEqual(PaintRobotSystem.role_policy.protected_app_role_values['remotesupport'], ['Admin'])
        network = application_wiring._build_network_settings_application(MagicMock())
        network.register(MagicMock())
        view = network.create_widget()
        try:
            self.assertEqual(view._tabs.count(), 2)
            self.assertFalse(view.has_remote_support)
            view._controller._model.get_remote_support_status = MagicMock()
            view._controller._refresh_remote_support()
            view._controller._model.get_remote_support_status.assert_not_called()
            self.assertFalse(view._controller._remote_timer.isActive())
        finally:
            view._controller.stop()
            view.close()

    def test_password_reset_requires_platform_admin_and_never_changes_access_window(self):
        client, passwords, auth = MagicMock(), MagicMock(), MagicMock()
        service = RemoteSupportApplicationService(client, platform="linux", password_client=passwords,
                                                   authentication_service=auth)
        client.status.return_value = {"enabled":True, "active":True, "timed_access_supported":True}
        for user in (None, SimpleNamespace(role="Operator")):
            auth.authenticate.return_value = user
            with self.assertRaisesRegex(ValueError, "Administrator"):
                service.set_unattended_password('admin', 'platform-secret', 'new-remote-secret')
            passwords.set_password.assert_not_called()
        auth.authenticate.return_value = SimpleNamespace(role="Admin")
        service.set_unattended_password('admin', 'platform-secret', 'new-remote-secret')
        auth.authenticate.assert_called_with('admin', 'platform-secret')
        passwords.set_password.assert_called_once_with('new-remote-secret')
        service.remove_unattended_password('admin', 'platform-secret')
        passwords.remove_password.assert_called_once_with()
        client.set_enabled.assert_not_called()

    def test_invalid_password_and_old_controller_are_rejected_before_mutation(self):
        client, passwords, auth = MagicMock(), MagicMock(), MagicMock()
        auth.authenticate.return_value = SimpleNamespace(role='Admin')
        service = RemoteSupportApplicationService(client, platform='linux', password_client=passwords,
                                                   authentication_service=auth)
        for password in ('short', ' '*8, 'x'*65):
            with self.assertRaises(ValueError):
                service.set_unattended_password('admin', 'platform-secret', password)
        passwords.set_password.assert_not_called()
        client.status.return_value = {'enabled':False,'active':False}
        with self.assertRaisesRegex(RuntimeError, 'updated remote support controller'):
            service.set_remote_support_enabled(True, 7200)
        client.set_enabled.assert_not_called()

    def test_password_management_while_support_off_never_starts_rustdesk(self):
        client, passwords, auth = MagicMock(), MagicMock(), MagicMock()
        client.status.return_value = {'enabled':False, 'active':False, 'timed_access_supported':True}
        auth.authenticate.return_value = SimpleNamespace(role='Admin')
        service = RemoteSupportApplicationService(client, platform='linux', password_client=passwords,
                                                   authentication_service=auth)
        self.assertEqual(service.get_password_status(), {'available':False,'configured':None,'unattended_enabled':None})
        with self.assertRaisesRegex(ValueError, 'Enable timed support'):
            service.set_unattended_password('admin','platform-secret','new-remote-secret')
        with self.assertRaisesRegex(ValueError, 'Enable timed support'):
            service.remove_unattended_password('admin','platform-secret')
        client.set_enabled.assert_not_called()
        passwords.set_password.assert_not_called()
        passwords.get_password_status.assert_not_called()
        passwords.remove_password.assert_not_called()

    def test_reset_form_clears_secrets_and_preserves_expiry(self):
        stub = StubRemoteSupportService()
        stub.set_remote_support_enabled(True, 7200)
        deadline = stub.expires_at
        view = RemoteSupportApplicationFactory().build(stub)
        try:
            self.wait_for(lambda: view._remote_enabled is True and not any(view._controller._busy.values()))
            self.assertIn('01:', view._countdown.text())
            fields = view._password_fields
            for key, value in (('admin_id','admin'), ('admin_password','admin'),
                               ('password','new-test-password'), ('confirmation','new-test-password')):
                fields[key].setText(value)
            view._password_buttons['reset'].click()
            self.assertEqual(fields['admin_password'].text(), '')
            self.assertEqual(fields['password'].text(), '')
            self.assertEqual(fields['confirmation'].text(), '')
            self.wait_for(lambda: not any(view._controller._busy.values()))
            self.assertTrue(stub.get_password_status()['unattended_enabled'])
            self.assertEqual(stub.expires_at, deadline)
            fields['admin_password'].setText('admin')
            view._password_buttons['remove'].click()
            self.wait_for(lambda: not any(view._controller._busy.values()))
            self.assertFalse(stub.get_password_status()['unattended_enabled'])
            self.assertEqual(stub.expires_at, deadline)
        finally:
            view._controller.stop()
            view.close()

    def test_password_confirmation_failure_does_not_call_service(self):
        from src.applications.remote_support.model.remote_support_model import RemoteSupportModel
        service = MagicMock()
        with self.assertRaisesRegex(ValueError, 'match'):
            RemoteSupportModel(service).set_unattended_password('admin','platform-secret','one','two')
        service.set_unattended_password.assert_not_called()

    def test_status_poll_preserves_password_focus_and_typing(self):
        from src.applications.base.widgets import custom_virtual_keyboard
        with patch.object(custom_virtual_keyboard, 'ENABLE_CUSTOM_VIRTUAL_KEYBOARD', False):
            view = RemoteSupportApplicationFactory().build(StubRemoteSupportService())
            window = QMainWindow()
            window.setCentralWidget(view)
            window.show()
            try:
                self.wait_for(lambda: view._remote_enabled is not None and not any(view._controller._busy.values()))
                view._tabs.setCurrentIndex(1)
                self.wait_for(lambda: not any(view._controller._busy.values()))
                window.activateWindow()
                self.app.processEvents()
                for key in ('admin_password', 'password', 'confirmation'):
                    field = view._password_fields[key]
                    field.setFocus()
                    self.app.processEvents()
                    self.assertTrue(field.hasFocus())
                    QTest.keyClicks(field, 'abc')
                    field.setCursorPosition(1)
                    view._controller._remote_timer.timeout.emit()
                    self.assertTrue(field.isEnabled())
                    self.assertTrue(field.hasFocus())
                    self.wait_for(lambda: not any(view._controller._busy.values()))
                    self.assertTrue(field.hasFocus())
                    self.assertEqual(field.cursorPosition(), 1)
                    QTest.keyClicks(field, 'Z')
                    self.assertEqual(field.text(), 'aZbc')
            finally:
                view._controller.stop()
                window.close()

    def test_shared_keyboard_keeps_top_and_bottom_fields_visible_and_password_masked(self):
        from src.applications.base.widgets import custom_virtual_keyboard
        view = RemoteSupportApplicationFactory().build(StubRemoteSupportService())
        window = QMainWindow()
        window.setCentralWidget(view)
        window.resize(1000, 700)
        try:
            with patch.object(custom_virtual_keyboard, 'ENABLE_CUSTOM_VIRTUAL_KEYBOARD', True):
                window.show()
                self.wait_for(lambda: view._remote_enabled is not None and not any(view._controller._busy.values()))
                view._tabs.setCurrentIndex(1)
                self.wait_for(lambda: not any(view._controller._busy.values()))
                view._controller._remote_timer.stop()
                for key in ('admin_id', 'confirmation'):
                    field = view._password_fields[key]
                    field._show_keyboard()
                    self.wait_for(lambda: field._keyboard_dialog is not None and field._keyboard_dialog.isVisible())
                    dialog = field._keyboard_dialog
                    self.wait_for(lambda: field.mapToGlobal(QPoint(0, field.height())).y() < dialog.keyboard_rect_global().top())
                    field.clear()
                    dialog._append('abc')
                    dialog._move_cursor_left()
                    dialog._append('Z')
                    self.assertEqual(field.text(), 'abZc')
                    if key == 'confirmation':
                        self.assertEqual(field.echoMode(), QLineEdit.EchoMode.Password)
                        self.assertNotEqual(field.displayText(), field.text())
                    dialog.close()
                    self.app.processEvents()
        finally:
            view._controller.stop()
            view.clear_password_fields()
            window.close()
