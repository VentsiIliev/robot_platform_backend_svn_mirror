import tempfile
import unittest
from pathlib import Path

from PyQt6 import sip
from PyQt6.QtWidgets import QApplication

from src.applications.user_management.service.i_user_management_service import HistoryChange, HistoryEntry
from src.applications.user_management.view.account_history_dialog import AccountHistoryDialog
from src.engine.localization.localization_service import LocalizationService


class AccountHistoryDialogTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def dialog(self, entries=None):
        if entries is None:
            entries = (HistoryEntry("2026-10-28T12:00:00Z", "Alice Admin (1)", "users.edit_profile", "succeeded",
                                    (HistoryChange("first_name", "Old", "New"),)),
                       HistoryEntry("2026-10-28T11:00:00Z", "Service Engineer (900)", "users.change_password",
                                    "succeeded", password_changed=True))
        dialog = AccountHistoryDialog(entries)
        self.addCleanup(sip.delete, dialog)
        return dialog

    def test_selected_event_shows_before_after_and_password_marker_has_no_values(self):
        dialog = self.dialog()
        self.assertEqual(dialog._events.item(0, 1).text(), "Alice Admin (1)")
        self.assertEqual([dialog._changes.item(0, column).text() for column in range(3)],
                         ["First Name", "Old", "New"])
        dialog._events.selectRow(1)
        self.assertEqual(dialog._changes.rowCount(), 0)
        self.assertIn("never stored", dialog._password_notice.text())
        dialog.reject()
        self.assertEqual(dialog._entries, ())
        self.assertIsNone(dialog._events.item(0, 1))

    def test_empty_history_is_explicit(self):
        dialog = self.dialog(())
        self.assertIn("No history", dialog._notice.text())
        self.assertEqual(dialog._events.rowCount(), 0)

    def test_initial_and_runtime_translation_preserve_selection_and_user_data(self):
        root = Path(__file__).resolve().parents[3] / "src/applications/user_management/localization"
        with tempfile.TemporaryDirectory() as directory:
            localization = LocalizationService(str(root), state_file=str(Path(directory) / "language.json"))
            try:
                localization.set_language("bg")
                dialog = self.dialog()
                self.assertEqual(dialog.windowTitle(), "История на акаунта")
                self.assertEqual(dialog._changes.horizontalHeaderItem(1).text(), "Преди")
                dialog._events.selectRow(1)
                localization.set_language("en")
                self.app.processEvents()
                self.assertEqual(dialog.windowTitle(), "Account history")
                self.assertEqual(dialog._events.currentRow(), 1)
                self.assertEqual(dialog._events.item(0, 1).text(), "Alice Admin (1)")
                self.assertIn("never stored", dialog._password_notice.text())
            finally:
                self.app.removeTranslator(localization._current_translator)
