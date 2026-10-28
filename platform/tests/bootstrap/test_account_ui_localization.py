import json
from pathlib import Path
import tempfile
import unittest

from PyQt6.QtWidgets import QApplication

from src.applications.base.widgets.private_text_dialog import PrivateTextDialog
from src.applications.login.view.admin_recovery_dialog import AdminRecoveryDialog
from src.applications.user_management.view.account_form_dialog import AccountFormDialog
from src.engine.localization.localization_service import LocalizationService


class AccountDialogLocalizationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(__file__).resolve().parents[2] / "src" / "applications"
        self.localization = LocalizationService(
            [str(self.root / "localization"), str(self.root / "login/localization"),
             str(self.root / "user_management/localization")],
            state_file=str(Path(temporary.name) / "language.json"))
        self.addCleanup(self.localization._remove_installed_translator, self.app)
        self.localization.set_language("bg")

    def dialogs(self):
        form = AccountFormDialog("Add User", (("id", "ID", False), ("role", "Role", False)),
                                 choices={"role": ("Admin", "Operator", "Manufacturer")})
        recovery = AdminRecoveryDialog()
        private = PrivateTextDialog("Save recovery codes", "Keep this password private.", "private-test-value")
        for dialog in (form, recovery, private):
            self.addCleanup(dialog.deleteLater)
            dialog.show()
        self.app.processEvents()
        return form, recovery, private

    def test_initial_bulgarian_and_runtime_english_preserve_role_ids_and_secrets(self):
        form, recovery, private = self.dialogs()
        bg = json.loads((self.root / "user_management/localization/bg.json").read_text())["UserManagement"]
        self.assertEqual(form._save.text(), bg["Save"])
        self.assertEqual(form._widgets["role"].itemText(0), bg["Admin"])
        self.assertEqual(form.values()["role"], "Admin")
        self.assertNotEqual(recovery._submit.text(), "Set new password")
        self.assertEqual(private._text.toPlainText(), "private-test-value")
        self.localization.set_language("en")
        self.app.processEvents()
        self.assertEqual(form._save.text(), "Save")
        self.assertEqual(recovery._submit.text(), "Set new password")
        self.assertEqual(private._close.text(), "Close")
        self.assertEqual(form.values()["role"], "Admin")
        self.assertEqual(private._text.toPlainText(), "private-test-value")

    def test_recovery_validation_retranslates_and_closing_erases_secret_fields(self):
        _form, recovery, private = self.dialogs()
        recovery._on_submit()
        self.assertTrue(recovery._error.text())
        self.localization.set_language("en")
        self.app.processEvents()
        self.assertEqual(recovery._error.text(), "Complete all fields and enter matching passwords.")
        for _label, field in recovery._fields.values():
            field.setText("sensitive-test-value")
        recovery.reject()
        self.assertTrue(all(not field.text() for _label, field in recovery._fields.values()))
        private.reject()
        self.assertEqual(private._text.toPlainText(), "")
