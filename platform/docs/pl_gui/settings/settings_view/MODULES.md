# Module reference: `pl_gui/settings/settings_view`

[Package guide](README.md) · [Complete source index](../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [build_showcase.py](#build_showcasepy)
- [group_widget.py](#group_widgetpy)
- [schema.py](#schemapy)
- [settings_view.py](#settings_viewpy)
- [styles.py](#stylespy)
- [widget_factory.py](#widget_factorypy)

## `__init__.py`

Source: [pl_gui/settings/settings_view/__init__.py](../../../../pl_gui/settings/settings_view/__init__.py).

Imports (including optional/function-local imports; not a startup dependency list): `pl_gui.settings.settings_view.group_widget`, `pl_gui.settings.settings_view.schema`, `pl_gui.settings.settings_view.settings_view`.

Package-level import/export surface:

```python
from pl_gui.settings.settings_view.schema import SettingField, SettingGroup
from pl_gui.settings.settings_view.group_widget import GenericSettingGroup
from pl_gui.settings.settings_view.settings_view import SettingsView
```

No top-level functions, classes or public value declarations; inspect the source for imports or entry-point statements.

## `build_showcase.py`

Source: [pl_gui/settings/settings_view/build_showcase.py](../../../../pl_gui/settings/settings_view/build_showcase.py).

Imports (including optional/function-local imports; not a startup dependency list): `pl_gui.settings.settings_view`.

Module declarations (expressions are shown without evaluating them):

```python
SPINBOX_GROUP = SettingGroup('spinbox  —  integer stepper', [SettingField('spin_no_pills', 'No step pills  (step_options=[1])', 'spinbox', default=42, min_val=0, max_val=100, step=1, step_options=[1]), SettingField('spin_with_pills', 'Step pills  (step_options=[1,5,10,50])', 'spinbox', default=100, min_val=0, max_val=1000, suffix=' mm/s', step=1, step_options=[1, 5, 10, 50])])
DOUBLE_SPINBOX_GROUP = SettingGroup('double_spinbox  —  float stepper', [SettingField('double_2dec', '2 decimals', 'double_spinbox', default=1.5, min_val=0.0, max_val=10.0, decimals=2, step=0.1, step_options=[0.1, 0.5, 1.0]), SettingField('double_3dec', '3 decimals + suffix', 'double_spinbox', default=0.025, min_val=-100.0, max_val=100.0, decimals=3, suffix=' mm', step=0.001, step_options=[0.001, 0.01, 0.1, 1.0])])
TEXT_GROUP = SettingGroup('line_edit  —  free text input', [SettingField('line_ip', 'IP address', 'line_edit', default='192.168.1.100'), SettingField('line_name', 'Name', 'line_edit', default='My Robot')])
COMBO_GROUP = SettingGroup('combo  —  dropdown selector', [SettingField('combo_mode', 'Operating mode', 'combo', default='Auto', choices=['Manual', 'Auto', 'Semi-Auto']), SettingField('combo_bool', 'Boolean as combo  (True / False)', 'combo', default='True', choices=['True', 'False'])])
INT_LIST_GROUP = SettingGroup('int_list  —  add / edit / remove integer items', [SettingField('int_list_ids', 'Marker IDs  (0 – 255)', 'int_list', default='0,1,2,3,4,5,6,8', min_val=0, max_val=255)])
MIXED_GROUP = SettingGroup('Mixed  —  int_list spans full width; other fields stay 2-column', [SettingField('mixed_spin', 'Spinbox left', 'spinbox', default=10, min_val=0, max_val=100, step=1, step_options=[1]), SettingField('mixed_combo', 'Combo right', 'combo', default='B', choices=['A', 'B', 'C']), SettingField('mixed_list', 'Int list  (full row)', 'int_list', default='10,20,30', min_val=0, max_val=999), SettingField('mixed_text', 'Line edit below', 'line_edit', default='back to normal')])
```

### `build_showcase`

```python
def build_showcase() -> SettingsView
```

## `group_widget.py`

Source: [pl_gui/settings/settings_view/group_widget.py](../../../../pl_gui/settings/settings_view/group_widget.py).

Imports (including optional/function-local imports; not a startup dependency list): `PyQt6.QtCore`, `PyQt6.QtWidgets`, `pl_gui.settings.settings_view.schema`, `pl_gui.settings.settings_view.styles`, `pl_gui.settings.settings_view.widget_factory`.

### `GenericSettingGroup`

```python
class GenericSettingGroup(QGroupBox):
```

Schema-driven QGroupBox — touch-friendly, 2-column grid. Layout per field: ┌─────────────┐ ┌─────────────┐ │ Label │ │ Label │ │ [ widget ] │ │ [ widget ] │ └─────────────┘ └─────────────┘ Fields whose handler has full_width=True always span both columns. Signals: value_changed(key: str, value: object)

Declared fields/defaults:

```python
value_changed = pyqtSignal(str, object)
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, group: SettingGroup, parent=None, *, compact: bool=False)
```

```python
def changeEvent(self, event) -> None
```

```python
def set_values(self, values: dict) -> None
```

```python
def get_values(self) -> dict
```

```python
def set_step(self, step: float) -> None
```

## `schema.py`

Source: [pl_gui/settings/settings_view/schema.py](../../../../pl_gui/settings/settings_view/schema.py).

Imports (including optional/function-local imports; not a startup dependency list): `dataclasses`, `typing`.

### `SettingField`

```python
@dataclass
class SettingField:
```

Declared fields/defaults:

```python
key: str
label: str
widget_type: str
default: Any = None
min_val: float = 0
max_val: float = 100
step: float = 1.0
decimals: int = 2
suffix: str = ''
choices: Optional[List[str]] = None
step_options: Optional[List[float]] = None
```

### `SettingGroup`

```python
@dataclass
class SettingGroup:
```

Declared fields/defaults:

```python
title: str
fields: List[SettingField] = field(default_factory=list)
columns: int = 2
axis_pairs: bool = False
```

## `settings_view.py`

Source: [pl_gui/settings/settings_view/settings_view.py](../../../../pl_gui/settings/settings_view/settings_view.py).

Imports (including optional/function-local imports; not a startup dependency list): `PyQt6.QtCore`, `PyQt6.QtGui`, `PyQt6.QtWidgets`, `pl_gui.settings.settings_view.group_widget`, `pl_gui.settings.settings_view.schema`, `pl_gui.settings.settings_view.styles`, `typing`.

### `_SettingsTabBar`

```python
class _SettingsTabBar(QTabBar):
```

Paint one segmented tab control without native tab overlap.

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, parent=None)
```

```python
def tabSizeHint(self, index: int) -> QSize
```

```python
def paintEvent(self, event) -> None
```

```python
def mouseMoveEvent(self, event) -> None
```

```python
def leaveEvent(self, event) -> None
```

### `SettingsView`

```python
class SettingsView(QWidget):
```

Schema-driven settings UI — touch-friendly. Usage: view = SettingsView("RobotSettings") view.add_tab("General", [ROBOT_INFO_GROUP, GLOBAL_MOTION_GROUP]) view.add_tab("Safety", [SAFETY_LIMITS_GROUP]) view.set_values(flat_dict) view.value_changed_signal.connect(handler) view.save_requested.connect(on_save)

Declared fields/defaults:

```python
value_changed_signal = pyqtSignal(str, object, str)
save_requested = pyqtSignal(dict)
discard_requested = pyqtSignal()
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, component_name: str='SettingsView', mapper=None, parent: QWidget=None)
```

```python
def enable_change_controls(self) -> None
```

```python
def set_dirty(self, dirty: bool) -> None
```

```python
def retranslateUi(self) -> None
```

```python
def changeEvent(self, event) -> None
```

```python
def add_tab(self, title: str, groups: List[SettingGroup]) -> None
```

Build a tab from a list of SettingGroup schemas and add it.

```python
def add_raw_tab(self, title: str, widget: QWidget) -> None
```

Add a tab containing an arbitrary widget (not schema-driven).

```python
def load(self, model) -> None
```

Convert model → flat dict via mapper, then push into widgets.

```python
def set_values(self, flat: dict) -> None
```

```python
def get_values(self) -> dict
```

## `styles.py`

Source: [pl_gui/settings/settings_view/styles.py](../../../../pl_gui/settings/settings_view/styles.py).

Module declarations (expressions are shown without evaluating them):

```python
PRIMARY = '#905BA9'
PRIMARY_DARK = '#5B3ED6'
PRIMARY_LIGHT = 'rgba(122, 90, 248, 0.10)'
BG_COLOR = '#F8F9FA'
BORDER = '#E0E0E0'
TEXT_COLOR = '#1A1A2E'
ERROR_COLOR = '#C62828'
STATUS_OK = '#2E7D32'
PRIMARY_HOVER = '#8B6FF9'
TEXT_PRIMARY = '#1D1B20'
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
TOUCH_SCROLL_AREA_STYLE = f'\nQScrollArea {{\n    border: none;\n    background: transparent;\n}}\nQScrollBar:vertical {{\n    background: {SCROLLBAR_BG};\n    width: 24px;\n    margin: 0;\n    border-radius: 8px;\n}}\nQScrollBar::handle:vertical {{\n    background: {SCROLLBAR_HANDLE};\n    min-height: 48px;\n    border-radius: 8px;\n}}\nQScrollBar::handle:vertical:hover {{\n    background: {SCROLLBAR_HANDLE_HOVER};\n}}\nQScrollBar::add-line:vertical,\nQScrollBar::sub-line:vertical {{\n    height: 0;\n}}\nQScrollBar::add-page:vertical,\nQScrollBar::sub-page:vertical {{\n    background: transparent;\n}}\n'
TOUCH_COMBO_STYLE = f'\nQFrame#touchCombo {{\n    background: white;\n    border: 2px solid {BORDER};\n    border-radius: 10px;\n}}\nQFrame#touchCombo:hover {{ border-color: {PRIMARY}; }}\nQFrame#touchCombo QComboBox {{\n    background: transparent;\n    color: {TEXT_COLOR};\n    border: none;\n    padding: 0 12px;\n    font-size: 12pt;\n    min-height: 48px;\n}}\nQFrame#touchCombo QComboBox::drop-down {{ width: 0; border: none; }}\nQFrame#touchCombo QComboBox::down-arrow {{ image: none; }}\nQFrame#touchCombo QPushButton#comboDrop {{\n    background: transparent;\n    color: {PRIMARY};\n    border: none;\n    font-size: 17pt;\n    font-weight: bold;\n}}\nQFrame#touchCombo QComboBox QAbstractItemView {{\n    background: white;\n    color: {TEXT_COLOR};\n    selection-background-color: {PRIMARY_LIGHT};\n    selection-color: {PRIMARY_DARK};\n    font-size: 11pt;\n    padding: 8px;\n}}\n'
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
TAB_WIDGET_STYLE = f'\nQTabWidget::pane {{\n    border: 1px solid {BORDER};\n    border-radius: 0 8px 8px 8px;\n    background: {BG_COLOR};\n}}\nQTabBar::tab {{\n    background: white;\n    color: #333333;\n    border: 2px solid {BORDER};\n    border-bottom: none;\n    border-radius: 8px 8px 0 0;\n    padding: 10px 28px;\n    font-size: 11pt;\n    font-weight: bold;\n    min-width: 100px;\n    min-height: 40px;\n}}\nQTabBar::tab:selected {{\n    background: white;\n    color: {PRIMARY};\n    border-color: {PRIMARY};\n    border-bottom: 2px solid white;\n}}\nQTabBar::tab:hover:!selected {{\n    background: {PRIMARY_LIGHT};\n}}\n'
SETTINGS_FOOTER_STYLE = f'\nQWidget#settingsFooter {{\n    background: white;\n    border-top: 1px solid {BORDER};\n    border-radius: 12px 12px 0 0;\n}}\n'
APP_PAGE_TITLE_STYLE = f'color: {PRIMARY}; font-size: 16pt; font-weight: bold; background: transparent;'
SETTINGS_HEADER_STYLE = APP_PAGE_TITLE_STYLE
APP_PHASE_TAB_STYLE = f'\nQTabBar {{ background: white; border: 1px solid {BORDER}; border-radius: 14px; }}\nQTabBar::tab {{ color: {TEXT_COLOR}; background: transparent; border: none;\n    padding: 10px 18px; min-height: 28px; font-size: 11pt; font-weight: bold; }}\nQTabBar::tab:selected {{ color: white; background: {PRIMARY}; border-radius: 10px; }}\n'
SETTINGS_CARD_FRAME_STYLE = f'\nQFrame#settingsCard {{\n    background: white;\n    border: 1px solid {BORDER};\n    border-radius: 14px;\n}}\nQWidget#settingsCardHeader {{\n    background: {SECONDARY_BG};\n    border-bottom: 1px solid {BORDER};\n    border-top-left-radius: 14px;\n    border-top-right-radius: 14px;\n}}\nQWidget#settingsCardContent {{\n    background: white;\n    border-bottom-left-radius: 14px;\n    border-bottom-right-radius: 14px;\n}}\nQLabel#settingsCardTitle {{\n    color: {PRIMARY};\n    background: transparent;\n    font-size: 10pt;\n    font-weight: bold;\n}}\nQGroupBox#settingsCardBody {{\n    background: white;\n    border: none;\n    margin: 0;\n    padding: 0;\n}}\n'
SETTINGS_STEP_STYLE = f'\nQPushButton {{\n    background: white;\n    color: {PRIMARY};\n    border: 1px solid {BORDER};\n    padding: 4px 10px;\n    min-height: 30px;\n    min-width: 36px;\n}}\nQPushButton:checked {{\n    background: {PRIMARY};\n    color: white;\n    border-color: {PRIMARY};\n}}\n'
SETTINGS_CARD_BODY_STYLE = f'\nQGroupBox#settingsCardBody {{\n    background: white;\n    border: none;\n    border-radius: 0;\n    margin: 0;\n    padding: 0;\n}}\n'
SETTINGS_FIELD_LABEL_STYLE = f'\nQLabel {{\n    color: {PRIMARY};\n    font-size: 9pt;\n    font-weight: normal;\n    background: transparent;\n}}\n'
GROUP_STYLE = f'\nQGroupBox {{\n    color: #333333;\n    font-size: 12pt;\n    font-weight: bold;\n    border: 2px solid {BORDER};\n    border-radius: 8px;\n    margin-top: 14px;\n    padding-top: 10px;\n    background: white;\n}}\nQGroupBox::title {{\n    subcontrol-origin: margin;\n    left: 14px;\n    padding: 0 8px;\n    background: {BG_COLOR};\n    border-radius: 4px;\n}}\n'
SAVE_BUTTON_STYLE = f'\nQPushButton {{\n    background-color: {PRIMARY};\n    color: white;\n    border: none;\n    border-radius: 8px;\n    padding: 12px 24px;\n    font-size: 12pt;\n    font-weight: bold;\n    min-height: 52px;\n}}\nQPushButton:hover   {{ background-color: {PRIMARY_DARK}; }}\nQPushButton:pressed {{ background-color: #4A2EC6; }}\nQPushButton:disabled {{ background-color: {SECONDARY_BG}; color: {DISABLED_BORDER}; }}\n'
LABEL_STYLE = f'\nQLabel {{\n    color: #333333;\n    font-size: 11pt;\n    font-weight: bold;\n    background: transparent;\n}}\n'
ACTION_BTN_STYLE = f'\nQPushButton {{\n    background-color: {PRIMARY};\n    color: white;\n    border: none;\n    border-radius: 8px;\n    padding: 0 16px;\n    font-size: 11pt;\n    font-weight: bold;\n    min-height: 44px;\n}}\nQPushButton:hover   {{ background-color: {PRIMARY_DARK}; }}\nQPushButton:pressed {{ background-color: {PRIMARY_DARK}; }}\n'
GHOST_BTN_STYLE = f'\nQPushButton {{\n    background-color: white;\n    color: {PRIMARY};\n    border: 2px solid {PRIMARY};\n    border-radius: 8px;\n    padding: 0 16px;\n    font-size: 11pt;\n    font-weight: bold;\n    min-height: 44px;\n}}\nQPushButton:hover   {{ background-color: {PRIMARY_LIGHT}; }}\nQPushButton:pressed {{ background-color: {PRIMARY_LIGHT}; }}\nQPushButton:disabled {{ color: {DISABLED_BORDER}; border-color: {DISABLED_BORDER}; }}\n'
```

## `widget_factory.py`

Source: [pl_gui/settings/settings_view/widget_factory.py](../../../../pl_gui/settings/settings_view/widget_factory.py).

Widget factory for GenericSettingGroup. Each widget type is described by a WidgetHandler that knows: - how to create the widget and wire its change signal - how to read its current value - how to set a value (used by set_values, no signal expected) - whether it should span both grid columns (full_width) Adding a new widget type = add one WidgetHandler to _REGISTRY. Nothing else needs to change.

Imports (including optional/function-local imports; not a startup dependency list): `PyQt6.QtGui`, `PyQt6.QtWidgets`, `__future__`, `dataclasses`, `pl_gui.settings.settings_view.schema`, `pl_gui.settings.settings_view.styles`, `pl_gui.utils.utils_widgets.SwitchButton`, `pl_gui.utils.utils_widgets.int_list_widget`, `pl_gui.utils.utils_widgets.touch_spinbox`, `typing`.

### `WidgetHandler`

```python
@dataclass
class WidgetHandler:
```

All widget-type-specific knowledge in one place. create(field, emit) — builds and returns the widget; must connect the widget's change signal to emit(value). get_value(widget) — returns the widget's current value. set_value(widget, v) — sets the widget's value silently (caller blocks signals). full_width — True → widget spans both grid columns.

Declared fields/defaults:

```python
create: Callable[[SettingField, Callable[[Any], None]], QWidget]
get_value: Callable[[QWidget], Any]
set_value: Callable[[QWidget, Any], None]
full_width: bool = False
```

### `_make_spinbox`

```python
def _make_spinbox(f: SettingField, emit: Callable) -> TouchSpinBox
```

### `_make_combo`

```python
def _make_combo(f: SettingField, emit: Callable) -> QComboBox
```

### `_make_line_edit`

```python
def _make_line_edit(f: SettingField, emit: Callable) -> QLineEdit
```

### `_make_int_list`

```python
def _make_int_list(f: SettingField, emit: Callable) -> IntListWidget
```

### `_make_toggle`

```python
def _make_toggle(f: SettingField, emit: Callable) -> QToggle
```

### `_combo_set`

```python
def _combo_set(w: QComboBox, v: Any) -> None
```

### `_toggle_set`

```python
def _toggle_set(w: QToggle, value: Any) -> None
```

### `get_handler`

```python
def get_handler(widget_type: str) -> WidgetHandler
```
