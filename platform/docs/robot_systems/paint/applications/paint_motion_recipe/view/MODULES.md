# Module reference: `src/robot_systems/paint/applications/paint_motion_recipe/view`

[Package guide](README.md) · [Complete source index](../../../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [paint_motion_recipe_view.py](#paint_motion_recipe_viewpy)

## `__init__.py`

Source: [src/robot_systems/paint/applications/paint_motion_recipe/view/__init__.py](../../../../../../src/robot_systems/paint/applications/paint_motion_recipe/view/__init__.py).

Imports (including optional/function-local imports; not a startup dependency list): `src.robot_systems.paint.applications.paint_motion_recipe.view.paint_motion_recipe_view`.

Package-level import/export surface:

```python
from src.robot_systems.paint.applications.paint_motion_recipe.view.paint_motion_recipe_view import PaintMotionRecipeView
```

Module declarations (expressions are shown without evaluating them):

```python
__all__ = ['PaintMotionRecipeView']
```

## `paint_motion_recipe_view.py`

Source: [src/robot_systems/paint/applications/paint_motion_recipe/view/paint_motion_recipe_view.py](../../../../../../src/robot_systems/paint/applications/paint_motion_recipe/view/paint_motion_recipe_view.py).

Imports (including optional/function-local imports; not a startup dependency list): `PyQt6.QtCore`, `PyQt6.QtWidgets`, `__future__`, `pl_gui.settings.settings_view.styles`, `src.applications.base.i_application_view`, `src.applications.base.styled_message_box`, `src.applications.base.widgets.custom_virtual_keyboard`, `src.robot_systems.paint.applications.paint_motion_recipe.domain.recipe`.

### `_t`

```python
def _t(text: str) -> str
```

### `PaintMotionRecipeView`

```python
class PaintMotionRecipeView(IApplicationView):
```

Declared fields/defaults:

```python
add_group_step_requested = pyqtSignal(str, str, str)
capture_pose_step_requested = pyqtSignal(str)
remove_step_requested = pyqtSignal(int)
move_step_requested = pyqtSignal(int, int)
step_enabled_changed = pyqtSignal(int, bool)
save_requested = pyqtSignal()
reload_requested = pyqtSignal()
test_step_requested = pyqtSignal(int)
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, parent=None) -> None
```

```python
def setup_ui(self) -> None
```

```python
def set_groups(self, groups: list[str]) -> None
```

```python
def set_recipe(self, recipe: MotionRecipe) -> None
```

```python
def set_status(self, message: str) -> None
```

```python
def show_info(self, title: str, message: str) -> None
```

```python
def show_error(self, title: str, message: str) -> None
```
