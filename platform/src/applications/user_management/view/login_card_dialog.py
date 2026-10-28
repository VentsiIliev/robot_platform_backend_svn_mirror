from PyQt6.QtCore import QCoreApplication, QEvent, Qt
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import QDialog, QLabel, QPushButton, QVBoxLayout

from pl_gui.settings.settings_view.styles import ACTION_BTN_STYLE


class LoginCardDialog(QDialog):
    def __init__(self, png: bytes, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        self._notice = QLabel()
        self._notice.setWordWrap(True)
        layout.addWidget(self._notice)
        self._image = QLabel()
        pixmap = QPixmap()
        pixmap.loadFromData(png, "PNG")
        self._image.setPixmap(pixmap.scaled(360, 360, Qt.AspectRatioMode.KeepAspectRatio))
        layout.addWidget(self._image)
        self._close = QPushButton()
        self._close.setStyleSheet(ACTION_BTN_STYLE)
        self._close.setCursor(Qt.CursorShape.PointingHandCursor)
        self._close.clicked.connect(self.accept)
        layout.addWidget(self._close)
        self.retranslateUi()

    def retranslateUi(self):
        self.setWindowTitle(self._t("Login card"))
        self._notice.setText(self._t("Treat this card as a password. The previous card is now invalid."))
        self._close.setText(self._t("Close"))

    @staticmethod
    def _t(text):
        return QCoreApplication.translate("UserManagement", text) or text

    def changeEvent(self, event):
        if event.type() == QEvent.Type.LanguageChange:
            self.retranslateUi()
        super().changeEvent(event)

    def done(self, result):
        self._image.clear()
        super().done(result)
