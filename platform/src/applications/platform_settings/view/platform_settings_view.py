from PyQt6.QtCore import Qt, QSignalBlocker, pyqtSignal
from PyQt6.QtWidgets import QComboBox, QFormLayout, QGroupBox, QHBoxLayout, QLabel, QPushButton, QScrollArea, QVBoxLayout, QWidget

from pl_gui.settings.settings_view.styles import (
    APP_PAGE_TITLE_STYLE,
    BG_COLOR,
    BORDER,
    ERROR_COLOR,
    GROUP_STYLE,
    TERTIARY_TEXT,
    TEXT_COLOR,
    ACTION_BTN_STYLE,
    GHOST_BTN_STYLE,
    TOUCH_SCROLL_AREA_STYLE,
    COMBO_BOX_STYLE,
)
from pl_gui.theme.color_field import ColorField
from src.applications.base.widgets.custom_virtual_keyboard import KeyboardLineEdit
from pl_gui.utils.utils_widgets.SwitchButton import QToggle
from src.applications.base.i_application_view import IApplicationView


class PlatformSettingsView(IApplicationView):
    SHOW_JOG_WIDGET = False
    virtual_keyboard_changed = pyqtSignal(bool)
    colors_changed = pyqtSignal(dict)
    color_preview_requested = pyqtSignal(str, str)
    color_preview_cancel_requested = pyqtSignal()
    default_colors_requested = pyqtSignal()
    theme_preview_requested = pyqtSignal(str)
    selected_language_changed = pyqtSignal(str)

    def __init__(self, parent=None) -> None:
        super().__init__("PlatformSettings", parent)

    def setup_ui(self) -> None:
        self.setObjectName("platformSettingsPage")
        self.setStyleSheet(f"QWidget#platformSettingsPage {{ background-color: {BG_COLOR}; }}")
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet(TOUCH_SCROLL_AREA_STYLE)
        content = QWidget()
        root = QVBoxLayout(content)
        scroll.setWidget(content)
        outer.addWidget(scroll)
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

        language_row = QHBoxLayout()
        self._language_label = QLabel()
        self._language_selector = QComboBox()
        self._language_selector.setStyleSheet(COMBO_BOX_STYLE)
        self._language_selector.setMinimumHeight(44)
        self._language_selector.setMinimumWidth(240)
        self._language_selector.setCursor(Qt.CursorShape.PointingHandCursor)
        self._language_selector.currentIndexChanged.connect(self._on_language_selected)
        language_row.addWidget(self._language_label)
        language_row.addWidget(self._language_selector)
        language_row.addStretch()
        root.addLayout(language_row)

        theme_row = QHBoxLayout()
        self._theme_label = QLabel()
        self._theme_selector = QComboBox()
        self._theme_selector.setStyleSheet(COMBO_BOX_STYLE)
        self._theme_selector.setMinimumHeight(44)
        self._theme_selector.setMinimumWidth(240)
        self._theme_selector.setCursor(Qt.CursorShape.PointingHandCursor)
        for preset in ("light", "dark", "custom"):
            self._theme_selector.addItem("", preset)
        # Custom describes manually edited colors; it is not a destructive preset.
        self._theme_selector.model().item(2).setEnabled(False)
        self._theme_selector.currentIndexChanged.connect(self._on_theme_selected)
        theme_row.addWidget(self._theme_label)
        theme_row.addWidget(self._theme_selector)
        theme_row.addStretch()
        root.addLayout(theme_row)

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

        self._color_card = QGroupBox()
        self._color_card.setStyleSheet(GROUP_STYLE)
        form = QFormLayout(self._color_card)
        form.setContentsMargins(24, 28, 24, 18)
        form.setSpacing(10)
        self._color_labels = {}
        self._color_fields = {}
        for role in ("primary", "primary_dark", "background", "surface", "text", "border"):
            label = QLabel()
            field = ColorField(KeyboardLineEdit())
            field.setProperty("colorRole", role)
            field.color_previewed.connect(self._on_color_preview)
            self._color_labels[role] = label
            self._color_fields[role] = field
            form.addRow(label, field)
        self._color_description = QLabel()
        self._color_description.setWordWrap(True)
        form.addRow(self._color_description)
        actions = QHBoxLayout()
        self._apply_colors = QPushButton()
        self._apply_colors.setStyleSheet(ACTION_BTN_STYLE)
        self._apply_colors.clicked.connect(self._on_apply_colors)
        self._reset_colors = QPushButton()
        self._reset_colors.setStyleSheet(GHOST_BTN_STYLE)
        self._reset_colors.clicked.connect(self._on_default_colors)
        for button in (self._apply_colors, self._reset_colors):
            button.setCursor(Qt.CursorShape.PointingHandCursor)
            actions.addWidget(button)
        form.addRow(actions)
        root.addWidget(self._color_card)

        self._status = QLabel()
        self._status_is_default = True
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

    def set_languages(self, languages: list[tuple[str, str]], current: str) -> None:
        with QSignalBlocker(self._language_selector):
            self._language_selector.clear()
            for code, name in languages:
                self._language_selector.addItem(name, code)
            self._language_selector.setEnabled(bool(languages))
            self.set_selected_language(current)

    def set_selected_language(self, code: str) -> None:
        with QSignalBlocker(self._language_selector):
            self._language_selector.setCurrentIndex(self._language_selector.findData(code))

    def _on_language_selected(self, index: int) -> None:
        if index >= 0:
            self.selected_language_changed.emit(self._language_selector.itemData(index))

    def set_selected_theme(self, preset: str) -> None:
        with QSignalBlocker(self._theme_selector):
            self._theme_selector.setCurrentIndex(self._theme_selector.findData(preset))

    def _on_theme_selected(self, index: int) -> None:
        if index >= 0:
            self.theme_preview_requested.emit(self._theme_selector.itemData(index))

    def _on_apply_colors(self) -> None:
        self.colors_changed.emit({role: field.color() for role, field in self._color_fields.items()})

    def _on_color_preview(self, color: str) -> None:
        self.color_preview_requested.emit(self.sender().property("colorRole"), color)

    def hideEvent(self, event) -> None:
        self.color_preview_cancel_requested.emit()
        super().hideEvent(event)

    def _on_default_colors(self) -> None:
        self.default_colors_requested.emit()

    def set_colors(self, colors: dict[str, str]) -> None:
        for role, field in self._color_fields.items():
            field.set_color(colors[role])

    def set_virtual_keyboard_enabled(self, enabled: bool) -> None:
        self._keyboard_toggle.sync_visual_state(enabled)

    def set_status(self, message: str) -> None:
        self._status_is_default = False
        self._status.setStyleSheet(
            f"background: white; color: {TERTIARY_TEXT}; border: 1px solid {BORDER};"
            " border-radius: 12px; padding: 12px 16px;"
        )
        self._status.setText(message)

    def set_error(self, message: str) -> None:
        self._status_is_default = False
        self._status.setStyleSheet(
            f"background: white; color: {ERROR_COLOR}; border: 1px solid {BORDER};"
            " border-radius: 12px; padding: 12px 16px;"
        )
        self._status.setText(message)

    def retranslateUi(self) -> None:
        self._title.setText(self.tr("Platform Settings"))
        self._section.setText(self.tr("Appearance"))
        self._language_label.setText(self.tr("Language"))
        self._theme_label.setText(self.tr("Theme"))
        self._theme_selector.setAccessibleName(self.tr("Theme"))
        with QSignalBlocker(self._theme_selector):
            for preset, label in (("light", self.tr("Light")), ("dark", self.tr("Dark")), ("custom", self.tr("Custom"))):
                self._theme_selector.setItemText(self._theme_selector.findData(preset), label)
        self._color_card.setTitle(self.tr("Colors"))
        labels = {
            "primary": self.tr("Accent"),
            "primary_dark": self.tr("Accent hover / pressed"),
            "background": self.tr("Page background"),
            "surface": self.tr("Cards and input background"),
            "text": self.tr("Text"),
            "border": self.tr("Borders"),
        }
        for role, text in labels.items():
            self._color_labels[role].setText(text)
            self._color_fields[role].set_label(text)
        self._apply_colors.setText(self.tr("Apply colors"))
        self._reset_colors.setText(self.tr("Restore defaults"))
        self._color_description.setText(self.tr("Colors preview immediately. Apply to save; leaving this page discards unsaved changes."))
        self._keyboard_label.setText(self.tr("Virtual keyboard"))
        self._keyboard_description.setText(
            self.tr("Show the on-screen keyboard when editing text or numbers.")
        )
        if self._status_is_default:
            self._status.setText(self.tr("Changes to the virtual keyboard apply immediately."))
