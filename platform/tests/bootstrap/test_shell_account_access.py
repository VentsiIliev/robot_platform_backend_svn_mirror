from types import SimpleNamespace
import unittest
from unittest.mock import MagicMock

from PyQt6.QtTest import QTest
from PyQt6.QtWidgets import QApplication, QWidget

from src.bootstrap.shell_account_access import ShellAccountAccess, _NavigationState
from src.engine.auth.user_session import UserSession
from src.applications.login.stub_login_application_service import _StubUser
from src.shared_contracts.accounts.sessions import AccountSessionStatus
from src.shared_contracts.authorization.results import Success


class _Shell(QWidget):
    current_running_app = None

    def __init__(self):
        super().__init__()
        self.guard = None
        self.opened = []
        self.factory = MagicMock(return_value=object())
        self.create = self.factory

    def set_application_access_guard(self, guard):
        self.guard = guard

    def show_app(self, name):
        if self.guard(name):
            self.opened.append(name)
            return self.create(name)


class ShellAccessTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def setUp(self):
        self.shell = _Shell()
        self.session = UserSession()
        self.user = _StubUser()
        self.session.login(self.user)
        self.spec = SimpleNamespace(name="Dashboard", app_id="dashboard")
        self.navigation = MagicMock()
        self.navigation.get_visible_apps.return_value = [self.spec]
        self.navigation.can_access.return_value = True
        self.runtime = SimpleNamespace(sessions=MagicMock())
        self.runtime.sessions.status.return_value = Success(AccountSessionStatus(self.session.snapshot().revision, True))
        self.replace, self.expire = MagicMock(), MagicMock(return_value=True)
        self.idle = MagicMock(return_value=True)
        self.access = ShellAccountAccess(shell=self.shell, session=self.session, runtime=self.runtime,
            navigation=self.navigation, specifications=[self.spec], replace_navigation=self.replace,
            expire_session=self.expire, read_operation_idle=self.idle)
        self.access.start()
        self.access._timer.stop()
        self.shell.create = self.access.guard_factory(self.shell.factory)
        self.addCleanup(self.shell.deleteLater)
        self.addCleanup(self.access.stop)
        self.access.refresh()
        self.wait()

    def wait(self):
        for _ in range(100):
            QTest.qWait(10)
            if not self.access.has_running_workers():
                return
        self.fail("Navigation worker did not finish")

    def test_opening_waits_for_authorization_before_creating_widget(self):
        self.assertIsNone(self.shell.show_app("Dashboard"))
        self.shell.factory.assert_not_called()
        self.wait()
        self.assertEqual(self.shell.opened, ["Dashboard"])
        self.shell.factory.assert_called_once_with("Dashboard")

    def test_direct_factory_and_unknown_navigation_are_denied(self):
        with self.assertRaises(PermissionError):
            self.shell.create("Dashboard")
        self.assertFalse(self.access.can_open("Unregistered"))
        self.shell.factory.assert_not_called()

    def test_previously_opened_app_is_reauthorized_and_denial_blocks_reopening(self):
        self.shell.show_app("Dashboard")
        self.wait()
        self.navigation.can_access.return_value = False
        self.shell.show_app("Dashboard")
        self.wait()
        self.assertEqual(self.shell.opened, ["Dashboard"])
        self.assertEqual(self.navigation.can_access.call_count, 2)

    def test_queued_grant_cannot_cross_logout_and_relogin(self):
        old = self.session.snapshot().revision
        self.session.logout()
        self.session.login(self.user)
        self.access._opening_authorized("Dashboard", old, True)
        self.assertEqual(self.shell.opened, [])

    def test_stale_navigation_batch_cannot_replace_new_session_descriptors(self):
        old = self.session.snapshot().revision
        self.replace.reset_mock()
        self.session.login(self.user)
        self.access._navigation_loaded(_NavigationState(old, True, ()))
        self.replace.assert_not_called()

    def test_invalid_session_requests_expiry_without_operating_robot(self):
        self.runtime.sessions.status.return_value = Success(AccountSessionStatus(self.session.snapshot().revision, False))
        self.access.refresh()
        self.wait()
        self.expire.assert_called_once()

    def test_revoking_current_app_requests_session_expiry(self):
        self.shell.current_running_app = "Dashboard"
        self.navigation.get_visible_apps.return_value = []
        self.access.refresh()
        self.wait()
        self.expire.assert_called_once()

    def test_revoking_hidden_cached_app_also_expires_session(self):
        self.shell.running_widgets = {"RemovedApp": object()}
        self.access.refresh()
        self.wait()
        self.expire.assert_called_once()

    def test_permission_refresh_rebuilds_visible_navigation(self):
        self.navigation.get_visible_apps.return_value = []
        self.access.refresh()
        self.wait()
        self.replace.assert_called_with(())

    def test_late_worker_result_after_stop_cannot_open_a_widget(self):
        revision = self.session.snapshot().revision
        self.access.stop()
        self.access._opening_authorized("Dashboard", revision, True)
        self.assertEqual(self.shell.opened, [])

    def test_invalid_session_waits_until_operation_is_idle(self):
        self.idle.return_value = False
        self.access._request_expiry()
        self.wait()
        self.expire.assert_not_called()
        self.assertFalse(self.access.can_open("Dashboard"))
        self.idle.return_value = True
        self.access._retry_expiry()
        self.wait()
        self.expire.assert_called_once()
        self.assertIsNone(self.access._pending_expiry)

    def test_widget_worker_delays_expiry_even_when_robot_is_idle(self):
        self.expire.return_value = False
        self.access._request_expiry()
        self.wait()
        self.assertIsNotNone(self.access._pending_expiry)
        self.expire.return_value = True
        self.access._retry_expiry()
        self.wait()
        self.assertIsNone(self.access._pending_expiry)

    def test_unknown_activity_does_not_expire_the_session(self):
        self.idle.side_effect = RuntimeError("unavailable")
        self.access._request_expiry()
        self.wait()
        self.expire.assert_not_called()
        self.assertIsNotNone(self.access._pending_expiry)

    def test_queued_expiry_cannot_log_out_a_new_session(self):
        revision = self.session.snapshot().revision
        self.session.login(self.user)
        self.access._idle_checked(revision, True)
        self.expire.assert_not_called()

    def test_failed_query_from_old_session_cannot_expire_new_session(self):
        revision = self.session.snapshot().revision
        self.session.login(self.user)
        self.access._navigation_failed(revision, "storage unavailable")
        self.expire.assert_not_called()
        self.assertIsNone(self.access._pending_expiry)
