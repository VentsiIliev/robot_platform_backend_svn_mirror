import unittest
from unittest.mock import MagicMock
from PyQt6.QtTest import QTest
from PyQt6.QtWidgets import QApplication

from src.applications.user_management.controller.permissions_controller import PermissionsController
from src.applications.user_management.model.permissions_model import PermissionsModel
from src.applications.user_management.service.stub_user_management_service import StubUserManagementService
from src.applications.user_management.service.i_user_management_service import UserError, UserErrorCode, UserFailure


class _SessionStub(StubUserManagementService):
    def __init__(self):
        super().__init__()
        self.revision = 1

    def session_revision(self):
        return self.revision


class PermissionsControllerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def setUp(self):
        self.service = _SessionStub()
        self.view = MagicMock()
        self.controller = PermissionsController(PermissionsModel(self.service), self.view)
        self.addCleanup(self.controller.stop)

    def wait(self):
        for _ in range(100):
            QTest.qWait(10)
            if not self.controller.has_running_workers():
                return
        self.fail("Permission worker did not finish")

    def test_load_and_toggle_use_workers_and_current_revision(self):
        self.controller.load()
        self.wait()
        self.view.set_permissions.assert_called_once()
        self.controller._on_permission_toggled("demo", "Operator", False)
        self.wait()
        self.assertEqual(self.view.set_permissions.call_count, 2)
        self.assertNotIn("Operator", self.view.set_permissions.call_args.args[2]["demo"])

    def test_late_result_from_prior_session_clears_the_table(self):
        self.controller._session_revision = 1
        self.service.revision = 2
        self.controller._loaded(self.service.permissions())
        self.view.set_permissions.assert_not_called()
        self.view.clear_permissions.assert_called_once()

    def test_stopped_controller_never_populates_deleted_widgets(self):
        result = self.service.permissions()
        self.controller.stop()
        self.view.reset_mock()
        self.controller._loaded(result)
        self.view.set_permissions.assert_not_called()

    def test_busy_write_gives_idle_guidance_and_allows_a_later_refresh(self):
        self.controller.load()
        self.wait()
        self.service.set_permission = MagicMock(return_value=UserFailure(UserError(UserErrorCode.BUSY)))
        self.controller._on_permission_toggled("demo", "Operator", False)
        self.wait()
        self.assertIsNone(self.controller._model.page)
        self.assertIn("idle", self.view.set_notice.call_args.args[0])
        self.controller.refresh()
        self.wait()
        self.assertIsNotNone(self.controller._model.page)
