from contour_editor.persistence.providers.widget_provider import IWidgetFactory
from src.applications.base.widgets.custom_virtual_keyboard import (
    KeyboardDoubleSpinBox,
    KeyboardLineEdit,
    KeyboardSpinBox,
)


class VirtualKeyboardWidgetFactory(IWidgetFactory):
    """Reusable widget factory with optional virtual keyboard support."""

    def create_double_spinbox(self, parent=None):
        return KeyboardDoubleSpinBox(parent)

    def create_spinbox(self, parent=None):
        return KeyboardSpinBox(parent)

    def create_lineedit(self, parent=None):
        return KeyboardLineEdit(parent)
