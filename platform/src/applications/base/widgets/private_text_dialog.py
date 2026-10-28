"""Reusable private, one-time display; no disk, logging, or automatic clipboard export."""
from PyQt6.QtCore import QCoreApplication, QEvent, Qt
from PyQt6.QtWidgets import QDialog, QLabel, QPlainTextEdit, QPushButton, QVBoxLayout

from pl_gui.settings.settings_view.styles import ACTION_BTN_STYLE


class PrivateTextDialog(QDialog):
    def __init__(self, title: str, notice: str, text: str, parent=None, *, context="UserManagement"):
        super().__init__(parent)
        self._title_source, self._notice_source, self._context = title, notice, context
        self.resize(600, 420)
        layout = QVBoxLayout(self)
        self._notice = QLabel()
        self._notice.setWordWrap(True)
        layout.addWidget(self._notice)
        self._text = QPlainTextEdit()
        self._text.setReadOnly(True)
        self._text.setPlainText(text)
        layout.addWidget(self._text)
        self._close = QPushButton()
        self._close.setStyleSheet(ACTION_BTN_STYLE)
        self._close.setCursor(Qt.CursorShape.PointingHandCursor)
        self._close.clicked.connect(self.accept)
        layout.addWidget(self._close)
        self.retranslateUi()

    def retranslateUi(self):
        self.setWindowTitle(self._t(self._title_source))
        self._notice.setText(self._t(self._notice_source))
        self._close.setText(self._t("Close"))

    def _t(self, text):
        return QCoreApplication.translate(self._context, text) or text

    def changeEvent(self, event):
        if event.type() == QEvent.Type.LanguageChange:
            self.retranslateUi()
        super().changeEvent(event)

    def done(self, result):
        self._text.clear()
        super().done(result)
