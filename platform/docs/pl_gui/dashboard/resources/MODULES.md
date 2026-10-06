# Module reference: `pl_gui/dashboard/resources`

[Package guide](README.md) · [Complete source index](../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [styles.py](#stylespy)

## `__init__.py`

Source: [pl_gui/dashboard/resources/__init__.py](../../../../pl_gui/dashboard/resources/__init__.py).

No top-level functions, classes or public value declarations; inspect the source for imports or entry-point statements.

## `styles.py`

Source: [pl_gui/dashboard/resources/styles.py](../../../../pl_gui/dashboard/resources/styles.py).

Central style configuration for the dashboard plugin. Provides consistent styling constants and stylesheets aligned with the application-wide design vision_service.

Module declarations (expressions are shown without evaluating them):

```python
PRIMARY = '#7A5AF8'
PRIMARY_DARK = '#6D4ED6'
BORDER = '#E4E6F0'
ICON_COLOR = '#905BA9'
BG_COLOR = '#F6F7FB'
TOPBAR_BG = '#F6F7FB'
GROUP_BG = 'rgba(122,90,248,0.05)'
STATUS_UNKNOWN = '#808080'
STATUS_INITIALIZING = '#FFA500'
STATUS_READY = '#28a745'
STATUS_LOW_WEIGHT = '#ffc107'
STATUS_EMPTY = '#dc3545'
STATUS_ERROR = '#d9534f'
STATUS_DISCONNECTED = '#6c757d'
STATUS_WARNING_BG = '#fff3cd'
METRIC_BLUE = '#1976D2'
METRIC_GREEN = '#388E3C'
TEXT_PRIMARY = '#2c3e50'
TEXT_VALUE = '#212121'
BUTTON_SIZE = 60
ICON_SIZE = 26
NORMAL_STYLE = f'\nQPushButton {{\n    background: white;\n    border: 1px solid {BORDER};\n    border-radius: 12px;\n}}\nQPushButton:hover {{\n    border: 1px solid {PRIMARY};\n    background-color: rgba(122,90,248,0.05);\n}}\nQPushButton:pressed {{\n    background-color: rgba(122,90,248,0.10);\n}}\n'
PRIMARY_STYLE = f'\nQPushButton {{\n    background-color: {PRIMARY};\n    border: none;\n    border-radius: 12px;\n}}\nQPushButton:hover {{\n    background-color: {PRIMARY_DARK};\n}}\n'
ACTIVE_STYLE = f'\nQPushButton {{\n    border: 1px solid {PRIMARY};\n    background-color: rgba(122,90,248,0.12);\n    border-radius: 12px;\n}}\n'
DIALOG_BUTTON_STYLE = f'\nQPushButton {{\n    background-color: white;\n    color: {ICON_COLOR};\n    border: 1px solid {BORDER};\n    border-radius: 8px;\n    padding: 8px 24px;\n}}\nQPushButton:hover {{\n    border: 1px solid {PRIMARY};\n    background-color: rgba(122,90,248,0.05);\n}}\nQPushButton:pressed {{\n    background-color: rgba(122,90,248,0.10);\n}}\n'
TAB_WIDGET_STYLE = f'\nQTabWidget::pane {{\n    border: 1px solid {BORDER};\n    background: white;\n    border-radius: 8px;\n    top: -1px;\n}}\nQTabBar::tab {{\n    background: white;\n    color: {ICON_COLOR};\n    padding: 12px 20px;\n    border: 1px solid {BORDER};\n    border-bottom: none;\n    border-top-left-radius: 8px;\n    border-top-right-radius: 8px;\n    margin-right: 4px;\n    font-size: 11pt;\n}}\nQTabBar::tab:selected {{\n    background: {PRIMARY};\n    color: white;\n    border-color: {PRIMARY};\n}}\nQTabBar::tab:hover:!selected {{\n    background-color: rgba(122,90,248,0.08);\n}}\nQComboBox {{\n    background-color: white;\n    color: #000000;\n    border: 1px solid {BORDER};\n    border-radius: 6px;\n    padding: 6px 10px;\n    min-height: 28px;\n}}\nQComboBox:hover {{\n    border: 1px solid {PRIMARY};\n}}\nQComboBox::drop-down {{\n    border: none;\n    padding-right: 8px;\n}}\nQComboBox QAbstractItemView {{\n    background: white;\n    color: #000000;\n    border: 1px solid {BORDER};\n    selection-background-color: rgba(122,90,248,0.15);\n    selection-color: {PRIMARY_DARK};\n}}\nQSpinBox, QDoubleSpinBox {{\n    background-color: white;\n    border: 1px solid {BORDER};\n    border-radius: 6px;\n    padding: 6px 10px;\n    min-height: 28px;\n}}\nQSpinBox:hover, QDoubleSpinBox:hover {{\n    border: 1px solid {PRIMARY};\n}}\nQSpinBox:focus, QDoubleSpinBox:focus {{\n    border: 2px solid {PRIMARY};\n}}\nQCheckBox {{\n    spacing: 8px;\n}}\nQCheckBox::indicator {{\n    width: 20px;\n    height: 20px;\n    border: 2px solid {BORDER};\n    border-radius: 4px;\n    background: white;\n}}\nQCheckBox::indicator:hover {{\n    border: 2px solid {PRIMARY};\n}}\nQCheckBox::indicator:checked {{\n    background: {PRIMARY};\n    border: 2px solid {PRIMARY};\n    image: url(none);\n}}\nQGroupBox {{\n    border: 1px solid {BORDER};\n    border-radius: 8px;\n    margin-top: 12px;\n    padding-top: 18px;\n    background: white;\n    font-weight: bold;\n    color: {PRIMARY_DARK};\n}}\nQGroupBox::title {{\n    subcontrol-origin: margin;\n    left: 12px;\n    padding: 0 8px;\n    background: white;\n}}\n'
CARD_STYLE = f'\nGlueMeterCard {{\n    background-color: white;\n    border: 1px solid {BORDER};\n    border-radius: 8px;\n}}\n'
CARD_HEADER_STYLE = f'\nQLabel {{\n    font-size: 18px;\n    font-weight: bold;\n    color: white;\n    padding: 10px;\n    background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0,\n        stop:0 {PRIMARY}, stop:1 {PRIMARY_DARK});\n    border-radius: 5px;\n}}\n'
INFO_FRAME_STYLE = f'\nQFrame {{\n    background-color: transparent;\n    border: none;\n    border-top: 1px solid {BORDER};\n    padding: 5px;\n}}\n'
METER_FRAME_STYLE = '\nbackground-color: transparent;\nborder: none;\npadding: 4px 0px;\n'
IMAGE_LABEL_STYLE = f'\nQLabel {{\n    background-color: {BG_COLOR};\n    border-radius: 6px;\n    border: 1px solid {BORDER};\n}}\n'
CONTAINER_FRAME_STYLE = f'\nQFrame {{\n    background-color: white;\n    border-radius: 8px;\n    border: 1px solid {BORDER};\n}}\n'
SLOT_PLACEHOLDER_STYLE = f'\nQFrame {{\n    background-color: {GROUP_BG};\n    border: 2px dashed {BORDER};\n    border-radius: 12px;\n}}\n'
WIZARD_IMAGE_PLACEHOLDER_STYLE = f'\nQLabel {{\n    background-color: {BG_COLOR};\n    border: 2px dashed {BORDER};\n    border-radius: 8px;\n}}\n'
WIZARD_WARNING_LABEL_STYLE = f'\nfont-size: 12px; padding: 10px; background-color: {STATUS_WARNING_BG}; border-radius: 5px;\n'
```
