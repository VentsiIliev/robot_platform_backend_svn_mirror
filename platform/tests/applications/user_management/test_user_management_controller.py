from dataclasses import replace
import unittest
from unittest.mock import MagicMock, patch

from PyQt6.QtTest import QTest
from PyQt6.QtWidgets import QApplication

from src.applications.user_management.service.stub_user_management_service import StubUserManagementService
from src.applications.user_management.service.i_user_management_service import (
    SecretDisplay, UserSuccess, UserFailure, UserError, UserErrorCode,
)
from src.applications.base.widgets.private_text_dialog import PrivateTextDialog
from src.applications.user_management.user_management_factory import UserManagementFactory


class _RestrictedStub(StubUserManagementService):
    def __init__(self):
        super().__init__()
        self.permissions_reads = 0
        self.current_revision = 1
        self.allow_permissions = False

    def session_revision(self):
        return self.current_revision

    def load_users(self):
        result = super().load_users()
        return UserSuccess(replace(result.value, session_revision=self.current_revision))

    def access(self, target_id):
        result = super().access(target_id)
        controls = tuple(replace(control, visible=self.allow_permissions, role_eligible=self.allow_permissions,
                                 allowed=self.allow_permissions) if control.key == "permissions" else control
                         for control in result.value.controls)
        return UserSuccess(replace(result.value, controls=controls, session_revision=self.current_revision))

    def permissions(self):
        self.permissions_reads += 1
        return super().permissions()


class ControllerAccessTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def setUp(self):
        self.service = _RestrictedStub()
        self.view = UserManagementFactory().build(self.service)
        self.controller = self.view._controller
        self.wait()
        self.controller._timer.stop()
        self.addCleanup(self.view.deleteLater)
        self.addCleanup(self.view.clean_up)

    def wait(self):
        for _ in range(150):
            QTest.qWait(10)
            child = self.controller._permissions
            if not self.controller.has_running_workers() and (child is None or not child.has_running_workers()):
                return
        self.fail("Account workers did not finish")

    def test_denied_permissions_tab_is_hidden_and_data_is_never_loaded(self):
        self.assertFalse(self.view._tabs.isTabVisible(1))
        self.assertEqual(self.service.permissions_reads, 0)
        self.view._tabs.setCurrentIndex(1)
        self.assertEqual(self.view._tabs.currentIndex(), 0)
        self.assertFalse(hasattr(self.view, "_permissions_view"))

    def test_permission_data_is_created_only_after_feature_grant(self):
        self.service.allow_permissions = True
        self.controller._request_access()
        self.wait()
        self.assertTrue(self.view._tabs.isTabVisible(1))
        self.assertEqual(self.service.permissions_reads, 1)

    def test_permission_tab_stays_selected_during_an_allowed_refresh(self):
        self.service.allow_permissions = True
        self.controller._request_access()
        self.wait()
        self.view._tabs.setCurrentIndex(1)
        self.controller._request_access()
        self.wait()
        self.assertEqual(self.view._tabs.currentIndex(), 1)

    def test_selection_does_not_expose_privileged_passwords(self):
        self.view._table.selectRow(0)
        self.wait()
        self.assertTrue(self.view._btn_reveal.isHidden())
        self.view._table.selectRow(1)
        self.wait()
        self.assertFalse(self.view._btn_reveal.isHidden())
        self.assertTrue(self.view._btn_reveal.isEnabled())

    def test_late_permission_response_cannot_grant_the_previous_selection(self):
        jobs = []
        with patch.object(self.controller, "_run_in_thread", side_effect=lambda fn, done, error: jobs.append((fn, done))):
            self.view._table.selectRow(1)
            first = jobs.pop(0)
            self.view._table.selectRow(0)
            first[1](first[0]())
            self.assertTrue(self.view._btn_reveal.isHidden())
            second = jobs.pop(0)
            second[1](second[0]())
            self.assertTrue(self.view._btn_reveal.isHidden())

    def test_busy_state_survives_a_permission_refresh(self):
        self.view._table.selectRow(1)
        self.wait()
        self.controller._busy = True
        self.controller._operational()
        result = self.service.access("demo-operator")
        self.controller._access_loaded(self.controller._epoch, result)
        self.assertFalse(self.view._btn_password.isEnabled())
        self.controller._busy = False

    def test_late_user_page_cannot_cross_session_switch(self):
        old = self.service.load_users()
        self.service.current_revision += 1
        self.controller._users_loaded(old)
        self.assertEqual(self.view._table.rowCount(), 0)
        self.assertIsNone(self.controller._model.page)

    def test_direct_signal_cannot_use_a_different_target_than_selection(self):
        self.view._table.selectRow(1)
        self.wait()
        other = self.service.load_users().value.users[0]
        with patch.object(self.view, "ask_form") as dialog:
            self.controller._on_password(other)
        dialog.assert_not_called()

    def test_closed_binding_ignores_late_worker_callbacks(self):
        result = self.service.access("demo-operator")
        self.controller.stop()
        self.controller._access_loaded(self.controller._epoch, result)
        self.assertTrue(self.view._btn_password.isHidden())

    def test_secret_result_cannot_be_displayed_after_session_switch(self):
        revision = self.service.session_revision()
        self.service.current_revision += 1
        with patch.object(self.view, "display_secret") as display:
            self.controller._delivered(self.controller._revealed, revision, UserSuccess(SecretDisplay("private")))
        display.assert_not_called()
        self.assertEqual(self.view._table.rowCount(), 0)

    def test_access_query_failure_clears_previously_loaded_data_and_private_text(self):
        self.service.allow_permissions = True
        self.controller._request_access()
        self.wait()
        dialog = PrivateTextDialog("Operator password", "Keep this password private.", "private-value", self.view)
        self.view._private_dialog = dialog
        failure = UserFailure(UserError(UserErrorCode.AUTHENTICATION_REQUIRED))
        with patch.object(self.service, "access", return_value=failure):
            self.controller._access_loaded(self.controller._epoch, failure)
            self.wait()
        self.assertEqual(dialog._text.toPlainText(), "")
        self.assertEqual(self.view._table.rowCount(), 0)
        self.assertIsNone(self.controller._model.page)
        self.assertIsNone(self.controller._permissions)
        self.assertFalse(self.view._tabs.isTabVisible(1))

