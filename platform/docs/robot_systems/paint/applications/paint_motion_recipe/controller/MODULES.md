# Module reference: `src/robot_systems/paint/applications/paint_motion_recipe/controller`

[Package guide](README.md) · [Complete source index](../../../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [paint_motion_recipe_controller.py](#paint_motion_recipe_controllerpy)

## `__init__.py`

Source: [src/robot_systems/paint/applications/paint_motion_recipe/controller/__init__.py](../../../../../../src/robot_systems/paint/applications/paint_motion_recipe/controller/__init__.py).

Imports (including optional/function-local imports; not a startup dependency list): `src.robot_systems.paint.applications.paint_motion_recipe.controller.paint_motion_recipe_controller`.

Package-level import/export surface:

```python
from src.robot_systems.paint.applications.paint_motion_recipe.controller.paint_motion_recipe_controller import PaintMotionRecipeController
```

Module declarations (expressions are shown without evaluating them):

```python
__all__ = ['PaintMotionRecipeController']
```

## `paint_motion_recipe_controller.py`

Source: [src/robot_systems/paint/applications/paint_motion_recipe/controller/paint_motion_recipe_controller.py](../../../../../../src/robot_systems/paint/applications/paint_motion_recipe/controller/paint_motion_recipe_controller.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `src.applications.base.i_application_controller`, `src.robot_systems.paint.applications.paint_motion_recipe.model.paint_motion_recipe_model`, `src.robot_systems.paint.applications.paint_motion_recipe.view.paint_motion_recipe_view`.

### `PaintMotionRecipeController`

```python
class PaintMotionRecipeController(IApplicationController):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, model: PaintMotionRecipeModel, view: PaintMotionRecipeView) -> None
```

```python
def load(self) -> None
```

```python
def stop(self) -> None
```
