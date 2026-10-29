"""A modal live message which composes the reusable alignment illustration."""

from PyQt6.QtCore import QCoreApplication, QEvent, Qt
from PyQt6.QtWidgets import QDialog, QPushButton, QVBoxLayout, QWidget

from pl_gui.settings.settings_view.styles import BG_COLOR, GHOST_BTN_STYLE
from src.robot_systems.paint.applications.dashboard.head_alignment_presentation import (
    HeadAlignmentFeedback,
)

from .head_alignment_guide import PaintHeadAlignmentGuide


class PaintHeadAlignmentPopup(QDialog):
    """Open asynchronously: modal input blocking must not block live feedback delivery."""

    def __init__(self, parent: QWidget) -> None:
        super().__init__(parent)
        self.setObjectName("paintHeadAlignmentPopup")
        self.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.FramelessWindowHint)
        self.setModal(True)
        self.setStyleSheet(f"QDialog {{ background: {BG_COLOR}; }}")
        self.setMinimumSize(380, 570)
        self.resize(420, 610)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)
        self._guide = PaintHeadAlignmentGuide(self)
        layout.addWidget(self._guide, stretch=1, alignment=Qt.AlignmentFlag.AlignHCenter)
        self._close_button = QPushButton(self)
        self._close_button.setObjectName("paintHeadAlignmentClose")
        self._close_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self._close_button.setStyleSheet(GHOST_BTN_STYLE)
        self._close_button.clicked.connect(self.reject)
        layout.addWidget(self._close_button)
        self.retranslateUi()

    def set_feedback(self, feedback: HeadAlignmentFeedback) -> None:
        self._guide.set_status(feedback.status_text, attention=feedback.attention)
        self._guide.set_notice(feedback.notice)
        self._guide.set_guide(feedback.guide)

    def retranslateUi(self) -> None:
        self.setWindowTitle(
            QCoreApplication.translate("PaintDashboard", "Paint-head alignment")
            or "Paint-head alignment"
        )
        self._close_button.setText(QCoreApplication.translate("PaintDashboard", "Close") or "Close")

    def changeEvent(self, event: QEvent | None) -> None:
        if event is not None and event.type() == QEvent.Type.LanguageChange:
            self.retranslateUi()
        super().changeEvent(event)
