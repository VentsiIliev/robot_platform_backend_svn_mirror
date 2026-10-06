# Module reference: `pl_gui/shell/ui`

[Package guide](README.md) · [Complete source index](../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [Header.py](#headerpy)
- [LanguageSelectorWidget.py](#languageselectorwidgetpy)
- [__init__.py](#__init__py)
- [icon_loader.py](#icon_loaderpy)
- [styles.py](#stylespy)

## `Header.py`

Source: [pl_gui/shell/ui/Header.py](../../../../pl_gui/shell/ui/Header.py).

Imports (including optional/function-local imports; not a startup dependency list): `.LanguageSelectorWidget`, `PyQt6.QtCore`, `PyQt6.QtWidgets`, `os`, `pl_gui.settings.settings_view.styles`, `pl_gui.shell.ui.icon_loader`, `pl_gui.shell.ui.styles`, `sys`, `traceback`, `typing`.

Module declarations (expressions are shown without evaluating them):

```python
RESOURCE_DIR: str = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'resources')
MENU_ICON_PATH: str = os.path.join(RESOURCE_DIR, 'pl_ui_icons', 'SANDWICH_MENU.png')
LOGO_ICON_PATH: str = os.path.join(RESOURCE_DIR, 'pl_ui_icons', 'logo.ico')
DASHBOARD_BUTTON_ICON_PATH: str = os.path.join(RESOURCE_DIR, 'pl_ui_icons', 'DASHBOARD_BUTTON_SQUARE.png')
```

### `Header`

```python
class Header(QFrame):
```

Declared fields/defaults:

```python
user_account_clicked = pyqtSignal()
power_off_requested = pyqtSignal()
fps_updated = pyqtSignal(float)
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, screen_width: int, screen_height: int, toggle_menu_callback: Optional[Callable[[], None]], dashboard_button_callback: Optional[Callable[[], None]], languages: Optional[list]=None) -> None
```

```python
def handle_language_change(self, language_code: str) -> None
```

```python
def update_fps_label(self, fps: float) -> None
```

Update FPS label when new FPS value is received.

```python
def on_user_account_clicked(self)
```

```python
def retranslateUi(self) -> None
```

```python
def set_remote_support_state(self, state: str) -> None
```

Display confirmed session state supplied by the shell controller.

```python
def changeEvent(self, event: QEvent) -> None
```

```python
def resizeEvent(self, event: QEvent) -> None
```

## `LanguageSelectorWidget.py`

Source: [pl_gui/shell/ui/LanguageSelectorWidget.py](../../../../pl_gui/shell/ui/LanguageSelectorWidget.py).

Imports (including optional/function-local imports; not a startup dependency list): `PyQt6.QtCore`, `PyQt6.QtWidgets`, `pl_gui.shell.ui.styles`, `typing`.

### `LanguageSelectorWidget`

```python
class LanguageSelectorWidget(QComboBox):
```

Language selector that emits Qt LanguageChange events. When language changes: 1. Emits custom languageChanged signal (emits the language code string) 2. Posts QEvent.LanguageChange to all top-level widgets 3. Widgets handle it in changeEvent() and call retranslateUi()

Declared fields/defaults:

```python
languageChanged = pyqtSignal(str)
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, languages: Optional[List[Tuple[str, str]]]=None, parent=None)
```

```python
def updateSelectedLang(self)
```

Update the selected language in the dropdown

## `__init__.py`

Source: [pl_gui/shell/ui/__init__.py](../../../../pl_gui/shell/ui/__init__.py).

No top-level functions, classes or public value declarations; inspect the source for imports or entry-point statements.

## `icon_loader.py`

Source: [pl_gui/shell/ui/icon_loader.py](../../../../pl_gui/shell/ui/icon_loader.py).

Imports (including optional/function-local imports; not a startup dependency list): `PyQt6.QtCore`, `PyQt6.QtGui`, `os`, `qtawesome`.

### `_tint_icon`

```python
def _tint_icon(icon, color, size)
```

Tint an existing QIcon's pixmap to the given color. Args: icon: QIcon to tint color: Color string (e.g. "#FFFFFF") size: QSize for the pixmap extraction Returns: QIcon with tinted pixmap, or the original icon on failure

### `load_icon`

```python
def load_icon(source, color=None, size=None)
```

Single source of truth for icon loading. Args: source: QIcon object, file path string, or qtawesome string (e.g. "fa5s.cog") color: Optional color string for tinting (e.g. "#FFFFFF") size: Optional QSize — required when tinting a QIcon object Returns: QIcon (empty QIcon if loading fails)

## `styles.py`

Source: [pl_gui/shell/ui/styles.py](../../../../pl_gui/shell/ui/styles.py).

Central style configuration for new_widgets This module provides consistent styling constants and stylesheets for all widgets in the new_widgets directory.

Module declarations (expressions are shown without evaluating them):

```python
PRIMARY = '#905BA9'
PRIMARY_DARK = '#6D4ED6'
BORDER = '#E4E6F0'
ICON_COLOR = '#905BA9'
QTA_ICON_COLOR = '#FFFFFF'
BG_COLOR = '#F6F7FB'
TOPBAR_BG = '#F6F7FB'
GROUP_BG = 'rgba(122,90,248,0.05)'
PRIMARY_HOVER = '#8B6FF9'
SURFACE = '#FFFFFF'
TEXT_PRIMARY = '#1D1B20'
TEXT_DISABLED = '#9C9A9E'
TEXT_ON_PRIMARY = '#FFFFFF'
SECONDARY_BG = '#EDE7F6'
SECONDARY_HOVER = '#E0D6F0'
SECONDARY_PRESSED = '#D4CAE4'
TERTIARY_BG = '#F6F7FB'
TERTIARY_HOVER = '#EDEEF2'
TERTIARY_PRESSED = '#E5E6EA'
TERTIARY_TEXT = '#7D5260'
DISABLED_BG = '#EDE7F6'
DISABLED_BORDER = '#B0A7BC'
DISABLED_PREVIEW_BG = '#F3EDF7'
DISABLED_PREVIEW_BORDER = '#C4C0CA'
SCROLLBAR_BG = '#F6F7FB'
SCROLLBAR_HANDLE = '#CAC4D0'
SCROLLBAR_HANDLE_HOVER = '#79747E'
OVERLAY_BG = 'rgba(0, 0, 0, 0.5)'
OVERLAY_LIGHT = 'rgba(0, 0, 0, 0.32)'
OVERLAY_SUBTLE = 'rgba(0, 0, 0, 0.16)'
OVERLAY_FAINT = 'rgba(0, 0, 0, 0.05)'
SHADOW_LIGHT = (0, 0, 0, 20)
SHADOW_MEDIUM = (0, 0, 0, 30)
SHADOW_DARK = (0, 0, 0, 40)
SHADOW_FAB = (0, 0, 0, 60)
SHADOW_PRIMARY_LIGHT = (122, 90, 248, 30)
SHADOW_PRIMARY = (122, 90, 248, 40)
SHADOW_PRIMARY_HOVER = (122, 90, 248, 60)
BUTTON_SIZE = 60
ICON_SIZE = 26
NORMAL_STYLE = f'\nQPushButton {{\n    background: white;\n    border: 1px solid {BORDER};\n    border-radius: 12px;\n}}\nQPushButton:hover {{\n    border: 1px solid {PRIMARY};\n    background-color: rgba(122,90,248,0.05);\n}}\nQPushButton:pressed {{\n    background-color: rgba(122,90,248,0.10);\n}}\n'
PRIMARY_STYLE = f'\nQPushButton {{\n    background-color: {PRIMARY};\n    border: none;\n    border-radius: 12px;\n}}\nQPushButton:hover {{\n    background-color: {PRIMARY_DARK};\n}}\n'
ACTIVE_STYLE = f'\nQPushButton {{\n    border: 1px solid {PRIMARY};\n    background-color: rgba(122,90,248,0.12);\n    border-radius: 12px;\n}}\n'
DIALOG_BUTTON_STYLE = f'\nQPushButton {{\n    background-color: white;\n    color: {ICON_COLOR};\n    border: 1px solid {BORDER};\n    border-radius: 8px;\n    padding: 8px 24px;\n}}\nQPushButton:hover {{\n    border: 1px solid {PRIMARY};\n    background-color: rgba(122,90,248,0.05);\n}}\nQPushButton:pressed {{\n    background-color: rgba(122,90,248,0.10);\n}}\n'
TAB_WIDGET_STYLE = f'\nQTabWidget::pane {{\n    border: 1px solid {BORDER};\n    background: white;\n    border-radius: 8px;\n    top: -1px;\n}}\nQTabBar::tab {{\n    background: white;\n    color: {ICON_COLOR};\n    padding: 12px 20px;\n    border: 1px solid {BORDER};\n    border-bottom: none;\n    border-top-left-radius: 8px;\n    border-top-right-radius: 8px;\n    margin-right: 4px;\n    font-size: 11pt;\n}}\nQTabBar::tab:selected {{\n    background: {PRIMARY};\n    color: white;\n    border-color: {PRIMARY};\n}}\nQTabBar::tab:hover:!selected {{\n    background-color: rgba(122,90,248,0.08);\n}}\nQComboBox {{\n    background-color: white;\n    color: #000000;\n    border: 1px solid {BORDER};\n    border-radius: 6px;\n    padding: 6px 10px;\n    min-height: 28px;\n}}\nQComboBox:hover {{\n    border: 1px solid {PRIMARY};\n}}\nQComboBox::drop-down {{\n    border: none;\n    padding-right: 8px;\n}}\nQComboBox QAbstractItemView {{\n    background: white;\n    color: #000000;\n    border: 1px solid {BORDER};\n    selection-background-color: rgba(122,90,248,0.15);\n    selection-color: {PRIMARY_DARK};\n}}\nQSpinBox, QDoubleSpinBox {{\n    background-color: white;\n    border: 1px solid {BORDER};\n    border-radius: 6px;\n    padding: 6px 10px;\n    min-height: 28px;\n}}\nQSpinBox:hover, QDoubleSpinBox:hover {{\n    border: 1px solid {PRIMARY};\n}}\nQSpinBox:focus, QDoubleSpinBox:focus {{\n    border: 2px solid {PRIMARY};\n}}\nQCheckBox {{\n    spacing: 8px;\n}}\nQCheckBox::indicator {{\n    width: 20px;\n    height: 20px;\n    border: 2px solid {BORDER};\n    border-radius: 4px;\n    background: white;\n}}\nQCheckBox::indicator:hover {{\n    border: 2px solid {PRIMARY};\n}}\nQCheckBox::indicator:checked {{\n    background: {PRIMARY};\n    border: 2px solid {PRIMARY};\n    image: url(none);\n}}\nQGroupBox {{\n    border: 1px solid {BORDER};\n    border-radius: 8px;\n    margin-top: 12px;\n    padding-top: 18px;\n    background: white;\n    font-weight: bold;\n    color: {PRIMARY_DARK};\n}}\nQGroupBox::title {{\n    subcontrol-origin: margin;\n    left: 12px;\n    padding: 0 8px;\n    background: white;\n}}\n'
```
