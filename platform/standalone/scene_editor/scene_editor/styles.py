"""Standalone platform-style presentation tokens.

Light/dark color roles and button/group dimensions match
pl_gui/theme/palette.py and pl_gui/settings/settings_view/styles.py.
They are kept local so copying this editor never requires platform imports.
"""
from pathlib import Path

from PyQt6.QtGui import QColor, QPalette

PALETTES = {
    'light': dict(primary='#905BA9', primary_dark='#5B3ED6', background='#F8F9FA',
                  surface='#FFFFFF', text='#1A1A2E', border='#E0E0E0'),
    'dark': dict(primary='#905BA9', primary_dark='#754D8C', background='#17141D',
                 surface='#211C28', text='#F2EDF5', border='#514759'),
}


def blend(first, second, fraction):
    a, b = QColor(first), QColor(second)
    return QColor(*(round(x+(y-x)*fraction) for x,y in zip(a.getRgb()[:3], b.getRgb()[:3]))).name()


def qt_palette(colors):
    palette = QPalette()
    roles = {'Window':'background', 'WindowText':'text', 'Base':'surface', 'AlternateBase':'background',
             'Text':'text', 'Button':'surface', 'ButtonText':'text', 'Highlight':'primary',
             'HighlightedText':None, 'Link':'primary', 'ToolTipBase':'surface', 'ToolTipText':'text',
             'Light':'surface', 'Mid':'border', 'Dark':'border'}
    for role, token in roles.items():
        palette.setColor(getattr(QPalette.ColorRole,role), QColor(colors[token] if token else '#FFFFFF'))
    muted = QColor(blend(colors['text'], colors['surface'], .48))
    for role in (QPalette.ColorRole.Text, QPalette.ColorRole.ButtonText, QPalette.ColorRole.WindowText):
        palette.setColor(QPalette.ColorGroup.Disabled, role, muted)
    return palette


