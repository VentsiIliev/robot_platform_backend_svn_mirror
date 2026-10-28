import unittest
from PyQt6.QtWidgets import QApplication
from PyQt6.QtTest import QTest
from src.applications.user_management.service.stub_user_management_service import StubUserManagementService
from src.applications.user_management.user_management_factory import UserManagementFactory
from src.applications.user_management.view.user_management_view import UserManagementView
from src.applications.user_management.controller.user_management_controller import UserManagementController


class FactoryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def build(self):
        view = UserManagementFactory().build(StubUserManagementService())
        self.addCleanup(view.deleteLater)
        self.addCleanup(view.clean_up)
        return view

    def test_base_factory_owns_controller_and_loads_asynchronously(self):
        view = self.build()
        self.assertIsInstance(view, UserManagementView)
        self.assertIsInstance(view._controller, UserManagementController)
        for _ in range(100):
            QTest.qWait(10)
            if view._table.rowCount() == 3:
                break
        self.assertEqual(view._table.rowCount(), 3)
        self.assertNotIn("Password", view._schema.get_table_headers())

    def test_two_instances_keep_independent_models_and_controllers(self):
        first, second = self.build(), self.build()
        self.assertIsNot(first._controller, second._controller)
        self.assertIsNot(first._controller._model, second._controller._model)

