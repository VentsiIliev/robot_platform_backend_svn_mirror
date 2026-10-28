"""Presentation-only account form; commands and authorization stay in the service."""
from PyQt6.QtCore import QCoreApplication, QEvent, Qt, QTimer
from PyQt6.QtWidgets import (
    QComboBox, QDialog, QFormLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QScrollArea, QVBoxLayout, QWidget,
)

from pl_gui.settings.settings_view.styles import ACTION_BTN_STYLE, GHOST_BTN_STYLE
from src.applications.base.widgets.custom_virtual_keyboard import KeyboardLineEdit


class AccountFormDialog(QDialog):
    def __init__(self, title, fields, values=None, choices=None, parent=None):
        super().__init__(parent)
        self._title, self._fields = title, fields
        self._choices = choices or {}
        self._labels, self._widgets = {}, {}
        self._virtual_keyboard_dock_window = parent.window() if parent is not None else None
        self.setMinimumWidth(460)
        root = QVBoxLayout(self)
        host = QWidget()
        form = QFormLayout(host)
        for key, label, secret in fields:
            widget = QComboBox() if key in (choices or {}) else KeyboardLineEdit()
            if isinstance(widget, QComboBox):
                for option in choices[key]:
                    widget.addItem(option, option)
                widget.setCurrentText((values or {}).get(key, widget.currentText()))
            else:
                widget.setText((values or {}).get(key, ""))
                if secret:
                    widget.setEchoMode(QLineEdit.EchoMode.Password)
            self._widgets[key] = widget
            self._labels[key] = QLabel()
            form.addRow(self._labels[key], widget)
        self._keyboard_spacer = QWidget()
        self._keyboard_spacer.setFixedHeight(0)
        form.addRow("", self._keyboard_spacer)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.Shape.NoFrame)
        scroll.setWidget(host)
        self._scroll = scroll
        root.addWidget(scroll)
        buttons = QHBoxLayout()
        self._save, self._cancel = QPushButton(), QPushButton()
        self._save.setStyleSheet(ACTION_BTN_STYLE)
        self._cancel.setStyleSheet(GHOST_BTN_STYLE)
        for button in (self._save, self._cancel):
            button.setCursor(Qt.CursorShape.PointingHandCursor)
            buttons.addWidget(button)
        self._save.clicked.connect(self.accept)
        self._cancel.clicked.connect(self.reject)
        root.addLayout(buttons)
        self.resize(500, min(650, 160 + 68 * len(fields)))
        self.retranslateUi()

    def values(self):
        return {key: widget.currentData() if isinstance(widget, QComboBox) else widget.text()
                for key, widget in self._widgets.items()}

    def clear(self):
        for widget in self._widgets.values():
            if isinstance(widget, QLineEdit):
                widget.clear()

    def _on_virtual_keyboard_shown(self, rect):
        viewport = self._scroll.viewport()
        overlap = viewport.mapToGlobal(viewport.rect().bottomLeft()).y() - rect.top() + 24
        self._keyboard_spacer.setFixedHeight(max(0, overlap))
        QTimer.singleShot(0, self._ensure_focused_visible)

    def _ensure_focused_visible(self):
        focused = self.focusWidget()
        if focused is not None:
            self._scroll.ensureWidgetVisible(focused, 12, 12)

    def _on_virtual_keyboard_hidden(self):
        self._keyboard_spacer.setFixedHeight(0)

    def retranslateUi(self):
        self.setWindowTitle(self._t(self._title))
        for key, label, _secret in self._fields:
            self._labels[key].setText(self._t(label))
        for key, choices in self._choices.items():
            for index, source in enumerate(choices):
                self._widgets[key].setItemText(index, self._t(source))
        self._save.setText(self._t("Save"))
        self._cancel.setText(self._t("Cancel"))

    @staticmethod
    def _t(text):
        return QCoreApplication.translate("UserManagement", text) or text

    def changeEvent(self, event):
        if event.type() == QEvent.Type.LanguageChange:
            self.retranslateUi()
        super().changeEvent(event)
