# Module reference: `pl_gui/shell/base_app_widget`

[Package guide](README.md) · [Complete source index](../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [AppWidget.py](#appwidgetpy)
- [__init__.py](#__init__py)

## `AppWidget.py`

Source: [pl_gui/shell/base_app_widget/AppWidget.py](../../../../pl_gui/shell/base_app_widget/AppWidget.py).

Imports (including optional/function-local imports; not a startup dependency list): `PyQt6.QtCore`, `PyQt6.QtWidgets`, `sys`.

### `AppWidget`

```python
class AppWidget(QWidget):
```

Base widget for individual applications. Satisfies IAppWidget protocol.

Declared fields/defaults:

```python
app_closed = pyqtSignal()
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, app_name, parent=None)
```

```python
def setup_ui(self)
```

Setup the basic app UI with a back button

```python
def close_app(self)
```

Close this app and return to the main view

```python
def changeEvent(self, event)
```

Handle Qt events — calls on_language_changed() on LanguageChange.

```python
def on_language_changed(self)
```

Called when the application language changes. Override in subclasses.

```python
def clean_up(self)
```

```python
def can_close(self) -> bool
```

Override to veto navigation. Return False to block the shell from closing this app. The shell calls this before clean_up(), removeWidget(), and deleteLater().

## `__init__.py`

Source: [pl_gui/shell/base_app_widget/__init__.py](../../../../pl_gui/shell/base_app_widget/__init__.py).

No top-level functions, classes or public value declarations; inspect the source for imports or entry-point statements.
