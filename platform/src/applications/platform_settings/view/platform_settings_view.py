from PyQt6.QtCore import QEvent, Qt, pyqtSignal
from PyQt6.QtWidgets import QGroupBox, QHBoxLayout, QLabel, QVBoxLayout

from pl_gui.settings.settings_view.styles import (
    APP_PAGE_TITLE_STYLE,
    BG_COLOR,
    BORDER,
    ERROR_COLOR,
    GROUP_STYLE,
    TERTIARY_TEXT,
    TEXT_COLOR,
)
from pl_gui.utils.utils_widgets.SwitchButton import QToggle
from src.applications.base.i_application_view import IApplicationView


class PlatformSettingsView(IApplicationView):
    SHOW_JOG_WIDGET = False
    virtual_keyboard_changed = pyqtSignal(bool)

    def __init__(self, parent=None) -> None:
        super().__init__("PlatformSettings", parent)

    def setup_ui(self) -> None:
        self.setStyleSheet(f"background-color: {BG_COLOR};")
        root = QVBoxLayout(self)
        root.setContentsMargins(30, 16, 30, 20)
        root.setSpacing(16)

        self._title = QLabel()
        self._title.setStyleSheet(APP_PAGE_TITLE_STYLE)
        root.addWidget(self._title)

        self._section = QLabel()
        self._section.setStyleSheet(
            f"color: {TEXT_COLOR}; font-size: 18pt; font-weight: bold;"
        )
        root.addWidget(self._section)

        card = QGroupBox()
        card.setStyleSheet(GROUP_STYLE)
        card_layout = QHBoxLayout(card)
        card_layout.setContentsMargins(24, 22, 24, 22)
        card_layout.setSpacing(20)

        labels = QVBoxLayout()
        labels.setSpacing(6)
        self._keyboard_label = QLabel()
        self._keyboard_label.setStyleSheet(
            f"color: {TEXT_COLOR}; font-size: 13pt; font-weight: bold;"
        )
        self._keyboard_description = QLabel()
        self._keyboard_description.setWordWrap(True)
        self._keyboard_description.setStyleSheet(f"color: {TERTIARY_TEXT};")
        labels.addWidget(self._keyboard_label)
        labels.addWidget(self._keyboard_description)
        card_layout.addLayout(labels, 1)

        self._keyboard_toggle = QToggle()
        self._keyboard_toggle.setFixedHeight(36)
        self._keyboard_toggle.setMinimumWidth(76)
        self._keyboard_toggle.setCursor(Qt.CursorShape.PointingHandCursor)
        self._keyboard_toggle.clicked.connect(self._on_keyboard_clicked)
        card_layout.addWidget(self._keyboard_toggle)
        root.addWidget(card)

        self._status = QLabel()
        self._status.setWordWrap(True)
        self._status.setStyleSheet(
            f"background: white; color: {TERTIARY_TEXT}; border: 1px solid {BORDER};"
            " border-radius: 12px; padding: 12px 16px;"
        )
        root.addWidget(self._status)
        root.addStretch(1)
        self.retranslateUi()

    def _on_keyboard_clicked(self, checked: bool) -> None:
        self.virtual_keyboard_changed.emit(bool(checked))

    def set_virtual_keyboard_enabled(self, enabled: bool) -> None:
        self._keyboard_toggle.sync_visual_state(enabled)

    def set_status(self, message: str) -> None:
        self._status.setStyleSheet(
            f"background: white; color: {TERTIARY_TEXT}; border: 1px solid {BORDER};"
            " border-radius: 12px; padding: 12px 16px;"
        )
        self._status.setText(message)

    def set_error(self, message: str) -> None:
        self._status.setStyleSheet(
            f"background: white; color: {ERROR_COLOR}; border: 1px solid {BORDER};"
            " border-radius: 12px; padding: 12px 16px;"
        )
        self._status.setText(message)

    def retranslateUi(self) -> None:
        self._title.setText(self.tr("Platform Settings"))
        self._section.setText(self.tr("Appearance"))
        self._keyboard_label.setText(self.tr("Virtual keyboard"))
        self._keyboard_description.setText(
            self.tr("Show the on-screen keyboard when editing text or numbers.")
        )
        if not self._status.text():
            self._status.setText(self.tr("Changes to the virtual keyboard apply immediately."))

    def changeEvent(self, event) -> None:
        if event.type() == QEvent.Type.LanguageChange:
            self.retranslateUi()
        super().changeEvent(event)
