from PyQt6.QtCore import QCoreApplication, QEvent, Qt, pyqtSignal
from PyQt6.QtWidgets import QDialog, QFormLayout, QLabel, QLineEdit, QPushButton, QVBoxLayout, QScrollArea, QWidget

from pl_gui.settings.settings_view.styles import ACTION_BTN_STYLE
from src.applications.base.widgets.custom_virtual_keyboard import KeyboardLineEdit


class AdminRecoveryDialog(QDialog):
    submitted = pyqtSignal(str, str, str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._busy = False
        self._validation_error = False
        self.setMinimumWidth(460)
        layout = QVBoxLayout(self)
        self._notice = QLabel()
        self._notice.setWordWrap(True)
        layout.addWidget(self._notice)
        host = QWidget()
        form = QFormLayout(host)
        self._fields = {}
        for name in ("User ID:", "Recovery code:", "New password:", "Confirm password:"):
            label, field = QLabel(), KeyboardLineEdit()
            if "password" in name:
                field.setEchoMode(QLineEdit.EchoMode.Password)
            self._fields[name] = (label, field)
            form.addRow(label, field)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(host)
        self._keyboard_scroll_area = scroll
        layout.addWidget(scroll)
        self._error = QLabel()
        self._error.setWordWrap(True)
        layout.addWidget(self._error)
        self._submit = QPushButton()
        self._submit.setStyleSheet(ACTION_BTN_STYLE)
        self._submit.setCursor(Qt.CursorShape.PointingHandCursor)
        self._submit.clicked.connect(self._on_submit)
        layout.addWidget(self._submit)
        self.retranslateUi()

    def _on_submit(self):
        if self._busy:
            return
        user_id, code, password, confirmation = [field.text() for _, field in self._fields.values()]
        if not user_id.strip() or not code.strip() or not password or password != confirmation:
            self.set_error(self._t("Complete all fields and enter matching passwords."))
            self._validation_error = True
            return
        self.submitted.emit(user_id.strip(), code.strip(), password)

    def set_busy(self, busy):
        self._busy = busy
        self._submit.setEnabled(not busy)
        for _, field in self._fields.values():
            field.setEnabled(not busy)

    def set_error(self, message):
        self._validation_error = False
        self._error.setText(message)

    def retranslateUi(self):
        self.setWindowTitle(self._t("Recover Admin account"))
        self._notice.setText(self._t("Use a saved personal recovery code. Operators must contact an Admin."))
        for source, (label, _) in self._fields.items():
            label.setText(self._t(source))
        self._submit.setText(self._t("Set new password"))
        if self._validation_error:
            self._error.setText(self._t("Complete all fields and enter matching passwords."))

    @staticmethod
    def _t(text):
        return QCoreApplication.translate("Login", text) or text

    def changeEvent(self, event):
        if event.type() == QEvent.Type.LanguageChange:
            self.retranslateUi()
        super().changeEvent(event)

    def reject(self):
        if not self._busy:
            super().reject()

    def done(self, result):
        for _, field in self._fields.values():
            field.clear()
        super().done(result)
