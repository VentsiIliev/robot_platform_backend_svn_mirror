import unittest
from unittest.mock import patch

from PyQt6 import sip
from PyQt6.QtCore import Qt
from PyQt6.QtTest import QTest
from PyQt6.QtWidgets import QApplication, QDoubleSpinBox, QLineEdit, QScrollArea, QVBoxLayout, QWidget

from src.applications.base.widgets.custom_virtual_keyboard import KeyboardLineEdit, _PopupKeyboardDialog


class PhysicalKeyboardTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def popup(self, field):
        field.show()
        field.setFocus()
        keyboard = _PopupKeyboardDialog(field)
        keyboard.show()
        self.app.processEvents()
        self.addCleanup(sip.delete, field)
        self.addCleanup(sip.delete, keyboard)
        return keyboard

    def test_physical_typing_selection_shortcuts_and_virtual_keys_can_be_mixed(self):
        field = QLineEdit()
        field.setEchoMode(QLineEdit.EchoMode.Password)
        keyboard = self.popup(field)
        QTest.keyClicks(keyboard, "Ab12")
        QTest.keyClick(keyboard, Qt.Key.Key_Left)
        QTest.keyClick(keyboard, Qt.Key.Key_Backspace)
        self.assertEqual(field.text(), "Ab2")
        QTest.keyClick(keyboard, Qt.Key.Key_A, Qt.KeyboardModifier.ControlModifier)
        QTest.keyClicks(keyboard, "New")
        keyboard._append("7")
        QTest.keyClicks(keyboard, "8")
        self.assertEqual(field.text(), "New78")
        self.assertEqual(field.echoMode(), QLineEdit.EchoMode.Password)

    def test_spin_box_receives_physical_input_and_keeps_native_validation(self):
        field = QDoubleSpinBox()
        field.setRange(-100, 100)
        keyboard = self.popup(field)
        QTest.keyClick(keyboard, Qt.Key.Key_A, Qt.KeyboardModifier.ControlModifier)
        QTest.keyClicks(keyboard, "12.5")
        QTest.keyClick(keyboard, Qt.Key.Key_Return)
        self.assertEqual(field.value(), 12.5)
        QTest.keyClicks(keyboard, "x")
        self.assertNotIn("x", field.text())

    def test_escape_dismisses_popup_without_modifying_input(self):
        field = QLineEdit("keep")
        keyboard = self.popup(field)
        QTest.keyClick(keyboard, Qt.Key.Key_Escape)
        self.assertFalse(keyboard.isVisible())
        self.assertEqual(field.text(), "keep")

    def test_tab_and_shift_tab_follow_form_focus_order(self):
        form = QWidget()
        layout = QVBoxLayout(form)
        first, second = QLineEdit(), QLineEdit()
        layout.addWidget(first)
        layout.addStretch()
        layout.addWidget(second)
        form.resize(400, 900)
        form.show()
        form.activateWindow()
        self.addCleanup(sip.delete, form)
        first.setFocus()
        self.assertTrue(QTest.qWaitForWindowActive(form))
        keyboard = _PopupKeyboardDialog(first, parent=form)
        keyboard.show()
        self.app.processEvents()
        QTest.keyClick(keyboard, Qt.Key.Key_Tab)
        self.assertTrue(second.hasFocus())
        keyboard = _PopupKeyboardDialog(second, parent=form)
        keyboard.show()
        self.app.processEvents()
        QTest.keyClick(keyboard, Qt.Key.Key_Tab, Qt.KeyboardModifier.ShiftModifier)
        self.assertTrue(first.hasFocus())

    def test_shared_fields_at_top_and_bottom_accept_physical_keys_with_docked_popup(self):
        module = "src.applications.base.widgets.custom_virtual_keyboard"
        with patch(module + ".is_custom_virtual_keyboard_enabled", return_value=True), \
                patch(module + "._ACTIVE_KEYBOARD_OWNER", None):
            form = QWidget()
            layout = QVBoxLayout(form)
            scroll = QScrollArea()
            scroll.setWidgetResizable(True)
            layout.addWidget(scroll)
            content = QWidget()
            fields = QVBoxLayout(content)
            first, last = KeyboardLineEdit(), KeyboardLineEdit()
            fields.addWidget(first)
            fields.addSpacing(900)
            fields.addWidget(last)
            scroll.setWidget(content)
            form.resize(1000, 900)
            form.show()
            form.activateWindow()
            self.assertTrue(QTest.qWaitForWindowActive(form))
            try:
                for field, value in ((first, "Top"), (last, "Bottom")):
                    field.setFocus()
                    field._show_keyboard()
                    QTest.qWait(30)
                    keyboard = field._keyboard_dialog
                    self.assertTrue(keyboard.isVisible())
                    QTest.keyClicks(keyboard, value)
                    self.assertEqual(field.text(), value)
                    self.assertLess(field.mapToGlobal(field.rect().bottomLeft()).y(), keyboard.y())
                    QTest.keyClick(keyboard, Qt.Key.Key_Escape)
                    QTest.qWait(30)
                    self.assertFalse(keyboard.isVisible())
            finally:
                sip.delete(form)
                self.app.processEvents()
