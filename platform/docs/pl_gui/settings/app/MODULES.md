# Module reference: `pl_gui/settings/app`

[Package guide](README.md) · [Complete source index](../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [basic_settings_app_widget.py](#basic_settings_app_widgetpy)

## `__init__.py`

Source: [pl_gui/settings/app/__init__.py](../../../../pl_gui/settings/app/__init__.py).

No top-level functions, classes or public value declarations; inspect the source for imports or entry-point statements.

## `basic_settings_app_widget.py`

Source: [pl_gui/settings/app/basic_settings_app_widget.py](../../../../pl_gui/settings/app/basic_settings_app_widget.py).

Imports (including optional/function-local imports; not a startup dependency list): `PyQt6.QtCore`, `PyQt6.QtWidgets`, `pl_gui.settings.settings_menu.build_showcase`, `pl_gui.shell.base_app_widget.AppWidget`.

### `BasicSettingsAppWidget`

```python
class BasicSettingsAppWidget(AppWidget):
```

Declared fields/defaults:

```python
tab_changing = pyqtSignal(str, str)
tab_changed = pyqtSignal(str, str)
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, parent=None)
```

```python
def setup_ui(self)
```
