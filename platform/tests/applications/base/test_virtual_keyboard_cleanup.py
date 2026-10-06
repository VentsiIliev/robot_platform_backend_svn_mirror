import unittest

from PyQt6 import sip
from PyQt6.QtWidgets import QApplication, QScrollArea

from src.applications.base.widgets.custom_virtual_keyboard import KeyboardLineEdit


class VirtualKeyboardCleanupTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def test_pending_scroll_restore_survives_form_destruction(self):
        scroll = QScrollArea()
        field = KeyboardLineEdit()
        scroll.setWidget(field)
        field._keyboard_scroll_area = scroll
        field._keyboard_scroll_value = 0
        field._restore_keyboard_scroll_space()
        # The delayed restore is still queued when the shell destroys the form.
        sip.delete(scroll)
        self.app.processEvents()