def stylesheet(colors):
    p, hover, bg, surface, text, border = [colors[k] for k in ('primary','primary_dark','background','surface','text','border')]
    tint = blend(p,surface,.89)
    muted = blend(text,surface,.48)
    assets = Path(__file__).with_name('assets').as_posix()
    return f'''
        QMainWindow, QDialog, QWidget {{ background-color: {bg}; color: {text}; font-size: 11pt; }}
        QLabel {{ background: transparent; }}
        QLabel#pageTitle {{ color: {p}; font-size: 16pt; font-weight: bold; }}
        QLabel#sectionTitle {{ color: {p}; font-weight: bold; padding: 4px 0; }}
        QMenuBar, QMenu, QToolBar {{ background: {surface}; color: {text}; }}
        QMenuBar {{ padding: 4px; border-bottom: 1px solid {border}; }}
        QMenuBar::item {{ padding: 6px 12px; border-radius: 6px; }}
        QMenuBar::item:selected, QMenu::item:selected {{ background: {tint}; color: {text}; }}
        QMenu::item {{ padding: 9px 24px; }}
        QMenu::item:disabled {{ color: {muted}; }}
        QToolBar {{ border: none; border-bottom: 1px solid {border}; padding: 6px; spacing: 6px; }}
        QToolBar::separator {{ background: {border}; width: 1px; margin: 6px; }}
        QToolButton {{ color: {p}; background: {surface}; border: 1px solid {border};
            border-radius: 8px; min-height: 36px; padding: 3px 10px; font-weight: bold; }}
        QToolButton:hover, QToolButton:checked {{ background: {tint}; border-color: {p}; }}
        QToolButton:pressed {{ background: {p}; color: white; }}
        QToolButton:disabled {{ color: {muted}; background: {bg}; }}
        QPushButton {{ background: {p}; color: white; border: none; border-radius: 8px;
            min-height: 44px; padding: 0 16px; font-size: 11pt; font-weight: bold; }}
        QPushButton:hover, QPushButton:pressed {{ background: {hover}; }}
        QPushButton[secondary="true"] {{ background: {surface}; color: {p}; border: 2px solid {p}; }}
        QPushButton[secondary="true"]:hover {{ background: {tint}; }}
        QPushButton:disabled, QPushButton[secondary="true"]:disabled {{ background: {bg}; color: {muted}; border: 1px solid {border}; }}
        QLineEdit, QDoubleSpinBox, QSpinBox, QComboBox {{ background: {surface}; color: {text};
            border: 1px solid {border}; border-radius: 6px; padding: 6px 10px; min-height: 28px; }}
        QLineEdit:focus, QDoubleSpinBox:focus, QSpinBox:focus, QComboBox:focus {{ border-color: {p}; }}
        QLineEdit:read-only, QDoubleSpinBox:read-only {{ background: {bg}; }}
        QDoubleSpinBox, QSpinBox {{ padding-right: 28px; }}
        QDoubleSpinBox::up-button, QSpinBox::up-button {{ subcontrol-origin: border; subcontrol-position: top right;
            width: 25px; border: none; border-top-right-radius: 6px; background: {tint}; }}
        QDoubleSpinBox::down-button, QSpinBox::down-button {{ subcontrol-origin: border; subcontrol-position: bottom right;
            width: 25px; border: none; border-bottom-right-radius: 6px; background: {tint}; }}
        QDoubleSpinBox::up-arrow, QSpinBox::up-arrow {{ image: url("{assets}/chevron_up.svg"); width: 14px; height: 10px; }}
        QDoubleSpinBox::down-arrow, QSpinBox::down-arrow {{ image: url("{assets}/chevron_down.svg"); width: 14px; height: 10px; }}
        QComboBox::drop-down {{ border: none; width: 24px; }}
        QComboBox::down-arrow {{ image: url("{assets}/chevron_down.svg"); width: 14px; height: 10px; }}
        QComboBox QAbstractItemView {{ background: {surface}; color: {text}; border: 1px solid {border};
            selection-background-color: {tint}; selection-color: {text}; padding: 6px; }}
        QListWidget {{ background: {surface}; color: {text}; border: 1px solid {border}; border-radius: 8px; padding: 6px; }}
        QListWidget::item {{ padding: 8px 4px; border-radius: 5px; }}
        QListWidget::item:selected {{ background: {tint}; color: {text}; }}
        QListWidget::item:hover {{ background: {tint}; }}
        QGroupBox {{ background: {surface}; color: {text}; font-size: 12pt; font-weight: bold;
            border: 2px solid {border}; border-radius: 8px; margin-top: 14px; padding: 14px 10px 10px; }}
        QGroupBox::title {{ subcontrol-origin: margin; left: 14px; padding: 0 8px; background: {bg}; border-radius: 4px; }}
        QScrollArea {{ background: {bg}; border: none; }}
        QScrollBar:vertical {{ background: {bg}; width: 16px; margin: 0; }}
        QScrollBar::handle:vertical {{ background: {border}; min-height: 44px; border-radius: 7px; }}
        QScrollBar::handle:vertical:hover {{ background: {p}; }}
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0; }}
        QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{ background: transparent; }}
        QSplitter::handle {{ background: {border}; width: 4px; }}
        QToolTip {{ background: {surface}; color: {text}; border: 1px solid {border}; padding: 6px; }}
        QStatusBar {{ background: {surface}; color: {text}; border-top: 1px solid {border}; padding: 6px; }}
        QStatusBar::item {{ border: none; }}
        QWidget#editorWorkspace {{ font-size: 10pt; }}
        QFrame#workspaceCard, QFrame#viewportTools, QFrame#workspaceFooter {{
            background: {surface}; border: 1px solid {border}; border-radius: 8px; }}
        QFrame#viewportCard {{ border: 1px solid {border}; border-radius: 8px; }}
        QToolButton#primaryTool {{ background: {p}; color: white; border-color: {p}; }}
        QToolButton#primaryTool:hover {{ background: {hover}; }}
        QToolButton#filterChip {{ min-height: 22px; padding: 2px 6px; font-size: 9pt;
            font-weight: normal; border-radius: 5px; }}
        QFrame#viewportTools QToolButton {{ min-height: 30px; padding: 4px 7px; font-size: 9pt; }}
        QTabWidget::pane {{ background: {surface}; border: none; }}
        QTabBar::tab {{ background: {surface}; color: {muted}; padding: 8px 10px;
            border-bottom: 2px solid {border}; font-size: 10pt; }}
        QTabBar::tab:selected {{ color: {p}; border-bottom-color: {p}; background: {tint}; }}
        QFrame#workspaceCard QGroupBox {{ font-size: 10pt; border-width: 1px;
            padding: 8px 6px 6px; margin-top: 12px; }}
        QFrame#workspaceCard QGroupBox::title {{ background: {surface}; left: 8px; padding: 0 4px; }}
        QFrame#workspaceCard QDoubleSpinBox {{ font-size: 10pt; padding: 4px 23px 4px 5px;
            min-height: 24px; }}
        QFrame#workspaceCard QDoubleSpinBox::up-button,
        QFrame#workspaceCard QDoubleSpinBox::down-button {{ width: 20px; }}
        QFrame#workspaceCard QDoubleSpinBox QLineEdit {{ border: none; padding: 0;
            min-height: 0; border-radius: 0; font-size: 10pt; }}
        QFrame#workspaceCard QDoubleSpinBox#poseValue {{ padding: 4px 5px; }}
        QFrame#workspaceCard QDoubleSpinBox#poseValue::up-button,
        QFrame#workspaceCard QDoubleSpinBox#poseValue::down-button {{ width: 0; }}
        QFrame#workspaceCard QDoubleSpinBox#poseValue QLineEdit {{ font-size: 9pt; }}
        QPushButton#compactButton {{ min-height: 30px; padding: 0 8px; font-size: 10pt; border-radius: 6px; }}
        QToolButton#sectionToggle {{ background: transparent; border: none;
            padding: 4px; min-height: 25px; text-align: left; }}
        QLabel#mutedText {{ color: {muted}; font-size: 9pt; }}
        QStatusBar {{ font-size: 9pt; padding: 2px; }}
    '''


def viewport_colors(colors):
    return dict(background=colors['background'], grid=blend(colors['border'], colors['text'], .12),
                selection=colors['primary'], overlay=colors['text'])
