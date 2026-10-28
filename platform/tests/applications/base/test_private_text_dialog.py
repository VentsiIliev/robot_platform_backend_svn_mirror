import unittest
from PyQt6.QtWidgets import QApplication
from src.applications.base.widgets.private_text_dialog import PrivateTextDialog


class PrivateDisplayTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def test_rejecting_or_accepting_clears_secret_text(self):
        for accepted in (False, True):
            dialog = PrivateTextDialog("Save recovery codes", "Keep private", "one-time-secret")
            self.assertEqual(dialog._text.toPlainText(), "one-time-secret")
            self.assertTrue(dialog._text.isReadOnly())
            dialog.accept() if accepted else dialog.reject()
            self.assertEqual(dialog._text.toPlainText(), "")
            dialog.deleteLater()
