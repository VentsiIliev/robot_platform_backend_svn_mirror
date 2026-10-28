import unittest
from unittest.mock import MagicMock

from PyQt6.QtWidgets import QApplication

from pl_gui.shell.AppShell import AppShell
from src.applications.login.stub_login_application_service import _StubUser
from src.bootstrap.shell_session_controller import ShellSessionController
from src.engine.auth.user_session import UserSession


class SessionExpiryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def setUp(self):
        self.shell = AppShell([], MagicMock())
        self.addCleanup(self.shell.deleteLater)
        self.shell.close_all_apps = MagicMock()
        self.session = UserSession()
        self.session.login(_StubUser())
        self.idle, self.login = MagicMock(return_value=False), MagicMock()
        self.controller = ShellSessionController(shell=self.shell, session=self.session,
            dev_skip_login=False, show_account_button_when_dev_skip_login=False,
            show_login_view=self.login, can_close_running_apps=MagicMock(return_value=False),
            can_expire_session=self.idle)

    def test_busy_expiry_preserves_session_and_operations(self):
        self.assertFalse(self.controller.expire_session())
        self.assertTrue(self.session.is_authenticated())
        self.shell.close_all_apps.assert_not_called()
        self.login.assert_not_called()

    def test_idle_expiry_closes_views_and_returns_to_login(self):
        self.idle.return_value = True
        self.assertTrue(self.controller.expire_session())
        self.assertFalse(self.session.is_authenticated())
        self.shell.close_all_apps.assert_called_once_with(force=True)
        self.login.assert_called_once()
        self.assertEqual(self.shell._app_descriptors, [])
        self.assertTrue(self.controller.expire_session())
        self.login.assert_called_once()
