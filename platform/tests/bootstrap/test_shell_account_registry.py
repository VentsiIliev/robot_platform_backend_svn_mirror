from types import SimpleNamespace
import unittest
from unittest.mock import MagicMock

from PyQt6.QtTest import QTest
from PyQt6.QtWidgets import QApplication

from pl_gui.shell.AppShell import AppShell
from pl_gui.shell.base_app_widget.AppWidget import AppWidget
from src.applications.base.widget_application import WidgetApplication
from src.applications.login.stub_login_application_service import _StubUser
from src.bootstrap.shell_account_access import ShellAccountAccess
from src.bootstrap.shell_application_registry import replace_shell_applications
from src.engine.auth.user_session import UserSession
from src.shared_contracts.accounts.sessions import AccountSessionStatus
from src.shared_contracts.authorization.results import Success
from src.shared_contracts.declarations.system_specs import ApplicationSpec


class ShellAccountRegistryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def test_cached_direct_navigation_and_descriptor_refresh_keep_the_access_gate(self):
        shell = AppShell([], MagicMock())
        self.addCleanup(shell.deleteLater)
        session = UserSession()
        session.login(_StubUser())
        widget = AppWidget("Accounts")
        spec = ApplicationSpec(name="Accounts", folder_id=1, icon="",
                               factory=MagicMock(return_value=WidgetApplication(lambda _ms: widget)))
        navigation = MagicMock()
        navigation.get_visible_apps.return_value = [spec]
        navigation.can_access.return_value = True
        runtime = SimpleNamespace(sessions=MagicMock())
        runtime.sessions.status.return_value = Success(AccountSessionStatus(session.snapshot().revision, True))
        def replace(specs):
            replace_shell_applications(shell, object(), MagicMock(), specs, access, show_folders=False)
        access = ShellAccountAccess(shell=shell, session=session, runtime=runtime, navigation=navigation,
            specifications=[spec], replace_navigation=replace, expire_session=MagicMock(return_value=True),
            read_operation_idle=MagicMock(return_value=True))
        self.addCleanup(access.stop)
        access.start()
        access._timer.stop()
        access.refresh()
        self.wait(access)
        with self.assertRaises(PermissionError):
            shell.create_app("Accounts")
        self.assertIsNone(shell.show_app("Accounts"))
        self.wait(access)
        self.assertIs(shell.stacked_widget.currentWidget(), widget)
        self.assertEqual(shell.current_running_app, "Accounts")
        replace([spec])
        self.assertIs(shell.stacked_widget.currentWidget(), widget)
        self.assertEqual(shell.stacked_widget.indexOf(shell.folders_page), 0)
        navigation.can_access.return_value = False
        shell.stacked_widget.setCurrentWidget(shell.folders_page)
        self.assertIsNone(shell.show_app("Accounts"))
        self.wait(access)
        self.assertIs(shell.stacked_widget.currentWidget(), shell.folders_page)
        spec.factory.assert_called_once()
        shell.close_all_apps(force=True)

    def wait(self, access):
        for _ in range(100):
            QTest.qWait(10)
            if not access.has_running_workers():
                return
        self.fail("Shell authorization worker did not finish")
