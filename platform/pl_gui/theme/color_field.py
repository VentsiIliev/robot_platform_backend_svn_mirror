"""Reusable color picker with editable hex input and a literal preview swatch."""

import re

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import QColorDialog, QHBoxLayout, QPushButton, QWidget

from pl_gui.settings.settings_view.styles import GHOST_BTN_STYLE


class ColorField(QWidget):
    color_previewed = pyqtSignal(str)

    def __init__(self, line_edit, parent=None):
        super().__init__(parent)
        self._input = line_edit
        self._last_valid_color = "#FFFFFF"
        self._button = QPushButton()
        self._button.setProperty("themeLiteralColors", True)
        self._button.setFixedSize(64, 44)
        self._button.setCursor(Qt.CursorShape.PointingHandCursor)
        self._button.clicked.connect(self._choose)
        self._input.setMaximumWidth(180)
        self._input.setMinimumHeight(44)
        self._input.textChanged.connect(self._update_preview)
        self._input.textEdited.connect(self._on_text_edited)
        row = QHBoxLayout(self)
        row.setContentsMargins(0, 0, 0, 0)
        row.addWidget(self._input)
        row.addWidget(self._button)
        row.addStretch()

    def set_color(self, color: str):
        """Update the field without emitting a user preview request."""
        self._input.setText(color)
        if re.fullmatch(r"#[0-9a-fA-F]{6}", color):
            self._last_valid_color = color.upper()

    def color(self) -> str:
        return self._input.text().strip()

    def set_label(self, label: str):
        self._input.setAccessibleName(label)
        self._button.setAccessibleName(label)
        self._button.setToolTip(label)

    def _update_preview(self):
        color = QColor(self.color())
        self._button.setStyleSheet(
            f"background-color: {color.name()}; border: 1px solid palette(mid); border-radius: 8px;"
            if color.isValid() else GHOST_BTN_STYLE
        )

    def _choose(self):
        original_text = self.color()
        original_color = self._last_valid_color
        dialog = QColorDialog(QColor(original_color), self)
        dialog.setWindowTitle(self._button.accessibleName())
        dialog.setOption(QColorDialog.ColorDialogOption.DontUseNativeDialog)
        dialog.currentColorChanged.connect(self._on_picker_color_changed)
        try:
            if dialog.exec() == QColorDialog.DialogCode.Accepted:
                self._on_picker_color_changed(dialog.selectedColor())
            else:
                self.set_color(original_text)
                self._last_valid_color = original_color
                self.color_previewed.emit(original_color)
        finally:
            dialog.deleteLater()

    def _on_text_edited(self, text: str):
        if re.fullmatch(r"#[0-9a-fA-F]{6}", text.strip()):
            self._last_valid_color = text.strip().upper()
            self.color_previewed.emit(self._last_valid_color)

    def _on_picker_color_changed(self, color: QColor):
        if color.isValid():
            self.set_color(color.name().upper())
            self.color_previewed.emit(self._last_valid_color)
