import json
from pathlib import Path
import tempfile
import unittest

from PyQt6 import sip
from PyQt6.QtWidgets import QApplication, QLineEdit, QPushButton

from src.applications.base.widgets.custom_virtual_keyboard import _PopupKeyboardDialog
from src.engine.localization.localization_service import LocalizationService


class VirtualKeyboardCapsLockTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def make_keyboard(self, *, numeric_only=False, password=False):
        field = QLineEdit()
        if password:
            field.setEchoMode(QLineEdit.EchoMode.Password)
        keyboard = _PopupKeyboardDialog(field, numeric_only=numeric_only)
        self.addCleanup(sip.delete, field)
        self.addCleanup(sip.delete, keyboard)
        return field, keyboard

    @staticmethod
    def key(keyboard, value):
        return next(button for button in keyboard.findChildren(QPushButton)
                    if button.property("keyboardValue") == value)

    def test_caps_lock_stays_on_for_multiple_letters_then_returns_to_lowercase(self):
        field, keyboard = self.make_keyboard(password=True)
        letter = self.key(keyboard, "a")
        caps = keyboard._caps_lock_button
        self.assertFalse(caps.isChecked())
        self.assertEqual("a", letter.text())
        letter.click()
        caps.click()
        self.assertTrue(caps.isChecked())
        self.assertEqual("A", letter.text())
        letter.click()
        self.key(keyboard, "b").click()
        self.assertTrue(caps.isChecked())
        self.key(keyboard, "1").click()
        self.key(keyboard, " ").click()
        caps.click()
        self.assertEqual("a", letter.text())
        self.key(keyboard, "c").click()
        self.assertEqual("aAB1 c", field.text())
        self.assertEqual(QLineEdit.EchoMode.Password, field.echoMode())

    def test_caps_lock_preserves_cursor_and_selection_when_inserting(self):
        field, keyboard = self.make_keyboard()
        field.setText("az")
        field.setSelection(0, 1)
        keyboard._caps_lock_button.click()
        self.key(keyboard, "b").click()
        self.assertEqual("Bz", field.text())
        self.assertEqual(1, field.cursorPosition())
        keyboard._caps_lock_button.click()
        self.key(keyboard, "c").click()
        self.assertEqual("Bcz", field.text())

    def test_numeric_keyboard_keeps_its_keys_without_caps_lock(self):
        field, keyboard = self.make_keyboard(numeric_only=True)
        self.assertIsNone(keyboard._caps_lock_button)
        for value in ("-", "1", ".", "2"):
            self.key(keyboard, value).click()
        self.assertEqual("-1.2", field.text())

    def test_caps_label_translates_initially_and_on_language_change(self):
        catalog = Path(__file__).resolve().parents[3] / "src/applications/localization"
        with tempfile.TemporaryDirectory() as directory:
            localization = LocalizationService(str(catalog), state_file=str(Path(directory) / "language.json"))
            try:
                localization.set_language("bg")
                _, keyboard = self.make_keyboard()
                self.assertEqual("Главни букви", keyboard._caps_lock_button.text())
                keyboard._caps_lock_button.click()
                localization.set_language("en")
                self.app.processEvents()
                self.assertEqual("Caps Lock", keyboard._caps_lock_button.text())
                self.assertTrue(keyboard._caps_lock_button.isChecked())
                self.assertEqual("A", self.key(keyboard, "a").text())
                for language in ("en", "bg"):
                    data = json.loads((catalog / (language + ".json")).read_text())
                    self.assertIn("Caps Lock", data["_PopupKeyboardDialog"])
            finally:
                self.app.removeTranslator(localization._current_translator)
