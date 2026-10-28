import threading
import unittest
from unittest.mock import MagicMock

from PyQt6.QtTest import QTest
from PyQt6.QtWidgets import QApplication

from src.applications.login.controller.login_controller import LoginController
from src.applications.login.model.login_model import LoginModel
from src.applications.login.stub_login_application_service import StubLoginApplicationService
from src.applications.login.i_login_application_service import LoginSuccess, LoginFailure, LoginError, LoginErrorCode


class _LoginStub(StubLoginApplicationService):
    def __init__(self):
        self.calls = []
        self.result = super().authenticate("1", "demo")
        self.first_run = False
        self.recovery_calls = []

    def authenticate(self, user_id, password):
        self.calls.append((user_id, password, threading.get_ident()))
        return self.result

    def is_first_run(self):
        return LoginSuccess(self.first_run)

    def recover_admin(self, command):
        self.recovery_calls.append(command)
        return super().recover_admin(command)


class LoginControllerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def setUp(self):
        self.service = _LoginStub()
        self.view = MagicMock()
        self.controller = LoginController(LoginModel(self.service), self.view)
        self.controller.load()
        self.addCleanup(self.controller.stop)

    def wait(self):
        for _ in range(100):
            QTest.qWait(10)
            if not self.controller.has_running_workers():
                return
        self.fail("Login worker did not finish")

    def test_login_runs_off_gui_thread_and_delivers_result(self):
        gui_thread = threading.get_ident()
        self.controller._on_login_submitted("42", " secret ")
        self.wait()
        self.assertEqual(self.service.calls[0][:2], ("42", " secret "))
        self.assertNotEqual(self.service.calls[0][2], gui_thread)
        self.view.accept_login.assert_called_once_with(self.service.result.value)

    def test_invalid_input_never_starts_authentication(self):
        self.controller._on_login_submitted("", "secret")
        self.assertEqual(self.service.calls, [])
        self.view.show_error.assert_called_once()

    def test_repeated_submission_cannot_start_duplicate_authentication(self):
        self.controller._on_login_submitted("42", "secret")
        self.controller._on_login_submitted("42", "second")
        self.wait()
        self.assertEqual(len(self.service.calls), 1)

    def test_rate_limit_is_shown_without_accepting_login(self):
        self.service.result = LoginFailure(LoginError(LoginErrorCode.RATE_LIMITED))
        self.controller._on_login_submitted("42", "secret")
        self.wait()
        self.assertIn("Too many attempts", self.view.show_error.call_args.args[0])
        self.view.accept_login.assert_not_called()

    def test_first_customer_setup_is_a_worker_query(self):
        self.service.first_run = True
        self.controller._on_setup_confirmed()
        self.wait()
        self.view.show_first_run.assert_called_once()
        self.view.show_login.assert_not_called()

    def test_recovery_displays_replacements_and_requires_normal_login(self):
        self.controller._on_recovery_submitted("42", "saved-code", "replacement")
        self.wait()
        self.view.show_replacement_codes.assert_called_once()
        self.view.show_login.assert_called_once()
        self.view.accept_login.assert_not_called()
        self.assertEqual(self.service.calls, [])

    def test_worker_exception_never_exposes_exception_text(self):
        self.service.authenticate = MagicMock(side_effect=RuntimeError("password=do-not-show"))
        self.controller._on_login_submitted("42", "secret")
        self.wait()
        self.assertNotIn("do-not-show", self.view.show_error.call_args.args[0])
        self.view.accept_login.assert_not_called()

    def test_stop_unsubscribes_named_broker_callback(self):
        messaging = MagicMock()
        controller = LoginController(LoginModel(self.service), MagicMock(), messaging)
        controller.load()
        controller.stop()
        messaging.unsubscribe.assert_called_once_with(*messaging.subscribe.call_args.args)
        controller.stop()
        self.assertEqual(messaging.unsubscribe.call_count, 1)

    def test_stopped_controller_ignores_new_authentication_requests(self):
        self.controller.stop()
        self.controller._on_login_submitted("42", "secret")
        self.assertEqual(self.service.calls, [])
