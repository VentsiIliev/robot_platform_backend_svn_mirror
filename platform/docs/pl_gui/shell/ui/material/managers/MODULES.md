# Module reference: `pl_gui/shell/ui/material/managers`

[Package guide](README.md) · [Complete source index](../../../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [expanded_view_manager.py](#expanded_view_managerpy)
- [floating_icon_manager.py](#floating_icon_managerpy)
- [overlay_manager.py](#overlay_managerpy)

## `__init__.py`

Source: [pl_gui/shell/ui/material/managers/__init__.py](../../../../../../pl_gui/shell/ui/material/managers/__init__.py).

Imports (including optional/function-local imports; not a startup dependency list): `.expanded_view_manager`, `.floating_icon_manager`, `.overlay_manager`.

Package-level import/export surface:

```python
from .expanded_view_manager import ExpandedViewManager
from .floating_icon_manager import FloatingIconManager
from .overlay_manager import OverlayManager
```

Module declarations (expressions are shown without evaluating them):

```python
__all__ = ['ExpandedViewManager', 'FloatingIconManager', 'OverlayManager']
```

## `expanded_view_manager.py`

Source: [pl_gui/shell/ui/material/managers/expanded_view_manager.py](../../../../../../pl_gui/shell/ui/material/managers/expanded_view_manager.py).

Imports (including optional/function-local imports; not a startup dependency list): `..expanded_view`, `..menu_icon`, `pl_gui.shell.ui.styles`.

### `ExpandedViewManager`

```python
class ExpandedViewManager:
```

Handles expanded view creation and lifecycle

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, parent_widget)
```

```python
def show_expanded_view(self, folder_name, overlay_parent, on_close, on_app_selected, on_minimize, on_close_app)
```

```python
def populate_apps(self, buttons)
```

```python
def fade_in(self, center_pos)
```

```python
def fade_out(self)
```

```python
def show_close_button(self)
```

```python
def hide_close_button(self)
```

## `floating_icon_manager.py`

Source: [pl_gui/shell/ui/material/managers/floating_icon_manager.py](../../../../../../pl_gui/shell/ui/material/managers/floating_icon_manager.py).

Imports (including optional/function-local imports; not a startup dependency list): `..floating_icon`, `PyQt6.QtCore`.

### `FloatingIconManager`

```python
class FloatingIconManager:
```

Manages floating folder icon lifecycle

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, parent_widget)
```

```python
def show_floating_icon(self, folder_name, on_click_callback)
```

Create and show floating icon with safer cleanup

```python
def hide_floating_icon(self)
```

Hide and cleanup floating icon safely

## `overlay_manager.py`

Source: [pl_gui/shell/ui/material/managers/overlay_manager.py](../../../../../../pl_gui/shell/ui/material/managers/overlay_manager.py).

Imports (including optional/function-local imports; not a startup dependency list): `..overlay`, `pl_gui.shell.ui.styles`, `traceback`.

### `OverlayManager`

```python
class OverlayManager:
```

Handles overlay creation and styling

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, parent_widget, overlay_parent, overlay_callback)
```

```python
def show_overlay(self)
```

Create and show overlay

```python
def set_style(self, style)
```

```python
def hide_overlay(self)
```
