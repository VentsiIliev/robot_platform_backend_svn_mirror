# Module reference: `src/applications/base/widgets`

[Package guide](README.md) · [Complete source index](../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [card_checkbox.py](#card_checkboxpy)
- [custom_virtual_keyboard.py](#custom_virtual_keyboardpy)
- [fluid_progress.py](#fluid_progresspy)
- [keyboard_number_field.py](#keyboard_number_fieldpy)
- [virtual_keyboard_widget_factory.py](#virtual_keyboard_widget_factorypy)

## `card_checkbox.py`

Source: [src/applications/base/widgets/card_checkbox.py](../../../../src/applications/base/widgets/card_checkbox.py).

Imports (including optional/function-local imports; not a startup dependency list): `PyQt6.QtCore`, `PyQt6.QtGui`, `PyQt6.QtWidgets`, `pl_gui.settings.settings_view.styles`.

### `CardCheckBox`

```python
class CardCheckBox(QCheckBox):
```

Touch-sized checkbox with a clear checked indicator.

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, text: str, parent=None)
```

```python
def paintEvent(self, event) -> None
```

## `custom_virtual_keyboard.py`

Source: [src/applications/base/widgets/custom_virtual_keyboard.py](../../../../src/applications/base/widgets/custom_virtual_keyboard.py).

Imports (including optional/function-local imports; not a startup dependency list): `PyQt6`, `PyQt6.QtCore`, `PyQt6.QtGui`, `PyQt6.QtWidgets`, `__future__`, `functools`, `src.applications.base.config.virtual_keyboard_config`, `typing`.

### `_keyboard_owner_for_widget`

```python
def _keyboard_owner_for_widget(widget: Optional[QWidget]) -> Optional['_KeyboardMixin']
```

### `_PopupKeyboardDialog`

```python
class _PopupKeyboardDialog(QDialog):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, target: QWidget, *, numeric_only: bool=False, parent: Optional[QWidget]=None) -> None
```

```python
def closeEvent(self, event) -> None
```

```python
def hideEvent(self, event) -> None
```

```python
def dock_to_target_window(self) -> None
```

```python
def keyboard_rect_global(self) -> QRect
```

### `_KeyboardMixin`

```python
class _KeyboardMixin:
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, *args, **kwargs)
```

```python
def focusInEvent(self, event) -> None
```

```python
def eventFilter(self, watched, event) -> bool
```

### `KeyboardLineEdit`

```python
class KeyboardLineEdit(_KeyboardMixin, QLineEdit):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def mousePressEvent(self, event: QMouseEvent) -> None
```

### `KeyboardSpinBox`

```python
class KeyboardSpinBox(_KeyboardMixin, QSpinBox):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def mousePressEvent(self, event: QMouseEvent) -> None
```

### `KeyboardDoubleSpinBox`

```python
class KeyboardDoubleSpinBox(_KeyboardMixin, QDoubleSpinBox):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def mousePressEvent(self, event: QMouseEvent) -> None
```

## `fluid_progress.py`

Source: [src/applications/base/widgets/fluid_progress.py](../../../../src/applications/base/widgets/fluid_progress.py).

Native PyQt6 determinate/indeterminate progress indicators using the shared
platform palette. Public widgets are `InkBar`, `PlumeLine`, and `Vessel`, all
derived from `FluidProgress`.

```python
def create_fluid_progress(style: str="plume", parent=None) -> FluidProgress
```

Supported styles are `"ink"`, `"plume"`, and `"vessel"`.

## `keyboard_number_field.py`

Source: [src/applications/base/widgets/keyboard_number_field.py](../../../../src/applications/base/widgets/keyboard_number_field.py).

Imports (including optional/function-local imports; not a startup dependency list): `PyQt6.QtCore`, `PyQt6.QtWidgets`, `pl_gui.settings.settings_view.styles`, `src.applications.base.widgets.custom_virtual_keyboard`.

### `KeyboardNumberField`

```python
class KeyboardNumberField(QFrame):
```

Touch stepper around the shared virtual-keyboard spin box.

Declared fields/defaults:

```python
valueChanged = pyqtSignal(object)
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, *, decimal: bool=False, button_width: int=50, parent=None)
```

```python
def eventFilter(self, watched, event) -> bool
```

```python
def setRange(self, minimum, maximum) -> None
```

```python
def setMinimum(self, minimum) -> None
```

```python
def setMaximum(self, maximum) -> None
```

```python
def setSingleStep(self, step) -> None
```

```python
def setDecimals(self, decimals: int) -> None
```

```python
def setSuffix(self, suffix: str) -> None
```

```python
def setSpecialValueText(self, text: str) -> None
```

```python
def setReadOnly(self, read_only: bool) -> None
```

```python
def setValue(self, value) -> None
```

```python
def value(self)
```

## `virtual_keyboard_widget_factory.py`

Source: [src/applications/base/widgets/virtual_keyboard_widget_factory.py](../../../../src/applications/base/widgets/virtual_keyboard_widget_factory.py).

Imports (including optional/function-local imports; not a startup dependency list): `PyQt6.QtWidgets`, `contour_editor.persistence.providers.widget_provider`, `src.applications.base.config.virtual_keyboard_config`, `src.applications.base.widgets.custom_virtual_keyboard`.

### `VirtualKeyboardWidgetFactory`

```python
class VirtualKeyboardWidgetFactory(IWidgetFactory):
```

Reusable widget factory with optional virtual keyboard support.

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def create_double_spinbox(self, parent=None)
```

```python
def create_spinbox(self, parent=None)
```

```python
def create_lineedit(self, parent=None)
```
