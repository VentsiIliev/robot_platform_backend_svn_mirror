# Module reference: `pl_gui/shell/ui/material`

[Package guide](README.md) · [Complete source index](../../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [animation.py](#animationpy)
- [expanded_view.py](#expanded_viewpy)
- [factory.py](#factorypy)
- [floating_icon.py](#floating_iconpy)
- [folder_widget.py](#folder_widgetpy)
- [menu_icon.py](#menu_iconpy)
- [overlay.py](#overlaypy)

## `__init__.py`

Source: [pl_gui/shell/ui/material/__init__.py](../../../../../pl_gui/shell/ui/material/__init__.py).

Imports (including optional/function-local imports; not a startup dependency list): `.factory`.

Package-level import/export surface:

```python
from .factory import MaterialUIFactory
```

Module declarations (expressions are shown without evaluating them):

```python
__all__ = ['MaterialUIFactory']
```

## `animation.py`

Source: [pl_gui/shell/ui/material/animation.py](../../../../../pl_gui/shell/ui/material/animation.py).

Animation Manager for PyQt6 Material Design Components This module centralizes all animation logic from the folder interface, providing consistent Material Design timing and easing curves.

Imports (including optional/function-local imports; not a startup dependency list): `PyQt6.QtCore`, `PyQt6.QtWidgets`, `typing`.

### `MaterialDesignTiming`

```python
class MaterialDesignTiming:
```

Material Design animation timing constants

Declared fields/defaults:

```python
FAST = 100
SHORT = 150
MEDIUM = 300
LONG = 500
EXTRA_LONG = 700
```

### `MaterialDesignEasing`

```python
class MaterialDesignEasing:
```

Material Design easing curve presets

Declared fields/defaults:

```python
STANDARD = QEasingCurve.Type.OutCubic
EMPHASIZED = QEasingCurve.Type.OutQuart
DECELERATED = QEasingCurve.Type.OutCubic
ACCELERATED = QEasingCurve.Type.InCubic
LINEAR = QEasingCurve.Type.Linear
```

### `AnimationManager`

```python
class AnimationManager(QObject):
```

Centralized animation management with Material Design principles

Declared fields/defaults:

```python
animation_finished = pyqtSignal(str)
all_animations_finished = pyqtSignal()
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, target_widget: QWidget, parent: Optional[QObject]=None)
```

```python
def create_fade_animation(self, duration: int=MaterialDesignTiming.MEDIUM, easing: QEasingCurve.Type=MaterialDesignEasing.STANDARD, animation_id: str='fade') -> QPropertyAnimation
```

Create opacity fade animation

```python
def create_geometry_animation(self, duration: int=MaterialDesignTiming.MEDIUM, easing: QEasingCurve.Type=MaterialDesignEasing.STANDARD, animation_id: str='geometry') -> QPropertyAnimation
```

Create geometry/scale animation

```python
def fade_in(self, start_opacity: float=0.0, end_opacity: float=1.0, duration: int=MaterialDesignTiming.MEDIUM, callback: Optional[Callable]=None) -> QPropertyAnimation
```

Material Design fade-in animation

```python
def fade_out(self, start_opacity: float=1.0, end_opacity: float=0.0, duration: int=MaterialDesignTiming.MEDIUM, hide_on_finish: bool=True, callback: Optional[Callable]=None) -> QPropertyAnimation
```

Material Design fade-out animation

```python
def scale_in_from_center(self, center_pos: QPoint, scale_factor: float=0.8, duration: int=MaterialDesignTiming.MEDIUM, callback: Optional[Callable]=None) -> QPropertyAnimation
```

Material Design scale-in from center point

```python
def scale_out_to_center(self, center_pos: Optional[QPoint]=None, scale_factor: float=0.8, duration: int=MaterialDesignTiming.MEDIUM, hide_on_finish: bool=True, callback: Optional[Callable]=None) -> QPropertyAnimation
```

Material Design scale-out to center point

```python
def combined_fade_and_scale_in(self, center_pos: QPoint, scale_factor: float=0.8, opacity_start: float=0.0, opacity_end: float=1.0, duration: int=MaterialDesignTiming.MEDIUM, callback: Optional[Callable]=None) -> QParallelAnimationGroup
```

Combined fade and scale animation for Material Design entrance

```python
def combined_fade_and_scale_out(self, center_pos: Optional[QPoint]=None, scale_factor: float=0.8, opacity_start: float=1.0, opacity_end: float=0.0, duration: int=MaterialDesignTiming.MEDIUM, hide_on_finish: bool=True, callback: Optional[Callable]=None) -> QParallelAnimationGroup
```

Combined fade and scale animation for Material Design exit

```python
def create_floating_icon_show_animation(self, start_offset: QPoint=QPoint(0, 16), duration: int=MaterialDesignTiming.MEDIUM) -> QParallelAnimationGroup
```

Animation for showing floating action button

```python
def create_floating_icon_hide_animation(self, duration: int=MaterialDesignTiming.SHORT, callback: Optional[Callable]=None) -> QPropertyAnimation
```

Animation for hiding floating action button

```python
def create_button_press_animation(self, scale_factor: float=0.95, duration: int=MaterialDesignTiming.FAST) -> QPropertyAnimation
```

Material Design button press feedback animation

```python
def create_button_release_animation(self, original_rect: Optional[QRect]=None, duration: int=MaterialDesignTiming.FAST) -> QPropertyAnimation
```

Material Design button release feedback animation

```python
def stop_animation(self, animation_id: str) -> bool
```

Stop specific animation by ID

```python
def stop_all_animations(self)
```

Stop all active animations

```python
def is_animation_active(self, animation_id: str) -> bool
```

Check if specific animation is currently running

```python
def has_active_animations(self) -> bool
```

Check if any animations are currently running

```python
def cleanup(self)
```

Clean up all animations and groups

### `create_material_entrance_animation`

```python
def create_material_entrance_animation(widget: QWidget, center_pos: QPoint, duration: int=MaterialDesignTiming.MEDIUM, callback: Optional[Callable]=None) -> AnimationManager
```

Create a standard Material Design entrance animation

### `create_material_exit_animation`

```python
def create_material_exit_animation(widget: QWidget, duration: int=MaterialDesignTiming.MEDIUM, callback: Optional[Callable]=None) -> AnimationManager
```

Create a standard Material Design exit animation

### `create_fab_animation`

```python
def create_fab_animation(widget: QWidget, show: bool=True, callback: Optional[Callable]=None) -> AnimationManager
```

Create floating action button show/hide animation

### `AnimationPatterns`

```python
class AnimationPatterns:
```

Common animation patterns used in the folder interface

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
@staticmethod
def folder_open_animation(expanded_view_widget: QWidget, center_pos: QPoint) -> AnimationManager
```

Standard folder opening animation

```python
@staticmethod
def folder_close_animation(expanded_view_widget: QWidget) -> AnimationManager
```

Standard folder closing animation

```python
@staticmethod
def floating_icon_transition(floating_icon_widget: QWidget, show: bool) -> AnimationManager
```

Floating icon show/hide transition

## `expanded_view.py`

Source: [pl_gui/shell/ui/material/expanded_view.py](../../../../../pl_gui/shell/ui/material/expanded_view.py).

Imports (including optional/function-local imports; not a startup dependency list): `.animation`, `PyQt6.QtCore`, `PyQt6.QtGui`, `PyQt6.QtWidgets`, `pl_gui.shell.ui.styles`.

### `ExpandedFolderView`

```python
class ExpandedFolderView(QFrame):
```

Material Design 3 expanded folder view

Declared fields/defaults:

```python
close_requested = pyqtSignal()
app_selected = pyqtSignal(str)
close_current_app_requested = pyqtSignal()
minimize_requested = pyqtSignal()
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, folder_name, parent=None)
```

```python
def setup_ui(self)
```

Material Design 3 surface styling

```python
def add_app_icon(self, app_icon_widget, row, col)
```

Add an app icon to the grid

```python
def safe_close(self)
```

Material Design close transition

```python
def fade_in(self, center_pos)
```

Material Design scale-in animation

```python
def fade_out(self)
```

Material Design scale-out animation

```python
def on_app_clicked(self, app_name)
```

Handle app selection

```python
def show_close_app_button(self)
```

Material Design button reveal animation

```python
def hide_close_app_button(self)
```

Hide close button with Material Design transition

```python
def on_close_app_clicked(self)
```

Handle close app button click

```python
def set_app_running_state(self, app_name=None)
```

Update app state with Material Design consistency

```python
def animation_finished(self)
```

Animation completion handler

```python
def safe_hide(self)
```

Safe hide with Material Design cleanup

```python
def mousePressEvent(self, event)
```

Accept mouse events to prevent propagation

```python
def closeEvent(self, event)
```

Material Design close event handling

## `factory.py`

Source: [pl_gui/shell/ui/material/factory.py](../../../../../pl_gui/shell/ui/material/factory.py).

Imports (including optional/function-local imports; not a startup dependency list): `.folder_widget`, `.managers.expanded_view_manager`, `.managers.floating_icon_manager`, `.managers.overlay_manager`.

### `MaterialUIFactory`

```python
class MaterialUIFactory:
```

Factory that creates Material Design 3 UI components (the existing implementation).

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def create_folder_widget(self, ID, folder_name)
```

```python
def create_expanded_view_manager(self, folder_widget)
```

```python
def create_floating_icon_manager(self, folder_widget)
```

```python
def create_overlay_manager(self, folder_widget, overlay_parent, overlay_callback)
```

## `floating_icon.py`

Source: [pl_gui/shell/ui/material/floating_icon.py](../../../../../pl_gui/shell/ui/material/floating_icon.py).

Imports (including optional/function-local imports; not a startup dependency list): `.animation`, `PyQt6.QtCore`, `PyQt6.QtGui`, `PyQt6.QtWidgets`, `pl_gui.shell.ui.styles`.

### `FloatingFolderIcon`

```python
class FloatingFolderIcon(QPushButton):
```

Material Design floating action button for folder icon

Declared fields/defaults:

```python
clicked_signal = pyqtSignal()
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, folder_name, parent=None)
```

```python
def setup_ui(self)
```

Setup Material Design floating action button

```python
def show_with_animation(self)
```

Material Design scale-in animation

```python
def hide_with_animation(self)
```

Material Design scale-out animation

## `folder_widget.py`

Source: [pl_gui/shell/ui/material/folder_widget.py](../../../../../pl_gui/shell/ui/material/folder_widget.py).

Imports (including optional/function-local imports; not a startup dependency list): `.menu_icon`, `PyQt6.QtCore`, `PyQt6.QtGui`, `PyQt6.QtWidgets`, `pl_gui.shell.ui.styles`.

### `LayoutManager`

```python
class LayoutManager:
```

Material Design 3 layout management

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, folder_widget)
```

```python
def setup_responsive_sizing(self)
```

```python
def update_main_layout_margins(self)
```

```python
def update_header_layout_spacing(self)
```

```python
def update_preview_layout_margins(self)
```

```python
def calculate_icon_size(self)
```

```python
def update_typography(self)
```

```python
def handle_resize_event(self)
```

### `FolderWidget`

```python
class FolderWidget(QFrame):
```

Pure UI component - only handles visual presentation

Declared fields/defaults:

```python
clicked = pyqtSignal()
outside_clicked = pyqtSignal()
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, ID, folder_name='Apps', parent=None)
```

```python
def update_title_label(self, message=None)
```

```python
def folder_clicked(self, event)
```

Handle folder preview click - just emit signal

```python
def setup_ui(self)
```

Material Design 3 UI setup - pure presentation

```python
def update_folder_preview(self)
```

Update folder preview icons - pure UI operation

```python
def set_grayed_out(self, grayed_out)
```

Update visual disabled state

```python
def add_app(self, app_name, icon_path='', callback=None)
```

Add app to UI - no business logic

```python
def sizeHint(self)
```

```python
def resizeEvent(self, event)
```

## `menu_icon.py`

Source: [pl_gui/shell/ui/material/menu_icon.py](../../../../../pl_gui/shell/ui/material/menu_icon.py).

Imports (including optional/function-local imports; not a startup dependency list): `.animation`, `PyQt6.QtCore`, `PyQt6.QtGui`, `PyQt6.QtWidgets`, `pl_gui.shell.ui.icon_loader`, `pl_gui.shell.ui.styles`, `re`.

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

## `overlay.py`

Source: [pl_gui/shell/ui/material/overlay.py](../../../../../pl_gui/shell/ui/material/overlay.py).

Imports (including optional/function-local imports; not a startup dependency list): `.animation`, `PyQt6.QtCore`, `PyQt6.QtWidgets`, `pl_gui.shell.ui.styles`.

### `FolderOverlay`

```python
class FolderOverlay(QWidget):
```

Overlay widget that appears when folder is opened

Declared fields/defaults:

```python
mouse_pressed_outside = pyqtSignal()
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, parent=None)
```

```python
def fade_in(self)
```

Animate overlay appearance

```python
def fade_out(self)
```

Animate overlay disappearance

```python
def mousePressEvent(self, event)
```

Close folder when clicking outside
