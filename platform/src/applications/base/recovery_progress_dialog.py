"""Reusable activity popup for operations completed by a background service."""
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QDialog, QLabel, QVBoxLayout

from pl_gui.settings.settings_view.styles import PRIMARY, TEXT_COLOR, TEXT_ON_PRIMARY
from src.applications.base.widgets.fluid_progress import create_fluid_progress


class RecoveryProgressDialog(QDialog):
    def __init__(self, parent, title: str, message: str):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setModal(True)
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose, True)
        self.setWindowFlag(Qt.WindowType.WindowCloseButtonHint, False)
        self.setMinimumWidth(520)
        self.setStyleSheet(f"QDialog {{ background: {TEXT_ON_PRIMARY}; color: {TEXT_COLOR}; }}")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 24, 28, 24)
        layout.setSpacing(18)
        heading = QLabel(title)
        heading.setWordWrap(True)
        heading.setStyleSheet(f"color: {PRIMARY}; font-size: 20px; font-weight: bold;")
        layout.addWidget(heading)
        self.progress = create_fluid_progress("plume", self)
        self.progress.set_waiting(True)
        self.progress.set_running(True)
        layout.addWidget(self.progress)
        body = QLabel(message)
        body.setObjectName("recoveryProgressMessage")
        body.setWordWrap(True)
        body.setTextFormat(Qt.TextFormat.PlainText)
        body.setStyleSheet(f"color: {TEXT_COLOR}; font-size: 14px;")
        layout.addWidget(body)
        self.ensurePolished()
        width = self.minimumWidth() - 56
        for label in (heading, body):
            label.setMinimumHeight(max(label.minimumSizeHint().height(), label.heightForWidth(width)))

    def closeEvent(self, event):
        self.progress.set_running(False)
        super().closeEvent(event)
