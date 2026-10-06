# Module reference: `pl_gui/settings/settings_menu`

[Package guide](README.md) · [Complete source index](../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [build_showcase.py](#build_showcasepy)
- [category_descriptor.py](#category_descriptorpy)
- [icon_loader.py](#icon_loaderpy)
- [menu_icon.py](#menu_iconpy)
- [settings_menu.py](#settings_menupy)

## `__init__.py`

Source: [pl_gui/settings/settings_menu/__init__.py](../../../../pl_gui/settings/settings_menu/__init__.py).

No top-level functions, classes or public value declarations; inspect the source for imports or entry-point statements.

## `build_showcase.py`

Source: [pl_gui/settings/settings_menu/build_showcase.py](../../../../pl_gui/settings/settings_menu/build_showcase.py).

Imports (including optional/function-local imports; not a startup dependency list): `pl_gui.settings.settings_menu.category_descriptor`, `pl_gui.settings.settings_menu.settings_menu`, `pl_gui.settings.settings_view.build_showcase`.

### `build_settings_menu_showcase`

```python
def build_settings_menu_showcase()
```

## `category_descriptor.py`

Source: [pl_gui/settings/settings_menu/category_descriptor.py](../../../../pl_gui/settings/settings_menu/category_descriptor.py).

Imports (including optional/function-local imports; not a startup dependency list): `dataclasses`.

### `CategoryDescriptor`

```python
@dataclass
class CategoryDescriptor:
```

Declared fields/defaults:

```python
id: str
icon: str
```

## `icon_loader.py`

Source: [pl_gui/settings/settings_menu/icon_loader.py](../../../../pl_gui/settings/settings_menu/icon_loader.py).

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

## `menu_icon.py`

Source: [pl_gui/settings/settings_menu/menu_icon.py](../../../../pl_gui/settings/settings_menu/menu_icon.py).

Imports (including optional/function-local imports; not a startup dependency list): `PyQt6.QtCore`, `PyQt6.QtGui`, `PyQt6.QtWidgets`, `pl_gui.settings.settings_menu.icon_loader`, `pl_gui.settings.settings_view.styles`, `re`.

### `MenuIcon`

```python
class MenuIcon(QPushButton):
```

Material Design 3 app icon with proper touch targets and visual feedback

Declared fields/defaults:

```python
button_clicked = pyqtSignal(str)
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, icon_label, icon_path, icon_text='', callback=None, parent=None, qta_color=None)
```

```python
def setup_ui(self)
```

Setup Material Design 3 styling with proper tokens

```python
def setup_icon_content(self)
```

Setup icon content following Material Design icon guidelines

```python
def setup_fallback_text(self)
```

Setup fallback text with Material Design typography

```python
def enterEvent(self, event)
```

Material Design hover state

```python
def leaveEvent(self, event)
```

Material Design normal state restoration

```python
def mousePressEvent(self, event)
```

Material Design press interaction

```python
def mouseReleaseEvent(self, event)
```

Material Design release interaction

```python
def paintEvent(self, event)
```

Custom paint event for Material Design visual consistency

```python
def sizeHint(self)
```

Material Design size hint

```python
def minimumSizeHint(self)
```

Minimum size following Material Design guidelines

```python
def set_icon_from_path(self, icon_path)
```

Update icon from new path with Material Design handling

```python
def set_material_style(self, style_variant='primary')
```

Apply different Material Design style variants

```python
def set_material_size(self, size_variant='standard')
```

Apply different Material Design size variants

## `settings_menu.py`

Source: [pl_gui/settings/settings_menu/settings_menu.py](../../../../pl_gui/settings/settings_menu/settings_menu.py).

Imports (including optional/function-local imports; not a startup dependency list): `.menu_icon`, `PyQt6.QtCore`, `PyQt6.QtGui`, `PyQt6.QtWidgets`, `pl_gui.settings.settings_view.styles`, `qtawesome`.

### `SettingsMenu`

```python
class SettingsMenu(QWidget):
```

Settings menu plugin that displays clickable icons for different settings categories. Signals: settings_selected(str): Emitted when a settings category is clicked (setting_id) Args: categories: List of category dicts with 'id', 'title', 'icon', 'description' keys. If None, uses default categories. compact: Whether to use compact mode (for sidebar) parent: Parent widget

Declared fields/defaults:

```python
settings_selected = pyqtSignal(str)
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, categories, compact: bool=False, parent=None)
```

```python
def set_active_item(self, setting_id: str)
```

Mark a specific item as active/selected

### `SettingsNavigationWidget`

```python
class SettingsNavigationWidget(QWidget):
```

Combined navigation widget with sidebar menu and content area. Icons remain visible for quick switching between settings. Args: categories: List of category dicts with 'id', 'title', 'icon', 'description' keys. If None, uses default categories from SettingsMenu. factory_map: Dict mapping category IDs to factory functions that create widgets. e.g., {"robot": lambda: RobotConfigUI(), "camera": create_camera_settings} If provided, views are automatically created for all categories. parent: Parent widget Signals: tab_changing(str, str): Emitted before tab changes (old_tab_id, new_tab_id) tab_changed(str, str): Emitted after tab changes (old_tab_id, new_tab_id)

Declared fields/defaults:

```python
tab_changing = pyqtSignal(str, str)
tab_changed = pyqtSignal(str, str)
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, categories, factory_map, parent=None)
```

```python
def add_settings_view(self, setting_id: str, widget: QWidget)
```

Add a settings view for a specific category
