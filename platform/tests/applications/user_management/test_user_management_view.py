import tempfile
import sys
import unittest
from pathlib import Path

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout

from src.applications.user_management.domain.default_schema import DEFAULT_USER_SCHEMA
from src.applications.user_management.domain.user_schema import UserRecord
from src.applications.user_management.service.stub_user_management_service import StubUserManagementService
from src.applications.user_management.user_management_factory import UserManagementFactory
from src.applications.user_management.view.user_management_view import UserManagementView
from src.engine.localization.localization_service import LocalizationService
from pl_gui.shell.ui.LanguageSelectorWidget import LanguageSelectorWidget


def _record(uid, first="Alice", last="Test", role="Admin", email="a@b.com"):
    return UserRecord({"id": uid, "firstName": first, "lastName": last,
                       "password": "secret", "role": role, "email": email})


class TestUserManagementViewSetUsers(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        from PyQt6.QtWidgets import QApplication
        cls._app = QApplication.instance() or QApplication(sys.argv)
        cls._view = UserManagementView(schema=DEFAULT_USER_SCHEMA)

    def test_set_users_populates_rows(self):
        self._view.set_users([_record("1"), _record("2")])
        self.assertEqual(self._view._table.rowCount(), 2)

    def test_set_users_replaces_previous_rows(self):
        self._view.set_users([_record("1"), _record("2"), _record("3")])
        self._view.set_users([_record("4")])
        self.assertEqual(self._view._table.rowCount(), 1)

    def test_set_users_empty_clears_table(self):
        self._view.set_users([_record("1")])
        self._view.set_users([])
        self.assertEqual(self._view._table.rowCount(), 0)

    def test_passwords_are_absent_from_the_table_schema(self):
        self._view.set_users([_record("1")])
        # Password column index in DEFAULT_USER_SCHEMA table fields
        headers = DEFAULT_USER_SCHEMA.get_table_headers()
        self.assertNotIn("Password", headers)

    def test_set_users_stores_record_in_user_role(self):
        record = _record("42")
        self._view.set_users([record])
        stored = self._view._table.item(0, 0).data(Qt.ItemDataRole.UserRole)
        self.assertEqual(stored.get("id"), "42")

    def test_actor_columns_render_readable_labels_and_retain_stable_actor_identity(self):
        from src.applications.user_management.model.user_management_model import UserManagementModel
        from src.applications.user_management.service.i_user_management_service import NewUser

        service = StubUserManagementService()
        created = service.create(NewUser("5", "New", "Operator", "Operator", "secret")).value
        model = UserManagementModel(service, permissions_model=None)
        model.page = model.load().value
        self._view.set_users(model.filtered_users("id", "5"))
        fields = DEFAULT_USER_SCHEMA.get_table_fields()
        for key in ("created_by_label", "updated_by_label"):
            column = next(index for index, field in enumerate(fields) if field.key == key)
            self.assertEqual(self._view._table.item(0, column).text(), "Service Engineer (3)")
        stored = self._view._table.item(0, 0).data(Qt.ItemDataRole.UserRole)
        self.assertEqual(stored.created_by, created.created_by)


class TestUserManagementViewSetStatus(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        from PyQt6.QtWidgets import QApplication
        cls._app = QApplication.instance() or QApplication(sys.argv)
        cls._view = UserManagementView(schema=DEFAULT_USER_SCHEMA)

    def test_set_status_updates_label(self):
        self._view.set_status("5 users loaded")
        self.assertEqual(self._view._status.text(), "5 users loaded")

    def test_set_status_empty(self):
        self._view.set_status("")
        self.assertEqual(self._view._status.text(), "")


class TestUserManagementViewSelectedRecord(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        from PyQt6.QtWidgets import QApplication
        cls._app = QApplication.instance() or QApplication(sys.argv)

    def setUp(self):
        self._view = UserManagementView(schema=DEFAULT_USER_SCHEMA)

    def test_selected_record_returns_none_when_no_selection(self):
        self._view.set_users([_record("1")])
        self.assertIsNone(self._view.selected_record())

    def test_selected_record_returns_record_after_selection(self):
        self._view.set_users([_record("7", first="Bob")])
        self._view._table.selectRow(0)
        record = self._view.selected_record()
        self.assertIsNotNone(record)
        self.assertEqual(record.get("id"), "7")
        self.assertEqual(record.get("firstName"), "Bob")


class TestUserManagementViewButtonStates(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        from PyQt6.QtWidgets import QApplication
        cls._app = QApplication.instance() or QApplication(sys.argv)

    def setUp(self):
        self._view = UserManagementView(schema=DEFAULT_USER_SCHEMA)

    def test_edit_delete_qr_buttons_disabled_initially(self):
        self.assertFalse(self._view._btn_edit.isEnabled())
        self.assertFalse(self._view._btn_delete.isEnabled())
        self.assertFalse(self._view._btn_qr.isEnabled())

    def test_selection_cannot_regrant_buttons_owned_by_access_binding(self):
        self._view.set_users([_record("1")])
        self._view._table.selectRow(0)
        self.assertFalse(self._view._btn_edit.isEnabled())
        self.assertFalse(self._view._btn_delete.isEnabled())
        self.assertFalse(self._view._btn_qr.isEnabled())

    def test_buttons_disabled_after_table_cleared(self):
        self._view.set_users([_record("1")])
        self._view._table.selectRow(0)
        self._view.set_users([])  # clears rows → currentRow() returns -1
        self.assertFalse(self._view._btn_edit.isEnabled())
        self.assertFalse(self._view._btn_delete.isEnabled())
        self.assertFalse(self._view._btn_qr.isEnabled())


class TestUserManagementViewSignals(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        from PyQt6.QtWidgets import QApplication
        cls._app = QApplication.instance() or QApplication(sys.argv)

    def setUp(self):
        self._view = UserManagementView(schema=DEFAULT_USER_SCHEMA)

    def test_add_button_emits_add_requested(self):
        received = []
        self._view.add_requested.connect(lambda: received.append(True))
        self._view._btn_add.click()
        self.assertTrue(received)

    def test_refresh_button_emits_refresh_requested(self):
        received = []
        self._view.refresh_requested.connect(lambda: received.append(True))
        self._view._btn_refresh.click()
        self.assertTrue(received)

    def test_edit_button_emits_edit_requested_with_record(self):
        received = []
        self._view.edit_requested.connect(lambda r: received.append(r))
        self._view.set_users([_record("5", first="Eve")])
        self._view._table.selectRow(0)
        self._view._btn_edit.setEnabled(True)
        self._view._btn_edit.click()
        self.assertEqual(len(received), 1)
        self.assertEqual(received[0].get("id"), "5")

    def test_delete_button_emits_delete_requested_with_record(self):
        received = []
        self._view.delete_requested.connect(lambda r: received.append(r))
        self._view.set_users([_record("3")])
        self._view._table.selectRow(0)
        self._view._btn_delete.setEnabled(True)
        self._view._btn_delete.click()
        self.assertEqual(len(received), 1)
        self.assertEqual(received[0].get("id"), "3")

    def test_qr_button_emits_qr_requested_with_record(self):
        received = []
        self._view.qr_requested.connect(lambda r: received.append(r))
        self._view.set_users([_record("9")])
        self._view._table.selectRow(0)
        self._view._btn_qr.setEnabled(True)
        self._view._btn_qr.click()
        self.assertEqual(len(received), 1)
        self.assertEqual(received[0].get("id"), "9")

    def test_filter_button_emits_filter_changed(self):
        received = []
        self._view.filter_changed.connect(lambda col, val: received.append((col, val)))
        self._view._filter_input.setText("alice")
        self._view._filter_col.setCurrentIndex(1)  # First non-"All" column
        # Click the Filter button
        from PyQt6.QtWidgets import QPushButton
        btns = self._view.findChildren(QPushButton)
        filter_btn = next((b for b in btns if b.text() == "Filter"), None)
        if filter_btn:
            filter_btn.click()
        self.assertTrue(len(received) > 0)

    def test_clear_button_resets_filter_and_emits_all(self):
        received = []
        self._view.filter_changed.connect(lambda col, val: received.append((col, val)))
        self._view._filter_input.setText("something")
        from PyQt6.QtWidgets import QPushButton
        btns = self._view.findChildren(QPushButton)
        clear_btn = next((b for b in btns if b.text() == "Clear"), None)
        if clear_btn:
            clear_btn.click()
        self.assertEqual(self._view._filter_input.text(), "")
        self.assertTrue(any(col == "" for col, _ in received))

    def test_clean_up_returns_none(self):
        self.assertIsNone(self._view.clean_up())


if __name__ == "__main__":
    unittest.main()


class TestUserManagementLocalizationRegression(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls._app = QApplication.instance() or QApplication(sys.argv)
        cls._shared_translations_dir = (
            Path(__file__).resolve().parents[3]
            / "src"
            / "applications"
            / "localization"
        )

    def setUp(self):
        self._temp_dir = tempfile.TemporaryDirectory()
        self._service = LocalizationService(
            [str(self._shared_translations_dir),
             str(self._shared_translations_dir.parent / "user_management/localization")],
            state_file=str(Path(self._temp_dir.name) / "localization.json"),
        )
        self._service.set_language("en")
        self.addCleanup(self._service._remove_installed_translator, self._app)

        self._selector = LanguageSelectorWidget(languages=self._service.available_languages())
        self._service.sync_selector(self._selector)
        self._selector.languageChanged.connect(self._service.set_language)

        self._view = UserManagementFactory().build(StubUserManagementService())
        self._window = QWidget()
        layout = QVBoxLayout(self._window)
        layout.addWidget(self._selector)
        layout.addWidget(self._view)
        self._window.show()
        self._app.processEvents()

        from PyQt6.QtTest import QTest
        for _ in range(100):
            QTest.qWait(10)
            if not self._view._controller.has_running_workers():
                break

    def tearDown(self):
        self._window.close()
        self._view.clean_up()
        self._temp_dir.cleanup()
        self._app.processEvents()

    def test_selector_retranslates_embedded_user_management_view(self):
        self.assertEqual(self._view._title_label.text(), "User Management")
        self.assertEqual(self._view._status.text(), "3 users loaded")

        self._selector.setCurrentIndex(self._selector.findText("Български"))
        self._app.processEvents()

        self.assertEqual(self._view._title_label.text(), "Управление на потребители")
        self.assertEqual(self._view._btn_refresh.text(), "Обнови")
        self.assertEqual(self._view._status.text(), "Заредени 3 потребителя")
