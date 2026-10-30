"""Application presentation styles composed from the shared platform palette."""

from pl_gui.settings.settings_view.styles import (
    BG_COLOR,
    BORDER,
    COMBO_BOX_STYLE,
    DISABLED_BORDER,
    GHOST_BTN_STYLE,
    PRIMARY,
    SCROLLBAR_HANDLE_HOVER,
    SECONDARY_BG,
    SETTINGS_CARD_FRAME_STYLE,
    TEXT_COLOR,
    TEXT_ON_PRIMARY,
)

CARD_STYLE = SETTINGS_CARD_FRAME_STYLE
SECTION_TITLE_STYLE = (
    f"color: {TEXT_COLOR}; font-size: 12pt; font-weight: bold; background: transparent;"
)
CAPTION_STYLE = f"color: {SCROLLBAR_HANDLE_HOVER}; font-size: 9pt; background: transparent;"
SECONDARY_BUTTON_STYLE = (
    GHOST_BTN_STYLE
    + f"""
QPushButton {{ border: 1px solid {BORDER}; }}
QPushButton:hover {{ border-color: {PRIMARY}; }}
QPushButton:checked {{ background: {SECONDARY_BG}; border-color: {PRIMARY}; }}
QPushButton:disabled {{ border-color: {DISABLED_BORDER}; }}
"""
)
ICON_BUTTON_STYLE = SECONDARY_BUTTON_STYLE + "QPushButton { padding: 0; }"

PAGE_STYLE = (
    COMBO_BOX_STYLE
    + f"""
QWidget#paintHeadSetup {{ background: {BG_COLOR}; color: {TEXT_COLOR}; }}
QWidget#calibrationObjectProperties,
QScrollArea#calibrationPropertiesScroll > QWidget {{ background: {TEXT_ON_PRIMARY}; }}
QWidget#calibrationSettingsContent {{ background: {BG_COLOR}; }}
QLabel {{ background: transparent; color: {TEXT_COLOR}; }}
QLabel#calibrationRuntimeSelection {{
    background: {SECONDARY_BG}; color: {PRIMARY}; border-radius: 8px;
    padding: 10px 14px; font-size: 10pt;
}}
QLineEdit {{
    background: {TEXT_ON_PRIMARY}; color: {TEXT_COLOR};
    border: 1px solid {BORDER}; border-radius: 8px;
    min-height: 36px; padding: 0 10px;
}}
QLineEdit:focus {{ border-color: {PRIMARY}; }}
QListWidget {{
    background: {TEXT_ON_PRIMARY}; border: none; outline: 0;
    color: {TEXT_COLOR}; padding: 4px; font-size: 10pt;
}}
QListWidget::item {{ padding: 9px 10px; border-radius: 7px; }}
QListWidget::item:selected {{ background: {SECONDARY_BG}; color: {PRIMARY}; }}
QListWidget#calibrationNavigation {{
    border: 1px solid {BORDER}; border-radius: 12px; padding: 8px;
}}
QListWidget#calibrationNavigation::item {{ min-height: 30px; margin: 2px 0; }}
QListWidget#calibrationNavigation::item:selected {{ font-weight: bold; }}
QTableWidget {{
    background: {TEXT_ON_PRIMARY}; alternate-background-color: {BG_COLOR};
    border: none; color: {TEXT_COLOR}; outline: 0; font-size: 10pt;
    selection-background-color: {SECONDARY_BG}; selection-color: {TEXT_COLOR};
}}
QTableWidget::item {{ padding: 8px 10px; border-bottom: 1px solid {BG_COLOR}; }}
QTableWidget::item:selected {{ color: {TEXT_COLOR}; background: {SECONDARY_BG}; }}
QHeaderView::section {{
    background: {BG_COLOR}; color: {TEXT_COLOR}; border: none;
    border-bottom: 1px solid {BORDER}; padding: 9px 10px;
    font-size: 9pt; font-weight: bold;
}}
QSplitter::handle {{ background: transparent; width: 12px; }}
QScrollArea {{ background: transparent; border: none; }}
QToolButton#calibrationSettingsSection {{
    color: {PRIMARY}; background: transparent; border: none;
    text-align: left; padding: 8px 4px; font-size: 11pt; font-weight: bold;
}}
"""
)
