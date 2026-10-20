"""Display backend-owned visualization state; emit intent without doing I/O."""

from PyQt6.QtCore import QEvent, QTimer, Qt, pyqtSignal
from PyQt6.QtWidgets import QGroupBox, QHBoxLayout, QLabel, QPushButton, QVBoxLayout, QWidget

from pl_gui.settings.settings_view.styles import (
    ACTION_BTN_STYLE, DISABLED_BG, DISABLED_BORDER, GHOST_BTN_STYLE, GROUP_STYLE,
)


class RobotVisualizationTab(QWidget):
    refresh_requested = pyqtSignal()
    rviz_enabled_requested = pyqtSignal(bool)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._busy = False
        self._running = None
        self._error = None
        root = QVBoxLayout(self)
        root.setContentsMargins(24, 20, 24, 20)
        self._group = QGroupBox()
        self._group.setStyleSheet(GROUP_STYLE)
        layout = QVBoxLayout(self._group)
        self._description = QLabel()
        self._description.setStyleSheet("background: transparent;")
        self._description.setWordWrap(True)
        self._status = QLabel()
        self._status.setStyleSheet("background: transparent;")
        self._status.setWordWrap(True)
        layout.addWidget(self._description)
        layout.addWidget(self._status)
        buttons = QHBoxLayout()
        self._start = QPushButton()
        self._stop = QPushButton()
        self._refresh = QPushButton()
        for button, style in ((self._start, ACTION_BTN_STYLE), (self._stop, GHOST_BTN_STYLE), (self._refresh, GHOST_BTN_STYLE)):
            button.setStyleSheet(style)
            button.setCursor(Qt.CursorShape.PointingHandCursor)
            buttons.addWidget(button)
        self._start.setStyleSheet(ACTION_BTN_STYLE + f"""
            QPushButton:disabled {{ background: {DISABLED_BG}; color: {DISABLED_BORDER}; }}
        """)
        layout.addLayout(buttons)
        root.addWidget(self._group)
        root.addStretch()
        self._start.clicked.connect(self._on_start)
        self._stop.clicked.connect(self._on_stop)
        self._refresh.clicked.connect(self._on_refresh)
        self._timer = QTimer(self)
        self._timer.setInterval(3000)
        self._timer.timeout.connect(self._on_refresh)
        self.retranslateUi()
        self._update_buttons()

    def _on_start(self):
        self.rviz_enabled_requested.emit(True)

    def _on_stop(self):
        self.rviz_enabled_requested.emit(False)

    def _on_refresh(self):
        if not self._busy:
            self.refresh_requested.emit()

    def set_busy(self, busy: bool):
        self._busy = busy
        self._update_buttons()

    def set_state(self, running: bool | None, error: str | None = None):
        self._running = running
        self._error = error
        self._busy = False
        self._update_buttons()
        self.retranslateUi()

    def _update_buttons(self):
        self._start.setEnabled(not self._busy and self._running is False)
        self._stop.setEnabled(not self._busy and self._running is True)
        self._refresh.setEnabled(not self._busy)

    def retranslateUi(self):
        self._group.setTitle(self.tr("RViz"))
        self._description.setText(self.tr("Open the robot and workcell visualization on the backend computer. Stopping RViz leaves robot control and MoveIt running."))
        self._start.setText(self.tr("Start RViz"))
        self._stop.setText(self.tr("Stop RViz"))
        self._refresh.setText(self.tr("Refresh status"))
        if self._error == "rviz_control_unsupported":
            self._status.setText(self.tr("This backend does not support RViz controls. Update the backend to enable them."))
        elif self._error:
            self._status.setText(self.tr("RViz unavailable: {message}").format(message=self._error))
        elif self._running is None:
            self._status.setText(self.tr("RViz status is unknown."))
        else:
            self._status.setText(self.tr("RViz is running.") if self._running else self.tr("RViz is stopped."))

    def showEvent(self, event):
        super().showEvent(event)
        self._on_refresh()
        self._timer.start()

    def hideEvent(self, event):
        self._timer.stop()
        super().hideEvent(event)

    def changeEvent(self, event):
        if event.type() == QEvent.Type.LanguageChange:
            self.retranslateUi()
        super().changeEvent(event)
