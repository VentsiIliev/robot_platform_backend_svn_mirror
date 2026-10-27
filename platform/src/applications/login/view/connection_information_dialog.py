"""Readable connection details opened after platform-password authorization."""

from PyQt6.QtCore import QCoreApplication, QEvent, Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QDialog, QFormLayout, QHBoxLayout, QLabel, QPushButton,
    QVBoxLayout,
)

from pl_gui.settings.settings_view.styles import (
    ACTION_BTN_STYLE, APP_PAGE_TITLE_STYLE, BG_COLOR, BORDER, GHOST_BTN_STYLE,
    LABEL_STYLE, TEXT_COLOR,
)


class ConnectionInformationDialog(QDialog):
    refresh_requested = pyqtSignal()

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setMinimumWidth(460)
        self.resize(560, 420)
        font = self.font()
        font.setPointSize(11)
        self.setFont(font)
        self.setStyleSheet(f"background-color: {BG_COLOR}; color: {TEXT_COLOR};")
        self._information = {}
        self._busy = False
        self._failed = False

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)
        self._title = QLabel()
        self._title.setStyleSheet(APP_PAGE_TITLE_STYLE)
        layout.addWidget(self._title)

        form = QFormLayout()
        form.setSpacing(12)
        self._hostname_label = QLabel()
        self._username_label = QLabel()
        self._addresses_label = QLabel()
        self._rustdesk_label = QLabel()
        for label in (self._hostname_label, self._username_label, self._addresses_label, self._rustdesk_label):
            label.setStyleSheet(LABEL_STYLE)
        self._hostname = QLabel()
        self._username = QLabel()
        self._rustdesk = QLabel()
        self._addresses = QLabel()
        for value in (self._hostname, self._username, self._rustdesk, self._addresses):
            value.setTextFormat(Qt.TextFormat.PlainText)
            value.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
            value.setWordWrap(True)
        value_font = self._addresses.font()
        value_font.setPointSize(16)
        value_font.setBold(True)
        self._addresses.setFont(value_font)
        self._addresses.setStyleSheet(
            f"background-color: {BG_COLOR}; color: {TEXT_COLOR};"
            f"border: 1px solid {BORDER}; border-radius: 8px; padding: 8px;"
        )
        form.addRow(self._hostname_label, self._hostname)
        form.addRow(self._username_label, self._username)
        form.addRow(self._addresses_label, self._addresses)
        form.addRow(self._rustdesk_label, self._rustdesk)
        layout.addLayout(form, 1)

        self._status = QLabel()
        self._status.setWordWrap(True)
        layout.addWidget(self._status)
        buttons = QHBoxLayout()
        self._refresh = QPushButton()
        self._refresh.setStyleSheet(GHOST_BTN_STYLE)
        self._refresh.clicked.connect(self._on_refresh_clicked)
        self._close = QPushButton()
        self._close.setStyleSheet(ACTION_BTN_STYLE)
        self._close.clicked.connect(self.reject)
        for button in (self._refresh, self._close):
            button.setCursor(Qt.CursorShape.PointingHandCursor)
            button.setAutoDefault(False)
        buttons.addWidget(self._refresh)
        buttons.addStretch(1)
        buttons.addWidget(self._close)
        layout.addLayout(buttons)
        self.retranslateUi()

    def set_busy(self, busy: bool) -> None:
        """Show progress and prevent overlapping refresh requests."""
        self._busy = busy
        self._refresh.setEnabled(not busy)
        self._render_information()

    def set_information(self, information: dict) -> None:
        """Display raw identifiers; translate only labels and missing values."""
        self._information = information
        self._failed = False
        self._render_information()

    def show_error(self) -> None:
        """Clear stale details after a failed refresh."""
        self._information = {}
        self._failed = True
        self._render_information()

    def _on_refresh_clicked(self) -> None:
        self.refresh_requested.emit()

    @staticmethod
    def _t(source: str) -> str:
        return QCoreApplication.translate("Login", source) or source

    def retranslateUi(self, *_) -> None:
        self.setWindowTitle(self._t("Connection information"))
        self._title.setText(self._t("Connection information"))
        self._hostname_label.setText(self._t("PC name:"))
        self._username_label.setText(self._t("PC user:"))
        self._addresses_label.setText(self._t("IP addresses:"))
        self._rustdesk_label.setText(self._t("RustDesk ID:"))
        self._refresh.setText(self._t("Refresh"))
        self._close.setText(self._t("Close"))
        self._render_information()

    def _render_information(self) -> None:
        unavailable = self._t("Unavailable")
        self._hostname.setText(self._information.get("hostname") or unavailable)
        self._username.setText(self._information.get("username") or unavailable)
        self._rustdesk.setText(self._information.get("rustdesk_id") or unavailable)
        addresses = self._information.get("addresses")
        if addresses is None:
            text = unavailable
        elif not addresses:
            text = self._t("No IP addresses assigned.")
        else:
            text = "\n".join(dict.fromkeys(item['address'] for item in addresses))
        self._addresses.setText(text)
        self._status.setText(
            self._t("Loading connection information…") if self._busy else
            self._t("Could not refresh connection information. Please try again.") if self._failed else ""
        )

    def changeEvent(self, event) -> None:
        if event.type() == QEvent.Type.LanguageChange:
            self.retranslateUi()
        super().changeEvent(event)
